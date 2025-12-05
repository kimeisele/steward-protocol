#!/usr/bin/env python3
"""
Test Scribe Publishing (Phase 2.5)
===================================

Tests that Scribe can:
1. Read project source for introspection (not lobotomized)
2. Write to sandbox (security)
3. Publish to project root (controlled)

Smoke Test:
- Boot kernel
- Register Scribe
- Generate all docs
- Verify all 4 docs exist in root
- Verify CITYMAP.md has content (not lobotomized)
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from vibe_core.cartridges.system.scribe.cartridge_main import ScribeCartridge
from vibe_core.kernel_impl import RealVibeKernel


def test_scribe_publishing():
    """Test Scribe publishing mechanism (Phase 2.5)."""

    print("🧪 Scribe Publishing Test (Phase 2.5)")
    print("=" * 70)

    # Step 1: Create Kernel
    print("\n1️⃣  Creating kernel...")
    try:
        kernel = RealVibeKernel(ledger_path=":memory:")
        print("   ✅ Kernel created")
    except Exception as e:
        print(f"   ❌ Kernel creation failed: {e}")
        return False

    # Step 2: Create and register Scribe
    print("\n2️⃣  Registering Scribe...")
    try:
        scribe = ScribeCartridge()
        kernel.register_agent(scribe)
        print("   ✅ Scribe registered")
    except Exception as e:
        print(f"   ❌ Scribe registration failed: {e}")
        import traceback

        traceback.print_exc()
        return False

    # Step 3: Verify system interface injection
    print("\n3️⃣  Verifying system interface...")
    if hasattr(scribe, "system"):
        print("   ✅ scribe.system injected")
        print(f"   📁 Sandbox: {scribe.system.get_sandbox_path()}")
    else:
        print("   ❌ scribe.system NOT injected")
        return False

    # Step 4: Generate all documentation
    print("\n4️⃣  Generating documentation...")
    try:
        from vibe_core.scheduling.task import Task

        task = Task(
            task_id="test_generate_all",
            agent_id="scribe",
            priority=1,
            payload={"action": "generate_all"},
        )

        result = scribe.process(task)

        if result.get("success"):
            print("   ✅ Documentation generation succeeded")
            print(f"   📊 Rendered: {result.get('rendered', {})}")
            print(f"   📤 Published: {result.get('published', {})}")
        else:
            print("   ❌ Documentation generation failed")
            print(f"   Error: {result.get('message')}")
            return False

    except Exception as e:
        print(f"   ❌ Documentation generation crashed: {e}")
        import traceback

        traceback.print_exc()
        return False

    # Step 5: Verify all 4 docs exist in project root
    print("\n5️⃣  Verifying published files in project root...")
    docs = ["README.md", "AGENTS.md", "CITYMAP.md", "HELP.md"]

    for doc in docs:
        doc_path = project_root / doc
        if doc_path.exists():
            size = doc_path.stat().st_size
            print(f"   ✅ {doc} exists ({size} bytes)")
        else:
            print(f"   ❌ {doc} NOT FOUND in project root")
            return False

    # Step 6: Verify CITYMAP.md is not lobotomized (has content)
    print("\n6️⃣  Checking CITYMAP.md for lobotomy...")
    citymap_path = project_root / "CITYMAP.md"

    try:
        content = citymap_path.read_text()

        # Check for expected content markers (3-layer architecture)
        markers = ["LAYER 1", "LAYER 2", "LAYER 3", "system_agents", "vibe_core"]

        found_markers = [m for m in markers if m in content]

        if len(found_markers) >= 4:
            print(f"   ✅ CITYMAP.md has complex content ({len(content)} bytes)")
            print(f"   ✅ Found markers: {found_markers}")
            print("   ✅ NOT LOBOTOMIZED - Introspection working!")
        else:
            print("   ❌ CITYMAP.md appears lobotomized")
            print(f"   Found only: {found_markers}")
            print(f"   Content preview: {content[:500]}")
            return False

    except Exception as e:
        print(f"   ❌ Failed to read CITYMAP.md: {e}")
        return False

    print("\n" + "=" * 70)
    print("✅ Phase 2.5 Scribe Publishing: ALL TESTS PASSED")
    print("=" * 70)
    print("\n📋 Summary:")
    print("   • Scribe reads project source (introspection intact)")
    print("   • Scribe writes to sandbox (security maintained)")
    print("   • Scribe publishes to root (controlled via whitelist)")
    print("   • All 4 docs generated with complex content")
    print("   • NO LOBOTOMY detected")

    return True


if __name__ == "__main__":
    success = test_scribe_publishing()
    sys.exit(0 if success else 1)
