"""
OPUS Assistant Events - Event-driven triggers.

Components:
- KernelTickHandler: Heartbeat via EventBus (keeps plugin ALIVE)
- DiamondHandlers: TDD enforcement (OPUS-037)
- MutationHandlers: Legacy code testing (OPUS-038)
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prahlada"
__position__ = 9
__genesis__ = "0x2fa46c06"  # GenesisByte: parampara % 37 == 0

from vibe_core.plugins.opus_assistant.events.diamond_handlers import DiamondHandlers, get_diamond_handlers
from vibe_core.plugins.opus_assistant.events.kernel_tick import KernelTickHandler, SyncKernelTickHandler
from vibe_core.plugins.opus_assistant.events.mutation_handlers import MutationHandlers, get_mutation_handlers

__all__ = [
    "KernelTickHandler",
    "SyncKernelTickHandler",
    "DiamondHandlers",
    "get_diamond_handlers",
    "MutationHandlers",
    "get_mutation_handlers",
]
