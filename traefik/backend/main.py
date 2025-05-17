import os, asyncio, json
import psycopg2, psycopg2.extras
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

def get_listener():
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=psycopg2.extras.RealDictCursor)
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
            for notify in conn.notifies:
                await ws.send_text(notify.payload)
            conn.notifies.clear()
            await asyncio.sleep(0.1)
    finally:
        await ws.close()
