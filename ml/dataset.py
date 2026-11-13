"""
PENELOPE ML Engine - Training Dataset Generation
Generates synthetic and semi-empirical historical meteorological/hydrological sequences
calibrated for Himalayan and Western Ghats basins using pure NumPy.
"""

from typing import Tuple, List, Dict
import numpy as np
from ml.features import FEATURE_NAMES
from ml.proxy_labels import compute_proxy_flash_flood_label


FOCUS_BASINS = [
    {"name": "Alaknanda Basin (Chamoli)", "lat": 30.5543, "lon": 79.5442, "elev_base": 1800, "slope_base": 28.0},
    {"name": "Mandakini Basin (Rudraprayag)", "lat": 30.2850, "lon": 78.9810, "elev_base": 900, "slope_base": 24.0},
    {"name": "Bhagirathi Basin (Uttarkashi)", "lat": 30.7268, "lon": 78.4354, "elev_base": 1150, "slope_base": 26.0},
    {"name": "Chaliyar / Iruvanji Basin (Wayanad)", "lat": 11.5300, "lon": 76.1300, "elev_base": 850, "slope_base": 22.0},
    {"name": "Periyar Basin (Idukki)", "lat": 9.8500, "lon": 76.9700, "elev_base": 1100, "slope_base": 20.0},
]


def generate_hydrometeorological_dataset(
    n_samples: int = 4000,
    random_state: int = 42
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Generates realistic multivariate feature matrix X and proxy labels y using pure NumPy.
    Returns:
      X: np.ndarray shape (n_samples, len(FEATURE_NAMES))
      y: np.ndarray shape (n_samples,)
      lstm_sequences: np.ndarray shape (n_samples, 24, 4)
    """
    np.random.seed(random_state)
    labels: List[int] = []
    X = np.zeros((n_samples, len(FEATURE_NAMES)), dtype=np.float32)

    # Sequence array for LSTM (n_samples, 24 timesteps, 4 channels: rain, soil_moisture, river_level, discharge)
    lstm_sequences = np.zeros((n_samples, 24, 4), dtype=np.float32)

    for i in range(n_samples):
        basin = FOCUS_BASINS[i % len(FOCUS_BASINS)]

        # Monsoon condition probability (~25% wet monsoon events, 75% normal/dry)
        is_monsoon = np.random.rand() < 0.28
        is_cloudburst = is_monsoon and (np.random.rand() < 0.22)

        if is_cloudburst:
            rain_1h = np.random.uniform(35.0, 85.0)
            rain_3h = rain_1h + np.random.uniform(20.0, 50.0)
            rain_6h = rain_3h + np.random.uniform(10.0, 30.0)
            rain_24h = rain_6h + np.random.uniform(15.0, 60.0)
            rain_peak = rain_1h * np.random.uniform(1.1, 1.6)
            sm_surf = np.random.uniform(0.78, 0.98)
            sm_deep = np.random.uniform(0.75, 0.95)
            api_7d = rain_24h * np.random.uniform(0.8, 1.4)
            discharge_pct = np.random.uniform(0.88, 0.99)
            sensor_level = np.random.uniform(4.0, 6.2)
            danger_mark = 5.0
            sensor_ror = np.random.uniform(0.4, 1.2)
        elif is_monsoon:
            rain_1h = np.random.exponential(scale=6.0)
            rain_3h = rain_1h + np.random.exponential(scale=10.0)
            rain_6h = rain_3h + np.random.exponential(scale=12.0)
            rain_24h = rain_6h + np.random.exponential(scale=20.0)
            rain_peak = rain_1h * np.random.uniform(1.0, 1.3)
            sm_surf = np.random.uniform(0.45, 0.82)
            sm_deep = np.random.uniform(0.40, 0.78)
            api_7d = rain_24h * np.random.uniform(0.5, 0.9)
            discharge_pct = np.random.uniform(0.40, 0.88)
            sensor_level = np.random.uniform(2.0, 4.2)
            danger_mark = 5.0
            sensor_ror = np.random.uniform(-0.1, 0.35)
        else:
            rain_1h = max(0.0, float(np.random.choice([0.0, 0.0, 0.0, np.random.uniform(0.1, 3.0)])))
            rain_3h = rain_1h + np.random.uniform(0.0, 4.0)
            rain_6h = rain_3h + np.random.uniform(0.0, 6.0)
            rain_24h = rain_6h + np.random.uniform(0.0, 12.0)
            rain_peak = rain_1h
            sm_surf = np.random.uniform(0.15, 0.45)
            sm_deep = np.random.uniform(0.20, 0.48)
            api_7d = rain_24h * np.random.uniform(0.2, 0.6)
            discharge_pct = np.random.uniform(0.10, 0.50)
            sensor_level = np.random.uniform(1.2, 2.5)
            danger_mark = 5.0
            sensor_ror = np.random.uniform(-0.15, 0.08)

        elev = float(basin["elev_base"] + np.random.normal(0, 150))
        slope = float(np.clip(basin["slope_base"] + np.random.normal(0, 4), 5.0, 55.0))
        discharge_m3s = float(5.0 + discharge_pct * 80.0 + (rain_24h * 0.4))
        sensor_ratio = float(sensor_level / danger_mark)

        row = {
            "rain_1h_mm": round(float(rain_1h), 2),
            "rain_3h_mm": round(float(rain_3h), 2),
            "rain_6h_mm": round(float(rain_6h), 2),
            "rain_24h_mm": round(float(rain_24h), 2),
            "rain_peak_rate_mmh": round(float(rain_peak), 2),
            "antecedent_precip_index_7d": round(float(api_7d), 2),
            "soil_moisture_surface_ratio": round(float(sm_surf), 3),
            "soil_moisture_deep_ratio": round(float(sm_deep), 3),
            "elevation_m": round(float(elev), 1),
            "slope_degrees": round(float(slope), 2),
            "river_discharge_m3s": round(float(discharge_m3s), 2),
            "discharge_percentile_anomaly": round(float(discharge_pct), 3),
            "sensor_level_m": round(float(sensor_level), 2),
            "sensor_rate_of_rise_mh": round(float(sensor_ror), 3),
            "sensor_danger_ratio": round(float(sensor_ratio), 3),
        }

        y_label = compute_proxy_flash_flood_label(row)
        labels.append(y_label)

        for col_idx, col_name in enumerate(FEATURE_NAMES):
            X[i, col_idx] = float(row[col_name])

        # Synthesize temporal sequence (24 steps hourly)
        t_steps = 24
        hourly_rain = np.zeros(t_steps)
        if rain_24h > 0:
            weights = np.exp(np.linspace(-3, 1, t_steps))
            hourly_rain = (weights / weights.sum()) * rain_24h

        soil_trajectory = np.linspace(sm_surf * 0.7, sm_surf, t_steps)
        level_trajectory = np.linspace(max(0.5, sensor_level - sensor_ror * 12), sensor_level, t_steps)
        discharge_trajectory = np.linspace(discharge_m3s * 0.6, discharge_m3s, t_steps)

        for t in range(t_steps):
            lstm_sequences[i, t, 0] = float(hourly_rain[t])
            lstm_sequences[i, t, 1] = float(soil_trajectory[t])
            lstm_sequences[i, t, 2] = float(level_trajectory[t])
            lstm_sequences[i, t, 3] = float(discharge_trajectory[t])

    y = np.array(labels, dtype=np.int32)
    return X, y, lstm_sequences
