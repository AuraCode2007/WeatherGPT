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
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import os

from backend.db.init_db import init_db

app = FastAPI(
    title="WeatherGPT API",
    description=(
        "AI-powered conversational platform for real-time weather intelligence, "
        "extreme-event alerts, multilingual forecasting, and climate analytics."
    ),
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

@app.on_event("startup")
def on_startup():
    init_db()

# ── CORS ─────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Cache-Control Middleware ──────────────────────────────────────────────────
@app.middleware("http")
async def add_no_cache_header(request, call_next):
    response = await call_next(request)
    if request.url.path.startswith("/css") or request.url.path.startswith("/js") or request.url.path == "/":
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response

# ── Routes ────────────────────────────────────────────────────────────────────
from backend.routes import chat, weather, alerts, climate  # noqa: E402

app.include_router(chat.router)
app.include_router(weather.router)
app.include_router(alerts.router)
app.include_router(climate.router)


# ── Health check ──────────────────────────────────────────────────────────────
@app.get("/health", tags=["system"])
async def health():
    return JSONResponse({"status": "ok", "service": "WeatherGPT API v2.0"})


# ── Serve frontend static files ───────────────────────────────────────────────
_frontend_dir = os.path.join(os.path.dirname(__file__), "..", "frontend")
_frontend_dir = os.path.abspath(_frontend_dir)

if os.path.isdir(_frontend_dir):
    app.mount("/", StaticFiles(directory=_frontend_dir, html=True), name="frontend")


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)