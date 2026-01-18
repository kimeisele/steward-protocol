#!/usr/bin/env python3
"""
Kernel Boot Test - CI/CD Script

Minimal kernel boot test - verify kernel can initialize.
Extracted from inline YAML script for maintainability.

PROTOCOL COMPLIANCE:
- Uses VibeFactory (not direct RealVibeKernel import)
- "Der Kernel darf nicht direkt angefasst werden." - Senior Architect
- See: vibe_core/factory.py
"""

import os
import sys

# Add project to path
sys.path.insert(0, os.getcwd())


def test_kernel_import():
    """Test that kernel modules can be imported via Factory (DIP compliant)"""
    try:
        # CORRECT: Import via Factory, not direct kernel_impl
        from vibe_core.factory import VibeFactory
        from vibe_core.protocols.kernel_protocol import KernelProtocol

        print("✅ Factory and Protocol imports OK")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False


def test_kernel_init():
    """Test that kernel can be instantiated via VibeFactory"""
    try:
        # CORRECT: Use Factory pattern, not direct instantiation
        from vibe_core.factory import VibeFactory

        kernel = VibeFactory.get_test_kernel()
        print("✅ Kernel instantiated via VibeFactory successfully")
        return True
    except Exception as e:
        print(f"❌ Kernel init failed: {e}")
        return False


if __name__ == "__main__":
    results = []
    results.append(test_kernel_import())
    results.append(test_kernel_init())

    if all(results):
        print("\n✅ All tests passed")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed")
        sys.exit(1)
