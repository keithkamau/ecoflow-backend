import asyncio

from sqlalchemy.orm import Session
from datetime import datetime, timezone
from typing import List, Optional

from app.models.notification import Notification


def _broadcast(user_id: str, notification: Notification):
    from app.routers.websocket import send_notification
    payload = {
        "type": "notification",
        "id": notification.id,
        "user_id": notification.user_id,
        "title": notification.title,
        "message": notification.message,
        "type_name": notification.type,
        "reference_type": notification.reference_type,
        "reference_id": notification.reference_id,
        "is_read": notification.is_read,
        "created_at": notification.created_at.isoformat() if notification.created_at else None,
        "read_at": None,
    }
    try:
        loop = asyncio.get_running_loop()
        loop.create_task(send_notification(user_id, payload))
    except RuntimeError:
        pass


def create_notification(
    db: Session,
    user_id: str,
    title: str,
    message: str,
    type: str = "info",
    reference_type: Optional[str] = None,
    reference_id: Optional[int] = None,
) -> Notification:
    notification = Notification(
        user_id=user_id,
        title=title,
        message=message,
        type=type,
        reference_type=reference_type,
        reference_id=reference_id,
    )
    db.add(notification)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
    db.refresh(notification)
    _broadcast(user_id, notification)
    return notification


def get_notifications(db: Session, user_id: str, skip: int = 0, limit: int = 50) -> List[Notification]:
    return (
        db.query(Notification)
        .filter(Notification.user_id == user_id)
        .order_by(Notification.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_unread_count(db: Session, user_id: str) -> int:
    return db.query(Notification).filter(
        Notification.user_id == user_id,
        Notification.is_read == False,
    ).count()


def mark_notification_as_read(db: Session, notification_id: int, user_id: str) -> Optional[Notification]:
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == user_id,
    ).first()
    if not notification:
        return None
    notification.is_read = True
    notification.read_at = datetime.now(timezone.utc)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
    db.refresh(notification)
    return notification


def mark_all_as_read(db: Session, user_id: str) -> int:
    count = db.query(Notification).filter(
        Notification.user_id == user_id,
        Notification.is_read == False,
    ).update({"is_read": True, "read_at": datetime.now(timezone.utc)})
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
    return count
