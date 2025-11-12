from pydantic import BaseModel

# Pydantic models
class PaymentRequest(BaseModel):
    amount: str
    currency: str = "CEDI"
    external_id: str = None
    payer_message: str = "Payment for services"
    payee_note: str = "Thank you for your business"

class PaymentStatusResponse(BaseModel):
    reference_id: str
    status: str
    amount: str = None
    currency: str = None
    financial_transaction_id: str = None


    