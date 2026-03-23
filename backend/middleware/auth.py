"""
JWT Authentication Middleware
"""

import jwt
from datetime import datetime, timedelta
from typing import Optional
from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from config import JWT_SECRET_KEY, JWT_ALGORITHM, JWT_EXPIRATION_MINUTES

security = HTTPBearer()


class TokenData(BaseModel):
    user_id: str
    email: str
    role: str
    exp: datetime


class User(BaseModel):
    user_id: str
    email: str
    role: str  # admin, researcher, viewer


def create_access_token(user_id: str, email: str, role: str = "researcher") -> str:
    """
    Create JWT access token
    """
    expire = datetime.utcnow() + timedelta(minutes=JWT_EXPIRATION_MINUTES)
    
    payload = {
        "user_id": user_id,
        "email": email,
        "role": role,
        "exp": expire,
        "iat": datetime.utcnow()
    }
    
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return token


def decode_token(token: str) -> TokenData:
    """
    Decode and validate JWT token
    """
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return TokenData(**payload)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> User:
    """
    Dependency to get current authenticated user
    """
    token = credentials.credentials
    token_data = decode_token(token)
    
    return User(
        user_id=token_data.user_id,
        email=token_data.email,
        role=token_data.role
    )


async def require_role(required_role: str):
    """
    Dependency to check user role
    """
    async def role_checker(user: User = Depends(get_current_user)) -> User:
        if user.role != required_role and user.role != "admin":
            raise HTTPException(
                status_code=403,
                detail=f"Insufficient permissions. Required role: {required_role}"
            )
        return user
    return role_checker


# Role-based dependencies
require_admin = require_role("admin")
require_researcher = require_role("researcher")
