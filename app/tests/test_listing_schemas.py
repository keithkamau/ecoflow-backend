# app/tests/test_listing_schemas.py
import pytest
from datetime import datetime

from app.schemas.listing_schemas import (
    MaterialCreate,
    MaterialResponse,
    ListingCreate,
    ListingUpdate,
    ListingResponse,
    ListingSearchFilters,
    ListingSearchResponse,
    InventoryItem,
    InventoryResponse,
)


def test_material_create():
    data = MaterialCreate(type="plastic", unit="kg", reference_price=15.0)
    assert data.type == "plastic"
    assert data.unit == "kg"
    assert data.reference_price == 15.0


def test_material_create_defaults():
    data = MaterialCreate(type="metal")
    assert data.unit == "kg"
    assert data.reference_price is None
    assert data.description is None


def test_listing_create():
    data = ListingCreate(material_id=1, quantity=50.0)
    assert data.material_id == 1
    assert data.quantity == 50.0
    assert data.condition is None


def test_listing_create_validation():
    with pytest.raises(ValueError):
        ListingCreate(material_id=1, quantity=-5.0)


def test_listing_update_partial():
    data = ListingUpdate(quantity=45.0)
    assert data.quantity == 45.0
    assert data.material_id is None
    assert data.condition is None


def test_listing_update_validation():
    with pytest.raises(ValueError):
        ListingUpdate(quantity=-1.0)


def test_listing_search_filters():
    filters = ListingSearchFilters(material_type="plastic", min_quantity=10.0)
    assert filters.material_type == "plastic"
    assert filters.min_quantity == 10.0
    assert filters.max_quantity is None


def test_listing_search_response():
    response = ListingSearchResponse(total=5, listings=[])
    assert response.total == 5
    assert response.listings == []


def test_inventory_item():
    item = InventoryItem(material_type="plastic", total_quantity=100.0, listing_count=2)
    assert item.material_type == "plastic"
    assert item.total_quantity == 100.0


def test_inventory_response():
    response = InventoryResponse(recycler_id=1, items=[])
    assert response.recycler_id == 1
    assert response.items == []