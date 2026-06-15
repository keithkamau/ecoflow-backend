def test_get_transactions(client):
    response = client.get("/api/v1/transactions/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_transaction_not_found(client):
    response = client.get("/api/v1/transactions/99999")
    assert response.status_code == 404


def test_create_transaction_without_accepted_offer(client):
    response = client.post("/api/v1/transactions/", json={
        "offer_id": 99999,
        "listing_id": 1,
        "seller_id": 1,
        "recycler_id": 2,
        "agreed_price": 15.0,
        "final_quantity": 50.0,
        "final_price": 750.0
    })
    assert response.status_code == 404


def test_create_transaction_success(client):
    create = client.post("/api/v1/offers/", json={
        "listing_id": 1,
        "offered_price": 15.0,
        "quantity": 50.0
    })
    offer_id = create.json()["id"]
    client.put(f"/api/v1/offers/{offer_id}", json={"status": "accepted"})

    response = client.post("/api/v1/transactions/", json={
        "offer_id": offer_id,
        "listing_id": 1,
        "seller_id": 1,
        "recycler_id": 2,
        "agreed_price": 15.0,
        "final_quantity": 50.0,
        "final_price": 750.0
    })
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "offer_accepted"
    assert data["offer_id"] == offer_id


def test_duplicate_transaction_for_offer_fails(client):
    create_offer = client.post("/api/v1/offers/", json={
        "listing_id": 2,
        "offered_price": 20.0,
        "quantity": 30.0
    })
    offer_id = create_offer.json()["id"]
    client.put(f"/api/v1/offers/{offer_id}", json={"status": "accepted"})

    client.post("/api/v1/transactions/", json={
        "offer_id": offer_id,
        "listing_id": 2,
        "seller_id": 1,
        "recycler_id": 2,
        "agreed_price": 20.0,
        "final_quantity": 30.0,
        "final_price": 600.0
    })

    response = client.post("/api/v1/transactions/", json={
        "offer_id": offer_id,
        "listing_id": 2,
        "seller_id": 1,
        "recycler_id": 2,
        "agreed_price": 20.0,
        "final_quantity": 30.0,
        "final_price": 600.0
    })
    assert response.status_code == 400


def test_update_transaction_status(client):
    create_offer = client.post("/api/v1/offers/", json={
        "listing_id": 3,
        "offered_price": 10.0,
        "quantity": 100.0
    })
    offer_id = create_offer.json()["id"]
    client.put(f"/api/v1/offers/{offer_id}", json={"status": "accepted"})

    create_tx = client.post("/api/v1/transactions/", json={
        "offer_id": offer_id,
        "listing_id": 3,
        "seller_id": 1,
        "recycler_id": 2,
        "agreed_price": 10.0,
        "final_quantity": 100.0,
        "final_price": 1000.0
    })
    tx_id = create_tx.json()["id"]

    response = client.put(f"/api/v1/transactions/{tx_id}", json={"status": "pickup_scheduled"})
    assert response.status_code == 200
    assert response.json()["status"] == "pickup_scheduled"


def test_invalid_state_transition_fails(client):
    create_offer = client.post("/api/v1/offers/", json={
        "listing_id": 4,
        "offered_price": 10.0,
        "quantity": 50.0
    })
    offer_id = create_offer.json()["id"]
    client.put(f"/api/v1/offers/{offer_id}", json={"status": "accepted"})

    create_tx = client.post("/api/v1/transactions/", json={
        "offer_id": offer_id,
        "listing_id": 4,
        "seller_id": 1,
        "recycler_id": 2,
        "agreed_price": 10.0,
        "final_quantity": 50.0,
        "final_price": 500.0
    })
    tx_id = create_tx.json()["id"]

    response = client.put(f"/api/v1/transactions/{tx_id}", json={"status": "completed"})
    assert response.status_code == 400
