"""
WebSocket Fan-out Service
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException

app = FastAPI(
    title="SmartSecurity WS",
    version="1.0",
    docs_url="/docs",
    redoc_url=None,
)

# ──────────────── simple in-memory hub ────────────────
connections: set[WebSocket] = set()

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    connections.add(ws)
    try:
        while True:
            msg = await ws.receive_text()
            # echo to all
            for conn in connections:
                await conn.send_text(msg)
    except WebSocketDisconnect:
        connections.discard(ws)

# ──────────────── health & ping ────────────────
@app.get("/ping", tags=["health"])
async def ping():
    return {"pong": True}

@app.get("/health", tags=["health"])
async def health():
    # If you have a DB, test it here; otherwise just say OK
    return {"status": "ok"}
