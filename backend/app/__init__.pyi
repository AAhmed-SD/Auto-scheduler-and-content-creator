from typing import Any, Dict, List, Optional, Union
from fastapi import FastAPI
from sqlalchemy.orm import Session

app: FastAPI

def get_db() -> Session: ... 