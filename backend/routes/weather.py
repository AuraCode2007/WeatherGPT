from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.orm import Session
from backend.models import WeatherResponse
from backend.services.weather_service import fetch_weather
from backend.services.db_service import save_weather_snapshot, get_weather_snapshots
from backend.db.init_db import get_db
from backend.utils.cache import get_cached, set_cached

router = APIRouter(prefix="/weather", tags=["Weather — Real-time Data"])


@router.get("/", response_model=WeatherResponse, summary="Current weather + 5-day forecast")
async def get_weather(
    city: str = Query(..., description="City name (e.g. Mumbai, Delhi, Chennai)"),
    db: Session = Depends(get_db)
):
    """
    Returns current conditions (temp, humidity, wind, AQI, visibility)
    plus a 5-day daily forecast and any derived IMD-style alerts.
    Data sourced from OpenWeatherMap and persisted to DB snapshot log.
    """
    cache_key = f"weather:{city.lower()}"
    cached = get_cached(cache_key)
    if cached:
        return WeatherResponse(**cached, source="cache")

    try:
        data = fetch_weather(city)
        try:
            save_weather_snapshot(db, data.get("city", city), data)
        except Exception as db_err:
            print(f"[DB] Weather snapshot error: {db_err}")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Weather API error: {e}")

    set_cached(cache_key, data, ttl=600)
    return WeatherResponse(**data, source="live")


@router.get("/history", summary="Get recent live weather snapshots from database")
async def get_weather_history(limit: int = 20, db: Session = Depends(get_db)):
    """Fetch recent live weather snapshots stored in database."""
    snapshots = get_weather_snapshots(db, limit=limit)
    return [
        {
            "id": s.id,
            "city": s.city,
            "temp": s.temp,
            "feels_like": s.feels_like,
            "humidity": s.humidity,
            "wind_speed": s.wind_speed,
            "condition": s.condition,
            "aqi": s.aqi,
            "recorded_at": s.recorded_at.isoformat() if s.recorded_at else None
        }
        for s in snapshots
    ]

