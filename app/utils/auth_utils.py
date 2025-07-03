"""Authentication utilities for AI agent."""

from typing import Dict, Any, Optional
import logging
from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader
import time
import jwt

from app.config import settings

logger = logging.getLogger(__name__)

# API key header
API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)

# Simple in-memory API key store (should be replaced with a database in production)
API_KEYS = {
    "test-key": {"user_id": "test-user", "name": "Test User"}
}

def get_current_user(api_key: str = Depends(API_KEY_HEADER)) -> Dict[str, Any]:
    """
    Get current user from API key.
    
    Args:
        api_key: API key from request header
        
    Returns:
        User information
        
    Raises:
        HTTPException: If API key is invalid
    """
    if not api_key:
        logger.warning("Missing API key in request")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key"
        )
        
    user_info = API_KEYS.get(api_key)
    if not user_info:
        logger.warning(f"Invalid API key: {api_key[:5]}...")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    
    logger.debug(f"Authenticated user: {user_info['user_id']}")
    return user_info

def create_jwt_token(
    user_id: str,
    expires_in_seconds: int = 3600,
    secret_key: Optional[str] = None
) -> str:
    """
    Create a JWT token.
    
    Args:
        user_id: User ID
        expires_in_seconds: Token expiration time in seconds
        secret_key: Secret key for JWT
        
    Returns:
        JWT token
    """
    if secret_key is None:
        # In production, use a secure secret key from settings
        secret_key = "insecure-secret-key-for-testing"
    
    payload = {
        "sub": user_id,
        "exp": int(time.time()) + expires_in_seconds,
        "iat": int(time.time())
    }
    
    token = jwt.encode(payload, secret_key, algorithm="HS256")
    return token
