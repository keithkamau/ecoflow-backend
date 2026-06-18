from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import enum

from app.database import Base


class TransactionStatus(str, enum.Enum):
    OFFER_ACCEPTED = "offer_accepted"
    PICKUP_SCHEDULED = "pickup_scheduled"
    PICKUP_COMPLETED = "pickup_completed"
    PAYMENT_PENDING = "payment_pending"
    COMPLETED = "completed"
    DISPUTED = "disputed"
    CANCELLED = "cancelled"


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    listing_id = Column(Integer, ForeignKey("listings.id"), nullable=False)
    offer_id = Column(Integer, ForeignKey("offers.id"), nullable=False)

    seller_id = Column(String, nullable=False)
    recycler_id = Column(String, nullable=False)

    agreed_price = Column(Float, nullable=False)
    final_quantity = Column(Float, nullable=False)
    final_price = Column(Float, nullable=False)

    status = Column(Enum(TransactionStatus), default=TransactionStatus.OFFER_ACCEPTED)

    pickup_notes = Column(String, nullable=True)
    pickup_scheduled_at = Column(DateTime, nullable=True)
    disputed_at = Column(DateTime, nullable=True)
    dispute_reason = Column(String, nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime, nullable=True)

    listing = relationship("Listing", foreign_keys=[listing_id])
    offer = relationship("Offer", foreign_keys=[offer_id])
