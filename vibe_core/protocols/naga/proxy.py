"""
NAGA PROXY - The Shape Shifter
==============================

Interceptors the execution flow.
Applies the 'iGene' logic to mutate the outcome.
"""

import functools
from typing import Any, Callable
from vibe_core.protocols.substrate.gene import iGene
from vibe_core.protocols.universal.ramanujan import RamanujanProtocol

class NagaProxy:
    """
    A Runtime Proxy that makes the object 'Alive'.
    It applies the iGene parameters to every method call.
    """
    def __init__(self, target: Any, gene: iGene):
        self._target = target
        self._gene = gene

    def __getattr__(self, name: str) -> Any:
        attr = getattr(self._target, name)
        
        # We only infect methods, not properties (usually)
        if not callable(attr):
            return attr
            
        # THE INJECTION
        # We wrap the method to apply Ramanujan Logic before/after
        @functools.wraps(attr)
        def wrapper(*args, **kwargs):
            # 1. PRE-EXECUTION: Check Vitality
            if self._gene.is_fatal:
                # The object is dead before it starts.
                # In a Living System, dead objects don't run methods.
                raise SystemError(f"💀 FATAL ENTROPY: Gene Load {self._gene.entropy_load:.2f} > Shield {self._gene.mantra_shield.coherence:.2f}")

            # 2. EXECUTION: Run the logic
            try:
                result = attr(*args, **kwargs)
            except Exception as e:
                # 3. POST-EXECUTION: Grace Handling?
                # If exception, maybe Mantra saves it?
                raise e

            # 4. MUTATION (Optional)
            # We could mutate the result based on mutation_vector
            # For now, we just return the result (Survival)
            return result
            
        return wrapper

    def __repr__(self):
        return f"NagaProxy({self._target!r}, gene={self._gene})"
