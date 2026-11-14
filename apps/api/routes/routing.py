"""
PENELOPE Backend - Safe Routing Endpoint (Part 4)
Computes flood-hazard-penalized routes across mountain road and trail graphs.
"""

from typing import Union, List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Body
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from apps.api.database import get_db
from apps.api.geospatial.routing import routing_engine

router = APIRouter(prefix="/routing", tags=["Routing"])


class SafeRouteRequest(BaseModel):
    from_location: Union[List[float], Dict[str, float]] = Field(
        ...,
        alias="from",
        description="Origin coordinates [lon, lat] or {'lat': ..., 'lon': ...}"
    )
    to_location: Union[List[float], Dict[str, float]] = Field(
        ...,
        alias="to",
        description="Destination coordinates [lon, lat] or {'lat': ..., 'lon': ...}"
    )
    region_id: Optional[str] = Field(None, description="Optional region catchment identifier")

    model_config = {
        "populate_by_name": True,
        "json_schema_extra": {
            "example": {
                "from": [79.5630, 30.5520],
                "to": [79.3242, 30.3753],
                "region_id": "optional-region-id"
            }
        }
    }


@router.post("/safe")
def calculate_safe_route(
    payload: SafeRouteRequest = Body(...),
    db: Session = Depends(get_db)
):
    """
    Computes optimal safe route between two coordinates, penalizing segments crossing
    active flash-flood hazard cells, submerged bridges, and low-lying riverbanks.
    Returns GeoJSON LineString route, risk exposure score, warnings, and nearest open shelter.
    """
    try:
        route = routing_engine.find_safe_route(
            db=db,
            from_coords=payload.from_location,
            to_coords=payload.to_location,
            region_id=payload.region_id
        )
        return route
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
