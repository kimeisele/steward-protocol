"""
NAGA Services - The Invisible Guardians
========================================

PROMPT.md Level 2: Die NAGAs (Das Nervensystem)

Services:
- NagaStateProxy: Wraps StateService with Dharma validation

The NAGAs are MIDDLEWARE that integrate into existing infrastructure.
"Niemand darf es merken" - the others don't know we're here.
"""

from vibe_core.services.naga.state_proxy import (
    DharmaPrinciple,
    DharmaVerdict,
    NagaStateProxy,
    StateCorruptionAttempt,
    get_naga_state_proxy,
)

__all__ = [
    "NagaStateProxy",
    "DharmaVerdict",
    "DharmaPrinciple",
    "StateCorruptionAttempt",
    "get_naga_state_proxy",
]
