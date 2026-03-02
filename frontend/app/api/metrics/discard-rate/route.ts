import { NextResponse } from "next/server";

/**
 * STORY-351 AC4: Public proxy for /v1/metrics/discard-rate.
 * No auth required — used by landing page StatsSection.
 */
export async function GET() {
  const backendUrl = process.env.BACKEND_URL;
  if (!backendUrl) {
    return NextResponse.json({ discard_rate_pct: 0, sample_size: 0 }, { status: 200 });
  }

  try {
    const res = await fetch(`${backendUrl}/v1/metrics/discard-rate?days=30`, {
      next: { revalidate: 3600 }, // Cache for 1 hour
    });

    if (!res.ok) {
      return NextResponse.json({ discard_rate_pct: 0, sample_size: 0 }, { status: 200 });
    }

    const data = await res.json();
    return NextResponse.json(data);
  } catch {
    // Graceful fallback — never fail the landing page
    return NextResponse.json({ discard_rate_pct: 0, sample_size: 0 }, { status: 200 });
  }
}
