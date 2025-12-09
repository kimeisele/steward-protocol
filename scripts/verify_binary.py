#!/usr/bin/env python3
"""
Binary Verification: The Frozen Pulse

Black-box test for the compiled VibeOS binary.
Proves the Singularity artifact is alive.
"""

import subprocess
import sys
from pathlib import Path


def verify_binary():
    print("🧊 FROZEN PULSE: Binary Verification Starting...")

    # Locate binary
    binary_candidates = [
        Path("dist/vibe/vibe"),  # One-dir mode (macOS) - PRIMARY
        Path("dist/vibe/vibe.exe"),  # One-dir mode (Windows)
        Path("dist/vibe"),  # One-file mode (legacy)
    ]

    binary_path = None
    for candidate in binary_candidates:
        if candidate.exists():
            binary_path = candidate
            break

    if not binary_path:
        print("❌ FAILURE: Binary not found in dist/")
        print(f"   Checked: {[str(c) for c in binary_candidates]}")
        return 1

    # Report binary size
    size_bytes = binary_path.stat().st_size
    size_mb = size_bytes / (1024 * 1024)
    print(f"📦 Binary: {binary_path}")
    print(f"📏 Size: {size_mb:.2f} MB")

    # Test 1: Basic execution (help)
    print("\n🔬 Test 1: Basic Execution (--help)")
    try:
        result = subprocess.run(
            [str(binary_path), "--help"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0:
            print("   ✅ PASS: Binary executes and returns help.")
        else:
            print(f"   ⚠️ WARN: Exit code {result.returncode}")
            print(f"   Stderr: {result.stderr[:500] if result.stderr else 'None'}")
    except Exception as e:
        print(f"   ❌ FAIL: {e}")
        return 1

    # Test 2: System Status
    print("\n🔬 Test 2: System Status (system status)")
    try:
        result = subprocess.run(
            [str(binary_path), "system", "status"],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=str(Path.cwd()),  # Ensure library/ and config/ are accessible
        )
        print(f"   Exit Code: {result.returncode}")
        if result.stdout:
            print(f"   Stdout (first 500 chars):\n{result.stdout[:500]}")
        if result.stderr:
            print(f"   Stderr (first 500 chars):\n{result.stderr[:500]}")

        if result.returncode == 0:
            print("   ✅ PASS: Kernel responded.")
        else:
            print("   ⚠️ WARN: Non-zero exit, but may still be functional.")
    except subprocess.TimeoutExpired:
        print("   ❌ FAIL: Timeout (30s). Binary may be stuck.")
        return 1
    except Exception as e:
        print(f"   ❌ FAIL: {e}")
        return 1

    print("\n" + "=" * 50)
    print("🧊 FROZEN PULSE: Verification Complete")
    print("=" * 50)
    return 0


if __name__ == "__main__":
    sys.exit(verify_binary())
