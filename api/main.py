"""Main FastAPI application module for InstaBids Management API."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from api.config import settings
from api.dependencies import get_supabase_client
from api.routers.auth import router as auth_router
from api.routers.properties import router as properties_router
from api.routers.projects import router as projects_router
from api.routers.quotes import router as quotes_router


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager."""
    logger.info("Starting InstaBids Management API")
    supabase = get_supabase_client()
    logger.info(f"Connected to Supabase: {settings.supabase_url}")
    yield
    logger.info("Shutting down InstaBids Management API")


app = FastAPI(
    title="InstaBids Management API",
    description="Property management platform for maintenance coordination",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trusted host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "*.vercel.app"],
)

# Include routers
app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
app.include_router(properties_router, prefix="/api/properties", tags=["properties"])
app.include_router(projects_router, prefix="/api/projects", tags=["projects"])
app.include_router(quotes_router, prefix="/api/quotes", tags=["quotes"])


@app.get("/")
async def root() -> dict[str, Any]:
    """Root endpoint."""
    return {"message": "InstaBids Management API", "version": "1.0.0"}


@app.get("/health")
async def health_check() -> dict[str, Any]:
    """Health check endpoint."""
    try:
        supabase = get_supabase_client()
        result = supabase.table("users").select("count", count="exact").limit(0).execute()
        return {"status": "healthy", "database": "connected"}
    except Exception as exc:
        logger.exception("Health check failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service unavailable",
        ) from exc