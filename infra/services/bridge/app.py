import os
import json
import psycopg2
import paho.mqtt.client as mqtt

# Environment (injected by Compose)
DATABASE_URL = os.getenv("DATABASE_URL")
MQTT_BROKER  = os.getenv("MQTT_BROKER", "mqtt")
MQTT_PORT    = int(os.getenv("MQTT_PORT", "1883"))
MQTT_TOPIC   = os.getenv("MQTT_TOPIC", "sensors/+/data")

def on_connect(client, userdata, flags, rc):
    print(f"Connected to MQTT (rc={rc}), subscribing to '{MQTT_TOPIC}'")
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    payload = msg.payload.decode("utf-8")
    # Optional: validate JSON
    try:
        json.loads(payload)
    except json.JSONDecodeError:
        print("Invalid JSON, skipping:", payload)
        return

    # Insert into PostgreSQL
    conn = psycopg2.connect(DATABASE_URL)
    with conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO sensor_data (payload) VALUES (%s)",
            (payload,)
        )
    conn.close()
    print(f"Inserted payload from topic {msg.topic}")

if __name__ == "__main__":
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
    client.loop_forever()
