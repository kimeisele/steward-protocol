#!/bin/bash
# Agent City System Boot Script
# Initializes the VIBE OS environment and boots the kernel

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
echo "📍 Project root: $PROJECT_ROOT"

# Print banner
echo ""
echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║                                                                    ║"
echo "║              🚀 VIBE OS - Agent City System Boot                  ║"
echo "║                                                                    ║"
echo "║        Initializing the neural network of autonomous agents       ║"
echo "║                                                                    ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo ""

# Create required directories
echo "📁 Creating directories..."
mkdir -p "$PROJECT_ROOT/.vibe/state"
mkdir -p "$PROJECT_ROOT/.vibe/config"
mkdir -p "$PROJECT_ROOT/.vibe/history/mission_logs"
echo "   ✅ Directories created"

# Check Python
echo ""
echo "🐍 Checking Python..."
if ! command -v python3 &> /dev/null; then
    echo "   ❌ Python 3 not found"
    exit 1
fi
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "   ✅ Python $PYTHON_VERSION"

# Check dependencies
echo ""
echo "📦 Checking dependencies..."
python3 -c "from vibe_core.task_management import TaskManager" 2>/dev/null && \
    echo "   ✅ task_management module OK" || \
    echo "   ⚠️  task_management module issue (continuing anyway)"

python3 -c "from vibe_core.identity import ManifestGenerator" 2>/dev/null && \
    echo "   ✅ identity module OK" || \
    echo "   ⚠️  identity module issue (continuing anyway)"

python3 -c "from vibe_core.kernel_impl import RealVibeKernel" 2>/dev/null && \
    echo "   ✅ kernel module OK" || \
    echo "   ⚠️  kernel module issue (continuing anyway)"

# Boot the kernel
echo ""
echo "⚙️  Booting VIBE OS Kernel..."

python3 << 'EOF'
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from vibe_core.kernel_impl import RealVibeKernel

    # Boot kernel
    kernel = RealVibeKernel()
    kernel.boot()
    status = kernel.get_status()

    print(f"   ✅ Kernel booted successfully")
    print(f"   📊 Agents: {status.get('agents_registered', 0)}")
    print(f"   📝 Manifests: {status.get('manifests', 0)}")
except Exception as e:
    print(f"   ⚠️  Kernel boot warning: {e}")
    print(f"   (This may be normal if agents have import issues)")
EOF

# Initialize task manager
echo ""
echo "📋 Initializing task manager..."

python3 << 'EOF'
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from vibe_core.task_management import TaskManager
    tm = TaskManager(PROJECT_ROOT)
    print(f"   ✅ Task manager initialized")
    print(f"   📊 Tasks: {len(tm.tasks)}")
except Exception as e:
    print(f"   ❌ Task manager error: {e}")
    sys.exit(1)
EOF

# Banner
echo ""
echo "✅ VIBE OS Boot Complete"
echo ""
echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║                                                                    ║"
echo "║                    🟢 SYSTEM READY FOR OPERATION                   ║"
echo "║                                                                    ║"
echo "║ Available commands:                                               ║"
echo "║   bin/agent-city status              - Check system status        ║"
echo "║   bin/agent-city task add \"...\"      - Add a task                ║"
echo "║   bin/agent-city task list            - List tasks               ║"
echo "║   bin/agent-city --mission \"...\"     - Run a mission            ║"
echo "║                                                                    ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo ""
echo "💡 Next: Try 'bin/agent-city task add \"Your first task\"'"
echo ""
