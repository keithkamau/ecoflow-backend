def auth_header(token):
    return {"Authorization": f"Bearer {token}"}


def test_get_transactions(client, recycler_token):
    response = client.get("/api/v1/transactions/", headers=auth_header(recycler_token))
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_transaction_not_found(client, recycler_token):
    response = client.get("/api/v1/transactions/99999", headers=auth_header(recycler_token))
    assert response.status_code == 404


def _create_accepted_offer(client, sample_listing_id, recycler_token):
    create = client.post("/api/v1/offers/", json={
        "listing_id": sample_listing_id,
        "offered_price": 15.0,
        "quantity": 50.0
    }, headers=auth_header(recycler_token))
    offer_id = create.json()["id"]
    client.put(f"/api/v1/offers/{offer_id}", json={"status": "accepted"}, headers=auth_header(recycler_token))
    return offer_id


def _get_me(client, token):
    return client.get("/api/v1/users/me", headers=auth_header(token)).json()["id"]


def test_create_transaction_without_accepted_offer(client, sample_listing_id, recycler_token):
    response = client.post("/api/v1/transactions/", json={
        "offer_id": 99999,
        "listing_id": sample_listing_id,
        "seller_id": "00000000-0000-0000-0000-000000000000",
        "recycler_id": "00000000-0000-0000-0000-000000000000",
        "agreed_price": 15.0,
        "final_quantity": 50.0,
        "final_price": 750.0
    }, headers=auth_header(recycler_token))
    assert response.status_code == 404


def test_create_transaction_success(client, sample_listing_id, recycler_token, seller_token):
    offer_id = _create_accepted_offer(client, sample_listing_id, recycler_token)
    seller_id = _get_me(client, seller_token)
    recycler_id = _get_me(client, recycler_token)

    response = client.post("/api/v1/transactions/", json={
        "offer_id": offer_id,
        "listing_id": sample_listing_id,
        "seller_id": seller_id,
        "recycler_id": recycler_id,
        "agreed_price": 15.0,
        "final_quantity": 50.0,
        "final_price": 750.0
    }, headers=auth_header(recycler_token))
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "offer_accepted"
    assert data["offer_id"] == offer_id


def test_duplicate_transaction_for_offer_fails(client, sample_listing_id, recycler_token, seller_token):
    offer_id = _create_accepted_offer(client, sample_listing_id, recycler_token)
    seller_id = _get_me(client, seller_token)
    recycler_id = _get_me(client, recycler_token)

    client.post("/api/v1/transactions/", json={
        "offer_id": offer_id,
        "listing_id": sample_listing_id,
        "seller_id": seller_id,
        "recycler_id": recycler_id,
        "agreed_price": 15.0,
        "final_quantity": 50.0,
        "final_price": 750.0
    }, headers=auth_header(recycler_token))

    response = client.post("/api/v1/transactions/", json={
        "offer_id": offer_id,
        "listing_id": sample_listing_id,
        "seller_id": seller_id,
        "recycler_id": recycler_id,
        "agreed_price": 15.0,
        "final_quantity": 50.0,
        "final_price": 750.0
    }, headers=auth_header(recycler_token))
    assert response.status_code == 400


def test_update_transaction_status(client, sample_listing_id, recycler_token, seller_token):
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

    response = client.put(f"/api/v1/transactions/{tx_id}", json={"status": "pickup_scheduled"}, headers=auth_header(recycler_token))
    assert response.status_code == 200
    assert response.json()["status"] == "pickup_scheduled"


def test_invalid_state_transition_fails(client, sample_listing_id, recycler_token, seller_token):
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

    response = client.put(f"/api/v1/transactions/{tx_id}", json={"status": "completed"}, headers=auth_header(recycler_token))
    assert response.status_code == 400
