"""
Unit and integration tests for PENELOPE ML Engine.
"""

import os
import json
import pytest
import numpy as np

from ml.features import (
    calculate_antecedent_precipitation_index,
    calculate_slope_from_dem,
    extract_features_vector,
    FEATURE_NAMES
)
from ml.proxy_labels import compute_proxy_flash_flood_label
from ml.dataset import generate_hydrometeorological_dataset
from ml.lstm_model import NumpyLSTMInference
from ml.train import train_models
from ml.predictor import FloodRiskPredictor


def test_antecedent_precipitation_index():
    rain_history = [10.0, 20.0, 30.0]
    api = calculate_antecedent_precipitation_index(rain_history, decay_constant=0.85)
    assert api > 0.0
    assert isinstance(api, float)


def test_calculate_slope_from_dem():
    # 90m spacing with 30m rise
    slope = calculate_slope_from_dem(
        elev_center=1000.0,
        elev_north=1030.0,
        elev_south=970.0,
        elev_east=1020.0,
        elev_west=980.0,
        grid_spacing_m=90.0
    )
    assert 0.0 <= slope <= 90.0
    assert slope > 10.0


def test_extract_features_vector():
    raw = {
        "rain_1h_mm": 25.0,
        "rain_3h_mm": 50.0,
        "elevation_m": 1400.0,
        "slope_degrees": 28.0,
    }
    vec = extract_features_vector(raw)
    assert len(vec) == len(FEATURE_NAMES)
    assert vec[0] == 25.0
    assert vec[1] == 50.0


def test_proxy_labels():
    normal_conditions = {
        "rain_1h_mm": 0.0,
        "rain_3h_mm": 1.0,
        "soil_moisture_surface_ratio": 0.3,
        "discharge_percentile_anomaly": 0.2,
        "sensor_danger_ratio": 0.3,
    }
    assert compute_proxy_flash_flood_label(normal_conditions) == 0

    flood_conditions = {
        "rain_1h_mm": 55.0,
        "rain_3h_mm": 90.0,
        "soil_moisture_surface_ratio": 0.92,
        "discharge_percentile_anomaly": 0.98,
        "sensor_danger_ratio": 0.95,
        "slope_degrees": 25.0,
    }
    assert compute_proxy_flash_flood_label(flood_conditions) == 1


def test_dataset_noise_and_missing_sensors():
    X_clean, y_clean, _ = generate_hydrometeorological_dataset(
        n_samples=200, random_state=42, label_noise=0.0, missing_sensor_rate=0.0
    )
    X_noisy, y_noisy, _ = generate_hydrometeorological_dataset(
        n_samples=200, random_state=42, label_noise=0.10, missing_sensor_rate=0.20
    )

    # Some labels should be flipped
    assert not np.array_equal(y_clean, y_noisy)
    # Differences in features due to missing sensor fallback
    assert not np.array_equal(X_clean, X_noisy)


def test_train_models_and_metrics(tmp_path):
    output_dir = str(tmp_path / "models")
    train_models(output_dir=output_dir)

    # Check files exist
    assert os.path.exists(os.path.join(output_dir, "lightgbm_flood_classifier.joblib"))
    assert os.path.exists(os.path.join(output_dir, "baseline_flood_model.joblib"))
    assert os.path.exists(os.path.join(output_dir, "ensemble_flood_model.joblib"))
    assert os.path.exists(os.path.join(output_dir, "lstm_hydrology_model.npz"))
    assert os.path.exists(os.path.join(output_dir, "metrics_lightgbm.json"))
    assert os.path.exists(os.path.join(output_dir, "metrics_baseline.json"))
    assert os.path.exists(os.path.join(output_dir, "metrics_holdout.json"))
    assert os.path.exists(os.path.join(output_dir, "metrics_ensemble.json"))
    assert os.path.exists(os.path.join(output_dir, "metrics_lstm.json"))

    # Validate MLflow-lite metrics structure
    with open(os.path.join(output_dir, "metrics_lightgbm.json")) as f:
        metrics = json.load(f)
        assert "metrics" in metrics
        assert metrics["metrics"]["roc_auc"] >= 0.70
        assert "advisory" in metrics["disclaimer"].lower()

    # Validate holdout metrics structure
    with open(os.path.join(output_dir, "metrics_holdout.json")) as f:
        holdout = json.load(f)
        assert len(holdout["folds"]) == 5
        for metric in ["roc_auc", "pr_auc", "f1", "precision", "recall", "brier"]:
            assert metric in holdout["mean_metrics"]
            assert metric in holdout["folds"][0]

    # Validate ensemble metrics structure
    with open(os.path.join(output_dir, "metrics_ensemble.json")) as f:
        ens = json.load(f)
        assert "metrics" in ens
        assert ens["metrics"]["roc_auc"] >= 0.70
        assert "holdout_evaluation" in ens


def test_flood_risk_predictor(tmp_path):
    output_dir = str(tmp_path / "models")
    train_models(output_dir=output_dir)

    predictor = FloodRiskPredictor(model_dir=output_dir)
    res = predictor.predict_risk({
        "rain_1h_mm": 45.0,
        "rain_3h_mm": 80.0,
        "soil_moisture_0_to_1cm": 0.40,
        "elevation_m": 1200.0,
        "slope_degrees": 26.0,
        "sensor_level_m": 4.8,
        "sensor_danger_mark_m": 5.0,
    })

    assert res["risk_score"] > 0.5
    assert res["risk_level"] in ["High", "Very High"]
    assert "horizons" in res
    assert "1h" in res["horizons"]
    assert len(res["key_factors"]) > 0
    assert "advisory_disclaimer" in res

