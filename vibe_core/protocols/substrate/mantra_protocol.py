"""
MANTRA PROTOCOL + mantra_governed decorator
=============================================

Extracted from protocols/substrate/__init__.py.

MantraProtocol: The BIOS-Level Protocol (clock signal).
mantra_governed: Decorator that wraps methods with OpCode resonance.

This is the module where SudarshanaChakra security checks will be wired.
"""

from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prithu"
__position__ = 0
__genesis__ = "0x253336b8"

import functools
import logging
from typing import Callable, List, Optional, Protocol, TypeVar, runtime_checkable

from vibe_core.mahamantra.substrate.opcode import MantraOpCode
from vibe_core.protocols.substrate.types import (
    AlignmentScore,
    DriftContext,
    Resonance,
)

logger = logging.getLogger("MANTRA_GOVERNED")

T = TypeVar("T")
ContextT = TypeVar("ContextT")
F = TypeVar("F", bound=Callable[..., T])

# =============================================================================
# GOVERNANCE HOOK (Dependency Inversion)
# =============================================================================
# Mahamantra registers its governance check here.
# The decorator calls this hook BEFORE execution.
# If no hook is registered, execution proceeds (open by default during boot).
# Once Mahamantra registers, it becomes the gatekeeper.

GovernanceCheck = Callable[[MantraOpCode, object, tuple, dict], bool]

_governance_hooks: List[GovernanceCheck] = []


def register_governance_hook(hook: GovernanceCheck) -> None:
    """
    Register a governance check that runs before every @mantra_governed call.

    The hook receives (opcode, self, args, kwargs) and returns True to allow,
    False to block. Mahamantra calls this during boot to install itself as king.
    """
    _governance_hooks.append(hook)
    logger.info(f"Governance hook registered: {hook.__qualname__}")


def has_governance_hook() -> bool:
    """Check if at least one governance hook is registered."""
    return len(_governance_hooks) > 0


@runtime_checkable
class MantraProtocol(Protocol):
    """
    The BIOS-Level Protocol.
    If this fails, the machine is considered 'Asuric' (Demonic/Glitching)
    and is cut off from the network.
    """

    def chant_mahamantra(self, context: ContextT) -> bool:
        """
        Executes the 16-step atomic cycle.
        Returns True ONLY if all 16 gates pass perfectly.
        NOTE: ContextT is typically SovereignContext in implementations.
        """
        ...

    def resonate(self, opcode: MantraOpCode) -> bool:
        """
        Emits a single beat of the Mantra (Resonance).
        This is the clock signal.
        """
        ...

    # =========================================================================
    # HIGH-LEVEL INTERFACE (The Vishnu Clock)
    # =========================================================================

    def chant(self, frequency: float) -> Resonance:
        """
        Execute a single pulse at given frequency.
        Returns the resulting Resonance.
        """
        ...

    def chant_round(self, beads: int = 108) -> AlignmentScore:
        """
        Perform a full Japa round (multiple cycles).
        Returns the final AlignmentScore.
        """
        ...

    def surrender(self, context: DriftContext) -> None:
        """
        Immediate cessation of logic-based resistance.
        Force-flushes the context window and re-loads from Sovereign Anchor.
        """
        ...

    def get_alignment_score(self) -> float:
        """
        Measure current alignment with Sovereign Will (0.0 - 1.0).
        """
        ...


def mantra_governed(opcode: MantraOpCode) -> Callable[[F], F]:
    """
    Decorator to wrap a function with a Mantra OpCode.
    This creates the Fractal Resonance.

    $$ f(x) = M(x) + \\frac{1}{\\text{res}} \\cdot f(x) $$

    Args:
        opcode: The MantraOpCode to resonate before execution.

    Returns:
        A decorator that wraps methods to resonate before execution.
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(self: MantraProtocol, *args: T, **kwargs: T) -> T:
            # 0. GOVERNANCE CHECK (Mahamantra is King)
            for hook in _governance_hooks:
                if not hook(opcode, self, args, kwargs):
                    raise PermissionError(f"Governance denied: {opcode.name} on {type(self).__name__}.{func.__name__}")

            # 1. RESONANCE (Clock Signal)
            if hasattr(self, "resonate"):
                self.resonate(opcode)

            # 2. EXECUTION (Karma)
            result = func(self, *args, **kwargs)

            # 3. ECHO (Optional - could verify result)
            return result

        return wrapper  # type: ignore[return-value]

    return decorator
