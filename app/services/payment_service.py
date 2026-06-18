import uuid
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from app.config import settings
from app.models.payment import Payment, PaymentStatus, PaymentMethod
from app.models.transaction import Transaction, TransactionStatus
from app.utils.daraja import stk_push, query_status
from app.services.notification_service import create_notification


def get_payment_by_transaction(db: Session, transaction_id: int):
    return db.query(Payment).filter(Payment.transaction_id == transaction_id).first()


def get_all_payments(db: Session):
    return db.query(Payment).all()


def get_payment_by_id(db: Session, payment_id: int):
    return db.query(Payment).filter(Payment.id == payment_id).first()


def initiate_payment(db: Session, transaction_id: int, user_id: str, amount: float, payment_method: PaymentMethod, phone_number: str = None):
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not transaction:
        return None

    commission_rate = settings.COMMISSION_RATE
    commission_amount = amount * commission_rate

    if payment_method == PaymentMethod.MPESA and phone_number:
        result = stk_push(
            phone=phone_number,
            amount=amount,
            account_ref=f"TXN{transaction_id}",
            transaction_desc="Waste Hub Payment",
        )

        if result["success"]:
            payment = Payment(
                transaction_id=transaction_id,
                user_id=user_id,
                amount=amount,
                payment_method=payment_method,
                status=PaymentStatus.PENDING,
                reference=result.get("checkout_request_id"),
                merchant_request_id=result.get("merchant_request_id"),
                checkout_request_id=result.get("checkout_request_id"),
                phone_number=phone_number,
                commission_rate=commission_rate,
                commission_amount=commission_amount,
            )
        else:
            mock_ref = f"DEMO-{uuid.uuid4().hex[:8].upper()}"
            payment = Payment(
                transaction_id=transaction_id,
                user_id=user_id,
                amount=amount,
                payment_method=payment_method,
                status=PaymentStatus.PENDING,
                reference=mock_ref,
                checkout_request_id=mock_ref,
                phone_number=phone_number,
                commission_rate=commission_rate,
                commission_amount=commission_amount,
            )
        db.add(payment)
        try:
            db.commit()
        except Exception:
            db.rollback()
            raise
        db.refresh(payment)
        return payment

    mock_reference = f"MOCK-{uuid.uuid4().hex[:8].upper()}"
    payment = Payment(
        transaction_id=transaction_id,
        user_id=user_id,
        amount=amount,
        payment_method=payment_method,
        status=PaymentStatus.PENDING,
        reference=mock_reference,
        phone_number=phone_number,
        commission_rate=commission_rate,
        commission_amount=commission_amount,
    )
    db.add(payment)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
    db.refresh(payment)
    return payment


def complete_payment(db: Session, checkout_request_id: str, mpesa_receipt: str, result_desc: str = None):
    payment = db.query(Payment).filter(Payment.checkout_request_id == checkout_request_id).first()
    if not payment:
        payment = db.query(Payment).filter(Payment.reference == checkout_request_id).first()
    if not payment:
        return None

    payment.status = PaymentStatus.SUCCESS
    payment.mpesa_receipt = mpesa_receipt
    payment.paid_at = datetime.now(timezone.utc)

    transaction = db.query(Transaction).filter(Transaction.id == payment.transaction_id).first()
    if transaction:
        transaction.status = TransactionStatus.COMPLETED
        transaction.completed_at = datetime.now(timezone.utc)

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
    db.refresh(payment)

    if transaction:
        create_notification(
            db, user_id=str(transaction.seller_id),
            title="Payment Received",
            message=f"Payment for transaction #{transaction.id} completed. Receipt: {mpesa_receipt or 'N/A'}",
            type="payment",
            reference_type="payment",
            reference_id=payment.id,
        )
        create_notification(
            db, user_id=str(transaction.recycler_id),
            title="Payment Sent",
            message=f"Your payment for transaction #{transaction.id} was successful",
            type="payment",
            reference_type="payment",
            reference_id=payment.id,
        )
    return payment


def confirm_payment_by_id(db: Session, payment_id: int, mpesa_receipt: str):
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        return None
    payment.status = PaymentStatus.SUCCESS
    payment.mpesa_receipt = mpesa_receipt
    payment.paid_at = datetime.now(timezone.utc)
    transaction = db.query(Transaction).filter(Transaction.id == payment.transaction_id).first()
    if transaction:
        transaction.status = TransactionStatus.COMPLETED
        transaction.completed_at = datetime.now(timezone.utc)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
    db.refresh(payment)

    if transaction:
        create_notification(
            db, user_id=str(transaction.recycler_id),
            title="Payment Confirmed",
            message=f"Payment for transaction #{transaction.id} confirmed. Receipt: {mpesa_receipt}",
            type="payment",
            reference_type="payment",
            reference_id=payment.id,
        )
    return payment


def fail_payment(db: Session, checkout_request_id: str, result_desc: str = None):
    payment = db.query(Payment).filter(Payment.checkout_request_id == checkout_request_id).first()
    if not payment:
        return None

    payment.status = PaymentStatus.FAILED
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
    db.refresh(payment)

    create_notification(
        db, user_id=str(payment.user_id),
        title="Payment Failed",
        message=f"Payment of KES {payment.amount} failed. {result_desc or ''}",
        type="payment",
        reference_type="payment",
        reference_id=payment.id,
    )
    return payment


def query_payment_status(db: Session, payment_id: int):
    payment = get_payment_by_id(db, payment_id)
    if not payment:
        return None
    if payment.checkout_request_id:
        result = query_status(payment.checkout_request_id)
        return {"payment": payment, "mpesa_status": result}
    return {"payment": payment, "mpesa_status": None}
