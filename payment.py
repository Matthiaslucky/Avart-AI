import uuid
import json
from fastapi import APIRouter, Request, HTTPException, Header, Depends
from pydantic import BaseModel, EmailStr
from services.paystack import initialize_payment, verify_paystack_webhook_signature

router = APIRouter(prefix="/payments", tags=["Payments"])

class CreditPurchaseRequest(BaseModel):
    email: EmailStr
    package_type: str # "single" (₦100 = 1 gen), "bundle" (₦500 = 6 gens), "sub_pro" (₦5000/mo)

@router.post("/initialize")
def start_payment(payload: CreditPurchaseRequest):
    reference = f"AVART_{uuid.uuid4().hex[:10]}"
    callback_url = "https://avart.mooo.com/payment-success"
    
    # Configure payment plans / rates
    if payload.package_type == "single":
        amount_kobo = 100 * 100 # ₦100
        plan_code = None
    elif payload.package_type == "bundle":
        amount_kobo = 500 * 100 # ₦500
        plan_code = None
    elif payload.package_type == "sub_pro":
        amount_kobo = 5000 * 100 # ₦5,000 / month
        plan_code = "PLN_9lsrqqv8i977q5w"  # Replace with your Paystack Plan Code
    else:
        raise HTTPException(status_code=400, detail="Invalid package type")

    payment_data = initialize_payment(
        email=payload.email,
        amount_kobo=amount_kobo,
        reference=reference,
        callback_url=callback_url,
        plan_code=plan_code
    )
    
    return {
        "status": "success",
        "authorization_url": payment_data["authorization_url"],
        "reference": reference
    }

@router.post("/webhook")
async def paystack_webhook(request: Request, x_paystack_signature: str = Header(None)):
    """Paystack webhook handler for automated credit top-up and subscription activations."""
    if not x_paystack_signature:
        raise HTTPException(status_code=400, detail="Missing Paystack signature")
        
    body = await request.body()
    if not verify_paystack_webhook_signature(body, x_paystack_signature):
        raise HTTPException(status_code=400, detail="Invalid webhook signature")

    event_data = json.loads(body.decode('utf-8'))
    event = event_data.get("event")

    if event == "charge.success":
        data = event_data["data"]
        customer_email = data["customer"]["email"]
        amount_paid = data["amount"] / 100 # Convert kobo back to Naira
        reference = data["reference"]

        # Credit allocation logic
        if amount_paid == 100:
            credits_to_add = 1
        elif amount_paid == 500:
            credits_to_add = 6
        elif amount_paid == 5000:
            credits_to_add = 100 # Pro monthly tier
        else:
            credits_to_add = 1

        # TODO: Update user record in database
        # db.users.update(email=customer_email, add_credits=credits_to_add)
        print(f"SUCCESS: Added {credits_to_add} credits to {customer_email} (Ref: {reference})")

    return {"status": "success"}
