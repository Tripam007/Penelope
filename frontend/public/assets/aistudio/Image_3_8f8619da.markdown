---
name: Tactical Hydrologic Command
colors:
  surface: '#0e141d'
  surface-dim: '#0e141d'
  surface-bright: '#343944'
  surface-container-lowest: '#080e17'
  surface-container-low: '#161c25'
  surface-container: '#1a2029'
  surface-container-high: '#242a34'
  surface-container-highest: '#2f353f'
  on-surface: '#dde2f0'
  on-surface-variant: '#bcc9cd'
  inverse-surface: '#dde2f0'
  inverse-on-surface: '#2b313b'
  outline: '#869397'
  outline-variant: '#3d494c'
  surface-tint: '#4cd7f6'
  primary: '#4cd7f6'
  on-primary: '#003640'
  primary-container: '#06b6d4'
  on-primary-container: '#00424f'
  inverse-primary: '#00687a'
  secondary: '#4fdbc8'
  on-secondary: '#003731'
  secondary-container: '#04b4a2'
  on-secondary-container: '#003f38'
  tertiary: '#ffb3ad'
  on-tertiary: '#68000a'
  tertiary-container: '#ff817a'
  on-tertiary-container: '#7e000f'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#acedff'
  primary-fixed-dim: '#4cd7f6'
  on-primary-fixed: '#001f26'
  on-primary-fixed-variant: '#004e5c'
  secondary-fixed: '#71f8e4'
  secondary-fixed-dim: '#4fdbc8'
  on-secondary-fixed: '#00201c'
  on-secondary-fixed-variant: '#005048'
  tertiary-fixed: '#ffdad7'
  tertiary-fixed-dim: '#ffb3ad'
  on-tertiary-fixed: '#410004'
  on-tertiary-fixed-variant: '#930013'
  background: '#0e141d'
  on-background: '#dde2f0'
  surface-variant: '#2f353f'
typography:
  headline-xl:
    fontFamily: Inter
    fontSize: 36px
    fontWeight: '700'
    lineHeight: 44px
    letterSpacing: -0.02em
  headline-xl-mobile:
    fontFamily: Inter
    fontSize: 28px
    fontWeight: '700'
    lineHeight: 34px
    letterSpacing: -0.01em
  headline-lg:
    fontFamily: Inter
    fontSize: 28px
    fontWeight: '600'
    lineHeight: 36px
    letterSpacing: -0.01em
  headline-lg-mobile:
    fontFamily: Inter
    fontSize: 22px
    fontWeight: '600'
    lineHeight: 28px
    letterSpacing: -0.01em
  headline-md:
    fontFamily: Inter
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
    letterSpacing: 0em
  headline-sm:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '600'
    lineHeight: 24px
    letterSpacing: 0em
  body-lg:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
    letterSpacing: 0em
  body-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
    letterSpacing: 0em
  body-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 16px
    letterSpacing: 0.01em
  label-lg:
    fontFamily: JetBrains Mono
    fontSize: 14px
    fontWeight: '500'
    lineHeight: 20px
    letterSpacing: 0.02em
  label-md:
    fontFamily: JetBrains Mono
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
    letterSpacing: 0.03em
  label-sm:
    fontFamily: JetBrains Mono
    fontSize: 10px
    fontWeight: '600'
    lineHeight: 14px
    letterSpacing: 0.05em
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  gutter: 1rem
  gutter-desktop: 1.25rem
  margin: 1rem
  margin-desktop: 1.5rem
  space-xs: 0.25rem
  space-sm: 0.5rem
  space-md: 0.75rem
  space-lg: 1.25rem
  space-xl: 2rem
---

## Brand & Style

This design system targets municipal dispatchers, hydrologists, field rescue leads, and civil protection teams who operate in high-tempo, mission-critical environments. The visual atmosphere balances the calm authority of an aerospace telemetry suite with the urgency of active crisis management.

### Personality & Emotional Tenor
- **Tactical Authority:** Absolute clarity under cognitive fatigue; UI chrome steps backward while sensor telemetry, water displacement velocity, and spatial risk layers project forward.
- **Vigilant Restraint:** Alert signals strictly obey hierarchical severity; neutral UI remains subdued to eliminate alarm fatigue.
- **Technical Precision:** Precision-milled panels, laser-fine dividing rules, and monospaced geodetic coordinates create trust and operational certainty.

### Design Movement
The interface executes an advanced **Geospatial Glassmorphism & High-Density Instrument** aesthetic. Deep, light-absorbent charcoal canvases host translucent, frosted data surfaces with hairline borders (`1px` with low-opacity cyan/slate tints). Visual volume is generated through layered ambient glares, optical depth blurs, and vector telemetry readouts rather than heavy opaque sheets.

## Colors

The palette employs deep naval and slate darkness to minimize eye strain in control room command environments, accented by electric cyan and teal telemetry channels. Severity indicators follow standard emergency risk protocols.

### Surface Roles
- **Canvas Base (`#0B111A`):** The primary view layer for base geospatial raster/vector maps and canvas backgrounds.
- **Surface Elevation 1 (`#111A24`):** Secondary navigation docks, telemetry toolbars, and floating auxiliary trays.
- **Surface Elevation 2 (`#1B2636`):** Modular inspection cards, modal sheets, and collapsible control drawers.

### Signal & Sensor Radiance
- **Primary Ray (`#06B6D4`) & Cyan Glow (`#22D3EE` / `#38BDF8`):** Dynamic water vectors, flow velocity contours, active telemetry nodes, selected states, and focus rings.
- **Secondary Ray (`#14B8A6`):** Sensor network health, pump activation states, drainage network throughput.

### Emergency Alert Taxonomy
Color accents for threat severity are reserved strictly for metrics, boundary polygons, and dynamic alert badges:
- **Low Advisory:** Emerald Green (`#10B981`) — Riverbed levels nominal, standard runoff rates.
- **Moderate Watch:** Amber Yellow (`#F59E0B`) — Soil saturation reaching threshold, non-critical floodways active.
- **High Warning:** Orange (`#F97316`) — River stage breach probable within 6 hours, localized road inundation.
- **Critical / Severe Threat:** Rose Red (`#EF4444`) — Immediate catastrophic surge, structural risk, evacuation underway.

## Typography

Typography establishes an unambiguous demarcation between conversational UI/human-readable narratives and live telemetry data.

### Structural Framework
- **Primary Typeface (Inter):** Deployed for all general UI elements, section titles, contextual field notes, and incident briefs. It guarantees exceptional legibility across extreme angles on high-resolution command monitors.
- **Telemetry & Instrument Typeface (JetBrains Mono):** Dedicated strictly to sensor readouts (cfs flow rates, stage elevation in feet/meters, radar precipitation values), coordinate grids (`EPSG:4326`, Lat/Long decimals), timestamps, and alphanumeric incident codes.

### Hierarchy & Tracking
- Display titles employ slight negative tracking (`-0.01em` to `-0.02em`) to ground dense dashboards without visual sprawl.
- All telemetry indicators (`label-sm`, `label-md`) use positive letter-spacing (`0.03em` to `0.05em`) and uppercase styling to ensure character identification during split-second tactical reviews.

## Layout & Spacing

The system leverages a compact, high-density layout paradigm optimized for continuous spatial visualization with contextual overlays.

### Spatial Grid System
- **Desktop (1440px+):** Spatial full-bleed map workspace with docked or floating instrumental heads-up-display (HUD) sidebars (360px–420px width). Auxiliary panels adhere to a dense 12-column sub-grid with `1.25rem` gutters.
- **Tablet (768px - 1439px):** Map maintains viewport dominance; analytics and station indices compress into an off-canvas drawer or a bottom sheet with 2-to-4 column modular grids.
- **Mobile (<768px):** Single-column stack. Map pane occupies 45vh sticky top, with telemetry stream, water-gauge metrics, and evacuation lists reflowing vertically beneath.

### Density Architecture
Spacing uses an explicit base-4 rhythm. Dense layouts maximize real-time situational awareness by reducing unnecessary white space while utilizing strict hairline margins and micro-paddings (`space-xs` and `space-sm`) within sensor arrays.

## Elevation & Depth

Visual hierarchy uses frosted optical depth and luminous chromatic edge treatments instead of traditional solid drop shadows.

### Atmospheric Tiering
- **Level 0 (Map & Base Ground):** Solid base `#0B111A`. Vector topologies, bathymetric contours, and satellite layers render directly here.
- **Level 1 (Docked Telemetry Panels):** Surface `#111A24` rendered with `85%` opacity, backed by a `16px` backdrop blur (`backdrop-filter: blur(16px)`). Edges are defined by a `1px` inner boundary of `rgba(34, 211, 238, 0.08)`.
- **Level 2 (Active Gauges & Overlays):** Surface `#1B2636` rendered at `75%` opacity with `24px` backdrop blur. Micro-drop shadow: `0 4px 20px -2px rgba(6, 182, 212, 0.12)`, grounding it above the spatial map.
- **Level 3 (Emergency Modals & Critical Alerts):** Surface `#1B2636` at `95%` opacity with a directional radiant halo keyed to the incident severity (e.g., severe flood warnings carry `0 0 24px 0 rgba(239, 68, 68, 0.25)`).

### Edge Precision
Shadows remain low-opacity and diffused (`blur 20px–32px`), letting `1px` subtle translucent outlines (`rgba(255, 255, 255, 0.07)`) furnish edge contrast against dynamic GIS satellite tiles.

## Shapes

The design system incorporates a disciplined, technical geometry (`roundedness: 1` — base `0.25rem` / `4px`). This structural precision avoids toy-like softness and reinforces military/industrial hardware aesthetics.

### Geometric Rules
- **Micro UI & Sensors (Badges, Inputs, Telemetry Tabs):** `0.25rem` (4px). Clean, crisp corners that stack flush within complex data grids.
- **Cards & Floating Glass Panels (`rounded-lg`):** `0.5rem` (8px). Softens modular card groups without eroding usable screen acreage.
- **Command Overlays & Dialogs (`rounded-xl`):** `0.75rem` (12px). Applied strictly to root modals and floating spatial action menus.
- **Sensor Indicator Beacons:** Full circle (`9999px`) reserved exclusively for hydro-gauge status nodes, radial velocity indicators, and pulse animations.

## Components

### Action Controls & Buttons
- **Primary Tactical Action:** Background `#06B6D4`, text `#0B111A` (Inter SemiBold), subtle cyan border glow. On hover: `#22D3EE` with `box-shadow: 0 0 12px rgba(6, 182, 212, 0.45)`.
- **Secondary / HUD Button:** Translucent `#1B2636` at `60%`, border `1px solid rgba(6, 182, 212, 0.3)`, text `#38BDF8`.
- **Destructive / Evac Trigger:** Surface `rgba(239, 68, 68, 0.15)`, border `1px solid #EF4444`, text `#EF4444`. Hover yields solid `#EF4444` fill with white text.

### Telemetry Gauges & Sensor Chips
- **Status Chips:** JetBrains Mono `10px` uppercase, padding `2px 8px`, border radius `4px`. Background tinted to severity level at `12%` opacity with matching solid `1px` border (e.g., Critical Alert: `#EF4444` border, `rgba(239, 68, 68, 0.12)` background, text `#EF4444`).
- **Water Level Stage Gauges:** Linear vertical scale with hairline tick marks. Nominal levels fill in `#06B6D4`, transitioning dynamically into Amber (`#F59E0B`) and Rose Red (`#EF4444`) threshold lines with numerical peak markers.

### Input Fields & Filter Docks
- **Search & Coordinate Entry:** Surface `#111A24`, border `1px solid rgba(255, 255, 255, 0.1)`, placeholder `#64748B`, text Inter `14px` white. Focused state shifts border to `#06B6D4` with `0 0 0 1px #06B6D4`.
- **Spatial Toggle Filters:** Segmented controllers encased in `#0B111A` containers. Active layer segment receives `#1B2636` fill, `#22D3EE` text, and a crisp hairline bottom accent line.

### Cards & Module Panels
- **HUD Telemetry Cards:** Frosted `#111A24` base with `backdrop-filter: blur(16px)`, `1px` border `rgba(34, 211, 238, 0.1)`. Padding strictly constrained to `12px` or `16px`. Header features primary gauge name in Inter Medium, alongside real-time ping indicator and JetBrains Mono value readouts.

### Incident Lists & Sensor Feeds
- **Feed Items:** Separated by `1px` hairline rules (`rgba(255, 255, 255, 0.05)`). Alternating states use transparent backgrounds with a left accent border (`3px`) indicating current risk severity (Green, Amber, Orange, Red).

### GIS Map Toolbars & Reticles
- **Floating Map Reticles:** Compact glass pods (`rounded-lg`) placed directly over the spatial canvas. Iconography rendered in `#38BDF8` with active selection states firing a solid `#06B6D4` halo.