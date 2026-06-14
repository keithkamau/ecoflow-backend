import uuid
from datetime import datetime, timedelta

import pytest

FUTURE = (datetime.utcnow() + timedelta(hours=2)).isoformat()
LOCATION = {"lat": -1.2921, "lng": 36.8219, "address": "Nairobi CBD"}


# ── Pickup scheduling ─────────────────────────────────────────────────────────

def test_schedule_pickup_returns_201(client, seller_headers, transaction_id):
    payload = {
        "transaction_id": str(transaction_id),
        "scheduled_time": FUTURE,
        "pickup_location": LOCATION,
    }
    resp = client.post("/api/v1/pickups", json=payload, headers=seller_headers)
    assert resp.status_code == 201
    body = resp.json()
    assert body["status"] == "pending"
    assert body["pickup_location"]["address"] == "Nairobi CBD"
    assert "id" in body


def test_schedule_pickup_stores_notes(client, seller_headers, transaction_id):
    payload = {
        "transaction_id": str(transaction_id),
        "scheduled_time": FUTURE,
        "pickup_location": LOCATION,
        "notes": "Call before arrival",
    }
    resp = client.post("/api/v1/pickups", json=payload, headers=seller_headers)
    assert resp.status_code == 201
    assert resp.json()["notes"] == "Call before arrival"


def test_schedule_pickup_requires_auth(client, transaction_id):
    payload = {
        "transaction_id": str(transaction_id),
        "scheduled_time": FUTURE,
        "pickup_location": LOCATION,
    }
    resp = client.post("/api/v1/pickups", json=payload)
    assert resp.status_code in (401, 403)


# ── Listing pickups ───────────────────────────────────────────────────────────

def test_list_pickups_empty(client, seller_headers):
    resp = client.get("/api/v1/pickups", headers=seller_headers)
    assert resp.status_code == 200
    assert resp.json() == []


def test_list_pickups_returns_created(client, seller_headers, transaction_id):
    payload = {
        "transaction_id": str(transaction_id),
        "scheduled_time": FUTURE,
        "pickup_location": LOCATION,
    }
    client.post("/api/v1/pickups", json=payload, headers=seller_headers)
    resp = client.get("/api/v1/pickups", headers=seller_headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 1


# ── Get single pickup ─────────────────────────────────────────────────────────

def test_get_pickup_by_id(client, seller_headers, transaction_id):
    payload = {
        "transaction_id": str(transaction_id),
        "scheduled_time": FUTURE,
        "pickup_location": LOCATION,
    }
    created = client.post("/api/v1/pickups", json=payload, headers=seller_headers).json()
    resp = client.get(f"/api/v1/pickups/{created['id']}", headers=seller_headers)
    assert resp.status_code == 200
    assert resp.json()["id"] == created["id"]


def test_get_pickup_not_found(client, seller_headers):
    resp = client.get(f"/api/v1/pickups/{uuid.uuid4()}", headers=seller_headers)
    assert resp.status_code == 404


# ── Update pickup ─────────────────────────────────────────────────────────────

def test_update_pickup_status(client, seller_headers, transaction_id):
    payload = {
        "transaction_id": str(transaction_id),
        "scheduled_time": FUTURE,
        "pickup_location": LOCATION,
    }
    created = client.post("/api/v1/pickups", json=payload, headers=seller_headers).json()
    resp = client.put(
        f"/api/v1/pickups/{created['id']}",
        json={"status": "confirmed"},
        headers=seller_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "confirmed"


# ── Proof of pickup ───────────────────────────────────────────────────────────

def test_upload_proof_completes_pickup(client, seller_headers, transaction_id):
    payload = {
        "transaction_id": str(transaction_id),
        "scheduled_time": FUTURE,
        "pickup_location": LOCATION,
    }
    created = client.post("/api/v1/pickups", json=payload, headers=seller_headers).json()
    proof_payload = {
        "weight": 12.5,
        "material_type": "plastic",
        "photos": ["https://s3.example.com/photo1.jpg"],
    }
    resp = client.post(
        f"/api/v1/pickups/{created['id']}/proof",
        json=proof_payload,
        headers=seller_headers,
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["weight"] == 12.5
    assert body["material_type"] == "plastic"

    pickup_resp = client.get(f"/api/v1/pickups/{created['id']}", headers=seller_headers).json()
    assert pickup_resp["status"] == "completed"


def test_upload_proof_duplicate_rejected(client, seller_headers, transaction_id):
    payload = {
        "transaction_id": str(transaction_id),
        "scheduled_time": FUTURE,
        "pickup_location": LOCATION,
    }
    created = client.post("/api/v1/pickups", json=payload, headers=seller_headers).json()
    proof_payload = {"weight": 5.0, "material_type": "metal"}
    client.post(f"/api/v1/pickups/{created['id']}/proof", json=proof_payload, headers=seller_headers)
    resp = client.post(f"/api/v1/pickups/{created['id']}/proof", json=proof_payload, headers=seller_headers)
    assert resp.status_code == 400


# ── Driver management ─────────────────────────────────────────────────────────

def test_create_driver_as_recycler(client, recycler_headers):
    payload = {
        "name": "John Mwangi",
        "phone": "0712345678",
        "vehicle": "Toyota Hilux",
        "license_plate": "KCA 123A",
    }
    resp = client.post("/api/v1/drivers", json=payload, headers=recycler_headers)
    assert resp.status_code == 201
    body = resp.json()
    assert body["name"] == "John Mwangi"
    assert body["status"] == "available"


def test_create_driver_seller_forbidden(client, seller_headers):
    payload = {
        "name": "Jane Doe",
        "phone": "0700000000",
        "vehicle": "Nissan",
        "license_plate": "KCA 999Z",
    }
    resp = client.post("/api/v1/drivers", json=payload, headers=seller_headers)
    assert resp.status_code == 403


def test_duplicate_license_plate_rejected(client, recycler_headers):
    payload = {
        "name": "Driver One",
        "phone": "0711111111",
        "vehicle": "Toyota",
        "license_plate": "KCB 001X",
    }
    client.post("/api/v1/drivers", json=payload, headers=recycler_headers)
    resp = client.post("/api/v1/drivers", json=payload, headers=recycler_headers)
    assert resp.status_code == 400


def test_get_available_drivers(client, recycler_headers):
    payload = {
        "name": "Driver Two",
        "phone": "0722222222",
        "vehicle": "Mitsubishi",
        "license_plate": "KCC 002Y",
    }
    client.post("/api/v1/drivers", json=payload, headers=recycler_headers)
    resp = client.get("/api/v1/drivers", headers=recycler_headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 1


# ── Distance calculation ──────────────────────────────────────────────────────

def test_distance_nairobi_to_thika(client, seller_headers):
    payload = {
        "origin_lat": -1.2921,
        "origin_lng": 36.8219,
        "dest_lat": -1.0332,
        "dest_lng": 37.0693,
        "base_price": 500.0,
    }
    resp = client.post("/api/v1/locations/distance", json=payload, headers=seller_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert 35 < body["distance_km"] < 55  # Nairobi → Thika haversine ~40 km
    assert body["adjusted_price"] > 500.0
    assert body["surcharge"] > 0


def test_distance_nearby_same_point(client, seller_headers):
    payload = {
        "origin_lat": -1.2921,
        "origin_lng": 36.8219,
        "dest_lat": -1.2921,
        "dest_lng": 36.8219,
        "base_price": 200.0,
    }
    resp = client.post("/api/v1/locations/distance", json=payload, headers=seller_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["distance_km"] == 0.0
    assert body["surcharge"] == 0.0
    assert body["adjusted_price"] == 200.0


# ── Environmental impact analytics ────────────────────────────────────────────

def test_impact_empty_db(client, seller_headers):
    resp = client.get("/api/v1/analytics/impact", headers=seller_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["total_weight_kg"] == 0.0
    assert body["co2_saved_kg"] == 0.0
    assert body["trees_equivalent"] == 0.0


def test_impact_after_proof_upload(client, seller_headers, transaction_id):
    payload = {
        "transaction_id": str(transaction_id),
        "scheduled_time": FUTURE,
        "pickup_location": LOCATION,
    }
    created = client.post("/api/v1/pickups", json=payload, headers=seller_headers).json()
    client.post(
        f"/api/v1/pickups/{created['id']}/proof",
        json={"weight": 100.0, "material_type": "plastic"},
        headers=seller_headers,
    )

    resp = client.get("/api/v1/analytics/impact", headers=seller_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["total_weight_kg"] == 100.0
    assert body["co2_saved_kg"] == 150.0  # plastic factor = 1.5
    assert body["total_pickups_completed"] == 1


# ── Transaction analytics ─────────────────────────────────────────────────────

def test_transaction_analytics(client, seller_headers):
    resp = client.get("/api/v1/analytics/transactions", headers=seller_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert "total_pickups" in body
    assert "completed" in body
    assert body["period_days"] == 30


def test_transaction_analytics_custom_period(client, seller_headers):
    resp = client.get("/api/v1/analytics/transactions?days=7", headers=seller_headers)
    assert resp.status_code == 200
    assert resp.json()["period_days"] == 7
