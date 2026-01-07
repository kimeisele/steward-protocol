from typing import List, Protocol, runtime_checkable

from .types import EnforceContext, Rule, Verdict


@runtime_checkable
class EnforceProtocol(Protocol):
    """
    Atomic protocol for policy enforcement.
    Used by Guardians, RateLimiters, and Stewards.
    """

    def enforce(self, action: str, context: EnforceContext) -> Verdict:
        """Enforce rules on an action."""
        ...

    def check(self, action: str) -> bool:
        """
        Quick check if action is allowed (boolean only).
        Useful for UI states or fast-fail paths.
        """
        ...

    def get_rules(self) -> List[Rule]:
        """Get active rules."""
        ...
