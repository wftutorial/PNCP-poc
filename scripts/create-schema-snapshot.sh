#!/usr/bin/env bash
# ============================================================================
# create-schema-snapshot.sh — DEBT-208: Schema snapshot via pg_dump
#
# Generates a schema-only dump of the Supabase database as an alternative
# to squashing migrations. Safe, non-destructive, and repeatable.
#
# Usage:
#   ./scripts/create-schema-snapshot.sh                   # Uses DATABASE_URL from .env
#   ./scripts/create-schema-snapshot.sh --url <db_url>    # Explicit DB URL
#   ./scripts/create-schema-snapshot.sh --compare         # Compare with previous snapshot
#   ./scripts/create-schema-snapshot.sh --help            # Show usage
#
# Output: supabase/snapshots/schema_YYYYMMDD.sql
# ============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SNAPSHOTS_DIR="$PROJECT_ROOT/supabase/snapshots"
TODAY=$(date +%Y%m%d)
OUTPUT_FILE="$SNAPSHOTS_DIR/schema_${TODAY}.sql"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Generate a schema-only snapshot of the Supabase database."
    echo ""
    echo "Options:"
    echo "  --url <db_url>    Database URL (overrides DATABASE_URL from .env)"
    echo "  --compare         Compare latest snapshot with previous one"
    echo "  --list            List all existing snapshots"
    echo "  --help            Show this help message"
    echo ""
    echo "Output: supabase/snapshots/schema_YYYYMMDD.sql"
    echo ""
    echo "When to generate:"
    echo "  - Before major migration batches"
    echo "  - After milestone releases"
    echo "  - Monthly (as routine reference)"
    echo ""
    echo "How to compare with previous version:"
    echo "  diff supabase/snapshots/schema_20260301.sql supabase/snapshots/schema_20260331.sql"
}

load_db_url() {
    if [ -n "${DATABASE_URL:-}" ]; then
        echo "$DATABASE_URL"
        return
    fi

    local env_file="$PROJECT_ROOT/.env"
    if [ -f "$env_file" ]; then
        local url
        url=$(grep -E '^DATABASE_URL=' "$env_file" | head -1 | cut -d'=' -f2- | tr -d '"' | tr -d "'")
        if [ -n "$url" ]; then
            echo "$url"
            return
        fi

        # Try SUPABASE_DB_URL as fallback
        url=$(grep -E '^SUPABASE_DB_URL=' "$env_file" | head -1 | cut -d'=' -f2- | tr -d '"' | tr -d "'")
        if [ -n "$url" ]; then
            echo "$url"
            return
        fi
    fi

    echo ""
}

list_snapshots() {
    echo -e "${GREEN}Existing snapshots:${NC}"
    if [ -d "$SNAPSHOTS_DIR" ]; then
        local count
        count=$(find "$SNAPSHOTS_DIR" -name "schema_*.sql" 2>/dev/null | wc -l)
        if [ "$count" -eq 0 ]; then
            echo "  (none)"
        else
            find "$SNAPSHOTS_DIR" -name "schema_*.sql" -exec ls -lh {} \; | sort
        fi
    else
        echo "  (snapshots directory does not exist)"
    fi
}

compare_snapshots() {
    local files
    files=$(find "$SNAPSHOTS_DIR" -name "schema_*.sql" 2>/dev/null | sort)
    local count
    count=$(echo "$files" | grep -c . || true)

    if [ "$count" -lt 2 ]; then
        echo -e "${YELLOW}Need at least 2 snapshots to compare. Found: $count${NC}"
        exit 1
    fi

    local prev latest
    prev=$(echo "$files" | tail -2 | head -1)
    latest=$(echo "$files" | tail -1)

    echo -e "${GREEN}Comparing:${NC}"
    echo "  Previous: $(basename "$prev")"
    echo "  Latest:   $(basename "$latest")"
    echo ""

    if command -v diff &>/dev/null; then
        diff --unified=3 "$prev" "$latest" || true
    else
        echo -e "${YELLOW}diff not available. Files:${NC}"
        echo "  $prev"
        echo "  $latest"
    fi
}

generate_snapshot() {
    local db_url="$1"

    mkdir -p "$SNAPSHOTS_DIR"

    if [ -f "$OUTPUT_FILE" ]; then
        echo -e "${YELLOW}Snapshot already exists: $OUTPUT_FILE${NC}"
        echo "Overwriting..."
    fi

    echo -e "${GREEN}Generating schema snapshot...${NC}"
    echo "  Output: $OUTPUT_FILE"

    if ! command -v pg_dump &>/dev/null; then
        echo -e "${RED}ERROR: pg_dump not found in PATH.${NC}"
        echo "Install PostgreSQL client tools or add pg_dump to PATH."
        echo ""
        echo "Alternatives:"
        echo "  - Windows: Install PostgreSQL or use Supabase CLI"
        echo "  - Docker:  docker run --rm postgres:17 pg_dump --schema-only <url>"
        echo "  - Supabase CLI: npx supabase db dump --schema-only > $OUTPUT_FILE"
        exit 1
    fi

    # Header comment
    {
        echo "-- ============================================================================"
        echo "-- SmartLic Schema Snapshot"
        echo "-- Generated: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
        echo "-- Tool: pg_dump --schema-only"
        echo "-- Purpose: Reference snapshot (DEBT-208). DO NOT squash migrations."
        echo "-- ============================================================================"
        echo ""
    } > "$OUTPUT_FILE"

    # Run pg_dump (schema-only, no owner, no privileges for portability)
    pg_dump \
        --schema-only \
        --no-owner \
        --no-privileges \
        --no-comments \
        --schema=public \
        "$db_url" >> "$OUTPUT_FILE" 2>&1

    local exit_code=$?
    if [ $exit_code -ne 0 ]; then
        echo -e "${RED}ERROR: pg_dump failed (exit code $exit_code).${NC}"
        echo "Check database URL and connectivity."
        rm -f "$OUTPUT_FILE"
        exit 1
    fi

    local size
    size=$(wc -c < "$OUTPUT_FILE")
    local lines
    lines=$(wc -l < "$OUTPUT_FILE")

    echo -e "${GREEN}Snapshot generated successfully!${NC}"
    echo "  File:  $OUTPUT_FILE"
    echo "  Size:  $size bytes"
    echo "  Lines: $lines"
}

# --- Main ---

DB_URL=""
ACTION="generate"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --url)
            DB_URL="$2"
            shift 2
            ;;
        --compare)
            ACTION="compare"
            shift
            ;;
        --list)
            ACTION="list"
            shift
            ;;
        --help|-h)
            usage
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            usage
            exit 1
            ;;
    esac
done

case "$ACTION" in
    list)
        list_snapshots
        ;;
    compare)
        compare_snapshots
        ;;
    generate)
        if [ -z "$DB_URL" ]; then
            DB_URL=$(load_db_url)
        fi
        if [ -z "$DB_URL" ]; then
            echo -e "${RED}ERROR: No database URL found.${NC}"
            echo "Set DATABASE_URL in .env or use --url <db_url>"
            exit 1
        fi
        generate_snapshot "$DB_URL"
        ;;
esac
