ls
clear
ls
nano requirements.txt
ls
nano Dockerfile
ls
cd ~/traefik
docker compose up -d --build bridge
ls
nano docker-compose.yml 
cd ~/traefik
docker compose up -d --build bridge
docker compose exec mqtt mosquitto_pub   -t sensors/test/data   -m '{"foo":"baz"}'
curl -s -k https://cloud.smartsecurity.solutions/api/dbtest
# → {"records":<new_count>}
docker compose logs -f bridge
docker compose exec mqtt mosquitto_pub -t sensors/test/data -m '{"foo":"baz"}'
docker compose logs mqtt --tail 20
# Make a config directory
mkdir -p ~/traefik/mosquitto/config
# Create the config file
cat << 'EOF' > ~/traefik/mosquitto/config/mosquitto.conf
listener 1883
allow_anonymous true
EOF

ls
cd mosquitto/
ls
nano config/
docker compose exec mqtt mosquitto_pub -t sensors/test/data -m '{"foo":"baz"}'
mkdir -p ~/traefik/mosquitto/config
cat << 'EOF' > ~/traefik/mosquitto/config/mosquitto.conf
listener 1883
allow_anonymous true
EOF

ls
cd traefik/
ls
nano docker-compose.yml 
cd ~/traefik
docker compose up -d mqtt
docker compose logs mqtt --tail 20
nano docker-compose.yml 
docker compose up -d
cd ~/services/ws
nano app.py 
cd ~/traefik
docker compose up -d --build ws
cd ~/traefik
docker compose up -d --build ws
docker compose exec mqtt mosquitto_pub -h mqtt -p 1883 -t sensors/demo1/data -m '{"temp":24.6}'
docker compose exec mqtt   mosquitto_pub -t sensors/demo1/data -m '{"temp":24.6}'
docker compose exec mqtt   mosquitto_pub -t sensors/demo1/data -m '{"temp":24.6}'
cd ~/traefik
# This runs mosquitto_pub directly inside the container:
docker compose exec --entrypoint mosquitto_pub mqtt   -h mqtt   -p 1883   -t sensors/demo1/data   -m '{"temp":24.6}'
docker compose exec mqtt   mosquitto_pub -t sensors/demo1/data -m '{"temp":24.6}'
const ws = new WebSocket("wss://cloud.smartsecurity.solutions/ws");
ws.onmessage = e => console.log("Live:", e.data);
// you should see Live: {"temp":24.6}
cd ~/traefik
ls
nano docker-compose.yml 
scp admin@cloud.smartsecurity.solutions:/home/admin/cloud.smartsecurity.solutions/docker-compose.yml ~/Downloads/docker-compose.yml
ls
scp admin@726361-smartsecurity:/traefik/docker-compose.yml C:\Users\Jaba\Desktop\media
scp admin@726361-smartsecurity:/traefik/docker-compose.yml C:\Users\Jaba
scp admin@726361-smartsecurity:/home/admin/cloud.smartsecurity.solutions/docker-compose.yml C:\Users\Jaba\Downloads\
nano docker-compose.yml 
cat /home/admin/cloud.smartsecurity.solutions/docker-compose.yml
# Fetch the remote file and copy it directly into your Windows clipboard
ssh admin@726361-smartsecurity   "cat /home/admin/cloud.smartsecurity.solutions/docker-compose.yml"   | clip.exe
..
cd ..
ls
ls -la
ls -R
sudo apt install tree   # Debian/Ubuntu
tree
ls
tree
nano ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
cp ~/.ssh/authorized_keys ~/.ssh/authorized_keys.bak
ls -ld ~/.ssh
ls -l  ~/.ssh/authorized_keys
ls
# Fetch the remote file and copy it directly into your Windows clipboard
ssh admin@726361-smartsecurity   "cat /home/admin/cloud.smartsecurity.solutions/docker-compose.yml"   | clip.exe
cat /home/admin/cloud.smartsecurity.solutions/docker-compose.yml
cd traefik/
nano docker-compose.yml
vim docker-compose.yml 
nano docker-compose.yml
cat /home/admin/cloud.smartsecurity.solutions/docker-compose.yml
cat docker-compose.yml | clip.exe
nano docker-compose.yml
sudo apt update && sudo apt install xclip
cat /home/admin/traefik/docker-compose.yml | xclip -selection clipboard
vim docker-compose.yml 
cd traefik/
ls
cat /path/to/your/file.txt | clip.exe
nano docker-compose.yml 
cd ..
ssh-keygen -lf %USERPROFILE%\.ssh\id_ed25519.pub
grep -v '^#' ~/.ssh/authorized_keys | xargs -n1 ssh-keygen -lf /dev/stdin
nano ~/.ssh/authorized_keys
clear
nano ~/.ssh/authorized_keys
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
chown admin:admin ~/.ssh ~/.ssh/authorized_keys
ssh-keygen -lf %USERPROFILE%\.ssh\id_ed25519.pub
awk '!/^#/ && NF' ~/.ssh/authorized_keys   | while read key; do echo "$key" | ssh-keygen -lf /dev/stdin; done
sudo nano /etc/ssh/sshd_config
exit
sudo nano /etc/ssh/sshd_config
exit
cd traefik/
ls
nano docker-compose.ymler
vim docker-compose.yml
cd traefik/nano doc
cd traefik/
nano docker-compose.yml
vim docker-compose.yml
nano
tree
nano docker-compose.yml
mkdir -p ~/traefik/nginx
ls
cd nginx/
ls
touch default.conf
ls
nano default.conf 
cd ..
mkdir -p ~/traefik/backend
nano ~/traefik/backend/upload.php
cd backend/
ls
cd ..
tree
cd ..
tree
cd ~/traefik
docker compose up -d --build
curl -X POST   https://cloud.smartsecurity.solutions/upload.php   -H "X-Secret-Key: YOUR_SHARED_SECRET"   -d '{"deviceId":"dev123","clientId":"clientA","metric":"temp","value":"72"}'
cd ~/traefik
docker compose exec php-fpm php -m | grep -E 'pgsql|PDO'
docker compose exec php-fpm php -r "print_r(PDO::getAvailableDrivers());"
# File: backend/Dockerfile
FROM php:8.3-fpm-alpine
# Install Postgres client libs & enable PDO_PGSQL
RUN apk add --no-cache libpq-dev  && docker-php-ext-install pdo_pgsql
# File: backend/Dockerfile
FROM php:8.3-fpm-alpine
# Install Postgres client libs & enable PDO_PGSQL
RUN apk add --no-cache libpq-dev  && docker-php-ext-install pdo_pgsql
mkdir -p backend
nano backend/Dockerfile
nano docker-compose.yml
mkdir -p backend
nano backend/Dockerfile
cd ~/traefik
docker compose up -d --build php-fpm
docker compose exec php-fpm php -m | grep pgsql
docker compose exec php-fpm php -r "print_r(PDO::getAvailableDrivers());"
nano docker-compose.yml
curl -v -X POST   https://cloud.smartsecurity.solutions/upload.php   -H "X-Secret-Key: YOUR_REAL_SECRET"   -H "Content-Type: application/json"   -d '{"deviceId":"dev123","clientId":"clientA","metric":"temp","value":"72"}'
nano ~/traefik/backend/upload.php
curl -v -X POST   https://cloud.smartsecurity.solutions/upload.php   -H "X-Secret-Key: MyUltraSecretKeyValue123!"   -H "Content-Type: application/json"   -d '{"deviceId":"dev123","clientId":"clientA","metric":"temp","value":"72"}'
# open a psql session inside the db container
docker compose exec db psql -U ssc -d sensordb
# inside psql prompt:
\dt
docker compose exec db   psql -U ssc -d sensordb -c "
  CREATE TABLE IF NOT EXISTS telemetry (
    id SERIAL PRIMARY KEY,
    device_id VARCHAR(64) NOT NULL,
    client_id VARCHAR(64) NOT NULL,
    metric VARCHAR(32) NOT NULL,
    value TEXT NOT NULL,
    ts TIMESTAMPTZ NOT NULL DEFAULT NOW()
  );
  CREATE INDEX IF NOT EXISTS idx_telemetry_device_ts
    ON telemetry(device_id, ts DESC);"
curl -X POST   https://cloud.smartsecurity.solutions/upload.php   -H "X-Secret-Key: MyUltraSecretKeyValue123!"   -H "Content-Type: application/json"   -d '{"deviceId":"dev123","clientId":"clientA","metric":"temp","value":"72"}'
docker compose exec db   psql -U ssc -d sensordb   -c "SELECT id, device_id, client_id, metric, value, ts
      FROM telemetry
      ORDER BY ts DESC
      LIMIT 5;"
cd ~/services/api/app
cd ~/services/api
ls
# 1. Make the `app` directory (if it doesn’t already exist)
mkdir -p app
# 2. Move your top-level app.py into that folder, and rename it to main.py
mv app.py app/main.py
# 3. (Optional) If you see an odd file called `app.api`, you can delete it:
rm -f app.api
ls
cd app
ls
tree
cd ..
tree
ls
nano Dockerfile 
ls
cd app/
ls
nano main.py 
cd ~/traefik
docker compose up -d --build api
cd ~/services/api
nano Dockerfile 
nano ~/traefik/docker-compose.yml
cd ~/traefik
docker compose up -d --build api
nano ~/traefik/docker-compose.yml
vim docker-compose.yml
nano docker-compose.yml
docker compose up -d --build api
nano docker-compose.yml
docker compose up -d --build api
nano docker-compose.yml
docker compose up -d --build api
nano ~/services/api/requirements.txt
docker compose up -d --build api
curl -s https://cloud.smartsecurity.solutions/api/v1/health
curl -s "https://cloud.smartsecurity.solutions/api/v1/telemetry?page=1&page_size=5" | jq
mkdir -p ~/dashboard
cd ~/dashboard
npm create vue@latest admin-dashboard
mkdir -p ~/dashboard
cd ~/dashboard
npm create vue@latest admin-dashboard
sudo apt install npm
npm create vue@latest admin-dashboard
cd admin-dashboard
npm install
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
npm install -g tailwindcss
sudo nano /etc/ssh/sshd_config
sudo systemctl reload ssh
cd ..
sudo systemctl reload ssh
ssh-keygen -lf ~/.ssh/authorized_keys
nano  ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
chown -R admin:admin ~/.ssh
sudo tail -f /var/log/auth.log
exit
cd ~/dashboard/admin-dashboard
npm run dev -- --port 5174
tree
npm install -g tailwindcss
clear
npm install -g tailwindcss
cd ~/dashboard/admin-dashboard
npx tailwindcss init -p
cat > tailwind.config.js << 'EOF'
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./index.html","./src/**/*.{vue,js,ts}"],
  theme: { extend: {} },
  plugins: [],
}
EOF

cat > postcss.config.js << 'EOF'
module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  }
}
EOF

ls
cd src
ls
tree
touch style.css
nano style.css
ls
nano main.js 
cd ~/dashboard/admin-dashboard
npm run dev
cd ~/dashboard/admin-dashboard
npm run dev
cd ~/dashboard/admin-dashboard
# Rename the configs
mv postcss.config.js postcss.config.cjs
mv tailwind.config.js tailwind.config.cjs
npm run dev -- --port 5174
ls
nano postcss.config.cjs 
nano tailwind.config.cjs 
npm run dev -- --port 5174
cd ~/dashboard/admin-dashboard
mv postcss.config.js postcss.config.cjs
mv tailwind.config.js tailwind.config.cjs
cd ~/dashboard/admin-dashboard
ls
npm run dev -- --port 5174
cd ~/traefik
docker compose ps dashboard
cd ~/traefik
docker compose ps dashboard
curl -vk https://admin.smartsecurity.solutions  || echo “Exit code: $? ”
cat > ~/dashboard/admin-dashboard/Dockerfile <<'EOF'
# ---------- build stage ----------
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build         # writes to /app/dist
# ---------- runtime stage ----------
FROM nginx:1.27-alpine
COPY --from=builder /app/dist /usr/share/nginx/html
# tiniest config – just serve static files
EOF

nano ~/traefik/docker-compose.yml
cd ~/traefik
docker compose up -d --build dashboard
cd ~/dashboard/admin-dashboard
nano postcss.config.cjs
nano tailwind.config.cjs
npm ci
npm run build
cd ~/dashboard/admin-dashboard
npm install -D @tailwindcss/postcss
nano postcss.config.cjs
npm ci
npm run build
cd ~/traefik
docker compose up -d --build dashboard
cd traefik/
ls
nano docker-compose.yml
cd ~/traefik
docker compose up -d --build api ws
cd /home/admin/traefik/backend
nano upload.php
cd ~/services/ws/app/
ls
touch main.py
nano main.py 
nano ~/services/ws/Dockerfile
nano ~/services/ws/requirements.txt
nano ~/traefik/docker-compose.yml
cd ~/traefik
docker compose up -d --build ws
cd ~/services/ws
# if you haven’t already:
mkdir -p app
# move your FastAPI code into it:
mv main.py app/main.py
nano services/ws/app/main.py
nano services/ws/requirements.txt
exit
nano ~/dashboard/admin-dashboard/src/App.vue
cd ~/dashboard/admin-dashboard
npm ci
npm run build
cd ~/traefik
docker compose up -d --build dashboard
nano docker-compose.yml
ls
cd services/
ls
cd ws
ls
nano requirements.txt 
nano services/ws/app/main.py
ls
cd app/
ls
touch main.py
nano main.py 
nano services/ws/Dockerfile
cd ..
ls
cd ws
ls
nano Dockerfile 
cd ~/traefik
docker compose up -d --build ws
cd ~/traefik
docker compose config --services
docker compose config | sed -n '/^  api:/,/^[^ ]/p'
cd ~/traefik
docker compose up -d --build ws
cd ~/traefik
docker compose up -d --build ws
docker compose ps ws
docker compose logs ws --tail=20
docker compose ps ws
# you should see “ws” Up (0.0s) on port 8000 internally
docker compose logs ws --tail=20
# look for “Uvicorn running on http://0.0.0.0:8000” and the LISTEN setup
# install wscat if you don’t have it: npm install -g wscat
wscat -c wss://admin.smartsecurity.solutions/ws
curl -X POST https://cloud.smartsecurity.solutions/upload.php   -H "X-Secret-Key: MyUltraSecretKeyValue123!"   -H "Content-Type: application/json"   -d '{"deviceId":"devABC","clientId":"clientA","metric":"press","value":"1013"}'
ls
cd ..
ls
cd services/
ls
tree
cd ..
tree
$ wscat -c wss://admin.smartsecurity.solutions/ws
connected (press CTRL+C to quit)
< {"id":2,"deviceId":"devABC", … }
nano ~/dashboard/admin-dashboard/src/App.vue
cd ~/traefik
docker compose up -d --build dashboard
cd services/api/requirements.txt
cd ser
cd ..
la
cd services/
ls
cd api
ls
nano requirements.txt 
cd ~/traefik
docker compose up -d --build api
nano requirements.txt 
cd ~/services/api
nano requirements.txt 
cd ~/traefik
docker compose build --no-cache api
docker compose up -d api
docker compose ps api
docker compose logs api --tail=20
curl -s https://cloud.smartsecurity.solutions/api/v1/health
# should return {"db":"ok"} or similar
curl -X POST https://cloud.smartsecurity.solutions/api/v1/auth/login   -H "Content-Type: application/x-www-form-urlencoded"   -d "username=admin&password=ChangeMe123!"
curl -X POST https://cloud.smartsecurity.solutions/api/v1/auth/login   -H "Content-Type: application/x-www-form-urlencoded"   -d "username=admin&password=ChangeMe123!"
curl -X POST "https://cloud.smartsecurity.solutions/api/v1/auth/login"   -H "Content-Type: application/x-www-form-urlencoded"   -d "username=admin&password=ChangeMe123!"
cd services/api/app
cd services/api
ls
cd ..
ls
cs serv
cd services/
cd api
ls
cd app
ls
la
nano main.py 
vim services/api/app/main.py
nano main.py
cd ~/traefik
docker compose up -d --build api
curl -X POST   "https://cloud.smartsecurity.solutions/api/v1/auth/login"   -H "Content-Type: application/x-www-form-urlencoded"   -d "username=admin&password=ChangeMe123!"
nano services/api/app/main.py
cd services/api/app/
cd ~services/api/app/
cd ..
ls
cd services/
nano services/api/app/main.py
cd api
cd app/app
cd ~/services/api/app/
ls
nano main.py 
cd ~/traefik
docker compose up -d --build api
docker compose exec api sh -c '\
  curl -X POST http://localhost:5000/v1/auth/login \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=admin&password=ChangeMe123!" \
  && echo'
docker compose exec api sh -c '\
  curl -X POST http://localhost:5000/v1/auth/login \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=admin&password=ChangeMe123!" \
  && echo'
cd ~/traefik
docker compose up -d api   # bring the API back up, just in case
docker compose exec api sh -c " \
  curl -X POST http://localhost:5000/v1/auth/login \
    -H 'Content-Type: application/x-www-form-urlencoded' \
    -d 'username=admin&password=ChangeMe123!' \
  && echo"
docker compose logs api --tail=50
cd ..
cd services/
tree
cd app
cd api/
ls
tree
cd app/
tree
touch __init__.py
touch auth.py
cd ~/traefik
docker compose up -d --build api
docker compose config | sed -n '/^  api:/,/^[^ ]/p'
cd ~/traefik
docker compose up -d --build api
docker compose ps api
cd ~/services/api
# 1. Remove or rename the stray files:
mv app.api old-app.api.backup
mv app.py old-app.py.backup
# 2. Create a real `app/` directory:
mkdir app
# 3. Move your code into it:
#    – main.py should go to app/main.py
#    – auth.py (the file we generated) into app/auth.py
#    – any other modules (schemas.py, models.py, etc.) into app/
mv old-app.py app/main.py    # if your main entrypoint was in old-app.py
# and mv the auth.py you created into app/auth.py
# 4. Add __init__.py so Python sees it as a package:
touch app/__init__.py
# 5. Now your tree should look like:
# services/api
# ├── Dockerfile
# ├── requirements.txt
# └── app
#     ├── __init__.py
#     ├── main.py
#     └── auth.py
tree
nano Dockerfile 
cd ~/traefik
docker compose up -d --build api
docker compose ps api
docker compose exec api sh -c "\
  curl -i http://localhost:5000/v1/health && \
  curl -i -X POST http://localhost:5000/v1/auth/login \
     -H 'Content-Type: application/x-www-form-urlencoded' \
     -d 'username=admin&password=ChangeMe123!' \
  && echo"
nano traefik/docker-compose.yml
ls
nano docker-compose.yml
cd ~/traefik
docker compose up --build api
cd ..
cd services/
cd api
ls
nanoo Dockerfile 
nano Dockerfile 
cd ..
tree
cd api/
nano Dockerfile 
cd ~/traefik
docker compose up -d --build api
cd ..
cd service
cd services/
cd api/
nano Dockerfile 
tree
ls
nano requirements.txt 
docker compose up -d --build api
cd ..
docker compose up -d --build api
cd traefik/
docker compose up -d --build api
docker compose ps api
# Should show traefik-api-1 Up ... Ports 0.0.0.0:5000->5000/tcp
docker compose exec api sh -c "\
  curl -i http://localhost:5000/v1/health && \
  curl -i -X POST http://localhost:5000/v1/auth/login \
    -H 'Content-Type: application/x-www-form-urlencoded' \
    -d 'username=admin&password=ChangeMe123!' \
  && echo"
docker ps -a | grep traefik-api
docker exec -it traefik-api-1 sh -c "\
  curl -i http://localhost:5000/v1/health && echo \
  && curl -i -X POST http://localhost:5000/v1/auth/login \
       -H 'Content-Type: application/x-www-form-urlencoded' \
       -d 'username=admin&password=ChangeMe123!' \
      && echo"
# Show the last 50 lines of the API service logs:
docker compose logs api --tail 50
cd /
htop
cd services/api
ls
tree
cd ~/traefik
cd ..
cd services/
ls
cd api/
nano requirements.txt 
docker compose up -d --build api
cd ~/traefik/
docker compose up -d --build api
docker compose logs api --tail 20    # should show no errors on startup
docker compose exec api sh -c "\
  curl -i http://localhost:5000/v1/health && echo \
  && curl -i -X POST http://localhost:5000/v1/auth/login \
       -H 'Content-Type: application/x-www-form-urlencoded' \
       -d 'username=admin&password=ChangeMe123!' \
      && echo"
cd ..
cd services/api
ls
nano requirements.txt 
cd ~/traefik
docker compose up -d --build api
docker compose ps api
# expect: traefik-api-1  Up ... 0.0.0.0:5000->5000/tcp
docker compose exec api sh -c "\
  curl -i http://localhost:5000/v1/health && echo \
  && curl -i -X POST http://localhost:5000/v1/auth/login \
       -H 'Content-Type: application/x-www-form-urlencoded' \
       -d 'username=admin&password=ChangeMe123!' && echo"
# Health-check
curl -i http://localhost:5000/v1/health
# Login
curl -i -X POST http://localhost:5000/v1/auth/login      -H 'Content-Type: application/x-www-form-urlencoded'      -d 'username=admin&password=ChangeMe123!'
# Health-check
curl -i http://localhost:5000/v1/health
# Login
curl -i -X POST http://localhost:5000/v1/auth/login      -H 'Content-Type: application/x-www-form-urlencoded'      -d 'username=admin&password=ChangeMe123!'
docker compose exec api sh   # drop into a shell
top
cd traefik/
docker compose exec api sh
curl -i https://cloud.smartsecurity.solutions/api/v1/health
curl -i -X POST https://cloud.smartsecurity.solutions/api/v1/auth/login      -H "Content-Type: application/x-www-form-urlencoded"      -d "username=admin&password=ChangeMe123!"
nano services/api/Dockerfile
cd ~/traefik
docker compose build --no-cache api
docker compose up -d api
docker compose logs api --tail=20
# inside the api container
docker compose exec api sh -c "\
  curl -X POST http://localhost:5000/v1/auth/login \
    -H 'Content-Type: application/x-www-form-urlencoded' \
    -d 'username=admin&password=ChangeMe123!' \
  && echo"
curl -X POST "https://cloud.smartsecurity.solutions/api/v1/auth/login"   -H "Content-Type: application/x-www-form-urlencoded"   -d "username=admin&password=ChangeMe123!"
cd ..
touch services/api/app/__init__.py
cd services/
cd api/
cd app
ls
nano services/api/Dockerfile
cd ..
ls
nano Dockerfile 
cd ~/traefik
docker compose build --no-cache api
docker compose up -d api
docker compose ps api
# get a shell inside the healthy api container
docker compose exec api sh
# from the /app/app folder, list files:
ls /app/app
# you should see: __init__.py  main.py  auth.py
# now test the login route:
curl -X POST http://localhost:5000/v1/auth/login   -H "Content-Type: application/x-www-form-urlencoded"   -d "username=admin&password=ChangeMe123!"   && echo
nano traefik/docker-compose.yml
ls
rm docker-compose.ymler
ls
nano docker-compose.yml
cd ~/traefik
docker compose up --build api
docker compose logs api --tail=50
cd ..
nano services/api/app/auth.py
cd services/
tree
cd api/app
ls
nanp auth.py 
nano auth.py 
cd ~/traefik
docker compose build --no-cache api
docker compose up -d api
curl -X POST "https://cloud.smartsecurity.solutions/api/v1/auth/login"   -H "Content-Type: application/x-www-form-urlencoded"   -d "username=admin&password=ChangeMe123!"
curl -i https://cloud.smartsecurity.solutions/api/v1/health
tree
curl -i https://cloud.smartsecurity.solutions/api/v1/health
docker compose exec api sh -c " \
  curl -i http://localhost:5000/v1/health \
  && echo"
nano docker-compose.yml
# 1) Bring up (or rebuild + bring up) just the API service
docker compose up -d --build api
# 2) Check it’s healthy/running
docker compose ps api
# you should see something like:
#   Name         Command    State      Ports
# ------------------------------------------------
#   traefik-api-1 uvicorn…    Up 0.0.0.0:5000->5000/tcp
# 3) Now exec into it and hit /v1/health directly:
docker compose exec api sh -c "\
  curl -i http://localhost:5000/v1/health && echo"
docker compose up -d --build api
cd ~/traefik
docker compose up -d --build api
docker compose exec api sh
cd traefik/
docker compose exec api sh
cd ~/services/api/app/
nano main.py
cd ~/traefik/
docker compose up -d --build
docker compose exec api sh -c "\
  apt-get update && apt-get install -y curl \
  && curl -i http://localhost:5000/v1/health \
"
cd ~/services/api/app
nano main.py 
cd ~/traefik/
docker compose up -d --build api
docker compose exec api sh -c "\
  apt-get update && apt-get install -y curl \
  && curl -i http://localhost:5000/v1/health \
"
curl -i https://cloud.smartsecurity.solutions/api/v1/health
exit
nano /home/admin/docker-compose.yml
ls
cd traefic
cd traefik/
ls
cd /home/admin/traefik
nano docker-compose.yml     # open the file you already have
git add docker-compose.yml
git commit -m "feat(infra): add Postgres db service to docker-compose"
git push
# Launch only the DB (or all services if you prefer)
docker compose up -d db
vim docker-compose.yml
docker compose up -d db
docker compose ps
cd /home/admin/backend
source .venv/bin/activate
pip install alembic
alembic init alembic
ls
cd alembic/
touch env.py
nano env.py 
alembic revision --autogenerate -m "create devices/sensors/actuators"
alembic upgrade head
cd ...
cd ..
source .venv/bin/activate    # if you’re using the venv
alembic init alembic
cd /home/admin/backend
source .venv/bin/activate    # if you’re using the venv
alembic init alembic
tree
cd /home/admin/backend
mv alembic alembic_backup
cd /home/admin/backend
mv alembic alembic_backup
tree
# Still in /home/admin/backend, and with your venv active:
alembic init alembic
tree
cd alembic
ls
nano env.py 
alembic revision --autogenerate -m "create devices, sensors, actuators"
alembic upgrade head
ls
cd ..
ls
alembic revision --autogenerate -m "create devices, sensors, actuators"
alembic upgrade head
cd /home/admin/backend
source .venv/bin/activate    # (skip if already active)
pip install python-dotenv
nano /home/admin/backend/.env
ls
tree
cd /home/admin/backend
nano .env
la
source .venv/bin/activate
alembic revision --autogenerate -m "create devices, sensors, actuators tables"
alembic upgrade head
cd /home/admin/backend/app
mv db.py.save db.py
cd /home/admin/backend/app
nano models.py
cd /home/admin/backend
tree app -L 1
cd /home/admin/backend
source .venv/bin/activate      # if you’re in a virtual-env
# Generate a fresh migration
alembic revision --autogenerate -m "create devices, sensors, actuators tables"
# Apply it
alembic upgrade head
cd /home/admin/backend
source .venv/bin/activate      # if it’s not already active
pip install asyncpg
pip freeze | grep -E "asyncpg|python-dotenv" >> requirements.txt
git add requirements.txt
git commit -m "chore: add asyncpg & python-dotenv to backend requirements"
git push
alembic upgrade head
cd /home/admin/backend
source .venv/bin/activate
pip install greenlet
alembic upgrade head
cd alembic
ls
nano env.py 
cd..
cd ..
pip install psycopg2-binary python-dotenv
alembic revision --autogenerate -m "sync migrate"
alembic upgrade head
alembic revision --autogenerate -m "sync migrate"
alembic upgrade head
pip install psycopg2-binary python-dotenv
alembic revision --autogenerate -m "sync migrate"
alembic upgrade head
cd ..
cd traefik/
nano docker-compose.yml
docker compose build api
docker compose up -d
docker compose logs -f api
docker compose exec api bash
pip install alembic
alembic init migrations
nano docker-compose.yml
docker compose up -d --build
ls -a
ls services/api/.env
cp services/api/.env .
# now /home/admin/traefik/.env exists
docker compose up -d --build
ln -s services/api/.env .env
docker compose up -d --build
# From your project root (/home/admin/traefik)
git add .
git commit -m "WIP: snapshot before rollback"
git tag pre-rollout
git log --oneline services/api
cd ..
git log --oneline services/api
git reset --hard abc1234
git status
git log --oneline
git reset --hard 1398d13
git stash list
git stash pop
git cherry-pick <that-WIP-commit-hash>
# 1️⃣ Confirm you’re really in the repo root
git rev-parse --show-toplevel
# 2️⃣ Show branch, staged / unstaged changes, *and* every untracked file
git status --branch --untracked-files=all
# 3️⃣ Show the last 20 commits so I can see where HEAD is
git log --oneline --graph --decorate -n 20
cd /home/admin/
ls
la
cd /home/admin                # make sure you’re in the same dir that shows .git
cat <<'EOF' > .gitignore
# ─── Python ───────────────────────────────────────────────
__pycache__/
*.py[cod]
*.pyo
*.pyd

# ─── Virtual-envs ─────────────────────────────────────────
.venv/
env/
venv/

# ─── Logs & runtime files ─────────────────────────────────
*.log
*.sqlite
*.db
uvicorn.log

# ─── Environment / secrets ────────────────────────────────
.env
.env.*

# ─── Node / Vue ───────────────────────────────────────────
node_modules/
*.lock
!package-lock.json   # keep npm lock file if you like
!.npmrc

# ─── Front-end build artefacts ────────────────────────────
dist/
build/

# ─── Editor / OS clutter ──────────────────────────────────
.DS_Store
.idea/
.vscode/
.cache/
EOF

cat <<'EOF' > ~/.gitignore_global
__pycache__/
*.py[cod]
*.log
.DS_Store
EOF

git config --global core.excludesfile ~/.gitignore_global
# Remove everything from the index, keep it on disk
git rm -r --cached .
# Add what we actually care about
git add backend dashboard services traefik docker-compose.yml README.md
# Verify
git status
git commit -m "chore: add .gitignore and stage baseline project files"
git push origin main
git fetch origin
git rebase origin/main
git fetch origin git rebase origin/main
git checkout main
git pull origin main
git push origin main
# Run from repo root
tree -L 2 -a | head -n 50
# Ensure any old Uvicorn logs aren’t confusing you
rm -f backend/uvicorn.log
# Export a dummy DB URL so the health check can at least start
export DATABASE_URL="postgresql://dummy:dummy@localhost:5432/postgres"
# Launch Uvicorn from your repo root:
python -m uvicorn backend.app.main:app --port 8000 --reload
# See what’s listening
lsof -iTCP:8000 -sTCP:LISTEN
# Example output:
# COMMAND   PID   ...  NAME
# python   1234   ...  TCP *:8000 (LISTEN)
# Kill that PID (replace 1234 with whatever you saw)
kill -9 1234
sudo netstat -tulpn | grep :8000
pkill -f uvicorn
sudo fuser -k 8000/tcp
python -m uvicorn backend.app.main:app --port 8000 --reload
# Start only the database; avoids noise from other services
docker compose up -d db
docker compose logs -f db          # watch for “database system is ready”
docker  compose up 
tree
clear'
clear
# Start only the database; avoids noise from other services
docker compose up -d db
docker compose logs -f db          # watch for “database system is ready”
cd traefik/
# from your home (~) or any parent folder of the repo
find . -maxdepth 3 -type f \( -name "docker-compose*.yml" -o -name "compose.yml" \)
cd /path/that/contains/compose-file
ls -1
# verify the compose file is visible here
docker compose config --services
# replace db with the exact service name if it differs
docker compose up -d db
docker compose logs -f db
cd backend/
uvicorn app.main:app --reload --port 8000
curl http://127.0.0.1:8000/v1/health
cd ..
curl http://127.0.0.1:8000/v1/health
cd ~/cloud.smartsecurity.solutions   # or wherever you cloned your repo
ls docker-compose.yml
cd traefik/
docker compose up -d db
docker compose up -d
docker compose logs db --tail=20
curl http://127.0.0.1:8000/v1/health
cd ..
curl http://127.0.0.1:8000/v1/health
clear
cd traefik/ 
docker compose up -d db
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
