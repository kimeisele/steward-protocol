"""
OPUS Assistant Events - Event-driven triggers.

Components:
- KernelTickHandler: Heartbeat via EventBus (keeps plugin ALIVE)
- DiamondHandlers: TDD enforcement (OPUS-037)
"""

from vibe_core.plugins.opus_assistant.events.diamond_handlers import DiamondHandlers, get_diamond_handlers
from vibe_core.plugins.opus_assistant.events.kernel_tick import KernelTickHandler, SyncKernelTickHandler

__all__ = [
    "KernelTickHandler",
    "SyncKernelTickHandler",
    "DiamondHandlers",
    "get_diamond_handlers",
]
