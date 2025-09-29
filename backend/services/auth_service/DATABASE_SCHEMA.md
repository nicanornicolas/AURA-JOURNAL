# Database Schema Documentation

## Overview

This document describes the database schema implementation for the authentication service, including SQLAlchemy models, migrations, and repository patterns.

## Requirements Addressed

- **1.1**: User registration functionality with email and password
- **1.2**: Email format and password strength validation  
- **1.5**: Session tracking for token validation
- **1.6**: Session invalidation for logout

## Database Models

### Users Table

The `users` table stores user account information with the following schema:

```sql
CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    is_active BOOLEAN DEFAULT true NOT NULL,
    is_verified BOOLEAN DEFAULT false NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    last_login TIMESTAMP WITH TIME ZONE
);
```

**Indexes:**
- `idx_users_email` on `email` (unique constraint)
- `idx_users_active` on `is_active`
- `idx_users_created_at` on `created_at`

### User Sessions Table

The `user_sessions` table manages JWT refresh tokens and session tracking:

```sql
CREATE TABLE user_sessions (
    session_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(user_id) ON DELETE CASCADE NOT NULL,
    refresh_token_hash VARCHAR(255) NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    is_active BOOLEAN DEFAULT true NOT NULL
);
```

**Indexes:**
- `idx_user_sessions_user_id` on `user_id`
- `idx_user_sessions_active` on `is_active`
- `idx_user_sessions_expires_at` on `expires_at`
- `idx_user_sessions_user_active` on `user_id, is_active` (composite)

## SQLAlchemy Models

### User Model

```python
class User(Base):
    __tablename__ = "users"
    
    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Relationship to user sessions
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
```

### UserSession Model

```python
class UserSession(Base):
    __tablename__ = "user_sessions"
    
    session_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    refresh_token_hash = Column(String(255), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationship to user
    user = relationship("User", back_populates="sessions")
```

## Database Migrations

### Migration Management

The service uses Alembic for database migrations. Key files:

- `migrations/alembic.ini` - Alembic configuration
- `migrations/env.py` - Migration environment setup
- `migrations/versions/001_initial_user_auth_tables.py` - Initial schema migration
- `migrate.py` - Migration management script

### Running Migrations

```bash
# Upgrade to latest migration
python migrate.py upgrade

# Upgrade to specific revision
python migrate.py upgrade 001

# Downgrade to specific revision
python migrate.py downgrade 001

# Show current revision
python migrate.py current

# Show migration history
python migrate.py history

# Create new migration
python migrate.py create "description of changes"
```

## Repository Pattern Implementation

### Base Repository

The `BaseRepository` class provides common CRUD operations:

- `get_by_id(entity_id)` - Get entity by UUID
- `get_all(skip, limit, filters)` - Get entities with pagination and filtering
- `create(obj_in)` - Create new entity
- `update(entity_id, obj_in)` - Update existing entity
- `delete(entity_id)` - Delete entity
- `count(filters)` - Count entities with optional filtering
- `exists(entity_id)` - Check if entity exists

### User Repository

The `UserRepository` extends `BaseRepository` with user-specific methods:

**Core CRUD Operations:**
- `create_user(user_data, password_hash)` - Create user with hashed password
- `get_by_email(email)` - Find user by email address
- `email_exists(email)` - Check if email is already registered

**User Management:**
- `get_active_users(skip, limit)` - Get all active users
- `get_verified_users(skip, limit)` - Get all verified users
- `search_users(search_term, skip, limit)` - Search users by name/email
- `activate_user(user_id)` - Activate user account
- `deactivate_user(user_id)` - Deactivate user account
- `verify_user(user_id)` - Mark user as verified

**Authentication Support:**
- `update_last_login(user_id)` - Update last login timestamp
- `update_password(user_id, password_hash)` - Update user password

**Analytics:**
- `get_user_stats()` - Get user statistics
- `get_users_created_after(date, skip, limit)` - Get recent users

### Session Repository

The `SessionRepository` manages user sessions and JWT tokens:

**Session Management:**
- `create_session(user_id, refresh_token_hash, expires_at)` - Create new session
- `get_active_session(session_id)` - Get active session by ID
- `get_user_sessions(user_id, active_only)` - Get all sessions for user
- `update_refresh_token(session_id, token_hash, expires_at)` - Update session token

**Session Lifecycle:**
- `invalidate_session(session_id)` - Mark session as inactive
- `invalidate_user_sessions(user_id)` - Invalidate all user sessions
- `cleanup_expired_sessions()` - Clean up expired sessions

**Session Analytics:**
- `get_session_stats()` - Get session statistics
- `get_recent_sessions(hours, skip, limit)` - Get recent sessions
- `get_session_by_token_hash(token_hash)` - Find session by token hash

## Usage Examples

### Creating a User

```python
from repositories import UserRepository
from models import UserCreate

# Initialize repository
user_repo = UserRepository(db_session)

# Create user data
user_data = UserCreate(
    email="user@example.com",
    password="SecurePassword123!",
    first_name="John",
    last_name="Doe"
)

# Hash password (using auth handler)
password_hash = auth_handler.hash_password(user_data.password)

# Create user
user = user_repo.create_user(user_data, password_hash)
```

### Managing Sessions

```python
from repositories import SessionRepository
from datetime import datetime, timezone, timedelta

# Initialize repository
session_repo = SessionRepository(db_session)

# Create session
expires_at = datetime.now(timezone.utc) + timedelta(days=7)
session = session_repo.create_session(
    user_id=user.user_id,
    refresh_token_hash="hashed_token",
    expires_at=expires_at
)

# Get active session
active_session = session_repo.get_active_session(session.session_id)

# Invalidate session
session_repo.invalidate_session(session.session_id)
```

## Performance Considerations

### Indexes

The schema includes strategic indexes for common query patterns:

1. **Email lookups** - Unique index on `users.email`
2. **Active user queries** - Index on `users.is_active`
3. **Session lookups** - Composite index on `user_sessions.user_id, is_active`
4. **Session cleanup** - Index on `user_sessions.expires_at`

### Query Optimization

- Use `get_by_email()` instead of filtering manually
- Leverage composite indexes for user session queries
- Use pagination for large result sets
- Regular cleanup of expired sessions

## Security Features

### Password Security
- Passwords are hashed using bcrypt with configurable rounds
- Original passwords are never stored
- Password strength validation in Pydantic models

### Session Security
- Refresh tokens are hashed before storage
- Sessions have expiration timestamps
- Automatic cleanup of expired sessions
- Session invalidation on logout

### Data Integrity
- Foreign key constraints ensure referential integrity
- Cascade deletes remove sessions when users are deleted
- Unique constraints prevent duplicate emails
- Timezone-aware timestamps for accurate session management

## Testing

The implementation includes test utilities:

- `simple_test.py` - Basic model functionality test
- `test_repository_implementation.py` - Comprehensive repository tests

Run tests with:
```bash
python simple_test.py
```

## Migration from Existing Implementation

If migrating from an existing auth system:

1. Run the initial migration: `python migrate.py upgrade`
2. Update existing code to use repository pattern
3. Replace direct SQLAlchemy queries with repository methods
4. Update imports to use new repository classes

## Dependencies

Required packages:
- `sqlalchemy>=2.0.43` - ORM and database toolkit
- `alembic>=1.13.0` - Database migrations
- `psycopg2-binary>=2.9.10` - PostgreSQL adapter
- `pydantic[email]>=2.11.7` - Data validation

## Configuration

Database configuration is managed through environment variables:
- `DATABASE_URL` - PostgreSQL connection string
- `DATABASE_ECHO` - Enable SQL query logging (development only)

Example:
```bash
DATABASE_URL=postgresql://user:password@localhost:5432/aura_journal
DATABASE_ECHO=false
```