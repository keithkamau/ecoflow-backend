import pytest
import tempfile
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db


@pytest.fixture(scope="function")
def client():
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def override_get_db():
        db_ = TestingSessionLocal()
        try:
            yield db_
        finally:
            db_.close()

    app.dependency_overrides[get_db] = override_get_db
    Base.metadata.create_all(bind=engine)
    yield TestClient(app)
    app.dependency_overrides.clear()
    os.close(db_fd)
    os.unlink(db_path)


def _register(client, phone, email, role):
    client.post("/api/v1/auth/register", json={
        "phone": phone, "email": email,
        "name": "Test User", "password": "secret123", "role": role,
    })
    res = client.post("/api/v1/auth/login", json={"email": email, "password": "secret123"})
    return res.json()["access_token"]


# Material Tests

def test_create_material(client):
    token = _register(client, "+254700000001", "admin@test.com", "admin")
    response = client.post(
        "/api/v1/listings/materials",
        json={"type": "plastic", "unit": "kg", "reference_price": 15.0},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["type"] == "plastic"


def test_get_materials(client):
    token = _register(client, "+254700000002", "admin2@test.com", "admin")
    client.post("/api/v1/listings/materials", json={"type": "metal", "unit": "kg"},
                headers={"Authorization": f"Bearer {token}"})

    response = client.get("/api/v1/listings/materials")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["type"] == "metal"


def test_create_duplicate_material(client):
    token = _register(client, "+254700000003", "admin3@test.com", "admin")
    client.post("/api/v1/listings/materials", json={"type": "glass", "unit": "kg"},
                headers={"Authorization": f"Bearer {token}"})
    response = client.post(
        "/api/v1/listings/materials",
        json={"type": "glass", "unit": "kg"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 400


# Listing Tests

def test_create_listing(client):
    token = _register(client, "+254711111111", "l1@test.com", "seller")
    admin_token = _register(client, "+254700000004", "admin4@test.com", "admin")
    client.post("/api/v1/listings/materials", json={"type": "plastic", "unit": "kg"},
                headers={"Authorization": f"Bearer {admin_token}"})

    response = client.post(
        "/api/v1/listings/",
        json={
            "material_id": 1,
            "quantity": 50.0,
            "condition": "clean and sorted",
            "location_address": "Nairobi, Kenya",
            "price_expectation": 700.0,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["quantity"] == 50.0
    assert data["status"] == "active"


def test_get_listing(client):
    token = _register(client, "+254711111112", "l2@test.com", "seller")
    admin_token = _register(client, "+254700000005", "admin5@test.com", "admin")
    client.post("/api/v1/listings/materials", json={"type": "paper", "unit": "kg"},
                headers={"Authorization": f"Bearer {admin_token}"})
    client.post("/api/v1/listings/", json={"material_id": 1, "quantity": 20.0},
                headers={"Authorization": f"Bearer {token}"})

    response = client.get("/api/v1/listings/1")
    assert response.status_code == 200
    assert response.json()["quantity"] == 20.0


def test_get_listing_not_found(client):
    response = client.get("/api/v1/listings/999")
    assert response.status_code == 404


def test_update_listing(client):
    admin_token = _register(client, "+254700000001", "admin@test.com", "admin")
    token = _register(client, "+254711111113", "l3@test.com", "seller")
    client.post("/api/v1/listings/materials", json={"type": "metal", "unit": "kg"},
                headers={"Authorization": f"Bearer {admin_token}"})
    client.post("/api/v1/listings/", json={"material_id": 1, "quantity": 30.0},
                headers={"Authorization": f"Bearer {token}"})

    response = client.put(
        "/api/v1/listings/1",
        json={"quantity": 45.0, "condition": "updated condition"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["quantity"] == 45.0


def test_delete_listing(client):
    admin_token = _register(client, "+254700000002", "admin2@test.com", "admin")
    token = _register(client, "+254711111114", "l4@test.com", "seller")
    client.post("/api/v1/listings/materials", json={"type": "organic", "unit": "kg"},
                headers={"Authorization": f"Bearer {admin_token}"})
    client.post("/api/v1/listings/", json={"material_id": 1, "quantity": 10.0},
                headers={"Authorization": f"Bearer {token}"})

    response = client.delete("/api/v1/listings/1", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 204

    response = client.get("/api/v1/listings/1")
    assert response.status_code == 404


def test_get_listings_with_filter(client):
    admin_token = _register(client, "+254700000006", "admin6@test.com", "admin")
    token = _register(client, "+254711111115", "l5@test.com", "seller")
    client.post("/api/v1/listings/materials", json={"type": "plastic", "unit": "kg"},
                headers={"Authorization": f"Bearer {admin_token}"})
    client.post("/api/v1/listings/materials", json={"type": "glass", "unit": "kg"},
                headers={"Authorization": f"Bearer {admin_token}"})
    client.post("/api/v1/listings/", json={"material_id": 1, "quantity": 100.0},
                headers={"Authorization": f"Bearer {token}"})
    client.post("/api/v1/listings/", json={"material_id": 2, "quantity": 50.0},
                headers={"Authorization": f"Bearer {token}"})

    response = client.get("/api/v1/listings/")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert len(data["listings"]) == 2


def test_search_listings(client):
    admin_token = _register(client, "+254700000007", "admin7@test.com", "admin")
    token = _register(client, "+254711111116", "l6@test.com", "seller")
    client.post("/api/v1/listings/materials", json={"type": "e_waste", "unit": "pieces"},
                headers={"Authorization": f"Bearer {admin_token}"})
    client.post("/api/v1/listings/", json={"material_id": 1, "quantity": 5.0},
                headers={"Authorization": f"Bearer {token}"})

    response = client.get("/api/v1/listings/search?status=active")
    assert response.status_code == 200
    assert response.json()["total"] >= 1


def test_get_recycler_inventory(client):
    token = _register(client, "+254711111117", "l7@test.com", "seller")
    admin_token = _register(client, "+254700000008", "admin8@test.com", "admin")
    client.post("/api/v1/listings/materials", json={"type": "plastic", "unit": "kg"},
                headers={"Authorization": f"Bearer {admin_token}"})
    client.post("/api/v1/listings/", json={"material_id": 1, "quantity": 100.0},
                headers={"Authorization": f"Bearer {token}"})

    response = client.get("/api/v1/listings/recyclers/inventory?recycler_id=1",
                          headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["recycler_id"] == "1"
    assert "items" in data
