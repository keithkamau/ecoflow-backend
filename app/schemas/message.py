# message.py (schema)
# keeps messaging simple — just send a text, get messages back

from pydantic import BaseModel, ConfigDict, field_validator
from datetime import datetime
from typing import Optional

# what we need to send a message
class MessageCreate(BaseModel):
    recipient_id: int
    offer_id: int
    message_text: str

    # don't allow empty messages
    @field_validator("message_text")
    def message_cannot_be_empty(cls, v):
        if not v.strip():
            raise ValueError("message cannot be empty")
        return v

# what we send back when returning messages
class MessageResponse(BaseModel):
    id: int
    sender_id: int
    recipient_id: int
    offer_id: int
    message_text: str
    is_read: bool
    created_at: datetime
    read_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)