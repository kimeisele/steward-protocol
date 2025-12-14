"""
OPUS Assistant Events - Event-driven triggers.

Components:
- KernelTickHandler: Heartbeat via EventBus (keeps plugin ALIVE)
- DiamondHandlers: TDD enforcement (OPUS-037)
- MutationHandlers: Legacy code testing (OPUS-038)
"""

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
