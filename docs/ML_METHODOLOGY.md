# PENELOPE Machine Learning Methodology & Transparency

> **Core Principle (Hard Rule 4):** Model Honesty & Transparency  
> *No ground-truth flash-flood sensor labels exist in open public data.* PENELOPE strictly documents proxy label definitions, reports calibrated classification & calibration metrics, and prominently displays official disaster management disclaimers.

---

## 1. Hydro-Meteorological Proxy Label Formulation

Flash floods in steep mountainous terrain (Himalayas and Western Ghats) occur when multiple critical hydrological and meteorological factors converge simultaneously:

1. **Intense Convective Precipitation Trigger:**
   - 1-Hour Cumulative Rainfall $\ge 35\text{ mm}$ OR
   - 3-Hour Cumulative Rainfall $\ge 60\text{ mm}$ OR
   - 24-Hour Rainfall $\ge 64.5\text{ mm}$ (IMD Heavy Rainfall criterion) OR
   - Peak rainfall burst rate $\ge 40\text{ mm/h}$ (cloudburst initiation).

2. **Antecedent Soil Moisture Saturation:**
   - Topsoil Moisture (0-1cm depth) $\ge 0.38\text{ m}^3/\text{m}^3$ ($\ge 80\%$ of field saturation capacity). When soil pore space is saturated, infiltration ceases and direct overland runoff accelerates.

3. **Hydrological Channel Discharge Anomaly:**
   - GloFAS River Discharge $\ge 92\text{nd}$ to $95\text{th}$ percentile historical threshold.

4. **River Stage Proximity to Danger Level:**
   - Sensor Gauge Water Level $\ge 85\%$ of designated Danger Mark ($H / H_{\text{danger}} \ge 0.85$) OR Rate of Rise $dh/dt \ge 0.5\text{ m/h}$.

5. **Topographic Runoff Acceleration:**
   - Mountain slope gradient $\ge 15^\circ$ reduces time of concentration, accelerating upstream floodwave cresting downstream.

When the weighted composite hydro-meteorological hazard score reaches or exceeds $55.0$, `proxy_label = 1` (Flash Flood Event); otherwise `0`.

---

## 2. Feature Engineering

15 engineered features feed into the predictive models:

| Feature Name | Description | Source |
|---|---|---|
| `rain_1h_mm` | 1-Hour rolling precipitation | Open-Meteo Forecast |
| `rain_3h_mm` | 3-Hour rolling precipitation | Open-Meteo Forecast |
| `rain_6h_mm` | 6-Hour rolling precipitation | Open-Meteo Forecast |
| `rain_24h_mm` | 24-Hour rolling precipitation | Open-Meteo Forecast |
| `rain_peak_rate_mmh` | Peak rainfall intensity rate | Open-Meteo Forecast |
| `antecedent_precip_index_7d` | 7-day Antecedent Precipitation Index ($API = \sum P_{t-i} \cdot 0.85^i$) | Open-Meteo Archive |
| `soil_moisture_surface_ratio` | Soil moisture (0-1cm) / 0.45 saturation capacity | Open-Meteo Forecast |
| `soil_moisture_deep_ratio` | Subsurface soil moisture (9-27cm) / 0.45 | Open-Meteo Forecast |
| `elevation_m` | Digital Elevation Model altitude | Open-Meteo Elevation / SRTM |
| `slope_degrees` | Horn's algorithm slope gradient from DEM | Computed from DEM matrix |
| `river_discharge_m3s` | GloFAS daily discharge volume ($m^3/s$) | Open-Meteo Flood API |
| `discharge_percentile_anomaly` | Discharge percentile relative to max | Open-Meteo Flood API |
| `sensor_level_m` | Current gauge water level ($m$) | IoT River Sensors |
| `sensor_rate_of_rise_mh` | Stage rate of rise ($m/h$) | IoT River Sensors |
| `sensor_danger_ratio` | Water level / Danger level mark | IoT River Sensors |

---

## 3. Model Benchmark & MLflow-Lite Performance

The models were evaluated on an independent 20% test partition (1,000 mountain catchment samples):

| Metric | LightGBM Classifier (Primary) | Random Forest Baseline | Sequence Hydrology LSTM |
|---|---|---|---|
| **ROC-AUC** | **0.9988** | 0.9999 | 0.7449 |
| **PR-AUC (Avg Precision)** | **0.9903** | 0.9982 | 0.0993 |
| **F1-Score** | **0.9818** | 0.9730 | 0.1102 |
| **Precision** | **0.9780** | 0.9650 | 0.1050 |
| **Recall** | **0.9856** | 0.9810 | 0.1160 |
| **Brier Score (Calibration)**| **0.0076** | 0.0092 | 0.0820 |

---

## 4. Disaster Authority Disclaimer

> **ADVISORY ONLY:** PENELOPE is an experimental AI decision-support platform designed to assist disaster management teams. Emergency response actions must strictly adhere to official bulletins, orange/red alerts, and evacuation orders issued by the **India Meteorological Department (IMD)**, **Central Water Commission (CWC)**, and **State/National Disaster Management Authorities (SDMA / NDMA)**.

