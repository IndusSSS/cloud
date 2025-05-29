import os
import asyncio
import json
import psycopg2
import psycopg2.extras
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load DATABASE_URL from .env or from Docker ENV
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten this later to only your domains
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_listener():
    conn = psycopg2.connect(
        DATABASE_URL, cursor_factory=psycopg2.extras.RealDictCursor
    )
    conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    cur.execute("LISTEN telemetry_channel;")
    return conn, cur

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    conn, cur = get_listener()
    try:
        while True:
            conn.poll()
            while conn.notifies:
                notify = conn.notifies.pop(0)
                await ws.send_text(notify.payload)
            await asyncio.sleep(0.1)
    finally:
        await ws.close()
