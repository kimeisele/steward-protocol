"""
Technical Debt Panel - LIVE Code Scanner.

Scans codebase for:
- TODO comments
- FIXME comments
- DEPRECATED markers
- HACK/WORKAROUND notes
- Stale imports (future)

DATA-DRIVEN: No hardcoding, pure grep + analysis.
"""

import logging
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from .base_panel import OpusPanel

logger = logging.getLogger("PANEL_DEBT")


@dataclass
class DebtItem:
    """A single technical debt item."""

    file: str
    line: int
    marker: str  # TODO, FIXME, DEPRECATED, HACK
    text: str
    priority: str = "medium"  # low, medium, high, critical


@dataclass
class DebtSummary:
    """Summary of technical debt in codebase."""

    total_items: int = 0
    by_marker: Dict[str, int] = field(default_factory=dict)
    by_directory: Dict[str, int] = field(default_factory=dict)
    critical_items: List[DebtItem] = field(default_factory=list)
    recent_items: List[DebtItem] = field(default_factory=list)


class TechnicalDebtPanel(OpusPanel):
    """
    LIVE Technical Debt Scanner.

    Scans vibe_core/ for debt markers and reports them.
    Updates on every render (cached for performance).
    """

    def __init__(self):
        self._cache: Optional[DebtSummary] = None
        self._cache_time: float = 0
        self._cache_ttl: float = 300  # 5 minutes cache

    @property
    def panel_id(self) -> str:
        return "technical_debt"

    @property
    def priority(self) -> int:
        return 50  # Medium priority

    def render(self, config: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Render the technical debt panel."""
        now = time.time()

        # Use cache if valid
        if self._cache and (now - self._cache_time) < self._cache_ttl:
            summary = self._cache
        else:
            summary = self._scan_codebase()
            self._cache = summary
            self._cache_time = now

        return self._format_panel(summary)

    def _scan_codebase(self) -> DebtSummary:
        """Scan codebase for technical debt markers."""
        summary = DebtSummary()
        markers = ["TODO", "FIXME", "DEPRECATED", "HACK", "WORKAROUND", "XXX"]

        root = Path.cwd()
        scan_dirs = ["vibe_core", "scripts", "tests"]

        all_items: List[DebtItem] = []

        for scan_dir in scan_dirs:
            dir_path = root / scan_dir
            if not dir_path.exists():
                continue

            for marker in markers:
                items = self._grep_marker(dir_path, marker)
                all_items.extend(items)

                # Count by marker
                if marker not in summary.by_marker:
                    summary.by_marker[marker] = 0
                summary.by_marker[marker] += len(items)

        # Count by directory
        for item in all_items:
            parts = item.file.split("/")
            if len(parts) > 1:
                top_dir = parts[0]
                if top_dir not in summary.by_directory:
                    summary.by_directory[top_dir] = 0
                summary.by_directory[top_dir] += 1

        # Identify critical items (FIXME, DEPRECATED in kernel)
        summary.critical_items = [
            item for item in all_items if item.marker in ("FIXME", "DEPRECATED") and "kernel" in item.file.lower()
        ][:10]

        # Recent items (first 15)
        summary.recent_items = all_items[:15]
        summary.total_items = len(all_items)

        return summary

    def _grep_marker(self, directory: Path, marker: str) -> List[DebtItem]:
        """Grep for a specific marker in directory."""
        items = []

        try:
            # Use grep with line numbers
            result = subprocess.run(
                [
                    "grep",
                    "-rn",
                    f"# {marker}",
                    str(directory),
                    "--include=*.py",
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )

            for line in result.stdout.splitlines():
                # Format: file:line:content
                parts = line.split(":", 2)
                if len(parts) >= 3:
                    file_path = parts[0]
                    try:
                        line_num = int(parts[1])
                    except ValueError:
                        line_num = 0
                    content = parts[2].strip()

                    # Make path relative
                    try:
                        rel_path = str(Path(file_path).relative_to(Path.cwd()))
                    except ValueError:
                        rel_path = file_path

                    # Determine priority
                    priority = "medium"
                    if marker in ("FIXME", "DEPRECATED"):
                        priority = "high"
                    if "kernel" in rel_path.lower():
                        priority = "critical" if marker == "FIXME" else "high"

                    items.append(
                        DebtItem(
                            file=rel_path,
                            line=line_num,
                            marker=marker,
                            text=content[:80],
                            priority=priority,
                        )
                    )

        except (subprocess.TimeoutExpired, subprocess.CalledProcessError) as e:
            logger.warning(f"Grep failed for {marker}: {e}")

        return items

    def _format_panel(self, summary: DebtSummary) -> str:
        """Format the debt summary as markdown."""
        lines = [
            "## Technical Debt Tracker",
            "",
            f"> **Total Items:** {summary.total_items} | **Critical:** {len(summary.critical_items)}",
            "",
        ]

        # By Marker
        if summary.by_marker:
            lines.append("### By Type")
            lines.append("")
            lines.append("| Marker | Count |")
            lines.append("|--------|-------|")
            for marker, count in sorted(summary.by_marker.items(), key=lambda x: -x[1]):
                emoji = {"FIXME": "", "TODO": "", "DEPRECATED": "", "HACK": ""}.get(marker, "")
                lines.append(f"| {emoji} `{marker}` | {count} |")
            lines.append("")

        # By Directory
        if summary.by_directory:
            lines.append("### By Location")
            lines.append("")
            lines.append("| Directory | Items |")
            lines.append("|-----------|-------|")
            for dir_name, count in sorted(summary.by_directory.items(), key=lambda x: -x[1])[:5]:
                lines.append(f"| `{dir_name}/` | {count} |")
            lines.append("")

        # Critical Items
        if summary.critical_items:
            lines.append("### Critical Items (Kernel)")
            lines.append("")
            lines.append("| File | Line | Issue |")
            lines.append("|------|------|-------|")
            for item in summary.critical_items[:5]:
                short_file = item.file.split("/")[-1]
                short_text = item.text[:40] + "..." if len(item.text) > 40 else item.text
                lines.append(f"| `{short_file}` | {item.line} | {short_text} |")
            lines.append("")

        # Recent Items Sample
        if summary.recent_items:
            lines.append("### Recent Debt (Sample)")
            lines.append("")
            for item in summary.recent_items[:5]:
                lines.append(f"- `{item.file}:{item.line}` - {item.marker}: {item.text[:50]}")
            lines.append("")

        lines.append("---")
        lines.append("*Live scan from codebase*")

        return "\n".join(lines)
