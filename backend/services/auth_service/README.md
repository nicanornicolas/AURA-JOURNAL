# Authentication Service

The Authentication Service provides secure user authentication and authorization for the AURA Journal application using JWT tokens and bcrypt password hashing.

## Features

- **User Registration**: Secure user account creation with email validation and password strength requirements
- **User Authentication**: Login with email and password credentials
- **JWT Token Management**: Access and refresh token generation and validation
- **Password Security**: bcrypt hashing with configurable rounds
- **Session Management**: Secure session tracking and invalidation
- **Input Validation**: Comprehensive request validation using Pydantic models

## Requirements Implemented

This service implements the following requirements from the production readiness specification:

- **1.1**: User registration functionality with email and password
- **1.2**: Email format and password strength validation
- **1.3**: JWT token generation for authenticated requests
- **1.4**: Token validation and user-specific data authorization
- **1.5**: Session management and token refresh functionality
- **1.6**: Session invalidation for logout

## API Endpoints

### Authentication Endpoints

- `POST /auth/register` - Register new user account
- `POST /auth/login` - Authenticate user and return tokens
- `POST /auth/refresh` - Refresh access token using refresh token
- `POST /auth/logout` - Logout user and invalidate session
- `GET /auth/profile` - Get current user profile

### Health Check

- `GET /health` - Service health check

## Installation

1. Install dependencies with uv:
```bash
cd backend
uv sync
```

2. Set environment variables:
```bash
export AUTH_JWT_SECRET_KEY="your-secret-key"
export AUTH_DATABASE_URL="postgresql://user:pass@localhost:5432/aura_journal"
```

3. Run the service:
```bash
cd services/auth_service
uv run python main.py
```

## Configuration

The service can be configured using environment variables with the `AUTH_` prefix:

- `AUTH_JWT_SECRET_KEY`: Secret key for JWT token signing
- `AUTH_ACCESS_TOKEN_EXPIRE_MINUTES`: Access token expiration (default: 30)
- `AUTH_REFRESH_TOKEN_EXPIRE_DAYS`: Refresh token expiration (default: 7)
- `AUTH_DATABASE_URL`: PostgreSQL database connection string
- `AUTH_BCRYPT_ROUNDS`: bcrypt hashing rounds (default: 12)
- `AUTH_PORT`: Service port (default: 8001)

## Database Schema

The service uses PostgreSQL with the following tables:

### users
- `user_id` (UUID, Primary Key)
- `email` (String, Unique)
- `password_hash` (String)
- `first_name` (String, Optional)
- `last_name` (String, Optional)
- `is_active` (Boolean)
- `is_verified` (Boolean)
- `created_at` (DateTime)
- `updated_at` (DateTime)
- `last_login` (DateTime, Optional)

### user_sessions
- `session_id` (UUID, Primary Key)
- `user_id` (UUID, Foreign Key)
- `refresh_token_hash` (String)
- `expires_at` (DateTime)
- `created_at` (DateTime)
- `is_active` (Boolean)

## Security Features

- **Password Hashing**: bcrypt with configurable rounds
- **JWT Tokens**: Signed with HS256 algorithm
- **Session Management**: Refresh token rotation and validation
- **Input Validation**: Comprehensive request validation
- **Password Requirements**: Minimum 8 characters with uppercase, lowercase, digit, and special character

## Testing

Run tests with pytest using uv:

```bash
cd backend
uv run pytest services/auth_service/tests/
```

## Docker

Build and run with Docker:

```bash
docker build -t auth-service .
docker run -p 8001:8001 auth-service
```

## Usage Examples

### Register User
```bash
curl -X POST "http://localhost:8001/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!",
    "first_name": "John",
    "last_name": "Doe"
  }'
```

### Login
```bash
curl -X POST "http://localhost:8001/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!"
  }'
```

### Get Profile
```bash
curl -X GET "http://localhost:8001/auth/profile" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```