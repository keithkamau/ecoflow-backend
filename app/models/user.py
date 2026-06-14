"""User model — owned by Member 1. Stub with fields required by Member 4 foreign keys."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, Float, DateTime

from app.database import Base, GUID


class User(Base):
    __tablename__ = "users"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False, default="")
    full_name = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    role = Column(String(20), nullable=False, default="seller")  # seller | recycler | admin
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    # Location fields used by Member 4's nearby-query endpoint
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    address = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
