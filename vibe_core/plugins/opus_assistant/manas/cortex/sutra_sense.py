"""
OPUS-054: SUTRA SENSE - The Thread of Knowledge
=================================================

Sanskrit: Sutra = Thread, Aphorism, Rule

This cortex module gives MANAS the ability to PERCEIVE documentation
and COMPARE it with actual code - detecting GAPS in knowledge.

Following Bhagavad Gita 9.22:
"ananyāś cintayanto māṁ... yoga-kṣemaṁ vahāmy aham"
(I bring what is lacking [Yoga] and preserve what they have [Kshema])

MANAS' Documentation Duties:
1. YOGA (Gap Filling): See new code without docs -> generate doc intent
2. KSHEMA (Preservation): See docs without code -> flag for archival review

The Three Senses of MANAS:
- PrakritiSense: "What is the state of the world?" (Code/Git/State)
- DharmaSense: "Is this action righteous?" (Ethics/Permissions)
- SutraSense: "What knowledge is missing?" (Doc/Code alignment)

Together they form the complete cognitive perception of MANAS.

"Shiva's Dance on Documentation" - continuous transformation of knowledge.

<!-- @HARNESS
files:
  - path: vibe_core/plugins/opus_assistant/manas/cortex/sutra_sense.py
    required: true
    rationale: "The Thread Sense - doc/code gap detection for MANAS"
  - path: docs/architecture/OPUS/054-SUTRA.md
    required: true
    rationale: "The master harness for documentation curation rules"

wiring:
  - pattern: "class SutraSense"
    in: vibe_core/plugins/opus_assistant/manas/cortex/sutra_sense.py
  - pattern: "def perceive_gaps"
    in: vibe_core/plugins/opus_assistant/manas/cortex/sutra_sense.py
  - pattern: "def compare_doc_to_code"
    in: vibe_core/plugins/opus_assistant/manas/cortex/sutra_sense.py
-->
"""

from __future__ import annotations

import hashlib
import json
import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Set

if TYPE_CHECKING:
    from vibe_core.plugins.opus_assistant.manas.intent_generator import Intent

logger = logging.getLogger("MANAS.Cortex.SutraSense")


@dataclass
class DocCodeGap:
    """A gap between documentation and code."""

    gap_type: str  # "missing_doc", "stale_doc", "orphan_doc", "missing_harness"
    severity: str  # "critical", "high", "medium", "low"
    doc_path: Optional[Path]
    code_path: Optional[Path]
    description: str
    suggested_action: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "gap_type": self.gap_type,
            "severity": self.severity,
            "doc_path": str(self.doc_path) if self.doc_path else None,
            "code_path": str(self.code_path) if self.code_path else None,
            "description": self.description,
            "suggested_action": self.suggested_action,
        }


@dataclass
class SutraSummary:
    """Summary of documentation health."""

    total_docs: int
    docs_with_harness: int
    docs_without_harness: int
    gaps_found: int
    gaps_by_type: Dict[str, int]
    gaps_by_severity: Dict[str, int]
    health_ratio: float  # 0.0-1.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_docs": self.total_docs,
            "docs_with_harness": self.docs_with_harness,
            "docs_without_harness": self.docs_without_harness,
            "gaps_found": self.gaps_found,
            "gaps_by_type": self.gaps_by_type,
            "gaps_by_severity": self.gaps_by_severity,
            "health_ratio": self.health_ratio,
        }


@dataclass
class HarnessCheck:
    """Result of checking a @HARNESS block."""

    doc_path: Path
    has_harness: bool
    files_declared: List[str]
    files_existing: List[str]
    files_missing: List[str]
    wiring_patterns: List[str]
    wiring_found: List[str]
    wiring_missing: List[str]
    score: float  # 0.0-1.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "doc_path": str(self.doc_path),
            "has_harness": self.has_harness,
            "files_declared": self.files_declared,
            "files_existing": self.files_existing,
            "files_missing": self.files_missing,
            "wiring_found": self.wiring_found,
            "wiring_missing": self.wiring_missing,
            "score": self.score,
        }


# Known OPUS doc ranges that MANAS can curate
MANAS_DOC_TERRITORY = {
    "range": (50, 99),  # OPUS-050 to OPUS-099 are MANAS territory
    "path": "docs/architecture/OPUS",
    "pattern": r"(\d{3})-.*\.md",
}

# Code directories to scan for doc coverage
CODE_DIRECTORIES = [
    "vibe_core/plugins/opus_assistant/manas",
    "vibe_core/plugins/opus_assistant/manas/cortex",
    "vibe_core/state",
    "vibe_core/plugins/vedic_governance",
]


class SutraSense:
    """
    The Thread Sense - Doc/Code Gap Detection for MANAS.

    This cortex module compares documentation with actual code,
    detecting gaps in knowledge that need to be filled (Yoga)
    or preserved (Kshema).

    Following Bhagavad Gita 9.22:
    "I bring what is lacking and preserve what they have."

    Usage:
        sense = SutraSense(workspace=Path("."))
        summary = sense.perceive_gaps()
        if summary.gaps_found > 0:
            for gap in sense.get_gaps():
                print(f"GAP: {gap.gap_type} - {gap.description}")
    """

    def __init__(
        self,
        workspace: Optional[Path] = None,
    ):
        """
        Initialize SUTRA SENSE.

        Args:
            workspace: Workspace root (default: cwd)
        """
        self._workspace = workspace or Path.cwd()
        self._gaps: List[DocCodeGap] = []
        self._harness_checks: Dict[str, HarnessCheck] = {}

        logger.info("[SUTRA_SENSE] Initialized - The Thread of Knowledge")

    # =========================================================================
    # Core Perception Methods
    # =========================================================================

    def perceive_gaps(self, refresh: bool = True) -> SutraSummary:
        """
        Perceive all documentation gaps.

        This is the PRIMARY perception method - scans docs and code
        to find where knowledge is missing or stale.

        Args:
            refresh: Force re-scan

        Returns:
            SutraSummary with gap counts and health ratio
        """
        if refresh:
            self._gaps = []
            self._harness_checks = {}

            # 1. Scan OPUS docs for harness checks
            self._scan_opus_docs()

            # 2. Scan code for missing docs
            self._scan_code_for_missing_docs()

            # 3. Cross-reference harnesses with code
            self._verify_harness_wiring()

        # Build summary
        gaps_by_type: Dict[str, int] = {}
        gaps_by_severity: Dict[str, int] = {}

        for gap in self._gaps:
            gaps_by_type[gap.gap_type] = gaps_by_type.get(gap.gap_type, 0) + 1
            gaps_by_severity[gap.severity] = gaps_by_severity.get(gap.severity, 0) + 1

        total_docs = len(self._harness_checks)
        docs_with_harness = sum(1 for h in self._harness_checks.values() if h.has_harness)

        # Health ratio: (docs with harness - critical gaps) / total
        critical_gaps = gaps_by_severity.get("critical", 0)
        health = max(0.0, (docs_with_harness - critical_gaps) / max(1, total_docs))

        return SutraSummary(
            total_docs=total_docs,
            docs_with_harness=docs_with_harness,
            docs_without_harness=total_docs - docs_with_harness,
            gaps_found=len(self._gaps),
            gaps_by_type=gaps_by_type,
            gaps_by_severity=gaps_by_severity,
            health_ratio=health,
        )

    def get_gaps(self, severity: Optional[str] = None) -> List[DocCodeGap]:
        """Get all detected gaps, optionally filtered by severity."""
        if severity:
            return [g for g in self._gaps if g.severity == severity]
        return list(self._gaps)

    def get_harness_check(self, doc_name: str) -> Optional[HarnessCheck]:
        """Get harness check result for a specific doc."""
        return self._harness_checks.get(doc_name)

    # =========================================================================
    # Internal Scanning Methods
    # =========================================================================

    def _scan_opus_docs(self) -> None:
        """Scan OPUS docs for @HARNESS blocks."""
        doc_dir = self._workspace / MANAS_DOC_TERRITORY["path"]
        if not doc_dir.exists():
            return

        pattern = re.compile(MANAS_DOC_TERRITORY["pattern"])

        for doc_file in sorted(doc_dir.glob("*.md")):
            match = pattern.match(doc_file.name)
            if not match:
                continue

            doc_num = int(match.group(1))
            min_num, max_num = MANAS_DOC_TERRITORY["range"]

            # Only scan docs in MANAS territory
            if min_num <= doc_num <= max_num:
                self._check_doc_harness(doc_file)

    def _check_doc_harness(self, doc_path: Path) -> None:
        """Check a single doc for @HARNESS block and verify it."""
        try:
            content = doc_path.read_text()
        except Exception:
            return

        # Extract @HARNESS block
        harness_match = re.search(r"<!--\s*@HARNESS\s*(.*?)-->", content, re.DOTALL | re.IGNORECASE)

        if not harness_match:
            # Doc without harness - this is a gap
            self._harness_checks[doc_path.name] = HarnessCheck(
                doc_path=doc_path,
                has_harness=False,
                files_declared=[],
                files_existing=[],
                files_missing=[],
                wiring_patterns=[],
                wiring_found=[],
                wiring_missing=[],
                score=0.0,
            )
            self._gaps.append(
                DocCodeGap(
                    gap_type="missing_harness",
                    severity="medium",
                    doc_path=doc_path,
                    code_path=None,
                    description=f"Doc {doc_path.name} has no @HARNESS block",
                    suggested_action="Add @HARNESS block with file references and wiring patterns",
                )
            )
            return

        # Parse HARNESS YAML-like content
        harness_content = harness_match.group(1)
        files_declared = self._extract_harness_files(harness_content)
        wiring_patterns = self._extract_harness_wiring(harness_content)

        # Check which files exist
        files_existing = []
        files_missing = []
        for file_path in files_declared:
            full_path = self._workspace / file_path
            if full_path.exists():
                files_existing.append(file_path)
            else:
                files_missing.append(file_path)
                self._gaps.append(
                    DocCodeGap(
                        gap_type="missing_code",
                        severity="high",
                        doc_path=doc_path,
                        code_path=Path(file_path),
                        description=f"Doc {doc_path.name} references {file_path} but it doesn't exist",
                        suggested_action="Either create the file or update the harness",
                    )
                )

        # Calculate score
        total_checks = len(files_declared) + len(wiring_patterns)
        passed_checks = len(files_existing)  # Wiring checked separately
        score = passed_checks / max(1, total_checks)

        self._harness_checks[doc_path.name] = HarnessCheck(
            doc_path=doc_path,
            has_harness=True,
            files_declared=files_declared,
            files_existing=files_existing,
            files_missing=files_missing,
            wiring_patterns=wiring_patterns,
            wiring_found=[],  # Filled by _verify_harness_wiring
            wiring_missing=[],
            score=score,
        )

    def _extract_harness_files(self, harness_content: str) -> List[str]:
        """Extract file paths from harness content."""
        files = []
        # Match: - path: some/path/file.py
        pattern = re.compile(r"-\s*path:\s*([^\n]+)", re.MULTILINE)
        for match in pattern.finditer(harness_content):
            path = match.group(1).strip()
            if path:
                files.append(path)
        return files

    def _extract_harness_wiring(self, harness_content: str) -> List[str]:
        """Extract wiring patterns from harness content."""
        patterns = []
        # Match: - pattern: "something"
        pattern = re.compile(r'-\s*pattern:\s*["\']?([^"\'\n]+)["\']?', re.MULTILINE)
        for match in pattern.finditer(harness_content):
            p = match.group(1).strip()
            if p:
                patterns.append(p)
        return patterns

    def _scan_code_for_missing_docs(self) -> None:
        """Scan code directories for modules without documentation."""
        documented_modules: Set[str] = set()

        # Build set of documented modules from harness files
        for check in self._harness_checks.values():
            for file_path in check.files_declared:
                # Extract module name from path
                parts = Path(file_path).parts
                if len(parts) >= 2:
                    module = parts[-2]  # e.g., "cortex" from "manas/cortex/file.py"
                    documented_modules.add(module)

        # Scan code directories
        for code_dir in CODE_DIRECTORIES:
            code_path = self._workspace / code_dir
            if not code_path.exists():
                continue

            for py_file in code_path.glob("*.py"):
                if py_file.name.startswith("_"):
                    continue

                # Check if this file is documented
                file_documented = any(
                    str(py_file.relative_to(self._workspace)) in check.files_declared
                    for check in self._harness_checks.values()
                )

                if not file_documented:
                    # Check if it's a significant file (not just __init__)
                    try:
                        content = py_file.read_text()
                        if len(content) > 500 and "class " in content:
                            self._gaps.append(
                                DocCodeGap(
                                    gap_type="missing_doc",
                                    severity="low",
                                    doc_path=None,
                                    code_path=py_file,
                                    description=f"Code file {py_file.name} has no documentation reference",
                                    suggested_action="Add to relevant OPUS doc harness or create new doc",
                                )
                            )
                    except Exception:
                        pass

    def _verify_harness_wiring(self) -> None:
        """Verify that wiring patterns are actually present in code."""
        for doc_name, check in self._harness_checks.items():
            if not check.has_harness or not check.wiring_patterns:
                continue

            wiring_found = []
            wiring_missing = []

            for pattern in check.wiring_patterns:
                # Search in all declared files
                found = False
                for file_path in check.files_existing:
                    full_path = self._workspace / file_path
                    try:
                        content = full_path.read_text()
                        if re.search(pattern, content):
                            found = True
                            break
                    except Exception:
                        pass

                if found:
                    wiring_found.append(pattern)
                else:
                    wiring_missing.append(pattern)
                    self._gaps.append(
                        DocCodeGap(
                            gap_type="stale_doc",
                            severity="medium",
                            doc_path=check.doc_path,
                            code_path=None,
                            description=f"Wiring pattern '{pattern}' not found in code",
                            suggested_action="Update harness or implement the pattern",
                        )
                    )

            check.wiring_found = wiring_found
            check.wiring_missing = wiring_missing

    # =========================================================================
    # Intent Generation (YOGA - Filling Gaps)
    # =========================================================================

    def generate_gap_intents(self, limit: int = 3) -> List[Dict[str, Any]]:
        """
        Generate intents for the most critical gaps.

        YOGA: "I bring what is lacking"

        Args:
            limit: Maximum intents to generate

        Returns:
            List of intent dictionaries for MANAS
        """
        intents = []

        # Sort gaps by severity
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        sorted_gaps = sorted(self._gaps, key=lambda g: severity_order.get(g.severity, 99))

        for gap in sorted_gaps[:limit]:
            intent = {
                "intent_type": f"sutra_{gap.gap_type}",
                "title": f"Sutra Gap: {gap.description[:50]}...",
                "description": gap.description,
                "reasoning": f"SutraSense detected {gap.gap_type} gap with {gap.severity} severity",
                "priority": "high" if gap.severity in ("critical", "high") else "medium",
                "risk": "safe",  # Doc updates are safe
                "params": gap.to_dict(),
                "auto_executable": gap.gap_type == "missing_harness",  # Can auto-add harness
            }
            intents.append(intent)

        return intents

    # =========================================================================
    # Chat Integration
    # =========================================================================

    def get_status_for_chat(self) -> str:
        """Get human-readable status for chat interface."""
        summary = self.perceive_gaps()

        lines = [
            "SUTRA SENSE - Documentation Health",
            "=" * 40,
            "",
            f"Total Docs Scanned: {summary.total_docs}",
            f"Docs with @HARNESS: {summary.docs_with_harness}",
            f"Docs without @HARNESS: {summary.docs_without_harness}",
            "",
            f"Gaps Found: {summary.gaps_found}",
            f"Health Ratio: {summary.health_ratio:.1%}",
            "",
            "Gaps by Type:",
        ]

        for gap_type, count in summary.gaps_by_type.items():
            lines.append(f"  {gap_type}: {count}")

        if summary.gaps_found > 0:
            lines.extend(
                [
                    "",
                    "Top Gaps:",
                ]
            )
            for gap in self._gaps[:5]:
                lines.append(f"  [{gap.severity}] {gap.gap_type}: {gap.description[:40]}...")

        return "\n".join(lines)


# =============================================================================
# Singleton for Global Access
# =============================================================================

_sutra_sense: Optional[SutraSense] = None


def get_sutra_sense(workspace: Optional[Path] = None) -> SutraSense:
    """Get or create the global SutraSense instance."""
    global _sutra_sense
    if _sutra_sense is None:
        _sutra_sense = SutraSense(workspace=workspace)
    return _sutra_sense


# =============================================================================
# Availability Flag
# =============================================================================

SUTRA_SENSE_AVAILABLE = True


# =============================================================================
# Public API Exports
# =============================================================================

__all__ = [
    "SutraSense",
    "SutraSummary",
    "DocCodeGap",
    "HarnessCheck",
    "get_sutra_sense",
    "SUTRA_SENSE_AVAILABLE",
]
