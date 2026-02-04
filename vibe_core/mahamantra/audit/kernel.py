"""
UNIFIED AUDIT KERNEL - Orchestrates ALL Audit Components
=========================================================

"sarvasya cāhaṁ hṛdi sanniviṣṭo" (BG 15.15)
"I am seated in everyone's heart"

This kernel ORCHESTRATES existing tools - it does NOT reinvent them.

COMPONENTS ORCHESTRATED:
    1. DriftAuditor      - lineage, ssot, protocols
    2. project_introspection - scan_codebase, find_gaps, measure_scale
    3. CodeScanner       - graph-based analysis
    4. narada_vina       - physics constants validation
    5. SystemAudit       - databases, imports, ledger

Usage:
    from vibe_core.mahamantra.audit.kernel import AuditKernel
    
    kernel = AuditKernel()
    report = kernel.full_audit()  # UnifiedAuditReport
"""

__mahajana__ = "yamaraja"
__position__ = 15
__genesis__ = "0x8000000f"

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Tuple

from vibe_core.mahamantra.protocols._seed import PARAMPARA

assert int(__genesis__, 16) % PARAMPARA == 0, "BROKEN LINEAGE"


@dataclass(frozen=True)
class UnifiedAuditReport:
    """Complete audit report from all components."""
    # DriftAuditor
    lineage_valid: int
    lineage_broken: int
    protocols_alive: int
    protocols_dead: int
    ssot_violations: int
    
    # project_introspection
    total_files: int
    total_lines: int
    coverage_percent: int
    gaps_count: int
    gaps_critical: int
    
    # narada_vina
    physics_constants: int
    physics_derived: int
    physics_coverage: int
    
    # SystemAudit
    databases: int
    
    @property
    def is_pristine(self) -> bool:
        return (self.lineage_broken == 0 and 
                self.protocols_dead == 0 and 
                self.ssot_violations == 0 and
                self.gaps_critical == 0)


class AuditKernel:
    """
    Unified Audit Kernel - Orchestrates all audit components.
    
    Does NOT reinvent - only ORCHESTRATES.
    """
    
    def __init__(self, root: Path | None = None) -> None:
        self._root = Path(root or ".")
    
    def quick_audit(self) -> UnifiedAuditReport:
        """Quick audit - drift + physics only (fast)."""
        drift = self._audit_drift()
        physics = self._audit_physics()

        return UnifiedAuditReport(
            lineage_valid=drift["lineage_valid"],
            lineage_broken=drift["lineage_broken"],
            protocols_alive=drift["protocols_alive"],
            protocols_dead=drift["protocols_dead"],
            ssot_violations=drift["ssot_violations"],
            total_files=0, total_lines=0, coverage_percent=0,
            gaps_count=0, gaps_critical=0,
            physics_constants=physics["total"],
            physics_derived=physics["derived"],
            physics_coverage=physics["coverage"],
            databases=0,
        )

    def full_audit(self) -> UnifiedAuditReport:
        """Full audit - ALL components (slow, scans entire codebase)."""
        drift = self._audit_drift()
        introspection = self._audit_introspection()
        physics = self._audit_physics()
        system = self._audit_system()

        return UnifiedAuditReport(
            lineage_valid=drift["lineage_valid"],
            lineage_broken=drift["lineage_broken"],
            protocols_alive=drift["protocols_alive"],
            protocols_dead=drift["protocols_dead"],
            ssot_violations=drift["ssot_violations"],
            total_files=introspection["total_files"],
            total_lines=introspection["total_lines"],
            coverage_percent=introspection["coverage_percent"],
            gaps_count=introspection["gaps_count"],
            gaps_critical=introspection["gaps_critical"],
            physics_constants=physics["total"],
            physics_derived=physics["derived"],
            physics_coverage=physics["coverage"],
            databases=system["databases"],
        )
    
    def _audit_drift(self) -> Dict[str, int]:
        """Use DriftAuditor."""
        from vibe_core.mahamantra.audit.drift import DriftAuditor
        auditor = DriftAuditor(self._root / "vibe_core/mahamantra")
        report = auditor.audit()
        return {
            "lineage_valid": report.lineage_valid,
            "lineage_broken": report.lineage_broken,
            "protocols_alive": report.protocols_alive,
            "protocols_dead": report.protocols_dead,
            "ssot_violations": len(report.ssot_violations),
        }
    
    def _audit_introspection(self) -> Dict[str, int]:
        """Use project_introspection."""
        from vibe_core.mahamantra.research.project_introspection import (
            scan_codebase, find_gaps, measure_scale
        )
        scale = measure_scale(self._root)
        files, _ = scan_codebase(self._root)
        gaps = find_gaps(files)
        critical = [g for g in gaps if g.severity == "critical"]
        return {
            "total_files": scale["total_files"],
            "total_lines": scale["total_lines"],
            "coverage_percent": scale["coverage_percent"],
            "gaps_count": len(gaps),
            "gaps_critical": len(critical),
        }
    
    def _audit_physics(self) -> Dict[str, int]:
        """Use narada_vina."""
        from vibe_core.mahamantra.analysis.narada_vina import get_coverage
        cov = get_coverage()
        # get_coverage returns nested dict with 'coverage' key
        inner = cov.get("coverage", cov)
        return {
            "total": inner.get("total", 0),
            "derived": inner.get("derived", 0),
            "coverage": int(inner.get("coverage_percent", 0)),
        }
    
    def _audit_system(self) -> Dict[str, int]:
        """Use SystemAudit."""
        try:
            from vibe_core.tools.system_audit import SystemAudit
            audit = SystemAudit(self._root)
            dbs = audit.run_database_audit()
            return {"databases": len(dbs)}
        except Exception:
            return {"databases": 0}


__all__ = ["AuditKernel", "UnifiedAuditReport"]

