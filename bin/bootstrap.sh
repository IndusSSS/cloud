#!/usr/bin/env bash
# Idempotent first-run helper  –  never dies because of missing env files
set -euo pipefail
cd "$(dirname "$0")/.."   # repo root

# ── 1. Choose whichever template exists ──────────────────────────────
TPL=""
if   [[ -f .env.example ]]; then TPL=".env.example"
elif [[ -f env.example  ]]; then TPL="env.example"
fi

# ── 2. Create .env if absent ─────────────────────────────────────────
if [[ ! -f .env ]]; then
  echo ">>> Creating .env"
  if [[ -n "$TPL" ]]; then
    cp "$TPL" .env
  else
    # Last-chance fallback (never abort)
    cat > .env <<'FOO'
SECRET_KEY=REPLACE_ME
ACCESS_TOKEN_EXPIRE_MINUTES=60
ALGORITHM=HS256
POSTGRES_USER=smartsec
POSTGRES_PASSWORD=smartsecpass
POSTGRES_DB=smartsec
DATABASE_URL=postgresql+asyncpg://smartsec:smartsecpass@db:5432/smartsec
REDIS_URL=redis://redis:6379/0
FOO
  fi
fi

# ── 2b. Create Traefik htpasswd if absent ───────────────────────────
if [[ ! -f traefik/htpasswd ]]; then
  echo ">>> Creating traefik/htpasswd"
  htpasswd -bc traefik/htpasswd admin admin123
fi

# ── 3. Ensure SECRET_KEY is not placeholder ─────────────────────────
if grep -q "YOUR_SHARED_SECRET\|REPLACE_ME" .env; then
  sed -i "s/SECRET_KEY=.*/SECRET_KEY=$(openssl rand -hex 32)/" .env
fi

# ── 4. Spin up the stack ────────────────────────────────────────────
docker compose pull
docker compose up -d

# ── 5. Run migrations ───────────────────────────────────────────────
docker compose exec api alembic upgrade head

echo "✔  Bootstrap complete!"
