"""
OPUS Assistant Events - Event-driven triggers.

Components:
- KernelTickHandler: Heartbeat via EventBus (keeps plugin ALIVE)
"""

from vibe_core.plugins.opus_assistant.events.kernel_tick import KernelTickHandler, SyncKernelTickHandler

__all__ = [
    "KernelTickHandler",
    "SyncKernelTickHandler",
]
