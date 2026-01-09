"""
KALA PROTOCOL - The Law of Entropy (Thermodynamics/Time).
=========================================================

"Time I am, the great destroyer of the worlds." (BG 11.32)

Dieses Modul simuliert den Zerfall. Es beweist, dass "Material Objects"
ohne spirituelle Anbindung (Mantra) nicht überleben können.
"""

import time
import random
from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Protocol, runtime_checkable

from vibe_core.protocols.universal.guna import GunaProtocol, ZERO

@dataclass
class EntropyState:
    """
    Der Zustand eines Objekts in der materiellen Welt.
    """
    decay_rate: float       # Wie schnell verfällt das Objekt? (Kali Yuga Factor)
    integrity: float        # 1.0 = Neu, 0.0 = Tot (Pralaya)
    last_refresh: float     # Letzter Mantra-Kontakt

@runtime_checkable
class KalaProtocol(Protocol):
    """
    Das Interface der Zeit.
    """
    def apply_decay(self, target: Any) -> Decimal:
        """
        Wendet Entropie auf ein Objekt an.
        Returns: New integrity factor (or growth).
        """
        ...
        
    def apply_state_decay(self, state: EntropyState) -> float:
        """
        Legacy method for PrahladMemory state.
        """
        ...

class KaliYugaEngine(KalaProtocol):
    """
    Die Implementation des Zeitalters des Streits.
    Maximale Destruktion, minimale Gnade (außer durch Nama).
    """
    def __init__(self, intensity: float = 1.0):
        self.intensity = intensity # Kali Yuga Factor

    def apply_decay(self, target: Any) -> Decimal:
        
        if isinstance(target, GunaProtocol):
            profile = target.get_guna_profile()
            
            # 1. SPIRITUAL HEALING (Negentropy)
            # Das Mantra stoppt nicht nur den Zerfall, es kehrt ihn um.
            if profile.is_transcendental:
                # Spirituelle Energie wächst durch Verteilung (nicht wie Materie)
                return Decimal("1.08") # Growth!
            
            # 2. VOID COLLAPSE
            if profile.is_void:
                return ZERO # Instant Pralaya
            
            # 3. MATERIAL DECAY (Standard Physics)
            # Tamas rots (0.1), Rajas burns (0.5), Sattva sustains (0.9)
            base_decay = (
                (profile.tamas * Decimal("0.1")) + 
                (profile.rajas * Decimal("0.5")) + 
                (profile.sattva * Decimal("0.9"))
            )
            # Kali Yuga Factor accelerates decay if not pure
            return base_decay * Decimal("0.9") # Slow degradation
            
        return Decimal("0.5") # Default Decay for unprofiled objects

    def apply_state_decay(self, state: EntropyState) -> float:
        """
        Legacy calculation for Store/Recall Prahlad.
        """
        now = time.time()
        delta = now - state.last_refresh
        decay = (delta * self.intensity) * 0.1 
        new_integrity = state.integrity - decay
        return max(0.0, new_integrity)
