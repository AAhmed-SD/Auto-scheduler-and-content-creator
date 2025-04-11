# Auto-Scheduler & Content Creator Backend

This is the backend service for the Auto-Scheduler & Content Creator platform, built with FastAPI.

## Features

- RESTful API with FastAPI
- PostgreSQL database with SQLAlchemy ORM
- JWT authentication
- Redis caching
- Social media integration
- Content management
- Project management
- Team collaboration
- Analytics and reporting

## Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Node.js 18+ (for Supabase CLI)

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

3. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. Initialize the database:
   ```bash
   alembic upgrade head
   ```

## Development

1. Start the development server:
   ```bash
   uvicorn app.main:app --reload
   ```

2. Access the API documentation:
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## Testing

Run tests with pytest:
```bash
pytest
```

## Project Structure

```
backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/
│   │       └── api.py
│   ├── core/
│   │   └── config.py
│   ├── db/
│   │   └── session.py
│   ├── models/
│   ├── schemas/
│   ├── services/
│   └── utils/
├── tests/
├── alembic/
├── requirements.txt
└── README.md
```

## API Documentation

The API documentation is automatically generated and available at:
- Swagger UI: `/docs`
- ReDoc: `/redoc`

## Contributing

1. Create a new branch for your feature
2. Make your changes
3. Run tests
4. Submit a pull request

## License

This project is licensed under the MIT License. 