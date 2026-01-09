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
from typing import Protocol, runtime_checkable

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
    def apply_decay(self, state: EntropyState) -> float:
        """
        Wendet Entropie auf ein Objekt an.
        Reduziert Integrität basierend auf Delta-Time.
        Returns: New integrity value
        """
        ...

class KaliYugaEngine(KalaProtocol):
    """
    Die Implementation des Zeitalters des Streits.
    Maximale Destruktion, minimale Gnade (außer durch Nama).
    """
    def __init__(self, intensity: float = 1.0):
        self.intensity = intensity # Kali Yuga Factor

    def apply_decay(self, state: EntropyState) -> float:
        # Berechnung der verstrichenen Zeit
        now = time.time()
        delta = now - state.last_refresh
        
        # Exponential Decay (Materieller Zerfall ist nicht linear!)
        # Integrity(t) = Integrity(0) * e^(-lambda * t)
        # Simplified simulation for discrete steps:
        decay = (delta * self.intensity) * 0.1 
        
        new_integrity = state.integrity - decay
        
        # Clamp to 0
        return max(0.0, new_integrity)
