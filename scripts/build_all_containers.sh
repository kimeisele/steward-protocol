#!/bin/bash
# =============================================================================
# Build All Vibe Containers (.vibe)
# =============================================================================
# OPUS-020: Container Migration Strategy
#
# Usage:
#   ./scripts/build_all_containers.sh           # Build all to dist/plugins/
#   ./scripts/build_all_containers.sh --inplace # Build next to source folders
#
# The script:
# 1. Discovers all plugins with manifest.json
# 2. Signs each with ECDSA (.steward/keys/)
# 3. Outputs to dist/plugins/ (default) or next to source (--inplace)
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
PLUGINS_DIR="$PROJECT_ROOT/vibe_core/plugins"
OUTPUT_DIR="$PROJECT_ROOT/dist/plugins"
PACKER="$PROJECT_ROOT/scripts/pack_vibe.py"

# Parse arguments
INPLACE=false
for arg in "$@"; do
    case $arg in
        --inplace)
            INPLACE=true
            shift
            ;;
    esac
done

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}📦 Building Vibe Containers${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Create output directory
if [ "$INPLACE" = false ]; then
    mkdir -p "$OUTPUT_DIR"
    echo -e "Output: ${YELLOW}$OUTPUT_DIR${NC}"
else
    echo -e "Output: ${YELLOW}In-place (next to source folders)${NC}"
fi

# Counter
BUILT=0
SKIPPED=0
FAILED=0

# Find all plugin directories with manifest.json
for plugin_dir in "$PLUGINS_DIR"/*/; do
    plugin_name=$(basename "$plugin_dir")

    # Skip __pycache__ and hidden directories
    if [[ "$plugin_name" == __* ]] || [[ "$plugin_name" == .* ]]; then
        continue
    fi

    # Check for manifest
    if [ -f "$plugin_dir/manifest.json" ]; then
        manifest_type="manifest.json"
    elif [ -f "$plugin_dir/steward.json" ]; then
        manifest_type="steward.json"
    else
        echo -e "  ${YELLOW}⏭️  $plugin_name${NC} - No manifest, skipping"
        ((SKIPPED++))
        continue
    fi

    # Check for tests directory (OPUS-020: HARD FAIL without tests)
    if [ ! -d "$plugin_dir/tests" ]; then
        echo -e "  ${YELLOW}⏭️  $plugin_name${NC} - No tests/ directory, skipping"
        ((SKIPPED++))
        continue
    fi

    # Determine output path
    if [ "$INPLACE" = true ]; then
        output_path="$PLUGINS_DIR/$plugin_name.vibe"
    else
        output_path="$OUTPUT_DIR/$plugin_name.vibe"
    fi

    # Build container
    echo -e "  📦 Building ${GREEN}$plugin_name${NC}..."
    if python "$PACKER" "$plugin_dir" -o "$output_path" 2>&1 | sed 's/^/     /'; then
        ((BUILT++))
    else
        echo -e "  ${RED}❌ Failed to build $plugin_name${NC}"
        ((FAILED++))
    fi
done

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}✅ Built:${NC} $BUILT containers"
echo -e "${YELLOW}⏭️  Skipped:${NC} $SKIPPED (no manifest or tests)"
if [ $FAILED -gt 0 ]; then
    echo -e "${RED}❌ Failed:${NC} $FAILED"
    exit 1
fi

# List output
if [ "$INPLACE" = false ] && [ $BUILT -gt 0 ]; then
    echo ""
    echo "Containers in $OUTPUT_DIR:"
    ls -lh "$OUTPUT_DIR"/*.vibe 2>/dev/null || true
fi

echo ""
echo -e "${GREEN}Done!${NC}"
