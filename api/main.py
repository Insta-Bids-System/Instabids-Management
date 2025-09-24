import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .middleware.rate_limit import rate_limit_middleware
from .routers import auth, projects, properties, quotes, smartscope
from .services.supabase import supabase_service

# Configure logging
logging.basicConfig(
    level=logging.INFO if settings.api_env == "development" else logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting InstaBids Management API...")
    logger.info(f"Environment: {settings.api_env}")
    logger.info(f"Supabase URL: {settings.supabase_url_value}")

    # Initialize Supabase connection
    try:
        supabase_service.force_reinitialize()
        _ = supabase_service.client
        logger.info("Supabase connection established")
        logger.info(f"Service key available: {bool(settings.supabase_service_key_value)}")
    except Exception as e:
        logger.error(f"Failed to connect to Supabase: {e}")
        raise

    yield

    # Shutdown
    logger.info("Shutting down InstaBids Management API...")


# Create FastAPI app
app = FastAPI(
    title="InstaBids Management API",
    description="Backend API for InstaBids property management platform",
    version="0.1.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.cors_origins),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting middleware
@app.middleware("http")
async def add_rate_limiting(request, call_next):
    return await rate_limit_middleware(request, call_next)


# Include routers
app.include_router(
    auth.router,
    prefix="/api",
    tags=["Authentication"],
)

app.include_router(
    properties.router,
    prefix="/api",
    tags=["Properties"],
)

app.include_router(
    projects.router,
    prefix="/api",
    tags=["Projects"],
)

app.include_router(
    quotes.router,
    prefix="/api",
    tags=["Quotes"],
)

app.include_router(
    smartscope.router,
    prefix="/api",
    tags=["SmartScope"],
)


# Health check endpoint
@app.get("/health")
async def health_check():
    """Simple health check endpoint"""
    return {
        "status": "healthy",
        "environment": settings.api_env,
        "timestamp": __import__("datetime").datetime.utcnow().isoformat()
    }


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "InstaBids Management API",
        "version": "0.1.0",
        "status": "running",
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_env == "development",
    )