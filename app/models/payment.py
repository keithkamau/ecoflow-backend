from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, Enum
from datetime import datetime, timezone
import enum

from app.database import Base


class PaymentMethod(enum.Enum):
    MPESA = "mpesa"


class PaymentStatus(enum.Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    REFUNDED = "refunded"


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(Integer, ForeignKey("transactions.id"), nullable=False)
    user_id = Column(Integer, nullable=False)

    amount = Column(Float, nullable=False)
    payment_method = Column(Enum(PaymentMethod), default=PaymentMethod.MPESA)
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)

    reference = Column(String, nullable=True)
    mpesa_receipt = Column(String, nullable=True)
    merchant_request_id = Column(String, nullable=True)
    checkout_request_id = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)

    commission_rate = Column(Float, default=0.05)
    commission_amount = Column(Float, nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    paid_at = Column(DateTime, nullable=True)
