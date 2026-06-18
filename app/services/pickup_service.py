import uuid
from typing import List, Optional
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.pickup import Pickup, PickupStatus
from app.models.transaction import Transaction, TransactionStatus
from app.models.listing import Listing, ListingStatus
from app.models.user import User
from app.models.payment import PaymentMethod
from app.schemas.pickup import PickupCreate, PickupUpdate
from app.services.notification_service import create_notification
from app.services.payment_service import initiate_payment


def create_pickup(db: Session, data: PickupCreate) -> Pickup:
    pickup = Pickup(
        transaction_id=data.transaction_id,
        scheduled_time=data.scheduled_time,
        pickup_address=data.pickup_address,
        notes=data.notes,
    )
    db.add(pickup)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
    db.refresh(pickup)
    return pickup


def get_pickup(db: Session, pickup_id: int) -> Optional[Pickup]:
    return db.query(Pickup).filter(Pickup.id == pickup_id).first()


def get_pickups(db: Session, skip: int = 0, limit: int = 100) -> tuple[List[Pickup], int]:
    total = db.query(Pickup).count()
    pickups = db.query(Pickup).order_by(Pickup.created_at.desc()).offset(skip).limit(limit).all()
    return pickups, total


def update_pickup(db: Session, pickup_id: int, data: PickupUpdate) -> Optional[Pickup]:
    pickup = get_pickup(db, pickup_id)
    if not pickup:
        return None

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(pickup, field, value)

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
    db.refresh(pickup)
    return pickup


def assign_driver(db: Session, pickup_id: int, driver_id: int) -> Optional[Pickup]:
    pickup = get_pickup(db, pickup_id)
    if not pickup:
        return None

    pickup.driver_id = driver_id
    if pickup.status == PickupStatus.SCHEDULED:
        pickup.status = PickupStatus.ON_THE_WAY

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
    db.refresh(pickup)
    return pickup


def upload_proof(db: Session, pickup_id: int, proof_url: str, weight: Optional[float] = None, signature: Optional[str] = None) -> Optional[Pickup]:
    pickup = get_pickup(db, pickup_id)
    if not pickup:
        return None

    pickup.proof_url = proof_url
    if weight is not None:
        pickup.weight = weight
    if signature is not None:
        pickup.signature = signature
    pickup.status = PickupStatus.COMPLETED
    pickup.actual_time = datetime.utcnow()

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
    db.refresh(pickup)
    return pickup


def self_complete_pickup(db: Session, pickup_id: int) -> Optional[Pickup]:
    pickup = get_pickup(db, pickup_id)
    if not pickup:
        return None
    if pickup.status in (PickupStatus.COMPLETED, PickupStatus.CANCELLED):
        return None

    pickup.status = PickupStatus.COMPLETED
    pickup.actual_time = datetime.now(timezone.utc)

    transaction = db.query(Transaction).filter(Transaction.id == pickup.transaction_id).first()
    if transaction:
        listing = db.query(Listing).filter(Listing.id == transaction.listing_id).first()
        if listing:
            listing.status = ListingStatus.PICKUP_COMPLETE

        transaction.status = TransactionStatus.PAYMENT_PENDING

        recycler = db.query(User).filter(User.id == uuid.UUID(transaction.recycler_id)).first() if transaction.recycler_id else None
        phone = recycler.phone if recycler else None

        initiate_payment(
            db,
            transaction_id=transaction.id,
            user_id=str(transaction.recycler_id),
            amount=transaction.final_price,
            payment_method=PaymentMethod.MPESA,
            phone_number=phone,
        )

        create_notification(
            db, user_id=str(transaction.seller_id),
            title="Successful Delivery",
            message=f"Recycler has collected the waste for transaction #{transaction.id}. Delivery complete!",
            type="delivery",
            reference_type="transaction",
            reference_id=transaction.id,
        )
        create_notification(
            db, user_id=str(transaction.recycler_id),
            title="Pickup Complete",
            message=f"You confirmed collection for transaction #{transaction.id}.",
            type="delivery",
            reference_type="transaction",
            reference_id=transaction.id,
        )

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
    db.refresh(pickup)
    return pickup
