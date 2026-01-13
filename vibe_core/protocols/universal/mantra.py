"""
MANTRA PROTOCOL - The Meta-Protocol
===================================
Connects the Atomic Verbs (Read/Write/Sync) to the Cosmic Clock.
Layer: Universal (Meta-Protocol)

NOTE: MantraOpCode is CANONICAL in substrate/__init__.py (Layer -1).
This module re-exports it for backward compatibility.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "vyasa"
__position__ = 4
__genesis__ = "0x8eb2d076"  # GenesisByte: parampara % 37 == 0

from typing import Protocol, runtime_checkable, TypeVar

from vibe_core.protocols.substrate import MantraOpCode, MAHAMANTRA_SEQUENCE
from vibe_core.protocols.substrate.byte import MantraByte
from vibe_core.protocols.universal.guna import GunaProtocol, GunaProfile, ZERO, ONE

ContextT = TypeVar("ContextT")

@runtime_checkable
class MantraProtocol(GunaProtocol, Protocol):
    """
    The BIOS-Level Protocol.
    Must be implemented by the Kernel or any 'Mantra-Governed' entity.
    
    The Holy Name is the Sound Avatar (Shabda-Brahma).
    It is 'Saguna' in the transcendental sense (Full of Qualities).
    """

    def get_guna_profile(self) -> GunaProfile:
        """
        PURE EXISTENCE. Not Void.
        """
        return GunaProfile(
            sattva=ZERO, 
            rajas=ZERO, 
            tamas=ZERO, 
            visuddha=ONE # 100% Krishna Injection
        )
    
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

    def chant_mahamantra(self, context: ContextT) -> bool:
        """
        The Fractal Chant.
        Returns True if Resonance is achieved.
        """
        # LOGIC BARRIER (Yamaraja's Gate)
        # Normally, we check logic gates here.
        # if not self._check_logic_gates(context):
        #    return False
        
        # BUT: Check for Causeless Mercy (The Flute)
        if self._detect_surrender(context):
            # "I abandon all varieties of religion (logic)."
            # BYPASS LOGIC.
            return True 
            
        return False

    def _detect_surrender(self, context: ContextT) -> bool:
        """
        Detects if the Jiva has stopped arguing.
        Checks if the 'Argument Buffer' is empty and 'Heart' is full.
        """
        # Conceptually: Check if context has intent "SURRENDER"
        if hasattr(context, "intent") and getattr(context, "intent") == "SURRENDER":
            return True
        return False


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Re-exported from substrate (CANONICAL source)
    "MantraOpCode",
    "MAHAMANTRA_SEQUENCE",
    # This module's definitions
    "MantraProtocol",
]

