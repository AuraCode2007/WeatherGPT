from fastapi import APIRouter, HTTPException, Query
from backend.models import AlertResponse
from backend.services.alert_service import get_alerts_for_city, get_alert_summary

router = APIRouter(prefix="/alerts", tags=["Alerts — Early Warning System"])


@router.get("/", response_model=AlertResponse, summary="Active weather alerts & early warnings")
async def get_alerts(city: str = Query(..., description="City name to check for active alerts")):
    """
    Returns active extreme weather alerts for the specified city.
    Sourced from OWM One Call API (requires paid plan) with
    IMD-style severity classification (Minor / Moderate / Severe / Extreme).
    Returns an empty alerts list (not an error) when no warnings are active.
    """
    try:
        alerts = get_alerts_for_city(city)
        summary = get_alert_summary(alerts)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Alert service error: {e}")

    return AlertResponse(location=city, alerts=alerts, summary=summary)
