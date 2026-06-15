def test_send_message(client):
    response = client.post("/api/v1/messages/", json={
        "recipient_id": 2,
        "offer_id": 1,
        "message_text": "Is this still available?"
    })
    assert response.status_code == 201
    assert response.json()["message_text"] == "Is this still available?"


def test_empty_message_rejected(client):
    response = client.post("/api/v1/messages/", json={
        "recipient_id": 2,
        "offer_id": 1,
        "message_text": "   "
    })
    assert response.status_code == 422


def test_get_messages_empty_list(client):
    response = client.get("/api/v1/messages/99999")
    assert response.status_code == 200
    assert response.json() == []
