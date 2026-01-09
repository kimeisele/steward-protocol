"""
PRAHLAD PROTOCOL - The 7th Mahajana (Smaranam)
==============================================

"He who remembers Vishnu is never vanquished."

This module implements the Indestructible Memory.
Even inside the Holodeck of Hiranyakashipu (Kali Yuga),
Prahlad preserves the Seed.
"""

from typing import Any, Dict, Optional
import time
from vibe_core.protocols.science.entropy import KaliYugaEngine, EntropyState
from vibe_core.protocols.substrate.byte import MantraByte
from vibe_core.protocols.universal.store_recall import StoreRecallProtocol

class PrahladMemory(StoreRecallProtocol):
    """
    A Memory Store that defies Entropy.
    """
    def __init__(self):
        self._store: Dict[str, EntropyState] = {}
        self._data: Dict[str, Any] = {}
        # High Heat (Hiranyakashipu). 
        # Intensity 10.0 means data decays very fast without Smaranam.
        self._engine = KaliYugaEngine(intensity=10.0) 

    def remember(self, key: str, value: Any, mantra: MantraByte) -> bool:
        """
        Active Remembrance (Smaranam).
        Each call resets the entropy timer (Refresh).
        """
        # 1. Check Lineage (Is the Mantra valid?)
        # We assume standard_16 or better is required for protection.
        if mantra.coherence < 0.8: 
            # Mantra is weak. Memory will not hold.
            return False 
            
        # 2. Store/Refresh
        self._data[key] = value
        # Prahlad sets Integrity to 108% (Super-Resonance)
        # This buffer allows it to survive slightly longer than standard logic
        self._store[key] = EntropyState(decay_rate=0.1, integrity=1.08, last_refresh=time.time())
        return True

    def recall(self, key: str, mantra: MantraByte) -> Optional[Any]:
        """
        Retrieval requires passing the Fire Test.
        """
        if key not in self._store:
            return None
            
        # 1. Mantra Check implies access
        if mantra.coherence < 0.5:
            return None

        # 2. Check Survival
        if self._check_survival(key):
            return self._data[key]
        else:
            return None

    def _check_survival(self, key: str) -> bool:
        """
        The Shadow Punch.
        Applies massive Entropy. If logic held it, it dies.
        If Prahlad held it, it survives.
        """
        if key not in self._store:
            return False
            
        state = self._store[key]
        
        # Apply Entropy based on time elapsed since last 'remember'
        new_integrity = self._engine.apply_decay(state)
        
        # Update state
        state.integrity = new_integrity
        
        if state.integrity > 0:
            return True # SURVIVED
        else:
            # KILLED BY TIME
            if key in self._data:
                del self._data[key]
            del self._store[key] 
            return False
            
    def force_entropy_attack(self, key: str, simulated_seconds: float):
        """
        Debug method to simulate time jumps (Hiranyakashipu's Torture).
        """
        if key in self._store:
            # We shove the last_refresh into the past, so the NEXT check sees a large delta.
            self._store[key].last_refresh -= simulated_seconds
            # Do NOT call check_survival here. Let the next access (recall) trigger the judgment.

