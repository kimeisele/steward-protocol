"""
RAMA ROUTER ADAPTER - The True Algorithm Service
================================================

Exposes the RAMA Grid logic via the standard PhoneticRoutingProtocol.
This is the bridge between the Core (Protocol) and the Substrate (Rama Grid).
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prahlada" # Memory/Router
__position__ = 9
__genesis__ = "0xc4ae098d"

from typing import Optional

from vibe_core.protocols.substrate.resonance import PhoneticClass, PHONETIC_MAP
from vibe_core.mahamantra.protocols.routing import PhoneticRoutingProtocol
from vibe_core.mahamantra.substrate.rama_grid import (
    krishna_route,
    rama_to_phoneme,
    POSITION_SUM_RAMA,
    POSITION_SUM_KRISHNA
)

class RamaPhoneticRouter:
    """
    Adapter for the Rama Grid Substrate.
    Implements PhoneticRoutingProtocol.
    """
    
    def route_to_rama(self, position: int) -> int:
        """
        Route a Mahamantra position (1-16) to a RAMA Grid coordinate (0-48).
        Uses the Krishna Router (Prime 17).
        """
        # Rama Grid uses 0-indexed positions for calculation
        # But accepts 1-indexed as input for API clarity
        return krishna_route(position - 1)
        
    def get_phoneme(self, rama_coord: int) -> str:
        """
        Get the string phoneme for a RAMA coordinate.
        """
        return rama_to_phoneme(rama_coord)
        
    def get_phonetic_class(self, rama_coord: int) -> PhoneticClass:
        """
        Get the PhoneticClass (Verification Type) for a RAMA coordinate.
        """
        phoneme = self.get_phoneme(rama_coord)
        
        # Direct hit (e.g. vowels "a", "i", or simple consonants if mapped)
        if phoneme in PHONETIC_MAP:
            return PHONETIC_MAP[phoneme]
            
        # Handle Sanskrit inherent 'a' (e.g. "kha" -> "kh")
        if phoneme.endswith("a") and len(phoneme) > 1:
            nucleus = phoneme[:-1]
            if nucleus in PHONETIC_MAP:
                return PHONETIC_MAP[nucleus]
            
        # Fallback logic if direct map misses
        # Verify resonance.py map covers all Rama Grid outputs
        return PhoneticClass.NULL

# Singleton instance
_router_instance: Optional[RamaPhoneticRouter] = None

def get_phonetic_router() -> PhoneticRoutingProtocol:
    """Get the singleton Phonetic Routiner service."""
    global _router_instance
    if _router_instance is None:
        _router_instance = RamaPhoneticRouter()
    return _router_instance
