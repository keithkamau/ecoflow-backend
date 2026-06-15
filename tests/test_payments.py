def test_get_payments(client):
    response = client.get("/api/v1/payments/")
    assert response.status_code == 200


def test_payment_not_found(client):
    response = client.get("/api/v1/payments/99999")
    assert response.status_code == 404


def test_create_payment_invalid_transaction(client):
    response = client.post("/api/v1/payments/", json={
        "transaction_id": 99999,
        "user_id": 1,
        "amount": 500.0,
        "payment_method": "mpesa"
    })
    assert response.status_code == 404


def test_create_payment_with_mock(client):
    create_offer = client.post("/api/v1/offers/", json={
        "listing_id": 1,
        "offered_price": 15.0,
        "quantity": 50.0
    })
    offer_id = create_offer.json()["id"]
    client.put(f"/api/v1/offers/{offer_id}", json={"status": "accepted"})

    create_tx = client.post("/api/v1/transactions/", json={
        "offer_id": offer_id,
        "listing_id": 1,
        "seller_id": 1,
        "recycler_id": 2,
        "agreed_price": 15.0,
        "final_quantity": 50.0,
        "final_price": 750.0
    })
    tx_id = create_tx.json()["id"]

    response = client.post("/api/v1/payments/", json={
        "transaction_id": tx_id,
        "user_id": 1,
        "amount": 750.0,
        "payment_method": "mpesa"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "success"
    assert data["transaction_id"] == tx_id


def test_get_payment_by_transaction(client):
    create_offer = client.post("/api/v1/offers/", json={
        "listing_id": 2,
        "offered_price": 20.0,
        "quantity": 30.0
    })
    offer_id = create_offer.json()["id"]
    client.put(f"/api/v1/offers/{offer_id}", json={"status": "accepted"})

    create_tx = client.post("/api/v1/transactions/", json={
        "offer_id": offer_id,
        "listing_id": 2,
        "seller_id": 1,
        "recycler_id": 2,
        "agreed_price": 20.0,
        "final_quantity": 30.0,
        "final_price": 600.0
    })
    tx_id = create_tx.json()["id"]

    client.post("/api/v1/payments/", json={
        "transaction_id": tx_id,
        "user_id": 1,
        "amount": 600.0,
        "payment_method": "mpesa"
    })

    response = client.get(f"/api/v1/payments/{tx_id}")
    assert response.status_code == 200
    assert response.json()["transaction_id"] == tx_id
