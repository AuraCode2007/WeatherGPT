# pyrefly: ignore [missing-import]
from fastapi import APIRouter, HTTPException, Query
from backend.models import WeatherResponse
from backend.services.weather_service import fetch_weather
from backend.utils.cache import get_cached, set_cached

router = APIRouter(prefix="/weather", tags=["Weather — Real-time Data"])


@router.get("/", response_model=WeatherResponse, summary="Current weather + 5-day forecast")
async def get_weather(city: str = Query(..., description="City name (e.g. Mumbai, Delhi, Chennai)")):
    """
    Returns current conditions (temp, humidity, wind, AQI, visibility)
    plus a 5-day daily forecast and any derived IMD-style alerts.
    Data sourced from OpenWeatherMap.
    """
    cache_key = f"weather:{city.lower()}"
    cached = get_cached(cache_key)
    if cached:
        return WeatherResponse(**cached, source="cache")

    try:
        data = fetch_weather(city)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Weather API error: {e}")

    set_cached(cache_key, data, ttl=600)
    return WeatherResponse(**data, source="live")
