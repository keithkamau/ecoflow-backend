from sqlalchemy.orm import Session
from datetime import datetime, timezone
from app.models.transaction import Transaction, TransactionStatus
from app.models.offer import Offer, OfferStatus


VALID_TRANSITIONS = {
    TransactionStatus.OFFER_ACCEPTED: [
        TransactionStatus.PICKUP_SCHEDULED,
        TransactionStatus.CANCELLED,
    ],
    TransactionStatus.PICKUP_SCHEDULED: [
        TransactionStatus.PICKUP_COMPLETED,
        TransactionStatus.CANCELLED,
    ],
    TransactionStatus.PICKUP_COMPLETED: [
        TransactionStatus.PAYMENT_PENDING,
        TransactionStatus.CANCELLED,
    ],
    TransactionStatus.PAYMENT_PENDING: [
        TransactionStatus.COMPLETED,
        TransactionStatus.DISPUTED,
    ],
    TransactionStatus.COMPLETED: [],
    TransactionStatus.DISPUTED: [TransactionStatus.COMPLETED],
    TransactionStatus.CANCELLED: [],
}


def get_all_transactions(db: Session, seller_id: str = None, recycler_id: str = None):
    query = db.query(Transaction)
    if seller_id:
        query = query.filter(Transaction.seller_id == seller_id)
    if recycler_id:
        query = query.filter(Transaction.recycler_id == recycler_id)
    return query.all()


def get_transaction_by_id(db: Session, transaction_id: int):
    return db.query(Transaction).filter(Transaction.id == transaction_id).first()


def create_transaction(
    db: Session, offer_id: int, listing_id: int, seller_id: str,
    recycler_id: str, agreed_price: float, final_quantity: float, final_price: float
):
    offer = db.query(Offer).filter(Offer.id == offer_id).first()
    if not offer:
        return None
    if offer.status != OfferStatus.ACCEPTED:
        return False
    existing = db.query(Transaction).filter(Transaction.offer_id == offer_id).first()
    if existing:
        return False
    transaction = Transaction(
        offer_id=offer_id,
        listing_id=listing_id,
        seller_id=seller_id,
        recycler_id=recycler_id,
        agreed_price=agreed_price,
        final_quantity=final_quantity,
        final_price=final_price,
    )
    db.add(transaction)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
    db.refresh(transaction)
    return transaction


def update_transaction_status(
    db: Session, transaction_id: int, status: TransactionStatus,
    pickup_notes: str = None, dispute_reason: str = None
):
    transaction = get_transaction_by_id(db, transaction_id)
    if not transaction:
        return None

    allowed = VALID_TRANSITIONS.get(transaction.status, [])
    if status not in allowed:
        return None

    transaction.status = status

    if status == TransactionStatus.PICKUP_SCHEDULED:
        transaction.pickup_scheduled_at = datetime.now(timezone.utc)
        if pickup_notes:
            transaction.pickup_notes = pickup_notes

    if status == TransactionStatus.DISPUTED:
        transaction.disputed_at = datetime.now(timezone.utc)
        if dispute_reason:
            transaction.dispute_reason = dispute_reason

    if status == TransactionStatus.COMPLETED:
        transaction.completed_at = datetime.now(timezone.utc)

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
    db.refresh(transaction)
    return transaction
