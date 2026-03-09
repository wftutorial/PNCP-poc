"use client";

import { ErrorBoundary } from "../../components/ErrorBoundary";

/**
 * DEBT-105 AC2: Error boundary wrapping pipeline page.
 */
export default function PipelineLayout({ children }: { children: React.ReactNode }) {
  return <ErrorBoundary pageName="pipeline">{children}</ErrorBoundary>;
}
