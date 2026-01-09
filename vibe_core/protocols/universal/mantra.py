"""
MANTRA PROTOCOL - The Meta-Protocol
===================================
Connects the Atomic Verbs (Read/Write/Sync) to the Cosmic Clock.
Layer: Universal (Meta-Protocol)
"""

from enum import Enum, auto
from typing import Protocol, runtime_checkable, List, Optional, TypeVar
from vibe_core.protocols.substrate.byte import MantraByte

ContextT = TypeVar("ContextT")

class MantraOpCode(Enum):
    """
    The 16 Atomic Kernel Instructions.
    Aligned with the 16 Words of the Mahamantra.
    """
    # --- QUARTER 1: INVOCATION (H K H K) ---
    SYS_WAKE = auto()        # HARE
    LOAD_ROOT = auto()       # KRISHNA
    ALLOC_MEM = auto()       # HARE
    BIND_CTX = auto()        # KRISHNA
    
    # --- QUARTER 2: VERIFICATION (K K H H) ---
    ASSERT_TRUTH = auto()    # KRISHNA
    RESOLVE_REQ = auto()     # KRISHNA
    GARBAGE_COLLECT = auto() # HARE
    PULSE_SYNC = auto()      # HARE
    
    # --- QUARTER 3: EXECUTION (H R H R) ---
    FETCH_RES = auto()       # HARE
    EXEC_SERVICE = auto()    # RAMA
    CHECK_DHARMA = auto()    # HARE
    COMMIT_LOG = auto()      # RAMA
    
    # --- QUARTER 4: CONCLUSION (R R H H) ---
    CACHE_STATE = auto()     # RAMA
    OPTIMIZE = auto()        # RAMA
    YIELD_CPU = auto()       # HARE
    RESET_IP = auto()        # HARE

@runtime_checkable
class MantraProtocol(Protocol):
    """
    The BIOS-Level Protocol.
    Must be implemented by the Kernel or any 'Mantra-Governed' entity.
    """
    
    def chant(self, frequency_hz: float = 432.0) -> float:
        """
        Emits the Sovereign Signal.
        Returns the current Resonance Score (0.0 - 1.0).
        """
        ...

    def surrender(self, context: ContextT) -> None:
        """
        Immediate cessation of logic (Neti Neti).
        Forces a reload from the Sovereign Anchor.
        """
        ...

    def get_alignment_score(self) -> float:
        """
        Measures deviation from the Sovereign Will.
        """
        ...
    
    def receive_mantra(self, mantra: MantraByte) -> None:
        """
        Receive a full sequence of Trits.
        """
        ...
