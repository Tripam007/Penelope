import { NextRequest, NextResponse } from "next/server";
import { MOCK_REGIONS } from "@/lib/mockData";

export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  const reg = MOCK_REGIONS.find(
    (r) => r.id === params.id || r.name.toLowerCase().includes(params.id.toLowerCase())
  );

  return NextResponse.json(reg || MOCK_REGIONS[0]);
}
