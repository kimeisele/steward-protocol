"""
OPUS-212: ShuddhiEngine - The Surgical Orchestrator.

OPUS-307: No more hardcoded remedies!
Remedies are auto-discovered via RemedyLoader (VEDA-4 pattern).

KARMA: All healing operations emit Ledger events for audit trail.
YANTRA: duration_ms tracked for performance monitoring.
"""

import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Type

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
    # KARMA: Ledger Event Recording
    # =========================================================================

    def _record_healing_event(
        self,
        event_type: str,
        file_path: Path,
        rule_id: str,
        status: str,
        duration_ms: float,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        KARMA: Record healing operation to Ledger.

        This creates an immutable audit trail of all healing operations.
        """
        try:
            from vibe_core.di import ServiceRegistry
            from vibe_core.protocols.ledger import VibeLedger

            ledger = ServiceRegistry.get(VibeLedger)
            if ledger is None:
                logger.debug("[SHUDDHI] Ledger not available, skipping event recording")
                return

            event_details = {
                "file_path": str(file_path),
                "rule_id": rule_id,
                "status": status,
                "duration_ms": round(duration_ms, 2),
                "timestamp": datetime.now().isoformat(),
            }
            if details:
                event_details.update(details)

            ledger.record_event(
                event_type=event_type,
                agent_id="shuddhi",
                details=event_details,
            )
            logger.debug(f"[SHUDDHI] Recorded {event_type} to Ledger")
        except Exception as e:
            # DHARMA: Never crash on Ledger failure, but always log
            logger.warning(f"[SHUDDHI] Failed to record to Ledger: {e}")

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

        KARMA: Emits VIOLATION_HEALED ledger event for audit trail.
        YANTRA: Tracks duration_ms for performance monitoring.

        Args:
            file_path: Path to the file to heal
            rule_id: The rule ID to apply
            violation_id: Optional KG node ID to mark as healed
            write_file: If True, write the healed code to disk

        Returns:
            ShuddhiResult with healing outcome
        """
        start_time = time.perf_counter()

        # 1. Perform the healing
        result = self.purify(file_path, rule_id)

        # 2. Calculate duration
        duration_ms = (time.perf_counter() - start_time) * 1000

        # 3. If successful, update Knowledge Graph
        if result.status == ShuddhiStatus.PURIFIED:
            try:
                from vibe_core.di import ServiceRegistry
                from vibe_core.knowledge.graph import UnifiedKnowledgeGraph

                kg = ServiceRegistry.get(UnifiedKnowledgeGraph)
                if kg and violation_id:
                    kg.mark_violation_healed(violation_id, rule_id)
                    logger.info(f"[SHUDDHI→KG] Marked violation {violation_id} as healed")

                # 4. Optionally write the healed file
                if write_file and result.purified_code:
                    file_path.write_text(result.purified_code)
                    logger.info(f"[SHUDDHI] Wrote healed code to {file_path}")

            except Exception as e:
                # Don't fail the healing if KG update fails
                logger.warning(f"[SHUDDHI→KG] Failed to record healing: {e}")

        # KARMA: Record to Ledger
        self._record_healing_event(
            event_type="VIOLATION_HEALED",
            file_path=file_path,
            rule_id=rule_id,
            status=result.status.value,
            duration_ms=duration_ms,
            details={
                "violation_id": violation_id,
                "write_file": write_file,
                "message": result.message,
            },
        )

        # YANTRA: Warn on slow operations (>100ms per PROMPT.md)
        if duration_ms > 100:
            logger.warning(f"[SHUDDHI] Slow healing: {duration_ms:.1f}ms for {rule_id} in {file_path}")

        return result

    def heal_all_violations(self, dry_run: bool = True) -> List[ShuddhiResult]:
        """
        OUROBOROS: Heal all violations from Knowledge Graph that have remedies.

        This is the automatic healing loop - reads violations from KG,
        applies remedies where available, marks them as healed.

        KARMA: Emits HEALING_BATCH_COMPLETE ledger event for audit trail.
        YANTRA: Tracks duration_ms for performance monitoring.

        Args:
            dry_run: If True, don't write files (just return diffs)

        Returns:
            List of ShuddhiResults for each attempted healing
        """
        start_time = time.perf_counter()
        results = []
        healed_count = 0
        skipped_count = 0
        failed_count = 0

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

            healable_count = 0
            for v in violations:
                rule_id = v.properties.get("rule_id", "")
                file_path_str = v.properties.get("file_path", "")

                # Check if we have a remedy
                if not self.can_heal(rule_id):
                    continue

                file_path = Path(file_path_str)
                if not file_path.exists():
                    continue

                healable_count += 1

                # Attempt healing (heal_and_record already tracks its own duration)
                result = self.heal_and_record(
                    file_path=file_path,
                    rule_id=rule_id,
                    violation_id=v.id,
                    write_file=not dry_run,
                )
                results.append(result)

                if result.status == ShuddhiStatus.PURIFIED:
                    healed_count += 1
                    logger.info(f"[SHUDDHI] ✅ Healed {rule_id} in {file_path}")
                elif result.status == ShuddhiStatus.SKIPPED:
                    skipped_count += 1
                else:
                    failed_count += 1

        except Exception as e:
            logger.exception(f"[SHUDDHI] Error in heal_all_violations: {e}")

        # YANTRA: Calculate total batch duration
        duration_ms = (time.perf_counter() - start_time) * 1000

        # KARMA: Record batch completion to Ledger
        if results or healable_count > 0:
            self._record_batch_event(
                healed=healed_count,
                skipped=skipped_count,
                failed=failed_count,
                total_violations=len(violations) if "violations" in dir() else 0,
                healable=healable_count if "healable_count" in dir() else 0,
                duration_ms=duration_ms,
                dry_run=dry_run,
            )

        # YANTRA: Warn on slow batch operations (>100ms per PROMPT.md)
        if duration_ms > 100:
            logger.warning(f"[SHUDDHI] Slow batch healing: {duration_ms:.1f}ms for {len(results)} attempts")

        return results

    def _record_batch_event(
        self,
        healed: int,
        skipped: int,
        failed: int,
        total_violations: int,
        healable: int,
        duration_ms: float,
        dry_run: bool,
    ) -> None:
        """KARMA: Record batch healing completion to Ledger."""
        try:
            from vibe_core.di import ServiceRegistry
            from vibe_core.protocols.ledger import VibeLedger

            ledger = ServiceRegistry.get(VibeLedger)
            if ledger is None:
                return

            ledger.record_event(
                event_type="HEALING_BATCH_COMPLETE",
                agent_id="shuddhi",
                details={
                    "healed": healed,
                    "skipped": skipped,
                    "failed": failed,
                    "total_violations": total_violations,
                    "healable": healable,
                    "duration_ms": round(duration_ms, 2),
                    "dry_run": dry_run,
                    "timestamp": datetime.now().isoformat(),
                },
            )
            logger.info(
                f"[SHUDDHI] Batch complete: {healed} healed, {skipped} skipped, "
                f"{failed} failed ({duration_ms:.1f}ms, dry_run={dry_run})"
            )
        except Exception as e:
            logger.warning(f"[SHUDDHI] Failed to record batch event: {e}")
