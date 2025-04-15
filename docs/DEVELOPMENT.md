# Development Guide

## Setup

1. **Prerequisites**
   - Python 3.11+
   - Docker and Docker Compose
   - Git

2. **Environment Setup**
   ```bash
   # Clone the repository
   git clone <repository-url>
   cd autoscheduler

   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

   # Install dependencies
   pip install -r requirements.txt

   # Copy environment file
   cp .env.example .env
   ```

3. **Docker Setup**
   ```bash
   # Start services
   docker-compose up -d

   # Check services
   docker-compose ps
   ```

## Development

1. **Running the Application**
   ```bash
   # Start the development server
   uvicorn app.main:app --reload
   ```

2. **Running Tests**
   ```bash
   # Run all tests
   pytest

   # Run with coverage
   pytest --cov=app

   # Run specific test
   pytest app/tests/test_basic.py
   ```

3. **Database Migrations**
   ```bash
   # Create new migration
   alembic revision --autogenerate -m "description"

   # Apply migrations
   alembic upgrade head
   ```

## Project Structure

```
app/
├── core/               # Core functionality
│   ├── config.py      # Configuration
│   ├── security.py    # Security utilities
│   └── ...
├── api/               # API endpoints
│   ├── v1/           # API version 1
│   └── ...
├── models/            # Database models
├── schemas/           # Pydantic schemas
├── services/          # Business logic
└── tests/             # Tests
```

## API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Development Tools

1. **Database**
   - PgAdmin: http://localhost:5050
   - Credentials:
     - Email: admin@admin.com
     - Password: admin

2. **Redis**
   - Port: 6379
   - No authentication by default

## Testing

1. **Unit Tests**
   - Location: `app/tests/`
   - Run: `pytest`

2. **Integration Tests**
   - Location: `app/tests/integration/`
   - Run: `pytest app/tests/integration/`

3. **Test Coverage**
   - Run: `pytest --cov=app`
   - Report: `coverage.xml`

## Deployment

1. **Production**
   ```bash
   # Build Docker image
   docker-compose -f docker-compose.prod.yml build

   # Start services
   docker-compose -f docker-compose.prod.yml up -d
   ```

2. **Staging**
   ```bash
   # Build Docker image
   docker-compose -f docker-compose.staging.yml build

   # Start services
   docker-compose -f docker-compose.staging.yml up -d
   ```

## Troubleshooting

1. **Database Issues**
   - Check PostgreSQL logs: `docker-compose logs db`
   - Reset database: `docker-compose down -v && docker-compose up -d`

2. **Redis Issues**
   - Check Redis logs: `docker-compose logs redis`
   - Clear cache: `docker-compose exec redis redis-cli FLUSHALL`

3. **Application Issues**
   - Check application logs: `docker-compose logs app`
   - Restart application: `docker-compose restart app` 