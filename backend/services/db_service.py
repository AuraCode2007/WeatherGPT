"""
db_service.py
PostgreSQL query helpers using SQLAlchemy sessions.
"""
from sqlalchemy.orm import Session
from backend.db.models import ChatLog


def save_chat_log(db: Session, location: str, question: str, response: str) -> ChatLog:
    """Persist a chat interaction to the database."""
    log = ChatLog(location=location, question=question, response=response)
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def get_recent_chats(db: Session, limit: int = 20) -> list[ChatLog]:
    """Fetch the most recent chat logs."""
    return db.query(ChatLog).order_by(ChatLog.id.desc()).limit(limit).all()
