#!/usr/bin/env python3
"""
Simplified test version of SmartSecurity.Solutions Cloud
This version can run without database dependencies for testing purposes.
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Form, Header
from fastapi.security import HTTPBearer
from datetime import datetime, timedelta
import jwt
import json
from typing import Optional

# Test configuration
SECRET_KEY = "test-secret-key-for-development-only"
ALGORITHM = "HS256"

app = FastAPI(
    title="SmartSecurity Cloud - Test Version",
    version="3.0.0",
    description="Test version without database dependencies"
)

# In-memory storage for testing
test_users = {
    "admin": {
        "id": "admin-123",
        "username": "admin",
        "email": "admin@example.com",
        "hashed_password": "hashed_admin123",  # In real app, this would be Argon2 hashed
        "is_active": True,
        "is_admin": True,
        "tenant_id": "default"
    }
}

test_devices = []
test_sensor_data = []

# WebSocket connections
active_connections = {}

def create_test_token(user_id: str) -> str:
    """Create a test JWT token"""
    payload = {
        "sub": user_id,
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verify_test_token(token: str) -> Optional[dict]:
    """Verify a test JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None

# Security scheme
security = HTTPBearer(auto_error=False)

@app.get("/api/v1/health", tags=["health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "3.0.0",
        "mode": "test"
    }

@app.get("/api/v1/docs", tags=["documentation"])
async def get_docs():
    """Get API documentation"""
    return {"message": "API documentation available at /docs"}

@app.post("/api/v1/auth/login", tags=["authentication"])
async def login(username: str = Form(...), password: str = Form(...)):
    """Test login endpoint"""
    if username in test_users and test_users[username]["hashed_password"] == f"hashed_{password}":
        user = test_users[username]
        token = create_test_token(user["id"])
        return {
            "access_token": token,
            "token_type": "bearer",
            "user_id": user["id"],
            "username": user["username"],
            "is_admin": user["is_admin"]
        }
    else:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

@app.post("/api/v1/auth/register", tags=["authentication"])
async def register(user_data: dict):
    """Test registration endpoint"""
    username = user_data.get("username")
    email = user_data.get("email")
    password = user_data.get("password")
    
    if not username or not email or not password:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username, email, and password are required"
        )
    
    if username in test_users:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists"
        )
    
    new_user = {
        "id": f"user-{len(test_users) + 1}",
        "username": username,
        "email": email,
        "hashed_password": f"hashed_{password}",
        "is_active": True,
        "is_admin": False,
        "tenant_id": "default"
    }
    test_users[username] = new_user
    
    return {
        "id": new_user["id"],
        "username": new_user["username"],
        "email": new_user["email"],
        "is_active": new_user["is_active"]
    }

@app.get("/api/v1/auth/me", tags=["authentication"])
async def get_current_user(authorization: Optional[str] = Header(None)):
    """Get current user info"""
    from fastapi import HTTPException, status, Header
    
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No valid authorization header provided"
        )
    
    token = authorization.replace("Bearer ", "")
    
    payload = verify_test_token(token)
    if not payload:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    user_id = payload.get("sub")
    for user in test_users.values():
        if user["id"] == user_id:
            return {
                "id": user["id"],
                "username": user["username"],
                "email": user["email"],
                "is_active": user["is_active"],
                "is_admin": user["is_admin"],
                "created_at": datetime.utcnow().isoformat(),
                "last_login": datetime.utcnow().isoformat()
            }
    
    from fastapi import HTTPException, status
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="User not found"
    )

@app.get("/api/v1/devices", tags=["devices"])
async def get_devices(authorization: Optional[str] = Header(None)):
    """Get list of devices"""
    if not authorization or not authorization.startswith("Bearer "):
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No valid authorization header provided"
        )
    
    token = authorization.replace("Bearer ", "")
    payload = verify_test_token(token)
    if not payload:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    return test_devices

@app.post("/api/v1/devices", tags=["devices"])
async def create_device(device_data: dict, authorization: Optional[str] = Header(None)):
    """Create a new device"""
    if not authorization or not authorization.startswith("Bearer "):
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No valid authorization header provided"
        )
    
    token = authorization.replace("Bearer ", "")
    payload = verify_test_token(token)
    if not payload:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    name = device_data.get("name")
    description = device_data.get("description")
    
    if not name:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Device name is required"
        )
    
    device = {
        "id": f"device-{len(test_devices) + 1}",
        "name": name,
        "description": description,
        "is_active": True,
        "created_at": datetime.utcnow().isoformat()
    }
    test_devices.append(device)
    
    return device

@app.post("/api/v1/ingest/root/v1/health", tags=["data ingestion"])
async def ingest_health_data(data: dict):
    """Ingest health beacon data"""
    # Store the data
    sensor_record = {
        "id": f"sensor-{len(test_sensor_data) + 1}",
        "device_id": data.get("deviceId"),
        "data": data,
        "timestamp": datetime.utcnow().isoformat()
    }
    test_sensor_data.append(sensor_record)
    
    # Broadcast to WebSocket connections if any
    if active_connections:
        message = json.dumps({
            "type": "health_data",
            "device_id": data.get("deviceId"),
            "data": data,
            "timestamp": sensor_record["timestamp"]
        })
        for connections in active_connections.values():
            for ws in connections:
                try:
                    await ws.send_text(message)
                except:
                    pass
    
    return {"status": "ok", "message": "Health data ingested successfully"}

@app.websocket("/ws/{tenant_id}")
async def websocket_endpoint(websocket: WebSocket, tenant_id: str):
    """WebSocket endpoint for real-time data"""
    await websocket.accept()
    
    if tenant_id not in active_connections:
        active_connections[tenant_id] = set()
    active_connections[tenant_id].add(websocket)
    
    try:
        while True:
            # Keep connection alive
            data = await websocket.receive_text()
            # Echo back for testing
            await websocket.send_text(json.dumps({
                "type": "echo",
                "message": data,
                "timestamp": datetime.utcnow().isoformat()
            }))
    except WebSocketDisconnect:
        if tenant_id in active_connections:
            active_connections[tenant_id].discard(websocket)
            if not active_connections[tenant_id]:
                del active_connections[tenant_id]

@app.get("/", tags=["root"])
async def root():
    """Root endpoint"""
    return {
        "message": "SmartSecurity.Solutions Cloud - Test Version",
        "version": "3.0.0",
        "status": "running",
        "timestamp": datetime.utcnow().isoformat(),
        "endpoints": {
            "health": "/api/v1/health",
            "docs": "/api/v1/docs",
            "login": "/api/v1/auth/login",
            "devices": "/api/v1/devices",
            "websocket": "/ws/{tenant_id}"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 