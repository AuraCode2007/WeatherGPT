"""
backend/models.py
Pydantic request/response schemas for all WeatherGPT API endpoints.
"""
from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional


# ── /chat ─────────────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    user_question: str = Field(..., description="Natural-language weather query from the user.")
    location: str = Field("Delhi", description="City / region name.")
    language_code: str = Field("en", description="BCP-47 language code for the response (e.g. 'hi', 'ta').")
    domain: str = Field("General", description="Use-case domain: Agriculture, Aviation, Marine, etc.")

class ChatResponse(BaseModel):
    response: str
    location: str
    language_code: str
    domain: str
    source: str  # "live" | "cache"


# ── /weather ──────────────────────────────────────────────────────────────────

class WeatherResponse(BaseModel):
    city: str
    country: str = ""
    temp: float
    feels_like: float = 0.0
    temp_min: float = 0.0
    temp_max: float = 0.0
    condition: str
    description: str = ""
    humidity: int
    wind_speed: float          # km/h
    wind_direction: int = 0   # degrees
    visibility: float = 0.0   # km
    uv_index: float = 0.0
    aqi: Optional[int] = None  # Air Quality Index
    forecast: list[str]
    alert: Optional[str] = None
    source: str = "live"


# ── /alerts ───────────────────────────────────────────────────────────────────

class AlertDetail(BaseModel):
    event: str
    severity: str = "Unknown"   # Minor / Moderate / Severe / Extreme
    description: str
    start: Optional[str] = None
    end: Optional[str] = None

class AlertResponse(BaseModel):
    location: str
    alerts: list[AlertDetail] = []
    summary: Optional[str] = None


# ── /climate ──────────────────────────────────────────────────────────────────

class ClimateRequest(BaseModel):
    city: str
    month: int = Field(..., ge=1, le=12, description="Month number (1=Jan … 12=Dec).")
    year: Optional[int] = None

class ClimateResponse(BaseModel):
    city: str
    month: int
    avg_temp: float
    avg_humidity: float
    avg_rainfall_mm: float
    trend_summary: str


# ── /simulate (Atmospheric AI Twin & What-If Sandbox) ─────────────────────────

class SimulationRequest(BaseModel):
    location: str = Field("Mumbai", description="Base location for telemetry.")
    temp_delta: float = Field(0.0, description="Temperature shift in Celsius (-10 to +15).")
    humidity_delta: float = Field(0.0, description="Humidity shift in percentage points (-40 to +40).")
    rain_rate_mm_hr: float = Field(0.0, description="Simulated rainfall intensity in mm/hr (0 to 150).")
    wind_gust_kmh: float = Field(0.0, description="Simulated wind gust speed in km/h (0 to 120).")
    domain: str = Field("General", description="Primary operational domain.")
    preset_name: Optional[str] = Field(None, description="Preset scenario title if activated.")
    language_code: str = Field("en", description="BCP-47 language code for the response (e.g. 'hi', 'es').")


class SectorImpact(BaseModel):
    score: int = Field(..., ge=0, le=100, description="Impact hazard score 0-100.")
    risk_level: str = Field(..., description="Low / Moderate / Severe / Critical")
    key_factor: str = Field(..., description="Primary driving atmospheric factor.")
    advisory: str = Field(..., description="Short domain operational guidance.")


class SimulationResponse(BaseModel):
    location: str
    preset_name: Optional[str] = None
    baseline_weather: dict
    simulated_weather: dict
    impact_matrix: dict[str, SectorImpact]
    overall_hazard_index: int
    hazard_level: str
    ai_playbook: str
    source: str = "simulation"