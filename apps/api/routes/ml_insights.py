"""
PENELOPE Backend - ML Insights, Explainability & Transparency (Hard Rule 4)
"""

import os
import json
from typing import Dict, Any
from fastapi import APIRouter
from apps.api.config import settings
from apps.api.ingestion.scheduler import ml_predictor

router = APIRouter(prefix="/ml", tags=["ML Insights"])


@router.get("/metrics")
def get_ml_metrics():
    """
    Returns verified MLflow-lite JSON metrics reports for all trained models.
    """
    models = ["lightgbm", "baseline", "lstm"]
    reports = {}

    for m in models:
        path = os.path.join(settings.MODEL_DIR, f"metrics_{m}.json")
        if os.path.exists(path):
            with open(path, "r") as f:
                reports[m] = json.load(f)
        else:
            reports[m] = {
                "status": "not_trained",
                "notice": "Run 'make train' to generate metrics report."
            }

    return {
        "active_model": settings.ACTIVE_TABULAR_MODEL,
        "reports": reports,
        "advisory_notice": "Advisory only. Model metrics evaluated against hydro-meteorological proxy thresholds. Follow official IMD/CWC/NDMA warnings."
    }


@router.post("/predict")
def predict_risk_on_demand(payload: Dict[str, Any]):
    """
    On-demand risk prediction with explainability and multi-horizon output.
    """
    prediction = ml_predictor.predict_risk(payload)
    return prediction


@router.get("/transparency")
def get_model_transparency_statement():
    """
    Model honesty and transparency statement (Hard Rule 4 compliance).
    """
    return {
        "tagline": "Data today. Safer tomorrows.",
        "pillars": ["Predict", "Prepare", "Protect"],
        "ground_truth_disclosure": {
            "statement": "No standardized ground-truth flash-flood observational labels exist in open public data.",
            "proxy_methodology": "PENELOPE uses a calibrated hydro-meteorological composite proxy combining IMD extreme precipitation thresholds (>=64.5mm/24h or intense cloudburst bursts), GloFAS discharge anomalies (>=92nd percentile), topsoil moisture saturation (>=80%), and mountain slope angles.",
            "official_authority": "PENELOPE is an AI-powered advisory and research platform. Emergency response operations must always align with official advisories issued by India Meteorological Department (IMD), Central Water Commission (CWC), and National Disaster Management Authority (NDMA)."
        },
        "model_architectures": {
            "tabular": "LightGBM Gradient Boosted Decision Trees (160 estimators, multi-horizon risk scoring)",
            "baseline": "Scikit-Learn Random Forest Classifier (100 estimators)",
            "sequence": "2-layer PyTorch/NumPy Hydrological Sequence LSTM (24-hour temporal rolling context)"
        }
    }
