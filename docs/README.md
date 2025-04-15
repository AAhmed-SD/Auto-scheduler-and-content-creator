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

## Development Timeline (2.5 Months)

### Phase 1: Core Infrastructure & Authentication (2 weeks)
- Database setup with Supabase
- Basic API structure with FastAPI
- User authentication system
- Project management features
- Basic content management
- Documentation

### Phase 2: Content & Social Integration (2 weeks)
- Content creation interface
- Content scheduling system
- Media upload and storage
- Instagram API integration
- TikTok API integration
- LinkedIn API integration
- Basic analytics

### Phase 3: Advanced Features & Analytics (2 weeks)
- Advanced scheduling features
- Content automation
- Performance analytics
- Team collaboration features
- Advanced reporting
- Email marketing integration

### Phase 4: Enterprise Features & Optimization (2 weeks)
- Team collaboration tools
- Advanced security features
- Performance optimization
- Custom integrations
- White-label solutions
- Advanced API features

### Phase 5: Testing, Documentation & Launch (1 week)
- Comprehensive testing
- User documentation
- API documentation
- Deployment preparation
- Launch checklist
- Post-launch support

*Note: This timeline assumes 10-12 hours of development work per day, 7 days a week.*

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