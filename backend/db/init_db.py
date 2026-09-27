"""
db/init_db.py
Creates all database tables on application startup.
Supports SQLite (default, no server needed) and PostgreSQL.
"""
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker
from backend.config import DATABASE_URL, DB_PATH
from backend.db.models import Base

_is_sqlite = DATABASE_URL.startswith("sqlite")
connect_args = {"check_same_thread": False} if _is_sqlite else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)

# Enable Write-Ahead Logging for SQLite — safe concurrent reads & writes
if _is_sqlite:
    @event.listens_for(engine, "connect")
    def _set_sqlite_pragmas(dbapi_conn, _record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    """Create all tables defined in ORM models (no-op if already exist)."""
    Base.metadata.create_all(bind=engine)
    db_info = f"SQLite -> {DB_PATH}" if _is_sqlite else DATABASE_URL
    print(f"[DB] OK  Database ready ({db_info})")
    print("[DB]     Tables: chat_logs | weather_snapshots | alert_logs")



def get_db():
    """Dependency that yields a database session and closes it on completion."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
