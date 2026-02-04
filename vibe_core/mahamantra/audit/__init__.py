"""
AUDIT - System Intelligence via Existing Components
====================================================

ROUTING ONLY. Logic lives in submodules.

Structure:
    audit/
    ├── __init__.py      # THIS FILE - routing only
    ├── kernel.py        # Orchestrator
    ├── gad/             # GAD-000 compliance
    └── ssot/            # SSOT violations

USES (NO REINVENTING):
    - ComplianceTool (auditor cartridge)
    - SystemAudit (tools/system_audit.py)
    - project_introspection (research/)
"""

# === MAHAJANA DECLARATION ===
__mahajana__ = "yamaraja"
__position__ = 15
__genesis__ = "0x8000000f"  # 2147483663 % 37 == 0

from vibe_core.mahamantra.protocols._seed import PARAMPARA

assert int(__genesis__, 16) % PARAMPARA == 0, "BROKEN LINEAGE"

__all__ = ["run_audit", "get_drift", "get_scale"]


def run_audit():
    """Run full audit using existing tools."""
    from .kernel import AuditKernel
    return AuditKernel().run()


def get_drift():
    """Get drift report."""
    from .kernel import AuditKernel
    return AuditKernel().detect_drift()


def get_scale():
    """Get scale metrics."""
    from vibe_core.mahamantra.research.project_introspection import measure_scale
    return measure_scale()

