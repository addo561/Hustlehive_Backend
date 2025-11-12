from fastapi import BackgroundTasks, FastAPI, HTTPException, status,APIRouter
import requests
import uuid
import os
from dotenv import load_dotenv
from utils import get_momo_token
from models import PaymentRequest,PaymentStatusResponse

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
async def request_payment(payment_req: PaymentRequest, background_tasks: BackgroundTasks):
    """
     Momo payment request
    """
    try:
        # Generate reference ID if not provided
        if not payment_req.external_id:
            payment_req.external_id = str(uuid.uuid4())
        
        # Get access token
        access_token = get_momo_token()
        
        # Prepare request to Momo API
        url = f"{CONFIG['MOMO_BASE_URL']}/collection/v1_0/requesttopay"
        reference_id = str(uuid.uuid4())
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "X-Reference-Id": reference_id,
            "X-Target-Environment": CONFIG["TARGET_ENVIRONMENT"],
            "Content-Type": "application/json",
            "Ocp-Apim-Subscription-Key": CONFIG["SUBSCRIPTION_PRIMARY_KEY"],
        }
        
        # Create payload
        payload = {
            "amount": payment_req.amount,
            "currency": payment_req.currency,
            "externalId": payment_req.external_id,
            "payer": {
                "partyIdType": "MSISDN",
                "partyId": '233454567898' # Sandbox test number
                #"partyId": payment_req.payer_phone_number # Sandbox test number
            },
            "payerMessage": payment_req.payer_message,
            "payeeNote": payment_req.payee_note
        }
        
        # Make API call
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 202:
            return {
                "message": "Payment request initiated successfully",
                "reference_id": reference_id,
                "external_id": payment_req.external_id,
                "status": "PENDING",
                "amount": payment_req.amount,
                "currency": payment_req.currency
            }
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"MTN Momo API Error: {response.text}"
            )
            
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to initiate payment: {str(e)}"
        )

@router.get("/payment/status/{reference_id}", response_model=PaymentStatusResponse)
async def get_payment_status(reference_id: str):
    """
    Check the status of a payment request
    """
    try:
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
        
        return PaymentStatusResponse(
            reference_id=reference_id,
            status=payment_data.get("status", "UNKNOWN"),
            amount=payment_data.get("amount"),
            currency=payment_data.get("currency"),
            financial_transaction_id=payment_data.get("financialTransactionId")
        )
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            raise HTTPException(status_code=404, detail="Payment transaction not found")
        else:
            raise HTTPException(
                status_code=500, 
                detail=f"Error fetching payment status: {str(e)}"
            )

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
