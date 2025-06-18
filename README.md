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

## Development
Use the provided `.devcontainer` folder with VS Code Remote Containers for an integrated environment.
