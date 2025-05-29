docker compose logs db --tail=20
curl http://127.0.0.1:8000/v1/health
nano docker-compose.yml
vim 
nano docker-compose.yml
# Export a matching DATABASE_URL
export DATABASE_URL='postgresql+asyncpg://ssc:ChangeMeToAStrongPass!@localhost:5432/sensordb'
# Now restart your app
uvicorn app.main:app --reload --port 8000
exit
source ~/cloud-mini/.venv/bin/activate
curl -X POST http://127.0.0.1:8000/api/v1/logs      -H "Content-Type: application/json"      -d '{"device_id":"demo-esp32","switch":true,"ts":1234567890}'
cd backend
# install deps if needed: pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
sudo apt install uvicorn
cd backend
# install deps if needed: pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
# confirm where you are
pwd  
# should print something like:
/home/admin/backend
# from /home/admin/backend
source .venv/bin/activate
pip install -r requirements.txt
ls -1
# verify whether __init__.py exists
ls app/__init__.py
# verify whether __init__.py exists
ls app/__init__.py
touch app/__init__.py
# ensure your venv is active (you already see the "(.venv)" prompt)
source .venv/bin/activate
# install the essentials
pip install fastapi uvicorn psycopg2-binary python-dotenv alembic
# (optional) lock them for next time
pip freeze > requirements.txt
uvicorn app.main:app --reload --port 8000
ls -la app
tree
find . -type f -name "main.py"
touch app/main.py
nano  app/main.py
# File: app/main.py
import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import psycopg2
from psycopg2.extras import RealDictCursor
# import your database helper and any routers
from app.db import get_conn
from app.routes.metrics import router as metrics_router
app = FastAPI(
)
# ——— Mount routers ——————————————————————————————————————————————
app.include_router(metrics_router, prefix="/metrics", tags=["metrics"])
# add other routers here, e.g.
# from app.routes.auth import router as auth_router
# app.include_router(auth_router, prefix="/auth", tags=["auth"])
# ——— Health check ——————————————————————————————————————————————
@app.get("/health", tags=["health"])
def health():
# ——— Example root endpoint ————————————————————————————————————————
@app.get("/", include_in_schema=False)
def root():
uvicorn app.main:app --reload --port 8000
nano app/db.py
cd app
ls
nano db.py
nano  main.py 
nano app/routes/metrics.py
tree
cd routes/
ls
nano metrics.py 
ls
tree /backend
tree ~/backend
cd app
cd ..
la
touch requirements.txt
nano requirements.txt 
cd ..
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
clear
cd ~/backend
uvicorn app.main:app --reload --port 8000
clear
tree
cd traefik/
nano docker-compose.yml
cd ..
# 1-a. Move to the directory that will hold the project
cd ~              # or any workspace you prefer
# 1-b. Make the folder structure shown in the plan
mkdir -p cloud-mini && cd cloud-mini
touch requirements.txt models.py main.py
ls
nano requirements.txt 
nano models.py 
nano main.py 
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
# 2-a. Create & activate a virtual environment (recommended)
python3 -m venv .venv
source .venv/bin/activate        # Windows PowerShell: .venv\Scripts\Activate.ps1
# 2-b. Install the packages listed in requirements.txt
pip install --upgrade pip
pip install -r requirements.txt
# 3-a. Still inside the cloud-mini folder *with the venv active*
uvicorn main:app --host 0.0.0.0 --port 8000
ls
cd bb
ls
cd ~/backend/app
ls
nano models.py 
cd ~/backend/app/routers
ls
cd routes/
ls
touch log.py
nano log.py 
nano backend/app/main.py
cd /
ls
la
tree
cd home
la
cd admin
tree
cd ..
mkdir bb
cd admin
la
mkdir bb
la
cd ~/backend/app
ls
nano main.py 
uvicorn app.main:app --reload --port 8000
cd backend/
uvicorn app.main:app --reload --port 8000
# Export a matching DATABASE_URL
export DATABASE_URL='postgresql+asyncpg://ssc:ChangeMeToAStrongPass!@localhost:5432/sensordb'
# Now restart your app
uvicorn app.main:app --reload --port 8000
cd ~/backend
source .venv/bin/activate
pip install -r requirements.txt
pip install fastapi uvicorn[standard] sqlalchemy asyncpg
uvicorn app.main:app --reload --port 8000
nano ~/backend/app/main.py
uvicorn app.main:app --reload --port 8000
nano ~/backend/app/main.py
uvicorn app.main:app --reload --port 8000
cd ~/backend
source .venv/bin/activate
# export the exact URL from your compose file
export DATABASE_URL='postgresql+asyncpg://ssc:ChangeMeToAStrongPass!@localhost:5432/sensordb'
python - << 'PYCODE'
import os, asyncio, asyncpg

async def test_conn():
    url = os.environ.get("DATABASE_URL")
    print("Attempting:", url)
    try:
        conn = await asyncpg.connect(url)
        await conn.close()
        print("✅ Connection successful!")
    except Exception as e:
        print("❌ Connection failed:", type(e).__name__, e)

asyncio.run(test_conn())
PYCODE

cd ~/backend
source .venv/bin/activate
export DATABASE_URL='postgresql+asyncpg://ssc:ChangeMeToAStrongPass!@localhost:5432/sensordb'
python - << 'PYCODE'
import os, asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def test_engine():
    url = os.environ["DATABASE_URL"]
    print("Using engine URL:", url)
    engine = create_async_engine(url, echo=False)
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT 1"))
        print("✅ SQLAlchemy engine works, SELECT 1 →", result.scalar())
    await engine.dispose()

asyncio.run(test_engine())
PYCODE

cd ~/backend
source .venv/bin/activate
export DATABASE_URL='postgresql+asyncpg://ssc:ChangeMeToAStrongPass!@localhost:5432/sensordb'
python - << 'PYCODE'import os, asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def test_engine():
url = os.environ.get("DATABASE_URL")
print("→ Using engine URL:", url)
engine = create_async_engine(url, echo=False)
async with engine.connect() as conn:
result = await conn.execute(text("SELECT 1"))
print("✅ Engine works, SELECT 1 →", result.scalar())
await engine.dispose()

asyncio.run(test_engine())
PYCODE







cd ~/backend
source .venv/bin/activate
export DATABASE_URL='postgresql+asyncpg://ssc:ChangeMeToAStrongPass!@localhost:5432/sensordb'
python - << 'PYCODE'
import os, asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def test_engine():
    url = os.environ.get("DATABASE_URL")
    print("→ Using engine URL:", url)
    engine = create_async_engine(url, echo=False)
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT 1"))
        print("✅ Engine works, SELECT 1 →", result.scalar())
    await engine.dispose()

asyncio.run(test_engine())
PYCODE

cd ..
cd traefik/
nano docker-compose.yml 
# From the folder with that compose file:
docker compose up -d db
docker compose up d- db
nano docker-compose.yml 
nanp docker-compose.yml 
nano docker-compose.yml 
docker compose up -d db
cd ..
find . -type f -name "docker-compose.yml"
pwd
touch docker-compose.yml
nano docker-compose.yml 
docker compose config       # should pass with no errors
docker compose up -d db     # brings up Postgres on localhost:5432
cd traefik
nano docker-compose.yml 
cd ..
nano docker-compose.yml 
docker compose config      # validates your YAML
docker compose up -d db    # starts Postgres
docker compose up -d api   # starts your FastAPI service
curl http://127.0.0.1:8000/v1/health
cd ~/bb
ls
cd 
pwd
htop
pwd
la
cd traefik/
la
rm docker-compose.yml.save 
ls
nano traefik.yml 
tree
nano acme.json 
docker compose config      # validates your YAML
docker compose up -d db    # starts Postgres
docker compose up -d api   # starts your FastAPI service
nano docker-compose.yml 
# 1) Validate the YAML
docker compose config
# 2) Start only Postgres
docker compose up -d db
# 3) Start only your API
docker compose up -d api
docker compose config
docker compose up -d db
docker compose up -d api
ls
cd backend/
ls
touch Dockerfile
cat > backend/Dockerfile << 'EOF'
# File: backend/Dockerfile

FROM python:3.12-slim

# 1. Set a working directory
WORKDIR /app

# 2. Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3. Copy your application code
COPY . .

# 4. Default command
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
EOF

la
cd ..
# From your project root (where docker-compose.yml lives):
# 1. Validate the compose file
docker compose config
# 2. Start Postgres
docker compose up -d db
# 3. Build & start your API (this time the Dockerfile exists)
docker compose up -d api
# 4. Tail logs if you like
docker compose logs -f api
cd backend/
nano Dockerfile 
# From your project root (where docker-compose.yml lives):
# 1. Validate the compose file
docker compose config
# 2. Start Postgres
docker compose up -d db
# 3. Build & start your API (this time the Dockerfile exists)
docker compose up -d api
# 4. Tail logs if you like
docker compose logs -f api
curl http://127.0.0.1:8000/v1/health
docker ps --format "table {{.Names}}\t{{.Ports}}"
curl -I http://localhost:8000/v1/docs
curl http://198.38.89.127:8000/v1/metrics
curl http://198.38.89.127:8000/v1/metrics/
curl -L http://198.38.89.127:8000/v1/metrics
alembic upgrade head
cd ~/backend
source .venv/bin/activate
pip install alembic
export DATABASE_URL='postgresql+asyncpg://ssc:ChangeMeToAStrongPass\!@localhost:5432/sensordb'
set +H
export DATABASE_URL='postgresql+asyncpg://ssc:ChangeMeToAStrongPass!@localhost:5432/sensordb'
alembic upgrade head
nano ~/app/models.py
cd ..
la
rm docker-mini
rm cloud-mini/
ls
cd backend/
la
cd app
la
nano models.py 
ls
cd ..
ls
cd alembic
ls
nano env.py 
cd ..
alembic upgrade head
cd alembic
alembic upgrade head
cd ..
alembic upgrade head
cd alembic
nano env.py 
cd ..
alembic upgrade head
curl -L http://198.38.89.127:8000/v1/metrics/
cd ..
curl -L http://198.38.89.127:8000/v1/metrics/
cd ~/backend
source .venv/bin/activate
# If you haven’t already in this shell:
export DATABASE_URL='postgresql+asyncpg://ssc:ChangeMeToAStrongPass\!@localhost:5432/sensordb'
alembic revision --autogenerate -m "create initial tables"
cd ~/backend
source .venv/bin/activate
export DATABASE_URL='postgresql+asyncpg://ssc:ChangeMeToAStrongPass\!@localhost:5432/sensordb'
alembic revision --autogenerate -m "create initial tables"
cd ..
docker compose down
docker volume rm admin_db_data
docker compose up -d db
cd backend/
ls
alembic upgrade head
cd ..
nano docker-compose.yml 
psql smartdb -c "SELECT device_id,switch,ts_device FROM logs ORDER BY id DESC LIMIT 5;"
exit
nano docker-compose.yml 
cd traefik/
nano docker-compose.yml 
cd ..
sudo -u postgres psql
postgres=# ALTER USER smart WITH PASSWORD 'smart@123';
postgres=# \q
cd traefik/
nano docker-compose.yml 
curl http://198.38.89.127:8000/v1/health
# Activate your backend venv if needed
cd ~/backend && source .venv/bin/activate
# Connect and insert
# Activate your backend venv if needed
cd ~/backend && source .venv/bin/activate
# Connect and insert
# From your backend folder, venv active (if you need migrations later):
cd ~/backend && source .venv/bin/activate
# Export the password for psql
export PGPASSWORD='ChangeMeToAStrongPass!'
# Run psql with host, user, db, and your INSERT in one line
psql   -h localhost   -U ssc   -d sensordb   -c "INSERT INTO metrics (device_id, value) VALUES ('test-device', 42.42);"
# Unset the password when you’re done (optional)
unset PGPASSWORD
alembic revision --autogenerate -m "create metrics table"
# From your backend folder, venv active (if you need migrations later):
cd ~/backend && source .venv/bin/activate
# Export the password for psql
export PGPASSWORD='ChangeMeToAStrongPass!'
# Run psql with host, user, db, and your INSERT in one line
psql   -h localhost   -U ssc   -d sensordb   -c "INSERT INTO metrics (device_id, value) VALUES ('test-device', 42.42);"
# Unset the password when you’re done (optional)
unset PGPASSWORD
cd ~/backend/alembic/versions/
ls
la
nano 3929a63c9eae_create_metrics_table.py 
cd ~/backend/
alembic upgrade head
curl -L http://198.38.89.127:8000/v1/metrics/
cd ..
docker compose ps
docker compose up -d api
docker compose ps
curl -L http://127.0.0.1:8000/v1/metrics/
docker exec -it admin-db-1 psql -U ssc -d sensordb   -c "INSERT INTO metrics (device_id, value) VALUES ('test-device', 42.42);"
curl -L http://198.38.89.127:8000/v1/metrics/
nano backend/app/routes/metrics.py
docker compose restart api
curl -L http://127.0.0.1:8000/v1/metrics/
cd ~/dashboard/admin-dashboard
ls
la
cat > .env.local << 'EOF'
VITE_API_BASE_URL=http://127.0.0.1:8000/v1
EOF

npm install   # only if you haven’t yet
npm run dev
npm run dev -- --host 0.0.0.0
npm run dev -- --host 0.0.0.0 --port 5173
sudo ufw allow 5173/tcp
sudo ufw reload
ss -tlnp | grep 5173
npm run dev -- --host 0.0.0.0 --port 5173
ss -tlnp | grep 5173
ls
cd dashboard/
la
cd admin-dashboard/
ls
nano vite.config.js 
sudo ufw allow 5173/tcp
sudo ufw reload
sudo ufw status verbose
npm run dev -- --host 0.0.0.0
cd ~/dashboard/admin-dashboard
npm run dev -- --host 0.0.0.0
la
nano vite.config.js 
cd src
la
cd ~/traefik/
nano docker-compose.yml 
docker compose up -d dashboard
docker network create web
cd ~/traefik
docker compose up -d dashboard
nano docker-compose.yml 
docker compose up -d dashboard
cd ~/traefik
docker compose up -d dashboard
cd 
cd backend/
la
cd app
nano main.py 
cd ~/traefik
docker compose up -d api
docker compose up -d --build dashboard
curl -i http://127.0.0.1:8000/v1/metrics
cd ~/backend
source .venv/bin/activate
alembic upgrade head
docker exec -it admin-db-1 psql -U ssc -d sensordb   -c "INSERT INTO metrics (device_id, value) VALUES ('test-device', 42.42);"
curl -L http://127.0.0.1:8000/v1/metrics
cd..
# on the VPS prompt
curl -L http://127.0.0.1:8000/v1/metrics
docker compose ps
cd ..
cd backend/ curl -i http://127.0.0.1:8000/v1/metrics
cd backend/
;s
ss -tlnp | grep 8000
curl -i http://127.0.0.1:8000/v1/metrics
curl -i http://127.0.0.1:8000/v1/metrics/
curl -i -L http://127.0.0.1:8000/v1/metrics
sudo ufw allow 8000/tcp
sudo ufw reload
sudo ufw status verbose
curl -i http://127.0.0.1:8000/v1/metrics/
sudo ufw status verbose
curl -i http://127.0.0.1:8000/v1/metrics/
# tail the API logs in one pane
docker-compose logs --follow api
# in another pane, send a request
curl -v http://127.0.0.1:8000/v1/metrics
cd ~/traefik   # wherever your compose file lives  
docker compose logs --follow api
cd 
cd
cd backend/
nano backend/app/main.py
cd app/
nano main.py 
cd ~/traefik
docker compose up -d --build api
docker compose logs --follow api
cd ~/traefik
docker compose logs --follow api
curl -v http://127.0.0.1:8000/v1/metrics
cd ~/backend
docker compose logs --follow api
ls
docker compose logs --follow api
cd ~/backend
docker compose logs --follow api
cd ~/backend/app/routes
nano logs.py
cd 
cd backend/
cd app
nano main.py 
ls -l backend/app/routes/logs.py
cd 
ls -l backend/app/routes/logs.py
cd ~/backend/app/routes/
la
nano logs.py
la
cd ..
la
cd ..
la
tree
touch app/routes/__init__.py
cd ~/traefik           # or wherever your docker-compose.yml is
docker compose build api
docker compose up -d api
docker compose logs --follow api
cd ~/traefik 
docker compose logs --follow api
curl -v http://127.0.0.1:8000/v1/metrics
cd backend/
nano backend/app/main.py     # or vim, code etc.
cd app
la
nano main.py 
cd 
cd traefik/
docker compose up -d --build api
curl -i http://127.0.0.1:8000/v1/metrics/
cd traefik/
docker network ls | grep web          # you should see something like 'web   bridge'
nano ~/traefik/docker-compose.yml
cd ~/traefik
docker compose up -d --build traefik api dashboard
nano ~/traefik/docker-compose.yml
cd ~/traefik
docker compose up -d --build traefik api dashboard
docker network inspect web --format '{{range .Containers}}{{println .Name}}{{end}}'
nano docker-compose.yml 
cd traefik/
nano docker-compose.yml 
cd ~/traefik
docker compose up -d --build api
docker network inspect web   --format '{{range .Containers}}{{println .Name}}{{end}}'
# ↳ should list: traefik-traefik-1, admin-dashboard, and admin-api-1
docker network inspect web   --format '{{range .Containers}}{{println .Name}}{{end}}'
docker compose logs -f traefik
nano docker-compose.yml 
docker network rm web 2>/dev/null || true
docker network create web
docker compose up -d --build
docker network inspect web   --format '{{range .Containers}}{{println .Name}}{{end}}'
vim docker-compose.yml 
cd traefik/
vim docker-compose.yml 
la
nano docker-compose.yml 
curl -i http://localhost:8000/v1/metrics/
cd backend/
cd app/
la
nano main.py 
cd 
cd traefik/
# still inside the traefik project folder
docker compose up -d --build api
docker compose logs -f api
cd ~/backend/app/routes/
la
nano metrics.py 
nano logs.py
cd ~/traefik/
# from the traefik/ project folder
docker compose up -d --build api
docker compose logs -f api
cd 
cd backend/
cd app/
la
nano main.py 
cd ~/traefik/
docker compose up -d --build api
docker compose logs -f api
cd 
cd backend/
cd app
la
nano main.py 
cd ~/traefik
docker compose up -d --build api
docker compose logs -f api
cd backend/app/routes
cd ~/backend/app/routes
la
nano metrics.py 
nano logs.py 
cd ~/traefik
docker compose up -d --build api
docker compose logs -f api
cd 
cd backend/app/
la
nano main.py 
nano logs.p
la
cd routes/
la
nano metrics.py 
nano logs.py 
cd ~/traefik/
docker compose build api
docker compose up -d api
docker compose logs -f api
# in the directory that contains docker-compose.yml
docker compose build --no-cache api     # force a fresh copy of your code
docker compose up -d api                # start the new image
docker compose logs -f api              # watch – the NameError should be gone
la
cd
la
cd services/
la
cd api/
la
tree
cd app/
nano main.py 
cd traefik                     # folder with docker-compose.yml
docker compose build --no-cache api
docker compose up -d api
docker compose logs -f api     # should now say “Application startup complete.”
curl -i https://cloud.smartsecurity.solutions/api/v1/metrics
curl -i https://admin.smartsecurity.solutions/api/v1/metrics
docker compose up -d --build
docker network inspect web   --format '{{range .Containers}}{{println .Name}}{{end}}'
cd traefik/
nano docker-compose.yml 
docker compose pull            # fetch new images if any
docker compose up -d --build   # recreate / (re)attach api to “web”
curl -i http://localhost/api/health         # should return 200 {"db":"ok"}
curl -i http://localhost/api/metrics        # JSON with metrics
cd traefik/
cd ~/traefik   # or wherever your “traefik + api + dashboard” compose file is
docker-compose build api
docker-compose up -d api
docker-compose ps
docker-compose build api
docker-compose up -d api
docker-compose ps
docker compose build api
docker compose up -d api
docker compose ps
docker compose logs -f api
cd traefik/
la
nano docker-compose.yml 
la
cd ..
la
cd traefik/
tree
cd traefik/
nano docker-compose.yml 
la
nano docker-compose.yml 
docker-compose build api
docker-compose up -d api traefik
docker compose up -d api traefik
docker compose build api
docker compose up -d api traefik
curl -i http://127.0.0.1:8000/metrics/
curl -i https://cloud.smartsecurity.solutions/api/metrics/
curl -i https://admin.smartsecurity.solutions/api/metrics/curl -i https://admin.smartsecurity.solutions/api/metrics
curl -i http://127.0.0.1:8000/metrics/
curl -i https://cloud.smartsecurity.solutions/api/metrics/
curl -i https://admin.smartsecurity.solutions/api/metrics/
vim docker-compose.yml 
nano docker-compose.yml 
docker-compose build api
docker-compose up -d api traefik
cd ~/traefik
docker compose build api
docker compose up -d api traefik
$ docker compose ps
# … api                Up      0.0.0.0:8000->8000/tcp
# … traefik            Up      0.0.0.0:80->80/tcp, 0.0.0.0:443->443/tcp
cd ~/traefik
docker compose build api
docker compose up -d api traefik
docker compose ps
cd
curl -i http://127.0.0.1:8000/metrics/                    # 200 + JSON
curl -i https://cloud.smartsecurity.solutions/api/metrics/  # 200 + JSON
curl -i https://admin.smartsecurity.solutions/api/metrics/  # 200 + JSON
docker compose ps
cd ~/traefik
docker compose build api
docker compose up -d api traefik
docker compose ps
curl -i http://127.0.0.1:8000/metrics/   # should return 200 + JSON
curl -i https://cloud.smartsecurity.solutions/api/metrics/
curl -i https://admin.smartsecurity.solutions/api/metrics/
clear
docker compose ps
curl -i http://127.0.0.1:8000/metrics/
curl -i https://cloud.smartsecurity.solutions/api/metrics/
curl -i https://admin.smartsecurity.solutions/api/metrics/
clear
docker compose ps
curl -i http://127.0.0.1:8000/metrics/
docker compose ps
curl -i https://cloud.smartsecurity.solutions/api/metrics/
curl -i https://admin.smartsecurity.solutions/api/metrics/
clear
curl -i https://cloud.smartsecurity.solutions/api/metrics/   # 200 + JSON
curl -i https://admin.smartsecurity.solutions/api/metrics/   # 200 + JSON
nano docker-compose.yml 
exit
cd backend/
la
nano Dockerfile 
tree
curl -i http://127.0.0.1:8000/metrics/
\cd back
cd backend/
nano Dockerfile 
cd
cd traefik/
la
nano docker-compose.yml 
docker compose build api
docker compose up -d api
curl -i http://127.0.0.1:8000/metrics/
curl -i https://cloud.smartsecurity.solutions/api/metrics/
curl -i https://admin.smartsecurity.solutions/api/metrics/
nano docker-compose.yml 
tree
# rebuild your api image
docker compose build api
# restart it
docker compose up -d api
curl -i https://cloud.smartsecurity.solutions/api/metrics/
curl -i https://admin.smartsecurity.solutions/api/metrics/
curl -i http://127.0.0.1:5000/metrics/   # should return your JSON
curl -i https://cloud.smartsecurity.solutions/api/metrics/
curl -i https://admin.smartsecurity.solutions/api/metrics/
curl -i http://127.0.0.1:8000/metrics/
cd traefik/
curl -i https://cloud.smartsecurity.solutions/api/metrics/
curl -i https://admin.smartsecurity.solutions/api/metrics/
cd traefik/
nano docker-compose.yml 
# if you have docker-compose installed:
docker-compose build api
docker-compose up -d api
# or if you’re on compose v2 plugin:
docker compose build api
docker compose up -d api
curl -i http://127.0.0.1:5000/metrics/   # should return your JSON
nano docker-compose.yml 
cd ~/traefik
docker-compose build api
docker-compose up -d api
cd ~/traefik
docker-compose build api
docker-compose up -d api
cd ~/traefik
docker-compose build api
docker-compose up -d api
cd ~/traefik
docker-compose build api
docker-compose up -d api
cd ~/traefik
docker-compose build api
docker-compose up -d api
cd ~/traefik
docker-compose build api
docker-compose up -d api
cd ~/traefik
docker-compose build api
docker-compose up -d api
docker compose up -d api
cd ~/traefik
docker compose build api
docker compose up -d api
nano docker-compose.yml 
exit
cd traefik/
nano docker-compose.yml 
clear
cd traefik/
nano docker-compose.yml 
cd ~/traefik
docker compose build api
docker compose up -d traefik api
curl -i https://cloud.smartsecurity.solutions/api/metrics/   # should return 200 + JSON
curl -i https://admin.smartsecurity.solutions/api/metrics/   # should also return 200 + JSON
cd /home/admin/traefik
docker compose up -d --no-deps --build api traefik
curl -s http://127.0.0.1:8080/api/http/routers | jq .
curl -s http://127.0.0.1:8080/api/http/middlewares | jq .
curl -i https://cloud.smartsecurity.solutions/api/metrics/
nano docker-compose.yml 
cd ~/traefik
docker compose up -d --no-deps --build api traefik     # ~5 s
curl -i http://127.0.0.1:8000/metrics/

curl -i https://admin.smartsecurity.solutions/api/metrics/
nano docker-compose.yml 
cd ~/traefik
docker compose up -d --no-deps --build api traefik
curl -i http://127.0.0.1:8000/metrics/
curl -i https://cloud.smartsecurity.solutions/api/metrics/
curl -i https://admin.smartsecurity.solutions/api/metrics/
# 1) show routers
curl -s http://127.0.0.1:8080/api/http/routers | jq -C '.[] | {name, rule, service, middlewares}'
# 2) show services (ports Traefik forwards to)
curl -s http://127.0.0.1:8080/api/http/services | jq -C '.[] | {name, url: .loadBalancer.servers}'
# 3) show middlewares
curl -s http://127.0.0.1:8080/api/http/middlewares | jq -C '.[] | {name, stripPrefix}'
# 4) show live logs for 10 s while hitting the public URL in another tab
docker compose logs --no-log-prefix -f traefik | timeout 10s cat
curl -s http://127.0.0.1:8080/api/http/routers | jq -C '.[] | {name, rule, service, middlewares}'
curl -s http://127.0.0.1:8080/api/http/services | jq -C '.[] | {name, url: .loadBalancer.servers}'
curl -s http://127.0.0.1:8080/api/http/middlewares | jq -C '.[] | {name, stripPrefix}'
docker compose logs --no-log-prefix -f traefik | timeout 10s cat
docker compose stop nginx
docker compose restart traefik
nano traefik.yml 
docker compose restart traefik
curl -s http://127.0.0.1:8080/api/http/routers | jq .
nano traefik.yml 
cd ~/traefik
docker compose restart traefik
curl -s http://127.0.0.1:8080/api/http/routers | jq .
curl -i https://cloud.smartsecurity.solutions/api/metrics/
curl -i https://admin.smartsecurity.solutions/api/metrics/
cd services/
la
cd api/
nano Dockerfile 
cd ~/traefik
docker compose build api
docker compose up -d api
cd ~/traefik
docker compose build api
docker compose up -d api
curl -i http://127.0.0.1:8000/metrics
curl -i https://cloud.smartsecurity.solutions/api/metrics/
curl -i https://admin.smartsecurity.solutions/api/metrics/
cd 
cd serv
cd services/
cd api/
nano Dockerfile 
tree
cd ~/traefik/
nano docker-compose.yml 
cd ~/traefik
docker compose up -d api          # hot-reloads the new labels
curl -i http://127.0.0.1:8000/metrics/
curl -i https://cloud.smartsecurity.solutions/api/metrics/
curl -i https://admin.smartsecurity.solutions/api/metrics/
docker inspect --format='{{ json .Config.Labels }}' traefik-api-1 | jq .
curl -i https://cloud.smartsecurity.solutions/api/metrics/  
curl -i https://admin.smartsecurity.solutions/api/metrics/
docker network inspect web --format='{{json .Containers}}' | jq .
nano docker-compose.yml 
cd
la
cd backend/
cd api
la
nano Dockerfile 
ls
cd api
la
tree
cd 
nono docker-compose.yml 
nano docker-compose.yml 
cd traefik/
nano docker-compose.yml 
cd backend/
nano Dockerfile 
cd 
cd services/
la
cd api
la
nano Dockerfile 
cd ~/traefik
docker compose up -d --no-deps --build api traefik
cd ~/traefik
docker compose up -d --no-deps --force-recreate api traefik
curl -i https://cloud.smartsecurity.solutions/api/metrics/
curl -i https://admin.smartsecurity.solutions/api/metrics/
docker compose up -d --no-deps --build api traefik
docker inspect --format='{{json .Config.Labels}}' traefik-api-1 | jq .docker inspect --format='{{json .Config.Labels}}' traefik-api-1 | jq .
docker inspect --format='{{json .Config.Labels}}' traefik-api-1 | jq .
curl -i https://cloud.smartsecurity.solutions/api/metrics/
curl -i https://admin.smartsecurity.solutions/api/metrics/
nano docker-compose.yml 
cd ~/traefik
docker compose up -d --no-deps --build api traefik
curl -s http://127.0.0.1:8080/api/http/routers | jq .
curl -s http://127.0.0.1:8080/api/http/services | jq .
curl -s http://127.0.0.1:8080/api/http/routers | jq .
curl -s http://127.0.0.1:8080/api/http/services | jq .
[200~curl -i https://cloud.smartsecurity.solutions/api/metrics/
curl -i https://admin.smartsecurity.solutions/api/metrics/
nano docker-compose.yml 
docker exec admin-db-1 env | grep -E 'POSTGRES_USER|POSTGRES_PASSWORD'
docker exec   -e PGPASSWORD=ChangeMeToAStrongPass!   -it admin-db-1   psql -U smart -d postgres
curl -s http://198.38.89.127:8000/docs | grep /api | head
curl -s http://198.38.89.127:8000/openapi.json | grep '"/' | sort | uniq
cd ~/backend/app/routers/
la
cd backend/
cd app/
la
cd routes/
la
nano logs.py 
uvicorn app.main:app --reload
cd 
curl -s http://198.38.89.127:8000/openapi.json   | grep '"\/logs' -n
cd traefik/
nano docker-compose.yml 
cd ~/traefik
docker compose up -d api traefik
cd ~/traefik
docker compose up -d api traefik
nano docker-compose.yml 
docker compose up -d api traefik
curl -s http://127.0.0.1:8080/api/http/routers | jq .
curl -i https://cloud.smartsecurity.solutions/api/metrics/
curl -i https://admin.smartsecurity.solutions/api/metrics/
git config --global user.name  "YOUR-NAME"
git config --global user.email "you@example.com"
cd ~
git init
cat > .gitignore <<'EOF'
# Docker artefacts
**/__pycache__/
**/*.pyc
**/.pytest_cache/
**/node_modules/
**/.venv/
acme.json
# Compose volumes
volumes/
db_data/
mosquitto_*/
# Editor / OS noise
.vscode/
.idea/
.DS_Store
EOF

git add .
git status      # sanity-check the list before committing
git remote add origin https://github.com/your-org/smartsecurity-cloud.git
git branch -M main           # rename default branch to main (if desired)
git push -u origin main
tree
la
la
pwd
cd traefik/
cd .
la
la
cd backend/
tree
cd ..
cd traefik/
tree
la
cd 
cd services/
la
tree
cd ..
cd dashboard/
tree
cd ..
la
cd ~/                   # make sure you’re in /home/admin
mkdir cloud             # create the new container for all your “mono-repo” files
# move just the folders & files you showed into cloud/
mv   backend   dashboard   services   traefik   migrations   docker-compose.yml   nginx   mosquitto   alembic   alembic_backup   cloud-mini   cloud   .env*   README*   requirements.txt   cloud/                 ./cloud
la
cd cloud
la
mv ~/alembic ~/alembic_backup ~/migrations ~/nginx ~/mosquitto ~/README* ~/requirements.txt ~/cloud-mini ~/nginx ~/mosquitto ~/env* .
cd ..
cd ~
pwd
mv backend    cloud-mini    dashboard    services    traefik    docker-compose.yml    .gitignore*    README*    requirements.txt    cloud/
cd cloud
tree -L 2
tree -L 3
tree -L 1
tree -L 2
cd ..
la
mv .gitconfig /cloud
cd cloud/
tree -L 2
la
cd traefik/
la
cd ..
rm -rf ~/cloud/traefik/backend
rm -f  ~/cloud/traefik/docker-compose.yml
rm -rf ~/cloud/traefik/backend
rm -f  ~/cloud/traefik/docker-compose.yml
rm -rf ~/cloud/traefik/backend
rm -f  ~/cloud/traefik/docker-compose.yml
htop
la
tree -L 2
tree -L 3
htop
docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}"
# Show only running units; narrow to things we care about
systemctl list-units --type=service --state=running | grep -E 'docker|traefik|nginx|mosquitto|postgres|uvicorn|gunicorn'
# Requires root to show the owning process
sudo ss -tulpn | sort -k5
# (or, if you prefer lsof)
# sudo lsof -i -P -n | grep LISTEN
# Tail the last 50 lines, then follow in real time
docker logs -f --tail=50 traefik-api-1
curl -s http://127.0.0.1:8000/v1/health | jq
curl -s https://cloud.smartsecurity.solutions/api/v1/health | jq
cd cloud/
cd traefik/
curl -s https://cloud.smartsecurity.solutions/api/v1/health | jq
cd 
# Dump the OpenAPI spec from the container that is mapped to 8000
curl -s http://127.0.0.1:8000/openapi.json | jq '.paths | keys'
# See which host port maps to each container port
docker port admin-api-1
docker port traefik-api-1
clear
tree
la
cd .ssh/
la
loa
touch config
nano config
sudo apt update
sudo apt install screen
cd
screen -S work
cd ~/cloud
docker compose config --services
# Replace <api-service> with the name you found above
docker compose up -d --build <api-service>
docker compose up -d --build api
docker compose logs -f --tail=50 api
docker compose exec <api-service> alembic upgrade head
# List service names as defined in docker-compose.yml
cd ~/cloud          # folder that holds docker-compose.yml
docker compose config --services
docker compose up -d --build api
docker compose logs -f --tail=50 api
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
docker stop admin-db-1 traefik-db-1
bash # One-time schema upgrade docker compose exec api alembic upgrade head # Seed admin user docker compose exec api python - <<'PY' from app import crud, db, models models.Base.metadata.create_all(bind=db.engine) crud.create_user( db=db.SessionLocal(), email="admin@smartsecurity.solutions", password="ChangeMeNow!", is_superuser=True ) print("✅ Super-admin created") PY
# Confirm exactly one Postgres is listening
sudo ss -tulpn | grep 5432
docker ps | grep postgres
curl -s https://cloud.smartsecurity.solutions/api/v1/health | jq     # expect {"db":"ok"}
cd ~/cloud/docker-compose.yml
nano docker-compose.yml 
cd cloud/
cd cloud/
nano docker-compose.yml 
nano ~/cloud/docker-compose.yml       # or use vim / code .
docker compose logs -f db | grep ready
docker compose exec api alembic upgrade head
# still in ~/cloud (where docker-compose.yml lives)
docker compose up -d --build api
la
docker compose up -d --build
docker compose logs -f db | grep ready
docker compose exec api alembic upgrade head
docker compose exec api python - <<'PY'

6. **Smoke-test the API**

```bash
curl -s http://127.0.0.1:8000/api/v1/health      # local
curl -s https://cloud.smartsecurity.solutions/api/v1/health


sudo ss -tulpn | grep ':8000'
# or
sudo lsof -i :8000
docker ps --filter "publish=8000"
docker stop admin-api-1
docker rm   admin-api-1
cd ~/cloud
docker compose up -d --build api
cd ~/cloud
docker compose exec api alembic upgrade head
docker compose exec api python - <<'PY'
from app import crud, db, models

# Ensure tables exist (harmless if already run)
models.Base.metadata.create_all(bind=db.engine)

# Create the first super-admin user
crud.create_user(
    db=db.SessionLocal(),
    email="admin@smartsecurity.solutions",
    password="ChangeMeNow!",   # ← be sure to change this via the UI
    is_superuser=True
)
print("✅ Super-admin created")
PY

docker compose exec api python - <<'PY'
from app import crud, db, models

# Ensure tables exist (harmless if already run)
models.Base.metadata.create_all(bind=db.engine)

# Create the first super-admin user
crud.create_user(
    db=db.SessionLocal(),
    email="admin@smartsecurity.solutions",
    password="ChangeMeNow!",   # ← be sure to change this via the UI
    is_superuser=True
)
print("✅ Super-admin created")
PY

# 1. (If you haven’t already) apply migrations
docker compose exec api alembic upgrade head
# 2. Seed the super-admin without a TTY
docker compose exec -T api python - <<'PY'
from app import crud, db, models

# Ensure tables exist
models.Base.metadata.create_all(bind=db.engine)

# Create or re-create the super-admin
crud.create_user(
    db=db.SessionLocal(),
    email="admin@smartsecurity.solutions",
    password="ChangeMeNow!",
    is_superuser=True
)
print("✅ Super-admin created")
PY

cd ~/cloud
docker compose exec api alembic upgrade head
cd ~/cloud
docker compose exec api alembic upgrade head
cd ~/cloud
docker compose exec api alembic upgrade head
cd ~/cloud
docker compose exec api alembic upgrade head
cd ~/cloud
docker compose exec api alembic upgrade head
cd ~/cloud
docker compose exec api alembic upgrade head
docker compose exec -T api python - <<'PY'
from app import crud, db, models

# Ensure models are registered (harmless if already done)
models.Base.metadata.create_all(bind=db.engine)

# Create your initial super-admin user
crud.create_user(
    db=db.SessionLocal(),
    email="admin@smartsecurity.solutions",
    password="ChangeMeNow!",   # ← be sure to change this after first login
    is_superuser=True
)
print("✅ Super-admin created")
PY

mkdir smartsecurity
mv edge gateway cloud dashboard android devops docs smartsecurity/
la
mkdir -p smartsecurity/{edge,gateway,cloud,dashboard,android,devops,docs}
cd smartsecurity/
la
tree -L 2
tree -L 3
# move the whole folder; the empty 'dashboard/' placeholder will be replaced
rm -rf dashboard                          # delete the empty placeholder
mv cloud/dashboard dashboard              # puts admin-dashboard & src/ at top level
la
tree -L2
tree -L 2
# move the whole folder; the empty 'dashboard/' placeholder will be replaced
rm -rf dashboard                          # delete the empty placeholder
mv cloud/dashboard dashboard              # puts admin-dashboard & src/ at top level
# 1️⃣  (optional) keep a backup of the soon-to-be-deleted folder
mkdir -p _archive
mv cloud/cloud-mini _archive/          # stash instead of rm in case you change your mind
# 2️⃣  create the target location for backend
mkdir -p cloud/services
# 3️⃣  rename `backend` → `auth-api` inside services
git mv cloud/backend cloud/services/auth-api
# 4️⃣  move the Vue dashboard out of the cloud folder to its own top-level dir
git mv cloud/dashboard .
# 5️⃣  remove the now-empty dashboard stub that was created earlier
rmdir dashboard 2>/dev/null || true    # ignore error if it’s not empty / already gone
# 6️⃣  double-check the layout
tree -L 2
tree -L 3
# create the target folder (if not already present)
mkdir -p cloud/services
# move the whole backend folder in one shot
git mv cloud/backend cloud/services/auth-api   # use plain mv if you’re not using git
rmdir cloud/backend 2>/dev/null || true   # will silently skip if directory is already gone
tree -L 2 cloud
# move the backend directory into services as auth-api
mv cloud/backend cloud/services/auth-api
# confirm the result
tree -L 2 cloud
nano ~smartsecurity/cloud/docker-compose.yml
cd ~/smartsecurity/cloud/
la
nano docker-compose.yml 
vim docker-compose.yml 
cd smartsecurity/
cd cloud/
la
nano docker-compose.yml 
cd ~/smartsecurity/cloud
docker compose build auth-api
docker compose up -d
# Stop and remove the previous container (if still around)
docker rm -f cloud-api-1 2>/dev/null || true
cd ~/smartsecurity/cloud
docker compose down --remove-orphans
docker compose up -d
curl -f http://localhost:8000/docs
# open a shell in the auth-api container
docker compose exec auth-api bash
# activate the venv if you use one (skip if not)
source .venv/bin/activate 2>/dev/null || true
# generate a blank migration
alembic revision -m "add devices table"
docker compose exec auth-api bash
# change this line in the auth-api service
- ./services/auth-api:/code                # remove the :ro suffix
cd ~/smartsecurity/cloud/services/auth-api
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
exit
clear
cd ~/smartsecurity/cloud/
nano docker-compose.yml 
cd ~/smartsecurity/cloud
docker compose up -d --build auth-api
docker compose exec auth-api bash
source .venv/bin/activate 2>/dev/null || true
alembic revision -m "add devices table"    # should succeed this time
alembic upgrade head
exit
cd ~/smartsecurity/cloud/services/auth-api/alembic/versions
ls -t
nano 3929a63c9eae_create_metrics_table.py 
cd ~/smartsecurity/cloud
docker compose exec auth-api bash -lc "source .venv/bin/activate 2>/dev/null || true && alembic upgrade head"
docker compose exec auth-api bash -lc "psql \"$DATABASE_URL\" -c '\d devices'"
admin@726361-smartsecurity:~/smartsecurity/cloud/services/auth-api/alembic/versions$ cd ~/smartsecurity/cloud
docker compose exec auth-api bash -lc "source .venv/bin/activate 2>/dev/null || true && alembic upgrade head"
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
/usr/local/lib/python3.12/site-packages/alembic/script/revision.py:241: UserWarning: Revision <PUT_PREVIOUS_REV_ID_HERE> referenced from <PUT_PREVIOUS_REV_ID_HERE> -> add_devices_table (head), add devices table is not present
Traceback (most recent call last):
KeyError: '<PUT_PREVIOUS_REV_ID_HERE>'
admin@726361-smartsecurity:~/smartsecurity/cloud$ docker compose exec auth-api bash -lc "psql \"$DATABASE_URL\" -c '\d devices'"
bash: line 1: psql: command not found
admin@726361-smartsecurity:~/smartsecurity/cloud$
cd ~/smartsecurity/cloud/services/auth-api
alembic history --verbose | head
cd ~/smartsecurity/cloud
docker compose exec auth-api bash -lc "\
  source .venv/bin/activate 2>/dev/null || true && \
  alembic history --verbose | head -n 5\
"
cd ~/smartsecurity/cloud
docker compose exec auth-api bash -lc "\
  source .venv/bin/activate 2>/dev/null || true && \
  alembic history --verbose | head -n 5\
"
~/smartsecurity/cloud/services/auth-api/alembic/versions/<your_migration>.py
cd ~/smartsecurity/cloud/services/auth-api/alembic/versions
la
nano 3929a63c9eae_create_metrics_table.py 
cd ~/smartsecurity/cloud
docker compose exec auth-api bash -lc "\
  source .venv/bin/activate 2>/dev/null || true && \
  alembic upgrade head\
"
cd ~/smartsecurity/cloud
docker compose exec auth-api bash -lc "\
  source .venv/bin/activate 2>/dev/null || true && \
  alembic upgrade head\
"
ls ~/smartsecurity/cloud/services/auth-api/alembic/versions
cd ~/martsecurity/cloud/
nano docker-compose.yml 
docker compose exec auth-api bash -lc "\
  source .venv/bin/activate 2>/dev/null || true && \
  alembic revision -m 'add devices table'\
"
rm services/auth-api/alembic/versions/*add_devices_table*.py 2>/dev/null || true
cd ~/smartsecurity/cloud
docker compose exec auth-api bash -lc "\
  source .venv/bin/activate 2>/dev/null || true && \
  alembic revision -m 'add devices table'\
"
nano services/auth-api/alembic/versions/3929a63c9eae_create_metrics_table.py
nano ~/smartsecurity/cloud/services/auth-api/alembic/versions/3929a63c9eae_create_metrics_table.py
cd ~/smartsecurity/cloud
docker compose up -d --build auth-api
docker compose exec auth-api bash -lc "\
  source .venv/bin/activate 2>/dev/null || true && \
  alembic revision -m 'add devices table'\
"
nano ~/smartsecurity/cloud/services/auth-api/alembic/versions/3929a63c9eae_create_metrics_table.py
revision = "3929a63c9eae"
-down_revision = "<SOMETHING_INVALID>"
+down_revision = None   # this is the very first migration
nano ~/smartsecurity/cloud/services/auth-api/alembic/versions/3929a63c9eae_create_metrics_table.py
cd ~/smartsecurity/cloud
docker compose up -d --build auth-api
docker compose exec auth-api bash -lc "\
  source .venv/bin/activate 2>/dev/null || true && \
  alembic revision -m 'add devices table'\
"
cd  ~/smartsecurity/cloud/services/auth-api/alembic/versions/
la
nano ~/smartsecurity/cloud/services/auth-api/alembic/versions/39d8a6ba176f_add-devices-table.py
docker compose exec auth-api bash -lc "\
  source .venv/bin/activate 2>/dev/null || true && \
  alembic upgrade head\
"
cd ~/smartsecurity/cloud
docker compose exec auth-api bash -lc "\
  source .venv/bin/activate 2>/dev/null || true && \
  alembic upgrade 39d8a6ba176f\
"
docker compose exec db psql -U ssc -d sensordb -c "\d devices"
cd ~/smartsecurity/cloud
# Add tenant_id
docker compose exec db psql -U ssc -d sensordb -c "\
ALTER TABLE devices
  ADD COLUMN tenant_id INTEGER REFERENCES tenants(id);"
# Add name
docker compose exec db psql -U ssc -d sensordb -c "\
ALTER TABLE devices
  ADD COLUMN name VARCHAR(64) NOT NULL;"
# Add status
docker compose exec db psql -U ssc -d sensordb -c "\
ALTER TABLE devices
  ADD COLUMN status VARCHAR(16) NOT NULL DEFAULT 'offline';"
docker compose exec db psql -U ssc -d sensordb -c "\d devices"
cd ~/smartsecurity/cloud/services/auth-api/app/models
la
cd ~/smartsecurity/cloud/services/auth-api/app/models
cd ~/smartsecurity/cloud/services/auth-api/app/
la
tree
mkdir models
cd models/
touch device.py
nano device.py 
cd ..
la
mkdir schemas
touch ddevice.py
rm ddevice.py 
la
cd schemas/
la
touch device.py
nano device.py 
cd ..
la
mkdir routes
cd routes/
touch device.py
nano device.py 
cd ..
la
nano main.py 
vim main.py 
cd ~/smartsecurity/cloud/services/auth-api/app/
nano main.py 
cd ~/smartsecurity/cloud
docker compose up -d --build auth-api
docker compose exec db psql -U ssc -d sensordb -c "INSERT INTO devices (tenant_id, name, status) VALUES (1, 'demo-esp32', 'online');"
exit
# 1) Add tenant_id (with a FK to tenants.id)
docker compose exec db psql -U ssc -d sensordb -c "ALTER TABLE devices ADD COLUMN tenant_id INTEGER REFERENCES tenants(id);"
# 2) Add name (non-nullable text)
docker compose exec db psql -U ssc -d sensordb -c "ALTER TABLE devices ADD COLUMN name VARCHAR(64) NOT NULL DEFAULT '';"
# 3) Add status (non-nullable, default 'offline')
docker compose exec db psql -U ssc -d sensordb -c "ALTER TABLE devices ADD COLUMN status VARCHAR(16) NOT NULL DEFAULT 'offline';"
cd smartsecurity/cloud/
# 1) Add tenant_id (with a FK to tenants.id)
docker compose exec db psql -U ssc -d sensordb -c "ALTER TABLE devices ADD COLUMN tenant_id INTEGER REFERENCES tenants(id);"
# 2) Add name (non-nullable text)
docker compose exec db psql -U ssc -d sensordb -c "ALTER TABLE devices ADD COLUMN name VARCHAR(64) NOT NULL DEFAULT '';"
# 3) Add status (non-nullable, default 'offline')
docker compose exec db psql -U ssc -d sensordb -c "ALTER TABLE devices ADD COLUMN status VARCHAR(16) NOT NULL DEFAULT 'offline';"
docker compose exec db psql -U ssc -d sensordb -c "\d devices"
docker compose exec db psql -U ssc -d sensordb -c "INSERT INTO devices (tenant_id, name, status) VALUES (1, 'demo-esp32', 'online');"
docker compose exec db psql -U ssc -d sensordb -c "ALTER TABLE devices ADD COLUMN tenant_id INTEGER;"
docker compose exec db psql -U ssc -d sensordb -c "ALTER TABLE devices
  ADD CONSTRAINT devices_tenant_id_fkey
  FOREIGN KEY (tenant_id) REFERENCES tenants(id);"
docker compose exec db psql -U ssc -d sensordb -c "CREATE TABLE tenants (
   id         SERIAL PRIMARY KEY,
   name       VARCHAR(64) NOT NULL UNIQUE,
   created_at TIMESTAMPTZ    NOT NULL DEFAULT now()
 );"
docker compose exec db psql -U ssc -d sensordb -c "ALTER TABLE devices
   ADD CONSTRAINT devices_tenant_id_fkey
   FOREIGN KEY (tenant_id) REFERENCES tenants(id);"
docker compose exec db psql -U ssc -d sensordb -c "\d tenants"
docker compose exec db psql -U ssc -d sensordb -c "\d devices"
docker compose exec db psql -U ssc -d sensordb -c "INSERT INTO tenants (name) VALUES ('demo-tenant');"
docker compose exec db psql -U ssc -d sensordb -c "INSERT INTO devices (tenant_id, name, status) VALUES (1, 'demo-esp32', 'online');"
curl -s -X POST http://localhost:8000/api/v1/auth/login   -H "Content-Type: application/json"   -d '{"username":"admin","password":"SecretPass!"}'
{   "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.…",;   "token_type": "bearer"; }
curl -s -X POST http://localhost:8000/api/v1/auth/login   -H "Content-Type: application/json"   -d '{"username":"admin","password":"SecretPass!"}'
cd smartsecurity/cloud/services/auth-api/app/
cd ~/smartsecurity/cloud/services/auth-api/app/
la
nano main.py 
cd ~/smartsecurity/cloud
docker compose up -d --build auth-api
curl http://localhost:8000/api/v1/openapi.json | jq '.paths | keys'
cd ~/smartsecurity/cloud
docker compose ps
# From your home directory:
cd ~/smartsecurity/cloud
# Should list docker-compose.yml at the top:
ls -1
tree
tree -L 3
tree -L 2
cd ~/smartsecurity/cloud
docker compose config --services
docker compose up -d auth-api
docker compose ps
docker compose logs auth-api --tail=50
~/smartsecurity/cloud/services/auth-api/app/routes/
cd ~/smartsecurity/cloud/services/auth-api/app/
la
cd routes/
la
nano device.py 
mv   smartsecurity/cloud/services/auth-api/app/routes/device.py   smartsecurity/cloud/services/auth-api/app/routes/devices.py
rm device.py 
touch devices.py
nano devices.py 
la
cd 
cd :~/smartsecurity/cloud/services/auth-api/app/routes
cd ~/smartsecurity/cloud/services/auth-api/
la
cd app/
la
nano  main.py 
cd smartsecurity/cloud
docker compose up -d --build auth-api
curl -i http://localhost:8000/api/v1/openapi.json | jq '.paths | keys'
cd ~/smartsecurity/cloud
curl -i http://localhost:8000/api/v1/openapi.json | jq '.paths | keys'
cd ~/smartsecurity/cloud
ls
# docker-compose.yml  services  traefik  …
docker compose up -d --build auth-api
docker compose ps
docker compose logs auth-api --tail=30
~/smartsecurity/cloud/services/auth-api/app/
cd services/
la
tree 
tree _L 2
tree -L 2
cd ~/smartsecurity/cloud/services/auth-api/app
mv routes/device.py routes/devices.py
la
cd routes/
la
cd ..
la
nano main.py 
cd smartsecurity/cloud
docker compose up -d --build auth-api
cd smartsecurity/cloud
docker compose up -d --build auth-api
cd
cd smartsecurity/cloud/
docker compose up -d --build auth-api
curl -i http://localhost:8000/api/v1/openapi.json
docker compose ps
cd ~/smartsecurity/cloud
docker compose up -d --build
docker compose ps
cd ~/smartsecurity/cloud
docker compose ps -a
docker compose logs auth-api --tail=50
nano smartsecurity/cloud/services/auth-api/app/routes/devices.py
cd 
cd ~/smartsecurity/cloud/services/auth-api/app/routes/
la
nano devices.py 
cd ~/smartsecurity/cloud
docker compose up -d --build auth-api
docker compose ps
# expect cloud-auth-api-1  Up (healthy)  0.0.0.0:8000->8000/tcp
curl -i http://localhost:8000/api/v1/openapi.json
docker compose logs auth-api --tail=50
cat << 'EOF' > services/auth-api/app/security.py
from fastapi import Depends, HTTPException, status
from pydantic import BaseModel

class TokenData(BaseModel):
    tenant_id: int = 1  # default demo tenant

async def require_tenant() -> TokenData:
    """
    TEMP stub that always returns tenant_id=1.
    Replace with real JWT validation later.
    """
    return TokenData()
EOF

cd ~/smartsecurity/cloud
docker compose up -d --build auth-api
cd ~/smartsecurity/cloud
docker compose up -d --build auth-api
curl -i http://localhost:8000/api/v1/devices
docker compose logs auth-api --tail=50
cd services/auth-api/app/routes/
nano devices.py 
cd ~/smartsecurity/cloud
docker compose up -d --build auth-api
curl -i http://localhost:8000/api/v1/openapi.json | jq '.paths | keys'
docker compose logs auth-api --tail=50
cat << 'EOF' > services/auth-api/app/routes/auth.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

class LoginIn(BaseModel):
    username: str
    password: str

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"

@router.post("/login", response_model=TokenOut)
async def login(data: LoginIn):
    # temporary stub: only accepts admin / SecretPass!
    if data.username == "admin" and data.password == "SecretPass!":
        return TokenOut(access_token="fake-jwt-token")
    raise HTTPException(status_code=401, detail="Invalid credentials")
EOF

# ensure the routes/ package is recognized
touch services/auth-api/app/routes/__init__.py
cd ~/smartsecurity/cloud
docker compose up -d --build auth-api
curl -i http://localhost:8000/api/v1/openapi.json | jq '.paths | keys'
docker compose logs auth-api --tail=50
curl -i http://localhost:8000/api/v1/openapi.json | jq '.paths | keys'
docker compose up -d --build
docker compose ps
cd smartsecurity/cloud/
docker compose up -d --build
docker compose ps
curl -s http://localhost:8000/api/v1/openapi.json | head -n3
curl -i http://localhost:8000/openapi.json | head -n3
curl -i http://localhost:8000/docs | head -n3
nano ~/services/auth-api/app/main.py
cd services/
cd auth-api/app/
la
nano main.py 
cd ~/smartsecurity/cloud
docker compose up -d --build auth-api
curl -i http://localhost:8000/api/v1/openapi.json | head -n3
curl -i http://localhost:8000/api/v1/docs | head -n3
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"SecretPass!"}' \
  | jq -r .access_token)
curl -i -H "Authorization: Bearer $TOKEN"      http://localhost:8000/api/v1/devices/
docker compose logs auth-api --tail=50
cd ~/services/auth-api/app/
cd services/
cd auth-api/app/
la
nano db.py
cd ~/smartsecurity/cloud
docker compose up -d --build auth-api
docker compose logs auth-api --tail=20
curl -i http://localhost:8000/api/v1/openapi.json
curl -I http://localhost:8000/docs
curl -I http://localhost:8000/openapi.json
curl -I http://localhost:8000/api/v1/docs
curl -I http://localhost:8000/api/v1/openapi.json
cd ~/smartsecurity/cloud
docker compose ps
cd services/auth-api/app/
la
nano main.py 
exit
cd ~/smartsecurity/cloud
docker compose up -d --build auth-api
curl -i http://localhost:8000/api/v1/openapi.json | jq '.paths | keys'
curl -i -X POST http://localhost:8000/api/v1/auth/login   -H "Content-Type: application/json"   -d '{"username":"admin","password":"SecretPass!"}'
curl -i http://localhost:8000/api/v1/devices
la
curl -s http://localhost:8000/api/v1/openapi.json | jq '.paths | keys'
curl -i http://localhost:8000/api/v1/devices/
docker compose logs auth-api --tail=30
nano services/auth-api/app/models.py
cd ~/smartsecurity/cloud
docker compose up -d --build auth-api
curl -i http://localhost:8000/api/v1/devices/
nano services/auth-api/app/models.py
cd ~/smartsecurity/cloud
docker compose up -d --build auth-api
curl -i http://localhost:8000/api/v1/devices/
cd ~/smartsecurity/cloud/services/auth-api
echo "python-jose[cryptography]>=3.0.0" >> requirements.txt
nano app/security.py
nano app/routes/auth.py
nano app/routes/devices.py
docker compose up -d --build auth-api
curl -s http://localhost:8000/api/v1/openapi.json | jq '.paths | keys'
curl -s -X POST http://localhost:8000/api/v1/auth/login   -H "Content-Type: application/json"   -d '{"username":"admin","password":"SecretPass!"}' | jq -r .access_token
TOKEN=$(…copy the token from step 2…)
curl -i -H "Authorization: Bearer $TOKEN"      http://localhost:8000/api/v1/devices/
cd ~/smartsecurity/clou
cd ~/smartsecurity/cloud
TOKEN=$(
  curl -s -X POST http://localhost:8000/api/v1/auth/login \
    -H "Content-Type: application/json" \
    -d '{"username":"admin","password":"SecretPass!"}' \
  | jq -r .access_token
)
curl -i   -H "Authorization: Bearer $TOKEN"   http://localhost:8000/api/v1/devices/
mkdir -p services/auth-api/app/schemas
nano services/auth-api/app/schemas/device.py
nano services/auth-api/app/routes/devices.py
cd ~/smartsecurity/cloud
docker compose up -d --build auth-api
# get a valid JWT again
TOKEN=$(
  curl -s -X POST http://localhost:8000/api/v1/auth/login \
    -H "Content-Type: application/json" \
    -d '{"username":"admin","password":"SecretPass!"}' \
  | jq -r .access_token
)
curl -i -X POST http://localhost:8000/api/v1/devices/   -H "Authorization: Bearer $TOKEN"   -H "Content-Type: application/json"   -d '{"name":"new-device"}'
nano services/auth-api/app/routes/devices.py
cd ~/smartsecurity/cloud
docker compose up -d --build auth-api
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"SecretPass!"}' | jq -r .access_token)
curl -s -H "Authorization: Bearer $TOKEN"      http://localhost:8000/api/v1/devices/ | jq
curl -i -X POST http://localhost:8000/api/v1/devices/   -H "Authorization: Bearer $TOKEN"   -H "Content-Type: application/json"   -d '{"name":"another-device"}'
nano services/auth-api/app/routes/devices.py
cd ~/services/auth-api/app/routes/
cd smartsecurity/cloud/
la
cd services/
cd auth-api/app
la
cd routes/
la
nano devices.py 
cd ~/smartsecurity/cloud
docker compose up -d --build auth-api
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
   -H "Content-Type: application/json" \
   -d '{"username":"admin","password":"SecretPass!"}' \
 | jq -r .access_token)
curl -i -X POST http://localhost:8000/api/v1/devices/   -H "Authorization: Bearer $TOKEN"   -H "Content-Type: application/json"   -d '{"name":"another-device"}'
docker compose logs auth-api --tail=30
nano services/auth-api/app/models.py
cd ~/smartsecurity/cloud
docker compose up -d --build auth-api
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"SecretPass!"}' \
  | jq -r .access_token)
# Create a new device
curl -s -X POST http://localhost:8000/api/v1/devices/   -H "Authorization: Bearer $TOKEN"   -H "Content-Type: application/json"   -d '{"name":"yet-another-device"}' | jq
# List all devices
curl -s -H "Authorization: Bearer $TOKEN"      http://localhost:8000/api/v1/devices/ | jq
cd ~/smartsecurity/cloud
docker compose up -d --build auth-api
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"SecretPass!"}' \
  | jq -r .access_token)
# Create a new device
curl -s -X POST http://localhost:8000/api/v1/devices/   -H "Authorization: Bearer $TOKEN"   -H "Content-Type: application/json"   -d '{"name":"yet-another-device"}' | jq
# List all devices
curl -s -H "Authorization: Bearer $TOKEN"      http://localhost:8000/api/v1/devices/ | jq
curl -i -X POST http://localhost:8000/api/v1/devices/   -H "Authorization: Bearer $TOKEN"   -H "Content-Type: application/json"   -d '{"name":"yet-another-device"}'
cd ~/smartsecurity/cloud
docker compose up -d --build auth-api
cd ~/smartsecurity/cloud
docker compose ps
docker compose config --services
cat docker-compose.yml
la
nano docker-compose.yml 
docker compose up -d --build
docker compose ps
cd ~/smartsecurity/cloud
docker compose ps
docker compose up -d auth-api
cd services/auth-api/app/
la
nano main.py 
docker compose up -d --build auth-api
docker compose ps
# look for 0.0.0.0:8000->8000/tcp on auth-api
curl -I http://localhost:8000/api/v1/docs
# HTTP/1.1 200 OK
curl -I http://localhost:8000/api/v1/openapi.json
# HTTP/1.1 200 OK
cd ~/smartsecurity/infra
mkdir -p services/{api,auth-api,bridge,ws}
ln -s ../../cloud/services/api    services/api
ln -s ../../cloud/services/auth-api services/auth-api
ln -s ../../cloud/services/bridge services/bridge
ln -s ../../cloud/services/ws     services/ws
nano docker-compose.yml 
la
tree
rm services/
rm -rf services/
cd ~/smartsecuritycd ~/smartsecurity
cd ~/smartsecurity
mv cloud/services/api    infra/services/
mv cloud/services/auth-api infra/services/
mv cloud/services/bridge infra/services/
mv cloud/services/ws     infra/services
la
cd infra/
tree
cd ..
la
rm -rf cloud/services
cd infra/
nano docker-compose.yml 
docker network create web
clear
docker network rm web
docker network create web
docker compose down
docker network rm web
docker network create web
docker compose up -d --build
cd ~/smartsecurity/cloud
docker compose down
docker network rm web
la
cd ~/smartsecurity/cloud/traefik
docker compose down
docker network inspect web
cd ~/smartsecurity/cloud/traefik
docker compose down
cd ~/smartsecurity/dashboard
docker compose down
cd ~/smartsecurity/cloud/ws
docker compose down
docker network inspect web
docker network rm web
cd ~/smartsecurity/cloud/traefik
docker compose down
cd ~/smartsecurity/dashboard
docker compose down
cd ~/smartsecurity/cloud/ws
docker compose down
cd ~/smartsecurity/cloud
docker compose down auth-api
docker network inspect web
dig +short api.smartsecurity.solutions
cd smartsecurity/cloud/
tree -L 3
cd ..
tree -L 3
cd ~/smartsecurity
rm -rf _archive
# or
mv _archive archive
rm -rf _archive
for dir in android devops docs edge gateway; do
  echo "# $dir" > $dir/README.md; done
tree -L 3
mkdir -p dashboard
mv path/to/your-dashboard/* dashboard/mv path/to/your-dashboard/* dashboard/
tree -L 4
tree -L 5
tree -L 6
tree
cd ..
la
cd 
tree -L 3
cd smartsecurity/
find . -type f -name package.json
cd
find . -type f -name package.json
cd smartsecurity/
cp -r ~/projects/my-dashboard/*    dashboard/
# 1. Create a top-level folder called "dashboard"
mkdir dashboard
# 2. Copy (or git clone) your existing Vue project into it.
#    For example, if your Vue lives at ~/projects/my-dashboard:
cp -r ~/projects/my-dashboard/*    dashboard/
cd dashboard
ls package.json   # should list your project’s dependencies and scripts
ls src/           # should exist
cd ..
cd cloud 
la
nano docker-compose.yml 
la
cd traefik/
la
tree

cd smartsecurity/cloud/
la
nano docker-compose.yml 
cd ..
la
tree -L  3
tree -L  5
cd smartsecurity/cloud/
cd ~/smartsecurity/cloud
mv docker-compose.yml docker-compose.yml.bak
la
touch docker-compose.yml
la
tree
nano docker-compose.yml
docker network create web
nano docker-compose.yml
cd ~/smartsecurity/cloud
docker compose up -d --build
tree
cd ..
la
cd smartsecurity/
la
mkdir infra
la
cd infra
la
cd smartsecurity/infra/
touch docker-compose.yml
nano docker-compose.yml 
cd ..
cd smartsecurity/infra
docker network create web        # only if you haven’t already
docker compose up -d --build
cd smartsecurity/infra
cd infra/
docker network create web
tree -L 4
cd ~/smartsecurity/cloud/traefik
docker compose down
cd ~/smartsecurity/cloud/traefik
docker compose down
cd ~/smartsecurity/dashboard
docker compose down
cd ~/smartsecurity/cloud/ws
docker compose down
cd ~/smartsecurity/cloud
docker compose down auth-api
docker network rm web
cd ~/smartsecurity/infra
docker network rm web || true
docker ps --filter "network=web"
docker stop traefik-ws-1 traefik-api-1 traefik-traefik-1 admin-dashboard
docker rm   traefik-ws-1 traefik-api-1 traefik-traefik-1 admin-dashboard
docker ps -q --filter "network=web" | xargs -r docker stop
docker ps -a -q --filter "network=web" | xargs -r docker rm
docker network rm web
cd ~/smartsecurity/infra
docker compose up -d --build
# 1) create the target services folder (only once)
mkdir -p ~/smartsecurity/infra/services
# 2) move each service directory from cloud → infra
#    (use cp -r … if you want to keep a backup copy)
mv ~/smartsecurity/cloud/services/api       ~/smartsecurity/infra/services/
mv ~/smartsecurity/cloud/services/auth-api  ~/smartsecurity/infra/services/
mv ~/smartsecurity/cloud/services/bridge    ~/smartsecurity/infra/services/
mv ~/smartsecurity/cloud/services/ws        ~/smartsecurity/infra/services/
cd ~/smartsecurity/infra
docker compose up -d --build
tree
tree -L 3
cd service 
la
cd services/
la
tree
tree -L 3
mkdir -p ~/smartsecurity/infra/dashboard
cp -r ~/path/to/your-dashboard       ~/smartsecurity/infra/dashboard/admin-dashboard
cd..
cd ..
la
nano docker-compose.yml 
