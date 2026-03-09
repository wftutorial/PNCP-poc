"use client";

import { ErrorBoundary } from "../../components/ErrorBoundary";

/**
 * DEBT-105 AC1: Error boundary wrapping dashboard page.
 */
export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return <ErrorBoundary pageName="dashboard">{children}</ErrorBoundary>;
}
