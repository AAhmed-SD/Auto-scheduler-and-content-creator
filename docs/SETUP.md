# Auto Scheduler & Content Creator - Setup Guide

## Development Environment Setup

### 1. Prerequisites
- Node.js 18+
- Python 3.9+
- Git
- Docker (optional)
- VS Code (recommended)

### 2. System Requirements
- 8GB RAM minimum
- 20GB free disk space
- Modern processor (4+ cores recommended)

## Initial Setup

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/auto-scheduler.git
cd auto-scheduler
```

### 2. Backend Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your credentials
```

### 3. Frontend Setup
```bash
# Install dependencies
npm install

# Set up environment variables
cp .env.local.example .env.local
# Edit .env.local with your credentials
```

## Infrastructure Setup

### 1. Oracle Cloud Setup
1. Create Oracle Cloud account
2. Set up free tier instance
3. Configure security rules
4. Set up SSH access

### 2. Cloudflare Setup
1. Create Cloudflare account
2. Add domain
3. Configure DNS
4. Set up SSL/TLS

### 3. Supabase Setup
1. Create Supabase project
2. Set up database
3. Configure authentication
4. Set up storage

## Development Workflow

### 1. Starting Development
```bash
# Start backend
cd backend
uvicorn app.main:app --reload

# Start frontend
cd frontend
npm run dev
```

### 2. Testing
```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

### 3. Building
```bash
# Backend
cd backend
python setup.py build

# Frontend
cd frontend
npm run build
```

## Deployment

### 1. Backend Deployment
```bash
# Build Docker image
docker build -t backend .

# Push to registry
docker push your-registry/backend

# Deploy to Oracle Cloud
kubectl apply -f k8s/backend.yaml
```

### 2. Frontend Deployment
```bash
# Build
npm run build

# Deploy to Cloudflare Pages
wrangler pages deploy ./dist
```

## Monitoring Setup

### 1. Sentry Setup
1. Create Sentry account
2. Create project
3. Configure DSN
4. Set up alerts

### 2. Prometheus Setup
1. Install Prometheus
2. Configure scraping
3. Set up Grafana
4. Create dashboards

## Security Setup

### 1. SSL/TLS
```bash
# Generate certificates
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365

# Configure Cloudflare
# Enable SSL/TLS
# Set to Full (strict)
```

### 2. Authentication
```bash
# Set up Supabase Auth
supabase auth setup

# Configure OAuth providers
# Set up MFA
```

## Backup Setup

### 1. Database Backup
```bash
# Set up automated backups
pg_dump -U postgres -d your_db > backup.sql

# Configure retention policy
# Set up monitoring
```

### 2. File Backup
```bash
# Set up Backblaze B2
b2 authorize-account
b2 sync ./data b2://your-bucket/data
```

## Troubleshooting

### 1. Common Issues
- Database connection issues
- API authentication problems
- File upload failures
- Performance issues

### 2. Solutions
- Check environment variables
- Verify network connectivity
- Monitor resource usage
- Check logs

## Maintenance

### 1. Regular Tasks
- Update dependencies
- Backup verification
- Security patches
- Performance optimization

### 2. Monitoring
- Check error rates
- Monitor resource usage
- Review security logs
- Check backup status 