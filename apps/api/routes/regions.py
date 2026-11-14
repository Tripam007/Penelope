"""
PENELOPE Backend - Region Catchment Summaries (Part 4)
Returns live aggregate flood metrics, population at risk, trends, and top causal drivers.
"""

from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select

from apps.api.database import get_db
from apps.api.models import Region
from apps.api.geospatial.risk_engine import get_region_summary_stats

router = APIRouter(prefix="/regions", tags=["Regions"])


@router.get("")
def list_regions(db: Session = Depends(get_db)):
    """
    Lists all monitored mountain regions and basins.
    """
    regions = db.execute(select(Region)).scalars().all()
    return [
        {
            "id": r.id,
            "name": r.name,
            "state": r.state,
            "center_lat": r.center_lat,
            "center_lon": r.center_lon,
            "locations_count": len(r.locations) if r.locations else 0
        }
        for r in regions
    ]


@router.get("/{region_id}/summary")
def get_region_summary(region_id: str, db: Session = Depends(get_db)):
    """
    Returns high-level flood risk intelligence summary for a region:
    counts (villages, at-risk villages, population at risk, live alerts),
    trend (rising, stable, falling), top drivers, and last update timestamp.
    """
    summary = get_region_summary_stats(region_id, db)
    if "error" in summary:
        raise HTTPException(status_code=404, detail=summary["error"])
    return summary
