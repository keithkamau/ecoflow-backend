from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.middleware.auth_middleware import get_current_user
from app.models.user import User
from app.schemas.payment import PaymentCreate, PaymentResponse
from app.services.payment_service import (
    initiate_payment,
    get_payment_by_transaction,
    get_all_payments,
    get_payment_by_id,
    complete_payment,
    fail_payment,
    query_payment_status,
)

router = APIRouter(prefix="/payments", tags=["payments"])


@router.post("/", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
def create_payment(payment: PaymentCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = initiate_payment(
        db,
        transaction_id=payment.transaction_id,
        user_id=payment.user_id,
        amount=payment.amount,
        payment_method=payment.payment_method,
        phone_number=payment.phone_number,
    )
    if result is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return result


@router.post("/callback")
async def mpesa_callback(request: Request, db: Session = Depends(get_db)):
    body = await request.json()
    body_obj = body.get("Body", {})
    stk_callback = body_obj.get("stkCallback", {})
    result_code = stk_callback.get("ResultCode")
    checkout_request_id = stk_callback.get("CheckoutRequestID")
    result_desc = stk_callback.get("ResultDesc")

    if result_code == 0:
        metadata = stk_callback.get("CallbackMetadata", {})
        items = metadata.get("Item", [])
        mpesa_receipt = None
        for item in items:
            if item.get("Name") == "MpesaReceiptNumber":
                mpesa_receipt = item.get("Value")
                break
        if checkout_request_id:
            complete_payment(db, checkout_request_id, mpesa_receipt, result_desc)
    else:
        if checkout_request_id:
            fail_payment(db, checkout_request_id, result_desc)

    return {"ResultCode": 0, "ResultDesc": "Success"}


@router.post("/{payment_id}/confirm")
def confirm_payment_manual(payment_id: int, mpesa_receipt: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    from app.services.payment_service import confirm_payment_by_id
    result = confirm_payment_by_id(db, payment_id, mpesa_receipt)
    if not result:
        raise HTTPException(status_code=404, detail="Payment not found")
    return result


@router.post("/{payment_id}/fail")
def fail_payment_manual(payment_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    payment = get_payment_by_id(db, payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    if not payment.checkout_request_id:
        raise HTTPException(status_code=400, detail="No M-Pesa checkout request for this payment")
    result = fail_payment(db, payment.checkout_request_id)
    if not result:
        raise HTTPException(status_code=400, detail="Failed to update payment")
    return result


@router.get("/", response_model=List[PaymentResponse])
def list_payments(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_all_payments(db)


@router.get("/detail/{payment_id}", response_model=PaymentResponse)
def get_payment_detail(payment_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    payment = get_payment_by_id(db, payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment


@router.get("/{payment_id}/status")
def check_payment_status(payment_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = query_payment_status(db, payment_id)
    if not result:
        raise HTTPException(status_code=404, detail="Payment not found")
    return result


@router.get("/{transaction_id}", response_model=PaymentResponse)
def get_payment(transaction_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    payment = get_payment_by_transaction(db, transaction_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment
