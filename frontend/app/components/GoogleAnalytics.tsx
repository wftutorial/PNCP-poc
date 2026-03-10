'use client';

import Script from 'next/script';
import { useEffect } from 'react';
import { safeGetItem } from '../../lib/storage';

// DEBT-108: nonce prop passed from layout.tsx (read from x-nonce header set by middleware).
export function GoogleAnalytics({ nonce }: { nonce?: string }) {
  const GA_MEASUREMENT_ID = process.env.NEXT_PUBLIC_GA4_MEASUREMENT_ID;

  useEffect(() => {
    // Check for user consent (LGPD/GDPR compliant)
    const hasConsent = safeGetItem('cookie-consent') === 'accepted';

    if (hasConsent && GA_MEASUREMENT_ID && typeof window !== 'undefined') {
      // Initialize dataLayer
      window.dataLayer = window.dataLayer || [];
      function gtag(...args: unknown[]) {
        window.dataLayer.push(args);
      }

      gtag('js', new Date());
      gtag('config', GA_MEASUREMENT_ID, {
        page_path: window.location.pathname,
        anonymize_ip: true, // LGPD/GDPR compliance
      });
    }
  }, [GA_MEASUREMENT_ID]);

  // Don't load GA if no measurement ID is configured
  if (!GA_MEASUREMENT_ID) {
    return null;
  }

  return (
    <>
      {/* DEBT-108: nonce allows this external script under nonce-based CSP */}
      <Script
        src={`https://www.googletagmanager.com/gtag/js?id=${GA_MEASUREMENT_ID}`}
        strategy="afterInteractive"
        nonce={nonce}
      />
      {/* DEBT-108: nonce allows this inline script block under nonce-based CSP */}
      <Script id="google-analytics" strategy="afterInteractive" nonce={nonce}>
        {`
          window.dataLayer = window.dataLayer || [];
          function gtag(){dataLayer.push(arguments);}
          gtag('js', new Date());

          // Wait for consent before initializing
          if (localStorage.getItem('cookie-consent') === 'accepted') {
            gtag('config', '${GA_MEASUREMENT_ID}', {
              page_path: window.location.pathname,
              anonymize_ip: true
            });
          }
        `}
      </Script>
    </>
  );
}

// Helper function to track custom events
export function trackEvent(
  eventName: string,
  eventParams?: Record<string, string | number | boolean | object>
) {
  if (typeof window !== 'undefined' && window.gtag) {
    const hasConsent = safeGetItem('cookie-consent') === 'accepted';
    if (hasConsent) {
      window.gtag('event', eventName, eventParams);
    }
  }
}

// Predefined event trackers for key actions
export const trackSearchEvent = (query: string, resultsCount: number) => {
  trackEvent('search', {
    search_term: query,
    results_count: resultsCount,
  });
};

export const trackDownloadEvent = (filename: string, fileType: string) => {
  trackEvent('file_download', {
    file_name: filename,
    file_type: fileType,
  });
};

export const trackSignupEvent = (method: string) => {
  trackEvent('sign_up', {
    method: method, // e.g., 'email', 'google', etc.
  });
};

export const trackLoginEvent = (method: string) => {
  trackEvent('login', {
    method: method,
  });
};

export const trackPlanSelectedEvent = (planName: string, planPrice: number) => {
  trackEvent('select_item', {
    item_list_name: 'Pricing Plans',
    items: [
      {
        item_name: planName,
        price: planPrice,
      },
    ],
  });
};

// Declare gtag on window — must match searchStatePersistence.ts declaration
declare global {
  interface Window {
    dataLayer: unknown[];
    gtag?: (...args: unknown[]) => void;
  }
}
