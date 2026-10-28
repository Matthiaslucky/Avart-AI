import os
import hmac
import hashlib
import requests
from fastapi import HTTPException

PAYSTACK_SECRET_KEY = os.getenv("PAYSTACK_SECRET_KEY")

PAYSTACK_BASE_URL = "https://api.paystack.co"

def initialize_payment(email: str, amount_kobo: int, reference: str, callback_url: str, plan_code: str = None):
    """
    Initialize a Paystack transaction.
    amount_kobo: Amount in Kobo (e.g., ₦500 = 50000 kobo).
    plan_code: Optional Paystack Plan Code for recurring subscriptions.
    """
    headers = {
        "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "email": email,
        "amount": amount_kobo,
        "reference": reference,
        "callback_url": callback_url
    }
    if plan_code:
        payload["plan"] = plan_code

    response = requests.post(f"{PAYSTACK_BASE_URL}/transaction/initialize", json=payload, headers=headers)
    res_data = response.json()
    
    if not res_data.get("status"):
        raise HTTPException(status_code=400, detail=res_data.get("message", "Paystack initialization failed"))
    
    return res_data["data"]

def verify_paystack_webhook_signature(payload_body: bytes, signature_header: str) -> bool:
    """Verify that incoming webhook requests genuinely came from Paystack."""
    computed_signature = hmac.new(
        PAYSTACK_SECRET_KEY.encode('utf-8'),
        payload_body,
        hashlib.sha512
    ).hexdigest()
    return hmac.compare_digest(computed_signature, signature_header)
