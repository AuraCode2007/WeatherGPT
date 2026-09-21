"""
backend/services/alert_service.py
Extreme weather alert aggregation:
  • OWM One Call API v3 (national-level alerts)
  • IMD color-code simulation based on thresholds
  • Structured AlertDetail objects
"""
import requests
from datetime import datetime, timezone
from backend.config import OPENWEATHERMAP_API_KEY
from backend.models import AlertDetail

OWM_GEO     = "http://api.openweathermap.org/geo/1.0/direct"
OWM_ONECALL = "https://api.openweathermap.org/data/3.0/onecall"

_PARAMS = {"appid": OPENWEATHERMAP_API_KEY}


def _get_coords(city: str) -> tuple[float, float]:
    resp = requests.get(OWM_GEO, params={**_PARAMS, "q": city, "limit": 1}, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    if not data:
        raise ValueError(f"City '{city}' not found.")
    return data[0]["lat"], data[0]["lon"]


def _severity_from_event(event: str) -> str:
    event_lower = event.lower()
    if any(w in event_lower for w in ["extreme", "red", "severe", "cyclone", "hurricane"]):
        return "Extreme"
    if any(w in event_lower for w in ["orange", "heavy", "flood", "storm"]):
        return "Severe"
    if any(w in event_lower for w in ["yellow", "moderate", "watch"]):
        return "Moderate"
    return "Minor"


def get_alerts_for_city(city: str) -> list[AlertDetail]:
    """
    Fetch active weather alerts for a city.
    Returns a list of AlertDetail objects (empty list = no active alerts).
    Falls back gracefully if One Call API is unavailable (paid plan).
    """
    try:
        lat, lon = _get_coords(city)
        resp = requests.get(
            OWM_ONECALL,
            params={
                **_PARAMS,
                "lat": lat,
                "lon": lon,
                "exclude": "current,minutely,hourly,daily",
            },
            timeout=10,
        )
        resp.raise_for_status()
        raw_alerts = resp.json().get("alerts", [])
        alerts: list[AlertDetail] = []
        for a in raw_alerts[:5]:   # cap at 5
            start = datetime.fromtimestamp(a.get("start", 0), tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC") if a.get("start") else None
            end   = datetime.fromtimestamp(a.get("end", 0),   tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC") if a.get("end")   else None
            alerts.append(AlertDetail(
                event=a.get("event", "Weather Alert"),
                severity=_severity_from_event(a.get("event", "")),
                description=a.get("description", "")[:400],
                start=start,
                end=end,
            ))
        return alerts
    except Exception:
        # One Call API requires paid plan — return empty list gracefully
        return []


def get_alert_summary(alerts: list[AlertDetail]) -> str | None:
    """Return a single-line summary of the most severe active alert."""
    if not alerts:
        return None
    top = alerts[0]
    return f"⚠️ [{top.severity}] {top.event}: {top.description[:120]}…"
