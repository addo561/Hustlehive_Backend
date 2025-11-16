from fastapi import BackgroundTasks, HTTPException, status,APIRouter
import requests
import uuid
import os
from dotenv import load_dotenv
from utils import get_momo_token
from models import PaymentRequest,PaymentStatusResponse

from sqlalchemy.orm import Session
from database import get_db
from models import Transaction
from fastapi import Depends

router = APIRouter(tags=['Routers'])
load_dotenv()

# Configuration from environment
CONFIG = {
    "SUBSCRIPTION_PRIMARY_KEY": os.getenv("SUBSCRIPTION_PRIMARY_KEY"),
    "API_USER_ID": os.getenv("API_USER_ID"),
    "API_KEY": os.getenv("API_KEY"),
    "TARGET_ENVIRONMENT": os.getenv("TARGET_ENVIRONMENT"),
    "MOMO_BASE_URL": os.getenv("MOMO_BASE_URL"),
}

# API Routes
@router.get("/")
async def root():
    return {"message": "MTN Momo Payment API is running!"}

@router.get("/health")
async def health_check():
    """Check if API and Momo service are healthy"""
    try:
        token = get_momo_token()
        return {
            "status": "healthy",
            "api": "running",
            "momo_api": "accessible"
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Service unhealthy: {str(e)}"
        )

@router.post("/payment/request", response_model=dict, status_code=status.HTTP_202_ACCEPTED)
async def request_payment(payment_req: PaymentRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Momo payment request
    """
    try:
        # Generate reference ID if not provided
        if not payment_req.external_id:
            payment_req.external_id = str(uuid.uuid4())
        
        # Generate MTN reference ID
        reference_id = str(uuid.uuid4())
        
        # ✅ CREATE TRANSACTION RECORD IN DATABASE FIRST
        transaction = Transaction(
            momo_reference_id=reference_id,
            external_id=payment_req.external_id,
            amount=float(payment_req.amount),
            currency=payment_req.currency,
            payer_phone_number=payment_req.payer_phone_number,
            payer_message=payment_req.payer_message,
            payee_note=payment_req.payee_note,
            status='INITIATED'
        )
        db.add(transaction)
        db.commit()
        db.refresh(transaction)
        
        # Get access token
        access_token = get_momo_token()
        
        # Prepare request to Momo API
        url = f"{CONFIG['MOMO_BASE_URL']}/collection/v1_0/requesttopay"
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "X-Reference-Id": reference_id,
            "X-Target-Environment": CONFIG["TARGET_ENVIRONMENT"],
            "Content-Type": "application/json",
            "Ocp-Apim-Subscription-Key": CONFIG["SUBSCRIPTION_PRIMARY_KEY"],
        }
        
        # Create payload - use dynamic phone number for production, test number for sandbox
        payer_phone = '233454567898' if CONFIG["TARGET_ENVIRONMENT"] == "sandbox" else payment_req.payer_phone_number
        
        payload = {
            "amount": payment_req.amount,
            "currency": payment_req.currency,
            "externalId": payment_req.external_id,
            "payer": {
                "partyIdType": "MSISDN",
                "partyId": payer_phone
            },
            "payerMessage": payment_req.payer_message,
            "payeeNote": payment_req.payee_note
        }
        
        # Make API call
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 202:
            # ✅ UPDATE TRANSACTION STATUS TO PENDING
            transaction.status = 'PENDING'
            db.commit()
            
            return {
                "message": "Payment request initiated successfully",
                "reference_id": reference_id,
                "external_id": payment_req.external_id,
                "status": "PENDING",
                "amount": payment_req.amount,
                "currency": payment_req.currency
            }
        else:
            # ✅ UPDATE TRANSACTION STATUS TO FAILED
            transaction.status = 'FAILED'
            db.commit()
            
            raise HTTPException(
                status_code=response.status_code,
                detail=f"MTN Momo API Error: {response.text}"
            )
            
    except requests.exceptions.RequestException as e:
        # ✅ UPDATE TRANSACTION STATUS TO ERROR ON EXCEPTION
        if 'transaction' in locals():
            transaction.status = 'ERROR'
            db.commit()
            
        raise HTTPException(
            status_code=500,
            detail=f"Failed to initiate payment: {str(e)}"
        )
    except Exception as e:
        # ✅ CATCH ANY OTHER EXCEPTIONS
        if 'transaction' in locals():
            transaction.status = 'ERROR'
            db.commit()
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {str(e)}"
        )

@router.get("/payment/status/{reference_id}", response_model=PaymentStatusResponse)
async def get_payment_status(reference_id: str, db: Session = Depends(get_db)):
    """
    Check the status of a payment request
    """
    try:
        # ✅ FIRST CHECK DATABASE FOR TRANSACTION
        transaction = db.query(Transaction).filter(
            Transaction.momo_reference_id == reference_id
        ).first()
        
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        # If status is still PENDING, check with MTN API
        if transaction.status == 'PENDING':
            access_token = get_momo_token()
            
            url = f"{CONFIG['MOMO_BASE_URL']}/collection/v1_0/requesttopay/{reference_id}"
            headers = {
                "Authorization": f"Bearer {access_token}",
                "X-Target-Environment": CONFIG["TARGET_ENVIRONMENT"],
                "Ocp-Apim-Subscription-Key": CONFIG["SUBSCRIPTION_PRIMARY_KEY"],
            }
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            payment_data = response.json()
            new_status = payment_data.get("status", "UNKNOWN")
            
            # ✅ UPDATE DATABASE WITH LATEST STATUS
            transaction.status = new_status
            if new_status == 'SUCCESSFUL':
                transaction.financial_transaction_id = payment_data.get("financialTransactionId")
            db.commit()
        
        return PaymentStatusResponse(
            reference_id=reference_id,
            status=transaction.status,
            amount=str(transaction.amount),
            currency=transaction.currency,
            financial_transaction_id=transaction.financial_transaction_id
        )
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            raise HTTPException(status_code=404, detail="Payment transaction not found")
        else:
            raise HTTPException(
                status_code=500, 
                detail=f"Error fetching payment status: {str(e)}"
            )

@router.get("/transactions")
async def list_transactions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """✅ NEW ENDPOINT: List all transactions"""
    transactions = db.query(Transaction).offset(skip).limit(limit).all()
    return transactions

@router.get("/transactions/{external_id}")
async def get_transaction_by_external_id(external_id: str, db: Session = Depends(get_db)):
    """✅ NEW ENDPOINT: Get transaction by external ID"""
    transaction = db.query(Transaction).filter(Transaction.external_id == external_id).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction

@router.get("/config/test")
async def test_config():
    """Test if configuration is loaded correctly (without sensitive data)"""
    return {
        "api_user_id": CONFIG["API_USER_ID"][:8] + "..." if CONFIG["API_USER_ID"] else None,
        "target_environment": CONFIG["TARGET_ENVIRONMENT"],
        "momo_base_url": CONFIG["MOMO_BASE_URL"],
        "config_loaded": all([
            CONFIG["SUBSCRIPTION_PRIMARY_KEY"],
            CONFIG["API_USER_ID"], 
            CONFIG["API_KEY"]
        ])
    }