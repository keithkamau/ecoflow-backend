import pytest

API_LISTINGS = "/api/v1/listings/listings"
API_MATERIALS = "/api/v1/listings/materials"

def test_create_material(client):
    response = client.post(f"{API_MATERIALS}", json={
        "type": "plastic",
        "unit": "kg",
        "reference_price": 15.0
    })
    assert response.status_code == 201
    data = response.json()
    assert data["type"] == "plastic"

def test_get_materials(client):
    response = client.get(f"{API_MATERIALS}")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_create_listing(client):
    material_resp = client.post(f"{API_MATERIALS}", json={
        "type": "metal",
        "unit": "kg",
        "reference_price": 50.0
    })
    material_id = material_resp.json()["id"]
    
    response = client.post(f"{API_LISTINGS}", json={
        "material_id": material_id,
        "quantity": 10.5,
        "condition": "Good",
        "location_address": "Nairobi"
    })
    assert response.status_code == 201
    assert response.json()["quantity"] == 10.5

def test_get_listings(client):
    response = client.get(f"{API_LISTINGS}")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data

def test_get_listing(client):
    material_resp = client.post(f"{API_MATERIALS}", json={
        "type": "glass",
        "unit": "kg",
        "reference_price": 10.0
    })
    material_id = material_resp.json()["id"]
    
    listing_resp = client.post(f"{API_LISTINGS}", json={
        "material_id": material_id,
        "quantity": 5.0
    })
    listing_id = listing_resp.json()["id"]
    
    response = client.get(f"{API_LISTINGS}/{listing_id}")
    assert response.status_code == 200
    assert response.json()["id"] == listing_id

def test_update_listing(client):
    material_resp = client.post(f"{API_MATERIALS}", json={
        "type": "paper",
        "unit": "kg",
        "reference_price": 8.0
    })
    material_id = material_resp.json()["id"]
    
    listing_resp = client.post(f"{API_LISTINGS}", json={
        "material_id": material_id,
        "quantity": 20.0
    })
    listing_id = listing_resp.json()["id"]
    
    response = client.put(f"{API_LISTINGS}/{listing_id}", json={
        "quantity": 25.0
    })
    assert response.status_code == 200
    assert response.json()["quantity"] == 25.0

def test_delete_listing(client):
    material_resp = client.post(f"{API_MATERIALS}", json={
        "type": "organic",
        "unit": "kg",
        "reference_price": 5.0
    })
    material_id = material_resp.json()["id"]
    
    listing_resp = client.post(f"{API_LISTINGS}", json={
        "material_id": material_id,
        "quantity": 15.0
    })
    listing_id = listing_resp.json()["id"]
    
    response = client.delete(f"{API_LISTINGS}/{listing_id}")
    assert response.status_code == 204

def test_search_listings(client):
    response = client.get(f"{API_LISTINGS}/search")
    assert response.status_code == 200
