"""
MANAS - The Cognitive Kernel (OPUS-032)

Sanskrit: मनस् (manas) = mind, intellect, perception

The bridge between REACTION and PROACTION.
Without MANAS, the system is a sophisticated script.
With MANAS, the system awakens.

Philosophy:
    Prakriti observes → MANAS thinks → The Hand acts

The Mind generates its own input. It doesn't wait.
"""

from .cognitive_kernel import CognitiveKernel, ManasConfig
from .intent_generator import Intent, IntentGenerator, IntentPriority
from .memory_store import MemoryEntry, MemoryStore
from .shiva import ShivaLifecycleManager

__all__ = [
    "CognitiveKernel",
    "ManasConfig",
    "IntentGenerator",
    "Intent",
    "IntentPriority",
    "MemoryStore",
    "MemoryEntry",
    "ShivaLifecycleManager",
]
