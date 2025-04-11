# API Endpoints Documentation

## Overview
This document provides detailed information about the API endpoints available in the Auto-Scheduler & Content Creator platform. All endpoints require JWT authentication unless otherwise specified.

## Authentication

### Login
- **POST** `/api/auth/login`
- **Description**: Authenticate user and get JWT token
- **Request Body**:
  ```json
  {
    "email": "string",
    "password": "string"
  }
  ```
- **Response**:
  ```json
  {
    "access_token": "string",
    "token_type": "bearer",
    "user": {
      "id": "uuid",
      "email": "string",
      "full_name": "string"
    }
  }
  ```

### Refresh Token
- **POST** `/api/auth/refresh`
- **Description**: Get new access token using refresh token
- **Request Body**:
  ```json
  {
    "refresh_token": "string"
  }
  ```
- **Response**:
  ```json
  {
    "access_token": "string",
    "token_type": "bearer"
  }
  ```

## Users

### Get Current User
- **GET** `/api/users/me`
- **Description**: Get current user's profile
- **Response**:
  ```json
  {
    "id": "uuid",
    "email": "string",
    "full_name": "string",
    "is_active": boolean,
    "created_at": "datetime"
  }
  ```

### Update User
- **PUT** `/api/users/me`
- **Description**: Update current user's profile
- **Request Body**:
  ```json
  {
    "full_name": "string",
    "password": "string" // optional
  }
  ```
- **Response**: Updated user profile

## Projects

### List Projects
- **GET** `/api/projects`
- **Description**: Get list of user's projects
- **Query Parameters**:
  - `page`: integer (default: 1)
  - `per_page`: integer (default: 10)
- **Response**:
  ```json
  {
    "items": [
      {
        "id": "uuid",
        "name": "string",
        "description": "string",
        "created_at": "datetime"
      }
    ],
    "total": integer,
    "page": integer,
    "per_page": integer
  }
  ```

### Create Project
- **POST** `/api/projects`
- **Description**: Create new project
- **Request Body**:
  ```json
  {
    "name": "string",
    "description": "string",
    "settings": {
      // project-specific settings
    }
  }
  ```
- **Response**: Created project

### Get Project
- **GET** `/api/projects/{project_id}`
- **Description**: Get project details
- **Response**:
  ```json
  {
    "id": "uuid",
    "name": "string",
    "description": "string",
    "settings": object,
    "created_at": "datetime",
    "updated_at": "datetime"
  }
  ```

## Content

### List Content
- **GET** `/api/projects/{project_id}/content`
- **Description**: Get list of project's content
- **Query Parameters**:
  - `page`: integer (default: 1)
  - `per_page`: integer (default: 10)
  - `status`: string (optional)
  - `content_type`: string (optional)
- **Response**:
  ```json
  {
    "items": [
      {
        "id": "uuid",
        "title": "string",
        "description": "string",
        "content_type": "string",
        "status": "string",
        "created_at": "datetime"
      }
    ],
    "total": integer,
    "page": integer,
    "per_page": integer
  }
  ```

### Create Content
- **POST** `/api/projects/{project_id}/content`
- **Description**: Create new content
- **Request Body**:
  ```json
  {
    "title": "string",
    "description": "string",
    "content_type": "string",
    "media_urls": ["string"],
    "metadata": object
  }
  ```
- **Response**: Created content

### Update Content
- **PUT** `/api/projects/{project_id}/content/{content_id}`
- **Description**: Update content
- **Request Body**:
  ```json
  {
    "title": "string",
    "description": "string",
    "status": "string",
    "media_urls": ["string"],
    "metadata": object
  }
  ```
- **Response**: Updated content

## Social Media

### List Social Media Accounts
- **GET** `/api/projects/{project_id}/social-media`
- **Description**: Get list of project's social media accounts
- **Response**:
  ```json
  {
    "items": [
      {
        "id": "uuid",
        "platform": "string",
        "username": "string",
        "is_active": boolean
      }
    ]
  }
  ```

### Create Social Media Post
- **POST** `/api/projects/{project_id}/content/{content_id}/posts`
- **Description**: Create social media post
- **Request Body**:
  ```json
  {
    "platform": "string",
    "scheduled_time": "datetime",
    "metadata": object
  }
  ```
- **Response**: Created post

### Get Post Performance
- **GET** `/api/projects/{project_id}/content/{content_id}/posts/{post_id}/performance`
- **Description**: Get post performance metrics
- **Response**:
  ```json
  {
    "metrics": {
      "likes": integer,
      "comments": integer,
      "shares": integer,
      "views": integer
    },
    "recorded_at": "datetime"
  }
  ```

## Error Responses

All endpoints may return the following error responses:

### 400 Bad Request
```json
{
  "detail": "string"
}
```

### 401 Unauthorized
```json
{
  "detail": "Not authenticated"
}
```

### 403 Forbidden
```json
{
  "detail": "Not enough permissions"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["string"],
      "msg": "string",
      "type": "string"
    }
  ]
}
```

## Rate Limiting
- 100 requests per minute per user
- 1000 requests per hour per user
- Headers:
  - `X-RateLimit-Limit`: Maximum requests
  - `X-RateLimit-Remaining`: Remaining requests
  - `X-RateLimit-Reset`: Reset time

## Best Practices
1. Always include `Authorization` header
2. Handle rate limiting
3. Use proper HTTP methods
4. Validate input data
5. Handle errors appropriately
6. Use pagination for list endpoints
7. Cache responses when possible 