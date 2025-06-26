# SmartSecurity Cloud Backend

This repository contains the containerised IoT backend for **SmartSecurity.Solutions**. The stack is composed of several FastAPI micro-services behind a Traefik reverse proxy with HTTPS, backed by PostgreSQL, Redis and MinIO.

## Quick start

1. Install [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/) on your host.
2. Clone this repository and change into the project directory.
3. Launch the complete stack:

```bash
docker compose up -d
```

Traefik will obtain certificates from Let's Encrypt automatically. The API gateway will be available at `https://api.smartsecurity.solutions` once DNS points to your host.

### Services

- **gateway** – API gateway / BFF exposed through Traefik
- **auth-api** – authentication and tenant/user management
- **device-api** – CRUD operations for registered devices
- **metrics-api** – ingestion and querying of device metrics
- **postgres** – PostgreSQL 15 database
- **redis** – Redis 7 instance
- **minio** – S3-compatible object storage

Environment variables for each service can be configured via the `.env.example` files located under `services/<service>`. Copy them to `.env` and adjust as needed.

## API documentation

Each micro-service exposes interactive documentation via FastAPI. When the stack is running, open the following URLs:

- Gateway: `https://api.smartsecurity.solutions/docs`
- Auth API: `http://auth:8000/docs` (internal)
- Device API: `http://device:8000/docs` (internal)
- Metrics API: `http://metrics:8000/docs` (internal)

Only the gateway is exposed publicly; the other URLs are reachable from inside the Docker network.

## Development

The recommended workflow is to use the provided `docker compose` stack for a production-like environment. Subsequent documentation will cover local development, CI and deployment.
