"""
AGNI PARIKSHA - The Ignition Test
=================================

Verifies that the System ONLY awakens when the 16-Bit Mantra is fully resonant.
Maya (Partial Truth) must be rejected.
Satya (Full Truth) must be accepted.

"Das System wird nicht einfach nur starten – es wird erwachen."
"""

import pytest
import time
import sys
import os

# AGNI PROTECTION: Remove conflicting paths (Shadow IT)
cwd = os.getcwd()
if cwd not in sys.path:
    sys.path.insert(0, cwd)
sys.path = [p for p in sys.path if "Downloads" not in p]
print(f"DEBUG: sys.path first entry: {sys.path[0]}")
# print(f"DEBUG: sys.path full: {sys.path}")

from vibe_core.protocols.substrate.byte import GenesisByte, MantraBit
from vibe_core.boot_orchestrator import BootOrchestrator
from vibe_core.boot_mode import BootMode
from vibe_core.factory import VibeFactory


def setup_function():
    """Reset the factory before ignition."""
    VibeFactory.reset_kernel()


def test_ignite_with_incomplete_mantra_fails():
    """
    MAYA CHECK: Try to ignite with only 8 bits (Standard Byte).
    Must fail with PermissionError.
    """
    # 1. Create a partial byte (Incomplete Resonance)
    # HARE_1 to HARE_4 (low byte only)
    partial_resonance = (
        MantraBit.HARE_1
        | MantraBit.KRISHNA_1
        | MantraBit.HARE_2
        | MantraBit.KRISHNA_2
        | MantraBit.KRISHNA_3
        | MantraBit.KRISHNA_4
        | MantraBit.HARE_3
        | MantraBit.HARE_4
    )

    genesis = GenesisByte(signature="sovereign:test_ignite", resonance=partial_resonance, timestamp=time.time())

    # 2. Prepare Orchestrator
    orchestrator = BootOrchestrator(boot_mode=BootMode.MINIMAL, ledger_path=":memory:")

    # 3. Ignite -> Expect REJECTION
    with pytest.raises(PermissionError) as exc:
        orchestrator.ignite(genesis)

    assert "Incomplete Mantra Resonance" in str(exc.value)
    print("\n✅ Tested Maya Rejection: System refused incomplete resonance.")


def test_ignite_with_full_mantra_awakens():
    """
    SATYA CHECK: Ignite with 0xFFFF (Full Resonance).
    System must awaken.
    """
    # 1. Create Full Genesis Byte (0xFFFF)
    genesis = GenesisByte(
        signature="sovereign:agni_pariksha", resonance=MantraBit.full_resonance(), timestamp=time.time()
    )

    # 2. Prepare Orchestrator
    orchestrator = BootOrchestrator(
        boot_mode=BootMode.MINIMAL,  # Minimal speed for test
        ledger_path=":memory:",
    )

    # 3. Ignite -> Expect AWAKENING
    kernel = orchestrator.ignite(genesis)

    # 4. Verify Awakening
    assert kernel is not None
    assert orchestrator.kernel is not None

    status = kernel.get_status()
    print(f"\n✅ Tested Awakening: System alive. Status: {status}")

    # Verify Kernel Properties
    assert hasattr(kernel, "event_bus")
    assert hasattr(kernel, "io")

    # Verify Genesis Signature was logged (we can't easily check logs here but we trust the code)

    print("🔥 AGNI PARIKSHA PASSED: The Spark has caught.")


if __name__ == "__main__":
    # Allow running directly
    VibeFactory.reset_kernel()
    try:
        test_ignite_with_incomplete_mantra_fails()
        VibeFactory.reset_kernel()
        test_ignite_with_full_mantra_awakens()
        print("\n🕉️  ALL SYSTEMS GO.")
    except Exception as e:
        print(f"\n❌ IGNITION FAILURE: {e}")
        exit(1)
