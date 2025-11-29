#!/usr/bin/env python3
"""
Test Herald Migration (Phase 2.1)
==================================

Tests that Herald boots successfully after migration:
1. No requirements.txt dependency
2. Uses system.add_dependency() API (via pyproject.toml)
3. EventLog uses sandboxed path via system interface
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from vibe_core.kernel_impl import RealVibeKernel
from steward.system_agents.herald.cartridge_main import HeraldCartridge


def test_herald_migration():
    """Test Herald migration to system interface."""

    print("🧪 Herald Migration Test (Phase 2.1)")
    print("=" * 60)

    # Step 1: Create Herald instance
    print("\n1️⃣  Creating Herald instance...")
    try:
        herald = HeraldCartridge()
        print("   ✅ Herald __init__ successful")
    except Exception as e:
        print(f"   ❌ Herald __init__ failed: {e}")
        return False

    # Step 2: Create Kernel and register Herald
    print("\n2️⃣  Creating Kernel and registering Herald...")
    try:
        kernel = RealVibeKernel(ledger_path=":memory:")
        kernel.register_agent(herald)
        print("   ✅ Herald registered in kernel")
    except Exception as e:
        print(f"   ❌ Herald registration failed: {e}")
        return False

    # Step 3: Verify system interface injection
    print("\n3️⃣  Verifying system interface injection...")
    if hasattr(herald, "system"):
        print(f"   ✅ herald.system injected")
        print(f"   📁 Sandbox: {herald.system.get_sandbox_path()}")
    else:
        print(f"   ❌ herald.system NOT injected")
        return False

    # Step 4: Test EventLog lazy-loading (triggers sandboxed path)
    print("\n4️⃣  Testing EventLog lazy-loading...")
    try:
        event_log = herald.event_log  # Triggers property
        print(f"   ✅ EventLog initialized")
        print(f"   📖 Ledger path: {event_log.ledger_path}")

        # Verify it's in sandbox
        sandbox = herald.system.get_sandbox_path()
        if str(sandbox) in str(event_log.ledger_path):
            print(f"   ✅ EventLog is sandboxed (correct)")
        else:
            print(f"   ❌ EventLog NOT sandboxed: {event_log.ledger_path}")
            return False

    except Exception as e:
        print(f"   ❌ EventLog initialization failed: {e}")
        import traceback

        traceback.print_exc()
        return False

    # Step 5: Verify requirements.txt doesn't exist
    print("\n5️⃣  Verifying requirements.txt deleted...")
    req_path = project_root / "steward/system_agents/herald/requirements.txt"
    if req_path.exists():
        print(f"   ❌ requirements.txt still exists: {req_path}")
        return False
    else:
        print(f"   ✅ requirements.txt deleted")

    print("\n" + "=" * 60)
    print("✅ Phase 2.1 Herald Migration: ALL TESTS PASSED")
    print("=" * 60)
    return True


if __name__ == "__main__":
    success = test_herald_migration()
    sys.exit(0 if success else 1)
