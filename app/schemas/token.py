"""Token-related Pydantic schemas."""

from typing import Optional

from pydantic import BaseModel


class Token(BaseModel):
    """Token response schema."""

    access_token: str
    token_type: str
    refresh_token: Optional[str] = None


class TokenPayload(BaseModel):
    """Token payload schema."""

    sub: int  # subject (user id)
    exp: int  # expiration time
    iat: int  # issued at time
    type: str  # token type (access or refresh) 