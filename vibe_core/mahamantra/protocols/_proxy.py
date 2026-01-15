"""
MAHAMANTRA PROXY - The Balarama Mantel
======================================

"balarama hoite haya krsna-bhakti-dayaka"
"From Balarama one receives devotion to Krishna."

FUNCTION: 
    Wraps any legacy object/module and gives it a Mahamantra Identity.
    Implements PanchaTattvaProtocol automatically.

SCALABILITY:
    Instead of refactoring 1000 files, we wrap them at the Router level.
    The proxy 'sacrifices' the raw object into the Lotus.

LOCATION: vibe_core.mahamantra.protocols._proxy (THE LAW)
"""

from typing import Any, Dict, Optional, Union
from vibe_core.mahamantra.protocols._pancha import PanchaTattvaProtocol, TattvaDict
from vibe_core.mahamantra.protocols._seed import WORDS

class MahamantraProxy(PanchaTattvaProtocol):
    """
    The Balarama Proxy.
    Wraps a target and provides the 5 Tattva answers.
    """
    
    def __init__(self, target: Any, position: int, guardian: str):
        self._target = target
        self._position = position
        self._guardian = guardian

    @property
    def __tattva__(self) -> TattvaDict:
        """
        Derives the 5 Truths.
        If the target already has __tattva__, it wins (Sovereignty).
        Otherwise, Balarama provides the strength (Derived from position).
        """
        if hasattr(self._target, "__tattva__"):
            return self._target.__tattva__
            
        # Default Tattva derived from the Lotus Position
        return {
            "chaitanya": f"Proxied {type(self._target).__name__}",
            "nityananda": f"Lotus Position {self._position}",
            "advaita": "Automatic Integration",
            "gadadhara": "Balarama Proxy Flow",
            "srivasa": f"Guarded by {self._guardian}",
        }

    def __getattr__(self, name: str) -> Any:
        """Forward everything to the target."""
        return getattr(self._target, name)

    def __repr__(self) -> str:
        return f"MahamantraProxy({self._target!r}, pos={self._position})"

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """Forward calls if target is callable."""
        if callable(self._target):
            return self._target(*args, **kwargs)
        raise TypeError(f"Target {type(self._target)} is not callable")

    # =========================================================================
    # UNIVERSAL SANKIRTAN (CHAT BRIDGE)
    # =========================================================================

    def chat(self, message: str) -> str:
        """
        Speak to the Proxied Service.
        
        Args:
            message: Input string.
            
        Returns:
            Response string.
        """
        # 1. GATEWAY DELEGATION (The Iron Scepter)
        # We look for explicit execution interfaces on the target.
        # This is NOT a blind passthrough; we only honor governed verbs.
        handler = getattr(self._target, "execute", None)
        if not callable(handler):
            handler = getattr(self._target, "chat", None)
        if not callable(handler):
            handler = getattr(self._target, "on_chat", None)
            
        if callable(handler):
            try:
                # The target handles the message, but the Proxy 
                # still owns the context (Guardian/Position).
                response = handler(message)
                if isinstance(response, str):
                    return response
            except Exception as e:
                return f"⚠️ Proxy Execution Error (at {self._guardian}): {e}"

        # 2. Fallback: Identity Response (The Balarama Mantel)
        return (
            f"🕉️  [PROXY RESPONSE] I am {type(self._target).__name__}.\n"
            f"    Identity: {self._guardian.upper()} (Pos {self._position})\n"
            f"    Status:   Wrapped/Active\n"
            f"\n"
            f"    (I do not speak 'chat' natively yet, but I am listening via the Lotus.)"
        )

# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "MahamantraProxy",
]
