# Aura Journal - Backend Services

This project contains the backend services for the Aura Journal application, built with FastAPI and a microservices architecture.

## Architecture

The backend consists of several services:

- **Entry Ingestor**: Handles journal entry creation and storage (PostgreSQL + MongoDB for insights)
- **NLP Agent**: Provides text analysis using Google Cloud Natural Language API
- **Shared**: Common utilities, schemas, and database management

## Services Overview

### Entry Ingestor Service
- **Port**: 8000
- **Technology**: FastAPI, SQLAlchemy, PostgreSQL, MongoDB
- **Purpose**: Creates journal entries, coordinates with NLP service for analysis, stores insights

### NLP Agent Service  
- **Port**: 8001
- **Technology**: FastAPI, Google Cloud Language API
- **Purpose**: Provides sentiment analysis and topic extraction for journal entries

## Development Setup

### Prerequisites
- Python 3.11+
- [uv](https://github.com/astral-sh/uv) package manager
- Docker and Docker Compose
- PostgreSQL and MongoDB (via Docker)

### Installation

1. **Install dependencies for each service:**
   ```bash
   # Entry Ingestor
   cd services/entry_ingestor
   uv sync
   
   # NLP Agent  
   cd ../nlp_agent
   uv sync
   ```

2. **Environment Setup:**
   Create a `.env` file in the backend root with:
   ```bash
   # Database Configuration
   POSTGRES_USER=your_user
   POSTGRES_PASSWORD=your_password
   POSTGRES_DB=aura_journal
   POSTGRES_HOST=localhost
   POSTGRES_PORT=5432
   
   # MongoDB Configuration
   MONGO_URL=mongodb://localhost:27017
   MONGO_DB_NAME=aura_insights
   
   # NLP Service Configuration
   NLP_SERVICE_URL=http://localhost:8001/analyze
   
   # Google Cloud Configuration
   GCP_KEYFILE_PATH=/path/to/your/gcp-key.json
   ```

## Running Tests

### Entry Ingestor Tests
```bash
cd backend
./services/entry_ingestor/.venv/Scripts/Activate.ps1  # Windows
# source ./services/entry_ingestor/.venv/bin/activate  # Linux/Mac
python -m pytest services/entry_ingestor/tests/ -v
```

### NLP Agent Tests
```bash
cd backend
./services/nlp_agent/.venv/Scripts/Activate.ps1  # Windows
# source ./services/nlp_agent/.venv/bin/activate  # Linux/Mac
python -m pytest services/nlp_agent/tests/ -v
```

## Running Services

### Using Docker Compose (Recommended)
```bash
docker-compose up --build
```

This starts:
- PostgreSQL database (port 5432)
- MongoDB database (port 27017)
- Entry Ingestor API (port 8000)
- NLP Agent API (port 8001)

### Manual Development Setup
```bash
# Terminal 1: Start Entry Ingestor
cd services/entry_ingestor
./.venv/Scripts/Activate.ps1  # Windows
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2: Start NLP Agent
cd services/nlp_agent
./.venv/Scripts/Activate.ps1  # Windows  
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

## API Endpoints

### Entry Ingestor Service (localhost:8000)
- `POST /entries` - Create a new journal entry
- `GET /health` - Health check

### NLP Agent Service (localhost:8001)
- `POST /analyze` - Analyze text for sentiment and topics
- `GET /health` - Health check

## Technology Stack

- **Framework**: FastAPI
- **Package Management**: uv
- **Databases**: PostgreSQL (entries), MongoDB (insights)
- **External APIs**: Google Cloud Natural Language API
- **Containerization**: Docker & Docker Compose
- **Testing**: pytest
- **Code Quality**: ruff (linting & formatting)

## Key Features

- **Microservices Architecture**: Separate, containerized services
- **Database Integration**: PostgreSQL for structured data, MongoDB for analytics
- **Error Handling**: Comprehensive error handling and logging
- **Testing**: Full test coverage with mocking for external dependencies
- **Development Tools**: Hot reload, dependency injection, type hints
- **Cloud Integration**: Google Cloud Natural Language API for text analysis

## Project Structure
```
backend/
├── services/
│   ├── entry_ingestor/
│   │   ├── app/
│   │   ├── tests/
│   │   ├── Dockerfile
│   │   └── pyproject.toml
│   └── nlp_agent/
│       ├── app/
│       ├── tests/
│       ├── Dockerfile
│       └── pyproject.toml
├── shared/
├── docker-compose.yml
└── README.md
```

## Next Steps

1. **Environment Variables**: Configure your `.env` file with proper credentials
2. **GCP Setup**: Set up Google Cloud credentials for NLP functionality
3. **Database Migrations**: Run initial database setup
4. **Integration Testing**: Test the complete flow between services
5. **Production Deployment**: Configure for production environment

A restructured, testable, and maintainable backend architecture for the Aura Journal application.

## 🏗️ Architecture Overview

This backend follows a clean architecture pattern with:

### **Shared Components**
- **`shared/`**: Common schemas, database utilities, and configuration
- **`tests/`**: Global test fixtures and shared tests

### **Microservices**
- **`services/entry_ingestor/`**: Handles journal entry creation and storage
- **`services/nlp_agent/`**: Provides text analysis using Google Cloud NLP

### **Key Architectural Benefits**
- ✅ **Dependency Injection**: Easy testing and swappable components
- ✅ **Protocol-Based Design**: Type-safe interfaces with proper abstractions
- ✅ **Shared Schemas**: Consistent data models across services
- ✅ **Comprehensive Testing**: Unit, integration, and mocked tests
- ✅ **Clean Separation**: Business logic separated from FastAPI routes

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL (for journal entries)
- MongoDB (for insights)
- Google Cloud credentials (for NLP analysis)

### Installation

1. **Clone and navigate to backend:**
```bash
cd backend/
```

2. **Install dependencies:**
```bash
# Using uv (recommended)
uv sync --extra dev --extra gcp

# Or using pip
pip install -e ".[dev,gcp]"
```

3. **Set up environment variables:**
```bash
cp .env.example .env
# Edit .env with your database URLs and GCP credentials
```

### Environment Variables
```bash
# Database connections
DATABASE_URL=postgresql://user:password@localhost:5432/aura_journal
MONGODB_URL=mongodb://localhost:27017

# Service URLs
NLP_AGENT_URL=http://localhost:8001/analyze

# Google Cloud Platform
GOOGLE_APPLICATION_CREDENTIALS=/path/to/gcp-key.json
GCP_KEYFILE_PATH=/path/to/gcp-key.json

# Development
DEBUG=true
LOG_LEVEL=INFO
```

## 🧪 Running Tests

### Run All Tests
```bash
python scripts/run_tests.py
```

### Run Specific Test Types
```bash
# Unit tests only
python scripts/run_tests.py --unit

# Integration tests only
python scripts/run_tests.py --integration

# Specific service tests
python scripts/run_tests.py --service entry-ingestor
python scripts/run_tests.py --service nlp-agent

# With coverage report
python scripts/run_tests.py --coverage
```

### Manual Testing
```bash
# Run tests directly with pytest
pytest tests/                          # Shared tests
pytest services/entry_ingestor/tests/  # Entry ingestor tests
pytest services/nlp_agent/tests/       # NLP agent tests

# With verbose output
pytest -v

# With coverage
pytest --cov=. --cov-report=html
```

## 🏃‍♂️ Running Services

### Individual Services (Development)
```bash
# Entry Ingestor (port 8000)
python scripts/run_service.py entry-ingestor

# NLP Agent (port 8001)
python scripts/run_service.py nlp-agent
```

### Using Docker Compose (Production-like)
```bash
# From the parent directory
cd ../
docker-compose -f backend/docker-compose.yml up
```

### Manual Service Startup
```bash
# Entry Ingestor
PYTHONPATH=. uvicorn services.entry_ingestor.app.main:app --reload --port 8000

# NLP Agent
PYTHONPATH=. uvicorn services.nlp_agent.app.main:app --reload --port 8001
```

## 📝 API Documentation

### Entry Ingestor Service (Port 8000)

#### Create Journal Entry
```bash
POST /entries
Content-Type: application/json

{
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "content": "Today was a great day at work!"
}
```

**Response:**
```json
{
  "entry_id": "456e7890-e89b-12d3-a456-426614174001",
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "timestamp": "2025-01-25T10:30:00Z",
  "content": "Today was a great day at work!",
  "analysis": {
    "sentiment": {
      "label": "POSITIVE",
      "score": 0.8
    },
    "topics": ["work", "productivity"]
  }
}
```

#### Health Check
```bash
GET /health
```

### NLP Agent Service (Port 8001)

#### Analyze Text
```bash
POST /analyze
Content-Type: application/json

{
  "text": "I had an amazing day at the office!"
}
```

**Response:**
```json
{
  "sentiment": {
    "label": "POSITIVE", 
    "score": 0.85
  },
  "topics": ["work", "office", "productivity"]
}
```

#### Health Check
```bash
GET /health
```

## 🛠️ Development Workflow

### Code Quality
```bash
# Lint and format code
ruff check --fix .
ruff format .

# Type checking
mypy shared/ services/
```

### Testing Strategy

1. **Unit Tests**: Test individual components in isolation
   - Services with mocked dependencies
   - Shared utilities and schemas
   - Individual functions and classes

2. **Integration Tests**: Test API endpoints with mocked external services
   - FastAPI endpoint behavior
   - Request/response validation
   - Error handling

3. **Contract Tests**: Ensure service communication works
   - Schema compatibility between services
   - API contract validation

### Adding New Features

1. **Shared Components**: Add to `shared/` if used by multiple services
2. **Service-Specific**: Add to appropriate service directory
3. **Always Add Tests**: Every new feature should have corresponding tests
4. **Follow Patterns**: Use dependency injection and protocol-based design

## 📁 Project Structure

```
backend/
├── shared/                          # Shared utilities and schemas
│   ├── __init__.py
│   ├── config.py                    # Configuration classes
│   ├── database.py                  # Database connection management
│   └── schemas.py                   # Pydantic models
├── services/
│   ├── entry_ingestor/              # Journal entry service
│   │   ├── app/
│   │   │   ├── __init__.py
│   │   │   ├── main.py              # FastAPI app
│   │   │   ├── models.py            # SQLAlchemy models
│   │   │   ├── services.py          # Business logic
│   │   │   └── dependencies.py     # Dependency injection
│   │   └── tests/
│   │       ├── test_main.py         # API endpoint tests
│   │       └── test_services.py     # Service layer tests
│   └── nlp_agent/                   # Text analysis service
│       ├── app/
│       │   ├── __init__.py
│       │   ├── main.py              # FastAPI app
│       │   └── gcp_client.py        # Google Cloud client
│       └── tests/
│           └── test_main.py         # API endpoint tests
├── tests/
│   ├── conftest.py                  # Global test fixtures
│   └── test_shared.py               # Shared component tests
├── scripts/
│   ├── run_tests.py                 # Test runner script
│   └── run_service.py               # Service runner script
├── pyproject.toml                   # Project dependencies and config
├── docker-compose.yml               # Container orchestration
└── README.md                        # This file
```

## 🔧 Troubleshooting

### Common Issues

1. **Import Errors**
   - Ensure `PYTHONPATH` includes the backend directory
   - Check that `__init__.py` files exist in all packages

2. **Database Connection Issues**
   - Verify `DATABASE_URL` and `MONGODB_URL` in `.env`
   - Ensure databases are running and accessible

3. **Google Cloud Authentication**
   - Set `GOOGLE_APPLICATION_CREDENTIALS` environment variable
   - Verify GCP key file has proper permissions

4. **Test Failures**
   - Check if external services are properly mocked
   - Verify test isolation (no shared state between tests)

### Debug Mode
```bash
# Run with debug logging
LOG_LEVEL=DEBUG python scripts/run_service.py entry-ingestor
```

## 🚢 Deployment

### Docker Build
```bash
# Build individual service images
docker build -t aura-entry-ingestor services/entry_ingestor/
docker build -t aura-nlp-agent services/nlp_agent/

# Run with docker-compose
docker-compose up --build
```

### Production Considerations
- Use environment-specific configuration
- Set up proper logging and monitoring
- Configure database connection pooling
- Set up health checks and readiness probes
- Use secrets management for sensitive data

## 🤝 Contributing

1. Follow the existing code patterns and architecture
2. Write tests for all new functionality
3. Ensure code passes linting and type checking
4. Update documentation for significant changes
5. Use dependency injection for testability

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://pydantic-docs.helpmanual.io/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [pytest Documentation](https://docs.pytest.org/)
- [Google Cloud Natural Language API](https://cloud.google.com/natural-language/docs)
