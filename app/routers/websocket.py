import json
import logging
from uuid import UUID
from collections import defaultdict
from typing import Dict, List

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status

from app.database import SessionLocal
from app.models.user import User
from app.services.message_service import send_message
from app.utils.security import verify_token
from app.websockets.chat_manager import chat_manager

logger = logging.getLogger(__name__)
router = APIRouter()


notification_clients: Dict[str, List[WebSocket]] = defaultdict(list)


@router.websocket("/ws/chat/{offer_id}")
async def chat_websocket(ws: WebSocket, offer_id: int):
    token = ws.query_params.get("token")
    if not token:
        await ws.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    try:
        payload = verify_token(token)
        user_id = UUID(payload["sub"])
    except (ValueError, KeyError):
        await ws.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    db = SessionLocal()
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        db.close()
        await ws.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await chat_manager.connect_to_room(offer_id, ws)

    try:
        while True:
            raw = await ws.receive_text()
            data = json.loads(raw)
            action = data.get("action")

            if action == "ping":
                await ws.send_text(json.dumps({"type": "pong"}))
                continue

            if action == "message":
                msg = send_message(
                    db=db,
                    sender_id=str(user.id),
                    recipient_id=data["recipient_id"],
                    offer_id=offer_id,
                    message_text=data["message_text"],
                )
                payload = {
                    "type": "new_message",
                    "id": msg.id,
                    "sender_id": msg.sender_id,
                    "recipient_id": msg.recipient_id,
                    "offer_id": msg.offer_id,
                    "message_text": msg.message_text,
                    "is_read": msg.is_read,
                    "created_at": msg.created_at.isoformat(),
                    "read_at": None,
                }
                await chat_manager.broadcast_to_room(offer_id, payload)
            else:
                await ws.send_text(json.dumps({"type": "error", "detail": f"Unknown action: {action}"}))
    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        chat_manager.disconnect_from_room(offer_id, ws)
        db.close()


@router.websocket("/ws/notifications")
async def notification_websocket(ws: WebSocket):
    token = ws.query_params.get("token")
    if not token:
        await ws.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    try:
        payload = verify_token(token)
        user_id = str(UUID(payload["sub"]))
    except (ValueError, KeyError):
        await ws.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await ws.accept()
    notification_clients[user_id].append(ws)
    logger.info(f"Notification WS connected for user {user_id}")

    try:
        while True:
            raw = await ws.receive_text()
            data = json.loads(raw)
            if data.get("action") == "ping":
                await ws.send_text(json.dumps({"type": "pong"}))
    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.error(f"Notification WS error: {e}")
    finally:
        notification_clients[user_id] = [w for w in notification_clients[user_id] if w != ws]
        if not notification_clients[user_id]:
            del notification_clients[user_id]


async def send_notification(user_id: str, payload: dict):
    for ws in notification_clients.get(user_id, []):
        try:
            await ws.send_text(json.dumps(payload))
        except Exception:
            pass
