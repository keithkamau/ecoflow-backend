# app/tests/test_listings.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app
from app.database import Base, get_db


# Setup test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


# Material Tests 

def test_create_material():
    response = client.post(
        "/api/v1/listings/materials",
        json={"type": "plastic", "unit": "kg", "reference_price": 15.0}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["type"] == "plastic"
    assert data["unit"] == "kg"
    assert data["reference_price"] == 15.0


def test_get_materials():
    # Create first
    client.post("/api/v1/listings/materials", json={"type": "metal", "unit": "kg"})
    
    response = client.get("/api/v1/listings/materials")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["type"] == "metal"


def test_create_duplicate_material():
    client.post("/api/v1/listings/materials", json={"type": "glass", "unit": "kg"})
    response = client.post(
        "/api/v1/listings/materials",
        json={"type": "glass", "unit": "kg"}
    )
    assert response.status_code == 400


#  Listing Tests 

def test_create_listing():
    # Create material first
    client.post("/api/v1/listings/materials", json={"type": "plastic", "unit": "kg"})
    
    response = client.post(
        "/api/v1/listings/listings",
        json={
            "material_id": 1,
            "quantity": 50.0,
            "condition": "clean and sorted",
            "location_address": "Nairobi, Kenya",
            "price_expectation": 700.0
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["quantity"] == 50.0
    assert data["status"] == "active"
    assert data["seller_id"] == 1


def test_get_listing():
    # Create material and listing
    client.post("/api/v1/listings/materials", json={"type": "paper", "unit": "kg"})
    client.post("/api/v1/listings/listings", json={"material_id": 1, "quantity": 20.0})
    
    response = client.get("/api/v1/listings/listings/1")
    assert response.status_code == 200
    data = response.json()
    assert data["quantity"] == 20.0


def test_get_listing_not_found():
    response = client.get("/api/v1/listings/listings/999")
    assert response.status_code == 404


def test_update_listing():
    # Setup
    client.post("/api/v1/listings/materials", json={"type": "metal", "unit": "kg"})
    client.post("/api/v1/listings/listings", json={"material_id": 1, "quantity": 30.0})
    
    response = client.put(
        "/api/v1/listings/listings/1",
        json={"quantity": 45.0, "condition": "updated condition"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["quantity"] == 45.0
    assert data["condition"] == "updated condition"


def test_delete_listing():
    # Setup
    client.post("/api/v1/listings/materials", json={"type": "organic", "unit": "kg"})
    client.post("/api/v1/listings/listings", json={"material_id": 1, "quantity": 10.0})
    
    response = client.delete("/api/v1/listings/listings/1")
    assert response.status_code == 204
    
    # Verify deleted
    response = client.get("/api/v1/listings/listings/1")
    assert response.status_code == 404


def test_get_listings_with_filter():
    # Setup
    client.post("/api/v1/listings/materials", json={"type": "plastic", "unit": "kg"})
    client.post("/api/v1/listings/materials", json={"type": "glass", "unit": "kg"})
    client.post("/api/v1/listings/listings", json={"material_id": 1, "quantity": 100.0})
    client.post("/api/v1/listings/listings", json={"material_id": 2, "quantity": 50.0})
    
    response = client.get("/api/v1/listings/listings")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert len(data["listings"]) == 2


def test_search_listings():
    # Setup
    client.post("/api/v1/listings/materials", json={"type": "e_waste", "unit": "pieces"})
    client.post("/api/v1/listings/listings", json={"material_id": 1, "quantity": 5.0})
    
    response = client.get("/api/v1/listings/listings/search?status=active")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1


def test_get_recycler_inventory():
    # Setup
    client.post("/api/v1/listings/materials", json={"type": "plastic", "unit": "kg"})
    client.post("/api/v1/listings/listings", json={"material_id": 1, "quantity": 100.0})
    
    response = client.get("/api/v1/listings/recyclers/inventory?recycler_id=1")
    assert response.status_code == 200
    data = response.json()
    assert data["recycler_id"] == 1
    assert "items" in data
