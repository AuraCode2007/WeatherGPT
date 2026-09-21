"""
backend/services/weather_service.py
OpenWeatherMap integration:
  - Current conditions (temp, humidity, wind, visibility, AQI)
  - 5-day / 3-hour forecast condensed to daily summaries
  - Air Quality Index via OWM Pollution API
"""
import requests
from datetime import datetime, timezone
from backend.config import OPENWEATHERMAP_API_KEY

OWM_BASE = "https://api.openweathermap.org/data/2.5"
OWM_AIR  = "http://api.openweathermap.org/data/2.5/air_pollution"
OWM_GEO  = "http://api.openweathermap.org/geo/1.0/direct"

_PARAMS = {"appid": OPENWEATHERMAP_API_KEY, "units": "metric"}

# IMD-style color warnings based on weather category
_ALERT_THRESHOLDS = {
    "temp_extreme_high": 42.0,   # °C
    "temp_extreme_low": 4.0,     # °C
    "wind_severe": 62.0,          # km/h (gale force)
    "humidity_very_high": 95,
}


def _resolve_coords(city: str) -> tuple[float, float, str, str]:
    """Return (lat, lon, resolved_name, country)."""
    resp = requests.get(OWM_GEO, params={**_PARAMS, "q": city, "limit": 1}, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    if not data:
        raise ValueError(f"City '{city}' not found.")
    return data[0]["lat"], data[0]["lon"], data[0].get("name", city), data[0].get("country", "")


def _fetch_aqi(lat: float, lon: float) -> int | None:
    """Fetch Air Quality Index (1=Good … 5=Very Poor)."""
    try:
        resp = requests.get(OWM_AIR, params={**_PARAMS, "lat": lat, "lon": lon}, timeout=8)
        resp.raise_for_status()
        return resp.json()["list"][0]["main"]["aqi"]
    except Exception:
        return None


def fetch_weather(city: str) -> dict:
    """
    Fetch comprehensive current weather + 5-day forecast for a city.
    Returns a unified dict compatible with the WeatherResponse schema.
    """
    lat, lon, resolved_name, country = _resolve_coords(city)

    # ── Current weather ──────────────────────────────────────────────────────
    cur = requests.get(
        f"{OWM_BASE}/weather",
        params={**_PARAMS, "lat": lat, "lon": lon},
        timeout=10,
    )
    if cur.status_code == 404:
        raise ValueError(f"City '{city}' not found.")
    cur.raise_for_status()
    c = cur.json()

    wind_info = c.get("wind") or {}
    weather_list = c.get("weather") or [{}]
    weather_primary = weather_list[0] if weather_list else {}

    wind_speed_kmh = round(wind_info.get("speed", 0) * 3.6, 1)
    visibility_km = round(c.get("visibility", 0) / 1000, 1)

    # ── 5-Day forecast (3-hourly → daily summary) ────────────────────────────
    fc = requests.get(
        f"{OWM_BASE}/forecast",
        params={**_PARAMS, "lat": lat, "lon": lon, "cnt": 40},
        timeout=10,
    )
    fc.raise_for_status()
    forecast_raw = fc.json().get("list", [])

    seen: set[str] = set()
    daily: list[str] = []
    for entry in forecast_raw:
        dt_txt = entry.get("dt_txt", "")
        if not dt_txt or " " not in dt_txt:
            continue
        date_str = dt_txt.split(" ")[0]
        if date_str in seen:
            continue
        seen.add(date_str)
        t = entry.get("main", {}).get("temp", 0)
        e_weather = entry.get("weather") or [{}]
        desc = e_weather[0].get("description", "").title()
        hum = entry.get("main", {}).get("humidity", 0)
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            label = dt.strftime("%a %d %b")
        except ValueError:
            label = date_str
        daily.append(f"{label}: {t:.0f}°C, {desc}, Humidity {hum}%")
        if len(daily) == 5:
            break

    # ── AQI ──────────────────────────────────────────────────────────────────
    aqi = _fetch_aqi(lat, lon)

    # ── Derived alert ─────────────────────────────────────────────────────────
    alert = _derive_local_alert(c, wind_speed_kmh)

    main_info = c.get("main", {})

    return {
        "city": resolved_name,
        "country": country,
        "temp": round(main_info.get("temp", 0), 1),
        "feels_like": round(main_info.get("feels_like", main_info.get("temp", 0)), 1),
        "temp_min": round(main_info.get("temp_min", main_info.get("temp", 0)), 1),
        "temp_max": round(main_info.get("temp_max", main_info.get("temp", 0)), 1),
        "condition": weather_primary.get("main", "Clear"),
        "description": weather_primary.get("description", "").title(),
        "humidity": main_info.get("humidity", 0),
        "wind_speed": wind_speed_kmh,
        "wind_direction": wind_info.get("deg", 0),
        "visibility": visibility_km,
        "uv_index": 0.0,   # requires One Call API
        "aqi": aqi,
        "forecast": daily,
        "alert": alert,
    }


def _derive_local_alert(c: dict, wind_kmh: float) -> str | None:
    """Generate a simple IMD-style advisory from current conditions."""
    main_info = c.get("main", {})
    weather_list = c.get("weather") or [{}]
    weather_primary = weather_list[0] if weather_list else {}

    temp = main_info.get("temp", 25.0)
    hum  = main_info.get("humidity", 50)
    cond = weather_primary.get("main", "").lower()
    desc_str = weather_primary.get("description", "").lower()

    parts: list[str] = []
    if temp >= _ALERT_THRESHOLDS["temp_extreme_high"]:
        parts.append(f"🔴 RED ALERT — Severe Heat Wave: {temp:.0f}°C. Avoid outdoor activity.")
    elif temp >= 40:
        parts.append(f"🟠 ORANGE ALERT — Heat Wave: {temp:.0f}°C. Stay hydrated.")
    if temp <= _ALERT_THRESHOLDS["temp_extreme_low"]:
        parts.append(f"🔵 COLD WAVE WARNING: {temp:.0f}°C. Risk of frost.")
    if wind_kmh >= _ALERT_THRESHOLDS["wind_severe"]:
        parts.append(f"⚡ GALE WARNING: Wind {wind_kmh:.0f} km/h. Secure loose objects.")
    if "thunderstorm" in cond:
        parts.append("⛈️ THUNDERSTORM ALERT: Lightning risk. Stay indoors.")
    if "heavy" in desc_str:
        parts.append("🌧️ HEAVY RAINFALL WARNING: Waterlogging & flash flood risk.")

    return " | ".join(parts) if parts else None
