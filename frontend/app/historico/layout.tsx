"use client";

import { ErrorBoundary } from "../../components/ErrorBoundary";

/**
 * DEBT-105 AC3: Error boundary wrapping historico page.
 */
export default function HistoricoLayout({ children }: { children: React.ReactNode }) {
  return <ErrorBoundary pageName="historico">{children}</ErrorBoundary>;
}
