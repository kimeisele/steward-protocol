"""
OPUS-212: ShuddhiEngine - The Surgical Orchestrator.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Type

import libcst as cst

from vibe_core.protocols.shuddhi import ShuddhiProtocol, ShuddhiResult, ShuddhiStatus
from vibe_core.shuddhi.remedies.base import CSTRemedy, ShuddhiScopeError

logger = logging.getLogger("SHUDDHI")


class ShuddhiEngine(ShuddhiProtocol):
    """
    Implementation of the Shuddhi self-healing service.

    This engine manages the lifecycle of a healing operation:
    Parse -> Transform -> Verify -> Result.
    """

    def __init__(self):
        self._remedies: Dict[str, Type[CSTRemedy]] = {}
        self._register_default_remedies()

    def _register_default_remedies(self):
        """Register built-in healers."""
        from vibe_core.shuddhi.remedies.silent_except import SilentExceptRemedy
        from vibe_core.shuddhi.remedies.subprocess_timeout import SubprocessTimeoutRemedy
        from vibe_core.shuddhi.remedies.unsafe_io_write import UnsafeIOWriteRemedy

        self.register_remedy(UnsafeIOWriteRemedy)
        self.register_remedy(SubprocessTimeoutRemedy)
        self.register_remedy(SilentExceptRemedy)

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
