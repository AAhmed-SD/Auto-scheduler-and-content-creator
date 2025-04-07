# Auto Scheduler & Content Creator - Backend

This is the backend service for the Auto Scheduler & Content Creator application. It provides APIs for content generation, style analysis, and scheduling across multiple social media platforms.

## Features

- User authentication and authorization
- Content style analysis
- AI-powered content generation
- Multi-platform content scheduling
- Secure API endpoints
- Database integration

## Tech Stack

- FastAPI
- SQLAlchemy
- PostgreSQL
- JWT Authentication
- OpenAI API
- Pydantic

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the backend directory with the following variables:
```env
SECRET_KEY=your-secret-key
POSTGRES_SERVER=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=autoscheduler
OPENAI_API_KEY=your-openai-api-key
```

4. Initialize the database:
```bash
alembic upgrade head
```

5. Run the development server:
```bash
uvicorn app.main:app --reload
```

## API Documentation

Once the server is running, you can access the API documentation at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Authentication

1. Register a new user:
```bash
curl -X POST "http://localhost:8000/api/auth/register" \
     -H "Content-Type: application/json" \
     -d '{"email": "user@example.com", "password": "password123", "full_name": "John Doe"}'
```

2. Login to get access token:
```bash
curl -X POST "http://localhost:8000/api/auth/token" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=user@example.com&password=password123"
```

### Content Generation

1. Analyze content style:
```bash
curl -X POST "http://localhost:8000/api/content/analyze" \
     -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"reference_url": "https://example.com/video", "content_type": "video", "style_elements": {}}'
```

2. Generate content:
```bash
curl -X POST "http://localhost:8000/api/content/generate" \
     -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"template_id": "template_123", "content_type": "video", "quote": "Your quote here", "style_adjustments": {}}'
```

3. Schedule content:
```bash
curl -X POST "http://localhost:8000/api/content/schedule" \
     -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"content_id": "content_123", "platforms": ["instagram", "tiktok"], "schedule": {}, "captions": {}, "hashtags": {}}'
```

## Development

### Running Tests

```bash
pytest
```

### Database Migrations

Create a new migration:
```bash
alembic revision --autogenerate -m "description of changes"
```

Apply migrations:
```bash
alembic upgrade head
```

## License

MIT 