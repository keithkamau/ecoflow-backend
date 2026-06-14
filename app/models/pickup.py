import uuid
import enum
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, Text, ForeignKey, Enum as SAEnum, JSON
from sqlalchemy.orm import relationship

from app.database import Base, GUID


class PickupStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class DriverStatus(str, enum.Enum):
    AVAILABLE = "available"
    ON_PICKUP = "on_pickup"
    OFF_DUTY = "off_duty"


class Driver(Base):
    __tablename__ = "drivers"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    recycler_id = Column(GUID(), ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=False)
    vehicle = Column(String(50), nullable=False)
    license_plate = Column(String(20), nullable=False, unique=True)
    status = Column(SAEnum(DriverStatus), default=DriverStatus.AVAILABLE, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    pickups = relationship("Pickup", back_populates="driver")


class Pickup(Base):
    __tablename__ = "pickups"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    transaction_id = Column(GUID(), ForeignKey("transactions.id"), nullable=False, index=True)
    scheduled_time = Column(DateTime, nullable=False)
    actual_time = Column(DateTime, nullable=True)
    # Stored as JSON: {"lat": float, "lng": float, "address": str}
    pickup_location = Column(JSON, nullable=False)
    status = Column(SAEnum(PickupStatus), default=PickupStatus.PENDING, nullable=False)
    driver_id = Column(GUID(), ForeignKey("drivers.id"), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    driver = relationship("Driver", back_populates="pickups")
    proof = relationship("ProofOfPickup", back_populates="pickup", uselist=False)


class ProofOfPickup(Base):
    __tablename__ = "proof_of_pickups"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    pickup_id = Column(GUID(), ForeignKey("pickups.id"), unique=True, nullable=False)
    weight = Column(Float, nullable=False)
    material_type = Column(String(50), nullable=False, default="other")
    photos = Column(JSON, nullable=False, default=list)  # list of S3 URLs
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    driver_signature = Column(String(500), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    pickup = relationship("Pickup", back_populates="proof")
