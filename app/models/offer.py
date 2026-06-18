from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta, timezone
import enum

from app.database import Base


class OfferStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    COUNTERED = "countered"
    EXPIRED = "expired"


class Offer(Base):
    __tablename__ = "offers"

    id = Column(Integer, primary_key=True, index=True)
    listing_id = Column(Integer, ForeignKey("listings.id"), nullable=True)
    recycler_id = Column(String, nullable=False)
    material_id = Column(Integer, ForeignKey("materials.id"), nullable=True)

    offered_price = Column(Float, nullable=False)
    quantity = Column(Float, nullable=False)

    status = Column(Enum(OfferStatus), default=OfferStatus.PENDING, nullable=False)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    expires_at = Column(DateTime, default=lambda: datetime.now(timezone.utc) + timedelta(hours=24))

    counter_price = Column(Float, nullable=True)
    counter_quantity = Column(Float, nullable=True)
    counter_note = Column(String, nullable=True)
    countered_at = Column(DateTime, nullable=True)

    note = Column(String, nullable=True)

    listing = relationship("Listing", foreign_keys=[listing_id])
    material = relationship("Material", foreign_keys=[material_id])
