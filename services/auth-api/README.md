# Auth API

FastAPI microservice providing authentication.

## Environment Variables
- `DATABASE_URL` – Postgres connection string
- `SECRET_KEY` – JWT signing key

## Endpoints
- `POST /v1/auth/register`
- `POST /v1/auth/login`
- `POST /v1/auth/refresh`
- `POST /v1/auth/logout`
- `GET  /v1/health`
