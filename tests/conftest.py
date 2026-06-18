import pytest
import tempfile
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.main import app
from app.database import Base, get_db
from app.utils.security import hash_password
from app.models.user import User
from app.models.listing import Material, MaterialType, Listing, ListingStatus


@pytest.fixture(scope="module")
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

    test_client = TestClient(app)
    yield test_client

    app.dependency_overrides.clear()
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture(scope="module")
def seller_token(client):
    client.post("/api/v1/auth/register", json={
        "phone": "+254700000001", "email": "seller@test.com",
        "name": "Test Seller", "password": "secret123", "role": "seller",
    })
    res = client.post("/api/v1/auth/login", json={
        "email": "seller@test.com", "password": "secret123",
    })
    return res.json()["access_token"]


@pytest.fixture(scope="module")
def recycler_token(client):
    client.post("/api/v1/auth/register", json={
        "phone": "+254700000002", "email": "recycler@test.com",
        "name": "Test Recycler", "password": "secret123", "role": "recycler",
    })
    res = client.post("/api/v1/auth/login", json={
        "email": "recycler@test.com", "password": "secret123",
    })
    return res.json()["access_token"]


@pytest.fixture(scope="module")
def sample_listing_id(client, seller_token):
    # Create a material
    client.post("/api/v1/listings/materials", json={"type": "plastic", "unit": "kg"})
    # Create a listing
    res = client.post(
        "/api/v1/listings/",
        json={"material_id": 1, "quantity": 50.0},
        headers={"Authorization": f"Bearer {seller_token}"},
    )
    return res.json()["id"]
