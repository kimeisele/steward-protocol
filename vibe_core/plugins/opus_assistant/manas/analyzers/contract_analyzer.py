"""
Contract Analyzer - The Immune System.

OPUS-032: Translates @HARNESS verification failures into repair intents.

This is the 50% analyzer - it fixes what's BROKEN.
The system feels "pain" when contracts are violated and generates
intents to heal itself.

Flow:
    HarnessResult.failures → ContractAnalyzer → List[Intent]
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from vibe_core.governance import ContractFailure, ContractFailureType

from ..intent_generator import Intent, IntentPriority, IntentRisk
from .base import AnalyzerConfig, BaseAnalyzer

logger = logging.getLogger("MANAS.ContractAnalyzer")


class ContractAnalyzer(BaseAnalyzer):
    """
    OPUS-032: The Immune System.

    Translates verification failures into repair intents.
    Each failure type maps to a specific intent with appropriate
    priority and risk levels.

    This is the "pain" response - when contracts break,
    the system feels it and generates healing impulses.
    """

    def __init__(
        self,
        workspace: Optional[Path] = None,
        config: Optional[AnalyzerConfig] = None,
    ):
        """Initialize ContractAnalyzer."""
        super().__init__(workspace=workspace, config=config)
        self._intent_counter = 0

    @property
    def name(self) -> str:
        """Analyzer name for logging and cooldowns."""
        return "contract_analyzer"

    def _next_id(self) -> str:
        """Generate next intent ID."""
        self._intent_counter += 1
        return f"contract_{self._intent_counter:04d}"

    def analyze(self, context: Dict[str, Any]) -> List[Intent]:
        """
        Analyze verification results and generate repair intents.

        Args:
            context: System context containing verification_results

        Returns:
            List of repair intents
        """
        intents: List[Intent] = []

        # Extract verification results injected by ContextService
        verification = context.get("verification_results", {})
        failures = verification.get("failures", [])

        if not failures:
            logger.debug("ContractAnalyzer: No failures to process")
            return []

        logger.info(f"ContractAnalyzer: Processing {len(failures)} failures")

        for failure in failures:
            intent = self._failure_to_intent(failure)
            if intent:
                intents.append(intent)

                # Respect max intents per run
                if len(intents) >= self._config.max_intents_per_run:
                    logger.debug(f"ContractAnalyzer: Hit max intents ({self._config.max_intents_per_run})")
                    break

        return intents

    def _failure_to_intent(self, failure: Any) -> Optional[Intent]:
        """
        Convert a failure to an intent.

        Args:
            failure: Either a ContractFailure object or a dict

        Returns:
            Intent or None if failure type not recognized
        """
        # Handle both ContractFailure objects and dicts
        if isinstance(failure, ContractFailure):
            f_type = failure.type
            f_path = failure.path
            f_message = failure.message
            f_source = failure.harness_source
            f_details = failure.details or {}
        elif isinstance(failure, dict):
            # Parse type from string if needed
            type_str = failure.get("type", "")
            try:
                if isinstance(type_str, str):
                    f_type = ContractFailureType[type_str]
                else:
                    f_type = type_str
            except (KeyError, TypeError):
                logger.warning(f"Unknown failure type: {type_str}")
                return None

            f_path = failure.get("path", "unknown")
            f_message = failure.get("message", "")
            f_source = failure.get("harness_source")
            f_details = failure.get("details", {})
        else:
            logger.warning(f"Unexpected failure format: {type(failure)}")
            return None

        # Map failure type to intent
        return self._create_intent_for_type(f_type, f_path, f_message, f_source, f_details)

    def _create_intent_for_type(
        self,
        failure_type: ContractFailureType,
        path: str,
        message: str,
        harness_source: Optional[str],
        details: Dict[str, Any],
    ) -> Optional[Intent]:
        """
        Create an intent based on failure type.

        Each failure type has specific handling.
        """
        # === FILE-LEVEL FAILURES ===
        if failure_type == ContractFailureType.FILE_MISSING:
            return Intent(
                id=self._next_id(),
                intent_type="contract_file_create",
                title=f"Restore missing file: {Path(path).name}",
                description=f"Required file `{path}` is defined in @HARNESS but missing from disk.",
                reasoning=f"Contract violation detected. Source: {harness_source or 'unknown'}",
                priority=IntentPriority.HIGH,
                risk=IntentRisk.MEDIUM,
                params={
                    "file_path": path,
                    "failure_type": failure_type.name,
                    "harness_source": harness_source,
                    **details,
                },
                auto_executable=False,  # Creating files needs approval
                # WEAVING: Link the missing file + harness doc
                related_files=[path],
                related_docs=[harness_source] if harness_source else [],
            )

        if failure_type == ContractFailureType.FILE_EXTRA:
            return Intent(
                id=self._next_id(),
                intent_type="contract_file_review",
                title=f"Review unexpected file: {Path(path).name}",
                description=f"File `{path}` exists but is marked as 'absent' in @HARNESS.",
                reasoning="File should not exist according to contract. Review and remove if stale.",
                priority=IntentPriority.LOW,
                risk=IntentRisk.LOW,
                params={
                    "file_path": path,
                    "failure_type": failure_type.name,
                    "harness_source": harness_source,
                },
                auto_executable=False,
                related_files=[path],
                related_docs=[harness_source] if harness_source else [],
            )

        # === PATTERN-LEVEL FAILURES ===
        if failure_type == ContractFailureType.PATTERN_MISSING:
            return Intent(
                id=self._next_id(),
                intent_type="contract_pattern_fix",
                title=f"Fix missing pattern in: {Path(path).name}",
                description=f"Required wiring pattern not found in `{path}`. {message}",
                reasoning="Contract requires specific code pattern that is missing.",
                priority=IntentPriority.HIGH,
                risk=IntentRisk.MEDIUM,
                params={
                    "file_path": path,
                    "failure_type": failure_type.name,
                    "expected_pattern": details.get("pattern"),
                    "harness_source": harness_source,
                },
                auto_executable=False,
                related_files=[path],
                related_docs=[harness_source] if harness_source else [],
            )

        if failure_type == ContractFailureType.PATTERN_BROKEN:
            return Intent(
                id=self._next_id(),
                intent_type="contract_pattern_fix",
                title=f"Fix broken pattern in: {Path(path).name}",
                description=f"Pattern exists but has syntax errors in `{path}`. {message}",
                reasoning="Contract pattern found but malformed.",
                priority=IntentPriority.HIGH,
                risk=IntentRisk.MEDIUM,
                params={
                    "file_path": path,
                    "failure_type": failure_type.name,
                    "harness_source": harness_source,
                },
                auto_executable=False,
                related_files=[path],
                related_docs=[harness_source] if harness_source else [],
            )

        # === DOC-LEVEL FAILURES (Auto-fixable!) ===
        if failure_type == ContractFailureType.DOC_STALE:
            # 🌟 This is the 51% auto-fix candidate!
            return Intent(
                id=self._next_id(),
                intent_type="contract_doc_update",
                title=f"Update stale documentation: {Path(path).name}",
                description=f"Documentation in `{path}` references outdated paths or APIs. {message}",
                reasoning="Documentation drift causes confusion. Safe to auto-update.",
                priority=IntentPriority.LOW,
                risk=IntentRisk.SAFE,  # Safe to auto-execute!
                params={
                    "file_path": path,
                    "failure_type": failure_type.name,
                    "harness_source": harness_source,
                },
                auto_executable=True,  # 🙏 Earned autonomy for doc fixes
                related_docs=[path],  # The stale doc itself
            )

        if failure_type == ContractFailureType.DOC_INCOMPLETE:
            return Intent(
                id=self._next_id(),
                intent_type="contract_doc_complete",
                title=f"Complete documentation: {Path(path).name}",
                description=f"Documentation in `{path}` is missing required sections. {message}",
                reasoning="Incomplete docs reduce usability.",
                priority=IntentPriority.LOW,
                risk=IntentRisk.SAFE,
                params={
                    "file_path": path,
                    "failure_type": failure_type.name,
                    "missing_sections": details.get("missing_sections", []),
                },
                auto_executable=True,
                related_docs=[path],  # The incomplete doc
            )

        # === SEMANTIC FAILURES ===
        if failure_type == ContractFailureType.SEMANTIC_IMPORT_FAIL:
            return Intent(
                id=self._next_id(),
                intent_type="contract_import_fix",
                title=f"Fix import failure: {Path(path).name}",
                description=f"Module `{path}` cannot be imported. {message}",
                reasoning="FATAL: Broken imports block system functionality.",
                priority=IntentPriority.CRITICAL,
                risk=IntentRisk.HIGH,  # Import fixes can have side effects
                params={
                    "file_path": path,
                    "failure_type": failure_type.name,
                    "import_error": details.get("error"),
                },
                auto_executable=False,  # Never auto-fix import errors
                related_files=[path],
                related_docs=[harness_source] if harness_source else [],
            )

        if failure_type == ContractFailureType.SEMANTIC_TEST_FAIL:
            return Intent(
                id=self._next_id(),
                intent_type="contract_test_fix",
                title=f"Fix failing test: {Path(path).name}",
                description=f"Test in `{path}` is failing. {message}",
                reasoning="TDD Dharma: Tests must pass for system integrity.",
                priority=IntentPriority.HIGH,
                risk=IntentRisk.MEDIUM,
                params={
                    "file_path": path,
                    "failure_type": failure_type.name,
                    "test_output": details.get("output"),
                },
                auto_executable=False,
                related_files=[path],
            )

        logger.warning(f"Unhandled failure type: {failure_type}")
        return None
