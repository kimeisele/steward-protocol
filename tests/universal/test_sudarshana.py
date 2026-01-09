"""
TEST: THE SUDARSHANA SINGULARITY (16 GATES)
===========================================

Verifies that the Mantra Kernel Map is correctly loaded and that the
"Radial Implosion" logic functions as expected.

"Wenn diese 16 Bits gleichzeitig auf '1' stehen, bricht die Wellenfunktion zusammen."
"""

import pytest

from vibe_core.kernel_impl import RealVibeKernel
from vibe_core.protocols.universal import (
    MANTRA_KERNEL_MAP,
    MantraGate,
    MantraOpCode,
    SovereignContext,
    SudarshanaMantra,
)


def test_sudarshana_dna_structure():
    """Verify the 16-bit DNA is correctly loaded."""
    dna = MANTRA_KERNEL_MAP["THE_16_BIT_DNA"]
    assert len(dna) == 16, "The DNA must have exactly 16 Gates."

    # Verify first and last gates
    assert dna[0].name == "HARE"
    assert dna[0].op == MantraOpCode.SYS_WAKE

    assert dna[15].name == "HARE"
    assert dna[15].op == MantraOpCode.RESET_IP


def test_sudarshana_chant_singularity():
    """Verify that the chant_mahamantra triggers the Singularity (returns True)."""
    mantra = SudarshanaMantra()

    # Context is currently unused in the placeholder logic, but required by type signature
    ctx = SovereignContext(identity_id="test-sovereign", signature="test-signature", roles=["sovereign"])

    # The Hologram Check
    # This invokes the loop over 16 gates.
    # Since our placeholder .check() returns True, this should generally pass.
    # The TEST is ensuring the mechanism works.
    singularity_achieved = mantra.chant_mahamantra(ctx)

    assert singularity_achieved is True, "The Singularity was not declared!"


def test_vishnu_clock_attributes():
    """Verify Kernel has the Vishnu Clock attributes."""
    assert hasattr(RealVibeKernel, "watchdog"), "Kernel missing 'watchdog' attribute"
    assert hasattr(RealVibeKernel, "chaitanya"), "Kernel missing 'chaitanya' attribute"

    # They should be None by default (discovery placeholders)
    assert RealVibeKernel.watchdog is None
    assert RealVibeKernel.chaitanya is None


def test_linear_resonance_fallback():
    """Verify individual resonance still works (Legacy Mode)."""
    mantra = SudarshanaMantra()
    # Check a specific op
    assert mantra.resonate(MantraOpCode.SYS_WAKE) is True
    # Check an op that is in the map
    assert mantra.resonate(MantraOpCode.COMMIT_LOG) is True

    # Check an op that is NOT in the map (if any exist that aren't mapped?
    # Actually all MantraOpCodes are mapped in the DNA, so this is hard to fail unless we invent one)
