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

    # =========================================================================
    # OUROBOROS: Knowledge Graph Integration
    # =========================================================================

    def heal_and_record(
        self,
        file_path: Path,
        rule_id: str,
        violation_id: Optional[str] = None,
        write_file: bool = False,
    ) -> ShuddhiResult:
        """
        OUROBOROS: Heal a violation AND record the healing in Knowledge Graph.

        This is the Nadi (channel) between Shuddhi and the self-healing loop.
        When healing succeeds, the violation is marked as healed in KG.

        Args:
            file_path: Path to the file to heal
            rule_id: The rule ID to apply
            violation_id: Optional KG node ID to mark as healed
            write_file: If True, write the healed code to disk

        Returns:
            ShuddhiResult with healing outcome
        """
        # 1. Perform the healing
        result = self.purify(file_path, rule_id)

        # 2. If successful, update Knowledge Graph
        if result.status == ShuddhiStatus.PURIFIED:
            try:
                from vibe_core.di import ServiceRegistry
                from vibe_core.knowledge.graph import UnifiedKnowledgeGraph

                kg = ServiceRegistry.get(UnifiedKnowledgeGraph)
                if kg and violation_id:
                    kg.mark_violation_healed(violation_id, rule_id)
                    logger.info(f"[SHUDDHI→KG] Marked violation {violation_id} as healed")

                # 3. Optionally write the healed file
                if write_file and result.purified_code:
                    file_path.write_text(result.purified_code)
                    logger.info(f"[SHUDDHI] Wrote healed code to {file_path}")

            except Exception as e:
                # Don't fail the healing if KG update fails
                logger.warning(f"[SHUDDHI→KG] Failed to record healing: {e}")

        return result

    def heal_all_violations(self, dry_run: bool = True) -> List[ShuddhiResult]:
        """
        OUROBOROS: Heal all violations from Knowledge Graph that have remedies.

        This is the automatic healing loop - reads violations from KG,
        applies remedies where available, marks them as healed.

        Args:
            dry_run: If True, don't write files (just return diffs)

        Returns:
            List of ShuddhiResults for each attempted healing
        """
        results = []

        try:
            from vibe_core.di import ServiceRegistry
            from vibe_core.knowledge.graph import UnifiedKnowledgeGraph

            kg = ServiceRegistry.get(UnifiedKnowledgeGraph)
            if not kg:
                logger.warning("[SHUDDHI] Knowledge Graph not available")
                return results

            # Get unhealed violations
            violations = kg.get_violations(healed=False)
            logger.info(f"[SHUDDHI] Found {len(violations)} unhealed violations")

            for v in violations:
                rule_id = v.properties.get("rule_id", "")
                file_path_str = v.properties.get("file_path", "")

                # Check if we have a remedy
                if not self.can_heal(rule_id):
                    continue

                file_path = Path(file_path_str)
                if not file_path.exists():
                    continue

                # Attempt healing
                result = self.heal_and_record(
                    file_path=file_path,
                    rule_id=rule_id,
                    violation_id=v.id,
                    write_file=not dry_run,
                )
                results.append(result)

                if result.status == ShuddhiStatus.PURIFIED:
                    logger.info(f"[SHUDDHI] ✅ Healed {rule_id} in {file_path}")

        except Exception as e:
            logger.exception(f"[SHUDDHI] Error in heal_all_violations: {e}")

        return results
