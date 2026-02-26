---
task: "Audit DNS, SSL & CSP"
responsavel: "@infra-auditor"
responsavel_type: agent
atomic_layer: task
Entrada: |
  - Production URL: https://smartlic.tech
  - API URL: https://api.smartlic.tech
  - frontend/next.config.js (CSP headers)
Saida: |
  - DNS/SSL assessment
  - CSP policy analysis
  - CORS configuration check
Checklist:
  - "[ ] DNS resolves for smartlic.tech"
  - "[ ] DNS resolves for api.smartlic.tech"
  - "[ ] SSL valid (not expired)"
  - "[ ] HSTS header present"
  - "[ ] CSP connect-src includes api.smartlic.tech"
  - "[ ] CORS origins configured correctly"
  - "[ ] No mixed-content warnings"
---

# *audit-dns-ssl

Check DNS resolution, SSL certificates, and Content Security Policy.

## Steps

1. Check DNS resolution for both domains
2. Verify SSL certificate validity and expiry date
3. Read `frontend/next.config.js` — check CSP headers
4. Check CORS configuration in backend config
5. Test cross-origin API call from frontend to backend

## P0 Known Issue

CSP `connect-src` may be missing `https://api.smartlic.tech`, blocking all API communication from frontend.

## Output

Score (0-10) + findings list + recommendations
