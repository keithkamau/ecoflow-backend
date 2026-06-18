# message_service.py
# handles sending and retrieving messages between sellers and recyclers

from sqlalchemy.orm import Session
from datetime import datetime, timezone
from app.models.message import Message
from app.services.notification_service import create_notification


def get_messages_by_offer(db: Session, offer_id: int):
    return db.query(Message).filter(Message.offer_id == offer_id).all()


def get_unread_count(db: Session, user_id: str):
    return db.query(Message).filter(
        Message.recipient_id == user_id,
        Message.is_read == False
    ).count()

def send_message(db: Session, sender_id: str, recipient_id: str, offer_id: int, message_text: str):
    message = Message(
        sender_id=sender_id,
        recipient_id=recipient_id,
        offer_id=offer_id,
        message_text=message_text
    )
    db.add(message)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
    db.refresh(message)
    create_notification(
        db, user_id=recipient_id,
        title="New Message",
        message=f"You have a new message regarding offer #{offer_id}",
        type="message",
        reference_type="offer",
        reference_id=offer_id,
    )
    return message

def mark_message_as_read(db: Session, message_id: int):
    message = db.query(Message).filter(Message.id == message_id).first()
    if not message:
        return None
    message.is_read = True
    message.read_at = datetime.now(timezone.utc)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
    db.refresh(message)
    return message