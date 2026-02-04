"""
GADADHARA - Audit Reporter
===========================

"gadadhara pandita gosai pandita pradhana"
"Gadadhara Pandita is the chief among the learned scholars."
-- Chaitanya Charitamrita

Generates outputs:
- Token-efficient structured reports
- Graph visualizations (text-based)
- Summary dashboards
- JSON exports for further processing
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from . import AuditAgency

# === MAHAJANA DECLARATION ===
__mahajana__ = "gadadhara"
__position__ = 5
__genesis__ = "0x00000005"


@dataclass
class AuditReport:
    """Complete audit report."""
    timestamp: str
    scanner_summary: Dict[str, Any]
    graph_summary: Dict[str, Any]
    semantic_summary: Dict[str, Any]
    validation_summary: Dict[str, Any]


class AuditReporter:
    """
    Generates audit reports in various formats.
    
    Usage:
        reporter = AuditReporter(agency)
        report = reporter.full_report()
        text = reporter.text_report()
        json_str = reporter.json_report()
    """
    
    def __init__(self, agency: "AuditAgency"):
        self.agency = agency
    
    def full_report(self) -> AuditReport:
        """Generate a complete audit report."""
        return AuditReport(
            timestamp=datetime.now().isoformat(),
            scanner_summary=self.agency.scanner.summary(),
            graph_summary=self.agency.graph.summary(),
            semantic_summary=self.agency.semantic.summary(),
            validation_summary=self.agency.validator.summary(),
        )
    
    def text_report(self) -> str:
        """Generate a token-efficient text report."""
        report = self.full_report()
        
        lines = [
            "=" * 60,
            "MAHA AUDIT AGENCY - Full System Report",
            f"Generated: {report.timestamp}",
            "=" * 60,
            "",
            "--- SCANNER (File Discovery) ---",
            f"Total Files: {report.scanner_summary['total_files']}",
            f"Total LOC: {report.scanner_summary['total_loc']}",
            f"Parse Errors: {report.scanner_summary['parse_errors']}",
            "",
            "Mahajana Distribution:",
        ]
        
        for mahajana, count in sorted(
            report.scanner_summary.get('mahajana_distribution', {}).items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]:
            lines.append(f"  {mahajana}: {count} files")
        
        lines.extend([
            "",
            "--- GRAPH (Dependencies) ---",
            f"Total Nodes: {report.graph_summary['total_nodes']}",
            f"Total Edges: {report.graph_summary['total_edges']}",
            "",
            "Top Hubs (high connectivity):",
        ])
        
        for path, in_deg, out_deg in report.graph_summary.get('hubs', [])[:5]:
            lines.append(f"  {path}: in={in_deg}, out={out_deg}")
        
        lines.extend([
            "",
            "--- SEMANTIC (Meaning) ---",
        ])
        
        flow = report.semantic_summary.get('delegation_flow', {})
        for layer, count in flow.get('hierarchy', []):
            lines.append(f"  {layer}: {count} files")
        
        lines.append(f"  Gita Integration: {flow.get('gita_integration', 0)} files")
        
        br = report.semantic_summary.get('build_runtime', {})
        lines.extend([
            "",
            "BUILD vs RUNTIME:",
            f"  BUILD only: {len(br.get('build_only', []))}",
            f"  RUNTIME only: {len(br.get('runtime_only', []))}",
            f"  Both: {len(br.get('both', []))}",
        ])
        
        lines.extend([
            "",
            "--- VALIDATION (Compliance) ---",
            f"Passed: {report.validation_summary['passed']}",
            f"Failed: {report.validation_summary['failed']}",
            f"Total Issues: {report.validation_summary['total_issues']}",
            "",
            "Issues by Type:",
        ])
        
        for issue_type, count in report.validation_summary.get('by_type', {}).items():
            lines.append(f"  {issue_type}: {count}")
        
        lines.extend([
            "",
            "=" * 60,
            "END REPORT",
            "=" * 60,
        ])
        
        return "\n".join(lines)
    
    def json_report(self) -> str:
        """Generate JSON report for further processing."""
        report = self.full_report()
        return json.dumps(asdict(report), indent=2, default=str)
    
    def mahajana_map(self) -> str:
        """Generate a mahajana-level map of the system."""
        graph = self.agency.graph.mahajana_graph()
        
        lines = [
            "MAHAJANA DEPENDENCY MAP",
            "=" * 40,
            "",
        ]
        
        for mahajana, count in sorted(
            graph.get('mahajanas', {}).items(),
            key=lambda x: x[1],
            reverse=True
        ):
            deps = graph.get('edges', {}).get(mahajana, [])
            lines.append(f"{mahajana} ({count} files)")
            if deps:
                lines.append(f"  -> {', '.join(deps)}")
            lines.append("")
        
        return "\n".join(lines)
    
    def quick_summary(self) -> Dict[str, Any]:
        """Get the most essential metrics only."""
        return {
            "files": self.agency.scanner.summary()["total_files"],
            "loc": self.agency.scanner.summary()["total_loc"],
            "mahajanas": len(self.agency.scanner.summary()["mahajana_distribution"]),
            "issues": self.agency.validator.summary()["total_issues"],
        }

