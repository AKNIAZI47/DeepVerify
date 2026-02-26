"""
FastAPI dependency injection functions.

This module provides reusable dependencies for authentication,
database access, services, and configuration.
"""

from fastapi import Depends, HTTPException, Request
from bson import ObjectId
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection

from config.settings import Settings, get_settings
from db import get_db, users as users_collection
from security import decode_token
from services.analysis_service import AnalysisService, get_analysis_service


# Configuration dependency
def get_app_settings() -> Settings:
    """
    Get application settings.
    
    Returns:
        Settings instance
    """
    return get_settings()


# Database dependencies
async def get_database() -> AsyncIOMotorDatabase:
    """
    Get database instance.
    
    Returns:
        Database instance
    """
    return get_db()


async def get_users_collection() -> AsyncIOMotorCollection:
    """
    Get users collection.
    
    Returns:
        Users collection
    """
    return users_collection


# Authentication dependencies
async def get_current_user_optional(request: Request) -> Optional[dict]:
    """
    Get current user from JWT token (optional).
    
    Returns None if no valid token is provided.
    
    Args:
        request: FastAPI request
        
    Returns:
        User document or None
    """
    auth = request.headers.get("Authorization")
    if not auth or not auth.lower().startswith("bearer "):
        return None
    
    token = auth.split()[1]
    try:
        data = decode_token(token)
        uid = data["sub"]
        user = await users_collection.find_one({"_id": ObjectId(uid)})
        return user
    except Exception:
        return None


async def get_current_user(request: Request) -> dict:
    """
    Get current user from JWT token (required).
    
    Raises HTTPException if no valid token is provided.
    
    Args:
        request: FastAPI request
        
    Returns:
        User document
        
    Raises:
        HTTPException: If authentication fails
    """
    auth = request.headers.get("Authorization")
    if not auth or not auth.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    token = auth.split()[1]
    try:
        data = decode_token(token)
        uid = data["sub"]
        user = await users_collection.find_one({"_id": ObjectId(uid)})
        if not user:
            raise HTTPException(status_code=401, detail="Unauthorized")
        return user
    except Exception:
        raise HTTPException(status_code=401, detail="Unauthorized")


async def get_current_user_id(user: dict = Depends(get_current_user)) -> str:
    """
    Get current user ID.
    
    Args:
        user: User document from get_current_user
        
    Returns:
        User ID as string
    """
    return str(user["_id"])


# Service dependencies
def get_analysis_service_dependency() -> AnalysisService:
    """
    Get analysis service instance.
    
    Returns:
        AnalysisService instance
    """
    return get_analysis_service()


# Request context dependencies
def get_client_ip(request: Request) -> str:
    """
    Get client IP address from request.
    
    Args:
        request: FastAPI request
        
    Returns:
        Client IP address
    """
    return request.client.host if request.client else "unknown"
