import { NextRequest, NextResponse } from "next/server";

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams;
  const lang = searchParams.get("lang") || "en";

  const isHindi = lang.toLowerCase().startsWith("hi");

  return NextResponse.json({
    status: "CAUTION",
    risk_now: 0.64,
    risk_24h: 0.72,
    advice: isHindi
      ? "अलकनंदा बेसिन में अत्यधिक बारिश की संभावना है। कृपया निचले नदी तटों और घाटी ट्रेक से दूर रहें।"
      : "High rainfall advisory active across Alaknanda basin. Avoid low-lying riverbeds and valley treks. Seek designated high-ground shelters.",
    safe_to_travel: false,
    nearest_shelter: {
      name: "Joshimath Town Hall Relief Shelter",
      distance_km: 3.2
    }
  });
}
