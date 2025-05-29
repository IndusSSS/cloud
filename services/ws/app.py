from fastapi import FastAPI, WebSocket
import asyncio, json, os
import paho.mqtt.client as mqtt

app = FastAPI()
clients: set[WebSocket] = set()

# MQTT settings
MQTT_BROKER = os.getenv("MQTT_BROKER", "mqtt")
MQTT_PORT   = int(os.getenv("MQTT_PORT", "1883"))
MQTT_TOPIC  = "sensors/+/data"

# ---------- MQTT → WebSocket fan-out ----------
def on_connect(client, userdata, flags, rc):
    print("MQTT connected (rc=%s), sub to", rc, MQTT_TOPIC)
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    loop = asyncio.get_event_loop()
    payload = msg.payload.decode()
    print("MQTT got", payload)
    # schedule push to all WS clients
    loop.create_task(broadcast(payload))

async def broadcast(message: str):
    stale = []
    for ws in clients:
        try:
            await ws.send_text(message)
        except Exception:
            stale.append(ws)
    for ws in stale:
        clients.discard(ws)

# start MQTT loop in background thread
mqttc = mqtt.Client()
mqttc.on_connect = on_connect
mqttc.on_message = on_message
mqttc.connect(MQTT_BROKER, MQTT_PORT)
mqttc.loop_start()
# ------------------------------------------------

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    clients.add(ws)
    try:
        while True:
            # Echo anything the browser sends (optional)
            msg = await ws.receive_text()
            await ws.send_text(f"ECHO: {msg}")
    except Exception:
        pass
    finally:
        clients.discard(ws)
