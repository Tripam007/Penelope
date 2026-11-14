import { NextRequest, NextResponse } from "next/server";
import { MOCK_VILLAGES } from "@/lib/mockData";

export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  const village = MOCK_VILLAGES.find(
    (v) => v.id === params.id || v.name.toLowerCase() === params.id.toLowerCase()
  );

  if (!village) {
    // Return first village as fallback
    return NextResponse.json(MOCK_VILLAGES[0]);
  }

  return NextResponse.json(village);
}
