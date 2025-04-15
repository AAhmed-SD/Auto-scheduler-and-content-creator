# Quick Start Guide

## Prerequisites
- Install Docker Desktop from https://www.docker.com/products/docker-desktop
- Clone this repository

## Start Development Server
1. Open terminal in project directory
2. Run:
```bash
docker-compose up
```
3. Wait for containers to start
4. Access API at http://localhost:8000
5. Access docs at http://localhost:8000/docs

## Development Workflow
- Make changes to code
- Changes reflect automatically
- View logs in terminal
- Press Ctrl+C to stop

## Common Commands
```bash
# Start services
docker-compose up

# Start in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild containers
docker-compose up --build

# View container status
docker-compose ps
```

## Troubleshooting
1. If containers won't start:
   ```bash
   docker-compose down
   docker-compose up --build
   ```

2. If changes don't reflect:
   ```bash
   docker-compose restart api
   ```

3. To clear all data:
   ```bash
   docker-compose down -v
   ```

## Environment Variables
Create a `.env` file in project root:
```env
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
```

## Accessing Services
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Admin: http://localhost:8000/admin 