# Frontend Admin Nginx Configuration Fix

## Issue
The `frontend_admin` container is failing with the error:
```
host not found in upstream "backend" in /etc/nginx/conf.d/default.conf:35
```

## Root Cause
The nginx configuration is trying to connect to a service named "backend", but the actual service name in docker-compose.yml is "api".

## Solution

### Option 1: Quick Fix (Recommended)

Run the automated fix script:
```bash
chmod +x fix_frontend_admin_nginx.sh
./fix_frontend_admin_nginx.sh
```

### Option 2: Manual Fix

1. **Stop the problematic container:**
   ```bash
   docker-compose stop frontend_admin
   ```

2. **Remove the container:**
   ```bash
   docker-compose rm -f frontend_admin
   ```

3. **Verify the nginx configuration is correct:**
   ```bash
   grep "proxy_pass" frontend_admin/nginx.conf
   ```
   Should show: `proxy_pass http://api:8000/api/;`

4. **Rebuild the container:**
   ```bash
   docker-compose build --no-cache frontend_admin
   ```

5. **Start the service:**
   ```bash
   docker-compose up -d frontend_admin
   ```

6. **Check the logs:**
   ```bash
   docker-compose logs --tail=20 frontend_admin
   ```

### Option 3: Complete Service Restart

If the above doesn't work, restart all services:

```bash
# Stop all services
docker-compose down

# Start all services
docker-compose up -d

# Check status
docker-compose ps

# Check logs
docker-compose logs --tail=50 frontend_admin
```

## Verification

After applying the fix, verify that:

1. **No nginx errors in logs:**
   ```bash
   docker-compose logs frontend_admin | grep -i error
   ```

2. **Container is running:**
   ```bash
   docker-compose ps frontend_admin
   ```

3. **Health check passes:**
   ```bash
   curl -s http://localhost:8083/health
   ```

## Configuration Details

The correct nginx configuration should have:
```nginx
location /api/ {
    proxy_pass http://api:8000/api/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_connect_timeout 30s;
    proxy_send_timeout 30s;
    proxy_read_timeout 30s;
    proxy_buffering off;
}
```

## Troubleshooting

If the issue persists:

1. **Check service names in docker-compose.yml:**
   ```bash
   grep -A 5 "api:" docker-compose.yml
   ```

2. **Verify network connectivity:**
   ```bash
   docker network ls
   docker network inspect cloud_backend
   ```

3. **Check if API service is healthy:**
   ```bash
   docker-compose ps api
   docker-compose logs api --tail=10
   ```

4. **Test API connectivity directly:**
   ```bash
   curl -s http://localhost:8082/api/v1/health
   ```

## Expected Result

After the fix, the frontend_admin container should:
- Start without nginx errors
- Be able to proxy API requests to the backend
- Show "healthy" status in docker-compose ps
- Have no "host not found" errors in logs 