# Auto-scheduler and Content Creator

An AI-powered platform for intelligent content scheduling and management, built with FastAPI and React.

## Features

- 🤖 AI-powered content generation and scheduling
- 👥 Multi-user and team collaboration
- 🔄 Automated content workflow management
- ✅ Client approval system
- 📊 Analytics and performance tracking
- 🔒 Role-based access control
- 🚀 Auto-scaling infrastructure

## Tech Stack

### Backend
- FastAPI
- PostgreSQL
- Redis
- Celery
- SQLAlchemy
- Alembic
- OpenAI
- AWS Services

### Infrastructure
- Docker
- Terraform
- AWS (ECS, RDS, ElastiCache)
- Prometheus & Grafana

## Local Development Setup

### Prerequisites
- Python 3.11+
- Docker and Docker Compose
- Poetry (Python package manager)
- Node.js 18+ (for frontend)

### Environment Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/auto-scheduler.git
cd auto-scheduler
```

2. Copy the example environment file:
```bash
cp .env.example .env
```

3. Update the `.env` file with your configuration values.

### Using Docker Compose

1. Start all services:
```bash
docker-compose up -d
```

2. Access the services:
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- pgAdmin: http://localhost:5050
- Grafana: http://localhost:3000
- Prometheus: http://localhost:9090

### Manual Setup

1. Install dependencies:
```bash
poetry install
```

2. Set up the database:
```bash
poetry run alembic upgrade head
```

3. Start the development server:
```bash
poetry run uvicorn app.main:app --reload
```

## Database Migrations

Create a new migration:
```bash
poetry run alembic revision --autogenerate -m "description"
```

Apply migrations:
```bash
poetry run alembic upgrade head
```

## Testing

Run tests with coverage:
```bash
poetry run pytest
```

## Code Quality

Format code:
```bash
poetry run black .
poetry run isort .
```

Run linting:
```bash
poetry run flake8
poetry run mypy .
```

## Deployment

### AWS Deployment

1. Configure AWS credentials:
```bash
aws configure
```

2. Initialize Terraform:
```bash
cd infrastructure/terraform
terraform init
```

3. Apply infrastructure changes:
```bash
terraform apply
```

### CI/CD Pipeline

The project uses GitHub Actions for:
- Running tests
- Code quality checks
- Security scanning
- Automated deployments

## API Documentation

Detailed API documentation is available at:
- Swagger UI: `/docs`
- ReDoc: `/redoc`

## Architecture

### System Components
- FastAPI application server
- PostgreSQL database with read replicas
- Redis for caching and session management
- Celery for background tasks
- ECS for container orchestration
- CloudWatch for monitoring
- S3 for file storage

### Security Features
- JWT authentication
- Role-based access control
- Rate limiting
- Input validation
- SQL injection protection
- XSS prevention

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please:
1. Check the documentation
2. Search existing issues
3. Create a new issue if needed

## Roadmap

See our [project board](https://github.com/yourusername/auto-scheduler/projects) for planned features and improvements.
