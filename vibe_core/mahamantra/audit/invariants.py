"""
INVARIANTS - Atomic Invariant Verification (THE JUDGE)
======================================================

Access to InvariantEngine on-demand. No side effects.

Usage:
    from vibe_core.mahamantra.audit import invariants
    judge = invariants.engine()  # Returns InvariantEngine
    rules = invariants.rules()   # Returns list of rule names
"""

__mahajana__ = "yamaraja"
__position__ = 15
__genesis__ = "0x8000000f"

from typing import Any, Dict, List

from vibe_core.mahamantra.protocols._seed import PARAMPARA

assert int(__genesis__, 16) % PARAMPARA == 0, "BROKEN LINEAGE"


def engine():
    """
    Get the InvariantEngine (THE JUDGE) singleton.

    Returns:
        InvariantEngine with all registered rules
    """
    from vibe_core.cartridges.system.auditor.tools.invariant_tool import get_judge

    return get_judge()


def rules() -> List[str]:
    """Get list of registered invariant rule names."""
    return list(engine().rules.keys())


def rule_info(name: str) -> Dict[str, Any]:
    """Get info about a specific rule."""
    rule = engine().rules.get(name)
    if not rule:
        return {"error": f"Rule {name} not found"}
    return {"name": rule.name, "description": rule.description, "severity": rule.severity.value}


def verify(events: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Verify events against all invariants.

    Args:
        events: List of event dicts from ledger

    Returns:
        VerificationReport as dict
    """
    report = engine().verify_ledger(events)
    return report.to_dict()


__all__ = ["engine", "rules", "rule_info", "verify"]
