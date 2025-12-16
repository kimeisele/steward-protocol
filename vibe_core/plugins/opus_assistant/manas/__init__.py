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

from .api import AnalysisResult, ManasOracle
from .cognitive_kernel import CognitiveKernel, ManasConfig
from .intent_generator import Intent, IntentPriority
from .memory_store import MemoryEntry, MemoryStore

__all__ = [
    "CognitiveKernel",
    "ManasConfig",
    "IntentGenerator",
    "Intent",
    "IntentPriority",
    "MemoryStore",
    "MemoryEntry",
    "ManasOracle",
    "AnalysisResult",
]
