"""Authentication and authorization utilities."""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from app.models.project import Project
from app.models.user import User
from app.core.database import get_db

# OAuth2 configuration
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
SECRET_KEY = "your-secret-key"  # TODO: Move to environment variable
ALGORITHM = "HS256"

def check_project_access(project_id: int, user_id: int, db: Session) -> bool:
    """Check if a user has access to a project."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        return False

    # Check if user is team member
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return False

    # Check if user is in the project's team
    return bool(any(team.id == project.team_id for team in user.teams))

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Get the current authenticated user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id_str = payload.get("sub")
        if user_id_str is None:
            raise credentials_exception
        user_id = int(user_id_str)
    except (JWTError, ValueError):
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user
