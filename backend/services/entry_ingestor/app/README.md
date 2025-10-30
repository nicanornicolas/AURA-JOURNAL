# Entry Ingestor Service

The Entry Ingestor service handles the creation and management of journal entries in the Aura Journal application. It coordinates between PostgreSQL for structured data storage and MongoDB for analytical insights.

## Overview

This service provides:

- Journal entry creation and storage
- Integration with NLP analysis services
- Data persistence across PostgreSQL and MongoDB
- RESTful API for entry management

## Architecture

The service follows a clean architecture pattern with:

- **FastAPI** for the web framework
- **SQLAlchemy** for PostgreSQL ORM
- **MongoDB** for insight storage
- **Dependency injection** for testability
- **Protocol-based design** for component swappability

## API Endpoints

### POST /entries

Creates a new journal entry with optional NLP analysis.

**Request:**

```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "content": "Today was a productive day. I completed all my tasks and felt accomplished."
}
```

**Response:**

```json
{
  "entry_id": "550e8400-e29b-41d4-a716-446655440001",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-15T10:30:00Z",
  "content": "Today was a productive day. I completed all my tasks and felt accomplished.",
  "analysis": {
    "sentiment": {
      "score": 0.8,
      "magnitude": 1.2
    },
    "topics": [
      {
        "name": "productivity",
        "type": "OTHER",
        "salience": 0.8
      }
    ],
    "entities": []
  }
}
```

### GET /health

Health check endpoint.

**Response:**

```json
{
  "service": "entry-ingestor",
  "version": "1.0.0"
}
```

## Development Setup

### Prerequisites

- Python 3.11+
- PostgreSQL database
- MongoDB database
- uv package manager

### Installation

1. **Install dependencies:**

```bash
cd backend/services/entry_ingestor
uv sync
```

2. **Environment Setup:**
   Create a `.env` file in the service directory:

```bash
# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/aura_journal
MONGO_URL=mongodb://localhost:27017
MONGO_DB_NAME=aura_insights

# Service Configuration
NLP_AGENT_URL=http://localhost:8001/analyze
DEBUG=true
LOG_LEVEL=INFO
```

### Running the Service

**Development mode:**

```bash
cd backend/services/entry_ingestor
uv run uvicorn app.main:app --reload --port 8000
```

**Using Docker:**

```bash
# From the backend root directory
docker-compose up entry_ingestor_api
```

## Testing

### Run Tests

```bash
cd backend/services/entry_ingestor

# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=. --cov-report=html

# Run specific tests
uv run pytest tests/test_main.py -v
uv run pytest tests/test_services.py -v
```

### Test Structure

- **Unit tests** for service layer components
- **Integration tests** for API endpoints
- **Mocked tests** for external dependencies (NLP service, databases)

## Project Structure

```
entry_ingestor/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI application
│   ├── models.py        # SQLAlchemy models
│   ├── services.py      # Business logic
│   ├── dependencies.py  # Dependency injection
│   └── README.md       # This file
├── tests/
│   ├── __init__.py
│   ├── test_main.py     # API endpoint tests
│   └── test_services.py # Service layer tests
├── Dockerfile           # Container definition
├── pyproject.toml       # Dependencies and configuration
└── uv.lock             # Lock file
```

## Configuration

### Environment Variables

| Variable        | Description                  | Required                    |
| --------------- | ---------------------------- | --------------------------- |
| `DATABASE_URL`  | PostgreSQL connection string | Yes                         |
| `MONGO_URL`     | MongoDB connection string    | Yes                         |
| `MONGO_DB_NAME` | MongoDB database name        | No (default: aura_insights) |
| `NLP_AGENT_URL` | URL of the NLP agent service | Yes                         |
| `DEBUG`         | Enable debug mode            | No                          |
| `LOG_LEVEL`     | Logging level                | No                          |

### Database Setup

#### PostgreSQL

The service uses PostgreSQL to store structured journal entry data:

- **Table**: `journal_entries`
- **Fields**: `entry_id` (UUID), `user_id` (UUID), `timestamp`, `content`

#### MongoDB

The service uses MongoDB to store analytical insights:

- **Collection**: `insights`
- **Documents**: Entry analysis results with sentiment, topics, and entities

## Dependencies

### Core Dependencies

- `fastapi`: Web framework
- `sqlalchemy`: PostgreSQL ORM
- `psycopg2-binary`: PostgreSQL driver
- `pymongo`: MongoDB driver
- `httpx`: HTTP client for NLP service
- `pydantic`: Data validation
- `loguru`: Logging

### Development Dependencies

- `pytest`: Testing framework
- `pytest-asyncio`: Async testing support
- `httpx`: HTTP client for testing

## Business Logic

### Entry Creation Flow

1. **Validate Input**: Ensure user_id and content are provided
2. **Store Entry**: Save entry to PostgreSQL with generated UUID and timestamp
3. **Request Analysis**: Send content to NLP service for analysis
4. **Store Insights**: Save analysis results to MongoDB
5. **Return Response**: Include entry data and analysis in response

### Error Handling

The service handles various error scenarios:

- Database connection failures
- NLP service unavailability (graceful degradation)
- Invalid input data
- Network timeouts

## Docker

The service includes a multi-stage Dockerfile:

```dockerfile
# Build stage
FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim as builder
# ... build dependencies

# Final stage
FROM base as final
# ... runtime image with health checks
```

## Monitoring

The service provides:

- Health check endpoints
- Structured logging with request tracking
- Database connection monitoring
- External service dependency checks

## Security

- Input validation using Pydantic models
- SQL injection prevention via SQLAlchemy
- Secure database connection handling
- No sensitive data logging
