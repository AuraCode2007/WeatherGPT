from dotenv import load_dotenv
import os

load_dotenv()

# ── Core API Keys ─────────────────────────────────────────────────────────────
OPENWEATHERMAP_API_KEY: str = os.getenv("OPENWEATHERMAP_API_KEY", "")
GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

# ── Database & Cache ──────────────────────────────────────────────────────────
_db_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "database"))
os.makedirs(_db_dir, exist_ok=True)
_default_sqlite_path = os.path.join(_db_dir, "weather_gpt.db")

_db_env: str = os.getenv("DATABASE_URL", "")
if _db_env:
    DATABASE_URL: str = _db_env
else:
    DATABASE_URL: str = f"sqlite:///{_default_sqlite_path}"

REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")

# ── App ───────────────────────────────────────────────────────────────────────
APP_ENV: str = os.getenv("APP_ENV", "development")
BACKEND_URL: str = os.getenv("BACKEND_URL", "http://localhost:8000")

# ── Gemini model to use ───────────────────────────────────────────────────────
GEMINI_MODEL: str = "gemini-3.5-flash-lite"

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