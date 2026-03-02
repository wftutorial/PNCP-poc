import { NextResponse } from "next/server";

/**
 * STORY-358 AC4: Public proxy for /v1/metrics/daily-volume.
 * No auth required — used by InstitutionalSidebar on login/signup pages.
 */
export async function GET() {
  const backendUrl = process.env.BACKEND_URL;
  if (!backendUrl) {
    return NextResponse.json(
      { avg_bids_per_day: 0, display_value: "centenas" },
      { status: 200 },
    );
  }

  try {
    const res = await fetch(`${backendUrl}/v1/metrics/daily-volume?days=30`, {
      next: { revalidate: 3600 }, // Cache for 1 hour
    });

    if (!res.ok) {
      return NextResponse.json(
        { avg_bids_per_day: 0, display_value: "centenas" },
        { status: 200 },
      );
    }

    const data = await res.json();
    return NextResponse.json(data);
  } catch {
    // Graceful fallback — never fail the login/signup page
    return NextResponse.json(
      { avg_bids_per_day: 0, display_value: "centenas" },
      { status: 200 },
    );
  }
}
