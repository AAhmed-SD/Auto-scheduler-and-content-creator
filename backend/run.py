import uvicorn
from app.core.init_db import init_db

if __name__ == "__main__":
    # Initialize database
    init_db()
    
    # Run the application
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        workers=4
    )
