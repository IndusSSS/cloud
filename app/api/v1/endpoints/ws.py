# app/api/v1/endpoints/ws.py
"""
WebSocket endpoints for real-time data streaming.
"""

from uuid import UUID
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, Set

router = APIRouter()

# In-memory broadcaster for WebSocket connections
broadcaster: Dict[UUID, Set[WebSocket]] = {}


@router.websocket("/ws/live/{device_id}")
async def ws_live(websocket: WebSocket, device_id: UUID):
    await websocket.accept()
    if device_id not in broadcaster:
        broadcaster[device_id] = set()
    broadcaster[device_id].add(websocket)
    try:
        while True:
            await websocket.receive_text()   # keepalive
    finally:
        broadcaster[device_id].discard(websocket) 