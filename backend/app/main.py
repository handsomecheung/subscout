#!/usr/bin/env python3
"""FastAPI main application entry point."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import routes
from app.core.config import settings, init_directories
from app.models.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown events."""
    # Startup
    init_directories()
    await init_db()
    yield
    # Shutdown
    pass


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint."""
    return {"name": settings.APP_NAME, "version": settings.VERSION, "status": "running"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


app.include_router(routes.router, prefix="/api")
