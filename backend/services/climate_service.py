"""
backend/services/climate_service.py
Historical climate analytics using Open-Meteo (free, no API key required).

Open-Meteo Historical API: https://open-meteo.com/en/docs/historical-weather-api
Covers 1940–present at 10km resolution globally.
"""
import requests
import statistics
from backend.config import OPENWEATHERMAP_API_KEY

OWM_GEO      = "http://api.openweathermap.org/geo/1.0/direct"
OPEN_METEO_H = "https://archive-api.open-meteo.com/v1/archive"

_OWM_PARAMS = {"appid": OPENWEATHERMAP_API_KEY}


def _get_coords(city: str) -> tuple[float, float]:
    resp = requests.get(OWM_GEO, params={**_OWM_PARAMS, "q": city, "limit": 1}, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    if not data:
        raise ValueError(f"City '{city}' not found.")
    return data[0]["lat"], data[0]["lon"]


def fetch_climate_data(city: str, month: int, year: int | None = None) -> dict:
    """
    Fetch historical daily climate averages for a city in a given month.
    Uses the most recent complete year for that month if year is not specified.
    Returns avg_temp, avg_humidity, avg_rainfall_mm.
    """
    import datetime
    lat, lon = _get_coords(city)

    target_year = year or (datetime.date.today().year - 1)
    start = f"{target_year}-{month:02d}-01"
    # last day of month
    import calendar
    last_day = calendar.monthrange(target_year, month)[1]
    end = f"{target_year}-{month:02d}-{last_day:02d}"

    resp = requests.get(
        OPEN_METEO_H,
        params={
            "latitude":  lat,
            "longitude": lon,
            "start_date": start,
            "end_date":   end,
            "daily": "temperature_2m_mean,relative_humidity_2m_mean,precipitation_sum",
            "timezone": "auto",
        },
        timeout=15,
    )
    resp.raise_for_status()
    data = resp.json().get("daily", {})

    temps  = [t for t in data.get("temperature_2m_mean", []) if t is not None]
    humids = [h for h in data.get("relative_humidity_2m_mean", []) if h is not None]
    rains  = [r for r in data.get("precipitation_sum", []) if r is not None]

    avg_temp     = round(statistics.mean(temps), 1)  if temps  else 0.0
    avg_humidity = round(statistics.mean(humids), 1) if humids else 0.0
    avg_rain     = round(sum(rains), 1)              if rains  else 0.0

    return {
        "city": city,
        "month": month,
        "year": target_year,
        "avg_temp": avg_temp,
        "avg_humidity": avg_humidity,
        "avg_rainfall_mm": avg_rain,
    }
