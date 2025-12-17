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
from datetime import datetime
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


# =============================================================================
# PHASE 2: PROACTIVE MODE - MANAS as Author
# =============================================================================


@dataclass
class HiddenCode:
    """Code element not referenced in any documentation."""

    element_type: str  # "class", "function", "module"
    name: str
    file_path: Path
    line_number: int
    docstring: Optional[str]
    complexity: str  # "simple", "moderate", "complex"
    importance: str  # "low", "medium", "high"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "element_type": self.element_type,
            "name": self.name,
            "file_path": str(self.file_path),
            "line_number": self.line_number,
            "docstring": self.docstring,
            "complexity": self.complexity,
            "importance": self.importance,
        }


@dataclass
class IntentCluster:
    """A cluster of similar intents pointing to a documentation need."""

    topic: str
    intent_count: int
    sample_intents: List[str]
    first_seen: str
    last_seen: str
    proposed_doc_title: Optional[str] = None
    proposed_doc_number: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "topic": self.topic,
            "intent_count": self.intent_count,
            "sample_intents": self.sample_intents,
            "first_seen": self.first_seen,
            "last_seen": self.last_seen,
            "proposed_doc_title": self.proposed_doc_title,
            "proposed_doc_number": self.proposed_doc_number,
        }


@dataclass
class DocEnhancement:
    """A proposed enhancement to an existing document."""

    doc_path: Path
    section: str
    current_content: str
    proposed_content: str
    reason: str
    alignment_verified: bool  # Has been checked against code

    def to_dict(self) -> Dict[str, Any]:
        return {
            "doc_path": str(self.doc_path),
            "section": self.section,
            "current_content_hash": hashlib.sha256(self.current_content.encode()).hexdigest()[:8],
            "proposed_content_preview": self.proposed_content[:200],
            "reason": self.reason,
            "alignment_verified": self.alignment_verified,
        }


@dataclass
class RoadmapItem:
    """An item in the documentation roadmap."""

    priority: int  # 1-10
    action: str  # "create_doc", "enhance_doc", "document_code", "add_harness"
    target: str  # Doc name or code path
    description: str
    estimated_effort: str  # "trivial", "small", "medium", "large"
    dependencies: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    stale_after_days: int = 7  # Item considered stale after this many days

    def to_dict(self) -> Dict[str, Any]:
        return {
            "priority": self.priority,
            "action": self.action,
            "target": self.target,
            "description": self.description,
            "estimated_effort": self.estimated_effort,
            "dependencies": self.dependencies,
            "created_at": self.created_at,
            "is_stale": self.is_stale(),
        }

    def is_stale(self) -> bool:
        """Check if this roadmap item is stale."""
        try:
            created = datetime.fromisoformat(self.created_at)
            age_days = (datetime.utcnow() - created).days
            return age_days >= self.stale_after_days
        except Exception:
            return False

    def age_days(self) -> int:
        """Get age of this item in days."""
        try:
            created = datetime.fromisoformat(self.created_at)
            return (datetime.utcnow() - created).days
        except Exception:
            return 0


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
        config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize SUTRA SENSE.

        Args:
            workspace: Workspace root (default: cwd)
            config: Optional config dict from config/manas.yaml (sutra_sense section)
        """
        self._workspace = workspace or Path.cwd()
        self._config = config or {}
        self._gaps: List[DocCodeGap] = []
        self._harness_checks: Dict[str, HarnessCheck] = {}

        # Phase 2: Proactive Mode State
        self._hidden_code: List[HiddenCode] = []
        self._intent_clusters: Dict[str, IntentCluster] = {}
        self._doc_enhancements: List[DocEnhancement] = []
        self._roadmap: List[RoadmapItem] = []
        self._intent_history_file = self._workspace / ".opus_state" / "sutra_intent_history.json"

        logger.info("[SUTRA_SENSE] Initialized - The Thread of Knowledge (Phase 2: Proactive Mode)")

        # 🧠 SEMANTIC ENGINE (Lazy Injection)
        self._semantic_engine: Any = None

    def inject_semantic_engine(self, engine: Any) -> None:
        """Inject the Semantic Engine for Level 2 intelligence."""
        self._semantic_engine = engine
        logger.info("📜 SUTRA SENSE: Semantic Engine injected")

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

    async def find_semantic_matches(self, query: str, context_type: str = "doc") -> List[str]:
        """
        Use semantic engine to find matches for a query.

        Args:
            query: Text to match (e.g. code file name)
            context_type: "doc" or "code"

        Returns:
            List of matching names (doc titles or code files)
        """
        if not self._semantic_engine:
            return []

        try:
            # Analyze query to get concepts
            concepts = await self._semantic_engine.analyze(query)
            # This is a simplification - real weaving would search a vector store of docs.
            # But we can at least return concepts found.
            return [c.name for c in concepts if c.confidence > 0.6]
        except Exception:
            return []

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
    # PHASE 2: HIDDEN CODE DISCOVERY
    # "See what is unseen, document what is undocumented"
    # =========================================================================

    def discover_hidden_code(self) -> List[HiddenCode]:
        """
        Discover code elements not referenced in any documentation.

        Scans all Python files in MANAS territory for classes and functions
        that are not mentioned in any OPUS doc. These are "hidden" from
        the knowledge base and may need documentation.

        Returns:
            List of HiddenCode elements
        """
        self._hidden_code = []

        # Build set of all documented patterns
        documented_patterns: Set[str] = set()
        for check in self._harness_checks.values():
            for pattern in check.wiring_patterns:
                documented_patterns.add(pattern.lower())
            for file_path in check.files_declared:
                # Add file name and common class names from path
                documented_patterns.add(Path(file_path).stem.lower())

        # Also scan doc content for class/function mentions
        doc_dir = self._workspace / MANAS_DOC_TERRITORY["path"]
        if doc_dir.exists():
            for doc_file in doc_dir.glob("*.md"):
                try:
                    content = doc_file.read_text().lower()
                    # Extract class and function names mentioned
                    for match in re.finditer(r"`(\w+)`|class\s+(\w+)|def\s+(\w+)", content):
                        for g in match.groups():
                            if g:
                                documented_patterns.add(g.lower())
                except Exception:
                    pass

        # Scan code directories for hidden elements
        for code_dir in CODE_DIRECTORIES:
            code_path = self._workspace / code_dir
            if not code_path.exists():
                continue

            for py_file in code_path.glob("**/*.py"):
                if "__pycache__" in str(py_file) or py_file.name.startswith("_"):
                    continue

                self._scan_file_for_hidden_elements(py_file, documented_patterns)

        logger.info(f"📜 SUTRA SENSE: Discovered {len(self._hidden_code)} hidden code elements")
        return self._hidden_code

    def _scan_file_for_hidden_elements(self, file_path: Path, documented: Set[str]) -> None:
        """Scan a Python file for undocumented elements."""
        try:
            content = file_path.read_text()
            lines = content.split("\n")
        except Exception:
            return

        # Find classes
        class_pattern = re.compile(r"^class\s+(\w+)")
        # Find functions (not methods - at module level)
        func_pattern = re.compile(r"^def\s+(\w+)")
        # Find docstrings
        docstring_pattern = re.compile(r'^\s*"""(.+?)"""', re.DOTALL)

        current_docstring = None

        for i, line in enumerate(lines):
            # Check for class
            class_match = class_pattern.match(line)
            if class_match:
                class_name = class_match.group(1)
                if class_name.lower() not in documented and not class_name.startswith("_"):
                    # Get docstring from next lines
                    docstring = self._extract_docstring(lines, i + 1)
                    complexity = self._estimate_complexity(lines, i, "class")
                    importance = self._estimate_importance(class_name, docstring, complexity)

                    self._hidden_code.append(
                        HiddenCode(
                            element_type="class",
                            name=class_name,
                            file_path=file_path,
                            line_number=i + 1,
                            docstring=docstring,
                            complexity=complexity,
                            importance=importance,
                        )
                    )

            # Check for module-level functions
            func_match = func_pattern.match(line)
            if func_match:
                func_name = func_match.group(1)
                if func_name.lower() not in documented and not func_name.startswith("_"):
                    docstring = self._extract_docstring(lines, i + 1)
                    complexity = self._estimate_complexity(lines, i, "function")
                    importance = self._estimate_importance(func_name, docstring, complexity)

                    self._hidden_code.append(
                        HiddenCode(
                            element_type="function",
                            name=func_name,
                            file_path=file_path,
                            line_number=i + 1,
                            docstring=docstring,
                            complexity=complexity,
                            importance=importance,
                        )
                    )

    def _extract_docstring(self, lines: List[str], start_line: int) -> Optional[str]:
        """Extract docstring starting from given line."""
        if start_line >= len(lines):
            return None

        # Look for triple-quoted string
        for i in range(start_line, min(start_line + 3, len(lines))):
            line = lines[i].strip()
            if line.startswith('"""') or line.startswith("'''"):
                # Find end of docstring
                quote = line[:3]
                if line.count(quote) >= 2:
                    # Single line docstring
                    return line.strip(quote).strip()
                else:
                    # Multi-line docstring
                    docstring_lines = [line[3:]]
                    for j in range(i + 1, min(i + 20, len(lines))):
                        if quote in lines[j]:
                            docstring_lines.append(lines[j].split(quote)[0])
                            return "\n".join(docstring_lines).strip()
                        docstring_lines.append(lines[j])
        return None

    def _estimate_complexity(self, lines: List[str], start_line: int, element_type: str) -> str:
        """Estimate complexity of a code element."""
        # Count lines until next class/def at same indentation
        line_count = 0
        indent = len(lines[start_line]) - len(lines[start_line].lstrip())

        for i in range(start_line + 1, min(start_line + 500, len(lines))):
            if i >= len(lines):
                break
            line = lines[i]
            if not line.strip():
                continue
            current_indent = len(line) - len(line.lstrip())
            if current_indent <= indent and (line.strip().startswith("class ") or line.strip().startswith("def ")):
                break
            line_count += 1

        if line_count < 20:
            return "simple"
        elif line_count < 100:
            return "moderate"
        else:
            return "complex"

    def _estimate_importance(self, name: str, docstring: Optional[str], complexity: str) -> str:
        """Estimate importance of documenting this element."""
        score = 0

        # Complex elements are more important to document
        if complexity == "complex":
            score += 2
        elif complexity == "moderate":
            score += 1

        # Elements with docstrings are already self-documenting (less urgent)
        if docstring and len(docstring) > 50:
            score -= 1

        # Certain naming patterns indicate importance
        important_patterns = ["kernel", "sense", "engine", "manager", "handler", "core"]
        if any(p in name.lower() for p in important_patterns):
            score += 2

        if score >= 3:
            return "high"
        elif score >= 1:
            return "medium"
        else:
            return "low"

    def get_hidden_code(self, importance: Optional[str] = None) -> List[HiddenCode]:
        """Get discovered hidden code, optionally filtered by importance."""
        if importance:
            return [h for h in self._hidden_code if h.importance == importance]
        return list(self._hidden_code)

    # =========================================================================
    # PHASE 2: INTENT CLUSTERING
    # "Patterns reveal needs"
    # =========================================================================

    def record_intent(self, intent_type: str, topic: str, title: str) -> None:
        """
        Record an intent for pattern detection.

        When MANAS generates intents repeatedly for similar topics,
        this indicates a need for structured documentation.

        Args:
            intent_type: Type of intent (e.g., "doc_modify", "sutra_gap")
            topic: Topic category (e.g., "state_management", "vedic_governance")
            title: Intent title
        """
        now = datetime.utcnow().isoformat()

        # Load existing history
        history = self._load_intent_history()

        # Add to history
        history.append(
            {
                "intent_type": intent_type,
                "topic": topic,
                "title": title,
                "timestamp": now,
            }
        )

        # Keep last 1000 intents
        history = history[-1000:]

        # Save
        self._save_intent_history(history)

        # Update clusters
        self._update_clusters(history)

    def _load_intent_history(self) -> List[Dict[str, Any]]:
        """Load intent history from disk."""
        if not self._intent_history_file.exists():
            return []
        try:
            return json.loads(self._intent_history_file.read_text())
        except Exception:
            return []

    def _save_intent_history(self, history: List[Dict[str, Any]]) -> None:
        """Save intent history to disk."""
        try:
            self._intent_history_file.parent.mkdir(parents=True, exist_ok=True)
            self._intent_history_file.write_text(json.dumps(history, indent=2))
        except Exception as e:
            logger.warning(f"📜 SUTRA SENSE: Could not save intent history: {e}")

    def _update_clusters(self, history: List[Dict[str, Any]]) -> None:
        """Update intent clusters from history."""
        # Group by topic
        topics: Dict[str, List[Dict[str, Any]]] = {}
        for entry in history:
            topic = entry.get("topic", "unknown")
            if topic not in topics:
                topics[topic] = []
            topics[topic].append(entry)

        # Build clusters
        self._intent_clusters = {}
        for topic, entries in topics.items():
            if len(entries) >= 3:  # Threshold for cluster
                self._intent_clusters[topic] = IntentCluster(
                    topic=topic,
                    intent_count=len(entries),
                    sample_intents=[e.get("title", "")[:50] for e in entries[-5:]],
                    first_seen=entries[0].get("timestamp", ""),
                    last_seen=entries[-1].get("timestamp", ""),
                    proposed_doc_title=self._suggest_doc_title(topic),
                    proposed_doc_number=self._suggest_doc_number(),
                )

    def _suggest_doc_title(self, topic: str) -> str:
        """Suggest a document title for a topic."""
        # Convert topic to title case
        title = topic.replace("_", " ").title()
        return f"OPUS-XXX: {title}"

    def _suggest_doc_number(self) -> int:
        """Suggest next available OPUS doc number in MANAS territory."""
        used_numbers: Set[int] = set()
        doc_dir = self._workspace / MANAS_DOC_TERRITORY["path"]

        if doc_dir.exists():
            pattern = re.compile(r"(\d{3})-.*\.md")
            for doc_file in doc_dir.glob("*.md"):
                match = pattern.match(doc_file.name)
                if match:
                    used_numbers.add(int(match.group(1)))

        # Find first available in MANAS range
        min_num, max_num = MANAS_DOC_TERRITORY["range"]
        for num in range(min_num, max_num + 1):
            if num not in used_numbers:
                return num

        return max_num + 1  # Overflow

    def get_clusters(self, min_intents: int = 3) -> List[IntentCluster]:
        """Get intent clusters that have reached threshold."""
        return [c for c in self._intent_clusters.values() if c.intent_count >= min_intents]

    def propose_new_doc(self, cluster: IntentCluster) -> Dict[str, Any]:
        """
        Propose a new OPUS document based on an intent cluster.

        Args:
            cluster: The intent cluster to base the doc on

        Returns:
            Dict with proposed doc content and metadata
        """
        doc_num = cluster.proposed_doc_number or self._suggest_doc_number()
        doc_title = cluster.proposed_doc_title or f"OPUS-{doc_num:03d}: {cluster.topic.title()}"

        return {
            "intent_type": "create_opus_doc",
            "title": f"Create new doc: {doc_title}",
            "description": f"Intent cluster '{cluster.topic}' has {cluster.intent_count} related intents. "
            f"This suggests a need for structured documentation.",
            "priority": "medium",
            "risk": "safe",
            "params": {
                "doc_number": doc_num,
                "doc_title": doc_title,
                "topic": cluster.topic,
                "intent_count": cluster.intent_count,
                "sample_intents": cluster.sample_intents,
            },
            "auto_executable": False,  # Needs human review
        }

    # =========================================================================
    # PHASE 2: DOC ENHANCEMENT AUTHORITY
    # "MANAS can improve documentation"
    # =========================================================================

    def propose_enhancement(
        self,
        doc_path: Path,
        section: str,
        proposed_content: str,
        reason: str,
    ) -> DocEnhancement:
        """
        Propose an enhancement to an existing document.

        MANAS can suggest content improvements if:
        1. The doc is in MANAS territory (050-099)
        2. The enhancement aligns with code reality
        3. Dharma gate approves (checked at execution)

        Args:
            doc_path: Path to the document
            section: Section to enhance
            proposed_content: New content
            reason: Why this enhancement is needed

        Returns:
            DocEnhancement proposal
        """
        # Read current content
        try:
            full_content = doc_path.read_text()
            # Extract section (simplified - find heading)
            # NOTE: Use {{1,3}} to escape curly braces in f-string for regex quantifier
            section_pattern = re.compile(
                rf"^#{{1,3}}\s*{re.escape(section)}.*?(?=^#{{1,3}}|\Z)", re.MULTILINE | re.DOTALL
            )
            match = section_pattern.search(full_content)
            current_content = match.group(0) if match else ""
        except Exception:
            current_content = ""

        # Verify alignment (basic check - ensure code patterns mentioned exist)
        alignment_verified = self._verify_content_alignment(proposed_content)

        enhancement = DocEnhancement(
            doc_path=doc_path,
            section=section,
            current_content=current_content,
            proposed_content=proposed_content,
            reason=reason,
            alignment_verified=alignment_verified,
        )

        self._doc_enhancements.append(enhancement)
        return enhancement

    def _verify_content_alignment(self, content: str) -> bool:
        """
        Verify that proposed content aligns with code reality.

        Checks that any code references (files, classes, functions)
        mentioned in the content actually exist.
        """
        # Extract file paths
        file_pattern = re.compile(r"`([a-z_/]+\.py)`")
        for match in file_pattern.finditer(content):
            file_path = self._workspace / match.group(1)
            if not file_path.exists():
                logger.warning(f"📜 SUTRA SENSE: Content references non-existent file: {match.group(1)}")
                return False

        # Extract class names (simple heuristic)
        class_pattern = re.compile(r"`([A-Z][a-zA-Z]+)`")
        for match in class_pattern.finditer(content):
            class_name = match.group(1)
            # Check if class exists in any tracked file
            found = False
            for check in self._harness_checks.values():
                for file_path in check.files_existing:
                    try:
                        full_path = self._workspace / file_path
                        file_content = full_path.read_text()
                        if f"class {class_name}" in file_content:
                            found = True
                            break
                    except Exception:
                        pass
                if found:
                    break
            if not found and class_name not in ("Path", "Dict", "List", "Any", "Optional"):
                logger.debug(f"📜 SUTRA SENSE: Could not verify class: {class_name}")
                # Don't fail - could be external

        return True

    def get_enhancements(self, verified_only: bool = False) -> List[DocEnhancement]:
        """Get proposed enhancements."""
        if verified_only:
            return [e for e in self._doc_enhancements if e.alignment_verified]
        return list(self._doc_enhancements)

    # =========================================================================
    # PHASE 2: ROADMAP GENERATION
    # "Plan the path to complete documentation"
    # =========================================================================

    def generate_roadmap(self) -> List[RoadmapItem]:
        """
        Generate a documentation roadmap from all detected needs.

        Combines:
        - Gap detection (missing harness, missing code)
        - Hidden code discovery
        - Intent clusters
        - Doc enhancements

        Into a prioritized roadmap.

        Returns:
            Sorted list of RoadmapItem
        """
        self._roadmap = []

        # 1. Critical gaps (missing code referenced in docs)
        for gap in self._gaps:
            if gap.severity == "critical" or gap.gap_type == "missing_code":
                self._roadmap.append(
                    RoadmapItem(
                        priority=1,
                        action="fix_code_reference",
                        target=str(gap.doc_path or gap.code_path),
                        description=gap.description,
                        estimated_effort="medium" if gap.severity == "critical" else "small",
                    )
                )

        # 2. Missing harnesses (high priority)
        for gap in self._gaps:
            if gap.gap_type == "missing_harness":
                self._roadmap.append(
                    RoadmapItem(
                        priority=2,
                        action="add_harness",
                        target=str(gap.doc_path),
                        description=f"Add @HARNESS to {gap.doc_path.name if gap.doc_path else 'unknown'}",
                        estimated_effort="trivial",
                    )
                )

        # 3. Intent clusters that warrant new docs
        for cluster in self.get_clusters(min_intents=5):
            self._roadmap.append(
                RoadmapItem(
                    priority=3,
                    action="create_doc",
                    target=f"OPUS-{cluster.proposed_doc_number or 'XXX'}",
                    description=f"Create doc for topic '{cluster.topic}' ({cluster.intent_count} related intents)",
                    estimated_effort="medium",
                )
            )

        # 4. High importance hidden code
        for hidden in self.get_hidden_code(importance="high"):
            self._roadmap.append(
                RoadmapItem(
                    priority=4,
                    action="document_code",
                    target=f"{hidden.file_path.name}:{hidden.name}",
                    description=f"Document {hidden.element_type} {hidden.name}",
                    estimated_effort="small" if hidden.complexity == "simple" else "medium",
                )
            )

        # 5. Doc enhancements
        for enhancement in self.get_enhancements(verified_only=True):
            self._roadmap.append(
                RoadmapItem(
                    priority=5,
                    action="enhance_doc",
                    target=str(enhancement.doc_path.name),
                    description=f"Enhance section '{enhancement.section}': {enhancement.reason}",
                    estimated_effort="small",
                )
            )

        # 6. Stale docs
        for gap in self._gaps:
            if gap.gap_type == "stale_doc":
                self._roadmap.append(
                    RoadmapItem(
                        priority=6,
                        action="update_doc",
                        target=str(gap.doc_path),
                        description=gap.description,
                        estimated_effort="small",
                    )
                )

        # Sort by priority
        self._roadmap.sort(key=lambda r: r.priority)

        logger.info(f"📜 SUTRA SENSE: Generated roadmap with {len(self._roadmap)} items")
        return self._roadmap

    def get_roadmap(self, max_items: int = 20, include_stale: bool = True) -> List[RoadmapItem]:
        """Get the documentation roadmap."""
        if not self._roadmap:
            self.generate_roadmap()

        if include_stale:
            return self._roadmap[:max_items]
        else:
            return [item for item in self._roadmap if not item.is_stale()][:max_items]

    def get_roadmap_health(self) -> Dict[str, Any]:
        """
        Get health metrics for the roadmap.

        Returns staleness report and progress tracking.
        """
        if not self._roadmap:
            self.generate_roadmap()

        total = len(self._roadmap)
        stale = sum(1 for item in self._roadmap if item.is_stale())
        fresh = total - stale

        by_priority = {}
        by_action = {}
        by_effort = {}

        for item in self._roadmap:
            by_priority[item.priority] = by_priority.get(item.priority, 0) + 1
            by_action[item.action] = by_action.get(item.action, 0) + 1
            by_effort[item.estimated_effort] = by_effort.get(item.estimated_effort, 0) + 1

        return {
            "total_items": total,
            "fresh_items": fresh,
            "stale_items": stale,
            "staleness_ratio": stale / max(1, total),
            "by_priority": by_priority,
            "by_action": by_action,
            "by_effort": by_effort,
            "oldest_item_days": max((item.age_days() for item in self._roadmap), default=0),
            "is_healthy": stale == 0 or (stale / max(1, total)) < 0.3,
        }

    def generate_roadmap_intents(self, limit: int = 3) -> List[Dict[str, Any]]:
        """
        Generate intents from roadmap items.

        Returns ready-to-execute intents for MANAS.
        """
        intents = []
        roadmap = self.get_roadmap(max_items=limit)

        for item in roadmap:
            intent = {
                "id": f"roadmap_{item.action}_{hashlib.sha256(item.target.encode()).hexdigest()[:8]}",
                "intent_type": f"roadmap_{item.action}",
                "title": f"Roadmap: {item.description[:50]}",
                "description": item.description,
                "reasoning": f"Generated from documentation roadmap (priority {item.priority})",
                "priority": "high" if item.priority <= 2 else "medium",
                "risk": "safe",
                "params": item.to_dict(),
                "auto_executable": item.action == "add_harness",  # Only trivial tasks
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
    # Core
    "SutraSense",
    "SutraSummary",
    "DocCodeGap",
    "HarnessCheck",
    "get_sutra_sense",
    "SUTRA_SENSE_AVAILABLE",
    # Phase 2: Proactive Mode
    "HiddenCode",
    "IntentCluster",
    "DocEnhancement",
    "RoadmapItem",
]
