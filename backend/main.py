"""
backend/main.py
WeatherGPT — FastAPI entry point.

Provides conversational AI for weather forecasting, alerts, and climate
information as per the hackathon requirements:
  • Real-time weather retrieval
  • NLP-based query understanding (Gemini)
  • Extreme weather alerts & early warnings
  • Location-based forecasting
  • Multilingual support (10 Indian languages)
  • Climate trend analysis
  • Decision support for Agriculture, Aviation, Marine, Urban & Research
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
import os
import time

from backend.db.init_db import init_db, get_db
from backend.config import DATABASE_URL, DB_PATH

# Operational telemetry counters
REQUEST_COUNT = 0
START_TIME = time.time()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager replacing deprecated on_event startup handlers."""
    init_db()
    yield


app = FastAPI(
    title="WeatherGPT API",
    description=(
        "AI-powered conversational platform for real-time weather intelligence, "
        "atmospheric AI twin microclimate simulation, extreme-event alerts, and climate analytics."
    ),
    version="2.4.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ── CORS ─────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Cache-Control & Metrics Middleware ───────────────────────────────────────
@app.middleware("http")
async def add_no_cache_and_metrics(request, call_next):
    global REQUEST_COUNT
    REQUEST_COUNT += 1
    response = await call_next(request)
    if request.url.path.startswith("/css") or request.url.path.startswith("/js") or request.url.path == "/":
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response

# ── Routes ────────────────────────────────────────────────────────────────────
from backend.routes import chat, weather, alerts, climate, simulation  # noqa: E402

app.include_router(chat.router)
app.include_router(weather.router)
app.include_router(alerts.router)
app.include_router(climate.router)
app.include_router(simulation.router)


# ── Health check ──────────────────────────────────────────────────────────────
@app.get("/health", tags=["system"])
async def health():
    return JSONResponse({"status": "ok", "service": "WeatherGPT API v2.4", "uptime_sec": int(time.time() - START_TIME)})


# ── Prometheus Metrics Endpoint ───────────────────────────────────────────────
@app.get("/metrics", tags=["system"], summary="Prometheus-formatted operational metrics")
async def metrics(db: Session = Depends(get_db)):
    """Expose real-time system metrics for technical monitoring."""
    from backend.db.models import ChatLog, WeatherSnapshot, AlertLog
    chat_count = db.query(ChatLog).count()
    weather_count = db.query(WeatherSnapshot).count()
    alert_count = db.query(AlertLog).count()
    uptime = time.time() - START_TIME

    metrics_text = f"""# HELP weathergpt_http_requests_total Total HTTP requests handled.
# TYPE weathergpt_http_requests_total counter
weathergpt_http_requests_total {REQUEST_COUNT}

# HELP weathergpt_uptime_seconds System uptime in seconds.
# TYPE weathergpt_uptime_seconds gauge
weathergpt_uptime_seconds {uptime:.2f}

# HELP weathergpt_db_chat_logs_total Total AI Q&A interactions logged.
# TYPE weathergpt_db_chat_logs_total counter
weathergpt_db_chat_logs_total {chat_count}

# HELP weathergpt_db_weather_snapshots_total Total live weather snapshots logged.
# TYPE weathergpt_db_weather_snapshots_total counter
weathergpt_db_weather_snapshots_total {weather_count}

# HELP weathergpt_db_alerts_total Total hazard alerts logged.
# TYPE weathergpt_db_alerts_total counter
weathergpt_db_alerts_total {alert_count}
"""
    return Response(content=metrics_text, media_type="text/plain; version=0.0.4")


# ── Database stats endpoint ──────────────────────────────────────────────────
@app.get("/db/stats", tags=["system"])
async def db_stats(db: Session = Depends(get_db)):
    """Live record counts from all database tables + DB metadata."""
    from backend.db.models import ChatLog, WeatherSnapshot, AlertLog
    try:
        chat_count     = db.query(ChatLog).count()
        weather_count  = db.query(WeatherSnapshot).count()
        alert_count    = db.query(AlertLog).count()
        latest_chat    = db.query(ChatLog).order_by(ChatLog.id.desc()).first()
        latest_weather = db.query(WeatherSnapshot).order_by(WeatherSnapshot.id.desc()).first()
        is_sqlite = DATABASE_URL.startswith("sqlite")
        return JSONResponse({
            "database_type": "SQLite" if is_sqlite else "PostgreSQL",
            "database_path": DB_PATH if is_sqlite else DATABASE_URL.split("@")[-1],
            "tables": {
                "chat_logs":          {"count": chat_count,
                                       "last_location": latest_chat.location if latest_chat else None,
                                       "last_at": latest_chat.created_at.isoformat() if latest_chat and latest_chat.created_at else None},
                "weather_snapshots":  {"count": weather_count,
                                       "last_city": latest_weather.city if latest_weather else None,
                                       "last_at": latest_weather.recorded_at.isoformat() if latest_weather and latest_weather.recorded_at else None},
                "alert_logs":         {"count": alert_count},
            },
            "total_records": chat_count + weather_count + alert_count,
        })
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


# ── Serve frontend static files ───────────────────────────────────────────────
_frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))

if os.path.isdir(_frontend_dir):
    app.mount("/", StaticFiles(directory=_frontend_dir, html=True), name="frontend")


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)