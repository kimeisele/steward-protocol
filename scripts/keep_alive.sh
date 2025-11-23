#!/bin/bash

#################################################################################
# HERALD HEARTBEAT
#################################################################################
# The HERALD Agent Autonomous Loop
#
# This script keeps HERALD running indefinitely, executing its workflow
# at regular intervals. It's the "heartbeat" that keeps Agent City alive.
#
# Usage:
#   ./scripts/keep_alive.sh                    # Default: 3600s (1 hour) interval
#   HERALD_INTERVAL=300 ./scripts/keep_alive.sh   # Custom: 300s (5 min) interval
#
# To stop the loop, press Ctrl+C or send SIGTERM to the process
#################################################################################

set -e

# Configuration
HERALD_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
INTERVAL=${HERALD_INTERVAL:-3600}  # Default: 1 hour (in production)
CYCLES=${HERALD_CYCLES:-0}         # 0 = infinite, N = run N times then exit
CYCLE_COUNT=0
DRY_RUN=${HERALD_DRY_RUN:-false}

# Log directory
LOG_DIR="${HERALD_ROOT}/logs/herald"
mkdir -p "$LOG_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    local level=$1
    shift
    local message="$@"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')

    case "$level" in
        INFO)
            echo -e "${BLUE}[${timestamp}]${NC} ℹ️  $message"
            echo "[${timestamp}] INFO: $message" >> "$LOG_DIR/herald.log"
            ;;
        OK)
            echo -e "${GREEN}[${timestamp}]${NC} ✅ $message"
            echo "[${timestamp}] OK: $message" >> "$LOG_DIR/herald.log"
            ;;
        WARN)
            echo -e "${YELLOW}[${timestamp}]${NC} ⚠️  $message"
            echo "[${timestamp}] WARN: $message" >> "$LOG_DIR/herald.log"
            ;;
        ERROR)
            echo -e "${RED}[${timestamp}]${NC} ❌ $message"
            echo "[${timestamp}] ERROR: $message" >> "$LOG_DIR/herald.log"
            ;;
        *)
            echo "[${timestamp}] $message"
            echo "[${timestamp}] $message" >> "$LOG_DIR/herald.log"
            ;;
    esac
}

# Trap signals for graceful shutdown
cleanup() {
    log INFO "Shutting down HERALD heartbeat..."
    log OK "Total cycles completed: $CYCLE_COUNT"
    exit 0
}

trap cleanup SIGINT SIGTERM

# Startup banner
log INFO "════════════════════════════════════════════════════════════════════════════════"
log INFO "🏙️  AGENT CITY HEARTBEAT STARTED"
log INFO "════════════════════════════════════════════════════════════════════════════════"
log INFO "Root directory: $HERALD_ROOT"
log INFO "Interval: ${INTERVAL}s"
log INFO "Dry run mode: ${DRY_RUN}"
if [ "$CYCLES" -gt 0 ]; then
    log INFO "Will run for $CYCLES cycles, then exit"
else
    log INFO "Will run indefinitely (Ctrl+C to stop)"
fi
log INFO "════════════════════════════════════════════════════════════════════════════════"

# Main loop
while true; do
    CYCLE_COUNT=$((CYCLE_COUNT + 1))

    # Check if we've reached the cycle limit
    if [ "$CYCLES" -gt 0 ] && [ "$CYCLE_COUNT" -gt "$CYCLES" ]; then
        log OK "Reached cycle limit ($CYCLES). Exiting."
        break
    fi

    log INFO ""
    log INFO "════════════════════════════════════════════════════════════════════════════════"
    log INFO "🧠 CYCLE #$CYCLE_COUNT - HERALD WAKING UP"
    log INFO "════════════════════════════════════════════════════════════════════════════════"

    CYCLE_START=$(date +%s)

    # Step 1: Change to HERALD root
    cd "$HERALD_ROOT"
    log INFO "Working directory: $(pwd)"

    # Step 2: Load environment
    if [ -f ".env" ]; then
        # shellcheck disable=SC1091
        source .env
        log OK "Environment loaded from .env"
    else
        log WARN ".env not found. Using system environment only."
    fi

    # Step 3: Ensure Python dependencies are available
    if ! python3 -c "import herald" 2>/dev/null; then
        log WARN "HERALD module not found. Installing dependencies..."
        if [ -f "herald/requirements.txt" ]; then
            pip install -q -r "herald/requirements.txt" 2>/dev/null || \
                log WARN "Failed to install dependencies (continuing anyway)"
        fi
    fi

    # Step 4: Execute HERALD campaign
    log INFO ""
    log INFO "📋 Running HERALD campaign generation..."

    DRY_RUN_FLAG=""
    if [ "$DRY_RUN" = "true" ]; then
        DRY_RUN_FLAG="--dry-run"
    fi

    if python3 herald/shim.py --action run $DRY_RUN_FLAG > "$LOG_DIR/cycle_${CYCLE_COUNT}.log" 2>&1; then
        log OK "Campaign generation succeeded"

        # Step 5: Check if we should publish
        if [ -f "dist/content.json" ] && [ "$DRY_RUN" != "true" ]; then
            log INFO ""
            log INFO "📤 Publishing to configured channels..."

            if python3 herald/shim.py --action publish >> "$LOG_DIR/cycle_${CYCLE_COUNT}.log" 2>&1; then
                log OK "Publishing succeeded"
            else
                log WARN "Publishing encountered issues (check logs)"
            fi
        fi
    else
        log WARN "Campaign generation had issues (check $LOG_DIR/cycle_${CYCLE_COUNT}.log)"
    fi

    CYCLE_END=$(date +%s)
    CYCLE_DURATION=$((CYCLE_END - CYCLE_START))

    log OK "Cycle #$CYCLE_COUNT complete (${CYCLE_DURATION}s elapsed)"

    # Step 6: Wait before next cycle
    log INFO ""
    if [ "$CYCLES" -eq 0 ] || [ "$CYCLE_COUNT" -lt "$CYCLES" ]; then
        log INFO "Next cycle in ${INTERVAL}s (press Ctrl+C to stop)..."
        sleep "$INTERVAL"
    fi
done

log OK "HERALD heartbeat stopped gracefully"
exit 0
