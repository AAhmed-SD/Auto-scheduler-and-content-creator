# Use Python 3.11 as base image
FROM python:3.11

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install packages one by one
RUN pip install --no-cache-dir fastapi==0.109.2
RUN pip install --no-cache-dir uvicorn==0.27.1
RUN pip install --no-cache-dir sqlalchemy==2.0.27
RUN pip install --no-cache-dir psycopg2-binary==2.9.9
RUN pip install --no-cache-dir "python-jose[cryptography]==3.3.0"
RUN pip install --no-cache-dir "passlib[bcrypt]==1.7.4"
RUN pip install --no-cache-dir python-multipart==0.0.9
RUN pip install --no-cache-dir redis==5.0.1
RUN pip install --no-cache-dir python-dotenv==1.0.1
RUN pip install --no-cache-dir pydantic==2.6.1
RUN pip install --no-cache-dir pydantic-settings==2.1.0
RUN pip install --no-cache-dir httpx==0.26.0
RUN pip install --no-cache-dir aioredis==2.0.1

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p uploads

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"] 