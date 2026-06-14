"""Offer & Transaction models — owned by Member 3. Stub with fields required by Member 4."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, ForeignKey

from app.database import Base, GUID


class Offer(Base):
    __tablename__ = "offers"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    listing_id = Column(GUID(), ForeignKey("listings.id"), nullable=False)
    buyer_id = Column(GUID(), ForeignKey("users.id"), nullable=False)
    offered_price_per_kg = Column(Float, nullable=False, default=0.0)
    status = Column(String(20), nullable=False, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    offer_id = Column(GUID(), ForeignKey("offers.id"), nullable=True)
    listing_id = Column(GUID(), ForeignKey("listings.id"), nullable=False)
    seller_id = Column(GUID(), ForeignKey("users.id"), nullable=False, index=True)
    buyer_id = Column(GUID(), ForeignKey("users.id"), nullable=False, index=True)  # recycler
    total_amount = Column(Float, nullable=False, default=0.0)
    status = Column(String(20), nullable=False, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
