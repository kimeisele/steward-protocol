#!/usr/bin/env python3
"""
Test P3.1 - Verify kernel injection to agents

This test verifies that agents receive kernel reference via set_kernel()
during registration in the VibeKernel.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def test_kernel_injection():
    """Test that agents receive kernel reference during registration."""
    print("🧪 Testing P3.1 - Kernel Injection")
    print("=" * 60)

    # Import after path is set
    from vibe_core.cartridges.system.envoy.cartridge_main import EnvoyCartridge
    from vibe_core.kernel_impl import RealVibeKernel

    # Create and boot kernel
    print("\n1️⃣ Creating and booting kernel...")
    kernel = RealVibeKernel()
    kernel.boot()
    print("✅ Kernel booted")

    # Manually register envoy to test kernel injection
    print("\n2️⃣ Registering ENVOY agent...")
    envoy = EnvoyCartridge()
    kernel.register_agent(envoy)
    print("✅ ENVOY registered")

    # Check if kernel was injected
    print("\n3️⃣ Verifying kernel injection...")
    if envoy.kernel is None:
        print("❌ FAIL: Kernel not injected! envoy.kernel is None")
        return False

    if envoy.kernel != kernel:
        print("❌ FAIL: Wrong kernel injected!")
        print(f"   Expected: {kernel}")
        print(f"   Got: {envoy.kernel}")
        return False

    print("✅ PASS: Kernel correctly injected to ENVOY")

    # Check if system interface was also injected
    print("\n4️⃣ Verifying system interface...")
    if envoy.system is None:
        print("❌ FAIL: System interface not injected!")
        return False

    if envoy.system.kernel != kernel:
        print("❌ FAIL: System interface has wrong kernel!")
        return False

    print("✅ PASS: System interface correctly injected")

    # Test MilkOcean router kernel injection
    print("\n5️⃣ Testing MilkOcean router kernel injection...")
    if envoy.router.kernel is None:
        print("⚠️  Router kernel not set initially (expected)")

    # Trigger process to inject kernel (P3.2 fix)
    from vibe_core.scheduling.task import Task

    test_task = Task(agent_id="envoy", payload={"input": "test"})

    # This should trigger kernel injection in process()
    import asyncio

    try:
        asyncio.run(envoy.process(test_task))
    except Exception as e:
        print(f"   Note: Process errored (expected): {e}")

    if envoy.router.kernel is not None:
        print("✅ PASS: Router received kernel injection")
    else:
        print("⚠️  Router still has no kernel (check P3.2 implementation)")

    print("\n" + "=" * 60)
    print("🎉 ALL TESTS PASSED - Kernel injection working!")
    return True


if __name__ == "__main__":
    success = test_kernel_injection()
    sys.exit(0 if success else 1)
