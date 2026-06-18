def auth_header(token):
    return {"Authorization": f"Bearer {token}"}


def _get_me(client, token):
    return client.get("/api/v1/users/me", headers=auth_header(token)).json()["id"]


def test_send_message(client, sample_listing_id, seller_token, recycler_token):
    recipient_id = _get_me(client, seller_token)

    response = client.post("/api/v1/messages/", json={
        "recipient_id": recipient_id,
        "offer_id": sample_listing_id,
        "message_text": "Is this still available?"
    }, headers=auth_header(recycler_token))
    assert response.status_code == 201
    assert response.json()["message_text"] == "Is this still available?"


def test_empty_message_rejected(client, seller_token, recycler_token):
    recipient_id = _get_me(client, seller_token)

    response = client.post("/api/v1/messages/", json={
        "recipient_id": recipient_id,
        "offer_id": 1,
        "message_text": "   "
    }, headers=auth_header(recycler_token))
    assert response.status_code == 422


def test_get_messages_empty_list(client, sample_listing_id, seller_token, recycler_token):
    recipient_id = _get_me(client, seller_token)

    msg_res = client.post("/api/v1/messages/", json={
        "recipient_id": recipient_id,
        "offer_id": sample_listing_id,
        "message_text": "Hello"
    }, headers=auth_header(recycler_token))
    assert msg_res.status_code == 201, f"Create message failed: {msg_res.json()}"

    response = client.get(f"/api/v1/messages/{sample_listing_id}", headers=auth_header(recycler_token))
    assert response.status_code == 200, f"Get messages failed: {response.status_code}"
    data = response.json()
    assert len(data) >= 1, f"Expected at least 1 message, got {len(data)}: {data}"
