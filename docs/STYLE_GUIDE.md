# Style Guide

Essential coding conventions for the SmartSecurity Cloud platform.

## Python Backend

### Naming
```python
# Variables and functions: snake_case
user_id = "user123"
async def authenticate_user(credentials):
    pass

# Classes: PascalCase
class AuthenticationService:
    pass

# Constants: UPPER_SNAKE_CASE
MAX_LOGIN_ATTEMPTS = 5
```

### Type Hints
```python
# Always use type hints
async def get_user(user_id: str) -> Optional[User]:
    pass

# Variables with types
user: Optional[User] = None
device_list: List[Dict[str, Any]] = []
```

### Imports
```python
# Standard library
import asyncio
from datetime import datetime

# Third-party
from fastapi import FastAPI
from sqlmodel import Field, select

# Local
from app.models.user import User
from app.services.auth import AuthenticationService
```

## Frontend (Vue.js)

### Component Structure
```vue
<template>
  <!-- Template content -->
</template>

<script setup lang="ts">
// Imports
import { ref, computed } from 'vue'

// Props
interface Props {
  userId: string
}
const props = defineProps<Props>()

// Reactive data
const loading = ref(false)
const user = ref<User | null>(null)

// Methods
const fetchUser = async () => {
  // Implementation
}
</script>
```

### CSS/Tailwind
```vue
<!-- Use Tailwind utility classes -->
<div class="flex flex-col space-y-4 p-6 bg-white rounded-lg shadow-md">
  <h2 class="text-2xl font-bold text-gray-900">Title</h2>
</div>
```

## Database

### SQL Conventions
```sql
-- Tables: snake_case
CREATE TABLE user_sessions (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes: descriptive names
CREATE INDEX idx_users_email ON users(email);
```

## Testing

### Test Structure
```python
class TestAuthentication:
    async def test_successful_login(self):
        # Arrange
        credentials = {"username": "test", "password": "pass"}
        
        # Act
        result = await auth_service.login(credentials)
        
        # Assert
        assert result["success"] == True
```

## Documentation

### Docstrings
```python
async def authenticate_user(credentials: LoginCredentials) -> User:
    """
    Authenticate user with rate limiting and security checks.
    
    Args:
        credentials: User login credentials
        
    Returns:
        Authenticated user object
        
    Raises:
        AuthenticationError: If credentials are invalid
    """
    pass
```

## That's It!

Keep it simple. Focus on readability and consistency. AI can infer the rest from the existing codebase. 