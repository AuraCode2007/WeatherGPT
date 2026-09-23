"""
db_service.py
Database interaction helpers using SQLAlchemy sessions.
"""
from sqlalchemy.orm import Session
from backend.db.models import ChatLog, WeatherSnapshot, AlertLog


def save_chat_log(db: Session, location: str, question: str, response: str, language_code: str = "en", domain: str = "General") -> ChatLog:
    """Persist a chat interaction to the database."""
    log = ChatLog(
        location=location,
        question=question,
        response=response,
        language_code=language_code,
        domain=domain
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def get_recent_chats(db: Session, limit: int = 20) -> list[ChatLog]:
    """Fetch the most recent chat logs."""
    return db.query(ChatLog).order_by(ChatLog.id.desc()).limit(limit).all()


def save_weather_snapshot(db: Session, city: str, weather_data: dict) -> WeatherSnapshot:
    """Persist a live weather telemetry snapshot to the database."""
    snapshot = WeatherSnapshot(
        city=city,
        temp=weather_data.get("temp"),
        feels_like=weather_data.get("feels_like"),
        humidity=weather_data.get("humidity"),
        wind_speed=weather_data.get("wind_speed"),
        condition=weather_data.get("condition"),
        aqi=weather_data.get("aqi"),
        raw_json=weather_data
    )
    db.add(snapshot)
    db.commit()
    db.refresh(snapshot)
    return snapshot


def get_weather_snapshots(db: Session, limit: int = 20) -> list[WeatherSnapshot]:
    """Fetch the most recent live weather snapshots."""
    return db.query(WeatherSnapshot).order_by(WeatherSnapshot.id.desc()).limit(limit).all()


def save_alert_log(db: Session, city: str, alert_data: dict) -> AlertLog:
    """Persist extreme weather alert data to the database."""
    log = AlertLog(
        city=city,
        event=alert_data.get("event"),
        severity=alert_data.get("severity"),
        description=alert_data.get("description"),
        raw_json=alert_data
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def get_alert_logs(db: Session, limit: int = 20) -> list[AlertLog]:
    """Fetch recorded weather alert logs."""
    return db.query(AlertLog).order_by(AlertLog.id.desc()).limit(limit).all()

