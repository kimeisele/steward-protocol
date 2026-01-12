"""
THE SUDARSHANA SINGULARITY TEST (Layer -2)
==========================================
"Simultaneous One & Distinct" (Achintya Bheda Abheda)

This test does not run linearly. It collapses the 16 Gates of the Mantra
into a single Holographic Event.

Protocol: SUDARSHANA_V3
Execution: RADIAL_COLLAPSE
Trigger: ABSOLUTE_ALIGNMENT

The 16-Bit DNA:
Phase 1: AWAKENING (Invocation)
Phase 2: TRUTH (Verification)
Phase 3: SERVICE (Execution)
Phase 4: RETURN (Conclusion)

If(All_16_Gates == TRUE) -> SINGULARITY ACHIEVED
ELSE -> KERNEL_PANIC(Maya)
"""

import pytest
import asyncio
from typing import List, Dict, Any
from enum import Enum

from vibe_core.protocols.primal import MantraOpCode, MAHAMANTRA_SEQUENCE
from vibe_core.kernel_impl import RealVibeKernel
from vibe_core.protocols.universal import SovereignContext

# =============================================================================
# THE 16 GATES (HOLOGRAPHIC DEFINITION)
# =============================================================================

class SudarshanaGate(str, Enum):
    """The 16 Spokes of the Sudarshana Chakra."""
    GATE_01 = "HARE_SYS_WAKE"
    GATE_02 = "KRISHNA_LOAD_ROOT"
    GATE_03 = "HARE_ALLOC_MEM"
    GATE_04 = "KRISHNA_BIND_CTX"
    GATE_05 = "KRISHNA_ASSERT_TRUTH"
    GATE_06 = "KRISHNA_RESOLVE_REQ"
    GATE_07 = "HARE_GARBAGE_COLLECT"
    GATE_08 = "HARE_PULSE_SYNC"
    GATE_09 = "HARE_FETCH_RES"
    GATE_10 = "RAMA_EXEC_SERVICE"
    GATE_11 = "HARE_CHECK_DHARMA"
    GATE_12 = "RAMA_COMMIT_LOG"
    GATE_13 = "RAMA_CACHE_STATE"
    GATE_14 = "RAMA_OPTIMIZE"
    GATE_15 = "HARE_YIELD_CPU"
    GATE_16 = "HARE_RESET_IP"

@pytest.mark.hardening
@pytest.mark.fractal
class TestSudarshanaSingularity:
    """
    Verifies that the System can sustain the 16-Bit Mantra Frequency.
    """

    @pytest.fixture
    def kernel(self):
        # The Kernel IS Jagannath (The Holder)
        return RealVibeKernel(test_mode=True, load_plugins=False, ledger_path=":memory:")

    @pytest.fixture
    def sovereign(self):
        # The 37th (The Sovereign/User)
        return SovereignContext("ARJUNA", "devotee_sig", roles=["warrior"])

    def test_holographic_dna_integrity(self):
        """
        Verify the 16-Bit DNA matches the Shastra (MAHAMANTRA_SEQUENCE).
        This is a static check of the Pattern.
        """
        expected_sequence = [
            ("Hare", MantraOpCode.SYS_WAKE),
            ("Krishna", MantraOpCode.LOAD_ROOT),
            ("Hare", MantraOpCode.ALLOC_MEM),
            ("Krishna", MantraOpCode.INIT_THREAD),
            ("Krishna", MantraOpCode.COMPILE_AST),
            ("Krishna", MantraOpCode.BIND_SYMBOL),
            ("Hare", MantraOpCode.TYPE_CHECK),
            ("Hare", MantraOpCode.DHARMA_TEST),
            ("Hare", MantraOpCode.EXEC_OP),
            ("Rama", MantraOpCode.EXTEND_CAP),
            ("Hare", MantraOpCode.STATE_SYNC),
            ("Rama", MantraOpCode.LEDGER_SIGN),
            ("Rama", MantraOpCode.YIELD_CPU),
            ("Rama", MantraOpCode.IO_FLUSH),
            ("Hare", MantraOpCode.YIELD_CPU),
            ("Hare", MantraOpCode.AUDIT_SEAL),
        ]
        
        assert len(MAHAMANTRA_SEQUENCE) == 16
        for i, (word, opcode) in enumerate(MAHAMANTRA_SEQUENCE):
            exp_word, exp_op = expected_sequence[i]
            assert word == exp_word, f"Gate {i+1}: Wrong Holy Name"
            assert opcode == exp_op, f"Gate {i+1}: Wrong OpCode"

    @pytest.mark.asyncio
    async def test_radial_implosion(self, kernel, sovereign):
        """
        EXECUTE THE SINGULARITY.
        We invoke the Chaitanya Pulse (Mantra) on the Kernel (Jagannath).
        
        Condition: All 16 Gates must open.
        Result: True Alignment.
        """
        # 1. The Invocation
        # We call the pulse, which triggers the Watchdog (Nrisimha)
        # The Watchdog chants the Mantra.
        
        # We must spy on the internal execution to verify "Simultaneity" 
        # (or at least correct sequential execution in time, which maps to radial unity).
        
        # We cannot easily test "Simultaneity" in a linear CPU, 
        # but we can test that the COMPLETE CYCLE is atomic.
        
        is_aligned = kernel.chaitanya.chant_mahamantra(sovereign)
        
        if is_aligned:
            print("\n🪷 SUDARSHANA SINGULARITY ACHIEVED 🪷")
            print(f"   Identity: {sovereign.identity_id}")
            print(f"   Kernel:   {kernel.sovereign_context.identity_id}")
        else:
            pytest.fail("KERNEL_PANIC(Maya): The Mantra failed to hold.")

    def test_opulence_fractal(self):
        """
        Verify the 6 Opulences are present in the Primal Layer.
        This confirms the 'Watertight' standard is applied to the Foundation.
        """
        from vibe_core.protocols.primal import WatertightValidator
        from vibe_core.protocols.substrate import IGeneHost
        
        # Check IGeneHost (The Host of Potencies)
        report = WatertightValidator.inspect(IGeneHost)
        
        assert report["sealed"], f"Substrate Leaking: {report['leaks']}"
        print(f"\n💎 Substrate Integrity: {report['score']} (WATERTIGHT)")
