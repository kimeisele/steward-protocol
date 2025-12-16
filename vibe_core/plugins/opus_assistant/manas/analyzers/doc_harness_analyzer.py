"""
Doc Harness Analyzer - The Self-Healing Documentation System.

OPUS-083: MANAS learns to maintain its own architecture docs.

This analyzer scans docs/architecture/OPUS/*.md files and:
1. Detects missing @HARNESS sections
2. Validates existing harnesses (are referenced files/tests real?)
3. Auto-generates harness suggestions for Sanskrit module docs (050-060)

This is "soft brain training" - low-risk intents that help MANAS
learn the karma loop: generate → execute → success/fail → learn.

Sanskrit Module Mapping (050-060 series):
    OPUS-050-VEDA.md     → vibe_core/.../manas/cortex/veda.py
    OPUS-051-MANDALA.md  → vibe_core/.../manas/cortex/mandala.py
    etc.
"""

import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..intent_generator import Intent, IntentPriority, IntentRisk
from .base import AnalyzerConfig, BaseAnalyzer

logger = logging.getLogger("MANAS.DocHarnessAnalyzer")

# Sanskrit module files that should have auto-generated harnesses
SANSKRIT_MODULE_MAP = {
    "050-VEDA": "veda",
    "051-MANDALA": "mandala",
    "052-AKASHA": "akasha",
    "053-SILPA": "silpa",
    "054-SUTRA": "sutra",
    "055-SANKALPA": "sankalpa",
    "056-SHUDDHI": "shuddhi",
    "057-VAJRA": "vajra",
    "058-PRATYAHARA": "pratyahara",
    "059-PRAMANA": "pramana",
    "060-SATYA": "satya",
}


class HarnessAnalysisResult:
    """Result of analyzing a single OPUS file's harness."""

    def __init__(self, opus_file: Path):
        self.opus_file = opus_file
        self.has_harness = False
        self.harness_content: Optional[str] = None

        # Validation results
        self.files_section: List[str] = []
        self.files_missing: List[str] = []
        self.wiring_section: List[Dict] = []
        self.wiring_broken: List[Dict] = []
        self.tests_section: List[str] = []
        self.tests_missing: List[str] = []

        # Meta
        self.is_sanskrit_module = False
        self.sanskrit_module_name: Optional[str] = None
        self.can_auto_generate = False

    @property
    def is_valid(self) -> bool:
        """Is the harness valid (all references exist)?"""
        if not self.has_harness:
            return False
        return len(self.files_missing) == 0 and len(self.wiring_broken) == 0 and len(self.tests_missing) == 0

    @property
    def quality_score(self) -> float:
        """Quality score 0.0-1.0 based on harness completeness."""
        if not self.has_harness:
            return 0.0

        total = len(self.files_section) + len(self.wiring_section) + len(self.tests_section)
        if total == 0:
            return 0.5  # Empty harness

        broken = len(self.files_missing) + len(self.wiring_broken) + len(self.tests_missing)
        return max(0.0, 1.0 - (broken / total))


class DocHarnessAnalyzer(BaseAnalyzer):
    """
    MANAS Analyzer for documentation harness health.

    Scans OPUS architecture docs and generates intents to:
    - Add missing harnesses
    - Fix broken harness references
    - Auto-generate harnesses for Sanskrit module docs

    This is "soft" training ground for MANAS karma system.
    """

    def __init__(
        self,
        workspace: Optional[Path] = None,
        config: Optional[AnalyzerConfig] = None,
    ):
        super().__init__(workspace=workspace, config=config)
        self._intent_counter = 0
        self._opus_dir = self._workspace / "docs" / "architecture" / "OPUS"
        self._cortex_dir = self._workspace / "vibe_core" / "plugins" / "opus_assistant" / "manas" / "cortex"

    @property
    def name(self) -> str:
        return "doc_harness_analyzer"

    def _next_id(self) -> str:
        self._intent_counter += 1
        return f"harness_{self._intent_counter:04d}"

    def analyze(self, context: Dict[str, Any]) -> List[Intent]:
        """
        Analyze OPUS docs and generate harness-related intents.

        Returns intents for:
        - Missing harnesses (especially Sanskrit modules)
        - Broken harness references
        - Auto-generation opportunities
        """
        intents: List[Intent] = []

        if not self._opus_dir.exists():
            logger.warning(f"OPUS dir not found: {self._opus_dir}")
            return []

        opus_files = list(self._opus_dir.glob("*.md"))
        logger.info(f"DocHarnessAnalyzer: Scanning {len(opus_files)} OPUS files")

        for opus_file in opus_files:
            # Skip index/readme
            if opus_file.name.lower() in ("readme.md", "000-index.md"):
                continue

            result = self._analyze_file(opus_file)

            # Generate intents based on analysis
            file_intents = self._result_to_intents(result)
            intents.extend(file_intents)

            # Respect max intents
            if len(intents) >= self._config.max_intents_per_run:
                logger.debug(f"DocHarnessAnalyzer: Hit max intents ({self._config.max_intents_per_run})")
                break

        return intents

    def _analyze_file(self, opus_file: Path) -> HarnessAnalysisResult:
        """Analyze a single OPUS file for harness quality."""
        result = HarnessAnalysisResult(opus_file)

        content = opus_file.read_text()

        # Check if it's a Sanskrit module file
        for prefix, module_name in SANSKRIT_MODULE_MAP.items():
            if opus_file.name.upper().startswith(prefix):
                result.is_sanskrit_module = True
                result.sanskrit_module_name = module_name
                result.can_auto_generate = True
                break

        # Extract @HARNESS block
        harness_match = re.search(
            r"<!--\s*@HARNESS\s*(.*?)\s*-->",
            content,
            re.DOTALL | re.IGNORECASE,
        )

        if not harness_match:
            result.has_harness = False
            return result

        result.has_harness = True
        result.harness_content = harness_match.group(1)

        # Parse and validate harness
        self._validate_harness(result)

        return result

    def _validate_harness(self, result: HarnessAnalysisResult) -> None:
        """Validate harness content - check if referenced files exist."""
        if not result.harness_content:
            return

        content = result.harness_content

        # Extract files: section
        # FIXED: Match ALL indented lines (not just lines starting with -)
        # This handles multi-line YAML items like:
        #   - path: foo.py
        #     required: true
        # Note: Last line may not have trailing newline (before -->)
        files_match = re.search(r"files:\s*\n((?:\s+.*(?:\n|$))*)", content)
        if files_match:
            files_block = files_match.group(1)
            paths = re.findall(r"path:\s*([^\s\n]+)", files_block)
            result.files_section = paths

            for path in paths:
                full_path = self._workspace / path
                if not full_path.exists():
                    result.files_missing.append(path)

        # Extract tests: section
        # FIXED: Match ALL indented lines until next section or end
        # Note: Last line before --> may not have trailing newline
        tests_match = re.search(r"tests:\s*\n((?:\s+.*(?:\n|$))*)", content)
        if tests_match:
            tests_block = tests_match.group(1)
            test_paths = re.findall(r"-\s*([^\s\n]+\.py)", tests_block)
            result.tests_section = test_paths

            for test_path in test_paths:
                full_path = self._workspace / test_path
                if not full_path.exists():
                    result.tests_missing.append(test_path)

        # Extract wiring: section and validate patterns
        # FIXED: Match ALL indented lines (including comments and multi-line items)
        # Note: Last line may not have trailing newline
        wiring_match = re.search(r"wiring:\s*\n((?:\s+.*(?:\n|$))*)", content)
        if wiring_match:
            wiring_block = wiring_match.group(1)
            # Extract pattern/in pairs
            patterns = re.findall(
                r'-\s*pattern:\s*["\']?([^"\'\n]+)["\']?\s*\n\s*in:\s*([^\s\n]+)',
                wiring_block,
            )
            for pattern, in_file in patterns:
                wiring_entry = {"pattern": pattern, "in": in_file}
                result.wiring_section.append(wiring_entry)

                # Check if file exists
                full_path = self._workspace / in_file
                if not full_path.exists():
                    result.wiring_broken.append(wiring_entry)
                else:
                    # Check if pattern is found
                    try:
                        file_content = full_path.read_text()
                        if not re.search(pattern, file_content):
                            result.wiring_broken.append(wiring_entry)
                    except Exception:
                        result.wiring_broken.append(wiring_entry)

    def _result_to_intents(self, result: HarnessAnalysisResult) -> List[Intent]:
        """Convert analysis result to intents."""
        intents = []
        opus_name = result.opus_file.stem

        # Case 1: No harness at all
        if not result.has_harness:
            if result.is_sanskrit_module and result.can_auto_generate:
                # High-value: Auto-generate harness for Sanskrit module
                intents.append(
                    Intent(
                        id=self._next_id(),
                        intent_type="harness_auto_generate",
                        title=f"Auto-generate @HARNESS for {opus_name}",
                        description=(
                            f"Sanskrit module doc {result.opus_file.name} has no @HARNESS. "
                            f"Can auto-generate based on {result.sanskrit_module_name}.py module."
                        ),
                        reasoning=(
                            f"Module {result.sanskrit_module_name}.py exists in cortex/. "
                            "The harness can be generated from code structure. "
                            "This is low-risk training for MANAS karma system."
                        ),
                        priority=IntentPriority.MEDIUM,
                        risk=IntentRisk.SAFE,  # Only writes markdown
                        auto_executable=True,  # Safe to auto-execute
                        params={
                            "opus_file": str(result.opus_file),
                            "module_name": result.sanskrit_module_name,
                            "action": "generate_harness",
                        },
                    )
                )
            else:
                # Standard missing harness
                intents.append(
                    Intent(
                        id=self._next_id(),
                        intent_type="harness_missing",
                        title=f"Add @HARNESS to {opus_name}",
                        description=f"OPUS doc {result.opus_file.name} has no @HARNESS section.",
                        reasoning="Harness provides machine-verifiable contract. Without it, doc is just words.",
                        priority=IntentPriority.LOW,
                        risk=IntentRisk.LOW,
                        auto_executable=False,  # Needs human to write harness
                        params={
                            "opus_file": str(result.opus_file),
                            "action": "add_harness",
                        },
                    )
                )

        # Case 2: Broken harness (references don't exist)
        elif not result.is_valid:
            broken_refs = []
            if result.files_missing:
                broken_refs.append(f"files: {result.files_missing}")
            if result.tests_missing:
                broken_refs.append(f"tests: {result.tests_missing}")
            if result.wiring_broken:
                broken_refs.append(f"wiring: {len(result.wiring_broken)} broken patterns")

            intents.append(
                Intent(
                    id=self._next_id(),
                    intent_type="harness_broken",
                    title=f"Fix broken @HARNESS in {opus_name}",
                    description=f"Harness references non-existent files/tests: {', '.join(broken_refs)}",
                    reasoning=f"Quality score: {result.quality_score:.0%}. Broken harness is worse than no harness.",
                    priority=IntentPriority.MEDIUM,
                    risk=IntentRisk.LOW,
                    auto_executable=False,
                    params={
                        "opus_file": str(result.opus_file),
                        "files_missing": result.files_missing,
                        "tests_missing": result.tests_missing,
                        "wiring_broken": [w["in"] for w in result.wiring_broken],
                        "quality_score": result.quality_score,
                        "action": "fix_harness",
                    },
                )
            )

        return intents

    def get_harness_report(self) -> Dict[str, Any]:
        """
        Generate a full harness health report.

        Useful for dashboard/OPUS.md display.
        """
        if not self._opus_dir.exists():
            return {"error": "OPUS dir not found"}

        opus_files = list(self._opus_dir.glob("*.md"))
        total = len(opus_files)
        with_harness = 0
        valid_harness = 0
        sanskrit_missing = []
        broken = []

        for opus_file in opus_files:
            if opus_file.name.lower() in ("readme.md", "000-index.md"):
                continue

            result = self._analyze_file(opus_file)

            if result.has_harness:
                with_harness += 1
                if result.is_valid:
                    valid_harness += 1
                else:
                    broken.append(opus_file.name)
            elif result.is_sanskrit_module:
                sanskrit_missing.append(opus_file.name)

        return {
            "total_files": total,
            "with_harness": with_harness,
            "without_harness": total - with_harness,
            "valid_harness": valid_harness,
            "broken_harness": len(broken),
            "broken_files": broken,
            "sanskrit_missing_harness": sanskrit_missing,
            "coverage_percent": (with_harness / total * 100) if total > 0 else 0,
            "quality_percent": (valid_harness / with_harness * 100) if with_harness > 0 else 0,
        }
