"""
PENELOPE Backend - Alerts & Authority Incident Management Endpoints (Hard Rules 4 & 8)
"""

from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import select

from apps.api.database import get_db
from apps.api.models import Alert, AlertDelivery, Basin, Village
from apps.api.schemas import AlertResponse, ManualAlertTriggerRequest
from apps.api.alerts.dispatcher import alert_dispatcher

router = APIRouter(prefix="/alerts", tags=["Alerts"])


@router.get("", response_model=List[AlertResponse])
def list_alerts(
    basin_id: Optional[str] = None,
    severity: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    stmt = select(Alert).order_by(Alert.triggered_at.desc()).limit(limit)
    if basin_id:
        stmt = stmt.where(Alert.basin_id == basin_id)
    if severity:
        stmt = stmt.where(Alert.severity == severity)
    if status:
        stmt = stmt.where(Alert.status == status)

    alerts = db.execute(stmt).scalars().all()
    return alerts


@router.get("/active", response_model=List[AlertResponse])
def list_active_alerts(db: Session = Depends(get_db)):
    stmt = select(Alert).where(Alert.status == "Active").order_by(Alert.triggered_at.desc())
    alerts = db.execute(stmt).scalars().all()
    return alerts


@router.post("/trigger", response_model=AlertResponse)
def trigger_manual_alert(payload: ManualAlertTriggerRequest, db: Session = Depends(get_db)):
    """
    Authority command endpoint to issue an emergency flash-flood advisory.
    Dispatches across requested channels (SMS, Telegram, Email, Webhook, Push)
    and stores delivery success/failure/skipped status per recipient.
    """
    basin = db.execute(select(Basin).where(Basin.id == payload.basin_id)).scalars().first()
    if not basin:
        raise HTTPException(status_code=404, detail="Basin not found")

    alert = Alert(
        basin_id=payload.basin_id,
        village_id=payload.village_id,
        severity=payload.severity,
        title=payload.title,
        title_hi=payload.title_hi,
        message=payload.message,
        message_hi=payload.message_hi,
        risk_score=0.92 if payload.severity == "Very High" else (0.70 if payload.severity == "High" else 0.40),
        triggered_at=datetime.utcnow(),
        status="Active"
    )
    db.add(alert)
    db.flush()

    # Dispatch across requested channels
    alert_dispatcher.dispatch_alert(db, alert, channels=payload.channels)

    db.refresh(alert)
    return alert


@router.post("/{alert_id}/resolve")
def resolve_alert(alert_id: str, db: Session = Depends(get_db)):
    alert = db.execute(select(Alert).where(Alert.id == alert_id)).scalars().first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    alert.status = "Resolved"
    db.commit()
    return {"status": "resolved", "alert_id": alert_id}

