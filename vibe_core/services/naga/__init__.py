"""
NAGA Services - The Invisible Guardians
========================================

PROMPT.md Level 2: Die NAGAs (Das Nervensystem)

Services:
- NagaStateProxy: Wraps StateService with Dharma validation

The NAGAs are MIDDLEWARE that integrate into existing infrastructure.
"Niemand darf es merken" - the others don't know we're here.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "janaka"
__position__ = 10
__genesis__ = "0xa4ec21b7"  # GenesisByte: parampara % 37 == 0

from vibe_core.services.naga.state_proxy import (
    DharmaVerdict,
    NagaStateProxy,
    StateCorruptionAttempt,
    get_naga_state_proxy,
)

__all__ = [
    "NagaStateProxy",
    "DharmaVerdict",
    "StateCorruptionAttempt",
    "get_naga_state_proxy",
]
