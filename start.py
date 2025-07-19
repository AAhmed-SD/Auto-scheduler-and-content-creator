#!/usr/bin/env python3
"""
Start Auto-scheduler Solo
"""

import os
import sys
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import fastapi
        import uvicorn
        return True
    except ImportError:
        print("❌ Missing dependencies. Run: python setup_solo.py")
        return False

def create_directories():
    """Create necessary directories"""
    for directory in ["data", "data/uploads", "data/logs"]:
        Path(directory).mkdir(parents=True, exist_ok=True)

def run_app():
    """Run the application"""
    print("🚀 Starting Auto-scheduler Solo...")
    
    # Set environment
    os.environ.setdefault("DEBUG", "true")
    os.environ.setdefault("DATABASE_URL", "sqlite:///data/app.db")
    
    try:
        from main import app
        import uvicorn
        
        print("✅ App loaded")
        print("🌐 http://127.0.0.1:8000")
        print("📚 http://127.0.0.1:8000/docs")
        print("🔄 Ctrl+C to stop")
        
        uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Run: python setup_solo.py")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

def main():
    """Main function"""
    print("🎯 Auto-scheduler Solo")
    print("=" * 25)
    
    if not check_dependencies():
        sys.exit(1)
    
    create_directories()
    run_app()

if __name__ == "__main__":
    main() 