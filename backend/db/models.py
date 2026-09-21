"""
backend/db/models.py
SQLAlchemy ORM models for WeatherGPT.
"""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, JSON
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class ChatLog(Base):
    """Stores every conversational query, language, domain, and AI response."""
    __tablename__ = "chat_logs"

    id            = Column(Integer, primary_key=True, index=True)
    location      = Column(String(150), nullable=False, index=True)
    language_code = Column(String(10), default="en")
    domain        = Column(String(80), default="General")
    question      = Column(Text, nullable=False)
    response      = Column(Text, nullable=False)
    created_at    = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class WeatherSnapshot(Base):
    """
    Periodic weather snapshots for trend analysis and DB-level cache.
    Stored every time the /weather endpoint is called.
    """
    __tablename__ = "weather_snapshots"

    id           = Column(Integer, primary_key=True, index=True)
    city         = Column(String(150), nullable=False, index=True)
    temp         = Column(Float)
    feels_like   = Column(Float)
    humidity     = Column(Integer)
    wind_speed   = Column(Float)
    condition    = Column(String(100))
    aqi          = Column(Integer, nullable=True)
    raw_json     = Column(JSON)
    recorded_at  = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)


class AlertLog(Base):
    """
    Persists every retrieved extreme weather alert for audit and analytics.
    """
    __tablename__ = "alert_logs"

    id          = Column(Integer, primary_key=True, index=True)
    city        = Column(String(150), nullable=False, index=True)
    event       = Column(String(200))
    severity    = Column(String(50))
    description = Column(Text)
    raw_json    = Column(JSON, nullable=True)
    fetched_at  = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
