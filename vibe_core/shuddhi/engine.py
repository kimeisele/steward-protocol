"""
OPUS-212: ShuddhiEngine - The Surgical Orchestrator.

OPUS-307: No more hardcoded remedies!
Remedies are auto-discovered via RemedyLoader (VEDA-4 pattern).
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Type

import libcst as cst

from vibe_core.protocols.shuddhi import ShuddhiProtocol, ShuddhiResult, ShuddhiStatus
from vibe_core.shuddhi.remedies.base import CSTRemedy, ShuddhiScopeError
from vibe_core.shuddhi.remedy_loader import get_remedy_loader

logger = logging.getLogger("SHUDDHI")


class ShuddhiEngine(ShuddhiProtocol):
    """
    Implementation of the Shuddhi self-healing service.

    This engine manages the lifecycle of a healing operation:
    Parse -> Transform -> Verify -> Result.

    OPUS-307: Remedies are auto-discovered from vibe_core/shuddhi/remedies/
    No hardcoded imports - scales to hundreds of remedies.
    """

    def __init__(self):
        self._remedies: Dict[str, Type[CSTRemedy]] = {}
        self._loader = get_remedy_loader()
        self._discover_remedies()

    def _discover_remedies(self):
        """Auto-discover all remedies via RemedyLoader."""
        discovered = self._loader.discover_and_load()
        for rule_id, remedy_class in discovered.items():
            self._remedies[rule_id] = remedy_class
            logger.debug(f"[SHUDDHI] Discovered remedy: {rule_id}")

    def register_remedy(self, remedy_class: Type[CSTRemedy]):
        """Register a new healer class."""
        remedy = remedy_class()
        self._remedies[remedy.rule_id] = remedy_class
        logger.debug(f"[SHUDDHI] Registered remedy: {remedy.rule_id}")

    def purify(self, file_path: Path, rule_id: str) -> ShuddhiResult:
        """Heals a specific structural violation in a file."""
        if rule_id not in self._remedies:
            return ShuddhiResult(
                status=ShuddhiStatus.FAILED,
                file_path=file_path,
                rule_id=rule_id,
                message=f"No remedy registered for rule '{rule_id}'",
            )

        if not file_path.exists():
            return ShuddhiResult(
                status=ShuddhiStatus.FAILED,
                file_path=file_path,
                rule_id=rule_id,
                message="File not found",
            )

        try:
            # 1. Read and Parse
            source_code = file_path.read_text()
            module = cst.parse_module(source_code)

            # 2. Transform
            remedy_class = self._remedies[rule_id]
            transformer = remedy_class()

            try:
                modified_module = module.visit(transformer)
            except ShuddhiScopeError as e:
                return ShuddhiResult(
                    status=ShuddhiStatus.OUT_OF_SCOPE,
                    file_path=file_path,
                    rule_id=rule_id,
                    message=str(e),
                )

            # 3. Check if any changes were made
            if not transformer.applied:
                return ShuddhiResult(
                    status=ShuddhiStatus.SKIPPED,
                    file_path=file_path,
                    rule_id=rule_id,
                    message="No violations found in the file structure.",
                )

            new_code = modified_module.code

            # 4. Verify (Memory Compile)
            try:
                compile(new_code, str(file_path), "exec")
            except SyntaxError as e:
                logger.error(f"[SHUDDHI] Syntax error after transformation: {e}")
                return ShuddhiResult(
                    status=ShuddhiStatus.FAILED,
                    file_path=file_path,
                    rule_id=rule_id,
                    message=f"Transformation produced invalid syntax: {e}",
                )

            # 5. Success
            return ShuddhiResult(
                status=ShuddhiStatus.PURIFIED,
                file_path=file_path,
                rule_id=rule_id,
                message="Surgery successful.",
                diff=transformer.get_diff(source_code, new_code),
                purified_code=new_code,
            )

        except Exception as e:
            logger.exception(f"[SHUDDHI] Unexpected error purifying {file_path}: {e}")
            return ShuddhiResult(
                status=ShuddhiStatus.FAILED,
                file_path=file_path,
                rule_id=rule_id,
                message=f"Internal error: {str(e)}",
            )

    def list_remedies(self) -> List[str]:
        """Returns list of registered remedy rule_ids."""
        return list(self._remedies.keys())

    def can_heal(self, rule_id: str) -> bool:
        """Returns True if a remedy is registered for this rule_id."""
        return rule_id in self._remedies

    def add_remedy_path(self, path: Path) -> None:
        """
        Add a custom path for remedy discovery.

        Use Case: Agent-written remedies in a dynamic directory.
        This allows the system to write and load its own remedies.
        """
        self._loader.add_scan_path(path)
        # Re-discover to pick up new remedies
        self._discover_remedies()

    def refresh_remedies(self) -> None:
        """
        Force refresh of remedy discovery.

        Use Case: After system writes new remedies, call this to pick them up.
        """
        self._loader.clear_cache()
        self._discover_remedies()
