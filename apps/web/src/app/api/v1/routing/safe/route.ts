import { NextRequest, NextResponse } from "next/server";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { from, to } = body;

    const fromCoord = Array.isArray(from) ? from : [30.4856, 79.6931];
    const toCoord = Array.isArray(to) ? to : [30.5564, 79.5667];

    // Compute midpoint high ground corridor
    const midLat = (fromCoord[0] + toCoord[0]) / 2 + 0.015;
    const midLng = (fromCoord[1] + toCoord[1]) / 2 - 0.01;

    return NextResponse.json({
      status: "SUCCESS",
      route: [
        [fromCoord[0], fromCoord[1]],
        [midLat, midLng],
        [toCoord[0], toCoord[1]]
      ],
      distance_km: 14.8,
      estimated_time_min: 32,
      risk_exposure_score: 0.18,
      safety_rating: "HIGH_GROUND_CORRIDOR",
      nearest_open_shelter: {
        id: "sh-1",
        name: "Joshimath Town Hall Relief Shelter",
        lat: 30.559,
        lng: 79.562,
        capacity: 600,
        available_beds: 420
      },
      hazard_warnings: [
        "Avoid riverside trail along Rishi Ganga due to rapid surge discharge."
      ]
    });
  } catch (error) {
    return NextResponse.json(
      { error: "Invalid routing request" },
      { status: 400 }
    );
  }
}
