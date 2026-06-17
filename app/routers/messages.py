from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas.message import MessageCreate, MessageResponse
from app.services.message_service import send_message, get_messages_by_offer, mark_message_as_read, get_unread_count

router = APIRouter(prefix="/messages", tags=["messages"])


@router.post("/", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
def create_message(message: MessageCreate, db: Session = Depends(get_db)):
    new_message = send_message(
        db,
        sender_id=1,
        recipient_id=message.recipient_id,
        offer_id=message.offer_id,
        message_text=message.message_text,
    )
    return new_message


@router.get("/unread/count")
def unread_count(db: Session = Depends(get_db)):
    count = get_unread_count(db, user_id=1)
    return {"count": count}


@router.get("/{offer_id}", response_model=List[MessageResponse])
def get_messages(offer_id: int, db: Session = Depends(get_db)):
    return get_messages_by_offer(db, offer_id)


@router.put("/{message_id}/read", response_model=MessageResponse)
def mark_as_read(message_id: int, db: Session = Depends(get_db)):
    message = mark_message_as_read(db, message_id)
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    return message
