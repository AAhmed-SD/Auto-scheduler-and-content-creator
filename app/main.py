from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

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