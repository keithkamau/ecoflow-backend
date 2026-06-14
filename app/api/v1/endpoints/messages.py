"""Messaging endpoints — owned by Member 3."""
from fastapi import APIRouter

router = APIRouter(prefix="/messages", tags=["messages"])


@router.get("/")
def list_messages():
    return {"detail": "Not implemented — Member 3"}
