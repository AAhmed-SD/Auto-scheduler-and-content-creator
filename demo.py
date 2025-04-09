from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import uvicorn
from datetime import datetime, timedelta
import jwt
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Auto Scheduler Demo")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Demo data
DEMO_USERS = {
    "admin": {
        "username": "admin",
        "password": "admin123",
        "role": "admin"
    },
    "user": {
        "username": "user",
        "password": "user123",
        "role": "user"
    }
}

DEMO_CONTENT = [
    {
        "id": 1,
        "title": "Welcome Post",
        "description": "First demo content",
        "scheduled_time": datetime.now() + timedelta(days=1)
    },
    {
        "id": 2,
        "title": "Product Launch",
        "description": "New feature announcement",
        "scheduled_time": datetime.now() + timedelta(days=2)
    }
]

# Models
class User(BaseModel):
    username: str
    password: str

class Content(BaseModel):
    title: str
    description: str
    scheduled_time: datetime

class Token(BaseModel):
    access_token: str
    token_type: str

# Security
SECRET_KEY = "demo_secret_key"
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Routes
@app.post("/token", response_model=Token)
async def login(user: User):
    if user.username not in DEMO_USERS or DEMO_USERS[user.username]["password"] != user.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token({"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/content")
async def get_content(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username not in DEMO_USERS:
            raise HTTPException(status_code=401, detail="Invalid token")
        return DEMO_CONTENT
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.post("/content")
async def create_content(content: Content, token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username not in DEMO_USERS:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        new_content = {
            "id": len(DEMO_CONTENT) + 1,
            **content.dict()
        }
        DEMO_CONTENT.append(new_content)
        return new_content
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

if __name__ == "__main__":
    uvicorn.run("demo:app", host="0.0.0.0", port=8000, reload=True) 