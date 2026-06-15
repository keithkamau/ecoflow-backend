# message.py
# Simple messaging between sellers and recyclers during negotiations
# keeping this as basic REST for MVP, no real-time stuff yet

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from datetime import datetime, timezone

from app.database import Base

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)

    # who sent it and who it's going to
    sender_id = Column(Integer, nullable=False)
    recipient_id = Column(Integer, nullable=False)

    # messages are tied to a specific offer so conversations stay organized
    offer_id = Column(Integer, ForeignKey("offers.id"), nullable=False)

    # the actual message
    message_text = Column(String, nullable=False)

    # track if the recipient has seen it
    is_read = Column(Boolean, default=False)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # read_at is only set when the recipient actually opens the message
    read_at = Column(DateTime, nullable=True)

    # relationships — commented out until all models exist
    # sender = relationship("User", foreign_keys=[sender_id])
    # recipient = relationship("User", foreign_keys=[recipient_id])
    # offer = relationship("Offer", back_populates="messages")