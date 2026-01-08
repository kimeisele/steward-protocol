from typing import List, Protocol, runtime_checkable

from .types import EnforceContext, Rule, Verdict


@runtime_checkable
class EnforceProtocol(Protocol):
    """
    Atomic protocol for policy enforcement (The Law/Dharma).

    GAD-000 COMPLIANCE:
    - Discoverability: 'get_rules' makes policy inspectable.
    - Observability: Decisions can be logged via returned Verdicts.
    - Parseability: 'Verdict' is an Enum, not a string.
    - Composability: Can chaining checks (check -> enforce).
    - Idempotency: Checks should be side-effect free.
    - Recoverability: Fallback to strict/safe defaults on error.
    """

    def enforce(self, action: str, context: EnforceContext) -> Verdict:
        """
        Enforce rules on an action.
        Args:
            action: The verb being attempted.
            context: The context (including Sovereign Identity).
        """
        ...

    def check(self, action: str) -> bool:
        """
        Quick check if action is allowed (boolean only).
        Useful for UI states or fast-fail paths.
        Does NOT replace 'enforce' for critical paths.
        """
        ...

    def get_rules(self) -> List[Rule]:
        """Get active rules (Transparency)."""
        ...
