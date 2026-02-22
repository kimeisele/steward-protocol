"""
MAHA KERNEL - The Military Grade Deterministic Core
===================================================

"ahaṁ sarvasya prabhavo mattaḥ sarvaṁ pravartate"
"I am the source of all. Everything emanates from Me." (BG 10.8)

MISSION:
    1. ZERO AMBIGUITY. Use MahaModularSynth (Quantum Preset).
    2. ZERO OBJECTS. 16-Bit Address Space (LotusArrayInt).
    3. 16-STEP SEQUENCE. The Standard Algorithm.

ARCHITECTURE:
    Input -> MahaCompression (Seed) -> MahaSynth (Attractor) -> Hybrid Address -> Result
"""

from __future__ import annotations
from vibe_core.mahamantra.protocols._seed import HARE_COUNT


__mahajana__ = "vishnu"
__position__ = 0
__genesis__ = "0x00000000"

import hashlib
import logging
from typing import TYPE_CHECKING, Dict, Optional, Union

from vibe_core.mahamantra.protocols._pancha import PanchaTattvaProtocol, TattvaDict
from vibe_core.mahamantra.substrate.lotus_radix import LotusArrayInt
from vibe_core.mahamantra.adapters.compression import MahaCompression
from vibe_core.mahamantra.substrate.algorithm.maha import MahaModularSynth

if TYPE_CHECKING:
    from vibe_core.mahamantra.protocols._header import MahaCell

logger = logging.getLogger("MAHA_KERNEL")


class MahaKernel(PanchaTattvaProtocol):
    """
    The Military Grade Deterministic Kernel.

    IMPLEMENTS: PanchaTattvaProtocol (Governance)
    USES: LotusArrayInt (16-Bit Flat Memory)
    LOGIC: MahaModularSynth (Quantum) + Variance
    """

    # NAGA BLESSING: MahaKernel IS mahamantra - absolute sovereignty
    _naga_flooded: bool = True

    __slots__ = ("_memory", "_compression", "_ledger", "_singularity", "_synth")

    def __init__(self, ledger_path: str = ":memory:") -> None:
        """
        Initialize the Kernel.
        """
        # 1. 16-Bit Address Space (0-65535) - O(1) Access
        self._memory = LotusArrayInt()

        # 2. Compression Engine (Intent -> Seed)
        self._compression = MahaCompression()

        # 3. The Algorithm (Quantum Preset = Feedback Enabled)
        # This restores the observer effect (Ksetrajna) in the calculation.
        self._synth = MahaModularSynth(default_preset="quantum")

        # 4. LEGACY INFRASTRUCTURE (Required for Governance/Ledger)
        # EKAMEVADVITIYAM: Use the ONE singleton, never create a second.
        from vibe_core.mahamantra.kernel.singularity import mahamantra as _sing

        self._singularity = _sing

        # 5. LEDGER (The Immutable Log)
        from vibe_core.mahamantra import InMemoryLedger, SQLiteLedger

        if ledger_path == ":memory:":
            self._ledger = InMemoryLedger()
        else:
            self._ledger = SQLiteLedger(ledger_path)

        # 6. INJECT LEDGER (System Integration)
        self._inject_ledger()

        logger.info("🕉️ MahaKernel initialized (Standard Quantum Logic)")

    # =========================================================================
    # PANCHA TATTVA PROTOCOL (5 Questions Every Entity Must Answer)
    # =========================================================================

    @property
    def __tattva__(self) -> TattvaDict:
        """The 5-fold truth of MahaKernel."""
        return {
            "chaitanya": "MahaKernel - Military Grade Deterministic Core",
            "nityananda": "LotusArrayInt (65,536 Slots)",
            "advaita": "MahaModularSynth (Quantum)",
            "gadadhara": "Input -> Seed -> Attractor -> Address",
            "srivasa": "PanchaTattvaProtocol Governance",
        }

    # =========================================================================
    # THE CORE: (__call__)
    # =========================================================================

    def __call__(self, input_data: Union[str, "MahaCell"]) -> int:
        """
        EXECUTE THE KERNEL SEQUENCE.

        Algorithm:
        1. Extract 32-bit Seed (Intent).
        2. Calculate Attractor using MahaModularSynth (Quantum).
           This preserves the 'Sacred Mapping' (e.g. Analyze -> 49/Kapila).
        3. Create Hybrid Address: (Attractor << 8) | (Seed & 0xFF).

        Args:
            input_data: Text or MahaCell

        Returns:
            The calculated Address (0-65535) in Lotus Memory.
        """
        # 1. SRAVANAM (Input & Seed Extraction)
        # PROTOCOL: Only str or MahaCell allowed - no fallback!
        seed: int
        if isinstance(input_data, str):
            # Compress text to 32-bit seed (Intent extraction)
            result = self._compression.compress(input_data, extract_summary=False)
            seed = result.seed
        elif hasattr(input_data, "header"):
            # Extract seed from MahaCell header
            seed = input_data.header.sravanam
        else:
            # PROTOCOL VIOLATION: Invalid input type
            # P0-FIX: No fallback - fail explicitly instead of using hash()
            raise TypeError(
                f"MahaKernel requires str or MahaCell input, got {type(input_data).__name__}. "
                f"This is a protocol violation - convert your input to str first."
            )

        # 2. TRANSFORM (The Sacred Path)
        # Use the standard synth to get the correct attractor (0-136)
        attractor = self._synth.transform(seed)

        # 3. VARIANCE (The Detail)
        # Use lower 8 bits of seed for variance within the attractor bucket
        variance = seed & 0xFF

        # 4. FUSION (16-Bit Address)
        # High Byte (8 bits) = Attractor (0-136)
        # Low Byte (8 bits) = Variance (0-255)
        final_address = (attractor << HARE_COUNT) | variance

        return final_address

    # =========================================================================
    # INFRASTRUCTURE (Ledger & Singularity)
    # =========================================================================

    def _inject_ledger(self) -> None:
        """Inject ledger to services via singularity.mod."""
        for guardian in ["brahma", "bhishma", "yamaraja"]:
            try:
                service = getattr(self._singularity.mod, guardian)
                if hasattr(service, "inject_ledger"):
                    service.inject_ledger(self._ledger)
                elif hasattr(service, "ledger"):
                    service.ledger = self._ledger
            except Exception as e:
                logger.debug(f"Could not inject ledger to {guardian}: {e}")

    @property
    def ledger(self):
        """The immutable event ledger."""
        return self._ledger

    @property
    def memory(self) -> LotusArrayInt:
        """Raw access to the memory array."""
        return self._memory

    # =========================================================================
    # SINGLETON ACCESS
    # =========================================================================

    # NOTE: __getattr__ proxy to Singularity was REMOVED (2026-02-17).
    # MahaKernel is for __call__() (Seed→Address), not for routing.
    # Use `from vibe_core.mahamantra import mahamantra` for routing/governance.


# =============================================================================
# SINGLETON
# =============================================================================

_kernel: Optional[MahaKernel] = None


def get_kernel(ledger_path: str = ":memory:") -> MahaKernel:
    """Get the singleton MahaKernel."""
    global _kernel
    if _kernel is None:
        _kernel = MahaKernel(ledger_path)
    return _kernel


def reset_kernel() -> None:
    """Reset the singleton (for testing)."""
    global _kernel
    _kernel = None


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "MahaKernel",
    "get_kernel",
    "reset_kernel",
]
