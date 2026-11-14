import { NextResponse } from "next/server";
import { MOCK_REGIONS } from "@/lib/mockData";

export async function GET() {
  return NextResponse.json(MOCK_REGIONS);
}
