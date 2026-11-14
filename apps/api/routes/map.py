"""
PENELOPE Backend - Geospatial Vector Tiles & Map Layers (Part 4)
Supplies live 4-tier flash flood risk layers, MVT vector tiles with PostGIS ST_AsMVT / pure-Python
fallback, terrain hillshade, rainfall, river discharge anomalies, and evacuation paths.
"""

import hashlib
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, Query, Request, Response, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import select, text

from apps.api.database import get_db, active_db_url
from apps.api.models import Village, Sensor, Shelter, SensorReading, Basin, GridCell
from apps.api.geo_types import extract_lon_lat
from apps.api.geospatial.risk_engine import (
    get_grid_risk_geojson,
    get_layer_geojson,
    compute_grid_cell_risk
)
from apps.api.geospatial.mvt import (
    tile_to_bbox,
    build_mvt_tile,
    parse_and_validate_mvt
)
from apps.api.ingestion.resilience import cache as hybrid_cache

router = APIRouter(prefix="/map", tags=["Map"])


# ---------------------------------------------------------------------------
# 1. Vector Tiles / GeoJSON Grid Risk Endpoint
# ---------------------------------------------------------------------------

@router.get("/risk.geojson")
def get_risk_geojson(
    request: Request,
    response: Response,
    bbox: Optional[str] = Query(None, description="Bounding box in min_lon,min_lat,max_lon,max_lat"),
    horizon: str = Query("3h", description="Forecast horizon: now, 1h, 3h, 6h, 24h, 48h"),
    db: Session = Depends(get_db)
):
    """
    Returns GeoJSON FeatureCollection of flood risk grid cells for the requested horizon.
    Includes ETag generation and 304 Not Modified support.
    """
    geojson_data, etag = get_grid_risk_geojson(db=db, bbox=bbox, horizon=horizon)

    # Check conditional ETag
    if_none_match = request.headers.get("if-none-match")
    if if_none_match and if_none_match.strip() == etag:
        return Response(status_code=status.HTTP_304_NOT_MODIFIED)

    response.headers["ETag"] = etag
    response.headers["Cache-Control"] = "public, max-age=60"
    return geojson_data


@router.get("/tiles/{z}/{x}/{y}.mvt")
def get_risk_mvt_tile(
    z: int,
    x: int,
    y: int,
    request: Request,
    response: Response,
    horizon: str = Query("3h", description="Forecast horizon"),
    db: Session = Depends(get_db)
):
    """
    Returns Mapbox Vector Tile (MVT) protobuf bytes for grid risk.
    Uses native PostGIS ST_AsMVT when deployed on PostgreSQL, and a pure-Python
    vector tile encoder fallback for local dev/test suites.
    """
    cache_key = f"mvt:{z}:{x}:{y}:{horizon}"
    cached_tile = hybrid_cache.get(cache_key)

    min_lon, min_lat, max_lon, max_lat = tile_to_bbox(z, x, y)
    tile_bbox = (min_lon, min_lat, max_lon, max_lat)

    tile_bytes: Optional[bytes] = None

    if cached_tile and isinstance(cached_tile, dict) and "mvt_hex" in cached_tile:
        tile_bytes = bytes.fromhex(cached_tile["mvt_hex"])
        etag = cached_tile.get("etag")
    else:
        # 1. Try PostGIS ST_AsMVT if running on PostgreSQL
        if "postgresql" in active_db_url.lower():
            try:
                query = text("""
                    SELECT ST_AsMVT(tile, 'risk_grid', 4096, 'geom')
                    FROM (
                        SELECT
                            gc.id,
                            gc.elevation_m,
                            gc.slope_deg,
                            gc.twi,
                            ST_AsMVTGeom(
                                gc.geom,
                                ST_TileEnvelope(:z, :x, :y),
                                4096,
                                64,
                                true
                            ) AS geom
                        FROM grid_cells gc
                        WHERE gc.geom && ST_TileEnvelope(:z, :x, :y)
                    ) AS tile
                """)
                raw = db.execute(query, {"z": z, "x": x, "y": y}).scalar()
                if raw:
                    tile_bytes = bytes(raw)
            except Exception:
                tile_bytes = None

        # 2. Pure-Python MVT Encoder fallback
        if tile_bytes is None:
            # Query grid cells whose centroid falls within or near the tile bounding box
            cells = db.execute(select(GridCell)).scalars().all()
            features = []

            for c in cells:
                c_lon, c_lat = extract_lon_lat(c.centroid)
                # Check if cell is inside or near tile bounds (with small margin)
                margin = (max_lon - min_lon) * 0.1
                if (min_lon - margin <= c_lon <= max_lon + margin and
                        min_lat - margin <= c_lat <= max_lat + margin):
                    risk = compute_grid_cell_risk(c, horizon=horizon)
                    geom = c.geom if isinstance(c.geom, dict) else {
                        "type": "Point",
                        "coordinates": [c_lon, c_lat]
                    }
                    features.append({
                        "id": c.id,
                        "geometry": geom,
                        "properties": {
                            "risk_score": risk["risk_score"],
                            "risk_level": risk["risk_level"],
                            "elevation_m": c.elevation_m,
                            "slope_deg": c.slope_deg,
                            "twi": c.twi,
                            "dist_to_river_m": c.dist_to_river_m
                        }
                    })

            # If no cells intersect this tile, encode an empty layer tile
            tile_bytes = build_mvt_tile("risk_grid", features, tile_bbox, extent=4096)

        etag = f'"{hashlib.md5(tile_bytes).hexdigest()}"'
        hybrid_cache.set(cache_key, {"mvt_hex": tile_bytes.hex(), "etag": etag}, ttl_sec=90)

    # Check ETag conditional request
    if_none_match = request.headers.get("if-none-match")
    if if_none_match and if_none_match.strip() == etag:
        return Response(status_code=status.HTTP_304_NOT_MODIFIED)

    return Response(
        content=tile_bytes,
        media_type="application/vnd.mapbox-vector-tile",
        headers={
            "ETag": etag,
            "Cache-Control": "public, max-age=60"
        }
    )


# ---------------------------------------------------------------------------
# 2. Layers Catalog & Individual Layer GeoJSON
# ---------------------------------------------------------------------------

@router.get("/layers")
def list_map_layers():
    """
    Catalog of all available geospatial layers for the PENELOPE interactive map.
    """
    return {
        "platform": "PENELOPE",
        "layers": [
            {
                "id": "risk-heatmap",
                "name": "Live Flash-Flood Risk Heatmap",
                "type": "raster/vector-grid",
                "endpoint": "/map/risk.geojson",
                "tile_endpoint": "/map/tiles/{z}/{x}/{y}.mvt",
                "description": "Composite AI flash-flood hazard probability surface (0.0 to 1.0)",
                "horizons": ["now", "1h", "3h", "6h", "24h", "48h"]
            },
            {
                "id": "terrain",
                "name": "Mountain Terrain & Hillshade",
                "type": "hillshade",
                "endpoint": "/map/layers/terrain",
                "description": "DEM elevation and cartographic hillshade illumination (0-255)"
            },
            {
                "id": "rainfall",
                "name": "Precipitation & Forecast",
                "type": "point",
                "endpoint": "/map/layers/rainfall",
                "description": "Latest 1h/3h rain observations and 24h/48h accumulated forecasts"
            },
            {
                "id": "river-network",
                "name": "River Network & Discharge Anomaly",
                "type": "line/point",
                "endpoint": "/map/layers/river-network",
                "description": "River channels, sensor stations, water levels, and discharge anomalies"
            },
            {
                "id": "locations",
                "name": "Settlements & Vulnerable Assets",
                "type": "point",
                "endpoint": "/map/layers/locations",
                "description": "Villages, towns, tourist spots, suspension bridges, and trek routes"
            },
            {
                "id": "shelters",
                "name": "Designated Evacuation Shelters",
                "type": "point",
                "endpoint": "/map/layers/shelters",
                "description": "Relief camps, capacity, high-ground elevation, and contact points"
            }
        ]
    }


@router.get("/layers/{layer_name}")
def get_layer_data(layer_name: str, db: Session = Depends(get_db)):
    """
    Returns GeoJSON FeatureCollection for a specific layer.
    """
    valid_layers = ["risk-heatmap", "risk", "terrain", "rainfall", "river-network", "rivers", "locations", "villages", "shelters"]
    if layer_name not in valid_layers:
        raise HTTPException(
            status_code=404,
            detail=f"Layer '{layer_name}' not found. Available layers: {valid_layers}"
        )
    return get_layer_geojson(layer_name, db)


# ---------------------------------------------------------------------------
# 3. Backward-Compatible MapLibre Unified GeoJSON
# ---------------------------------------------------------------------------

@router.get("/geojson")
def get_map_geojson_layers(db: Session = Depends(get_db)):
    """
    Returns unified GeoJSON FeatureCollection for MapLibre GL JS frontend.
    """
    features = []

    villages = db.execute(select(Village)).scalars().all()
    for v in villages:
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [v.lon, v.lat]
            },
            "properties": {
                "layer_type": "village",
                "id": v.id,
                "name": v.name,
                "hindi_name": v.hindi_name,
                "risk_score": v.current_risk_score,
                "risk_level": v.current_risk_level,
                "population": v.population,
                "elevation_m": v.elevation_m,
                "slope_degrees": v.slope_degrees,
                "river_distance_m": v.river_distance_m,
                "safe_shelter_id": v.safe_shelter_id,
            }
        })

    sensors = db.execute(select(Sensor)).scalars().all()
    for s in sensors:
        latest_reading = (
            db.execute(
                select(SensorReading)
                .where(SensorReading.sensor_id == s.id)
                .order_by(SensorReading.timestamp.desc())
                .limit(1)
            )
            .scalars()
            .first()
        )
        water_level = latest_reading.water_level_m if latest_reading else 1.5
        reading_source = latest_reading.source if latest_reading else ("simulated" if s.is_simulated else "live")
        danger_ratio = round(water_level / max(s.danger_level_m, 0.1), 2)

        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [s.lon, s.lat]
            },
            "properties": {
                "layer_type": "sensor",
                "id": s.id,
                "sensor_code": s.sensor_code,
                "name": s.name,
                "river_name": s.river_name,
                "water_level_m": water_level,
                "warning_level_m": s.warning_level_m,
                "danger_level_m": s.danger_level_m,
                "danger_ratio": danger_ratio,
                "is_simulated": s.is_simulated,
                "source": reading_source,
                "status": s.status,
            }
        })

    shelters = db.execute(select(Shelter)).scalars().all()
    shelter_map = {}
    for sh in shelters:
        shelter_map[sh.id] = sh
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [sh.lon, sh.lat]
            },
            "properties": {
                "layer_type": "shelter",
                "id": sh.id,
                "name": sh.name,
                "hindi_name": sh.hindi_name,
                "capacity": sh.capacity_persons,
                "elevation_m": sh.elevation_m,
                "contact_person": sh.contact_person,
                "contact_phone": sh.contact_phone,
                "status": sh.status,
            }
        })

    for v in villages:
        if v.safe_shelter_id and v.safe_shelter_id in shelter_map:
            sh = shelter_map[v.safe_shelter_id]
            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": [
                        [v.lon, v.lat],
                        [sh.lon, sh.lat]
                    ]
                },
                "properties": {
                    "layer_type": "evacuation_route",
                    "village_id": v.id,
                    "village_name": v.name,
                    "shelter_name": sh.name,
                    "risk_level": v.current_risk_level,
                    "elev_gain_m": round(sh.elevation_m - v.elevation_m, 1)
                }
            })

    return {
        "type": "FeatureCollection",
        "features": features
    }
