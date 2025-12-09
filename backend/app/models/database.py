#!/usr/bin/env python3
"""Database models for backend."""

from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, relationship

from app.core.config import settings

Base = declarative_base()


class Session(Base):
    """Session model for tracking subtitle processing sessions."""

    __tablename__ = "sessions"

    id = Column(String, primary_key=True)
    language = Column(String, nullable=False)
    subtitle_filename = Column(String, nullable=False)
    subtitle_path = Column(String, nullable=False)
    status = Column(String, default="uploaded")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    words = relationship("SessionWord", back_populates="session", cascade="all, delete-orphan")


class SessionWord(Base):
    """Word model for storing words from a session."""

    __tablename__ = "session_words"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, ForeignKey("sessions.id"), nullable=False)
    word = Column(String, nullable=False)
    frequency = Column(Integer, nullable=False, default=1)
    is_removed = Column(Boolean, default=False)  # User marked as "learned"

    session = relationship("Session", back_populates="words")


engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    future=True,
)

AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db():
    """Dependency for getting database session."""
    async with AsyncSessionLocal() as session:
        yield session


async def init_db():
    """Initialize database tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
