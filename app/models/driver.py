from sqlalchemy import Column, Integer, String, DateTime, Enum as SAEnum
from datetime import datetime, timezone
import enum

from app.database import Base


class DriverStatus(enum.Enum):
    AVAILABLE = "available"
    ON_TRIP = "on_trip"
    OFFLINE = "offline"


class Driver(Base):
    __tablename__ = "drivers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    vehicle = Column(String, nullable=False)
    license_plate = Column(String, nullable=False)
    status = Column(SAEnum(DriverStatus), default=DriverStatus.AVAILABLE, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
