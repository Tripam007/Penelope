"""
PENELOPE Geospatial Risk Engine
"""

from apps.api.geospatial.mvt import build_mvt_tile, parse_and_validate_mvt, tile_to_bbox
from apps.api.geospatial.risk_engine import (
    compute_grid_cell_risk,
    get_grid_risk_geojson,
    rollup_location_risk,
    get_region_summary_stats,
    get_layer_geojson,
    compute_hillshade
)
from apps.api.geospatial.routing import routing_engine, SafeRoutingEngine
from apps.api.geospatial.events import risk_event_bus, stream_risk_sse

__all__ = [
    "build_mvt_tile",
    "parse_and_validate_mvt",
    "tile_to_bbox",
    "compute_grid_cell_risk",
    "get_grid_risk_geojson",
    "rollup_location_risk",
    "get_region_summary_stats",
    "get_layer_geojson",
    "compute_hillshade",
    "routing_engine",
    "SafeRoutingEngine",
    "risk_event_bus",
    "stream_risk_sse"
]
