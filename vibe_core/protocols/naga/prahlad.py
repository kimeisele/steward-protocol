"""
PRAHLAD PROTOCOL - The Indestructible Memory.
Refactored: Strict Generics (No Any).
"""

from typing import Dict, Optional, TypeVar, Generic
import time
from vibe_core.protocols.science.entropy import KaliYugaEngine, EntropyState
from vibe_core.protocols.substrate.byte import MantraByte
from vibe_core.protocols.types import PersonProtocol

# T_Sacred: The type of data we are protecting (e.g., str, bytes, Model)
T_Sacred = TypeVar("T_Sacred")

class PrahladMemory(Generic[T_Sacred]):
    """
    A Typed Memory Store that defies Entropy.
    """
    def __init__(self, entropy_intensity: float = 10.0):
        self._store: Dict[str, EntropyState] = {}
        self._data: Dict[str, T_Sacred] = {} # Strictly Typed
        self._engine = KaliYugaEngine(intensity=entropy_intensity) 

    def remember(self, devotee: PersonProtocol, key: str, value: T_Sacred, mantra: MantraByte) -> bool:
        """
        Active Remembrance.
        Requires a 'Devotee' (Person), not just a script.
        """
        # 1. Identity Check (Dwarapala Logic embedded)
        # Only a Person can perform 'Smaranam' (Remembrance).
        if not isinstance(devotee, PersonProtocol):
            raise TypeError("Only a Person can perform Remembrance.")

        # 2. Mantra Check
        if mantra.coherence < 0.8: 
            return False 
            
        # 3. Store
        self._data[key] = value
        self._store[key] = EntropyState(decay_rate=0.1, integrity=1.08, last_refresh=time.time())
        return True

    def recall(self, devotee: PersonProtocol, key: str, mantra: MantraByte) -> Optional[T_Sacred]:
        """
        Retrieval. Returns T_Sacred or None.
        """
        if key not in self._store:
            return None
            
        # 1. Mantra/Person Check
        if not isinstance(devotee, PersonProtocol):
            return None
        if mantra.coherence < 0.5:
            return None

        # 2. Entropy Check
        if self._check_survival(key):
            return self._data[key]
        else:
            return None

    def _check_survival(self, key: str) -> bool:
        state = self._store[key]
        # Apply Entropy based on time elapsed since last 'remember'
        new_integrity = self._engine.apply_state_decay(state)
        
        # Update state
        state.integrity = new_integrity
        
        if state.integrity > 0:
            return True 
        else:
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
