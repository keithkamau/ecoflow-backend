def auth_header(token):
    return {"Authorization": f"Bearer {token}"}


def test_create_offer(client, sample_listing_id, recycler_token):
    response = client.post("/api/v1/offers/", json={
        "listing_id": sample_listing_id,
        "offered_price": 15.0,
        "quantity": 50.0,
        "note": "Can pick up on weekdays"
    }, headers=auth_header(recycler_token))
    assert response.status_code == 201
    data = response.json()
    assert data["offered_price"] == 15.0
    assert data["status"] == "pending"


def test_get_offers(client, recycler_token):
    response = client.get("/api/v1/offers/", headers=auth_header(recycler_token))
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_offer_by_id(client, sample_listing_id, recycler_token):
    create = client.post("/api/v1/offers/", json={
        "listing_id": sample_listing_id,
        "offered_price": 20.0,
        "quantity": 30.0
    }, headers=auth_header(recycler_token))
    offer_id = create.json()["id"]
    response = client.get(f"/api/v1/offers/{offer_id}", headers=auth_header(recycler_token))
    assert response.status_code == 200
    assert response.json()["id"] == offer_id


def test_get_offer_not_found(client, recycler_token):
    response = client.get("/api/v1/offers/99999", headers=auth_header(recycler_token))
    assert response.status_code == 404


def test_update_offer_status(client, sample_listing_id, recycler_token):
    create = client.post("/api/v1/offers/", json={
        "listing_id": sample_listing_id,
        "offered_price": 10.0,
        "quantity": 20.0
    }, headers=auth_header(recycler_token))
    offer_id = create.json()["id"]
    response = client.put(f"/api/v1/offers/{offer_id}", json={"status": "accepted"}, headers=auth_header(recycler_token))
    assert response.status_code == 200
    assert response.json()["status"] == "accepted"


def test_offer_price_must_be_positive(client, sample_listing_id, recycler_token):
    response = client.post("/api/v1/offers/", json={
        "listing_id": sample_listing_id,
        "offered_price": -5.0,
        "quantity": 10.0
    }, headers=auth_header(recycler_token))
    assert response.status_code == 422


def test_delete_pending_offer(client, sample_listing_id, recycler_token):
    create = client.post("/api/v1/offers/", json={
        "listing_id": sample_listing_id,
        "offered_price": 12.0,
        "quantity": 25.0
    }, headers=auth_header(recycler_token))
    offer_id = create.json()["id"]
    response = client.delete(f"/api/v1/offers/{offer_id}", headers=auth_header(recycler_token))
    assert response.status_code == 204


def test_delete_non_pending_offer_fails(client, sample_listing_id, recycler_token):
    create = client.post("/api/v1/offers/", json={
        "listing_id": sample_listing_id,
        "offered_price": 12.0,
        "quantity": 25.0
    }, headers=auth_header(recycler_token))
    offer_id = create.json()["id"]
    client.put(f"/api/v1/offers/{offer_id}", json={"status": "accepted"}, headers=auth_header(recycler_token))
    response = client.delete(f"/api/v1/offers/{offer_id}", headers=auth_header(recycler_token))
    assert response.status_code == 400


def test_counter_offer(client, sample_listing_id, recycler_token):
    create = client.post("/api/v1/offers/", json={
        "listing_id": sample_listing_id,
        "offered_price": 10.0,
        "quantity": 20.0
    }, headers=auth_header(recycler_token))
    offer_id = create.json()["id"]
    response = client.post(f"/api/v1/offers/{offer_id}/counter", json={
        "counter_price": 15.0,
        "counter_quantity": 20.0,
        "counter_note": "Can you do KES 15?"
    }, headers=auth_header(recycler_token))
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "countered"
    assert data["counter_price"] == 15.0
