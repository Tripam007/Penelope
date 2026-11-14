import { NextResponse } from "next/server";
import { MOCK_SENSORS } from "@/lib/mockData";

export async function GET() {
  return NextResponse.json(MOCK_SENSORS);
}
