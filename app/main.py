from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from datetime import datetime, timedelta
from typing import List, Optional
import uvicorn
from .core.storage import storage
from .core.scheduler import scheduler
from .core.worker import worker
from .core.logging_config import loggers
import asyncio

app = FastAPI(
    title="Auto Scheduler & Content Creator",
    description="API for managing content creation and scheduling",
    version="0.1.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Start background worker
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(worker.run())

@app.on_event("shutdown")
async def shutdown_event():
    await worker.stop()

@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <html>
        <head>
            <title>Auto Scheduler & Content Creator API</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                    line-height: 1.6;
                }
                .container {
                    background: #f5f5f5;
                    border-radius: 8px;
                    padding: 20px;
                    margin-top: 20px;
                }
                h1 { color: #2c3e50; }
                a {
                    color: #3498db;
                    text-decoration: none;
                }
                a:hover { text-decoration: underline; }
                .endpoints {
                    margin-top: 20px;
                }
                .endpoint {
                    background: white;
                    padding: 10px;
                    margin: 10px 0;
                    border-radius: 4px;
                    border-left: 4px solid #3498db;
                }
            </style>
        </head>
        <body>
            <h1>Welcome to Auto Scheduler & Content Creator API</h1>
            <div class="container">
                <h2>API Documentation</h2>
                <p>Explore our API using these interactive documentation interfaces:</p>
                <ul>
                    <li><a href="/docs">Swagger UI Documentation</a> - Interactive API documentation</li>
                    <li><a href="/redoc">ReDoc Documentation</a> - Alternative API documentation</li>
                </ul>
            </div>
            <div class="container">
                <h2>Available Services</h2>
                <ul>
                    <li>FastAPI Application - <code>http://localhost:8000</code></li>
                    <li>PostgreSQL Database - <code>localhost:5432</code></li>
                    <li>PgAdmin Interface - <a href="http://localhost:5050">http://localhost:5050</a></li>
                    <li>Redis Cache - <code>localhost:6379</code></li>
                </ul>
            </div>
            <div class="container endpoints">
                <h2>Key Features</h2>
                <div class="endpoint">
                    <h3>Content Creation</h3>
                    <p>AI-powered content generation and scheduling</p>
                </div>
                <div class="endpoint">
                    <h3>Social Media Management</h3>
                    <p>Manage and schedule posts across multiple platforms</p>
                </div>
                <div class="endpoint">
                    <h3>Analytics</h3>
                    <p>Track performance and engagement metrics</p>
                </div>
            </div>
        </body>
    </html>
    """

@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    project_id: str = None,
    metadata: Optional[dict] = None
):
    """Upload a file"""
    try:
        if not project_id:
            raise HTTPException(status_code=400, detail="Project ID is required")

        file_metadata = await storage.save_file(file, project_id, metadata)
        return {"status": "success", "data": file_metadata}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/schedule")
async def schedule_content(
    content_id: str,
    scheduled_time: datetime,
    platform: str,
    metadata: Optional[dict] = None
):
    """Schedule content for posting"""
    try:
        job_data = {
            "content_id": content_id,
            "platform": platform,
            "metadata": metadata or {}
        }

        job_id = await scheduler.schedule_job(job_data, scheduled_time)
        return {"status": "success", "job_id": job_id}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/jobs")
async def get_jobs(status: Optional[str] = None):
    """Get scheduled jobs"""
    try:
        # TODO: Implement job retrieval from database
        return {"status": "success", "jobs": []}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "storage": "ok",
            "scheduler": "ok",
            "worker": "running" if worker.running else "stopped"
        }
    }

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True) 