# Auto Scheduler & Content Creator

An AI-powered platform for automated content creation, scheduling, and distribution across multiple platforms.

## Quick Start

### Prerequisites
- Node.js 18+
- Python 3.9+
- Git
- OpenAI API key
- Cloudflare account
- Oracle Cloud account

### Installation
1. Clone the repository:
```bash
git clone https://github.com/yourusername/auto-scheduler.git
cd auto-scheduler
```

2. Install dependencies:
```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt

# Frontend
cd ../frontend
npm install
```

3. Set up environment variables:
```bash
# Backend (.env)
OPENAI_API_KEY=your_key
DATABASE_URL=your_db_url
CLOUDFLARE_API_KEY=your_key

# Frontend (.env.local)
NEXT_PUBLIC_API_URL=http://localhost:8000
```

4. Start development servers:
```bash
# Backend
cd backend
uvicorn app.main:app --reload

# Frontend
cd frontend
npm run dev
```

## Project Structure
```
auto-scheduler/
├── backend/           # FastAPI backend
│   ├── app/
│   │   ├── api/      # API routes
│   │   ├── core/     # Core functionality
│   │   └── models/   # Data models
│   └── tests/        # Backend tests
├── frontend/         # Next.js frontend
│   ├── app/         # App router
│   ├── components/  # React components
│   └── styles/      # CSS modules
├── shared/          # Shared code
└── docs/           # Documentation
```

## Features
- AI-powered content generation
- Multi-platform scheduling
- Video processing
- Email marketing
- Analytics dashboard
- Team collaboration

## Development Phases
1. **Phase 1: Core Infrastructure** (4 weeks)
   - Basic setup
   - Authentication
   - Database
   - API structure

2. **Phase 2: Content Management** (6 weeks)
   - Content generation
   - Media processing
   - Storage system

3. **Phase 3: Social Integration** (4 weeks)
   - Platform APIs
   - Scheduling
   - Analytics

4. **Phase 4: Email Marketing** (3 weeks)
   - Templates
   - Campaigns
   - Analytics

## Contributing
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License
MIT License - see LICENSE.md for details

## Support
- Documentation: [docs/](docs/)
- Issues: [GitHub Issues](https://github.com/yourusername/auto-scheduler/issues)
- Email: support@example.com 