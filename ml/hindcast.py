"""
PENELOPE ML Engine - Historical Hindcast & Negative Control Validation Pipeline

Evaluates the trained FloodRiskPredictor against historical flood events and quiet-day controls:
1. Kedarnath, Uttarakhand (June 2013)
2. Kerala Floods / Idukki (August 2018)
3. Wayanad Landslides (July 2024)
4. Dharali / Uttarkashi (August 2025)

Reads data/hindcast/ CSVs, extracts rolling hydrometeorological features and 7-day API
using antecedent lead-in observations, queries static elevation and basin slope, and
computes hourly 3h risk probabilities and warning tiers.
"""

from __future__ import annotations

import csv
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import urllib.request
import urllib.error

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import numpy as np

from ml.dataset import FOCUS_BASINS
from ml.features import (
    calculate_antecedent_precipitation_index,
    extract_features_vector,
)
from ml.predictor import FloodRiskPredictor

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("ml.hindcast")

DATA_DIR = Path("data/hindcast")
MODELS_DIR = Path("ml/models")
HOURLY_CSV_PATH = MODELS_DIR / "hindcast_hourly.csv"
RESULTS_JSON_PATH = MODELS_DIR / "hindcast_results.json"
SWEEP_CSV_PATH = MODELS_DIR / "hindcast_threshold_sweep.csv"

ELEVATION_API_URL = "https://api.open-meteo.com/v1/elevation"

# Local elevation fallback cache if external endpoint is unavailable
KNOWN_ELEVATIONS = {
    (30.7352, 79.0669): 3555.0,  # Kedarnath
    (9.8413, 76.9692): 725.0,    # Idukki
    (11.4980, 76.1330): 1095.0,  # Wayanad
    (31.0407, 78.7972): 2516.0,  # Dharali
}

_elevation_cache: Dict[Tuple[float, float], float] = dict(KNOWN_ELEVATIONS)


def get_elevation_m(lat: float, lon: float) -> float:
    """Fetch digital elevation model height from Open-Meteo elevation API with caching."""
    key = (round(lat, 4), round(lon, 4))
    if key in _elevation_cache:
        return _elevation_cache[key]

    for (k_lat, k_lon), elev in _elevation_cache.items():
        if abs(k_lat - lat) < 0.01 and abs(k_lon - lon) < 0.01:
            return elev

    url = f"{ELEVATION_API_URL}?latitude={lat:.4f}&longitude={lon:.4f}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "PenelopeHindcast/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            elev_val = float(data.get("elevation", [1200.0])[0])
            _elevation_cache[key] = elev_val
            return elev_val
    except Exception as exc:
        logger.warning("Could not fetch elevation for (%f, %f): %s. Using default.", lat, lon, exc)
        return 1200.0


def get_matching_basin_slope(lat: float, lon: float) -> float:
    """Determine slope gradient in degrees from the nearest basin in ml/dataset.py FOCUS_BASINS."""
    best_basin = min(FOCUS_BASINS, key=lambda b: (b["lat"] - lat) ** 2 + (b["lon"] - lon) ** 2)
    return float(best_basin["slope_base"])


def count_alert_episodes(is_high: List[bool]) -> int:
    """Counts distinct alert episodes where consecutive High+ hours count as 1 episode."""
    episodes = 0
    in_episode = False
    for flag in is_high:
        if flag and not in_episode:
            episodes += 1
            in_episode = True
        elif not flag and in_episode:
            in_episode = False
    return episodes


def compute_continuous_lead_time(
    probs: List[float],
    threshold: float = 0.55,
) -> Tuple[str, str]:
    """
    Computes lead time as the start of the LAST continuous High+ run (prob >= threshold)
    that lasts until event_time (the last hour of the window).

    Returns:
        (flagged_yes_no, lead_time_str)
    """
    is_high = [p >= threshold for p in probs]
    flagged = any(is_high)
    if not flagged:
        return "no", "never reached High"

    # Must last until event_time (index -1)
    if not is_high[-1]:
        return "yes", "not sustained to event"

    # Walk backwards from index len - 1
    k = len(is_high) - 1
    while k >= 0 and is_high[k]:
        k -= 1

    # Continuous run starts at index k + 1
    run_start_idx = k + 1
    if run_start_idx == 0:
        return "yes", ">=72h (censored)"

    lead_h = (len(is_high) - 1) - run_start_idx
    lead_str = f"{lead_h} hours" if lead_h != 1 else "1 hour"
    return "yes", lead_str


def process_dataset(
    filepath: Path,
    predictor: FloodRiskPredictor,
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """Process a single event or quiet CSV file hour-by-hour across its active window."""
    with open(filepath, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    if not rows:
        return [], {}

    filename = filepath.name
    dataset_name = filepath.stem
    is_event = "_event" in filename
    window_type = "event" if is_event else "quiet"

    lat = float(rows[0]["latitude"])
    lon = float(rows[0]["longitude"])
    loc_name = rows[0].get("location_name", dataset_name)
    elev = get_elevation_m(lat, lon)
    slope = get_matching_basin_slope(lat, lon)

    precip_series = [float(r["precipitation"]) for r in rows]
    discharge_series = [float(r["river_discharge"]) for r in rows]

    # Active window corresponds to rows where is_leadin == "false"
    active_indices = [i for i, r in enumerate(rows) if r.get("is_leadin", "").lower() == "false"]
    if not active_indices:
        active_indices = list(range(max(0, len(rows) - (72 if is_event else 120)), len(rows)))

    hourly_records: List[Dict[str, Any]] = []
    prob_3h_list: List[float] = []
    tier_list: List[str] = []
    api_7d_list: List[float] = []

    first_high_timestamp: Optional[str] = None
    event_time_str = rows[active_indices[-1]]["timestamp"] if is_event else None
    event_dt = datetime.fromisoformat(event_time_str) if event_time_str else None

    for pos, idx in enumerate(active_indices):
        current_row = rows[idx]
        ts_str = current_row["timestamp"]
        current_dt = datetime.fromisoformat(ts_str)

        # 1. Rolling rainfall features up to current hour idx
        r1 = precip_series[idx]
        r3 = sum(precip_series[max(0, idx - 2) : idx + 1])
        r6 = sum(precip_series[max(0, idx - 5) : idx + 1])
        r24 = sum(precip_series[max(0, idx - 23) : idx + 1])
        rpeak = max(precip_series[max(0, idx - 23) : idx + 1])

        # 2. 7-day antecedent precipitation index (API) computed from preceding 168 hours
        daily_7d: List[float] = []
        for day in range(7, 0, -1):
            s_idx = max(0, idx - day * 24)
            e_idx = max(0, idx - (day - 1) * 24)
            daily_7d.append(sum(precip_series[s_idx:e_idx]))
        api_7d = calculate_antecedent_precipitation_index(daily_7d)
        api_7d_list.append(api_7d)

        # 3. Soil moisture ratios relative to saturation capacity ~0.45 m³/m³
        sm_surf_raw = float(current_row["soil_moisture_0_to_7cm"])
        sm_deep_raw = float(current_row["soil_moisture_7_to_28cm"])
        sm_surf_ratio = min(1.0, max(0.0, sm_surf_raw / 0.45))
        sm_deep_ratio = min(1.0, max(0.0, sm_deep_raw / 0.45))

        # 4. GloFAS discharge and empirical percentile anomaly
        discharge_val = float(current_row["river_discharge"])
        dis_pct = float(np.mean([q <= discharge_val for q in discharge_series]))
        dis_pct = min(1.0, max(0.05, dis_pct))

        # 5. Build telemetry dictionary (leaving sensor_* features missing for fallback application)
        telemetry: Dict[str, Any] = {
            "rain_1h_mm": round(r1, 2),
            "rain_3h_mm": round(r3, 2),
            "rain_6h_mm": round(r6, 2),
            "rain_24h_mm": round(r24, 2),
            "rain_peak_rate_mmh": round(rpeak, 2),
            "antecedent_precip_index_7d": round(api_7d, 3),
            "soil_moisture_surface_ratio": round(sm_surf_ratio, 3),
            "soil_moisture_deep_ratio": round(sm_deep_ratio, 3),
            "elevation_m": round(elev, 1),
            "slope_degrees": round(slope, 2),
            "river_discharge_m3s": round(discharge_val, 2),
            "discharge_percentile_anomaly": round(dis_pct, 3),
        }

        # 6. Predict risk
        pred = predictor.predict_risk(telemetry)
        p_3h = float(pred["horizons"]["3h"])
        tier = str(pred["risk_level"])

        prob_3h_list.append(p_3h)
        tier_list.append(tier)

        hours_to_event = None
        if event_dt:
            hours_to_event = int((event_dt - current_dt).total_seconds() / 3600)

        if tier in ["High", "Very High"] and first_high_timestamp is None:
            first_high_timestamp = ts_str

        hourly_records.append({
            "dataset": dataset_name,
            "window_type": window_type,
            "location_name": loc_name,
            "timestamp": ts_str,
            "hours_to_event": hours_to_event if hours_to_event is not None else "",
            "rain_1h_mm": r1,
            "rain_3h_mm": r3,
            "rain_6h_mm": r6,
            "rain_24h_mm": r24,
            "rain_peak_rate_mmh": rpeak,
            "antecedent_precip_index_7d": api_7d,
            "soil_moisture_surface_ratio": round(sm_surf_ratio, 3),
            "soil_moisture_deep_ratio": round(sm_deep_ratio, 3),
            "river_discharge_m3s": discharge_val,
            "discharge_percentile_anomaly": round(dis_pct, 3),
            "elevation_m": elev,
            "slope_degrees": slope,
            "prob_3h": round(p_3h, 4),
            "risk_level": tier,
        })

    # Summary metrics
    window_rain_sum = sum(precip_series[i] for i in active_indices)
    max_api_7d = max(api_7d_list) if api_7d_list else 0.0
    peak_prob = max(prob_3h_list) if prob_3h_list else 0.0

    # Requirement 1: Continuous lead time definition (prob >= 0.55)
    flagged_yes_no, continuous_lead_time = compute_continuous_lead_time(prob_3h_list, threshold=0.55)

    # Requirement 2: Distinct alert episodes (prob >= 0.55)
    is_high_list = [p >= 0.55 for p in prob_3h_list]
    high_count_hours = sum(1 for flag in is_high_list if flag)
    episodes = count_alert_episodes(is_high_list)
    days_evaluated = len(active_indices) / 24.0
    episodes_per_day = round(episodes / days_evaluated, 2) if days_evaluated > 0 else 0.0
    far_hours = high_count_hours / len(active_indices) if active_indices else 0.0

    summary_meta = {
        "dataset": dataset_name,
        "window_type": window_type,
        "location_name": loc_name,
        "total_hours_evaluated": len(active_indices),
        "days_evaluated": days_evaluated,
        "cumulative_rain_72h_mm": round(window_rain_sum, 2),
        "max_antecedent_precip_index_7d": round(max_api_7d, 3),
        "peak_probability_3h": round(peak_prob, 4),
        "peak_risk_tier": FloodRiskPredictor.get_risk_level(peak_prob),
        "flagged": flagged_yes_no,
        "lead_time": continuous_lead_time,
        "first_hour_reached_high": first_high_timestamp if first_high_timestamp else "never reached High",
        "high_or_above_hours": high_count_hours,
        "false_alarm_rate_hours": round(far_hours, 4),
        "alert_episodes": episodes,
        "episodes_per_day": episodes_per_day,
        "event_time_ist": event_time_str,
        "prob_3h_series": prob_3h_list,
    }

    return hourly_records, summary_meta


def run_threshold_sweep(
    events_summary: Dict[str, Any],
    quiet_summary: Dict[str, Any],
    thresholds: List[float],
) -> List[Dict[str, Any]]:
    """Runs cutoff sweep on prob_3h at specified thresholds and writes CSV."""
    sweep_rows: List[Dict[str, Any]] = []

    for th in thresholds:
        row: Dict[str, Any] = {"threshold": th}

        # Event metrics: flagged yes/no, lead time
        for name, meta in events_summary.items():
            base_key = name.replace("_event", "")
            flagged, lt = compute_continuous_lead_time(meta["prob_3h_series"], threshold=th)
            row[f"{base_key}_flagged"] = flagged
            row[f"{base_key}_lead_time"] = lt

        # Quiet metrics: episodes per day
        for name, meta in quiet_summary.items():
            base_key = name.replace("_quiet", "")
            is_high = [p >= th for p in meta["prob_3h_series"]]
            episodes = count_alert_episodes(is_high)
            days = meta["days_evaluated"]
            ep_per_day = round(episodes / days, 2) if days > 0 else 0.0
            row[f"{base_key}_quiet_episodes_per_day"] = ep_per_day

        sweep_rows.append(row)

    if sweep_rows:
        fieldnames = list(sweep_rows[0].keys())
        with open(SWEEP_CSV_PATH, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(sweep_rows)
        logger.info("Saved threshold sweep to %s", SWEEP_CSV_PATH)

    return sweep_rows


def run_hindcast() -> None:
    logger.info("Initializing FloodRiskPredictor...")
    predictor = FloodRiskPredictor()
    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    event_files = sorted(DATA_DIR.glob("*_event.csv"))
    quiet_files = sorted(DATA_DIR.glob("*_quiet.csv"))

    if not event_files and not quiet_files:
        raise FileNotFoundError(f"No hindcast CSV files found in {DATA_DIR.resolve()}")

    all_hourly_rows: List[Dict[str, Any]] = []
    events_summary: Dict[str, Any] = {}
    quiet_summary: Dict[str, Any] = {}

    # Process events
    for ef in event_files:
        logger.info("Evaluating event file: %s", ef.name)
        rows, meta = process_dataset(ef, predictor)
        all_hourly_rows.extend(rows)
        events_summary[meta["dataset"]] = meta

    # Process quiet windows
    for qf in quiet_files:
        logger.info("Evaluating quiet file: %s", qf.name)
        rows, meta = process_dataset(qf, predictor)
        all_hourly_rows.extend(rows)
        quiet_summary[meta["dataset"]] = meta

    # Save per-hour predictions to CSV
    if all_hourly_rows:
        fieldnames = list(all_hourly_rows[0].keys())
        with open(HOURLY_CSV_PATH, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_hourly_rows)
        logger.info("Saved %d hourly prediction records to %s", len(all_hourly_rows), HOURLY_CSV_PATH)

    # Requirement 3: Threshold sweep at 0.55, 0.65, 0.75, 0.85
    thresholds = [0.55, 0.65, 0.75, 0.85]
    sweep_rows = run_threshold_sweep(events_summary, quiet_summary, thresholds)

    # Clean summaries for JSON serialization (remove large raw series)
    clean_events_summary = {}
    for k, v in events_summary.items():
        clean_v = dict(v)
        clean_v.pop("prob_3h_series", None)
        clean_events_summary[k] = clean_v

    clean_quiet_summary = {}
    for k, v in quiet_summary.items():
        clean_v = dict(v)
        clean_v.pop("prob_3h_series", None)
        clean_quiet_summary[k] = clean_v

    total_quiet_hours = sum(q["total_hours_evaluated"] for q in quiet_summary.values())
    total_quiet_high = sum(q["high_or_above_hours"] for q in quiet_summary.values())
    total_quiet_episodes = sum(q["alert_episodes"] for q in quiet_summary.values())
    total_quiet_days = total_quiet_hours / 24.0
    overall_far_hours = (total_quiet_high / total_quiet_hours) if total_quiet_hours > 0 else 0.0
    overall_ep_per_day = round(total_quiet_episodes / total_quiet_days, 2) if total_quiet_days > 0 else 0.0

    output_results = {
        "events": clean_events_summary,
        "quiet_controls": clean_quiet_summary,
        "threshold_sweep": sweep_rows,
        "summary": {
            "total_event_datasets": len(events_summary),
            "total_quiet_datasets": len(quiet_summary),
            "overall_quiet_hours": total_quiet_hours,
            "overall_quiet_false_alarm_hours": total_quiet_high,
            "overall_quiet_false_alarm_rate_hours": round(overall_far_hours, 4),
            "overall_quiet_alert_episodes": total_quiet_episodes,
            "overall_quiet_episodes_per_day": overall_ep_per_day,
        },
        "limitations": [
            "reanalysis rain underestimates cloudbursts",
            "no gauge inputs",
            "soil layers approximated",
            "quiet controls differ in wetness; Kedarnath and Dharali controls are dry",
        ],
        "limitations_details": {
            "reanalysis_underestimate": "ERA5 atmospheric reanalysis averages precipitation over ~25km grid cells, smoothing hyper-local convective cloudburst peaks (e.g. Dharali 2025 micro-burst).",
            "no_gauge_inputs": "Automated river level gauges and rate-of-rise telemetry were deliberately omitted to test fallback meteorology-only performance without stream sensors.",
            "soil_layers_approximated": "Open-Meteo Archive layers (0-7cm and 7-28cm) approximate the operational model's 0-1cm surface and 9-27cm deep soil moisture layers.",
            "quiet_controls_wetness": "Quiet controls differ in wetness; Kedarnath and Dharali controls are dry (0-11mm cumulative rain), whereas Western Ghats controls (Idukki, Wayanad) experience persistent monsoon background rain (40-60mm), yielding background false alarm episodes at standard thresholds.",
        },
    }

    with open(RESULTS_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(output_results, f, indent=2)
    logger.info("Saved validation summary to %s", RESULTS_JSON_PATH)

    # Print summary tables
    print("\n" + "=" * 125)
    print("HISTORICAL EVENT HINDCAST VALIDATION (72h Pre-Event, Continuous Lead Time)")
    print("=" * 125)
    header_events = (
        f"{'Event Location':<28} | {'Event Time (IST)':<17} | {'72h Rain':<9} | "
        f"{'Max 7d API':<10} | {'Peak 3h Prob':<12} | {'Peak Tier':<10} | {'Flagged':<8} | {'Lead Time (Last Continuous Run)'}"
    )
    print(header_events)
    print("-" * 125)
    for meta in clean_events_summary.values():
        row_str = (
            f"{meta['location_name']:<28} | {meta['event_time_ist']:<17} | {meta['cumulative_rain_72h_mm']:>6.1f} mm | "
            f"{meta['max_antecedent_precip_index_7d']:>8.2f} mm | {meta['peak_probability_3h']:>12.4f} | "
            f"{meta['peak_risk_tier']:<10} | {meta['flagged']:<8} | {meta['lead_time']}"
        )
        print(row_str)
    print("=" * 125)

    print("\n" + "=" * 95)
    print("SEASONAL QUIET-DAY NEGATIVE CONTROLS (Episode & Rate Analysis)")
    print("=" * 95)
    header_quiet = (
        f"{'Control Region':<32} | {'Hours':<6} | {'High+ Hours':<12} | "
        f"{'Hours FAR':<10} | {'Episodes':<9} | {'Episodes / Day'}"
    )
    print(header_quiet)
    print("-" * 95)
    for meta in clean_quiet_summary.values():
        far_pct = meta["false_alarm_rate_hours"] * 100
        print(
            f"{meta['location_name']:<32} | {meta['total_hours_evaluated']:<6} | "
            f"{meta['high_or_above_hours']:<12} | {far_pct:>7.2f}%  | "
            f"{meta['alert_episodes']:<9} | {meta['episodes_per_day']:>6.2f} ep/day"
        )
    print("-" * 95)
    print(
        f"{'OVERALL AGGREGATE':<32} | {total_quiet_hours:<6} | {total_quiet_high:<12} | "
        f"{overall_far_hours * 100:>7.2f}%  | {total_quiet_episodes:<9} | {overall_ep_per_day:>6.2f} ep/day"
    )
    print("=" * 95)

    print("\n" + "=" * 125)
    print("THRESHOLD SWEEP ON prob_3h CUTOFF (0.55, 0.65, 0.75, 0.85)")
    print("=" * 125)
    sweep_header = (
        f"{'Cutoff':<8} | {'Kedarnath (Lead)':<20} | {'Kerala (Lead)':<18} | "
        f"{'Wayanad (Lead)':<24} | {'Dharali (Lead)':<20} | {'Kerala ep/d':<12} | {'Wayanad ep/d'}"
    )
    print(sweep_header)
    print("-" * 125)
    for sr in sweep_rows:
        th = sr["threshold"]
        ked = f"{sr['kedarnath_2013_flagged']} ({sr['kedarnath_2013_lead_time']})"
        ker = f"{sr['kerala_2018_flagged']} ({sr['kerala_2018_lead_time']})"
        way = f"{sr['wayanad_2024_flagged']} ({sr['wayanad_2024_lead_time']})"
        dha = f"{sr['dharali_2025_flagged']} ({sr['dharali_2025_lead_time']})"
        ker_q = f"{sr['kerala_2018_quiet_episodes_per_day']:.2f}"
        way_q = f"{sr['wayanad_2024_quiet_episodes_per_day']:.2f}"
        print(f"{th:<8.2f} | {ked:<20} | {ker:<18} | {way:<24} | {dha:<20} | {ker_q:<12} | {way_q}")
    print("=" * 125 + "\n")


if __name__ == "__main__":
    run_hindcast()
