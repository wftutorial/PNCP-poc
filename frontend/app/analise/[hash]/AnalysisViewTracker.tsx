"use client";

import { useEffect } from "react";
import { useAnalytics } from "@/hooks/useAnalytics";

/**
 * SEO-PLAYBOOK P6: Client island to track analysis_viewed event on page load.
 */
export function AnalysisViewTracker({
  hash,
  viabilityScore,
  bidUf,
}: {
  hash: string;
  viabilityScore: number;
  bidUf: string | null;
}) {
  const { trackEvent } = useAnalytics();

  useEffect(() => {
    trackEvent("analysis_viewed", {
      hash,
      viability_score: viabilityScore,
      uf: bidUf || "",
    });
  }, [hash, viabilityScore, bidUf, trackEvent]);

  return null;
}
