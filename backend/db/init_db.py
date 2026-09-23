"""
db/init_db.py
Creates all database tables on application startup.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.config import DATABASE_URL
from backend.db.models import Base

connect_args = {"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    """Create all tables defined in ORM models (no-op if already exist)."""
    Base.metadata.create_all(bind=engine)
    print("[DB] Database tables created (or already exist).")


def get_db():
    """Dependency that yields a database session and closes it on completion."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


if __name__ == "__main__":
    init_db()

