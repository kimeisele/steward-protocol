"""
OPUS-212: ShuddhiEngine - The Surgical Orchestrator.

OPUS-307: No more hardcoded remedies!
Remedies are auto-discovered via RemedyLoader (VEDA-4 pattern).

CELLULAR HEALING (OPUS-400):
    Code fragments are Cells. Healing is atomic, per-fragment.
    The CellularHealer performs CST surgery on individual fragments.
    The Chamber gives healed cells Prana (resonance after surgery).
    Maya-Sync writes the reconstructed file to disk.

    File → Fragments → Cells → CellularHealer → Maya-Sync

VIBRATIONAL INTEGRATION (Top-Down Architecture):
    Mahamantra is the SINGULARITY - all intelligence flows from there.
    ShuddhiEngine EMITS vibrations to Mahamantra after each operation.
    Remedies are DUMB transformers - no cognition in leaves!
    Akash accumulates ALL operations - nothing is silent.

    Engine.purify() → result → _emit_vibration() → mahamantra → Akash
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "kapila"
__position__ = 6
__genesis__ = "0xef438df2"  # GenesisByte: parampara % 37 == 0

import logging
from pathlib import Path
from typing import Dict, List, Optional, Type

import libcst as cst

from vibe_core.mahamantra.substrate.shuddhi import ShuddhiProtocol, ShuddhiResult, ShuddhiStatus
from vibe_core.mahamantra.dharma.kapila.remedies.base import CSTRemedy, ShuddhiScopeError
from vibe_core.mahamantra.dharma.kapila.remedy_loader import get_remedy_loader

logger = logging.getLogger("SHUDDHI")


class ShuddhiEngine(ShuddhiProtocol):
    """
    Implementation of the Shuddhi self-healing service.

    This engine manages the lifecycle of a healing operation:
    Parse -> Transform -> Verify -> Result.

    OPUS-307: Remedies are auto-discovered from vibe_core/shuddhi/remedies/
    No hardcoded imports - scales to hundreds of remedies.

    VIBRATIONAL COMPUTING:
        Every operation VIBRATES through Mahamantra.
        Nothing is silent. Akash accumulates all.
    """

    def __init__(self):
        self._remedies: Dict[str, Type[CSTRemedy]] = {}
        self._loader = get_remedy_loader()
        self._discover_remedies()
        self._mahamantra = None  # Lazy-loaded
        self._sravanam_wired = False
        self._ensure_sravanam_wired()

    def _get_mahamantra(self):
        """Lazy-load Mahamantra singleton for vibration emission."""
        if self._mahamantra is None:
            try:
                from vibe_core.mahamantra import mahamantra
                self._mahamantra = mahamantra
            except ImportError:
                logger.debug("[SHUDDHI] Mahamantra not available for vibration")
        return self._mahamantra

    def _emit_vibration(self, result: ShuddhiResult) -> None:
        """
        VIBRATIONAL COMPUTING: Emit operation result to Mahamantra.

        Every Shuddhi operation vibrates:
            - PURIFIED: Healing succeeded - positive resonance
            - SKIPPED: No violation found - neutral
            - FAILED: Error occurred - needs attention
            - OUT_OF_SCOPE: Beyond remedy capability

        The vibration is computed from:
            rule_id + status + file_path → seed → attractor → Akash

        This is the Shabda Brahma principle:
            "In the beginning was the Word" - all operations are vibrations.
        """
        maha = self._get_mahamantra()
        if maha is None:
            return

        # Construct vibration message from operation
        vibration_msg = f"shuddhi:{result.rule_id}:{result.status.name}:{result.file_path}"

        try:
            vibration = maha.vibrate(vibration_msg)

            logger.debug(
                f"[SHUDDHI→AKASH] {result.rule_id} {result.status.name} "
                f"→ attractor={vibration['attractor']} resonance={vibration['resonance']:.3f}"
            )
        except Exception as e:
            # Don't fail operations if vibration fails
            logger.debug(f"[SHUDDHI] Vibration emission failed: {e}")

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
        """
        Heals a specific structural violation in a file.

        VIBRATIONAL: Every outcome vibrates to Akash.
        """
        if rule_id not in self._remedies:
            result = ShuddhiResult(
                status=ShuddhiStatus.FAILED,
                file_path=file_path,
                rule_id=rule_id,
                message=f"No remedy registered for rule '{rule_id}'",
            )
            self._emit_vibration(result)
            return result

        if not file_path.exists():
            result = ShuddhiResult(
                status=ShuddhiStatus.FAILED,
                file_path=file_path,
                rule_id=rule_id,
                message="File not found",
            )
            self._emit_vibration(result)
            return result

        try:
            # 1. Read and Parse
            source_code = file_path.read_text()
            module = cst.parse_module(source_code)

            # 2. Transform (with MetadataWrapper for position tracking)
            remedy_class = self._remedies[rule_id]
            transformer = remedy_class()

            # PANCHA TATTVA: Pass file_path to remedies that need it (e.g., BrokenGenesisRemedy)
            if hasattr(transformer, "set_file_path"):
                transformer.set_file_path(str(file_path))

            try:
                # Use MetadataWrapper if remedy needs position metadata
                # This enables get_metadata() calls in remedies
                wrapper = cst.MetadataWrapper(module)
                modified_module = wrapper.visit(transformer)
            except ShuddhiScopeError as e:
                result = ShuddhiResult(
                    status=ShuddhiStatus.OUT_OF_SCOPE,
                    file_path=file_path,
                    rule_id=rule_id,
                    message=str(e),
                )
                self._emit_vibration(result)
                return result

            # 3. Check if any changes were made
            if not transformer.applied:
                result = ShuddhiResult(
                    status=ShuddhiStatus.SKIPPED,
                    file_path=file_path,
                    rule_id=rule_id,
                    message="No violations found in the file structure.",
                )
                self._emit_vibration(result)
                return result

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
            result = ShuddhiResult(
                status=ShuddhiStatus.PURIFIED,
                file_path=file_path,
                rule_id=rule_id,
                message="Surgery successful.",
                diff=transformer.get_diff(source_code, new_code),
                purified_code=new_code,
            )
            # VIBRATE: Emit to Akash
            self._emit_vibration(result)
            return result

        except Exception as e:
            logger.exception(f"[SHUDDHI] Unexpected error purifying {file_path}: {e}")
            result = ShuddhiResult(
                status=ShuddhiStatus.FAILED,
                file_path=file_path,
                rule_id=rule_id,
                message=f"Internal error: {str(e)}",
            )
            # VIBRATE: Even failures vibrate!
            self._emit_vibration(result)
            return result

    def scan_file(self, file_path: Path, rule_ids: Optional[List[str]] = None) -> List[ShuddhiResult]:
        """
        Scan a single file with multiple remedies. Parses the file ONCE.

        This is the O(N) path: one parse, M remedy passes on the same CST.
        Each remedy gets its own transformer instance but shares the parse cost.

        Args:
            file_path: Path to the file to scan
            rule_ids: Optional list of rule_ids to check. None = all registered.

        Returns:
            List of ShuddhiResults (only PURIFIED results included).
        """
        results: List[ShuddhiResult] = []

        if not file_path.exists():
            return results

        targets = rule_ids if rule_ids else list(self._remedies.keys())

        try:
            source_code = file_path.read_text()
            module = cst.parse_module(source_code)
        except Exception as e:
            logger.warning("[SHUDDHI] Failed to parse %s: %s", file_path, e)
            return results

        for rule_id in targets:
            if rule_id not in self._remedies:
                continue

            remedy_class = self._remedies[rule_id]
            transformer = remedy_class()

            if hasattr(transformer, "set_file_path"):
                transformer.set_file_path(str(file_path))

            try:
                wrapper = cst.MetadataWrapper(module)
                modified_module = wrapper.visit(transformer)
            except ShuddhiScopeError:
                continue
            except Exception as e:
                logger.warning("[SHUDDHI] Remedy %s failed on %s: %s", rule_id, file_path, e)
                continue

            if not transformer.applied:
                continue

            new_code = modified_module.code

            try:
                compile(new_code, str(file_path), "exec")
            except SyntaxError as e:
                results.append(ShuddhiResult(
                    status=ShuddhiStatus.FAILED,
                    file_path=file_path,
                    rule_id=rule_id,
                    message=f"Transformation produced invalid syntax: {e}",
                ))
                continue

            result = ShuddhiResult(
                status=ShuddhiStatus.PURIFIED,
                file_path=file_path,
                rule_id=rule_id,
                message="Surgery successful.",
                diff=transformer.get_diff(source_code, new_code),
                purified_code=new_code,
            )
            self._emit_vibration(result)
            results.append(result)

        return results

    def scan_cell(
        self,
        source_code: str,
        rule_id: str,
        file_path: Optional[Path] = None,
    ) -> Optional[ShuddhiResult]:
        """
        SRAVANAM: Scan ONE source fragment with ONE rule.

        This is the ATOMIC scan unit — no file I/O, no bulk.
        The source_code is already in RAM (from a CSTFragment or Cell payload).

        Args:
            source_code: Python source code string (from fragment/cell).
            rule_id: Single remedy rule_id to check.
            file_path: Optional path for context (not read from disk).

        Returns:
            ShuddhiResult if violation found (PURIFIED), None otherwise.
        """
        if rule_id not in self._remedies:
            return None

        try:
            module = cst.parse_module(source_code)
        except Exception:
            return None

        remedy_class = self._remedies[rule_id]
        transformer = remedy_class()

        if hasattr(transformer, "set_file_path") and file_path:
            transformer.set_file_path(str(file_path))

        try:
            wrapper = cst.MetadataWrapper(module)
            modified_module = wrapper.visit(transformer)
        except ShuddhiScopeError:
            return None
        except Exception:
            return None

        if not transformer.applied:
            return None

        new_code = modified_module.code

        try:
            compile(new_code, str(file_path or "<cell>"), "exec")
        except SyntaxError:
            return None

        result = ShuddhiResult(
            status=ShuddhiStatus.PURIFIED,
            file_path=file_path or Path("<cell>"),
            rule_id=rule_id,
            message="Surgery successful.",
            diff=transformer.get_diff(source_code, new_code),
            purified_code=new_code,
        )
        self._emit_vibration(result)
        return result

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

        # 2. If successful, update Knowledge Graph via PROTOCOL
        if result.status == ShuddhiStatus.PURIFIED:
            try:
                from vibe_core.di import ServiceRegistry
                from vibe_core.protocols.mahajanas.prithu.knowledge import KnowledgeGraphProtocol

                # Use protocol, not implementation
                kg = ServiceRegistry.get(KnowledgeGraphProtocol)
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

        PANCHA TATTVA GATE MAPPING (OPUS-500):
            Each violation is wrapped in a MantraIntent(type=HEAL) and
            routed through the HealingIntentResolver, which fires all 5
            Tattva Gates:
                PARSE → VALIDATE → EXECUTE → RESULT → SYNC

            2-Phase Guna Model:
                Gates 0-3: SATTVA (analysis in RAM, no side effects)
                Gate 4: RAJAS (authorized commit via Srivasa gate)

            There is NO ungoverned path. If the resolver cannot wire,
            healing FAILS. No bypass. No legacy fallback.

        Args:
            dry_run: If True, don't write files (just return diffs)

        Returns:
            List of ShuddhiResults for each attempted healing

        Raises:
            RuntimeError: If HealingIntentResolver cannot be wired.
        """
        results: List[ShuddhiResult] = []

        # Wire the healing resolver — HARD FAIL if impossible
        self._ensure_resolver_wired()

        try:
            from vibe_core.di import ServiceRegistry
            from vibe_core.protocols.mahajanas.prithu.knowledge import KnowledgeGraphProtocol

            kg = ServiceRegistry.get(KnowledgeGraphProtocol)
            if not kg:
                logger.warning("[SHUDDHI] KnowledgeGraphProtocol not available")
                return results

            violations = kg.get_violations(healed=False)
            logger.info(f"[SHUDDHI] Found {len(violations)} unhealed violations")

            from collections import defaultdict
            by_file: Dict[str, List[tuple]] = defaultdict(list)
            for v in violations:
                rule_id = v.properties.get("rule_id", "")
                file_path_str = v.properties.get("file", "")
                if isinstance(rule_id, str) and isinstance(file_path_str, str):
                    by_file[file_path_str].append((rule_id, v.id))

            # ALL healing goes through gates. No other path exists.
            self._heal_through_gates(by_file, dry_run, results, kg)

        except Exception as e:
            logger.exception(f"[SHUDDHI] Error in heal_all_violations: {e}")

        return results

    def _ensure_resolver_wired(self) -> None:
        """
        Wire the HealingIntentResolver. HARD FAIL if impossible.

        There is no fallback. If this fails, healing cannot proceed.
        An ungoverned healing path is an architectural violation.
        """
        from vibe_core.mahamantra.dharma.kumaras.healing_resolver import (
            wire_healing_resolver,
        )
        if not wire_healing_resolver():
            raise RuntimeError(
                "FATAL: HealingIntentResolver could not be wired to MantraKernel. "
                "Healing CANNOT proceed without gate governance. "
                "No ungoverned path exists by design."
            )

    def _ensure_sravanam_wired(self) -> None:
        """
        Wire the SravanamListener. BEST-EFFORT — scanning is optional.

        Unlike healing (which hard-fails), scanning is advisory.
        If it can't wire, we log and continue.
        """
        if self._sravanam_wired:
            return
        try:
            from vibe_core.mahamantra.dharma.kumaras.sravanam import wire_sravanam
            wire_sravanam()
            self._sravanam_wired = True
        except Exception as exc:
            logger.debug("[SHUDDHI] Sravanam wiring skipped: %s", exc)

    def _heal_through_gates(
        self,
        by_file: Dict[str, List[tuple]],
        dry_run: bool,
        results: List[ShuddhiResult],
        kg: object,
    ) -> None:
        """
        Heal via MantraIntent → HealingIntentResolver → 5-gate pipeline.

        This is the ONLY healing path. There is no fallback.
        """
        from vibe_core.mahamantra.kernel.intent import (
            MantraIntent,
            IntentType,
            IntentPriority,
            get_kernel,
        )

        kernel = get_kernel()

        for file_path_str, violation_list in by_file.items():
            file_path = Path(file_path_str)
            if not file_path.exists():
                continue

            for rule_id, violation_id in violation_list:
                intent = MantraIntent(
                    type=IntentType.HEAL,
                    target=file_path_str,
                    params={
                        "file_path": file_path_str,
                        "rule_id": rule_id,
                        "dry_run": dry_run,
                        "violation_id": violation_id,
                    },
                    priority=IntentPriority.NORMAL,
                    requester="shuddhi_engine",
                )

                intent_result = kernel.resolve(intent)

                if intent_result.is_success and intent_result.value:
                    for cr in intent_result.value:
                        shuddhi_result = cr.shuddhi_result
                        results.append(shuddhi_result)
                        self._emit_vibration(shuddhi_result)

                        if shuddhi_result.status == ShuddhiStatus.PURIFIED:
                            try:
                                if kg and violation_id:
                                    kg.mark_violation_healed(violation_id, rule_id)
                                    logger.info(
                                        f"[SHUDDHI] Gate-healed: {rule_id} in "
                                        f"{cr.fragment.display_name if cr.fragment else file_path}"
                                    )
                            except Exception as e:
                                logger.warning(f"[SHUDDHI->KG] Failed to record: {e}")

                elif intent_result.error:
                    logger.warning(
                        "[SHUDDHI] Intent resolution failed: %s", intent_result.error
                    )

