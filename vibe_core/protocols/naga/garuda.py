"""
GARUDA PROTOCOL - The Controller of Nagas.

"When Garuda flies, the Nagas hide."

Architectural Role: RECURSION GUARD & GOVERNANCE SUPPRESSION.

Problem:
    Ouroboros (Nagas biting themselves).
    Sesha records event -> Naga Governance -> Sesha records event -> ...

Solution:
    Garuda Context.
    When code runs "under the wings of Garuda", Naga governance is SUSPENDED.
    The Nagas do not bite when Garuda is flying.

This Protocol defines the CONTRACT for recursion guarding.
Implementation uses contextvars to track depth.
"""

from typing import ContextManager, Protocol, runtime_checkable


@runtime_checkable
class GarudaProtocol(Protocol):
    """
    Protocol for the Garuda Recursion Guard.

    The Eagle that controls the Nagas.
    """

    @property
    def is_flying(self) -> bool:
        """
        Check if Garuda is currently flying (recursion active).

        If True, Nagas should SUSPEND governance (hide).
        """
        ...

    def fly(self) -> ContextManager[None]:
        """
        Spread wings. Suppress Naga governance for the duration.

        Usage:
            with garuda.fly():
                # Nagas are suppressed here
                # Safe to call governed methods recursively
        """
        ...


class NullGaruda:
    """No-op Garuda for when recursion guarding is disabled (unsafe)."""

    @property
    def is_flying(self) -> bool:
        return False

    def fly(self) -> ContextManager[None]:
        from contextlib import nullcontext

        return nullcontext()
