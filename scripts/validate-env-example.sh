#!/usr/bin/env bash
# SYS-037: Validate .env.example against actual config usage
# Checks that all env vars referenced in backend/config/ are documented in .env.example
# Usage: bash scripts/validate-env-example.sh

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ENV_EXAMPLE="$ROOT/.env.example"
CONFIG_DIR="$ROOT/backend/config"

if [ ! -f "$ENV_EXAMPLE" ]; then
  echo "ERROR: .env.example not found at $ENV_EXAMPLE"
  exit 1
fi

# Extract all env var names from .env.example (lines matching KEY=value, ignoring comments)
DOCUMENTED_VARS=$(grep -E '^[A-Z_][A-Z0-9_]*=' "$ENV_EXAMPLE" | cut -d= -f1 | sort -u)

# Extract all os.getenv/os.environ references from backend config and main modules
USED_VARS=$(grep -rhoP '(?:os\.getenv|os\.environ\.get|os\.environ\[)\s*\(?\s*["\x27]([A-Z_][A-Z0-9_]*)["\x27]' \
  "$CONFIG_DIR" "$ROOT/backend/main.py" "$ROOT/backend/rate_limiter.py" "$ROOT/backend/redis_pool.py" \
  "$ROOT/backend/supabase_client.py" "$ROOT/backend/startup/" 2>/dev/null \
  | grep -oP '[A-Z_][A-Z0-9_]+' | sort -u)

# Also check frontend NEXT_PUBLIC_ vars
FRONTEND_VARS=$(grep -rhoP 'process\.env\.([A-Z_][A-Z0-9_]*)' "$ROOT/frontend/lib/" "$ROOT/frontend/app/" 2>/dev/null \
  | grep -oP '[A-Z_][A-Z0-9_]+' | sort -u)

ALL_USED=$(echo -e "$USED_VARS\n$FRONTEND_VARS" | sort -u)

MISSING=0
echo "=== .env.example Validation Report ==="
echo ""

echo "--- Missing from .env.example (used in code but not documented) ---"
while IFS= read -r var; do
  if ! echo "$DOCUMENTED_VARS" | grep -qx "$var"; then
    # Skip internal/runtime vars
    case "$var" in
      PORT|HOST|PROCESS_TYPE|RAILWAY_*|NODE_ENV|VERCEL_*|CI|HOME|PATH|PWD) continue ;;
    esac
    echo "  MISSING: $var"
    MISSING=$((MISSING + 1))
  fi
done <<< "$ALL_USED"

if [ "$MISSING" -eq 0 ]; then
  echo "  (none — all env vars are documented)"
fi

echo ""
echo "--- Documented in .env.example ---"
echo "  Total documented: $(echo "$DOCUMENTED_VARS" | wc -l | tr -d ' ')"
echo "  Total used in code: $(echo "$ALL_USED" | wc -l | tr -d ' ')"
echo "  Missing: $MISSING"
echo ""

if [ "$MISSING" -gt 0 ]; then
  echo "WARN: $MISSING env vars are used in code but not documented in .env.example"
  exit 1
else
  echo "OK: All env vars are properly documented"
  exit 0
fi
