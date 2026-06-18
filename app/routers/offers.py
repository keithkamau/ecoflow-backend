from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.database import get_db
from app.middleware.auth_middleware import get_current_user
from app.models.user import User
from app.schemas.offer import OfferCreate, OfferUpdate, OfferResponse, CounterOfferCreate
from app.services.offer_service import (
    get_all_offers,
    get_offer_by_id,
    create_offer,
    update_offer_status,
    counter_offer,
    delete_offer,
)

router = APIRouter(prefix="/offers", tags=["offers"])


@router.post("/", response_model=OfferResponse, status_code=status.HTTP_201_CREATED)
def create_offer_endpoint(
    offer: OfferCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    new_offer = create_offer(
        db,
        listing_id=offer.listing_id,
        recycler_id=str(current_user.id),
        offered_price=offer.offered_price,
        quantity=offer.quantity,
        note=offer.note,
        material_id=offer.material_id,
    )
    return new_offer


@router.get("/", response_model=List[OfferResponse])
def list_offers(listing_id: int = None, recycler_id: str = None, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_all_offers(db, listing_id, recycler_id)


@router.get("/{offer_id}", response_model=OfferResponse)
def get_offer(offer_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    offer = get_offer_by_id(db, offer_id)
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")
    return offer


@router.put("/{offer_id}", response_model=OfferResponse)
def update_offer(offer_id: int, update: OfferUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    offer = update_offer_status(db, offer_id, update.status, update.note)
    if offer is None:
        existing = get_offer_by_id(db, offer_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Offer not found")
        raise HTTPException(status_code=400, detail="This offer is already closed")
    return offer


@router.post("/{offer_id}/counter", response_model=OfferResponse)
def counter_offer_endpoint(offer_id: int, counter: CounterOfferCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    offer = counter_offer(
        db,
        offer_id=offer_id,
        counter_price=counter.counter_price,
        counter_quantity=counter.counter_quantity,
        counter_note=counter.counter_note,
    )
    if offer is None:
        existing = get_offer_by_id(db, offer_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Offer not found")
        raise HTTPException(status_code=400, detail="Can only counter a pending offer")
    return offer


@router.delete("/{offer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_offer_endpoint(offer_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = delete_offer(db, offer_id)
    if result is None:
        existing = get_offer_by_id(db, offer_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Offer not found")
        raise HTTPException(status_code=400, detail="Can only delete pending offers")
