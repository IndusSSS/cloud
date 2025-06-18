#!/bin/sh
set -e

ssh -o StrictHostKeyChecking=no admin@198.38.89.127 <<'SH'
cd /home/admin/smartsecurity/Cloud
git pull
docker compose pull
docker compose up -d --remove-orphans
SH
