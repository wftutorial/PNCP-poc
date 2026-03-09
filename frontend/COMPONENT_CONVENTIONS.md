# Frontend Component Directory Convention

## Directory Structure

```
frontend/
  components/              # Shared across multiple pages
    ui/                    # Primitives (Button, Input, Label, etc.)
    billing/               # Billing components (PaymentRecoveryModal, etc.)
    auth/                  # Auth components (MfaSetupWizard, etc.)
    reports/               # Report components (PdfOptionsModal, etc.)
    ...
  app/
    components/            # App-wide shared (AuthProvider, Footer, etc.)
    buscar/components/     # Search-page specific
    dashboard/components/  # Dashboard-page specific
    alertas/components/    # Alerts-page specific
    pipeline/              # Pipeline-page specific
    ...
```

## Rules

1. **`components/`** (root) — Shared UI used by 2+ pages. Examples: Button, MobileDrawer, BackendStatusIndicator, ViabilityBadge.

2. **`app/components/`** — App-wide components tied to app layout (AuthProvider, Footer, ThemeToggle, UserMenu).

3. **`app/<page>/components/`** — Page-specific components used only within that page. Examples: SearchForm, FilterPanel, ResultCard.

4. **If a page-specific component is imported by another page**, promote it to `components/` (root shared).

5. **ESLint enforces this**: `no-restricted-imports` rule warns on cross-page component imports. See `.eslintrc.json`.

## Decision Log

- **DEBT-106 (2026-03-09)**: Convention documented. 10 components moved to correct directories.
  - To `app/buscar/components/`: ValorFilter, StatusFilter, ModalidadeFilter, EnhancedLoadingProgress, GoogleSheetsExportButton
  - To `components/`: ViabilityBadge, FeedbackButtons, CompatibilityBadge, ActionLabel, DeepAnalysisModal
