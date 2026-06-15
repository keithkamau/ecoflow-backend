# app/tests/test_listing_models.py
from app.models.listing import MaterialType, ListingStatus, Material, Listing, ListingPhoto


def test_material_type_enum():
    assert MaterialType.PLASTIC == "plastic"
    assert MaterialType.METAL == "metal"
    assert MaterialType.E_WASTE == "e_waste"


def test_listing_status_enum():
    assert ListingStatus.ACTIVE == "active"
    assert ListingStatus.MATCHED == "matched"
    assert ListingStatus.COMPLETED == "completed"
    assert ListingStatus.EXPIRED == "expired"


def test_material_tablename():
    assert Material.__tablename__ == "materials"


def test_listing_tablename():
    assert Listing.__tablename__ == "listings"


def test_listing_photo_tablename():
    assert ListingPhoto.__tablename__ == "listing_photos"


def test_listing_default_status():
    from sqlalchemy import Column, Enum
    status_col = None
    for col in Listing.__table__.columns:
        if col.name == "status":
            status_col = col
            break
    assert status_col is not None
    assert status_col.default.arg == ListingStatus.ACTIVE