"""Listing model — owned by Member 2. Stub with fields required by Member 4 analytics."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Text

from app.database import Base, GUID


class Listing(Base):
    __tablename__ = "listings"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    seller_id = Column(GUID(), ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(255), nullable=False, default="")
    description = Column(Text, nullable=True)
    material_type = Column(String(50), nullable=False, default="other")
    weight = Column(Float, nullable=False, default=0.0)
    price_per_kg = Column(Float, nullable=False, default=0.0)
    status = Column(String(20), nullable=False, default="active")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
