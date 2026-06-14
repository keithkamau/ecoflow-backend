from typing import List, Optional
from math import radians, cos, sin, asin, sqrt

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.listing import Material, Listing, ListingPhoto, Offer, MaterialType, ListingStatus
from app.schemas.listing_schemas import (
    OfferCreate,
    ListingCreate,
    ListingUpdate,
    MaterialCreate,
    ListingSearchFilters,
)


def haversine(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    return c * 6371


def create_material(db: Session, material: MaterialCreate) -> Material:
    db_material = Material(
        type=material.type,
        unit=material.unit,
        reference_price=material.reference_price,
        description=material.description,
    )
    db.add(db_material)
    db.commit()
    db.refresh(db_material)
    return db_material


def get_materials(db: Session) -> List[Material]:
    return db.query(Material).all()


def get_material_by_type(db: Session, material_type: str) -> Optional[Material]:
    return db.query(Material).filter(Material.type == material_type).first()


def create_listing(db: Session, listing: ListingCreate, seller_id: int) -> Listing:
    db_listing = Listing(
        seller_id=seller_id,
        material_id=listing.material_id,
        quantity=listing.quantity,
        condition=listing.condition,
        location_lat=listing.location_lat,
        location_lng=listing.location_lng,
        location_address=listing.location_address,
        price_expectation=listing.price_expectation,
        preferred_pickup_start=listing.preferred_pickup_start,
        preferred_pickup_end=listing.preferred_pickup_end,
        status=ListingStatus.ACTIVE,
    )
    db.add(db_listing)
    db.commit()
    db.refresh(db_listing)
    return db_listing


def get_listing(db: Session, listing_id: int) -> Optional[Listing]:
    return db.query(Listing).filter(Listing.id == listing_id).first()


def get_listings(
    db: Session,
    filters: Optional[ListingSearchFilters] = None,
    skip: int = 0,
    limit: int = 100,
) -> tuple[List[Listing], int]:
    query = db.query(Listing)

    if filters:
        if filters.material_type:
            material = get_material_by_type(db, filters.material_type)
            if material:
                query = query.filter(Listing.material_id == material.id)

        if filters.min_quantity is not None:
            query = query.filter(Listing.quantity >= filters.min_quantity)
        if filters.max_quantity is not None:
            query = query.filter(Listing.quantity <= filters.max_quantity)
        if filters.status:
            query = query.filter(Listing.status == filters.status)
        if filters.date_from:
            query = query.filter(Listing.created_at >= filters.date_from)
        if filters.date_to:
            query = query.filter(Listing.created_at <= filters.date_to)

    total = query.count()
    listings = query.offset(skip).limit(limit).all()

    if filters and filters.lat is not None and filters.lng is not None and filters.radius_km is not None:
        filtered = [
            l for l in listings
            if l.location_lat is not None and l.location_lng is not None
            and haversine(filters.lat, filters.lng, l.location_lat, l.location_lng) <= filters.radius_km
        ]
        listings = filtered
        total = len(listings)

    return listings, total


def update_listing(db: Session, listing_id: int, listing_update: ListingUpdate) -> Optional[Listing]:
    db_listing = get_listing(db, listing_id)
    if not db_listing:
        return None

    update_data = listing_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_listing, field, value)

    db.commit()
    db.refresh(db_listing)
    return db_listing


def delete_listing(db: Session, listing_id: int) -> bool:
    db_listing = get_listing(db, listing_id)
    if not db_listing:
        return False

    db.delete(db_listing)
    db.commit()
    return True


def add_listing_photo(db: Session, listing_id: int, photo_url: str) -> ListingPhoto:
    db_photo = ListingPhoto(listing_id=listing_id, photo_url=photo_url)
    db.add(db_photo)
    db.commit()
    db.refresh(db_photo)
    return db_photo


def get_recycler_inventory(db: Session, recycler_id: int) -> List[dict]:
    results = (
        db.query(
            Material.type.label("material_type"),
            func.sum(Listing.quantity).label("total_quantity"),
            func.count(Listing.id).label("listing_count"),
        )
        .join(Material, Listing.material_id == Material.id)
        .filter(Listing.seller_id == recycler_id)
        .filter(Listing.status == ListingStatus.COMPLETED)
        .group_by(Material.type)
        .all()
    )

    return [
        {
            "material_type": row.material_type,
            "total_quantity": float(row.total_quantity or 0),
            "listing_count": row.listing_count,
        }
        for row in results
    ]


def update_listing_status(db: Session, listing_id: int, status: str) -> Optional[Listing]:
    db_listing = get_listing(db, listing_id)
    if not db_listing:
        return None

    db_listing.status = status
    db.commit()
    db.refresh(db_listing)
    return db_listing


def create_offer(db: Session, listing_id: int, offer: OfferCreate) -> Offer:
    db_offer = Offer(
        listing_id=listing_id,
        recycler_id=offer.recycler_id,
        offered_price=offer.offered_price,
        status="pending",
    )
    db.add(db_offer)
    db.commit()
    db.refresh(db_offer)
    return db_offer


def get_offers_for_listing(db: Session, listing_id: int) -> List[Offer]:
    return db.query(Offer).filter(Offer.listing_id == listing_id).all()


def accept_offer_by_id(db: Session, offer_id: int) -> Optional[Offer]:
    db_offer = db.query(Offer).filter(Offer.id == offer_id).first()
    if not db_offer or db_offer.status != "pending":
        return None

    db_offer.status = "accepted"

    listing = get_listing(db, db_offer.listing_id)
    if listing:
        listing.status = ListingStatus.MATCHED

    db.commit()
    db.refresh(db_offer)
    return db_offer
