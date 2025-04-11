# API Documentation

## Overview
This document provides detailed information about the Auto-Scheduler & Content Creator API endpoints, request/response formats, and authentication requirements.

## Authentication

### JWT Authentication
All API endpoints require JWT authentication in the Authorization header:
```
Authorization: Bearer <jwt_token>
```

### Token Refresh
```http
POST /api/auth/refresh
Content-Type: application/json

{
  "refresh_token": "string"
}
```

## Endpoints

### Content Management

#### Create Content
```http
POST /api/content
Content-Type: application/json

{
  "title": "string",
  "content_type": "string",
  "content_data": {},
  "project_id": "uuid",
  "schedule": {
    "publish_at": "datetime",
    "platforms": ["string"]
  }
}
```

#### Get Content
```http
GET /api/content/{content_id}
```

#### Update Content
```http
PUT /api/content/{content_id}
Content-Type: application/json

{
  "title": "string",
  "content_data": {},
  "status": "string"
}
```

### Social Media Integration

#### Platform Posts

##### Instagram
```http
POST /api/platforms/instagram/posts
Content-Type: application/json

{
  "content_id": "uuid",
  "caption": "string",
  "location": "string",
  "hashtags": ["string"]
}
```

##### TikTok
```http
POST /api/platforms/tiktok/videos
Content-Type: application/json

{
  "content_id": "uuid",
  "description": "string",
  "hashtags": ["string"],
  "sound_id": "string"
}
```

##### LinkedIn
```http
POST /api/platforms/linkedin/posts
Content-Type: application/json

{
  "content_id": "uuid",
  "text": "string",
  "visibility": "string"
}
```

### Analytics

#### Get Content Performance
```http
GET /api/analytics/content/{content_id}
```

#### Get Platform Metrics
```http
GET /api/analytics/platforms/{platform}
```

### Team Collaboration

#### Create Team
```http
POST /api/teams
Content-Type: application/json

{
  "name": "string",
  "project_id": "uuid",
  "members": [
    {
      "user_id": "uuid",
      "role": "string"
    }
  ]
}
```

#### Assign Content
```http
POST /api/teams/{team_id}/assign
Content-Type: application/json

{
  "content_id": "uuid",
  "assignee_id": "uuid"
}
```

## Error Handling

### Error Response Format
```json
{
  "error": {
    "code": "string",
    "message": "string",
    "details": {}
  }
}
```

### Common Error Codes
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 429: Too Many Requests
- 500: Internal Server Error

## Rate Limiting
- 100 requests per minute per user
- 1000 requests per hour per user

## Webhooks

### Available Events
- content.created
- content.updated
- content.published
- content.failed
- team.assigned
- analytics.updated

### Webhook Payload Format
```json
{
  "event": "string",
  "data": {},
  "timestamp": "datetime"
}
```

## Best Practices

### Request Headers
- Always include Content-Type
- Use Accept header for response format
- Include User-Agent for tracking

### Response Handling
- Check status codes
- Handle errors gracefully
- Implement retry logic
- Cache responses when appropriate

### Security
- Use HTTPS
- Validate all input
- Sanitize output
- Implement rate limiting
- Monitor usage

## SDKs and Libraries

### Python
```python
from auto_scheduler import Client

client = Client(api_key="your_api_key")
content = client.content.create({
    "title": "My Post",
    "content_type": "text",
    "content_data": {"text": "Hello World"}
})
```

### JavaScript
```javascript
import { Client } from 'auto-scheduler';

const client = new Client({ apiKey: 'your_api_key' });
const content = await client.content.create({
    title: 'My Post',
    contentType: 'text',
    contentData: { text: 'Hello World' }
});
```

## Core Endpoints

### Content Generation

#### POST /api/content/analyze
Analyze reference content for style replication.

**Request Body:**
```json
{
  "reference_url": "https://example.com/video.mp4",
  "content_type": "video",
  "style_elements": {
    "cinematic": true,
    "slow_motion": true,
    "color_grading": "warm",
    "text_style": "minimal",
    "music_mood": "emotional"
  }
}
```

**Response:**
```json
{
  "style_analysis": {
    "shot_composition": ["wide", "close-up"],
    "color_palette": ["#FF0000", "#00FF00"],
    "transition_style": "fade",
    "text_animation": "fade-in",
    "music_tempo": "slow"
  },
  "template_id": "template_123"
}
```

#### POST /api/content/generate
Generate content based on analyzed style.

**Request Body:**
```json
{
  "template_id": "template_123",
  "content_type": "video",
  "quote": "Your quote here",
  "style_adjustments": {
    "color_grading": "warmer",
    "text_animation": "slide-in"
  },
  "music_preference": "emotional"
}
```

**Response:**
```json
{
  "content_id": "content_123",
  "status": "generating",
  "estimated_time": "5 minutes",
  "preview_url": "https://storage.example.com/preview.mp4"
}
```

### Auto-Posting

#### POST /api/schedule/content
Schedule generated content for posting.

**Request Body:**
```json
{
  "content_id": "content_123",
  "platforms": ["instagram", "tiktok"],
  "schedule": {
    "instagram": "2023-12-25T08:00:00Z",
    "tiktok": "2023-12-25T08:15:00Z"
  },
  "captions": {
    "instagram": "Your Instagram caption",
    "tiktok": "Your TikTok caption"
  },
  "hashtags": {
    "instagram": ["#islam", "#peace"],
    "tiktok": ["#islam", "#tiktok"]
  }
}
```

**Response:**
```json
{
  "schedule_id": "schedule_123",
  "status": "scheduled",
  "platform_status": {
    "instagram": "scheduled",
    "tiktok": "scheduled"
  }
}
```

#### GET /api/schedule/queue
Get content queue status.

**Query Parameters:**
- `platform`: Filter by platform
- `status`: Filter by status (scheduled, posted, failed)
- `start_date`: Start date range
- `end_date`: End date range

**Response:**
```json
{
  "queue": [
    {
      "schedule_id": "schedule_123",
      "content_id": "content_123",
      "platform": "instagram",
      "scheduled_time": "2023-12-25T08:00:00Z",
      "status": "scheduled",
      "preview_url": "https://storage.example.com/preview.mp4"
    }
  ]
}
```

### Content Management

#### GET /api/content/templates
Get available style templates.

**Response:**
```json
{
  "templates": [
    {
      "template_id": "template_123",
      "name": "Cinematic Quote",
      "style": {
        "color_grading": "warm",
        "text_animation": "fade-in",
        "music_mood": "emotional"
      },
      "preview_url": "https://storage.example.com/preview.mp4"
    }
  ]
}
```

#### POST /api/content/templates
Create new style template.

**Request Body:**
```json
{
  "name": "New Cinematic Style",
  "reference_url": "https://example.com/video.mp4",
  "style_elements": {
    "color_grading": "cool",
    "text_animation": "slide-in",
    "music_mood": "peaceful"
  }
}
```

**Response:**
```json
{
  "template_id": "template_456",
  "status": "created",
  "preview_url": "https://storage.example.com/preview.mp4"
}
```

## Error Responses

All endpoints may return the following error responses:

**400 Bad Request**
```json
{
  "detail": "Invalid request parameters"
}
```

**401 Unauthorized**
```json
{
  "detail": "Could not validate credentials"
}
```

**403 Forbidden**
```json
{
  "detail": "Not enough permissions"
}
```

**404 Not Found**
```json
{
  "detail": "Resource not found"
}
```

**500 Internal Server Error**
```json
{
  "detail": "Internal server error"
}
``` 