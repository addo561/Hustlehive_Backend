from pydantic import BaseModel, Field

# Pydantic models
class PaymentRequest(BaseModel):
    amount: str = Field(..., description="Amount as a string")
    currency: str = Field(default="EUR", description="Currency - GHS for production") 
    external_id: str = None
    payer_message: str = Field(default="Payment for services")
    payee_note: str = Field(default="Thank you for your business")

    
    #payer_phone_number: str = Field(..., description="Customer's MTN MoMo number from frontend") 
    '''@validator('payer_phone_number')
    def validate_phone_number(cls, v):
        try:
            # Parse and validate the phone number
            parsed = phonenumbers.parse(v, None)
            if not phonenumbers.is_valid_number(parsed):
                raise ValueError("Invalid phone number")
            # Format to E.164 format (e.g., +233XXXXXXXXX)
            return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
        except phonenumbers.NumberParseException:
            raise ValueError("Invalid phone number format")'''
class PaymentStatusResponse(BaseModel):
    reference_id: str
    status: str
    amount: str = None
    currency: str = None
    financial_transaction_id: str = None


    