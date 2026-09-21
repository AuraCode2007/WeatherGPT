"""
db/init_db.py
Creates all database tables on application startup.
Run directly to bootstrap the schema:
    python -m backend.db.init_db
"""
from sqlalchemy import create_engine
from backend.config import DATABASE_URL
from backend.db.models import Base


def init_db() -> None:
    """Create all tables defined in ORM models (no-op if already exist)."""
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created (or already exist).")


if __name__ == "__main__":
    init_db()
