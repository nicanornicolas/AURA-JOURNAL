# NLP Agent Service

The NLP Agent service provides natural language processing capabilities for the Aura Journal application, specifically handling text analysis using Google Cloud Natural Language API.

## Overview

This service analyzes journal entries to extract:

- Sentiment analysis (positive/negative/mixed emotions)
- Topic extraction and entity recognition
- Text classification and insights

## Architecture

The service follows a clean architecture pattern with:

- **FastAPI** for the web framework
- **Google Cloud Language API** for NLP processing
- **Pydantic** for data validation and serialization
- **Loguru** for structured logging

## API Endpoints

### POST /analyze

Analyzes text content and returns sentiment and topic analysis.

**Request:**

```json
{
  "text": "Today was a great day at work! I accomplished all my tasks and felt very productive."
}
```

**Response:**

```json
{
  "sentiment": {
    "score": 0.8,
    "magnitude": 1.2
  },
  "topics": [
    {
      "name": "work",
      "type": "OTHER",
      "salience": 0.7
    },
    {
      "name": "productivity",
      "type": "OTHER",
      "salience": 0.6
    }
  ],
  "entities": [
    {
      "name": "work",
      "type": "OTHER",
      "salience": 0.7,
      "mentions": 1
    }
  ]
}
```

### GET /health

Health check endpoint.

**Response:**

```json
{
  "service": "nlp-agent",
  "version": "1.0.0",
  "status": "healthy"
}
```

## Development Setup

### Prerequisites

- Python 3.11+
- Google Cloud credentials with Natural Language API enabled
- uv package manager

### Installation

1. **Install dependencies:**

```bash
cd backend/services/nlp_agent
uv sync
```

2. **Environment Setup:**
   Create a `.env` file in the service directory:

```bash
# Google Cloud Configuration
GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/gcp-key.json
GCP_KEYFILE_PATH=/path/to/your/gcp-key.json

# Service Configuration
DEBUG=true
LOG_LEVEL=INFO
```

### Running the Service

**Development mode:**

```bash
cd backend/services/nlp_agent
uv run uvicorn app.main:app --reload --port 8001
```

**Using Docker:**

```bash
# From the backend root directory
docker-compose up nlp_agent_api
```

## Testing

### Run Tests

```bash
cd backend/services/nlp_agent

# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=. --cov-report=html

# Run specific test
uv run pytest tests/test_main.py -v
```

### Test Structure

- **Unit tests** for individual components
- **Integration tests** for API endpoints
- **Mocked tests** for external GCP API calls

## Project Structure

```
nlp_agent/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI application
│   ├── config.py        # Configuration settings
│   └── gcp_client.py    # Google Cloud NLP client
├── tests/
│   ├── __init__.py
│   └── test_main.py     # API endpoint tests
├── Dockerfile           # Container definition
├── pyproject.toml       # Dependencies and configuration
└── README.md           # This file
```

## Configuration

### Environment Variables

| Variable                         | Description                                 | Required |
| -------------------------------- | ------------------------------------------- | -------- |
| `GOOGLE_APPLICATION_CREDENTIALS` | Path to GCP service account key             | Yes      |
| `GCP_KEYFILE_PATH`               | Alternative path to GCP key                 | No       |
| `DEBUG`                          | Enable debug mode                           | No       |
| `LOG_LEVEL`                      | Logging level (DEBUG, INFO, WARNING, ERROR) | No       |

### Google Cloud Setup

1. Create a Google Cloud Project
2. Enable the Natural Language API
3. Create a service account with appropriate permissions
4. Download the service account key JSON file
5. Set the `GOOGLE_APPLICATION_CREDENTIALS` environment variable

## Error Handling

The service includes comprehensive error handling for:

- Invalid request payloads
- GCP API failures
- Network timeouts
- Authentication issues

All errors return appropriate HTTP status codes with descriptive error messages.

## Dependencies

### Core Dependencies

- `fastapi`: Web framework
- `google-cloud-language`: Google NLP API client
- `pydantic`: Data validation
- `uvicorn`: ASGI server
- `loguru`: Logging

### Development Dependencies

- `pytest`: Testing framework
- `httpx`: HTTP client for testing

## Docker

The service includes a multi-stage Dockerfile for optimized production builds:

```dockerfile
# Build stage
FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim as builder
# ... build dependencies

# Final stage
FROM base as final
# ... runtime image
```

## Monitoring

The service provides:

- Health check endpoints
- Structured logging with request IDs
- Performance metrics via FastAPI middleware
- Error tracking and reporting

## Security

- Input validation using Pydantic models
- Secure credential handling
- No sensitive data logging
- HTTPS enforcement in production
