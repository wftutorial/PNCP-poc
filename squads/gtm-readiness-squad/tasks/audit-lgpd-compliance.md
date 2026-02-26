---
task: "Audit LGPD Compliance"
responsavel: "@security-auditor"
responsavel_type: agent
atomic_layer: task
Entrada: |
  - frontend/app/privacidade/page.tsx
  - frontend/app/termos/page.tsx
  - Cookie consent implementation
  - backend/log_sanitizer.py
Saida: |
  - LGPD compliance assessment
  - Gaps in data protection
  - Third-party data sharing disclosure check
Checklist:
  - "[ ] Cookie consent dialog present"
  - "[ ] Privacy policy published"
  - "[ ] Terms of Service published"
  - "[ ] ToS doesn't reference Mercado Pago (non-existent)"
  - "[ ] User data deletion mechanism"
  - "[ ] PII not in logs (log_sanitizer.py)"
  - "[ ] Third-party disclosure (OpenAI, Stripe, Sentry)"
  - "[ ] Data retention policy defined"
---

# *audit-lgpd

Check LGPD (Brazilian data protection) compliance.

## Steps

1. Read privacy policy page — check completeness
2. Read terms of service — check accuracy (no Mercado Pago reference)
3. Check cookie consent implementation
4. Read log_sanitizer.py — verify PII scrubbing
5. Check if user data deletion endpoint exists
6. Verify third-party data sharing is disclosed

## Output

Score (0-10) + compliance gaps + recommendations
