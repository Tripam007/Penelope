"""
PENELOPE Geospatial Risk Engine - Mapbox Vector Tile (MVT) Encoder & Validator
Encodes geometry and risk features into standard Mapbox Vector Tile (MVT / Protobuf) bytes,
with support for PostGIS ST_AsMVT when available and a pure-Python fallback encoder.
Specification: Mapbox Vector Tile 2.1 (vector_tile.proto).
"""

import math
import struct
from typing import List, Dict, Any, Tuple, Optional, Union


# ---------------------------------------------------------------------------
# Tile Math Helpers
# ---------------------------------------------------------------------------

def tile_to_bbox(z: int, x: int, y: int) -> Tuple[float, float, float, float]:
    """
    Returns (min_lon, min_lat, max_lon, max_lat) for a standard Web Mercator tile (z, x, y).
    """
    n = 2.0 ** z
    min_lon = x / n * 360.0 - 180.0
    max_lon = (x + 1) / n * 360.0 - 180.0
    lat_rad_max = math.atan(math.sinh(math.pi * (1.0 - 2.0 * y / n)))
    lat_rad_min = math.atan(math.sinh(math.pi * (1.0 - 2.0 * (y + 1) / n)))
    max_lat = math.degrees(lat_rad_max)
    min_lat = math.degrees(lat_rad_min)
    return min_lon, min_lat, max_lon, max_lat


def point_to_tile_coords(
    lon: float, lat: float,
    min_lon: float, min_lat: float, max_lon: float, max_lat: float,
    extent: int = 4096
) -> Tuple[int, int]:
    """
    Projects WGS84 (lon, lat) to tile coordinate space [0, extent].
    Tile Y is 0 at top (north) and extent at bottom (south).
    """
    lon_range = max(max_lon - min_lon, 1e-9)
    lat_range = max(max_lat - min_lat, 1e-9)
    px = int(round((lon - min_lon) / lon_range * extent))
    py = int(round((max_lat - lat) / lat_range * extent))
    px = max(0, min(extent, px))
    py = max(0, min(extent, py))
    return px, py


# ---------------------------------------------------------------------------
# Protobuf Low-Level Wire Encoding Helpers
# ---------------------------------------------------------------------------

def encode_varint(value: int) -> bytes:
    """Encode an integer as a protobuf varint."""
    if value < 0:
        value = (1 << 64) + value
    buf = bytearray()
    while value >= 0x80:
        buf.append((value & 0x7F) | 0x80)
        value >>= 7
    buf.append(value & 0x7F)
    return bytes(buf)


def decode_varint(data: bytes, pos: int) -> Tuple[int, int]:
    """Decode a protobuf varint starting at pos. Returns (value, new_pos)."""
    res = 0
    shift = 0
    while pos < len(data):
        b = data[pos]
        pos += 1
        res |= (b & 0x7F) << shift
        if not (b & 0x80):
            break
        shift += 7
    return res, pos


def encode_zigzag(n: int) -> int:
    """ZigZag encode a signed 32-bit int."""
    return (n << 1) ^ (n >> 31)


def decode_zigzag(n: int) -> int:
    """Decode a zigzag encoded integer."""
    return (n >> 1) ^ (-(n & 1))


def encode_tag(field_number: int, wire_type: int) -> bytes:
    return encode_varint((field_number << 3) | wire_type)


def encode_length_delimited(field_number: int, data: bytes) -> bytes:
    return encode_tag(field_number, 2) + encode_varint(len(data)) + data


def encode_string(field_number: int, text: str) -> bytes:
    data = text.encode("utf-8")
    return encode_length_delimited(field_number, data)


def encode_uint32(field_number: int, val: int) -> bytes:
    return encode_tag(field_number, 0) + encode_varint(val)


def encode_uint64(field_number: int, val: int) -> bytes:
    return encode_tag(field_number, 0) + encode_varint(val)


def encode_float(field_number: int, val: float) -> bytes:
    data = struct.pack("<f", float(val))
    return encode_tag(field_number, 5) + data


def encode_double(field_number: int, val: float) -> bytes:
    data = struct.pack("<d", float(val))
    return encode_tag(field_number, 1) + data


# ---------------------------------------------------------------------------
# MVT Value & Feature Encoder
# ---------------------------------------------------------------------------

def encode_mvt_value(val: Any) -> bytes:
    """
    Encode an MVT Value message:
    1: string_value
    2: float_value
    3: double_value
    4: int_value
    5: uint_value
    6: sint_value
    7: bool_value
    """
    if isinstance(val, bool):
        return encode_tag(7, 0) + (b"\x01" if val else b"\x00")
    elif isinstance(val, int):
        return encode_tag(4, 0) + encode_varint(val)
    elif isinstance(val, float):
        return encode_double(3, val)
    elif isinstance(val, str):
        return encode_string(1, val)
    else:
        return encode_string(1, str(val))


def encode_mvt_geometry(geom_type: str, coordinates: Any, bbox: Tuple[float, float, float, float], extent: int = 4096) -> Tuple[int, bytes]:
    """
    Encodes geometry to MVT commands (MoveTo=1, LineTo=2, ClosePath=7) with zigzag deltas.
    Returns (geom_type_enum, packed_geometry_bytes).
    GeomType enum: 1=POINT, 2=LINESTRING, 3=POLYGON.
    """
    min_lon, min_lat, max_lon, max_lat = bbox
    packed_cmds: List[int] = []

    def command(cmd_id: int, count: int) -> int:
        return (cmd_id & 0x7) | (count << 3)

    cur_x, cur_y = 0, 0

    if geom_type.upper() == "POINT":
        lon, lat = coordinates[0], coordinates[1]
        px, py = point_to_tile_coords(lon, lat, min_lon, min_lat, max_lon, max_lat, extent)
        dx = px - cur_x
        dy = py - cur_y
        packed_cmds.append(command(1, 1))  # MoveTo(1)
        packed_cmds.append(encode_zigzag(dx))
        packed_cmds.append(encode_zigzag(dy))
        type_enum = 1

    elif geom_type.upper() in ("LINESTRING", "MULTILINESTRING"):
        lines = [coordinates] if geom_type.upper() == "LINESTRING" else coordinates
        type_enum = 2
        for line in lines:
            if not line:
                continue
            # MoveTo first point
            px, py = point_to_tile_coords(line[0][0], line[0][1], min_lon, min_lat, max_lon, max_lat, extent)
            packed_cmds.append(command(1, 1))
            packed_cmds.append(encode_zigzag(px - cur_x))
            packed_cmds.append(encode_zigzag(py - cur_y))
            cur_x, cur_y = px, py

            # LineTo remaining points
            if len(line) > 1:
                packed_cmds.append(command(2, len(line) - 1))
                for pt in line[1:]:
                    px, py = point_to_tile_coords(pt[0], pt[1], min_lon, min_lat, max_lon, max_lat, extent)
                    packed_cmds.append(encode_zigzag(px - cur_x))
                    packed_cmds.append(encode_zigzag(py - cur_y))
                    cur_x, cur_y = px, py

    elif geom_type.upper() in ("POLYGON", "MULTIPOLYGON"):
        polys = [coordinates] if geom_type.upper() == "POLYGON" else coordinates
        type_enum = 3
        for poly in polys:
            for ring in poly:
                if len(ring) < 3:
                    continue
                # MoveTo ring[0]
                px, py = point_to_tile_coords(ring[0][0], ring[0][1], min_lon, min_lat, max_lon, max_lat, extent)
                packed_cmds.append(command(1, 1))
                packed_cmds.append(encode_zigzag(px - cur_x))
                packed_cmds.append(encode_zigzag(py - cur_y))
                cur_x, cur_y = px, py

                # LineTo ring[1:-1]
                ring_pts = ring[1:-1] if ring[0] == ring[-1] else ring[1:]
                if ring_pts:
                    packed_cmds.append(command(2, len(ring_pts)))
                    for pt in ring_pts:
                        px, py = point_to_tile_coords(pt[0], pt[1], min_lon, min_lat, max_lon, max_lat, extent)
                        packed_cmds.append(encode_zigzag(px - cur_x))
                        packed_cmds.append(encode_zigzag(py - cur_y))
                        cur_x, cur_y = px, py

                # ClosePath
                packed_cmds.append(command(7, 1))
    else:
        type_enum = 0

    geom_bytes = bytearray()
    for cmd in packed_cmds:
        geom_bytes.extend(encode_varint(cmd))
    return type_enum, bytes(geom_bytes)


# ---------------------------------------------------------------------------
# High-Level MVT Tile Builder
# ---------------------------------------------------------------------------

def build_mvt_tile(
    layer_name: str,
    features: List[Dict[str, Any]],
    bbox: Tuple[float, float, float, float],
    extent: int = 4096
) -> bytes:
    """
    Builds a complete Mapbox Vector Tile binary from GeoJSON-like features.
    features: List of dicts with 'id', 'geometry' {'type': '...', 'coordinates': ...}, and 'properties'.
    """
    keys: List[str] = []
    key_map: Dict[str, int] = {}
    values: List[Any] = []
    value_map: Dict[Any, int] = {}

    def get_key_idx(k: str) -> int:
        if k not in key_map:
            key_map[k] = len(keys)
            keys.append(k)
        return key_map[k]

    def get_val_idx(v: Any) -> int:
        if isinstance(v, (dict, list)):
            import json
            v = json.dumps(v)
        val_key = (type(v), v)
        if val_key not in value_map:
            value_map[val_key] = len(values)
            values.append(v)
        return value_map[val_key]

    encoded_features: List[bytes] = []

    for idx, feat in enumerate(features):
        feat_id = feat.get("id", idx + 1)
        if isinstance(feat_id, str):
            # numeric hash for protobuf uint64
            feat_id = abs(hash(feat_id)) % (1 << 53)

        geom = feat.get("geometry", {})
        geom_type = geom.get("type", "Point")
        coords = geom.get("coordinates", [0.0, 0.0])

        type_enum, geom_bytes = encode_mvt_geometry(geom_type, coords, bbox, extent)
        if not geom_bytes:
            continue

        # Tag indices (pairs of key_idx, val_idx)
        tag_bytes = bytearray()
        props = feat.get("properties", {})
        for k, v in props.items():
            if v is None:
                continue
            k_idx = get_key_idx(str(k))
            v_idx = get_val_idx(v)
            tag_bytes.extend(encode_varint(k_idx))
            tag_bytes.extend(encode_varint(v_idx))

        # Feature message:
        # 1: id (uint64)
        # 2: tags (packed uint32)
        # 3: type (enum)
        # 4: geometry (packed uint32)
        f_buf = bytearray()
        f_buf.extend(encode_uint64(1, feat_id))
        if tag_bytes:
            f_buf.extend(encode_length_delimited(2, bytes(tag_bytes)))
        f_buf.extend(encode_uint32(3, type_enum))
        f_buf.extend(encode_length_delimited(4, geom_bytes))

        encoded_features.append(bytes(f_buf))

    # Layer message:
    # 15: version = 2
    # 1: name = layer_name
    # 2: features (repeated)
    # 3: keys (repeated)
    # 4: values (repeated)
    # 5: extent = 4096
    layer_buf = bytearray()
    layer_buf.extend(encode_uint32(15, 2))
    layer_buf.extend(encode_string(1, layer_name))

    for ef in encoded_features:
        layer_buf.extend(encode_length_delimited(2, ef))

    for k in keys:
        layer_buf.extend(encode_string(3, k))

    for v in values:
        v_bytes = encode_mvt_value(v)
        layer_buf.extend(encode_length_delimited(4, v_bytes))

    layer_buf.extend(encode_uint32(5, extent))

    # Tile message:
    # 3: layers (repeated Layer)
    tile_buf = bytearray()
    tile_buf.extend(encode_length_delimited(3, bytes(layer_buf)))
    return bytes(tile_buf)


# ---------------------------------------------------------------------------
# MVT Validator / Parser (For Testing & Verification)
# ---------------------------------------------------------------------------

def parse_and_validate_mvt(data: bytes) -> Dict[str, Any]:
    """
    Parses and validates MVT binary protobuf bytes.
    Returns a dictionary of parsed layers, features, keys, values, and extent.
    Raises ValueError on malformed vector tile.
    """
    if not data or len(data) < 3:
        raise ValueError("Invalid MVT data: buffer too short.")

    pos = 0
    layers = []

    while pos < len(data):
        tag, pos = decode_varint(data, pos)
        field_num = tag >> 3
        wire_type = tag & 0x7

        if field_num == 3 and wire_type == 2:  # Layer
            length, pos = decode_varint(data, pos)
            layer_data = data[pos:pos + length]
            pos += length

            layer_info = _parse_layer(layer_data)
            layers.append(layer_info)
        else:
            # Skip unknown field
            pos = _skip_field(data, pos, wire_type)

    if not layers:
        raise ValueError("No layers found in MVT tile.")

    return {
        "valid": True,
        "layer_count": len(layers),
        "layers": layers
    }


def _parse_layer(data: bytes) -> Dict[str, Any]:
    pos = 0
    name = ""
    version = 2
    extent = 4096
    keys = []
    values = []
    features_count = 0

    while pos < len(data):
        tag, pos = decode_varint(data, pos)
        field_num = tag >> 3
        wire_type = tag & 0x7

        if field_num == 1 and wire_type == 2:
            length, pos = decode_varint(data, pos)
            name = data[pos:pos + length].decode("utf-8", errors="ignore")
            pos += length
        elif field_num == 15 and wire_type == 0:
            version, pos = decode_varint(data, pos)
        elif field_num == 5 and wire_type == 0:
            extent, pos = decode_varint(data, pos)
        elif field_num == 3 and wire_type == 2:
            length, pos = decode_varint(data, pos)
            keys.append(data[pos:pos + length].decode("utf-8", errors="ignore"))
            pos += length
        elif field_num == 4 and wire_type == 2:
            length, pos = decode_varint(data, pos)
            values.append(data[pos:pos + length])
            pos += length
        elif field_num == 2 and wire_type == 2:
            length, pos = decode_varint(data, pos)
            pos += length
            features_count += 1
        else:
            pos = _skip_field(data, pos, wire_type)

    return {
        "name": name,
        "version": version,
        "extent": extent,
        "keys": keys,
        "values_count": len(values),
        "features_count": features_count
    }


def _skip_field(data: bytes, pos: int, wire_type: int) -> int:
    if wire_type == 0:
        _, pos = decode_varint(data, pos)
    elif wire_type == 1:
        pos += 8
    elif wire_type == 2:
        length, pos = decode_varint(data, pos)
        pos += length
    elif wire_type == 5:
        pos += 4
    else:
        pos = len(data)  # stop
    return pos
