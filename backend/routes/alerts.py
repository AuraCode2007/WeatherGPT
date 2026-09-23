from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.orm import Session
from backend.models import AlertResponse
from backend.services.alert_service import get_alerts_for_city, get_alert_summary
from backend.services.db_service import save_alert_log, get_alert_logs
from backend.db.init_db import get_db

router = APIRouter(prefix="/alerts", tags=["Alerts — Early Warning System"])


@router.get("/", response_model=AlertResponse, summary="Active weather alerts & early warnings")
async def get_alerts(
    city: str = Query(..., description="City name to check for active alerts"),
    db: Session = Depends(get_db)
):
    """
    Returns active extreme weather alerts for the specified city.
    Sourced from OWM One Call API with IMD-style severity classification.
    Returns an empty alerts list when no warnings are active and logs alerts to DB.
    """
    try:
        alerts = get_alerts_for_city(city)
        summary = get_alert_summary(alerts)
        if alerts:
            for a in alerts:
                try:
                    save_alert_log(db, city, a.model_dump())
                except Exception as db_err:
                    print(f"[DB] Alert log error: {db_err}")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Alert service error: {e}")

    return AlertResponse(location=city, alerts=alerts, summary=summary)


@router.get("/history", summary="Get recorded weather alerts from database")
async def get_alerts_history(limit: int = 20, db: Session = Depends(get_db)):
    """Fetch recorded extreme weather alert logs stored in database."""
    logs = get_alert_logs(db, limit=limit)
    return [
        {
            "id": log.id,
            "city": log.city,
            "event": log.event,
            "severity": log.severity,
            "description": log.description,
            "fetched_at": log.fetched_at.isoformat() if log.fetched_at else None
        }
        for log in logs
    ]

