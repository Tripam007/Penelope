"""
PENELOPE Backend - PostGIS & Geospatial Type Abstractions
Provides native PostGIS GEOMETRY types in PostgreSQL while supporting
graceful SQLite fallback for local test/dev suites without PostGIS daemon.
"""

import json
from typing import Any, Optional, Dict, Tuple
from sqlalchemy.types import TypeDecorator, UserDefinedType, TEXT
from sqlalchemy.dialects.postgresql import dialect as pg_dialect


class Geometry(TypeDecorator):
    """
    Geospatial Geometry Type that compiles to native PostGIS GEOMETRY(geometry_type, srid)
    in PostgreSQL / PostGIS, and TEXT (GeoJSON/WKT) in SQLite.
    """
    impl = TEXT
    cache_ok = True

    def __init__(self, geometry_type: str = "GEOMETRY", srid: int = 4326, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry_type = geometry_type.upper()
        self.srid = srid

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            # Native PostGIS geometry column type definition
            return dialect.type_descriptor(UserDefinedType())
        return dialect.type_descriptor(TEXT())

    def process_bind_param(self, value: Any, dialect) -> Optional[str]:
        if value is None:
            return None
        if isinstance(value, dict):
            return json.dumps(value)
        if isinstance(value, (list, tuple)):
            # [lon, lat] point shorthand
            if len(value) == 2:
                return json.dumps({"type": "Point", "coordinates": [float(value[0]), float(value[1])]})
        return str(value)

    def process_result_value(self, value: Any, dialect) -> Optional[Any]:
        if value is None:
            return None
        if isinstance(value, str):
            try:
                # If it's stored as GeoJSON string
                if value.startswith("{"):
                    return json.loads(value)
            except Exception:
                pass
            return value
        return value


class PointGeometry(Geometry):
    def __init__(self, srid: int = 4326):
        super().__init__(geometry_type="POINT", srid=srid)


class PolygonGeometry(Geometry):
    def __init__(self, srid: int = 4326):
        super().__init__(geometry_type="POLYGON", srid=srid)


class MultiPolygonGeometry(Geometry):
    def __init__(self, srid: int = 4326):
        super().__init__(geometry_type="MULTIPOLYGON", srid=srid)


def make_point_geojson(lon: float, lat: float) -> Dict[str, Any]:
    """Return standard GeoJSON Point object."""
    return {
        "type": "Point",
        "coordinates": [round(float(lon), 6), round(float(lat), 6)]
    }


def make_polygon_geojson(coordinates: list) -> Dict[str, Any]:
    """Return standard GeoJSON Polygon object."""
    return {
        "type": "Polygon",
        "coordinates": coordinates
    }


def make_multipolygon_geojson(coordinates: list) -> Dict[str, Any]:
    """Return standard GeoJSON MultiPolygon object."""
    return {
        "type": "MultiPolygon",
        "coordinates": coordinates
    }


def extract_lon_lat(geom: Any) -> Tuple[float, float]:
    """Extract (lon, lat) tuple from GeoJSON dict, list, or WKT string."""
    if isinstance(geom, dict):
        coords = geom.get("coordinates", [0.0, 0.0])
        return float(coords[0]), float(coords[1])
    if isinstance(geom, (list, tuple)) and len(geom) >= 2:
        return float(geom[0]), float(geom[1])
    if isinstance(geom, str):
        if geom.startswith("{"):
            try:
                parsed = json.loads(geom)
                return extract_lon_lat(parsed)
            except Exception:
                pass
        # Handle WKT e.g. "POINT(79.5442 30.5543)"
        if "POINT" in geom.upper():
            inner = geom.split("(")[1].split(")")[0].strip()
            parts = inner.split()
            if len(parts) >= 2:
                return float(parts[0]), float(parts[1])
    return 0.0, 0.0

