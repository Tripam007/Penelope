import { NextResponse } from "next/server";
import { generateGeoJsonFeatureCollection } from "@/lib/mockData";

export async function GET() {
  const geojson = generateGeoJsonFeatureCollection();
  return NextResponse.json(geojson, {
    headers: {
      "Cache-Control": "public, max-age=15, stale-while-revalidate=60",
    },
  });
}
