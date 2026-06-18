# message.py
# Simple messaging between sellers and recyclers during negotiations

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from app.database import Base


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)

    sender_id = Column(String, nullable=False)
    recipient_id = Column(String, nullable=False)

    offer_id = Column(Integer, ForeignKey("offers.id"), nullable=False)

    message_text = Column(String, nullable=False)

    is_read = Column(Boolean, default=False)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    read_at = Column(DateTime, nullable=True)

    offer = relationship("Offer", foreign_keys=[offer_id])
