# app/tests/test_listing_service.py
import pytest
from datetime import datetime

from app.services import listing_service as service
from app.schemas.listing_schemas import ListingCreate, ListingUpdate, MaterialCreate
from app.models.listing import ListingStatus, MaterialType


def test_create_material(db):
    material = MaterialCreate(type="plastic", unit="kg", reference_price=15.0)
    result = service.create_material(db, material)
    assert result.type == "plastic"
    assert result.unit == "kg"
    assert result.reference_price == 15.0


def test_get_materials(db):
    service.create_material(db, MaterialCreate(type="metal", unit="kg"))
    service.create_material(db, MaterialCreate(type="glass", unit="kg"))
    materials = service.get_materials(db)
    assert len(materials) == 2


def test_get_material_by_type(db):
    service.create_material(db, MaterialCreate(type="paper", unit="kg"))
    found = service.get_material_by_type(db, "paper")
    assert found is not None
    assert found.type == "paper"
    not_found = service.get_material_by_type(db, "nonexistent")
    assert not_found is None


def test_create_listing(db):
    material = service.create_material(db, MaterialCreate(type="plastic", unit="kg"))
    listing = ListingCreate(material_id=material.id, quantity=50.0)
    result = service.create_listing(db, listing, seller_id="1")
    assert result.quantity == 50.0
    assert result.seller_id == "1"
    assert result.status == ListingStatus.ACTIVE


def test_get_listing(db):
    material = service.create_material(db, MaterialCreate(type="metal", unit="kg"))
    listing = service.create_listing(db, ListingCreate(material_id=material.id, quantity=20.0), seller_id="1")
    found = service.get_listing(db, listing.id)
    assert found is not None
    assert found.quantity == 20.0


def test_get_listing_not_found(db):
    result = service.get_listing(db, 999)
    assert result is None


def test_get_listings_with_filters(db):
    plastic = service.create_material(db, MaterialCreate(type="plastic", unit="kg"))
    metal = service.create_material(db, MaterialCreate(type="metal", unit="kg"))
    service.create_listing(db, ListingCreate(material_id=plastic.id, quantity=100.0), seller_id="1")
    service.create_listing(db, ListingCreate(material_id=metal.id, quantity=50.0), seller_id="1")
    
    listings, total = service.get_listings(db)
    assert total == 2
    
    listings, total = service.get_listings(db, filters=None, skip=0, limit=1)
    assert len(listings) == 1
    assert total == 2


def test_get_listings_filter_by_material(db):
    plastic = service.create_material(db, MaterialCreate(type="plastic", unit="kg"))
    metal = service.create_material(db, MaterialCreate(type="metal", unit="kg"))
    service.create_listing(db, ListingCreate(material_id=plastic.id, quantity=100.0), seller_id="1")
    service.create_listing(db, ListingCreate(material_id=metal.id, quantity=50.0), seller_id="1")
    
    from app.schemas.listing_schemas import ListingSearchFilters
    filters = ListingSearchFilters(material_type="plastic")
    listings, total = service.get_listings(db, filters)
    assert total == 1
    assert listings[0].material_id == plastic.id


def test_get_listings_filter_by_quantity(db):
    material = service.create_material(db, MaterialCreate(type="plastic", unit="kg"))
    service.create_listing(db, ListingCreate(material_id=material.id, quantity=100.0), seller_id="1")
    service.create_listing(db, ListingCreate(material_id=material.id, quantity=50.0), seller_id="1")
    
    from app.schemas.listing_schemas import ListingSearchFilters
    filters = ListingSearchFilters(quantity=60.0)
    listings, total = service.get_listings(db, filters)
    assert total == 1
    assert listings[0].quantity == 100.0


def test_get_listings_filter_by_status(db):
    material = service.create_material(db, MaterialCreate(type="plastic", unit="kg"))
    service.create_listing(db, ListingCreate(material_id=material.id, quantity=100.0), seller_id="1")
    
    from app.schemas.listing_schemas import ListingSearchFilters
    filters = ListingSearchFilters(status="active")
    listings, total = service.get_listings(db, filters)
    assert total == 1


def test_update_listing(db):
    material = service.create_material(db, MaterialCreate(type="plastic", unit="kg"))
    listing = service.create_listing(db, ListingCreate(material_id=material.id, quantity=30.0), seller_id="1")
    
    update = ListingUpdate(quantity=45.0, condition="updated")
    result = service.update_listing(db, listing.id, update)
    assert result.quantity == 45.0
    assert result.condition == "updated"


def test_update_listing_not_found(db):
    update = ListingUpdate(quantity=45.0)
    result = service.update_listing(db, 999, update)
    assert result is None


def test_delete_listing(db):
    material = service.create_material(db, MaterialCreate(type="plastic", unit="kg"))
    listing = service.create_listing(db, ListingCreate(material_id=material.id, quantity=10.0), seller_id="1")
    deleted = service.delete_listing(db, listing.id)
    assert deleted is True
    assert service.get_listing(db, listing.id) is None


def test_delete_listing_not_found(db):
    result = service.delete_listing(db, 999)
    assert result is False


def test_add_listing_photo(db):
    material = service.create_material(db, MaterialCreate(type="plastic", unit="kg"))
    listing = service.create_listing(db, ListingCreate(material_id=material.id, quantity=10.0), seller_id="1")
    photo = service.add_listing_photo(db, listing.id, "https://example.com/photo.jpg")
    assert photo.listing_id == listing.id
    assert photo.photo_url == "https://example.com/photo.jpg"


def test_get_recycler_inventory(db):
    from app.models.transaction import Transaction
    material = service.create_material(db, MaterialCreate(type="plastic", unit="kg"))
    listing = service.create_listing(db, ListingCreate(material_id=material.id, quantity=100.0), seller_id="1")
    listing.status = ListingStatus.COMPLETED
    tx = Transaction(listing_id=listing.id, offer_id=1, seller_id="1", recycler_id="1", agreed_price=50, final_quantity=100, final_price=5000)
    db.add(tx)
    db.commit()
    
    inventory = service.get_recycler_inventory(db, "1")
    assert len(inventory) == 1
    assert inventory[0]["material_type"] == "plastic"
    assert inventory[0]["quantity"] == 100.0
    assert inventory[0]["transaction_id"] == tx.id


def test_update_listing_status(db):
    material = service.create_material(db, MaterialCreate(type="plastic", unit="kg"))
    listing = service.create_listing(db, ListingCreate(material_id=material.id, quantity=10.0), seller_id="1")
    
    result = service.update_listing_status(db, listing.id, "completed")
    assert result.status == "completed"


def test_update_listing_status_not_found(db):
    result = service.update_listing_status(db, 999, "completed")
    assert result is None