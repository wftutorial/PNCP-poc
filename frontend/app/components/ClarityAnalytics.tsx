'use client';

import { useEffect } from 'react';

// SEO-FIX: nonce prop removed. Replaced <Script> inline with useEffect — the script
// src loads from https://www.clarity.ms (allowed by CSP domain allowlist), no
// inline script needed in HTML so no hash/nonce required.
export function ClarityAnalytics() {
  const CLARITY_PROJECT_ID = process.env.NEXT_PUBLIC_CLARITY_PROJECT_ID;

  useEffect(() => {
    if (!CLARITY_PROJECT_ID) return;

    // Initialize clarity queue before script loads
    const win = window as Window & { clarity?: ((...args: unknown[]) => void) & { q?: unknown[] } };
    win.clarity = win.clarity || function (...args: unknown[]) {
      (win.clarity!.q = win.clarity!.q || []).push(args);
    };

    // Dynamically load Clarity — src allowed by https://www.clarity.ms in CSP script-src
    const script = document.createElement('script');
    script.async = true;
    script.src = `https://www.clarity.ms/tag/${CLARITY_PROJECT_ID}`;
    document.head.appendChild(script);
  }, [CLARITY_PROJECT_ID]);

  return null;
}
