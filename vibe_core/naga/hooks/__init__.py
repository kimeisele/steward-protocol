"""
NAGA CLI Hooks - Level -2 Observers

These hooks wrap CLI execution at Level -2, enabling:
- Security validation (Takshaka)
- Capability enforcement (CapabilityHook)
- Performance profiling (Chitragupta)
- Audit logging (Sesha)

SAMUDRA MANTHAN: Each NAGA pulls the rope (HookChain) in coordination,
churning the CLI ocean to transform Gift (toxic input) into Nektar (clean execution).
"""

from vibe_core.naga.hooks.capability_cli import CapabilityCLIHook
from vibe_core.naga.hooks.chitragupta_cli import ChitraguptaCLIHook
from vibe_core.naga.hooks.sesha_cli import SeshaCLIHook
from vibe_core.naga.hooks.takshaka_cli import TakshakaCLIHook

__all__ = [
    "TakshakaCLIHook",
    "CapabilityCLIHook",
    "ChitraguptaCLIHook",
    "SeshaCLIHook",
]
