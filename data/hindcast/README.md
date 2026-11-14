# Penelope Hindcast & Negative Control Dataset

This directory contains hourly hydrometeorological datasets extracted from Open-Meteo APIs for 4 real historical flash flood / debris flow events across India, alongside 5-day seasonal quiet-day negative controls for each region.

---

## 1. Verified Event Profiles, Exact Event Times (IST), and Sources

### Event 1: Kedarnath Debris Flow & Glacial Lake Outburst (Uttarakhand, 16–17 June 2013)
- **Exact Event Time (IST):** `2013-06-17T07:00:00`
  - *Chronology:* The initial flash flood and debris surges struck Kedarnath town on the evening of June 16, 2013 (around ~19:15–19:18 IST). The catastrophic second wave that demolished the town was triggered between 06:15 AM and 06:45 AM on June 17, 2013, when the moraine dam of Chorabari Lake (Gandhi Sarovar) breached, releasing over 400,000 $m^3$ of water within 5 to 10 minutes. Truncating at `2013-06-17T07:00` captures the entire 72-hour antecedent buildup including the heavy storm on June 15–16 and the lake breach on the morning of June 17.
- **Coordinates:** $30.7352^\circ\text{ N}, 79.0669^\circ\text{ E}$ (Kedarnath Temple Valley, Mandakini Basin).
- **GloFAS Grid-Cell Coordinates:** $(30.7250^\circ\text{ N}, 79.0750^\circ\text{ E})$ (Elevation ~3,555 m).
- **72h Window:** `2013-06-14T08:00` to `2013-06-17T07:00` (72 hours, `is_leadin = false`).
- **8-Day Lead-In:** `2013-06-06T08:00` to `2013-06-14T07:00` (192 hours, `is_leadin = true`).
- **Quiet Control:** 5 days (`2013-06-01T00:00` to `2013-06-05T23:00`) + 8-day lead-in (`2013-05-24T00:00` to `2013-05-31T23:00`).
- **Discharge Warning:** Mean discharge is under $1\text{ m}^3/\text{s}$ ($\approx 0.52\text{ m}^3/\text{s}$) because this GloFAS grid cell represents an extreme high-altitude headwater origin (drainage area $< 50\text{ km}^2$) where base river discharge is low despite catastrophic moraine dam breach mechanics.
- **Verification Sources:**
  - *Wadia Institute of Himalayan Geology (WIHG):* "Chorabari Lake outburst and Kedarnath calamity: A field assessment" (2013).
  - *National Institute of Disaster Management (NIDM):* "Uttarakhand Disaster 2013 - High Level Committee Report" (2014).
  - *The Hindu / Down To Earth:* Chronology of June 16 (19:18 IST) and June 17 (06:30–06:45 IST) debris flows.

### Event 2: Kerala Floods Peak / Idukki Catchment (August 2018)
- **Exact Event Time (IST):** `2018-08-16T00:00:00`
  - *Chronology:* During the historic August 2018 Kerala flood disaster, the peak storm center was situated over the Peermade-Idukki catchment. The Central Water Commission (CWC) documented the single highest peak inflow into the Idukki reservoir reaching approximately 2,532 $m^3/s$ (cumecs) at 22:00 IST on August 15, 2018, while spillway discharges reached a historic peak of 1,500 $m^3/s$ across August 15–16. Truncating at `2018-08-16T00:00` captures the 72-hour extreme storm sequence of August 13–15 leading directly up to maximum reservoir impingement.
- **Coordinates:** $9.8413^\circ\text{ N}, 76.9692^\circ\text{ E}$ (Idukki Dam & Reservoir, Periyar Basin).
- **GloFAS Grid-Cell Coordinates:** $(9.8250^\circ\text{ N}, 76.9750^\circ\text{ E})$ (Elevation ~669 m).
- **72h Window:** `2018-08-13T01:00` to `2018-08-16T00:00` (72 hours, `is_leadin = false`).
- **8-Day Lead-In:** `2018-08-05T01:00` to `2018-08-13T00:00` (192 hours, `is_leadin = true`).
- **Quiet Control:** 5 days (`2018-08-01T00:00` to `2018-08-05T23:00`) + 8-day lead-in (`2018-07-24T00:00` to `2018-07-31T23:00`).
- **Verification Sources:**
  - *Central Water Commission (CWC), Government of India:* "Kerala Floods of August 2018 Study Report" (Section 5.3: Idukki Dam operations & peak inflow).
  - *India Meteorological Department (IMD):* "Hydromet Report on Southwest Monsoon 2018 Extreme Rainfall Spells over Kerala".

### Event 3: Wayanad First Landslide & Debris Flow (Kerala, 30 July 2024)
- **Exact Event Time (IST):** `2024-07-30T02:00:00`
  - *Chronology:* In Vythiri taluk of Wayanad district, unprecedented antecedent rain (>570 mm over 48h) triggered catastrophic slope failures along the Western Ghats escarpment. Eyewitness accounts, KSDMA logs, and Geological Survey of India (GSI) disaster tracking confirm the first massive debris flow crashed through Punjirimattom and Mundakkai at approximately 02:00–02:17 AM IST on July 30, 2024 (followed by a second wave at Chooralmala at ~04:10 AM IST). Truncating at `2024-07-30T02:00` captures the exact 72-hour antecedent buildup leading directly up to slope failure.
- **Coordinates:** $11.4980^\circ\text{ N}, 76.1330^\circ\text{ E}$ (Chooralmala / Mundakkai / Meppadi, Wayanad).
- **GloFAS Grid-Cell Coordinates:** $(11.4750^\circ\text{ N}, 76.1250^\circ\text{ E})$ (Elevation ~747 m).
- **72h Window:** `2024-07-27T03:00` to `2024-07-30T02:00` (72 hours, `is_leadin = false`).
- **8-Day Lead-In:** `2024-07-19T03:00` to `2024-07-27T02:00` (192 hours, `is_leadin = true`).
- **Quiet Control:** 5 days (`2024-07-01T00:00` to `2024-07-05T23:00`) + 8-day lead-in (`2024-06-23T00:00` to `2024-06-30T23:00`).
- **Verification Sources:**
  - *Geological Survey of India (GSI):* "Preliminary Geological Assessment of Chooralmala-Mundakkai Landslides, Wayanad District, Kerala" (August 2024).
  - *Kerala State Disaster Management Authority (KSDMA):* Emergency Operations Centre Incident Timeline (July 30, 2024).

### Event 4: Dharali Flash Flood & Debris Fan (Uttarkashi, 5 August 2025)
- **Exact Event Time (IST):** `2025-08-05T14:00:00`
  - *Chronology:* A localized severe cloudburst in the upper catchments of the Kheer Ganga (Kheer Gad) triggered a sudden high-velocity debris avalanche and flash surge at approximately 13:45–14:00 IST on August 5, 2025, depositing an estimated 20-hectare debris fan across Dharali village near its confluence with the Bhagirathi River. Truncating at `2025-08-05T14:00` captures the 72-hour antecedent hydrometeorological state leading into the cloudburst event.
- **Coordinates:** $31.0407^\circ\text{ N}, 78.7972^\circ\text{ E}$ (Dharali village, Bhagirathi / Kheer Ganga confluence, Uttarkashi).
- **GloFAS Grid-Cell Coordinates:** $(31.0250^\circ\text{ N}, 78.7750^\circ\text{ E})$ (Elevation ~2,572 m).
- **72h Window:** `2025-08-02T15:00` to `2025-08-05T14:00` (72 hours, `is_leadin = false`).
- **8-Day Lead-In:** `2025-07-25T15:00` to `2025-08-02T14:00` (192 hours, `is_leadin = true`).
- **Quiet Control:** 5 days (`2025-08-20T00:00` to `2025-08-24T23:00`) + 8-day lead-in (`2025-08-12T00:00` to `2025-08-19T23:00`).
- **Verification Sources:**
  - *ISRO National Remote Sensing Centre (NRSC):* Satellite Damage & Geomorphological Mapping of Dharali (August 2025).
  - *Uttarakhand State Emergency Operation Centre (SEOC) & ReliefWeb:* Dharali flash flood response and chronology reports (August 5–6, 2025).

---

## 2. API Endpoints Used

1. **Open-Meteo Historical Weather Archive API**:
   - `https://archive-api.open-meteo.com/v1/archive`
   - Parameters: `hourly=precipitation,soil_moisture_0_to_7cm,soil_moisture_7_to_28cm&timezone=Asia/Kolkata`
   - Surface layer: `soil_moisture_0_to_7cm` ($m^3/m^3$, closest available archive layer to 0–1 cm).
   - Subsurface layer: `soil_moisture_7_to_28cm` ($m^3/m^3$, closest available archive layer to 9–27 cm).
   - Timezone: `Asia/Kolkata` ensures hourly timestamps correspond directly to local Indian Standard Time (IST).

2. **Open-Meteo Flood API**:
   - `https://flood-api.open-meteo.com/v1/flood`
   - Parameters: `daily=river_discharge` (Copernicus GloFAS reanalysis model).
   - Converted to hourly resolution by forward-filling each calendar date's discharge.

---

## 3. CSV Schema

Each file contains the following columns:

| Column Name | Type | Description |
|---|---|---|
| `timestamp` | ISO 8601 string | Local hourly timestamp in IST (`YYYY-MM-DDTHH:MM`) |
| `precipitation` | float | Hourly precipitation in mm |
| `soil_moisture_0_to_7cm` | float | Volumetric soil water content in 0–7 cm depth ($m^3/m^3$) |
| `soil_moisture_7_to_28cm` | float | Volumetric soil water content in 7–28 cm depth ($m^3/m^3$) |
| `river_discharge` | float | Daily GloFAS river discharge ($m^3/s$), forward-filled hourly |
| `is_leadin` | string | `true` for the 8-day (192h) antecedent lead-in window; `false` for active event/quiet window |
| `latitude` | float | Monitored location latitude |
| `longitude` | float | Monitored location longitude |
| `glofas_latitude` | float | GloFAS model grid-cell latitude returned by API |
| `glofas_longitude` | float | GloFAS model grid-cell longitude returned by API |
| `location_name` | string | Geographic label |
| `window_type` | string | `event` or `quiet` |

---

## 4. Generated Datasets

- **Event Files (264 rows each):**
  - `kedarnath_2013_event.csv`: 192h lead-in + 72h event window up to `2013-06-17T07:00`.
  - `kerala_2018_event.csv`: 192h lead-in + 72h event window up to `2018-08-16T00:00`.
  - `wayanad_2024_event.csv`: 192h lead-in + 72h event window up to `2024-07-30T02:00`.
  - `dharali_2025_event.csv`: 192h lead-in + 72h event window up to `2025-08-05T14:00`.

- **Quiet-Day Control Files (312 rows each):**
  - `kedarnath_2013_quiet.csv`: 192h lead-in + 120h (5 days) control window.
  - `kerala_2018_quiet.csv`: 192h lead-in + 120h (5 days) control window.
  - `wayanad_2024_quiet.csv`: 192h lead-in + 120h (5 days) control window.
  - `dharali_2025_quiet.csv`: 192h lead-in + 120h (5 days) control window.
