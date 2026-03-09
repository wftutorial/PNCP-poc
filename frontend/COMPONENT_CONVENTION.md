# Component Directory Convention

This document defines where to place React components in the SmartLic frontend.

## Directory Structure

```
frontend/
├── components/              # Shared across features
│   ├── billing/             # Billing UI (PlanCard, PlanToggle, etc.)
│   ├── subscriptions/       # Subscription flows
│   ├── auth/                # Auth UI (MFA, TOTP)
│   ├── layout/              # Layout primitives
│   └── ui/                  # Generic UI primitives (Button, Input, etc.)
├── app/
│   ├── components/          # App-level wrappers and providers
│   └── {feature}/
│       └── components/      # Feature-specific components
```

## Rules

### `components/` — Shared Components

Used across **two or more** features. Anything here is fair game for any route.

Examples: `NavigationShell`, `Sidebar`, `BottomNav`, `PageHeader`, `EmptyState`,
`MobileDrawer`, `EnhancedLoadingProgress`, `SWRProvider`, billing/subscription/auth subfolders.

**Rule:** A shared component must not import from any `app/{feature}/components/` directory.

### `app/components/` — App-Level Providers and Layouts

Providers, layout wrappers, and app-level infrastructure that wrap the entire app
(usually referenced only in `app/layout.tsx` or root pages).

Examples: `AuthProvider`, `ThemeProvider`, `AnalyticsProvider`, `NProgressProvider`,
`StructuredData`, `GoogleAnalytics`, `ClarityAnalytics`, `CookieConsentBanner`,
`SessionExpiredBanner`, `Dialog`, `UpgradeModal`.

Also includes shared content components used across marketing/blog pages:
`LicitacaoCard`, `LicitacoesPreview`, `InstitutionalSidebar`, landing subdir, etc.

**Rule:** These components should not be imported from `components/` (avoid circular deps).
They CAN be imported by any page.

### `app/{feature}/components/` — Feature-Specific Components

Only used within that feature's routes.

Examples:
- `app/buscar/components/` — `SearchForm`, `FilterPanel`, `ViabilityBadge`, etc.
- `app/alertas/components/` — `AlertCard`, `AlertFormModal`, etc.
- `app/dashboard/components/` — `DashboardStatCards`, etc.

**Rule:** Feature components must not be imported directly by other features.
Cross-feature reuse means the component should be promoted to `components/`.

## Import Direction (enforced by ESLint)

```
app/{feature}/components/  →  app/components/  →  components/
                                                         ↑
                                        (no cross-feature imports)
```

## Flagged Misplacements

The following components may be misplaced based on their usage. They are flagged
for future review — do not move without explicit approval:

| Component | Current Location | Suggested Location | Reason |
|-----------|------------------|--------------------|--------|
| `LoadingProgress.tsx` | `components/` AND `app/components/` | Consolidate to `components/` | Duplicate exists in both directories |
| `EmptyState.tsx` | `components/` | OK — shared generic component | Used across features |
| `LicitacaoCard.tsx` | `app/components/` | Could move to `components/` | Used in marketing + buscar |
| `FilterPanel.tsx` | `app/buscar/components/` | OK — buscar-specific | Only used in search flow |

## Checklist for New Components

1. Will it be used in more than one feature? → `components/`
2. Is it a provider, layout wrapper, or app-level infrastructure? → `app/components/`
3. Is it specific to one feature? → `app/{feature}/components/`
4. When in doubt, start feature-local and promote when needed.
