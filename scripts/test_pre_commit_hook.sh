#!/bin/bash
#
# Test Pre-Commit Hook (Phase 3.1)
# =================================
# Verifies that the electric fence works correctly
#

set -e

REPO_ROOT=$(git rev-parse --show-toplevel)
HOOK="$REPO_ROOT/.githooks/pre-commit"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "🧪 Testing Pre-Commit Hook (Phase 3.1)"
echo "======================================"
echo ""

# Test 1: Hook is executable
echo -n "Test 1: Hook is executable... "
if [ -x "$HOOK" ]; then
    echo -e "${GREEN}PASS${NC}"
else
    echo -e "${RED}FAIL${NC}"
    echo "Hook is not executable. Run: chmod +x .githooks/pre-commit"
    exit 1
fi

# Test 2: Hook runs without errors on clean repo
echo -n "Test 2: Hook passes on clean repo... "
if "$HOOK" > /dev/null 2>&1; then
    echo -e "${GREEN}PASS${NC}"
else
    echo -e "${RED}FAIL${NC}"
    echo "Hook failed on clean repository"
    exit 1
fi

# Test 3: Create a violation (requirements.txt) and test detection
echo -n "Test 3: Detects requirements.txt violation... "

# Create a test requirements.txt
TEST_FILE="steward/system_agents/test_agent/requirements.txt"
mkdir -p "steward/system_agents/test_agent"
echo "pytest==7.0.0" > "$TEST_FILE"

# Stage it
git add "$TEST_FILE" 2>/dev/null || true

# Run hook (should fail)
if "$HOOK" > /dev/null 2>&1; then
    echo -e "${RED}FAIL${NC}"
    echo "Hook did NOT detect requirements.txt violation"
    # Cleanup
    git reset HEAD "$TEST_FILE" 2>/dev/null || true
    rm -rf "steward/system_agents/test_agent"
    exit 1
else
    echo -e "${GREEN}PASS${NC}"
fi

# Cleanup
git reset HEAD "$TEST_FILE" 2>/dev/null || true
rm -rf "steward/system_agents/test_agent"

# Test 4: Create Path("data/") violation
echo -n "Test 4: Detects Path('data/...') violation... "

TEST_FILE="steward/system_agents/test_agent/cartridge_main.py"
mkdir -p "steward/system_agents/test_agent"
cat > "$TEST_FILE" << 'PYEOF'
from pathlib import Path

class TestAgent:
    def __init__(self):
        self.data_path = Path("data/test")  # VIOLATION
PYEOF

git add "$TEST_FILE" 2>/dev/null || true

if "$HOOK" > /dev/null 2>&1; then
    echo -e "${RED}FAIL${NC}"
    echo "Hook did NOT detect Path('data/...') violation"
    git reset HEAD "$TEST_FILE" 2>/dev/null || true
    rm -rf "steward/system_agents/test_agent"
    exit 1
else
    echo -e "${GREEN}PASS${NC}"
fi

# Cleanup
git reset HEAD "$TEST_FILE" 2>/dev/null || true
rm -rf "steward/system_agents/test_agent"

# Test 5: Valid code passes
echo -n "Test 5: Valid agent code passes... "

TEST_FILE="steward/system_agents/test_agent/cartridge_main.py"
mkdir -p "steward/system_agents/test_agent"
cat > "$TEST_FILE" << 'PYEOF'
from pathlib import Path
from vibe_core.protocols import VibeAgent

class TestAgent(VibeAgent):
    def __init__(self):
        super().__init__(agent_id="test", name="Test")
        # PHASE 2.3: Lazy-load paths
        self._data_path = None

    @property
    def data_path(self):
        if self._data_path is None:
            self._data_path = self.system.get_sandbox_path() / "data"
        return self._data_path
PYEOF

git add "$TEST_FILE" 2>/dev/null || true

if "$HOOK" > /dev/null 2>&1; then
    echo -e "${GREEN}PASS${NC}"
else
    echo -e "${RED}FAIL${NC}"
    echo "Hook blocked valid code"
    git reset HEAD "$TEST_FILE" 2>/dev/null || true
    rm -rf "steward/system_agents/test_agent"
    exit 1
fi

# Cleanup
git reset HEAD "$TEST_FILE" 2>/dev/null || true
rm -rf "steward/system_agents/test_agent"

echo ""
echo "======================================"
echo -e "${GREEN}✅ All tests passed!${NC}"
echo ""
echo "The Electric Fence is operational."
echo ""
echo "To install:"
echo "  ln -sf ../../.githooks/pre-commit .git/hooks/pre-commit"
echo ""
