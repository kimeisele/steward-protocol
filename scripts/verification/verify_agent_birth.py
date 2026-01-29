#!/usr/bin/env python3
"""
VERIFY AGENT BIRTH (End-to-End)
===============================
Tests the full stack:
VibeOS -> DeterministicExecutor -> CircuitExecutor -> Kernel -> Agent Registry

Usage:
    python verify_agent_birth.py
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "yamaraja"
__position__ = 15
__genesis__ = "0x0520a450"  # GenesisByte: parampara % 37 == 0

import asyncio
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("VERIFY_BIRTH")

# Import VibeOS components
from vibe_core.kernel_impl import RealVibeKernel
from vibe_core.vibe_os import VibeOS


async def main():
    print("⚡️ STARTING END-TO-END AGENT BIRTH TEST")
    print("==================================================")

    # 1. Setup Environment
    ledger_path = Path("data/test_ledger.db")
    if ledger_path.exists():
        ledger_path.unlink()

    # 2. Initialize Kernel
    print("🔌 Initializing Kernel...")
    kernel = RealVibeKernel(ledger_path=str(ledger_path))

    # 3. Initialize VibeOS
    print("🖥️  Initializing VibeOS...")
    vibe = VibeOS(kernel=kernel)
    await vibe.boot()

    # 4. Trigger Agent Birth
    input_text = "Spawn a new agent named 'Socrates' with role 'Philosopher'"
    print(f"\n📥 SENDING INPUT: '{input_text}'")

    result = await vibe.process(input_text)

    print("\n📋 RESULT:")
    print(result)

    # 5. Verify Kernel Registry
    print("\n🔍 VERIFYING REGISTRY:")
    # The agent ID is usually generated or derived.
    # AGENT_BIRTH circuit usually creates an agent.
    # Let's check if ANY agent was registered (besides system agents).

    agents = kernel.list_agents()
    print(f"   Registered Agents: {agents}")

    found = False
    for agent_id in agents:
        if "socrates" in agent_id.lower():
            found = True
            print(f"   ✅ Found Socrates: {agent_id}")
            break

    if found:
        print("\n✅ TEST PASSED: Agent successfully spawned via VibeOS")
    else:
        print("\n❌ TEST FAILED: Socrates not found in registry")


if __name__ == "__main__":
    asyncio.run(main())
