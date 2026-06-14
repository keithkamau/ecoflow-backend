"""Message model — owned by Member 3."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Boolean

from app.database import Base, GUID


class Message(Base):
    __tablename__ = "messages"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    sender_id = Column(GUID(), ForeignKey("users.id"), nullable=False)
    recipient_id = Column(GUID(), ForeignKey("users.id"), nullable=False)
    listing_id = Column(GUID(), ForeignKey("listings.id"), nullable=True)
    body = Column(Text, nullable=False, default="")
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
