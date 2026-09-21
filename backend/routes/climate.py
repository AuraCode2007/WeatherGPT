from fastapi import APIRouter, HTTPException
from backend.models import ClimateRequest, ClimateResponse
from backend.services.climate_service import fetch_climate_data
from backend.services.llm_service import generate_climate_summary
from backend.utils.cache import get_cached, set_cached

router = APIRouter(prefix="/climate", tags=["Climate — Historical Analysis"])


@router.post("/", response_model=ClimateResponse, summary="Historical climate trend for a city/month")
async def get_climate(request: ClimateRequest):
    """
    Returns historical average temperature, humidity, and rainfall for a
    city in a specific month, along with an AI-generated trend summary.
    Data sourced from Open-Meteo Historical API (1940–present, free).
    """
    import datetime
    target_year = request.year or (datetime.date.today().year - 1)
    cache_key = f"climate:{request.city.lower()}:{request.month}:{target_year}"
    cached = get_cached(cache_key)
    if cached:
        return ClimateResponse(**cached)

    try:
        climate_data = fetch_climate_data(request.city, request.month, request.year)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Climate API error: {e}")

    try:
        trend_summary = generate_climate_summary(request.city, request.month, climate_data)
    except Exception:
        trend_summary = "Climate summary unavailable."

    result = ClimateResponse(
        city=climate_data["city"],
        month=climate_data["month"],
        avg_temp=climate_data["avg_temp"],
        avg_humidity=climate_data["avg_humidity"],
        avg_rainfall_mm=climate_data["avg_rainfall_mm"],
        trend_summary=trend_summary,
    )

    set_cached(cache_key, result.model_dump(), ttl=86400)  # cache 24 h
    return result
