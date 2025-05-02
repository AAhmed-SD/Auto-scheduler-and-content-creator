#!/bin/bash

# Exit on error
set -e

echo "Setting up development environment..."

# Check if Poetry is installed
if ! command -v poetry &> /dev/null; then
    echo "Installing Poetry..."
    curl -sSL https://install.python-poetry.org | python3 -
fi

# Install Python dependencies
echo "Installing Python dependencies..."
poetry install

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cp .env.example .env
fi

# Set up pre-commit hooks
echo "Setting up pre-commit hooks..."
poetry run pre-commit install

# Initialize database
echo "Setting up database..."
poetry run alembic upgrade head

echo "Setup complete! You can now start the development server with:"
echo "poetry run uvicorn app.main:app --reload" 