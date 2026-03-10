/**
 * Frontend Environment Configuration
 */

// ============================================
// Environment Configuration
// ============================================

export const config = {
  /**
   * Backend API base URL
   * Must be set via NEXT_PUBLIC_API_URL environment variable
   * No localhost fallback to prevent local network access prompts in production
   */
  apiUrl: process.env.NEXT_PUBLIC_API_URL || '',

  /**
   * Supabase configuration (public keys only)
   */
  supabase: {
    url: process.env.NEXT_PUBLIC_SUPABASE_URL || '',
    anonKey: process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || '',
  },

  /**
   * Analytics
   */
  mixpanel: {
    token: process.env.NEXT_PUBLIC_MIXPANEL_TOKEN || '',
  },

  /**
   * Branding (white-label configuration)
   */
  branding: {
    appName: process.env.NEXT_PUBLIC_APP_NAME || 'SmartLic.tech',
    logoUrl: process.env.NEXT_PUBLIC_LOGO_URL || '/logo.svg',
  },
} as const;

/**
 * Consolidated APP_NAME constant (TD-002 FE-24)
 * Import this instead of redeclaring per-file.
 */
export const APP_NAME = config.branding.appName;

// Type-safe config access
export type Config = typeof config;
