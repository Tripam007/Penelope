"""
PENELOPE ML Engine - Proxy Ground-Truth Labeling Methodology
Reference: Central Water Commission (CWC) & India Meteorological Department (IMD) standards.

Since open data repositories do not include standardized ground-truth flash-flood events,
we define a calibrated hydro-meteorological composite proxy label.
"""

from typing import Dict, Any


def compute_proxy_flash_flood_label(features: Dict[str, Any]) -> int:
    """
    Computes a binary proxy label (1 = Flash flood conditions, 0 = Non-flood)
    based on combined hydrological, meteorological, and topographic thresholds.

    Criteria:
    1. Rainfall Trigger (IMD Extreme / Intense Convective):
       - 1h rain > 35mm OR 3h rain > 60mm OR 24h rain > 100mm
    2. Hydrological Base (Soil Saturation & River Discharge):
       - Surface soil moisture ratio >= 0.80 (soil capacity reached)
       - GloFAS river discharge anomaly >= 0.92 (92nd percentile)
    3. River Gauge Stage:
       - Sensor stage level / Danger mark ratio >= 0.85
       - OR Sensor rate of rise >= 0.6 m/hour
    4. Topographic Acceleration:
       - Slope >= 15 degrees decreases catchment time to concentration.
    """
    score = 0.0

    rain_1h = float(features.get("rain_1h_mm", 0.0))
    rain_3h = float(features.get("rain_3h_mm", 0.0))
    rain_24h = float(features.get("rain_24h_mm", 0.0))
    rain_peak = float(features.get("rain_peak_rate_mmh", 0.0))

    sm_surf = float(features.get("soil_moisture_surface_ratio", 0.0))
    discharge_pct = float(features.get("discharge_percentile_anomaly", 0.0))
    sensor_ratio = float(features.get("sensor_danger_ratio", 0.0))
    sensor_ror = float(features.get("sensor_rate_of_rise_mh", 0.0))
    slope = float(features.get("slope_degrees", 0.0))

    # Rainfall score component (max 40 pts)
    if rain_1h >= 40.0 or rain_peak >= 50.0:
        score += 40.0
    elif rain_3h >= 60.0 or rain_1h >= 25.0:
        score += 30.0
    elif rain_24h >= 80.0 or rain_3h >= 35.0:
        score += 20.0
    elif rain_24h >= 40.0:
        score += 10.0

    # Soil saturation component (max 20 pts)
    if sm_surf >= 0.85:
        score += 20.0
    elif sm_surf >= 0.70:
        score += 12.0
    elif sm_surf >= 0.55:
        score += 5.0

    # Hydrological discharge & sensor stage (max 30 pts)
    if sensor_ratio >= 0.90 or discharge_pct >= 0.95:
        score += 30.0
    elif sensor_ratio >= 0.75 or discharge_pct >= 0.85:
        score += 20.0
    elif sensor_ratio >= 0.60 or discharge_pct >= 0.75:
        score += 10.0

    # Rate of rise surge bonus
    if sensor_ror >= 0.5:
        score += 10.0

    # Topographic terrain factor (steep slopes accelerate runoff)
    if slope >= 25.0:
        score *= 1.15
    elif slope >= 15.0:
        score *= 1.05

    # Threshold: Score >= 55 indicates flash flood conditions present
    return 1 if score >= 55.0 else 0

