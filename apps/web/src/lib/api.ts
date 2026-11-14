const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function fetchMapGeoJSON() {
  const res = await fetch(`${API_BASE}/api/v1/map/geojson`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch map GeoJSON");
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

