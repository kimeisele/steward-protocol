"""
MAHA KERNEL - The Military Grade Deterministic Core
===================================================

"ahaṁ sarvasya prabhavo mattaḥ sarvaṁ pravartate"
"I am the source of all. Everything emanates from Me." (BG 10.8)

MISSION:
    1. ZERO AMBIGUITY. Prime Field Mathematics (65521).
    2. ZERO OBJECTS. 16-Bit Address Space (LotusArrayInt).
    3. 16-STEP SEQUENCE. The Chatuh-Sloki Logic.

ARCHITECTURE:
    Input -> MahaCompression (Seed) -> Mantra Logic (Prime Field) ^ Jiva Identity -> Address -> Result
"""

from __future__ import annotations

__mahajana__ = "vishnu"
__position__ = 0
__genesis__ = "0x00000000"

import logging
from typing import TYPE_CHECKING, Any, Dict, Optional, Union

from vibe_core.mahamantra.protocols._pancha import PanchaTattvaProtocol, TattvaDict
from vibe_core.mahamantra.protocols._seed import (
    WORDS, MAHA_QUANTUM, SEVEN, TEN, 
    MAHAMANTRA_WORD_PATTERN, MAHAMANTRA_NAME_HARE, MAHAMANTRA_NAME_KRISHNA, MAHAMANTRA_NAME_RAMA
)
from vibe_core.mahamantra.research.lotus_tree import LotusArrayInt
from vibe_core.mahamantra.adapters.compression import MahaCompression

if TYPE_CHECKING:
    from vibe_core.mahamantra.protocols._header import MahaCell

logger = logging.getLogger("MAHA_KERNEL")


class MahaKernel(PanchaTattvaProtocol):
    """
    The Military Grade Deterministic Kernel.
    
    IMPLEMENTS: PanchaTattvaProtocol (Governance)
    USES: LotusArrayInt (16-Bit Flat Memory)
    LOGIC: Prime Field (65521) + Jiva XOR
    """

    # NAGA BLESSING: MahaKernel IS mahamantra - absolute sovereignty
    _naga_flooded: bool = True

    __slots__ = ("_memory", "_compression", "_ledger", "_singularity")

    def __init__(self, ledger_path: str = ":memory:") -> None:
        """
        Initialize the Kernel with 65,536 units of flat memory.
        """
        # 1. 16-Bit Address Space (0-65535) - O(1) Access
        self._memory = LotusArrayInt()
        
        # 2. Compression Engine (Intent -> Seed)
        self._compression = MahaCompression()
        
        # 3. LEGACY INFRASTRUCTURE (Required for Governance/Ledger)
        from vibe_core.mahamantra.kernel.singularity import Mahamantra
        self._singularity = Mahamantra()

        # 4. LEDGER (The Immutable Log)
        from vibe_core.mahamantra import InMemoryLedger, SQLiteLedger
        if ledger_path == ":memory:":
            self._ledger = InMemoryLedger()
        else:
            self._ledger = SQLiteLedger(ledger_path)

        # 5. INJECT LEDGER (System Integration)
        self._inject_ledger()

        logger.info("🕉️ MahaKernel initialized (Military Grade: Prime Field + Jiva XOR)")

    # =========================================================================
    # PANCHA TATTVA PROTOCOL (5 Questions Every Entity Must Answer)
    # =========================================================================

    @property
    def __tattva__(self) -> TattvaDict:
        """The 5-fold truth of MahaKernel."""
        return {
            "chaitanya": "MahaKernel - Military Grade Deterministic Core",
            "nityananda": "LotusArrayInt (65,536 Slots)",
            "advaita": "Prime Field (65521) ^ Jiva Identity",
            "gadadhara": "Input -> Seed -> Mantra -> Address",
            "srivasa": "PanchaTattvaProtocol Governance",
        }

    # =========================================================================
    # THE CORE: 16-STEP SEQUENCE (__call__)
    # =========================================================================

    def __call__(self, input_data: Union[str, "MahaCell"]) -> int:
        """
        EXECUTE THE 16-STEP SEQUENCE (Military Grade).
        
        Algorithm:
        1. Extract 32-bit Seed (Intent).
        2. Execute Mantra Logic in Prime Field (65521) to prevent bit-collapse.
        3. XOR Result with Jiva Identity (Lower 16 bits of Seed).
        
        Args:
            input_data: Text or MahaCell
            
        Returns:
            The calculated Address (0-65535) in Lotus Memory.
        """
        # 1. SRAVANAM (Input & Seed Extraction)
        seed: int
        if isinstance(input_data, str):
            # Compress text to 32-bit seed (Intent extraction)
            result = self._compression.compress(input_data, extract_summary=False)
            seed = result.seed
        elif hasattr(input_data, 'header'):
            # Extract seed from MahaCell header
            seed = input_data.header.sravanam
        else:
            # Fallback for raw bytes or other types
            seed = hash(str(input_data)) & 0xFFFFFFFF

        # 2. THE PRIME FIELD (Kshetra)
        # We use the largest prime < 65536 to ensure bijective operations.
        FIELD_PRIME = 65521
        
        current_value = seed % FIELD_PRIME
        mantra_mask = 0
        
        # 3. THE 16-STEP SEQUENCE (Chatuh-Sloki Logic)
        for pos in range(WORDS): # 0 to 15
            name = MAHAMANTRA_WORD_PATTERN[pos]
            
            # THE LAW: H=×7, K=+10, R=² (in Prime Field)
            if name == MAHAMANTRA_NAME_HARE:
                current_value = (current_value * SEVEN) % FIELD_PRIME
            elif name == MAHAMANTRA_NAME_KRISHNA:
                current_value = (current_value + TEN) % FIELD_PRIME
            elif name == MAHAMANTRA_NAME_RAMA:
                current_value = (current_value * current_value) % FIELD_PRIME
            
            # HARVEST NIBBLE (At end of each Quarter: 3, 7, 11, 15)
            # This builds the "Mantra Structure" of the address
            if (pos + 1) % 4 == 0:
                nibble = current_value & 0xF
                mantra_mask = (mantra_mask << 4) | nibble

        # 4. UNIFICATION (Yoga)
        # Mantra Structure (Divine Path) ^ Jiva Identity (Individual Will)
        # This ensures high distribution (low collision) while respecting the Mantra.
        final_address = mantra_mask ^ (seed & 0xFFFF)
        
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
    
    # Proxy remaining calls to Singularity for backward compatibility
    # (But strict logic happens in __call__)
    def __getattr__(self, name: str) -> Any:
        return getattr(self._singularity, name)

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

