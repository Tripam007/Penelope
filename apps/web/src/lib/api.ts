export function getApiBaseUrl(): string {
  if (process.env.NEXT_PUBLIC_API_URL && !process.env.NEXT_PUBLIC_API_URL.includes("localhost")) {
    return process.env.NEXT_PUBLIC_API_URL;
  }
  if (typeof window !== "undefined") {
    const isLocalhost = window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1";
    if (isLocalhost) {
      return process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    }
    return "";
  }
  return process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
}

const API_BASE = getApiBaseUrl();

export async function fetchMapGeoJSON() {
  const res = await fetch(`${API_BASE}/api/v1/map/geojson`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch map GeoJSON");
  return res.json();
}

export async function fetchRiskGeoJSON(bbox?: string, horizon: string = "3h") {
  const query = new URLSearchParams();
  if (bbox) query.set("bbox", bbox);
  if (horizon) query.set("horizon", horizon);
  const res = await fetch(`${API_BASE}/api/v1/map/risk.geojson?${query.toString()}`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch risk GeoJSON");
  return res.json();
}

export async function fetchMapLayers() {
  const res = await fetch(`${API_BASE}/api/v1/map/layers`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch layers");
  return res.json();
}

export async function fetchLayerData(layerName: string) {
  const res = await fetch(`${API_BASE}/api/v1/map/layers/${layerName}`, { cache: "no-store" });
  if (!res.ok) throw new Error(`Failed to fetch layer ${layerName}`);
  return res.json();
}

export async function fetchSafeRoute(fromLocation: [number, number], toLocation: [number, number], regionId?: string) {
  const res = await fetch(`${API_BASE}/api/v1/routing/safe`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      from: fromLocation,
      to: toLocation,
      region_id: regionId
    })
  });
  if (!res.ok) throw new Error("Failed to calculate safe route");
  return res.json();
}

export async function fetchTouristAdvice(lat: number, lng: number, lang: string = "en") {
  const res = await fetch(`${API_BASE}/api/v1/tourist/advice?lat=${lat}&lng=${lng}&lang=${lang}`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch tourist advice");
  return res.json();
}

export async function fetchRegions() {
  const res = await fetch(`${API_BASE}/api/v1/regions`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch regions");
  return res.json();
}

export async function fetchRegionSummary(regionId: string) {
  const res = await fetch(`${API_BASE}/api/v1/regions/${regionId}/summary`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch region summary");
  return res.json();
}

export async function fetchVillages() {
  const res = await fetch(`${API_BASE}/api/v1/villages`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch villages");
  return res.json();
}

export async function fetchVillageDetail(id: string) {
  const res = await fetch(`${API_BASE}/api/v1/villages/${id}`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch village detail");
  return res.json();
}

export async function fetchSensors() {
  const res = await fetch(`${API_BASE}/api/v1/sensors`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch sensors");
  return res.json();
}

export async function fetchActiveAlerts() {
  const res = await fetch(`${API_BASE}/api/v1/alerts/active`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch active alerts");
  return res.json();
}

export async function fetchAllAlerts() {
  const res = await fetch(`${API_BASE}/api/v1/alerts`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch alerts");
  return res.json();
}

export async function fetchMlMetrics() {
  const res = await fetch(`${API_BASE}/api/v1/ml/metrics`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch ML metrics");
  return res.json();
}

export async function fetchTransparency() {
  const res = await fetch(`${API_BASE}/api/v1/ml/transparency`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch transparency disclosure");
  return res.json();
}

export async function fetchSystemHealth() {
  const res = await fetch(`${API_BASE}/api/v1/healthz`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch health");
  return res.json();
}

export async function triggerManualAlert(payload: {
  basin_id: string;
  village_id?: string;
  severity: string;
  title: string;
  title_hi?: string;
  message: string;
  message_hi?: string;
  channels: string[];
}) {
  const res = await fetch(`${API_BASE}/api/v1/alerts/trigger`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error("Failed to trigger alert");
  return res.json();
}

export async function triggerSimulatedSurge(sensorCode: string) {
  const res = await fetch(`${API_BASE}/api/v1/sensors/simulate-surge?sensor_code=${encodeURIComponent(sensorCode)}`, {
    method: "POST",
  });
  if (!res.ok) throw new Error("Failed to trigger surge");
  return res.json();
}
