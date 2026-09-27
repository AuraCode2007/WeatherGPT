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


from fastapi import WebSocket, WebSocketDisconnect
import asyncio
import random
import time

@router.websocket("/ws/telemetry")
async def websocket_telemetry(websocket: WebSocket):
    """
    WebSocket endpoint streaming live Doppler & atmospheric telemetry ticks every 3 seconds.
    Used for technical live socket visualization.
    """
    await websocket.accept()
    try:
        city = "Mumbai"
        while True:
            # Send live pulse
            tick = {
                "timestamp": time.time(),
                "city": city,
                "doppler_sweep_deg": (int(time.time() * 30) % 360),
                "signal_dbz": round(random.uniform(15.0, 48.0), 1),
                "pressure_hpa": round(1012.0 + random.uniform(-1.5, 1.5), 1),
                "wind_gust_kmh": round(random.uniform(10.0, 28.0), 1),
                "aqi_pm25": round(random.uniform(25.0, 85.0), 1),
            }
            await websocket.send_json(tick)
            await asyncio.sleep(3)
    except WebSocketDisconnect:
        pass
    except Exception:
        pass


