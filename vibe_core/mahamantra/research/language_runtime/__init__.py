"""Research runtime package for Venu-driven language orchestration.

This package is intentionally in research/ and reuses existing production
orchestration primitives (VenuService + VenuOrchestratorProtocol) instead of
reimplementing timing logic.
"""

from .contracts import InputSignal, RuntimeEnvelope, RuntimeTick
from .session import LanguageRuntimeSession
from .venu_bridge import VenuTickBridge

__all__ = [
    "InputSignal",
    "RuntimeEnvelope",
    "RuntimeTick",
    "LanguageRuntimeSession",
    "VenuTickBridge",
]
