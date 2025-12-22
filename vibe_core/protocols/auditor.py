"""
Auditor Protocol - OPUS-209 Phase 2.4

Defines the interface for audit/verification implementations.
The kernel depends on this protocol, not the concrete InvariantEngine.

This separates the judiciary from the executive, enabling:
- Independent audit systems
- Pluggable compliance backends
- Optional verification (NullAuditor for dev mode)
"""

from typing import Any, Dict, List, Protocol, runtime_checkable


@runtime_checkable
class AuditorProtocol(Protocol):
    """
    Protocol for audit/verification implementations.

    The auditor provides semantic verification:
    - Verify event streams against invariant rules
    - Detect violations and policy breaches
    - Report on system integrity
    """

    def verify_ledger(self, events: List[Dict[str, Any]]) -> Any:
        """
        Verify a list of events against all registered invariants.

        Args:
            events: List of events from the ledger

        Returns:
            VerificationReport with all violations found
        """
        ...

    def register_rule(self, rule: Any) -> None:
        """
        Register a new invariant rule.

        Args:
            rule: InvariantRule to register
        """
        ...


class NullAuditor:
    """
    No-op auditor for development/testing.

    Used when no audit plugin is loaded.
    Always returns passed verification.
    """

    def verify_ledger(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        return {
            "passed": True,
            "violations": [],
            "checked_events": len(events),
            "timestamp": None,
        }

    def register_rule(self, rule: Any) -> None:
        pass
