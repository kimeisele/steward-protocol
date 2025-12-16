#!/usr/bin/env python3
"""
Kernel Boot Test - CI/CD Script

Minimal kernel boot test - verify kernel can initialize.
Extracted from inline YAML script for maintainability.
"""

import os
import sys

# Add project to path
sys.path.insert(0, os.getcwd())


def test_kernel_import():
    """Test that kernel modules can be imported"""
    try:
        from vibe_core.kernel_impl import RealVibeKernel
        from vibe_core.plugin_loader import PluginLoader
        from vibe_core.protocols import VibeKernel

        print("✅ All kernel modules imported successfully")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False


def test_kernel_init():
    """Test that kernel can be instantiated"""
    try:
        from vibe_core.kernel_impl import RealVibeKernel

        kernel = RealVibeKernel()
        print("✅ Kernel instantiated successfully")
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
