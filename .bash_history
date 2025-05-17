nano /home/admin/.ssh/authorized_keys
exit
sudo nano /etc/ssh/sshd_config
sudo systemctl reload sshd
sudo systemctl reload ssh
sudo systemctl restart ssh
sudo sshd -T | grep -E 'permitrootlogin|passwordauthentication|challengeresponseauthentication'
sudo grep -n 'PasswordAuthentication' /etc/ssh/sshd_config
sudo grep -R 'PasswordAuthentication' /etc/ssh
sudo nano /etc/ssh/sshd_config.d/50-cloud-init.conf
sudo systemctl restart ssh
sshd -T | grep -E 'permitrootlogin|passwordauthentication|challengeresponseauthentication'
sudo nano /etc/ssh/sshd_config.d/50-cloud-init.conf
sudo systemctl restart ssh
sudo sshd -T | grep -E 'permitrootlogin|passwordauthentication|challengeresponseauthentication'
# 1. Update package lists and install UFW
sudo apt update && sudo apt install -y ufw
# 2. Set default policies: deny all incoming, allow all outgoing
sudo ufw default deny incoming
sudo ufw default allow outgoing
# 3. Allow necessary ports for SSH, HTTP, and HTTPS
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP (for ACME HTTP-01 challenge)
sudo ufw allow 443/tcp   # HTTPS
# 4. Enable UFW
sudo ufw --force enable
# 5. (Optional) Check status
sudo ufw status verbose
sudo ufw status
# 1. Install Fail2Ban
sudo apt update && sudo apt install -y fail2ban
# 2. Create a jail for SSH in /etc/fail2ban/jail.d/sshd.conf
sudo tee /etc/fail2ban/jail.d/sshd.conf << 'EOF'
[sshd]
enabled   = true
port      = ssh
filter    = sshd
logpath   = /var/log/auth.log
maxretry  = 5
bantime   = 3600
EOF

# 3. Enable and start the service
sudo systemctl enable --now fail2ban
# 4. Check the SSH jail status
sudo fail2ban-client status sshd
# 1. Install Docker via the official convenience script
curl -fsSL https://get.docker.com | sudo sh
# 2. Install the Docker Compose plugin
sudo apt update
sudo apt install -y docker-compose-plugin
# 3. Add your user to the docker group so you can run Docker without sudo
sudo usermod -aG docker admin
# 4. Enable and start Docker
sudo systemctl enable docker
sudo systemctl start docker
# 5. Verify the installation
docker version
docker compose version
docker version
docker compose version
[200~exit   # drops your current admin session
ssh admin@198.38.89.127
clear
exit
docker version
docker compose version
mkdir -p ~/traefik
cd ~/traefik
touch acme.json
chmod 600 acme.json
# 1. Create the static config
cat << 'EOF' > traefik.yml
# Traefik static configuration
entryPoints:
  web:
    address: ":80"
  websecure:
    address: ":443"

providers:
  docker:
    endpoint: "unix:///var/run/docker.sock"
    exposedByDefault: false

certificatesResolvers:
  le:
    acme:
      email: contact@smartsecurity.solutions
      storage: acme.json
      httpChallenge:
        entryPoint: web
EOF

# 2. Create the Docker Compose file
cat << 'EOF' > docker-compose.yml
version: "3.8"

services:
  traefik:
    image: traefik:v2.9
    restart: unless-stopped
    command:
      - --configFile=/etc/traefik/traefik.yml
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./traefik.yml:/etc/traefik/traefik.yml:ro
      - ./acme.json:/acme.json
      - /var/run/docker.sock:/var/run/docker.sock:ro
    labels:
      - "traefik.enable=true"
EOF

docker compose up -d
docker compose ps
# A. Make a folder for the service
mkdir -p ~/services/api
cd ~/services/api
# B. Write the app
cat << 'EOF' > app.py
from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/")
def root():
    return jsonify(status="ok", message="Hello from SmartSecurity API")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
EOF

# C. Pin the dependency
echo "Flask==3.0.2" > requirements.txt
# D. Create a minimal Dockerfile
cat << 'EOF' > Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
CMD ["python", "app.py"]
EOF

cd ~/traefik
nano docker-compose.yml
docker compose up -d --build
curl -k https://cloud.smartsecurity.solutions/api
# → {"status":"ok","message":"Hello from SmartSecurity API"}
nano docker-compose.yml
cd ~/traefik
docker compose up -d --build
curl -k https://cloud.smartsecurity.solutions/api
cd ~/traefik
nano docker-compose.yml
cd ~/traefik
docker compose up -d --build
curl -k https://cloud.smartsecurity.solutions/api
cd ~/traefik
nano docker-compose.yml
docker compose up -d
docker compose ps db
docker compose up -d
docker compose ps db
cd ~/traefik
nano docker-compose.yml
docker compose up -d
cd ~/traefik
nano docker-compose.yml
cd ~/services/api
echo "psycopg2-binary==2.9.5" >> requirements.txt
nano app.py
cd ~/services/api
nano app.py
echo -e "Flask==3.0.2\npsycopg2-binary==2.9.5" > requirements.txt
cd ~/traefik
docker compose up -d --build api
curl -k https://cloud.smartsecurity.solutions/api      # health check
curl -k -X POST https://cloud.smartsecurity.solutions/api/data -H "Content-Type: application/json" -d '{"foo":"bar"}'
curl -k https://cloud.smartsecurity.solutions/api/dbtest
cd ~/traefik
nano docker-compose.yml
docker compose up -d --build
# 1. Health-check
curl -k https://cloud.smartsecurity.solutions/api
# → {"status":"ok","message":"Hello from SmartSecurity API"}
# 2. Ingest a sample payload
curl -k -X POST https://cloud.smartsecurity.solutions/api/data      -H "Content-Type: application/json"      -d '{"foo": "bar"}'
# → {"status":"ok"}
# 3. Read-back from the DB
curl -k https://cloud.smartsecurity.solutions/api/dbtest
# → {"records":1}
cd ~/services/api
nano app.py
echo -e "Flask==3.0.2\npsycopg2-binary==2.9.5" > requirements.txt
cd ~/traefik
docker compose up -d --build api
curl -k https://cloud.smartsecurity.solutions/api
# → {"status":"ok","message":"Hello from SmartSecurity API"}
curl -k -X POST https://cloud.smartsecurity.solutions/api/data      -H "Content-Type: application/json"      -d '{"foo":"bar"}'
# → {"status":"ok"}
curl -k https://cloud.smartsecurity.solutions/api/dbtest
# → {"records":1}
docker compose up -d --build api
curl -k https://cloud.smartsecurity.solutions/api
# → {"status":"ok","message":"Hello from SmartSecurity API"}
curl -k -X POST https://cloud.smartsecurity.solutions/api/data      -H "Content-Type: application/json"      -d '{"foo":"bar"}'
# → {"status":"ok"}
curl -k https://cloud.smartsecurity.solutions/api/dbtest
# → {"records":1}
curl -s -k https://cloud.smartsecurity.solutions/api/dbtest
# 1. Dump the Flask app inside the container
docker compose exec api cat /app/app.py | sed -n '1,200p'
# 1. Dump the Flask app inside the container
docker compose exec api cat /app/app.py | sed -n 
docker compose exec api cat /app/app.py | sed -n '1,200p'
cd ~/traefik
docker compose logs api --tail 50
cd ~/services/api/app.py
cd ~/services/api/
nano app.api
cd ~/services/api
nano app.py
nano requirements.txt 
cd ~/traefik
docker compose up -d --build api
curl -s -k https://cloud.smartsecurity.solutions/api
# → {"status":"ok","message":"Hello from SmartSecurity API"}
curl -s -k -X POST https://cloud.smartsecurity.solutions/api/data   -H "Content-Type: application/json" -d '{"foo":"bar"}'
# → {"status":"ok"}
curl -s -k https://cloud.smartsecurity.solutions/api/dbtest
# → {"records":1}
nano app.py
ls
cd ~/services/api
nano app.py
echo -e "Flask==3.0.2\npsycopg2-binary==2.9.5" > requirements.txt
cd ~/traefik
docker compose up -d --build api
cd ~/traefik
docker compose up -d --build api
curl -s -k https://cloud.smartsecurity.solutions/api/dbtest
curl -i -s -k -X POST https://cloud.smartsecurity.solutions/api/data      -H "Content-Type: application/json"      -d '{"foo":"bar"}'
docker compose logs api --tail 50
cd ~/services/api
nano app.py
ls
nano requirements.txt 
cd ~/traefik
docker compose up -d --build api
curl -s -k https://cloud.smartsecurity.solutions/api
curl -s -k -X POST https://cloud.smartsecurity.solutions/api/data      -H "Content-Type: application/json"      -d '{"foo":"bar"}'
curl -s -k https://cloud.smartsecurity.solutions/api/dbtest
# A) Make the folder and switch into it
mkdir -p ~/services/ws
cd ~/services/ws
# B) Write the FastAPI app
cat << 'EOF' > app.py
from fastapi import FastAPI, WebSocket

app = FastAPI()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        msg = await websocket.receive_text()
        await websocket.send_text(f"Echo: {msg}")
EOF

# C) Pin dependencies
cat << 'EOF' > requirements.txt
fastapi==0.100.0
uvicorn==0.23.1
EOF

# D) Create the Dockerfile
cat << 'EOF' > Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
CMD ["uvicorn","app:app","--host","0.0.0.0","--port","8000"]
EOF

cd ~/traefik
nano docker-compose.yml
cd ~/traefik
nano docker-compose.yml
cd ~/traefik
docker compose up -d --build ws
ls
nano docker-compose.yml
cd ~/traefik
ls
rm docker-compose.yml.save*
ls
nano docker-compose.yml 
cd ~/traefik
docker compose up -d --build ws
docker compose ps ws
cd ~/traefik
nano docker-compose.yml
cd ~/traefik
docker compose up -d --build
docker compose ps
mkdir -p ~/services/bridge
cd ~/services/bridge
ls
nano app.py
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
