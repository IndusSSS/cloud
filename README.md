# SmartSecurity Cloud Stack

This repository contains a multi-tenant IoT backend built with FastAPI services and a mediasoup SFU. All services run via Docker Compose and are reverse proxied by Traefik.

## Requirements
- Docker 20+
- Docker Compose 1.29+

## Running locally
```bash
docker compose up -d
```
Access the Traefik dashboard at `https://localhost/dashboard`.

## Services
- **gateway** – API gateway and BFF
- **auth-api** – authentication and JWT handling
- **device-api** – CRUD for devices
- **metrics-api** – metrics push/query API
- **billing-api** – Stripe/Razorpay webhooks
- **media-proxy** – mediasoup SFU
- **db** – PostgreSQL 15
- **redis** – Redis 7
- **objstore** – MinIO object storage

## Live streaming quick start
Send telemetry samples and consume them in real time:

```bash
curl -X POST https://device.localhost/v1/stream/device123 \
  -H 'Content-Type: application/json' \
  -d '{"ts":"2025-06-19T09:41:15Z","type":"temperature","value":23.7,"unit":"°C"}'

websocat ws://localhost:8080/ws/stream/device123
```

## Development
Use the provided `.devcontainer` folder with VS Code Remote Containers for an integrated environment.
