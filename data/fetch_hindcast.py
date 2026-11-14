"""Fetch hindcast and negative-control weather data from Open-Meteo APIs.

Features:
1. Hourly precipitation, shallow and deep soil moisture from Open-Meteo Archive API
   with timezone=Asia/Kolkata (IST).
2. Daily GloFAS river discharge from Open-Meteo Flood API, forward-filled to hourly.
3. 8 extra days (192 hours) before window start fetched as lead-in for computing
   antecedent precipitation index (API), marked with column `is_leadin` (true/false).
4. Exact event_time (IST) defined per event and truncated at event_time:
   72h event window immediately before event_time + 192h lead-in = 264 rows per event.
5. 5-day quiet-day negative controls + 192h lead-in = 312 rows per quiet control.
6. Summary table per event reporting 72h cumulative rain, peak hourly rain rate,
   GloFAS grid-cell coordinates, and a warning if mean discharge < 1.0 m³/s.
"""

from __future__ import annotations

import csv
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
import time
from typing import Any, Dict, List, Optional
import urllib.error
import urllib.parse
import urllib.request

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("fetch_hindcast")

ARCHIVE_API_BASE = "https://archive-api.open-meteo.com/v1/archive"
FLOOD_API_BASE = "https://flood-api.open-meteo.com/v1/flood"
OUTPUT_DIR = Path(__file__).resolve().parent / "hindcast"


class HindcastTargetConfig:
    def __init__(
        self,
        name: str,
        location_label: str,
        latitude: float,
        longitude: float,
        window_type: str,  # "event" or "quiet"
        filename: str,
        event_time_ist: Optional[str] = None,  # ISO format "YYYY-MM-DDTHH:MM"
        quiet_start_ist: Optional[str] = None,  # ISO format "YYYY-MM-DDTHH:MM"
        quiet_end_ist: Optional[str] = None,    # ISO format "YYYY-MM-DDTHH:MM"
    ):
        self.name = name
        self.location_label = location_label
        self.latitude = latitude
        self.longitude = longitude
        self.window_type = window_type
        self.filename = filename
        self.event_time_ist = event_time_ist
        self.quiet_start_ist = quiet_start_ist
        self.quiet_end_ist = quiet_end_ist

        if window_type == "event":
            if not event_time_ist:
                raise ValueError(f"event_time_ist required for event {name}")
            end_dt = datetime.fromisoformat(event_time_ist)
            # 72 hours ending at end_dt inclusive
            start_window_dt = end_dt - timedelta(hours=71)
            # 8 extra days (192 hours) before window start
            start_leadin_dt = start_window_dt - timedelta(days=8)

            self.window_start_dt = start_window_dt
            self.window_end_dt = end_dt
            self.leadin_start_dt = start_leadin_dt
            self.api_start_date = start_leadin_dt.strftime("%Y-%m-%d")
            self.api_end_date = end_dt.strftime("%Y-%m-%d")
        else:
            if not quiet_start_ist or not quiet_end_ist:
                raise ValueError(f"quiet_start_ist and quiet_end_ist required for quiet {name}")
            start_window_dt = datetime.fromisoformat(quiet_start_ist)
            end_window_dt = datetime.fromisoformat(quiet_end_ist)
            start_leadin_dt = start_window_dt - timedelta(days=8)

            self.window_start_dt = start_window_dt
            self.window_end_dt = end_window_dt
            self.leadin_start_dt = start_leadin_dt
            self.api_start_date = start_leadin_dt.strftime("%Y-%m-%d")
            self.api_end_date = end_window_dt.strftime("%Y-%m-%d")


TARGETS: List[HindcastTargetConfig] = [
    # 1. Kedarnath, Uttarakhand (June 2013)
    # Event: Chorabari lake outburst & devastating moraine breach early morning 17 June 2013 (~07:00 IST)
    HindcastTargetConfig(
        name="kedarnath_2013_event",
        location_label="Kedarnath, Uttarakhand",
        latitude=30.7352,
        longitude=79.0669,
        window_type="event",
        filename="kedarnath_2013_event.csv",
        event_time_ist="2013-06-17T07:00",
    ),
    HindcastTargetConfig(
        name="kedarnath_2013_quiet",
        location_label="Kedarnath, Uttarakhand",
        latitude=30.7352,
        longitude=79.0669,
        window_type="quiet",
        filename="kedarnath_2013_quiet.csv",
        quiet_start_ist="2013-06-01T00:00",
        quiet_end_ist="2013-06-05T23:00",
    ),
    # 2. Kerala Floods / Idukki Catchment (August 2018)
    # Event: Peak inflow to Idukki dam & record spillway discharge (Aug 15-16, 2018; peak midnight Aug 16 00:00 IST)
    HindcastTargetConfig(
        name="kerala_2018_event",
        location_label="Idukki Catchment, Kerala",
        latitude=9.8413,
        longitude=76.9692,
        window_type="event",
        filename="kerala_2018_event.csv",
        event_time_ist="2018-08-16T00:00",
    ),
    HindcastTargetConfig(
        name="kerala_2018_quiet",
        location_label="Idukki Catchment, Kerala",
        latitude=9.8413,
        longitude=76.9692,
        window_type="quiet",
        filename="kerala_2018_quiet.csv",
        quiet_start_ist="2018-08-01T00:00",
        quiet_end_ist="2018-08-05T23:00",
    ),
    # 3. Wayanad Landslides (July 2024)
    # Event: First major catastrophic debris flow at Mundakkai/Chooralmala at ~02:00-02:17 AM IST 30 July 2024
    HindcastTargetConfig(
        name="wayanad_2024_event",
        location_label="Chooralmala, Wayanad, Kerala",
        latitude=11.4980,
        longitude=76.1330,
        window_type="event",
        filename="wayanad_2024_event.csv",
        event_time_ist="2024-07-30T02:00",
    ),
    HindcastTargetConfig(
        name="wayanad_2024_quiet",
        location_label="Chooralmala, Wayanad, Kerala",
        latitude=11.4980,
        longitude=76.1330,
        window_type="quiet",
        filename="wayanad_2024_quiet.csv",
        quiet_start_ist="2024-07-01T00:00",
        quiet_end_ist="2024-07-05T23:00",
    ),
    # 4. Dharali / Uttarkashi (August 2025)
    # Event: Cloudburst and Kheer Ganga debris fan flood hitting Dharali village ~13:45-14:00 IST 5 Aug 2025
    HindcastTargetConfig(
        name="dharali_2025_event",
        location_label="Dharali, Uttarkashi, Uttarakhand",
        latitude=31.0407,
        longitude=78.7972,
        window_type="event",
        filename="dharali_2025_event.csv",
        event_time_ist="2025-08-05T14:00",
    ),
    HindcastTargetConfig(
        name="dharali_2025_quiet",
        location_label="Dharali, Uttarkashi, Uttarakhand",
        latitude=31.0407,
        longitude=78.7972,
        window_type="quiet",
        filename="dharali_2025_quiet.csv",
        quiet_start_ist="2025-08-20T00:00",
        quiet_end_ist="2025-08-24T23:00",
    ),
]


def fetch_with_retry(
    url: str,
    params: Dict[str, Any],
    max_retries: int = 4,
    initial_delay: float = 1.5,
    backoff_factor: float = 2.0,
) -> Dict[str, Any]:
    """Fetch JSON from a URL with parameters, retries, and exponential backoff."""
    query_string = urllib.parse.urlencode(params)
    full_url = f"{url}?{query_string}"
    delay = initial_delay

    for attempt in range(1, max_retries + 1):
        try:
            req = urllib.request.Request(
                full_url,
                headers={"User-Agent": "PenelopeFlashFloodHindcast/1.0 (flood-research)"},
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as exc:
            if attempt == max_retries:
                logger.error("Failed request after %d attempts: %s (error: %s)", attempt, full_url, exc)
                raise
            logger.warning(
                "Request failed (attempt %d/%d): %s. Retrying in %.1fs...",
                attempt,
                max_retries,
                exc,
                delay,
            )
            time.sleep(delay)
            delay *= backoff_factor

    raise RuntimeError(f"Unexpected termination while fetching {full_url}")


def fetch_target_data(target: HindcastTargetConfig) -> tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """Fetch archive hourly weather and flood daily discharge, returning filtered records and metadata."""
    logger.info(
        "Fetching archive weather for %s (API dates: %s to %s)...",
        target.name,
        target.api_start_date,
        target.api_end_date,
    )
    archive_params = {
        "latitude": target.latitude,
        "longitude": target.longitude,
        "start_date": target.api_start_date,
        "end_date": target.api_end_date,
        "hourly": "precipitation,soil_moisture_0_to_7cm,soil_moisture_7_to_28cm",
        "timezone": "Asia/Kolkata",
    }
    archive_data = fetch_with_retry(ARCHIVE_API_BASE, archive_params)
    time.sleep(1.0)

    logger.info(
        "Fetching GloFAS discharge for %s (API dates: %s to %s)...",
        target.name,
        target.api_start_date,
        target.api_end_date,
    )
    flood_params = {
        "latitude": target.latitude,
        "longitude": target.longitude,
        "start_date": target.api_start_date,
        "end_date": target.api_end_date,
        "daily": "river_discharge",
    }
    flood_data = fetch_with_retry(FLOOD_API_BASE, flood_params)
    time.sleep(1.0)

    glofas_lat = flood_data.get("latitude")
    glofas_lon = flood_data.get("longitude")

    # Map daily river discharge to lookup
    daily_discharge_map: Dict[str, Optional[float]] = {}
    daily = flood_data.get("daily", {})
    flood_dates = daily.get("time", [])
    flood_discharges = daily.get("river_discharge", [])
    for d_str, dis_val in zip(flood_dates, flood_discharges):
        daily_discharge_map[d_str] = dis_val

    # Align hourly timestamps
    hourly = archive_data.get("hourly", {})
    timestamps = hourly.get("time", [])
    precip = hourly.get("precipitation", [])
    sm_shallow = hourly.get("soil_moisture_0_to_7cm", [])
    sm_deep = hourly.get("soil_moisture_7_to_28cm", [])

    rows: List[Dict[str, Any]] = []
    last_known_discharge: Optional[float] = None

    for i, ts in enumerate(timestamps):
        current_dt = datetime.fromisoformat(ts)

        # Filter strictly within [leadin_start_dt, window_end_dt]
        if current_dt < target.leadin_start_dt or current_dt > target.window_end_dt:
            continue

        is_leadin_bool = current_dt < target.window_start_dt
        is_leadin_str = "true" if is_leadin_bool else "false"

        date_part = ts.split("T")[0]
        discharge_val = daily_discharge_map.get(date_part)
        if discharge_val is not None:
            last_known_discharge = discharge_val
        else:
            discharge_val = last_known_discharge

        row = {
            "timestamp": ts,
            "precipitation": precip[i] if i < len(precip) else None,
            "soil_moisture_0_to_7cm": sm_shallow[i] if i < len(sm_shallow) else None,
            "soil_moisture_7_to_28cm": sm_deep[i] if i < len(sm_deep) else None,
            "river_discharge": discharge_val,
            "is_leadin": is_leadin_str,
            "latitude": target.latitude,
            "longitude": target.longitude,
            "glofas_latitude": glofas_lat,
            "glofas_longitude": glofas_lon,
            "location_name": target.location_label,
            "window_type": target.window_type,
        }
        rows.append(row)

    meta = {
        "target": target,
        "glofas_lat": glofas_lat,
        "glofas_lon": glofas_lon,
    }
    return rows, meta


def save_csv(filepath: Path, rows: List[Dict[str, Any]]) -> None:
    """Save rows to CSV."""
    if not rows:
        return
    fieldnames = list(rows[0].keys())
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def inspect_dataset(filepath: Path) -> Dict[str, Any]:
    """Inspect saved CSV file for row counts and missing values."""
    with open(filepath, "r", encoding="utf-8") as f:
        reader = list(csv.DictReader(f))

    row_count = len(reader)
    leadin_rows = sum(1 for r in reader if r["is_leadin"] == "true")
    window_rows = sum(1 for r in reader if r["is_leadin"] == "false")

    missing_counts: Dict[str, int] = {}
    if reader:
        for key in reader[0].keys():
            missing_counts[key] = sum(1 for r in reader if r[key] is None or r[key] == "" or r[key] == "None")

    return {
        "filename": filepath.name,
        "row_count": row_count,
        "leadin_rows": leadin_rows,
        "window_rows": window_rows,
        "missing_counts": missing_counts,
        "total_missing": sum(missing_counts.values()),
        "rows": reader,
    }


def main() -> None:
    logger.info("Starting Open-Meteo hindcast data extraction with 8-day lead-in...")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    event_summaries: List[Dict[str, Any]] = []
    file_summaries: List[Dict[str, Any]] = []

    for target in TARGETS:
        out_path = OUTPUT_DIR / target.filename
        rows, meta = fetch_target_data(target)
        save_csv(out_path, rows)
        inspection = inspect_dataset(out_path)
        file_summaries.append(inspection)
        logger.info(
            "Saved %s: %d total rows (%d lead-in, %d window)",
            target.filename,
            inspection["row_count"],
            inspection["leadin_rows"],
            inspection["window_rows"],
        )

        if target.window_type == "event":
            # Extract only the 72h window (is_leadin == "false") for the event metrics
            window_rows = [r for r in inspection["rows"] if r["is_leadin"] == "false"]
            precip_values = [float(r["precipitation"]) for r in window_rows]
            discharge_values = [float(r["river_discharge"]) for r in window_rows]

            cumulative_rain = sum(precip_values)
            peak_rain_rate = max(precip_values) if precip_values else 0.0
            mean_discharge = (sum(discharge_values) / len(discharge_values)) if discharge_values else 0.0

            warning_str = ""
            if mean_discharge < 1.0:
                warning_str = f"WARN: Mean discharge < 1 m³/s ({mean_discharge:.2f} m³/s)"

            event_summaries.append({
                "name": target.location_label,
                "event_time_ist": target.event_time_ist,
                "window_range": f"{window_rows[0]['timestamp']} to {window_rows[-1]['timestamp']}",
                "cum_rain_72h": cumulative_rain,
                "peak_hourly_rate": peak_rain_rate,
                "glofas_coords": f"({meta['glofas_lat']:.4f}, {meta['glofas_lon']:.4f})",
                "mean_discharge": mean_discharge,
                "warning": warning_str,
            })

    # Requirement 3: Table per event
    print("\n" + "=" * 115)
    print("EVENT 72-HOUR METEOROLOGICAL & GLOFAS SUMMARY TABLE")
    print("=" * 115)
    header = (
        f"{'Event Location':<28} | {'Event Time (IST)':<17} | {'72h Rain':<10} | "
        f"{'Peak Rate':<11} | {'GloFAS Grid Cell':<22} | {'Mean Q':<8} | {'Notes / Warnings'}"
    )
    print(header)
    print("-" * 115)
    for es in event_summaries:
        row_str = (
            f"{es['name']:<28} | {es['event_time_ist']:<17} | {es['cum_rain_72h']:>7.1f} mm | "
            f"{es['peak_hourly_rate']:>6.1f} mm/h | {es['glofas_coords']:<22} | "
            f"{es['mean_discharge']:>6.2f} | {es['warning']}"
        )
        print(row_str)
    print("=" * 115)

    # Dataset file verification summary
    print("\n" + "=" * 105)
    print("DATASET FILE VERIFICATION SUMMARY")
    print("=" * 105)
    f_header = f"{'Filename':<30} | {'Total Rows':<10} | {'Lead-in':<8} | {'Window':<8} | {'Missing Total':<14} | {'Missing Breakdown'}"
    print(f_header)
    print("-" * 105)
    for s in file_summaries:
        breakdown = ", ".join(f"{k}:{v}" for k, v in s["missing_counts"].items() if v > 0)
        if not breakdown:
            breakdown = "None (0 missing)"
        print(
            f"{s['filename']:<30} | {s['row_count']:<10} | {s['leadin_rows']:<8} | {s['window_rows']:<8} | "
            f"{s['total_missing']:<14} | {breakdown}"
        )
    print("=" * 105 + "\n")


if __name__ == "__main__":
    main()
