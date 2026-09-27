from dotenv import load_dotenv
import os

load_dotenv()

# ── Core API Keys ─────────────────────────────────────────────────────────────
OPENWEATHERMAP_API_KEY: str = os.getenv("OPENWEATHERMAP_API_KEY", "")
GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

# ── Database & Cache ──────────────────────────────────────────────────────────
# SQLite is the default — no server needed. Set DATABASE_URL in .env only if
# you have a PostgreSQL server running (e.g. postgresql://user:pw@host/db).
_db_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "database"))
os.makedirs(_db_dir, exist_ok=True)
DB_PATH: str = os.path.join(_db_dir, "weather_gpt.db")  # absolute path to SQLite file

_db_env: str = (os.getenv("DATABASE_URL") or "").strip()
DATABASE_URL: str = _db_env if _db_env else f"sqlite:///{DB_PATH}"

REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")

# ── App ───────────────────────────────────────────────────────────────────────
APP_ENV: str = os.getenv("APP_ENV", "development")
BACKEND_URL: str = os.getenv("BACKEND_URL", "http://localhost:8000")

# ── Gemini model to use ───────────────────────────────────────────────────────
# Priority: .env GEMINI_MODEL → gemini-3.6-flash (latest stable)
GEMINI_MODEL: str = (os.getenv("GEMINI_MODEL") or "").strip() or "gemini-3.6-flash"

# ── Supported Indian languages ────────────────────────────────────────────────
SUPPORTED_LANGUAGES: dict[str, str] = {
    "English": "en",
    "हिंदी (Hindi)": "hi",
    "தமிழ் (Tamil)": "ta",
    "తెలుగు (Telugu)": "te",
    "বাংলা (Bengali)": "bn",
    "ಕನ್ನಡ (Kannada)": "kn",
    "मराठी (Marathi)": "mr",
    "ગુજરાતી (Gujarati)": "gu",
    "ਪੰਜਾਬੀ (Punjabi)": "pa",
    "മലയാളം (Malayalam)": "ml",
}

# ── Use-case domains ──────────────────────────────────────────────────────────
USE_CASE_DOMAINS: list[str] = [
    "General",
    "Agriculture / Farming",
    "Aviation",
    "Flood & Cyclone Warning",
    "Smart City / Urban",
    "Marine & Fisheries",
    "Climate Research",
]