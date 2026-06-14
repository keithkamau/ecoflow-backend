"""Offer/Transaction endpoints — owned by Member 3."""
from fastapi import APIRouter

router = APIRouter(prefix="/offers", tags=["offers"])


@router.get("/")
def list_offers():
    return {"detail": "Not implemented — Member 3"}


@router.post("/")
def create_offer():
    return {"detail": "Not implemented — Member 3"}
