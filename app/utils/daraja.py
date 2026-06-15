import base64
import datetime
import json
import logging
from typing import Optional

import httpx
from app.config import settings

logger = logging.getLogger(__name__)

SANDBOX_BASE_URL = "https://sandbox.safaricom.co.ke"
PRODUCTION_BASE_URL = "https://api.safaricom.co.ke"


def _get_base_url() -> str:
    return SANDBOX_BASE_URL if settings.MPESA_ENVIRONMENT == "sandbox" else PRODUCTION_BASE_URL


def _get_oauth_token() -> Optional[str]:
    url = f"{_get_base_url()}/oauth/v1/generate?grant_type=client_credentials"
    try:
        resp = httpx.get(url, auth=(settings.MPESA_CONSUMER_KEY, settings.MPESA_CONSUMER_SECRET), timeout=30)
        resp.raise_for_status()
        data = resp.json()
        return data.get("access_token")
    except Exception as e:
        logger.error(f"Failed to get M-Pesa OAuth token: {e}")
        return None


def _generate_password() -> str:
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    raw = f"{settings.MPESA_SHORTCODE}{settings.MPESA_PASSKEY}{timestamp}"
    return base64.b64encode(raw.encode()).decode(), timestamp


def stk_push(phone: str, amount: float, account_ref: str, transaction_desc: str = "Payment") -> dict:
    token = _get_oauth_token()
    if not token:
        return {"success": False, "error": "Failed to authenticate with M-Pesa"}

    password, timestamp = _generate_password()
    formatted_phone = phone.strip()
    if formatted_phone.startswith("0"):
        formatted_phone = "254" + formatted_phone[1:]
    elif formatted_phone.startswith("+"):
        formatted_phone = formatted_phone[1:]
    elif not formatted_phone.startswith("254"):
        formatted_phone = "254" + formatted_phone

    payload = {
        "BusinessShortCode": settings.MPESA_SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": int(round(amount)),
        "PartyA": formatted_phone,
        "PartyB": settings.MPESA_SHORTCODE,
        "PhoneNumber": formatted_phone,
        "CallBackURL": settings.MPESA_CALLBACK_URL,
        "AccountReference": account_ref[:12],
        "TransactionDesc": transaction_desc[:13],
    }

    url = f"{_get_base_url()}/mpesa/stkpush/v1/processrequest"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    try:
        resp = httpx.post(url, json=payload, headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        if data.get("ResponseCode") == "0":
            return {
                "success": True,
                "merchant_request_id": data.get("MerchantRequestID"),
                "checkout_request_id": data.get("CheckoutRequestID"),
                "response": data,
            }
        else:
            return {"success": False, "error": data.get("ResponseDescription", "STK Push failed"), "response": data}
    except Exception as e:
        logger.error(f"M-Pesa STK Push failed: {e}")
        return {"success": False, "error": str(e)}


def query_status(checkout_request_id: str) -> dict:
    token = _get_oauth_token()
    if not token:
        return {"success": False, "error": "Failed to authenticate with M-Pesa"}

    password, timestamp = _generate_password()
    payload = {
        "BusinessShortCode": settings.MPESA_SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "CheckoutRequestID": checkout_request_id,
    }

    url = f"{_get_base_url()}/mpesa/stkpushquery/v1/query"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    try:
        resp = httpx.post(url, json=payload, headers=headers, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        logger.error(f"M-Pesa query status failed: {e}")
        return {"success": False, "error": str(e)}


def b2c_payment(phone: str, amount: float, occasion: str = "Payment") -> dict:
    token = _get_oauth_token()
    if not token:
        return {"success": False, "error": "Failed to authenticate with M-Pesa"}

    formatted_phone = phone.strip()
    if formatted_phone.startswith("0"):
        formatted_phone = "254" + formatted_phone[1:]
    elif formatted_phone.startswith("+"):
        formatted_phone = formatted_phone[1:]
    elif not formatted_phone.startswith("254"):
        formatted_phone = "254" + formatted_phone

    payload = {
        "InitiatorName": "testapi",
        "SecurityCredential": "testapi",
        "CommandID": "BusinessPayment",
        "Amount": int(round(amount)),
        "PartyA": settings.MPESA_SHORTCODE,
        "PartyB": formatted_phone,
        "Remarks": occasion[:100],
        "Occasion": occasion[:100],
    }

    url = f"{_get_base_url()}/mpesa/b2c/v1/paymentrequest"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    try:
        resp = httpx.post(url, json=payload, headers=headers, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        logger.error(f"M-Pesa B2C payment failed: {e}")
        return {"success": False, "error": str(e)}


def validate_credentials() -> bool:
    token = _get_oauth_token()
    return token is not None
