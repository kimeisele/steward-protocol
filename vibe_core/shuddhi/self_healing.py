"""
OPUS-212: Self-Healing Loop - The Software Immune System.

This module orchestrates the complete self-healing cycle:

    NARASIMHA (Detection) → MANAS (Decision) → SHUDDHI (Repair) → LEDGER (Audit)
           AST                 Score              CST              Log

The loop is triggered by Watchman patrols or on-demand scans.

Architecture:
- Narasimha provides AST-based security analysis (SEC codes)
- LCOM4 provides cohesion analysis (GOD_CLASS codes)
- The bridge maps AST locations to CST for surgery
- Shuddhi remedies apply CST transformations
- Results are logged for audit trail
"""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from vibe_core.protocols.shuddhi import ShuddhiResult, ShuddhiStatus
from vibe_core.shuddhi.analyzers.lcom4 import LCOM4Result, calculate_lcom4
from vibe_core.shuddhi.analyzers.narasimha import (
    SecurityViolation,
    Severity,
    analyze_source,
    get_fixable_violations,
)
from vibe_core.shuddhi.engine import ShuddhiEngine

logger = logging.getLogger("SELF_HEALING")


# Mapping from Narasimha SEC codes to Shuddhi remedy rule_ids
VIOLATION_TO_REMEDY: Dict[str, str] = {
    "SEC005": "subprocess_timeout",  # subprocess without timeout
    "SEC007": "unsafe_io_write",  # open() for writing
    "SEC008": "silent_except",  # except: pass
}


@dataclass
class DiagnosticResult:
    """Result of a diagnostic scan."""

    file_path: Path
    security_violations: List[SecurityViolation]
    cohesion_violations: List[LCOM4Result]
    fixable_count: int
    critical_count: int

    @property
    def needs_attention(self) -> bool:
        """True if there are any violations."""
        return bool(self.security_violations or self.cohesion_violations)

    @property
    def auto_fixable(self) -> bool:
        """True if any violations can be auto-fixed."""
        return self.fixable_count > 0


@dataclass
class HealingResult:
    """Result of a healing operation."""

    file_path: Path
    attempted: int
    succeeded: int
    failed: int
    results: List[ShuddhiResult]

    @property
    def success_rate(self) -> float:
        """Percentage of successful fixes."""
        if self.attempted == 0:
            return 100.0
        return (self.succeeded / self.attempted) * 100


class SelfHealingLoop:
    """
    The Software Immune System - Autonomous Code Health Management.

    Usage:
        loop = SelfHealingLoop()

        # Diagnose a file
        diagnosis = loop.diagnose(Path("suspicious.py"))

        # Heal fixable violations
        if diagnosis.auto_fixable:
            healing = loop.heal(Path("suspicious.py"))
    """

    def __init__(self, engine: Optional[ShuddhiEngine] = None):
        """Initialize with optional custom engine."""
        self.engine = engine or ShuddhiEngine()
        self._healing_log: List[HealingResult] = []

    def diagnose(self, file_path: Path) -> DiagnosticResult:
        """
        Run full diagnostic scan on a file.

        This is the DETECTION phase (Narasimha + LCOM4).

        Args:
            file_path: Path to Python file

        Returns:
            DiagnosticResult with all detected violations
        """
        if not file_path.exists():
            return DiagnosticResult(
                file_path=file_path,
                security_violations=[],
                cohesion_violations=[],
                fixable_count=0,
                critical_count=0,
            )

        source_code = file_path.read_text()

        # Phase 1: Security Analysis (Narasimha)
        security_violations = analyze_source(source_code)
        fixable = get_fixable_violations(security_violations)
        critical = [v for v in security_violations if v.severity == Severity.CRITICAL]

        # Phase 2: Cohesion Analysis (LCOM4)
        cohesion_results = calculate_lcom4(source_code)
        god_classes = [r for r in cohesion_results.values() if r.is_god_class]

        logger.info(
            f"[DIAGNOSIS] {file_path.name}: "
            f"{len(security_violations)} security, "
            f"{len(god_classes)} god classes, "
            f"{len(fixable)} fixable"
        )

        return DiagnosticResult(
            file_path=file_path,
            security_violations=security_violations,
            cohesion_violations=god_classes,
            fixable_count=len(fixable),
            critical_count=len(critical),
        )

    def heal(self, file_path: Path, dry_run: bool = False) -> HealingResult:
        """
        Heal all fixable violations in a file.

        This is the REPAIR phase (Shuddhi).

        Args:
            file_path: Path to Python file
            dry_run: If True, don't write changes (just generate diffs)

        Returns:
            HealingResult with outcomes for each fix attempt
        """
        # First diagnose
        diagnosis = self.diagnose(file_path)
        fixable = get_fixable_violations(diagnosis.security_violations)

        results: List[ShuddhiResult] = []
        succeeded = 0
        failed = 0

        # Track current source (updated after each successful fix)
        current_source = file_path.read_text() if file_path.exists() else ""

        for violation in fixable:
            rule_id = VIOLATION_TO_REMEDY.get(violation.code)
            if not rule_id:
                logger.warning(f"No remedy for violation code: {violation.code}")
                continue

            # Apply remedy
            result = self.engine.purify(file_path, rule_id)
            results.append(result)

            if result.status == ShuddhiStatus.PURIFIED:
                succeeded += 1
                if not dry_run and result.purified_code:
                    # Write healed code
                    file_path.write_text(result.purified_code)
                    current_source = result.purified_code
                    logger.info(f"[HEALED] {file_path.name}: {rule_id} (line {violation.line})")
            elif result.status == ShuddhiStatus.FAILED:
                failed += 1
                logger.warning(f"[FAILED] {file_path.name}: {rule_id} - {result.message}")

        healing_result = HealingResult(
            file_path=file_path,
            attempted=len(fixable),
            succeeded=succeeded,
            failed=failed,
            results=results,
        )

        self._healing_log.append(healing_result)
        return healing_result

    def scan_directory(self, directory: Path, pattern: str = "**/*.py") -> List[DiagnosticResult]:
        """
        Scan all Python files in a directory.

        Args:
            directory: Root directory to scan
            pattern: Glob pattern for files

        Returns:
            List of DiagnosticResult for each file
        """
        results = []

        for file_path in directory.glob(pattern):
            if file_path.is_file():
                result = self.diagnose(file_path)
                if result.needs_attention:
                    results.append(result)

        logger.info(f"[SCAN] {directory}: {len(results)} files need attention")
        return results

    def heal_directory(self, directory: Path, dry_run: bool = True) -> List[HealingResult]:
        """
        Heal all fixable violations in a directory.

        Args:
            directory: Root directory to heal
            dry_run: If True, don't write changes

        Returns:
            List of HealingResult for each file
        """
        results = []
        diagnostics = self.scan_directory(directory)

        for diag in diagnostics:
            if diag.auto_fixable:
                result = self.heal(diag.file_path, dry_run=dry_run)
                results.append(result)

        total_fixed = sum(r.succeeded for r in results)
        total_failed = sum(r.failed for r in results)

        logger.info(f"[HEAL_DIR] {directory}: {total_fixed} fixed, {total_failed} failed")

        return results

    @property
    def healing_history(self) -> List[HealingResult]:
        """Get log of all healing operations."""
        return self._healing_log.copy()


def create_healing_report(results: List[HealingResult]) -> str:
    """
    Generate a human-readable healing report.

    Args:
        results: List of HealingResult

    Returns:
        Markdown-formatted report
    """
    lines = ["# Self-Healing Report", ""]

    total_attempted = sum(r.attempted for r in results)
    total_succeeded = sum(r.succeeded for r in results)
    total_failed = sum(r.failed for r in results)

    lines.append(f"**Total Fixes:** {total_succeeded}/{total_attempted}")
    if total_failed > 0:
        lines.append(f"**Failed:** {total_failed}")
    lines.append("")

    for result in results:
        lines.append(f"## {result.file_path.name}")
        lines.append(f"- Attempted: {result.attempted}")
        lines.append(f"- Succeeded: {result.succeeded}")
        if result.failed > 0:
            lines.append(f"- Failed: {result.failed}")
        lines.append("")

        for shuddhi_result in result.results:
            status = "✅" if shuddhi_result.success else "❌"
            lines.append(f"  {status} {shuddhi_result.rule_id}: {shuddhi_result.message}")

        lines.append("")

    return "\n".join(lines)
