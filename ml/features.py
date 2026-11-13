"""
PENELOPE ML Engine - Feature Engineering
Flash-flood feature extraction for hilly terrain (Himalayas & Western Ghats).
"""

from typing import Dict, List, Any
import numpy as np


FEATURE_NAMES = [
    "rain_1h_mm",
    "rain_3h_mm",
    "rain_6h_mm",
    "rain_24h_mm",
    "rain_peak_rate_mmh",
    "antecedent_precip_index_7d",
    "soil_moisture_surface_ratio",  # 0-1cm ratio to field capacity
    "soil_moisture_deep_ratio",     # 9-27cm
    "elevation_m",
    "slope_degrees",
    "river_discharge_m3s",
    "discharge_percentile_anomaly",
    "sensor_level_m",
    "sensor_rate_of_rise_mh",
    "sensor_danger_ratio",
]


def calculate_antecedent_precipitation_index(
    daily_rainfall: List[float],
    decay_constant: float = 0.85
) -> float:
    """
    Computes Antecedent Precipitation Index (API):
    API_t = sum_{i=1}^N (P_{t-i} * k^i)
    k = 0.80 - 0.90 typically for mountain watersheds.
    """
    if not daily_rainfall:
        return 0.0
    api = 0.0
    for day_idx, p in enumerate(reversed(daily_rainfall), start=1):
        api += float(p) * (decay_constant ** day_idx)
    return round(float(api), 3)


def calculate_slope_from_dem(
    elev_center: float,
    elev_north: float,
    elev_south: float,
    elev_east: float,
    elev_west: float,
    grid_spacing_m: float = 90.0
) -> float:
    """
    Horn's algorithm for slope gradient from digital elevation model points.
    Returns slope in degrees (0 - 90).
    """
    dz_dx = ((elev_east - elev_west) / (2.0 * grid_spacing_m))
    dz_dy = ((elev_north - elev_south) / (2.0 * grid_spacing_m))
    slope_rad = np.arctan(np.sqrt(dz_dx**2 + dz_dy**2))
    return round(float(np.degrees(slope_rad)), 2)


def extract_features_vector(raw_dict: Dict[str, Any]) -> List[float]:
    """
    Converts a telemetry dictionary into an ordered feature vector matching FEATURE_NAMES.
    """
    rain_1h = float(raw_dict.get("rain_1h_mm", 0.0))
    rain_3h = float(raw_dict.get("rain_3h_mm", rain_1h * 1.8))
    rain_6h = float(raw_dict.get("rain_6h_mm", rain_3h * 1.5))
    rain_24h = float(raw_dict.get("rain_24h_mm", rain_6h * 2.0))
    rain_peak = float(raw_dict.get("rain_peak_rate_mmh", rain_1h))

    # Soil moisture ratios (relative to saturation capacity ~0.45 m³/m³)
    sm_surf = float(raw_dict.get("soil_moisture_0_to_1cm", 0.25)) / 0.45
    sm_deep = float(raw_dict.get("soil_moisture_9_to_27cm", 0.28)) / 0.45

    api = float(raw_dict.get("antecedent_precip_index_7d", rain_24h * 0.75))
    elev = float(raw_dict.get("elevation_m", 1200.0))
    slope = float(raw_dict.get("slope_degrees", 22.0))

    discharge = float(raw_dict.get("river_discharge_m3s", 15.0))
    discharge_pct = float(raw_dict.get("discharge_percentile_anomaly", 0.50))

    sensor_level = float(raw_dict.get("sensor_level_m", 2.2))
    sensor_ror = float(raw_dict.get("sensor_rate_of_rise_mh", 0.05))
    danger_mark = float(raw_dict.get("sensor_danger_mark_m", 5.0))
    sensor_ratio = float(sensor_level / max(danger_mark, 0.1))

    return [
        max(0.0, rain_1h),
        max(0.0, rain_3h),
        max(0.0, rain_6h),
        max(0.0, rain_24h),
        max(0.0, rain_peak),
        max(0.0, api),
        min(1.0, max(0.0, sm_surf)),
        min(1.0, max(0.0, sm_deep)),
        max(0.0, elev),
        min(89.0, max(0.0, slope)),
        max(0.0, discharge),
        min(1.0, max(0.0, discharge_pct)),
        max(0.0, sensor_level),
        sensor_ror,
        min(2.5, max(0.0, sensor_ratio)),
    ]

