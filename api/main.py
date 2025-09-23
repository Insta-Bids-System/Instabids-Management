import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Force correct Supabase project (from main branch - MUST BE KEPT)
os.environ["SUPABASE_URL"] = "https://lmbpvkfcfhdfaihigfdu.supabase.co"
os.environ["SUPABASE_ANON_KEY"] = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxtYnB2a2ZjZmhkZmFpaGlnZmR1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTgxMjgzNTIsImV4cCI6MjA3MzcwNDM1Mn0.WH4-iA_FnW1EqGTl-hcpotzqBGgeCutKWBBMaa6Tnmg"
)
os.environ["SUPABASE_SERVICE_KEY"] = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxtYnB2a2ZjZmhkZmFpaGlnZmR1Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1ODEyODM1MiwiZXhwIjoyMDczNzA0MzUyfQ.SSyQjgk5SSgptLXjKM6tNi_ZFZln9tA3FMJYmF3qSz0"
)

# Using relative imports (from PR branch)
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
    logger.info(f"Supabase URL: {settings.supabase_url}")

    # Initialize Supabase connection
    try:
        _ = supabase_service.client
        logger.info("Supabase connection established")
    except Exception as e:
        logger.error(f"Failed to connect to Supabase: {e}")
        raise

    yield

    # Shutdown
    logger.info("Shutting down InstaBids Management API...")


# Create FastAPI app
app = FastAPI(
    title="InstaBids Management API",
    description="Property management platform API",
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


# Add rate limiting middleware
@app.middleware("http")
async def add_rate_limiting(request, call_next):
    return await rate_limit_middleware(request, call_next)


# Include routers
app.include_router(
    auth.router,
    prefix="/api/auth",
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
    tags=["SmartScope AI"],
)


# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "environment": settings.api_env,
        "version": "0.1.0",
    }


# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "InstaBids Management API",
        "docs": "/docs",
        "health": "/health",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_env == "development",
    )