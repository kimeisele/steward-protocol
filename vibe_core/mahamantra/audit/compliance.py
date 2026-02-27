"""
COMPLIANCE - Atomic GAD-000 Compliance (SRIVASA)
================================================

Returns compliance report on-demand. No side effects.

Usage:
    from vibe_core.mahamantra.audit import compliance
    report = compliance.check()  # Returns ComplianceReport
    passed = compliance.passed()  # Returns bool
"""

__mahajana__ = "yamaraja"
__position__ = 15
__genesis__ = "0x8000000f"

from pathlib import Path
from typing import Any, Dict

from vibe_core.mahamantra.protocols._seed import PARAMPARA

assert int(__genesis__, 16) % PARAMPARA == 0, "BROKEN LINEAGE"


def check(root: Path = None) -> Dict[str, Any]:
    """
    Run GAD-000 compliance check using ComplianceTool.

    Returns:
        ComplianceReport dict with passed, violations, warnings
    """
    from vibe_core.cartridges.system.auditor.tools.compliance_tool import ComplianceTool

    tool = ComplianceTool(root_path=root or Path.cwd())
    result = tool.execute({"action": "run_audit"})
    if result.success:
        return result.output
    return {"passed": False, "error": result.error}


def passed(root: Path = None) -> bool:
    """Quick check: is system compliant?"""
    return check(root).get("passed", False)


def violations(root: Path = None) -> list:
    """Get only violations."""
    return check(root).get("violations", [])


__all__ = ["check", "passed", "violations"]
