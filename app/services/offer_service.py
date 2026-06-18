from sqlalchemy.orm import Session
from datetime import datetime, timezone
from app.models.offer import Offer, OfferStatus
from app.models.listing import Listing, ListingStatus
from app.services.notification_service import create_notification


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

    if offer.listing_id:
        listing = db.query(Listing).filter(Listing.id == offer.listing_id).first()
        if listing:
            create_notification(
                db, user_id=str(listing.seller_id),
                title="New Offer",
                message=f"New offer #{offer.id} received for KES {offer.offered_price}/unit",
                type="offer",
                reference_type="offer",
                reference_id=offer.id,
            )
    return offer


def update_offer_status(db: Session, offer_id: int, status: OfferStatus, note: str = None):
    offer = get_offer_by_id(db, offer_id)
    if not offer:
        return None
    if offer.status == status:
        return offer
    if offer.status in [OfferStatus.ACCEPTED, OfferStatus.REJECTED, OfferStatus.EXPIRED]:
        return None
    offer.status = status
    if note:
        offer.note = note

    if status == OfferStatus.ACCEPTED and offer.listing_id:
        other = db.query(Offer).filter(
            Offer.listing_id == offer.listing_id,
            Offer.id != offer_id,
            Offer.status == OfferStatus.PENDING,
        ).all()
        for o in other:
            o.status = OfferStatus.REJECTED
        listing = db.query(Listing).filter(Listing.id == offer.listing_id).first()
        if listing:
            listing.status = ListingStatus.OFFER_ACCEPTED

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
    db.refresh(offer)

    if offer.listing_id:
        listing = db.query(Listing).filter(Listing.id == offer.listing_id).first()
        if listing:
            action = status.value if hasattr(status, 'value') else status
            create_notification(
                db, user_id=str(listing.seller_id),
                title=f"Offer {action.title()}",
                message=f"Offer #{offer_id} from recycler {offer.recycler_id[:8]}... was {action}",
                type="offer",
                reference_type="offer",
                reference_id=offer_id,
            )
            if status == OfferStatus.ACCEPTED:
                create_notification(
                    db, user_id=str(offer.recycler_id),
                    title="Offer Accepted",
                    message=f"Your offer #{offer_id} for {listing.material.type} was accepted!",
                    type="offer",
                    reference_type="offer",
                    reference_id=offer_id,
                )
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

    if offer.listing_id:
        listing = db.query(Listing).filter(Listing.id == offer.listing_id).first()
        if listing:
            create_notification(
                db, user_id=str(listing.seller_id),
                title="Offer Countered",
                message=f"Offer #{offer_id} was countered at KES {counter_price}/unit",
                type="offer",
                reference_type="offer",
                reference_id=offer_id,
            )
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
