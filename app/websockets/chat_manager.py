from fastapi import WebSocket
from collections import defaultdict
from typing import Dict, List, Optional
import json
import logging

logger = logging.getLogger(__name__)


class ChatManager:
    def __init__(self):
        self.rooms: Dict[int, List[WebSocket]] = defaultdict(list)

    async def connect_to_room(self, offer_id: int, ws: WebSocket):
        await ws.accept()
        self.rooms[offer_id].append(ws)
        logger.info(f"WebSocket connected to room {offer_id} (total: {len(self.rooms[offer_id])})")

    def disconnect_from_room(self, offer_id: int, ws: WebSocket):
        self.rooms[offer_id] = [w for w in self.rooms[offer_id] if w != ws]
        if not self.rooms[offer_id]:
            del self.rooms[offer_id]
        logger.info(f"WebSocket disconnected from room {offer_id}")

    async def broadcast_to_room(self, offer_id: int, message: dict, exclude: Optional[WebSocket] = None):
        dead = []
        for ws in self.rooms.get(offer_id, []):
            if ws == exclude:
                continue
            try:
                await ws.send_text(json.dumps(message))
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect_from_room(offer_id, ws)


chat_manager = ChatManager()
