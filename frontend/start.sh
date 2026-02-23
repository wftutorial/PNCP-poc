#!/bin/sh
# =============================================================================
# SLA-001: Graceful shutdown wrapper for Next.js standalone server
# =============================================================================
# Handles SIGTERM from Railway during deploys/scaling by:
#   1. Forwarding SIGTERM to the Node.js process
#   2. Allowing drainingSeconds (set in railway.toml) for in-flight requests
#   3. Exiting cleanly so Railway doesn't force-kill the container
#
# This prevents connection drops during deployments and scaling events.

set -e

echo "[START] Next.js server starting on port ${PORT:-3000}..."
echo "[START] HOSTNAME=${HOSTNAME:-0.0.0.0}"
echo "[START] NODE_ENV=${NODE_ENV:-production}"

# Trap SIGTERM and SIGINT to forward to child process
cleanup() {
  echo "[SHUTDOWN] Received signal, draining connections..."
  if [ -n "$SERVER_PID" ]; then
    kill -TERM "$SERVER_PID" 2>/dev/null || true
    # Wait for graceful shutdown (Railway's drainingSeconds handles the timeout)
    wait "$SERVER_PID" 2>/dev/null || true
  fi
  echo "[SHUTDOWN] Server stopped cleanly."
  exit 0
}

trap cleanup TERM INT

# Start Next.js standalone server in background so we can trap signals
node server.js &
SERVER_PID=$!

echo "[START] Server PID: $SERVER_PID"

# Wait for server process (this allows trap to fire)
wait "$SERVER_PID"
EXIT_CODE=$?

echo "[EXIT] Server exited with code: $EXIT_CODE"
exit $EXIT_CODE
