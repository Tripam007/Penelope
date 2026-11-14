export interface VillageData {
  id: string;
  name: string;
  hindi_name: string;
  type: string;
  region_id: string;
  lat: number;
  lng: number;
  elevation_m: number;
  slope_degrees: number;
  population: number;
  river_distance_m: number;
  current_risk_score: number;
  risk_24h: number;
  risk_48h: number;
  risk_level: "LOW" | "MODERATE" | "HIGH" | "VERY HIGH";
  trend: "RISING" | "STABLE" | "FALLING";
  drivers?: {
    rainfall_anomaly: number;
    river_discharge: number;
    soil_saturation: number;
    terrain_slope: number;
  };
}

export const MOCK_REGIONS = [
  {
    id: "chamoli",
    name: "Uttarakhand - Chamoli District",
    state: "Uttarakhand",
    centroid: [30.42, 79.45],
    status: "ALERT",
    live_alerts: 4,
    at_risk_villages: 18,
    population_at_risk: 34200,
    rainfall_24h_mm: 78.4,
    peak_discharge_m3s: 1420.0,
    last_updated: new Date().toISOString(),
    top_drivers: ["High 24h Rainfall Surge", "Steep Slope Runoff", "Alaknanda Basin Surge"]
  },
  {
    id: "kullu",
    name: "Himachal Pradesh - Kullu Valley",
    state: "Himachal Pradesh",
    centroid: [31.95, 77.10],
    status: "WATCH",
    live_alerts: 1,
    at_risk_villages: 6,
    population_at_risk: 12100,
    rainfall_24h_mm: 42.1,
    peak_discharge_m3s: 680.0,
    last_updated: new Date().toISOString(),
    top_drivers: ["Beas River Rising", "Localized Cloudburst Risk"]
  },
  {
    id: "wayanad",
    name: "Kerala - Wayanad Western Ghats",
    state: "Kerala",
    centroid: [11.68, 76.13],
    status: "NORMAL",
    live_alerts: 0,
    at_risk_villages: 2,
    population_at_risk: 2400,
    rainfall_24h_mm: 18.2,
    peak_discharge_m3s: 210.0,
    last_updated: new Date().toISOString(),
    top_drivers: ["Intermittent Showers", "Soil Saturated"]
  }
];

export const MOCK_VILLAGES: VillageData[] = [
  {
    id: "v-joshimath",
    name: "Joshimath",
    hindi_name: "जोशीमठ",
    type: "town",
    region_id: "chamoli",
    lat: 30.5564,
    lng: 79.5667,
    elevation_m: 1875.0,
    slope_degrees: 28.0,
    population: 16700,
    river_distance_m: 320.0,
    current_risk_score: 0.84,
    risk_24h: 0.89,
    risk_48h: 0.72,
    risk_level: "VERY HIGH",
    trend: "RISING",
    drivers: {
      rainfall_anomaly: 0.88,
      river_discharge: 0.92,
      soil_saturation: 0.81,
      terrain_slope: 0.75
    }
  },
  {
    id: "v-raini",
    name: "Raini",
    hindi_name: "रैणी",
    type: "village",
    region_id: "chamoli",
    lat: 30.4856,
    lng: 79.6931,
    elevation_m: 2045.0,
    slope_degrees: 32.5,
    population: 480,
    river_distance_m: 85.0,
    current_risk_score: 0.92,
    risk_24h: 0.95,
    risk_48h: 0.80,
    risk_level: "VERY HIGH",
    trend: "RISING",
    drivers: {
      rainfall_anomaly: 0.95,
      river_discharge: 0.96,
      soil_saturation: 0.89,
      terrain_slope: 0.90
    }
  },
  {
    id: "v-pipalkoti",
    name: "Pipalkoti",
    hindi_name: "पीपलकोटी",
    type: "town",
    region_id: "chamoli",
    lat: 30.4300,
    lng: 79.4300,
    elevation_m: 1260.0,
    slope_degrees: 22.0,
    population: 2900,
    river_distance_m: 110.0,
    current_risk_score: 0.68,
    risk_24h: 0.74,
    risk_48h: 0.58,
    risk_level: "HIGH",
    trend: "RISING",
    drivers: {
      rainfall_anomaly: 0.70,
      river_discharge: 0.75,
      soil_saturation: 0.65,
      terrain_slope: 0.60
    }
  },
  {
    id: "v-helang",
    name: "Helang",
    hindi_name: "हेलंग",
    type: "village",
    region_id: "chamoli",
    lat: 30.5122,
    lng: 79.5108,
    elevation_m: 1520.0,
    slope_degrees: 29.0,
    population: 850,
    river_distance_m: 90.0,
    current_risk_score: 0.79,
    risk_24h: 0.82,
    risk_48h: 0.64,
    risk_level: "HIGH",
    trend: "RISING",
    drivers: {
      rainfall_anomaly: 0.78,
      river_discharge: 0.84,
      soil_saturation: 0.74,
      terrain_slope: 0.80
    }
  },
  {
    id: "v-vishnuprayag",
    name: "Vishnuprayag",
    hindi_name: "विष्णुप्रयाग",
    type: "village",
    region_id: "chamoli",
    lat: 30.5639,
    lng: 79.5772,
    elevation_m: 1372.0,
    slope_degrees: 34.0,
    population: 320,
    river_distance_m: 45.0,
    current_risk_score: 0.94,
    risk_24h: 0.96,
    risk_48h: 0.85,
    risk_level: "VERY HIGH",
    trend: "RISING",
    drivers: {
      rainfall_anomaly: 0.94,
      river_discharge: 0.98,
      soil_saturation: 0.91,
      terrain_slope: 0.92
    }
  },
  {
    id: "v-karnaprayag",
    name: "Karnaprayag",
    hindi_name: "कर्णप्रयाग",
    type: "town",
    region_id: "chamoli",
    lat: 30.2600,
    lng: 79.2200,
    elevation_m: 860.0,
    slope_degrees: 19.0,
    population: 8200,
    river_distance_m: 70.0,
    current_risk_score: 0.61,
    risk_24h: 0.65,
    risk_48h: 0.50,
    risk_level: "HIGH",
    trend: "STABLE",
    drivers: {
      rainfall_anomaly: 0.62,
      river_discharge: 0.68,
      soil_saturation: 0.59,
      terrain_slope: 0.55
    }
  },
  {
    id: "v-badrinath",
    name: "Badrinath",
    hindi_name: "बद्रीनाथ",
    type: "town",
    region_id: "chamoli",
    lat: 30.7433,
    lng: 79.4938,
    elevation_m: 3133.0,
    slope_degrees: 27.0,
    population: 2400,
    river_distance_m: 150.0,
    current_risk_score: 0.52,
    risk_24h: 0.56,
    risk_48h: 0.45,
    risk_level: "MODERATE",
    trend: "STABLE",
    drivers: {
      rainfall_anomaly: 0.50,
      river_discharge: 0.55,
      soil_saturation: 0.48,
      terrain_slope: 0.55
    }
  },
  {
    id: "v-mana",
    name: "Mana",
    hindi_name: "माणा",
    type: "village",
    region_id: "chamoli",
    lat: 30.7719,
    lng: 79.4950,
    elevation_m: 3200.0,
    slope_degrees: 30.0,
    population: 1210,
    river_distance_m: 120.0,
    current_risk_score: 0.48,
    risk_24h: 0.50,
    risk_48h: 0.40,
    risk_level: "MODERATE",
    trend: "FALLING",
    drivers: {
      rainfall_anomaly: 0.45,
      river_discharge: 0.49,
      soil_saturation: 0.46,
      terrain_slope: 0.52
    }
  }
];

export const MOCK_SENSORS = [
  {
    id: "s-alaknanda-01",
    name: "Alaknanda - Joshimath Hydrometric Station",
    river_name: "Alaknanda",
    type: "ultrasonic_gauge",
    lat: 30.558,
    lng: 79.564,
    status: "ACTIVE",
    water_level_m: 4.82,
    danger_level_m: 5.0,
    warning_level_m: 4.2,
    discharge_m3s: 1120.5,
    rainfall_1h_mm: 14.2,
    battery_pct: 94,
    last_ping: new Date().toISOString()
  },
  {
    id: "s-dhauliganga-02",
    name: "Dhauliganga - Raini Flash Probe",
    river_name: "Dhauliganga",
    type: "radar_stage",
    lat: 30.487,
    lng: 79.691,
    status: "ALERT",
    water_level_m: 5.45,
    danger_level_m: 5.2,
    warning_level_m: 4.5,
    discharge_m3s: 640.2,
    rainfall_1h_mm: 22.8,
    battery_pct: 88,
    last_ping: new Date().toISOString()
  },
  {
    id: "s-pindar-03",
    name: "Pindar River - Karnaprayag Confluence",
    river_name: "Pindar",
    type: "pressure_transducer",
    lat: 30.261,
    lng: 79.222,
    status: "ACTIVE",
    water_level_m: 3.40,
    danger_level_m: 4.5,
    warning_level_m: 3.8,
    discharge_m3s: 410.0,
    rainfall_1h_mm: 8.5,
    battery_pct: 98,
    last_ping: new Date().toISOString()
  }
];

export const MOCK_ALERTS = [
  {
    id: "alt-01",
    village_id: "v-raini",
    village_name: "Raini",
    region_id: "chamoli",
    severity: "CRITICAL",
    category: "FLASH_FLOOD_SURGE",
    title: "Flash Flood Surge Warning - Dhauliganga Catchment",
    message: "Radar telemetry indicates extreme discharge surge (640 m³/s). Evacuation protocol triggered for low-lying settlements along river bank.",
    risk_score: 0.95,
    issued_at: new Date().toISOString(),
    expires_at: new Date(Date.now() + 86400000).toISOString()
  },
  {
    id: "alt-02",
    village_id: "v-vishnuprayag",
    village_name: "Vishnuprayag",
    region_id: "chamoli",
    severity: "HIGH",
    category: "DEBRIS_FLOW_RISK",
    title: "High Debris Flow Hazard Alert",
    message: "Confluence water levels exceeding Warning Threshold (4.82m). Saturated soil on 34° slope raises localized landslide probability.",
    risk_score: 0.94,
    issued_at: new Date().toISOString(),
    expires_at: new Date(Date.now() + 86400000).toISOString()
  }
];

export function generateGeoJsonFeatureCollection() {
  const features = [];

  // 1. Village Features
  for (const v of MOCK_VILLAGES) {
    features.push({
      type: "Feature",
      geometry: {
        type: "Point",
        coordinates: [v.lng, v.lat]
      },
      properties: {
        id: v.id,
        name: v.name,
        hindi_name: v.hindi_name,
        category: "village",
        type: v.type,
        elevation: v.elevation_m,
        risk_score: v.current_risk_score,
        risk_level: v.risk_level,
        population: v.population,
        river_distance_m: v.river_distance_m,
        contact_person: "District Magistrate Helpline (1077)"
      }
    });
  }

  // 2. Sensor Features
  for (const s of MOCK_SENSORS) {
    features.push({
      type: "Feature",
      geometry: {
        type: "Point",
        coordinates: [s.lng, s.lat]
      },
      properties: {
        id: s.id,
        name: s.name,
        category: "sensor",
        river: s.river_name,
        water_level: s.water_level_m,
        danger_level: s.danger_level_m,
        status: s.status
      }
    });
  }

  // 3. Evacuation Shelters
  const shelters = [
    { id: "sh-1", name: "Joshimath Town Hall Relief Shelter", lat: 30.559, lng: 79.562, capacity: 600, elevation: 1910 },
    { id: "sh-2", name: "Pipalkoti Inter College Shelter", lat: 30.432, lng: 79.435, capacity: 450, elevation: 1310 },
    { id: "sh-3", name: "Govindghat High Ground Camp", lat: 30.628, lng: 79.552, capacity: 350, elevation: 1890 }
  ];

  for (const sh of shelters) {
    features.push({
      type: "Feature",
      geometry: {
        type: "Point",
        coordinates: [sh.lng, sh.lat]
      },
      properties: {
        id: sh.id,
        name: sh.name,
        category: "shelter",
        capacity: sh.capacity,
        elevation: sh.elevation,
        contact_person: "Disaster Relief Officer (+91-1372-252101)"
      }
    });
  }

  return {
    type: "FeatureCollection",
    features
  };
}
