from sqlalchemy.orm import Session
from datetime import datetime, timezone
from app.models.offer import Offer, OfferStatus


def get_all_offers(db: Session, listing_id: int = None, recycler_id: str = None):
    query = db.query(Offer)
    if listing_id:
        query = query.filter(Offer.listing_id == listing_id)
    if recycler_id:
        query = query.filter(Offer.recycler_id == recycler_id)
    return query.all()


def get_offer_by_id(db: Session, offer_id: int):
    return db.query(Offer).filter(Offer.id == offer_id).first()


def create_offer(db: Session, listing_id: int = None, recycler_id: str = "", offered_price: float = 0, quantity: float = 0, note: str = None, material_id: int = None):
    offer = Offer(
        listing_id=listing_id,
        recycler_id=recycler_id,
        offered_price=offered_price,
        quantity=quantity,
        note=note,
        material_id=material_id,
    )
    db.add(offer)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
    db.refresh(offer)
    return offer


def update_offer_status(db: Session, offer_id: int, status: OfferStatus, note: str = None):
    offer = get_offer_by_id(db, offer_id)
    if not offer:
        return None
    if offer.status in [OfferStatus.ACCEPTED, OfferStatus.REJECTED, OfferStatus.EXPIRED]:
        return None
    offer.status = status
    if note:
        offer.note = note
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
    db.refresh(offer)
    return offer


def counter_offer(db: Session, offer_id: int, counter_price: float, counter_quantity: float = None, counter_note: str = None):
    offer = get_offer_by_id(db, offer_id)
    if not offer:
        return None
    if offer.status != OfferStatus.PENDING:
        return None
    offer.status = OfferStatus.COUNTERED
    offer.counter_price = counter_price
    offer.counter_quantity = counter_quantity or offer.quantity
    offer.counter_note = counter_note
    offer.countered_at = datetime.now(timezone.utc)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
    db.refresh(offer)
    return offer


def delete_offer(db: Session, offer_id: int):
    offer = get_offer_by_id(db, offer_id)
    if not offer:
        return None
    if offer.status != OfferStatus.PENDING:
        return None
    db.delete(offer)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
    return True


def is_offer_expired(offer: Offer):
    return datetime.now(timezone.utc) > offer.expires_at.replace(tzinfo=timezone.utc)
