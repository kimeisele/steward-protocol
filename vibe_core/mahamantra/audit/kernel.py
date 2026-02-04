"""
AUDIT KERNEL - Orchestrates Existing Tools
==========================================

NO NEW LOGIC. Just wires existing production tools together.

Uses:
    - SystemAudit.run_full_audit()
    - ComplianceTool.run_compliance_audit()
    - project_introspection.scan_codebase()
    - project_introspection.find_gaps()
"""

__mahajana__ = "yamaraja"
__position__ = 15
__genesis__ = "0x8000000f"

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List

from vibe_core.mahamantra.protocols._seed import PARAMPARA

assert int(__genesis__, 16) % PARAMPARA == 0, "BROKEN LINEAGE"


@dataclass
class AuditKernel:
    """
    Orchestrates existing audit tools.
    
    Returns structured data. No print().
    """
    
    root: Path = field(default_factory=Path.cwd)
    
    def run(self) -> Dict[str, Any]:
        """Run full audit using existing tools."""
        return {
            "scale": self._get_scale(),
            "gaps": self._get_gaps(),
            "system": self._get_system_audit(),
            "drift": self.detect_drift(),
        }
    
    def detect_drift(self) -> List[str]:
        """Find deviations using existing tools."""
        drift = []
        
        # Use project_introspection for gaps
        gaps = self._get_gaps()
        for gap in gaps:
            if gap.get("severity") == "critical":
                drift.append(f"{gap['gap_type']}: {gap['description']}")
        
        return drift
    
    def _get_scale(self) -> Dict[str, int]:
        """Use project_introspection.measure_scale()."""
        from vibe_core.mahamantra.research.project_introspection import measure_scale
        return measure_scale(self.root)
    
    def _get_gaps(self) -> List[Dict[str, Any]]:
        """Use project_introspection.find_gaps()."""
        from vibe_core.mahamantra.research.project_introspection import (
            scan_codebase,
            find_gaps,
        )
        files, _ = scan_codebase(self.root)
        gaps = find_gaps(files)
        return [
            {
                "file_path": str(g.file_path),
                "gap_type": g.gap_type,
                "description": g.description,
                "severity": g.severity,
            }
            for g in gaps
        ]
    
    def _get_system_audit(self) -> Dict[str, Any]:
        """Use SystemAudit.run_full_audit()."""
        try:
            from vibe_core.tools.system_audit import SystemAudit
            audit = SystemAudit(self.root)
            report = audit.run_full_audit()
            return {
                "databases": len(report.databases),
                "orphans": len(report.import_orphans),
                "recommendations": len(report.recommendations),
            }
        except Exception as e:
            return {"error": str(e)}


__all__ = ["AuditKernel"]

