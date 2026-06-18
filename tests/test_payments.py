def auth_header(token):
    return {"Authorization": f"Bearer {token}"}


def _get_me(client, token):
    return client.get("/api/v1/users/me", headers=auth_header(token)).json()["id"]


def _create_accepted_offer(client, sample_listing_id, recycler_token):
    create = client.post("/api/v1/offers/", json={
        "listing_id": sample_listing_id,
        "offered_price": 15.0,
        "quantity": 50.0
    }, headers=auth_header(recycler_token))
    offer_id = create.json()["id"]
    client.put(f"/api/v1/offers/{offer_id}", json={"status": "accepted"}, headers=auth_header(recycler_token))
    return offer_id


def test_get_payments(client, recycler_token):
    response = client.get("/api/v1/payments/", headers=auth_header(recycler_token))
    assert response.status_code == 200


def test_payment_not_found(client, recycler_token):
    response = client.get("/api/v1/payments/99999", headers=auth_header(recycler_token))
    assert response.status_code == 404


def test_create_payment_invalid_transaction(client, recycler_token):
    response = client.post("/api/v1/payments/", json={
        "transaction_id": 99999,
        "user_id": "00000000-0000-0000-0000-000000000000",
        "amount": 500.0,
        "payment_method": "mpesa"
    }, headers=auth_header(recycler_token))
    assert response.status_code == 404


def test_create_payment_success(client, sample_listing_id, recycler_token, seller_token):
    offer_id = _create_accepted_offer(client, sample_listing_id, recycler_token)
    seller_id = _get_me(client, seller_token)
    recycler_id = _get_me(client, recycler_token)

    create_tx = client.post("/api/v1/transactions/", json={
        "offer_id": offer_id,
        "listing_id": sample_listing_id,
        "seller_id": seller_id,
        "recycler_id": recycler_id,
        "agreed_price": 15.0,
        "final_quantity": 50.0,
        "final_price": 750.0
    }, headers=auth_header(recycler_token))
    tx_id = create_tx.json()["id"]

    response = client.post("/api/v1/payments/", json={
        "transaction_id": tx_id,
        "user_id": recycler_id,
        "amount": 750.0,
        "payment_method": "mpesa"
    }, headers=auth_header(recycler_token))
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "pending"
    assert data["transaction_id"] == tx_id


def test_get_payment_by_transaction(client, sample_listing_id, recycler_token, seller_token):
    offer_id = _create_accepted_offer(client, sample_listing_id, recycler_token)
    seller_id = _get_me(client, seller_token)
    recycler_id = _get_me(client, recycler_token)

    create_tx = client.post("/api/v1/transactions/", json={
        "offer_id": offer_id,
        "listing_id": sample_listing_id,
        "seller_id": seller_id,
        "recycler_id": recycler_id,
        "agreed_price": 15.0,
        "final_quantity": 50.0,
        "final_price": 750.0
    }, headers=auth_header(recycler_token))
    tx_id = create_tx.json()["id"]

    client.post("/api/v1/payments/", json={
        "transaction_id": tx_id,
        "user_id": recycler_id,
        "amount": 750.0,
        "payment_method": "mpesa"
    }, headers=auth_header(recycler_token))

    response = client.get(f"/api/v1/payments/{tx_id}", headers=auth_header(recycler_token))
    assert response.status_code == 200
    assert response.json()["transaction_id"] == tx_id
