import { NextResponse } from "next/server";

export async function GET() {
  return NextResponse.json({
    layers: [
      { id: "risk-heatmap", name: "Risk Heatmap", type: "raster", description: "Real-time AI flood risk surface" },
      { id: "terrain", name: "Terrain Elevation", type: "hillshade", description: "DEM slope & hillshade illumination" },
      { id: "rainfall", name: "Rainfall Anomaly", type: "heatmap", description: "Open-Meteo precipitation anomaly" },
      { id: "river-network", name: "River Network", type: "line", description: "River channels & GloFAS discharge" },
      { id: "locations", name: "Settlements & Treks", type: "symbol", description: "Villages, towns, bridges & routes" },
      { id: "shelters", name: "Evacuation Shelters", type: "symbol", description: "Safe shelters and capacity" }
    ]
  });
}
