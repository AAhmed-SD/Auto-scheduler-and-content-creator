# Development Environment Setup

## Prerequisites

- Python 3.9+
- Node.js 16+
- PostgreSQL 13+
- Docker (optional)
- Git

## Backend Setup

1. Create and activate virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. Initialize database:
   ```bash
   alembic upgrade head
   ```

5. Run development server:
   ```bash
   uvicorn main:app --reload
   ```

## Frontend Setup

1. Install dependencies:
   ```bash
   cd frontend
   npm install
   ```

2. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. Run development server:
   ```bash
   npm start
   ```

## Social Media API Setup

### X (Twitter) API
1. Create a Twitter Developer account
2. Create a new project and app
3. Get API keys and tokens
4. Add to backend .env:
   ```
   TWITTER_API_KEY=your_api_key
   TWITTER_API_SECRET=your_api_secret
   TWITTER_ACCESS_TOKEN=your_access_token
   TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret
   ```

### Instagram API
1. Create a Facebook Developer account
2. Create a new app
3. Get API credentials
4. Add to backend .env:
   ```
   INSTAGRAM_APP_ID=your_app_id
   INSTAGRAM_APP_SECRET=your_app_secret
   INSTAGRAM_ACCESS_TOKEN=your_access_token
   ```

### Pinterest API
1. Create a Pinterest Developer account
2. Create a new app
3. Get API credentials
4. Add to backend .env:
   ```
   PINTEREST_APP_ID=your_app_id
   PINTEREST_APP_SECRET=your_app_secret
   PINTEREST_ACCESS_TOKEN=your_access_token
   ```

### TikTok API
1. Create a TikTok Developer account
2. Create a new app
3. Get API credentials
4. Add to backend .env:
   ```
   TIKTOK_APP_ID=your_app_id
   TIKTOK_APP_SECRET=your_app_secret
   TIKTOK_ACCESS_TOKEN=your_access_token
   ```

### YouTube API
1. Create a Google Cloud account
2. Enable YouTube Data API
3. Create credentials
4. Add to backend .env:
   ```
   YOUTUBE_API_KEY=your_api_key
   YOUTUBE_CLIENT_ID=your_client_id
   YOUTUBE_CLIENT_SECRET=your_client_secret
   ```

## AI Services Setup

### Stable Diffusion
1. Set up Stable Diffusion API
2. Add to backend .env:
   ```
   STABLE_DIFFUSION_API_KEY=your_api_key
   STABLE_DIFFUSION_API_URL=your_api_url
   ```

### GPT-4
1. Get OpenAI API key
2. Add to backend .env:
   ```
   OPENAI_API_KEY=your_api_key
   ```

## Storage Setup

### AWS S3
1. Create AWS account
2. Create S3 bucket
3. Get access keys
4. Add to backend .env:
   ```
   AWS_ACCESS_KEY_ID=your_access_key
   AWS_SECRET_ACCESS_KEY=your_secret_key
   AWS_BUCKET_NAME=your_bucket_name
   AWS_REGION=your_region
   ```

## Testing

1. Backend tests:
   ```bash
   cd backend
   pytest
   ```

2. Frontend tests:
   ```bash
   cd frontend
   npm test
   ```

## Troubleshooting

### Common Issues

1. **Database Connection**
   - Check PostgreSQL is running
   - Verify credentials in .env
   - Check database exists

2. **API Authentication**
   - Verify API keys
   - Check token expiration
   - Ensure proper scopes

3. **CORS Issues**
   - Check frontend URL in CORS settings
   - Verify HTTPS settings
   - Check proxy configuration

4. **Storage Issues**
   - Verify AWS credentials
   - Check bucket permissions
   - Ensure proper CORS configuration

### Getting Help

1. Check documentation
2. Search issue tracker
3. Contact development team
4. Join community chat 