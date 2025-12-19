"""
Doc Harness Analyzer - The Self-Healing Documentation System.

OPUS-083: MANAS learns to maintain its own architecture docs.
OPUS-128: Edge Case Hardening - Watertight harness verification.

This analyzer scans docs/architecture/OPUS/*.md files and:
1. Detects missing @HARNESS sections
2. Validates existing harnesses (are referenced files/tests real?)
3. Auto-generates harness suggestions for Sanskrit module docs (050-060)
4. Handles edge cases: SUPERSEDED docs, TDD contracts, moved files

This is "soft brain training" - low-risk intents that help MANAS
learn the karma loop: generate → execute → success/fail → learn.

Sanskrit Module Mapping (050-060 series):
    OPUS-050-VEDA.md     → vibe_core/.../manas/cortex/veda.py
    OPUS-051-MANDALA.md  → vibe_core/.../manas/cortex/mandala.py
    etc.

Edge Case Handling (OPUS-128):
    - SUPERSEDED docs: Skip validation, no intents generated
    - TDD contracts (PLANNED status): Red harness is CORRECT
    - Moved files: Search repo-wide before flagging as missing
    - Required flag: Only required=true triggers broken status
"""

import json
import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from ..intent_generator import Intent, IntentPriority, IntentRisk
from .base import AnalyzerConfig, BaseAnalyzer

logger = logging.getLogger("MANAS.DocHarnessAnalyzer")

# Document status constants (OPUS-128)
STATUS_SUPERSEDED = "superseded"
STATUS_DEPRECATED = "deprecated"
STATUS_PLANNED = "planned"
STATUS_IN_PROGRESS = "in_progress"
STATUS_ACTIVE = "active"
STATUS_IMPLEMENTED = "implemented"

# Statuses where harness is a TDD contract (red = correct)
TDD_CONTRACT_STATUSES = {STATUS_PLANNED, STATUS_IN_PROGRESS}

# Statuses where harness should be skipped
SKIP_VALIDATION_STATUSES = {STATUS_SUPERSEDED, STATUS_DEPRECATED}

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

        # OPUS-128: Document status tracking
        self.doc_status: Optional[str] = None  # From header: SUPERSEDED, PLANNED, etc.
        self.superseded_by: Optional[str] = None  # What supersedes this doc
        self.is_tdd_contract = False  # True if harness is a TDD contract (PLANNED/IN_PROGRESS)
        self.skip_validation = False  # True if doc is SUPERSEDED/DEPRECATED

        # Validation results
        self.files_section: List[str] = []
        self.files_missing: List[str] = []
        self.files_required: Dict[str, bool] = {}  # path -> required flag
        self.files_found_elsewhere: Dict[str, str] = {}  # missing_path -> found_at_path
        self.wiring_section: List[Dict] = []
        self.wiring_broken: List[Dict] = []
        self.wiring_found_elsewhere: Dict[str, str] = {}  # pattern -> found_at_file
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
        # OPUS-128: Only count REQUIRED missing files
        required_missing = [f for f in self.files_missing if self.files_required.get(f, True)]
        return len(required_missing) == 0 and len(self.wiring_broken) == 0 and len(self.tests_missing) == 0

    @property
    def quality_score(self) -> float:
        """Quality score 0.0-1.0 based on harness completeness."""
        if not self.has_harness:
            return 0.0

        total = len(self.files_section) + len(self.wiring_section) + len(self.tests_section)
        if total == 0:
            return 0.5  # Empty harness

        # OPUS-128: Count only required missing files
        required_missing = [f for f in self.files_missing if self.files_required.get(f, True)]
        broken = len(required_missing) + len(self.wiring_broken) + len(self.tests_missing)
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

        # OPUS-128: Load manifest.json for authoritative status
        self._manifest: Dict[str, Any] = {}
        self._manifest_status: Dict[str, str] = {}  # file_name -> status
        self._load_manifest()

    @property
    def name(self) -> str:
        return "doc_harness_analyzer"

    def _load_manifest(self) -> None:
        """OPUS-128: Load manifest.json for authoritative document status."""
        manifest_path = self._opus_dir / "manifest.json"
        if not manifest_path.exists():
            logger.debug("No manifest.json found - status detection from headers only")
            return

        try:
            with open(manifest_path) as f:
                self._manifest = json.load(f)

            # Build file -> status lookup
            for doc in self._manifest.get("documents", []):
                file_name = doc.get("file", "")
                status = doc.get("status", "")
                if file_name and status:
                    self._manifest_status[file_name] = status.lower()
                    logger.debug(f"Manifest: {file_name} -> {status}")

            logger.info(f"DocHarnessAnalyzer: Loaded manifest with {len(self._manifest_status)} docs")
        except Exception as e:
            logger.warning(f"Failed to load manifest.json: {e}")

    def _get_doc_status(self, opus_file: Path, content: str) -> Tuple[Optional[str], Optional[str]]:
        """
        OPUS-128: Get document status from header or manifest.

        Returns: (status, superseded_by)
        """
        file_name = opus_file.name

        # Priority 1: Check manifest.json (authoritative)
        if file_name in self._manifest_status:
            manifest_status = self._manifest_status[file_name]
            logger.debug(f"Status from manifest: {file_name} = {manifest_status}")
            return manifest_status, None

        # Priority 2: Parse from document header
        # Look for: > **Status**: SUPERSEDED
        status_match = re.search(
            r">\s*\*\*Status\*\*\s*:\s*(\w+)",
            content,
            re.IGNORECASE,
        )
        if status_match:
            status = status_match.group(1).lower()
            logger.debug(f"Status from header: {file_name} = {status}")

            # Also look for: > **Superseded By**: OPUS-XXX
            superseded_match = re.search(
                r">\s*\*\*Superseded By\*\*\s*:\s*(.+?)(?:\n|$)",
                content,
                re.IGNORECASE,
            )
            superseded_by = superseded_match.group(1).strip() if superseded_match else None

            return status, superseded_by

        return None, None

    def _search_file_elsewhere(self, missing_path: str) -> Optional[str]:
        """
        OPUS-128: Search for a missing file elsewhere in the repo.

        If harness says 'vibe_core/old/foo.py' but file moved to 'vibe_core/new/foo.py',
        this will find it and return the new path.
        """
        filename = Path(missing_path).name

        # Search in common locations
        search_dirs = [
            self._workspace / "vibe_core",
            self._workspace / "tests",
        ]

        for search_dir in search_dirs:
            if not search_dir.exists():
                continue
            for found_path in search_dir.rglob(filename):
                # Return relative path
                rel_path = found_path.relative_to(self._workspace)
                if str(rel_path) != missing_path:  # Actually moved
                    logger.debug(f"File '{filename}' found at: {rel_path} (harness says: {missing_path})")
                    return str(rel_path)

        return None

    def _search_pattern_elsewhere(self, pattern: str, exclude_file: str) -> Optional[str]:
        """
        OPUS-128: Search for a wiring pattern elsewhere in the repo.

        If harness says pattern 'class Foo' should be in 'old.py' but class moved to 'new.py',
        this will find it.
        """
        try:
            # Compile pattern for efficiency
            regex = re.compile(pattern)
        except re.error:
            return None

        # Search Python files in vibe_core
        search_dir = self._workspace / "vibe_core"
        if not search_dir.exists():
            return None

        for py_file in search_dir.rglob("*.py"):
            rel_path = str(py_file.relative_to(self._workspace))
            if rel_path == exclude_file:
                continue

            try:
                content = py_file.read_text()
                if regex.search(content):
                    logger.debug(f"Pattern '{pattern}' found in: {rel_path} (harness says: {exclude_file})")
                    return rel_path
            except Exception:
                continue

        return None

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

        # OPUS-128: Detect document status
        status, superseded_by = self._get_doc_status(opus_file, content)
        result.doc_status = status
        result.superseded_by = superseded_by

        if status:
            # Check if doc is superseded/deprecated (skip validation)
            if status in SKIP_VALIDATION_STATUSES:
                result.skip_validation = True
                logger.debug(f"Skipping validation for {opus_file.name}: status={status}")

            # Check if doc is a TDD contract (red harness = correct)
            elif status in TDD_CONTRACT_STATUSES:
                result.is_tdd_contract = True
                logger.debug(f"TDD contract detected for {opus_file.name}: status={status}")

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

        # OPUS-128: Skip validation for superseded docs
        if result.skip_validation:
            logger.debug(f"Harness validation skipped for superseded doc: {opus_file.name}")
            return result

        # Parse and validate harness
        self._validate_harness(result)

        return result

    def _validate_harness(self, result: HarnessAnalysisResult) -> None:
        """Validate harness content - check if referenced files exist."""
        if not result.harness_content:
            return

        content = result.harness_content

        # Extract files: section
        # OPUS-128: Also parse required flag
        # This handles multi-line YAML items like:
        #   - path: foo.py
        #     required: true
        files_match = re.search(r"files:\s*\n((?:\s+.*(?:\n|$))*)", content)
        if files_match:
            files_block = files_match.group(1)

            # Parse each file entry to get path and required flag
            # Match entries like:
            #   - path: vibe_core/foo.py
            #     required: true
            file_entries = re.findall(
                r"-\s*path:\s*([^\s\n]+)(?:\s*\n\s*required:\s*(true|false))?",
                files_block,
                re.IGNORECASE,
            )

            for entry in file_entries:
                path = entry[0]
                # Default to required=True if not specified
                required = entry[1].lower() != "false" if entry[1] else True
                result.files_section.append(path)
                result.files_required[path] = required

                full_path = self._workspace / path
                if not full_path.exists():
                    result.files_missing.append(path)

                    # OPUS-128: Search for file elsewhere
                    found_at = self._search_file_elsewhere(path)
                    if found_at:
                        result.files_found_elsewhere[path] = found_at

        # Extract tests: section
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

                    # OPUS-128: Search for pattern elsewhere
                    found_at = self._search_pattern_elsewhere(pattern, in_file)
                    if found_at:
                        result.wiring_found_elsewhere[pattern] = found_at
                else:
                    # Check if pattern is found
                    try:
                        file_content = full_path.read_text()
                        if not re.search(pattern, file_content):
                            result.wiring_broken.append(wiring_entry)

                            # OPUS-128: Search for pattern elsewhere
                            found_at = self._search_pattern_elsewhere(pattern, in_file)
                            if found_at:
                                result.wiring_found_elsewhere[pattern] = found_at
                    except Exception:
                        result.wiring_broken.append(wiring_entry)

    def _result_to_intents(self, result: HarnessAnalysisResult) -> List[Intent]:
        """
        Convert analysis result to intents.

        OPUS-128 Edge Cases:
        1. SUPERSEDED docs: Skip entirely (no intents)
        2. TDD contracts: Red harness = correct, generate info intent
        3. Moved files: Generate stale_reference intent with found_at hint
        4. Optional missing: Lower priority than required missing
        """
        intents = []
        opus_name = result.opus_file.stem

        # OPUS-128: Skip superseded/deprecated docs entirely
        if result.skip_validation:
            logger.info(f"Skipping intents for superseded doc: {opus_name}")
            return []

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
                        # WEAVING: Link to related code/docs
                        related_files=[f"manas/cortex/{result.sanskrit_module_name}.py"],
                        related_docs=[result.opus_file.name],
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
                        # WEAVING: Link to the doc that needs harness
                        related_docs=[result.opus_file.name],
                    )
                )

        # Case 2: Has harness but not valid
        elif not result.is_valid:
            # OPUS-128: Check if this is a TDD contract (red = correct)
            if result.is_tdd_contract:
                # TDD contract: The harness is INTENTIONALLY red
                # This is NOT an error - it's a spec for what needs to be built
                required_missing = [f for f in result.files_missing if result.files_required.get(f, True)]
                intents.append(
                    Intent(
                        id=self._next_id(),
                        intent_type="harness_tdd_contract",
                        title=f"TDD Contract: {opus_name} ({len(required_missing)} files to implement)",
                        description=(
                            f"Status: {result.doc_status.upper()}. "
                            f"Harness defines TDD contract - red status is CORRECT. "
                            f"Files to create: {required_missing}"
                        ),
                        reasoning=(
                            "Red harness is intentional for PLANNED/IN_PROGRESS docs. "
                            "The harness specifies WHAT needs to be built, not WHAT is broken."
                        ),
                        priority=IntentPriority.HIGH,  # High priority to implement
                        risk=IntentRisk.MEDIUM,  # Creating new files
                        auto_executable=False,  # Human needs to implement
                        params={
                            "opus_file": str(result.opus_file),
                            "doc_status": result.doc_status,
                            "files_to_create": required_missing,
                            "wiring_to_implement": [w["pattern"] for w in result.wiring_broken],
                            "action": "implement_tdd_contract",
                        },
                        related_files=required_missing[:5],
                        related_docs=[result.opus_file.name],
                    )
                )
            else:
                # OPUS-128: Check if files/patterns were found elsewhere (stale reference)
                has_stale_refs = bool(result.files_found_elsewhere or result.wiring_found_elsewhere)

                if has_stale_refs:
                    # Files/patterns moved - generate update-reference intent
                    stale_files = [f"{old} → {new}" for old, new in result.files_found_elsewhere.items()]
                    stale_wiring = [f"'{pattern}' → {new}" for pattern, new in result.wiring_found_elsewhere.items()]
                    all_stale = stale_files + stale_wiring

                    intents.append(
                        Intent(
                            id=self._next_id(),
                            intent_type="harness_stale_reference",
                            title=f"Update stale references in {opus_name}",
                            description=(
                                f"Files/patterns moved to new locations. "
                                f"Moves detected: {', '.join(all_stale[:3])}" + ("..." if len(all_stale) > 3 else "")
                            ),
                            reasoning=(
                                "Code was refactored but harness not updated. "
                                "The references are stale, not broken. Update the harness paths."
                            ),
                            priority=IntentPriority.MEDIUM,
                            risk=IntentRisk.SAFE,  # Just updating doc
                            auto_executable=True,  # Can auto-fix paths
                            params={
                                "opus_file": str(result.opus_file),
                                "files_moved": result.files_found_elsewhere,
                                "wiring_moved": result.wiring_found_elsewhere,
                                "action": "update_stale_references",
                            },
                            related_docs=[result.opus_file.name],
                        )
                    )

                # OPUS-128: Separate required vs optional missing
                required_missing = [f for f in result.files_missing if result.files_required.get(f, True)]
                optional_missing = [f for f in result.files_missing if not result.files_required.get(f, True)]

                # Only generate broken intent if there are REQUIRED missing files
                # that weren't found elsewhere
                truly_missing_required = [f for f in required_missing if f not in result.files_found_elsewhere]
                truly_broken_wiring = [
                    w for w in result.wiring_broken if w["pattern"] not in result.wiring_found_elsewhere
                ]

                if truly_missing_required or truly_broken_wiring or result.tests_missing:
                    broken_refs = []
                    if truly_missing_required:
                        broken_refs.append(f"files: {truly_missing_required}")
                    if result.tests_missing:
                        broken_refs.append(f"tests: {result.tests_missing}")
                    if truly_broken_wiring:
                        broken_refs.append(f"wiring: {len(truly_broken_wiring)} broken patterns")

                    # WEAVING: Collect all broken files for semantic links
                    weave_files = truly_missing_required + [w["in"] for w in truly_broken_wiring]
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
                                "files_missing": truly_missing_required,
                                "files_optional_missing": optional_missing,
                                "tests_missing": result.tests_missing,
                                "wiring_broken": [w["in"] for w in truly_broken_wiring],
                                "quality_score": result.quality_score,
                                "action": "fix_harness",
                            },
                            # WEAVING: Link broken files + doc
                            related_files=weave_files[:5],  # Cap at 5 to avoid clutter
                            related_docs=[result.opus_file.name],
                        )
                    )

                # Low priority intent for optional missing files
                if optional_missing:
                    intents.append(
                        Intent(
                            id=self._next_id(),
                            intent_type="harness_optional_missing",
                            title=f"Optional files missing in {opus_name}",
                            description=f"Optional (required=false) files not found: {optional_missing}",
                            reasoning="These files are marked as optional. No action required unless desired.",
                            priority=IntentPriority.LOW,  # Low priority (optional files)
                            risk=IntentRisk.SAFE,
                            auto_executable=False,
                            params={
                                "opus_file": str(result.opus_file),
                                "files_missing": optional_missing,
                                "action": "info_only",
                            },
                            related_docs=[result.opus_file.name],
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
