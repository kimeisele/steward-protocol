#!/usr/bin/env python3
"""BOOTSTRAP.PY - The True Entry Point (PHASE 1: SELF-PRESERVATION)

This script implements the Samsara cycle for the Steward Protocol:
1. INIT (Birth): The Mechanic diagnoses the system
2. RUNTIME (Life): The Mechanic heals any brokenness
3. Kernel boot and API gateway startup
4. System runs until shutdown/crash
5. RESTART (Rebirth): User runs bootstrap.py again

The Mechanic (SDLC Manager) runs in standalone mode BEFORE the kernel.
This ensures the system can heal itself from any broken state.

AUTONOMY PRINCIPLE (GAD-000):
- The system fixes itself. No manual git checkout required.
- The system installs dependencies. No manual pip install required.
- The system validates integrity. No manual testing required.

Usage:
    python3 bootstrap.py [--port 8000] [--host 0.0.0.0] [--ledger data/vibe_ledger.db]
"""

import sys
import os
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT))

# PHASE 0: THE MECHANIC RUNS IN STANDALONE MODE
# ============================================================================
print("\n" + "=" * 70)
print("BOOTSTRAP SEQUENCE INITIATED")
print("=" * 70)
print("Phase 0: Mechanic Self-Diagnosis & Healing")
print("=" * 70 + "\n")

from agent_city.registry.mechanic.cartridge_main import MechanicCartridge

mechanic = MechanicCartridge(project_root=PROJECT_ROOT)
system_ready = mechanic.execute_bootstrap()

if not system_ready:
    print("\n" + "❌" * 35)
    print("SYSTEM UNRECOVERABLE - UNABLE TO BOOT")
    print("❌" * 35 + "\n")
    print("Please check the diagnostic report above and fix manually:")
    print("1. Missing dependencies? Run: pip install -r requirements.txt")
    print("2. Broken imports? Check: oracle/cartridge_main.py, run_server.py")
    print("3. Git issues? Run: git status")
    sys.exit(1)

# PHASE 1: KERNEL BOOT (after system is healthy)
# ============================================================================
print("\n" + "=" * 70)
print("Phase 1: Kernel Initialization")
print("=" * 70 + "\n")

try:
    # NOW it's safe to import from the kernel and cartridges
    from run_server import StewardBootLoader

    # Parse command-line arguments
    import argparse

    parser = argparse.ArgumentParser(
        description="Steward Protocol - Autonomous Agent Orchestration"
    )
    parser.add_argument(
        "--port", type=int, default=8000, help="API gateway port (default: 8000)"
    )
    parser.add_argument(
        "--host", default="0.0.0.0", help="API gateway host (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--ledger",
        default="data/vibe_ledger.db",
        help="Path to vibe ledger database (default: data/vibe_ledger.db)",
    )

    args = parser.parse_args()

    # Boot the system
    bootloader = StewardBootLoader(port=args.port, host=args.host, ledger=args.ledger)

    print("\n" + "=" * 70)
    print("Phase 2: Gateway Startup")
    print("=" * 70 + "\n")

    bootloader.run()

except KeyboardInterrupt:
    print("\n\n" + "⚡" * 35)
    print("SYSTEM SHUTDOWN INITIATED (User interrupt)")
    print("⚡" * 35 + "\n")
    sys.exit(0)
except Exception as e:
    print("\n\n" + "❌" * 35)
    print("CRITICAL ERROR DURING BOOT")
    print("❌" * 35 + "\n")
    print(f"Error: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)
