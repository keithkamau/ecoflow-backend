"""Payment model — owned by Member 3."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, ForeignKey

from app.database import Base, GUID


class Payment(Base):
    __tablename__ = "payments"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    transaction_id = Column(GUID(), ForeignKey("transactions.id"), nullable=False)
    amount = Column(Float, nullable=False, default=0.0)
    method = Column(String(20), nullable=False, default="mpesa")  # mpesa | card
    status = Column(String(20), nullable=False, default="pending")
    reference = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
