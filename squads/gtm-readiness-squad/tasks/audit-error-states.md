---
task: "Audit Error States"
responsavel: "@ux-auditor"
responsavel_type: agent
atomic_layer: task
Entrada: |
  - Error components in frontend
  - backend error responses
Saida: |
  - Error state inventory
  - Double-message issue validation
  - User-friendliness assessment
Checklist:
  - "[ ] Network error: single clear message"
  - "[ ] Timeout: suggests reducing UFs"
  - "[ ] Partial results: clear indication"
  - "[ ] Auth error: redirect to login"
  - "[ ] Rate limit: shows retry timing"
  - "[ ] Empty state: helpful suggestions"
  - "[ ] No overlapping error messages"
---

# *audit-errors

Check all error states for user-friendliness.

## P1 KNOWN ISSUE

Double error messages: red error box + gray "Fontes indisponiveis" card shown simultaneously.

## Steps

1. List all error components in frontend
2. Test each error scenario (network, timeout, auth, empty)
3. Check for overlapping/duplicate messages
4. Verify error messages are in Portuguese
5. Check error recovery paths

## Output

Score (0-10) + error inventory + recommendations
