"""
PENELOPE ML Engine - Fast Real-Time Predictor & Explainability
Pillars: Predict · Prepare · Protect
"""

import os
import joblib
import numpy as np
from typing import Dict, Any, List, Optional
from ml.features import FEATURE_NAMES, extract_features_vector
from ml.lstm_model import NumpyLSTMInference


class FloodRiskPredictor:
    def __init__(self, model_dir: str = "ml/models"):
        self.model_dir = model_dir
        self.tabular_model = None
        self.baseline_model = None
        self.lstm_model = None
        self._load_models()

    def _load_models(self):
        # 1. Load LightGBM
        lgbm_path = os.path.join(self.model_dir, "lightgbm_flood_classifier.joblib")
        if os.path.exists(lgbm_path):
            try:
                self.tabular_model = joblib.load(lgbm_path)
            except Exception as e:
                print(f"[FloodRiskPredictor] Warning: could not load LightGBM model: {e}")

        # 2. Load Baseline RF
        rf_path = os.path.join(self.model_dir, "baseline_flood_model.joblib")
        if os.path.exists(rf_path):
            try:
                self.baseline_model = joblib.load(rf_path)
            except Exception as e:
                print(f"[FloodRiskPredictor] Warning: could not load Baseline model: {e}")

        # 3. Load LSTM
        lstm_path = os.path.join(self.model_dir, "lstm_hydrology_model.npz")
        if os.path.exists(lstm_path):
            try:
                weights = np.load(lstm_path)
                self.lstm_model = NumpyLSTMInference(dict(weights))
            except Exception as e:
                print(f"[FloodRiskPredictor] Warning: could not load LSTM model: {e}")

    @staticmethod
    def get_risk_level(prob: float) -> str:
        """
        Maps probability to 4 standard early-warning disaster risk categories:
        - Low (< 0.25)
        - Moderate (0.25 - 0.55)
        - High (0.55 - 0.80)
        - Very High (>= 0.80)
        """
        if prob >= 0.80:
            return "Very High"
        elif prob >= 0.55:
            return "High"
        elif prob >= 0.25:
            return "Moderate"
        return "Low"

    def predict_risk(
        self,
        telemetry: Dict[str, Any],
        sequence_data: Optional[np.ndarray] = None
    ) -> Dict[str, Any]:
        """
        Generates comprehensive multi-horizon risk scoring with explainability.
        """
        features_vec = extract_features_vector(telemetry)
        X = np.array([features_vec], dtype=np.float32)

        # Tabular inference
        if self.tabular_model is not None:
            raw_prob = float(self.tabular_model.predict_proba(X)[0, 1])
        elif self.baseline_model is not None:
            raw_prob = float(self.baseline_model.predict_proba(X)[0, 1])
        else:
            # Fallback heuristic calculation if models not yet trained
            rain_3h = float(telemetry.get("rain_3h_mm", 0.0))
            sm_surf = float(telemetry.get("soil_moisture_0_to_1cm", 0.25)) / 0.45
            sensor_level = float(telemetry.get("sensor_level_m", 2.0))
            raw_prob = min(1.0, (rain_3h / 80.0) * 0.5 + sm_surf * 0.3 + (sensor_level / 5.0) * 0.2)

        # Temporal sequence LSTM inference
        lstm_prob = None
        if sequence_data is not None and self.lstm_model is not None:
            try:
                lstm_prob = self.lstm_model.forward(sequence_data)
            except Exception:
                lstm_prob = None

        # Multi-horizon risk projection:
        # 1h: driven strongly by current rain intensity and river rate of rise
        # 3h: peak flash flood hazard window in mountain catchments
        # 6h: sustained runoff accumulation
        # 24h: catchment drainage and antecedent moisture effect
        rain_1h = features_vec[0]
        rain_3h = features_vec[1]
        sensor_ror = features_vec[13]

        surge_factor = max(0.0, sensor_ror * 0.2)
        p_1h = float(np.clip(raw_prob * (0.8 + 0.3 * (rain_1h / max(rain_3h, 1.0))) + surge_factor, 0.0, 1.0))
        p_3h = float(np.clip(raw_prob + surge_factor * 0.5, 0.0, 1.0))
        p_6h = float(np.clip(raw_prob * 0.95, 0.0, 1.0))
        p_24h = float(np.clip(raw_prob * 0.75, 0.0, 1.0))

        risk_level = self.get_risk_level(p_3h)

        # Explainability: Top contributing factors to the risk score
        contributions = []
        if rain_3h >= 25.0:
            contributions.append({
                "factor": "Rainfall Intensity",
                "value": f"{rain_3h:.1f} mm / 3h",
                "impact": "High Positive",
                "description": "Exceeds mountain flash-flood critical trigger threshold"
            })
        if features_vec[6] >= 0.75:  # Soil moisture ratio
            contributions.append({
                "factor": "Soil Saturation",
                "value": f"{int(features_vec[6]*100)}%",
                "impact": "High Positive",
                "description": "High antecedent saturation reduces infiltration and amplifies direct surface runoff"
            })
        if features_vec[9] >= 20.0:  # Slope
            contributions.append({
                "factor": "Steep Slope Gradient",
                "value": f"{features_vec[9]:.1f}°",
                "impact": "Moderate Positive",
                "description": "Steep Himalayan/Ghats topography accelerates catchment time to concentration"
            })
        if features_vec[14] >= 0.80:  # Sensor danger ratio
            contributions.append({
                "factor": "River Stage",
                "value": f"{features_vec[12]:.2f} m ({int(features_vec[14]*100)}% danger level)",
                "impact": "Critical",
                "description": "River water level approaching or exceeding bankfull capacity"
            })

        if not contributions:
            contributions.append({
                "factor": "Meteorological Baseline",
                "value": "Normal Range",
                "impact": "Neutral",
                "description": "Current rainfall and river discharge remain within seasonal safe bounds"
            })

        return {
            "risk_score": round(p_3h, 4),
            "risk_level": risk_level,
            "horizons": {
                "1h": round(p_1h, 4),
                "3h": round(p_3h, 4),
                "6h": round(p_6h, 4),
                "24h": round(p_24h, 4),
            },
            "lstm_sequence_prob": round(lstm_prob, 4) if lstm_prob is not None else None,
            "key_factors": contributions,
            "advisory_disclaimer": "Advisory only. Model outputs are experimental AI predictions. Follow official IMD/CWC/NDMA warnings.",
        }

