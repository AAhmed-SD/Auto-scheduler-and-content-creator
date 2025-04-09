# API Documentation

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