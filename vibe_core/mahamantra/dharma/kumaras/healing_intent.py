"""
HEALING INTENT - Gate-Controlled Cellular Code Healing
======================================================

"cikitsitam auṣadhaṁ pathyam āhāraś ca yathā-vidhi"
"Treatment, medicine, diet — all according to proper method."
— Charaka Samhita

This module implements the cellular healing pipeline:

1. RECEIVE a MantraIntent(type=HEAL) targeting a Lotus address
2. RESOLVE the CSTFragment from the CellRouter
3. APPLY the CSTRemedy (CST transformation on the fragment)
4. VERIFY the healed code compiles
5. REGISTER the healed Cell in the CellRouter (new Lotus address)
6. MAYA-SYNC: Reconstruct and write the file

The healing flows through the Intent system, ensuring Gate control.
The Chamber is NOT the healer — it is the resonance space where
healed cells live and gain Prana after surgery.

PHASE 1: RAM healing + immediate Maya-Sync (no hot-swap).
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "kumaras"
__position__ = 5
__genesis__ = "0xfe9a70b8"  # GenesisByte: parampara % 37 == 0

import logging
from pathlib import Path
from typing import Dict, List, Optional, Type

import libcst as cst

from vibe_core.mahamantra.dharma.kapila.remedies.base import CSTRemedy, ShuddhiScopeError
from vibe_core.mahamantra.dharma.kapila.remedy_loader import get_remedy_loader
from vibe_core.mahamantra.dharma.kumaras.fragment import (
    CSTFragment,
    FileFragments,
)
from vibe_core.mahamantra.dharma.kumaras.fragment_parser import (
    parse_file_to_fragments,
)
from vibe_core.mahamantra.substrate.shuddhi import ShuddhiResult, ShuddhiStatus

logger = logging.getLogger("SHUDDHI.HEALING")


# =============================================================================
# HEALING RESULT - Extends ShuddhiResult with cellular context
# =============================================================================


class CellularHealingResult:
    """
    Result of a cellular healing operation.

    Wraps ShuddhiResult with fragment-level context:
    which fragment was healed, what its old/new Lotus address is,
    and whether Maya-Sync succeeded.
    """

    __slots__ = (
        "shuddhi_result",
        "fragment",
        "healed_fragment",
        "old_lotus_address",
        "new_lotus_address",
        "maya_synced",
    )

    def __init__(
        self,
        shuddhi_result: ShuddhiResult,
        fragment: Optional[CSTFragment] = None,
        healed_fragment: Optional[CSTFragment] = None,
        old_lotus_address: int = 0,
        new_lotus_address: int = 0,
        maya_synced: bool = False,
    ) -> None:
        self.shuddhi_result = shuddhi_result
        self.fragment = fragment
        self.healed_fragment = healed_fragment
        self.old_lotus_address = old_lotus_address
        self.new_lotus_address = new_lotus_address
        self.maya_synced = maya_synced

    @property
    def success(self) -> bool:
        return self.shuddhi_result.success

    @property
    def status(self) -> ShuddhiStatus:
        return self.shuddhi_result.status


# =============================================================================
# CELLULAR HEALER - The surgical pipeline
# =============================================================================


class CellularHealer:
    """
    Performs atomic, fragment-level code healing.

    This is the EXECUTE-Gate logic for healing intents.
    It does NOT touch the Chamber — that happens after,
    when the healed cell is given Prana through dance().

    Pipeline:
        1. Parse file → fragments → cells (if not already registered)
        2. Find the sick fragment (by Lotus address or qualified name)
        3. Apply CSTRemedy to the fragment's CST
        4. Verify the healed code compiles
        5. Create new CSTFragment with healed source
        6. Register healed cell in CellRouter
        7. Maya-Sync: reconstruct file and write to disk

    WATERTIGHT: No Any types. All operations verified.
    """

    def __init__(self) -> None:
        self._remedies: Dict[str, Type[CSTRemedy]] = {}
        self._file_fragments_cache: Dict[Path, FileFragments] = {}
        self._discover_remedies()

    def _discover_remedies(self) -> None:
        """Auto-discover remedies via RemedyLoader (VEDA-4 pattern)."""
        loader = get_remedy_loader()
        discovered = loader.discover_and_load()
        for rule_id, remedy_cls in discovered.items():
            self._remedies[rule_id] = remedy_cls
        logger.info(f"[HEALER] Discovered {len(self._remedies)} remedies")

    def can_heal(self, rule_id: str) -> bool:
        """Check if a remedy exists for this rule."""
        return rule_id in self._remedies

    def list_remedies(self) -> List[str]:
        """List all available remedy rule_ids."""
        return list(self._remedies.keys())

    # =========================================================================
    # CORE: Heal a single fragment
    # =========================================================================

    def heal_fragment(
        self,
        fragment: CSTFragment,
        rule_id: str,
        dry_run: bool = False,
    ) -> CellularHealingResult:
        """
        Heal a single CSTFragment using the appropriate CSTRemedy.

        This is the atomic healing operation — one fragment, one rule.

        Args:
            fragment: The sick fragment to heal.
            rule_id: Which violation to heal.
            dry_run: If True, don't write to disk or register new cell.

        Returns:
            CellularHealingResult with full context.
        """
        # 1. Find the remedy
        remedy_cls = self._remedies.get(rule_id)
        if remedy_cls is None:
            return CellularHealingResult(
                shuddhi_result=ShuddhiResult(
                    status=ShuddhiStatus.FAILED,
                    file_path=fragment.file_path,
                    rule_id=rule_id,
                    message=f"No remedy registered for rule '{rule_id}'",
                ),
                fragment=fragment,
            )

        # 2. Parse the fragment's CST
        try:
            source_tree = cst.parse_module(fragment.source_code)
        except cst.ParserSyntaxError as e:
            return CellularHealingResult(
                shuddhi_result=ShuddhiResult(
                    status=ShuddhiStatus.FAILED,
                    file_path=fragment.file_path,
                    rule_id=rule_id,
                    message=f"Cannot parse fragment '{fragment.display_name}': {e}",
                ),
                fragment=fragment,
            )

        # 3. Apply the remedy (CST transformation)
        transformer = remedy_cls()
        try:
            healed_tree = source_tree.visit(transformer)
        except ShuddhiScopeError as e:
            return CellularHealingResult(
                shuddhi_result=ShuddhiResult(
                    status=ShuddhiStatus.OUT_OF_SCOPE,
                    file_path=fragment.file_path,
                    rule_id=rule_id,
                    message=f"Scope error in '{fragment.display_name}': {e}",
                ),
                fragment=fragment,
            )
        except Exception as e:
            return CellularHealingResult(
                shuddhi_result=ShuddhiResult(
                    status=ShuddhiStatus.FAILED,
                    file_path=fragment.file_path,
                    rule_id=rule_id,
                    message=f"Remedy error in '{fragment.display_name}': {e}",
                ),
                fragment=fragment,
            )

        # 4. Check if anything changed
        new_code = healed_tree.code
        if not transformer.applied:
            return CellularHealingResult(
                shuddhi_result=ShuddhiResult(
                    status=ShuddhiStatus.SKIPPED,
                    file_path=fragment.file_path,
                    rule_id=rule_id,
                    message=f"No violation found in '{fragment.display_name}'",
                ),
                fragment=fragment,
            )

        # 5. Verify the healed code compiles
        try:
            compile(new_code, f"<healed:{fragment.display_name}>", "exec")
        except SyntaxError as e:
            return CellularHealingResult(
                shuddhi_result=ShuddhiResult(
                    status=ShuddhiStatus.FAILED,
                    file_path=fragment.file_path,
                    rule_id=rule_id,
                    message=f"Healed code fails compilation: {e}",
                ),
                fragment=fragment,
            )

        # 6. Create healed fragment
        healed_fragment = fragment.with_new_source(new_code)

        # 7. Compute Lotus addresses
        old_address = self._get_lotus_address(fragment.source_code)
        new_address = self._get_lotus_address(new_code)

        # 8. Register healed cell (unless dry_run)
        if not dry_run:
            self._register_healed_cell(healed_fragment, new_address)

        # 9. Build result
        diff = transformer.get_diff(fragment.source_code, new_code)

        result = CellularHealingResult(
            shuddhi_result=ShuddhiResult(
                status=ShuddhiStatus.PURIFIED,
                file_path=fragment.file_path,
                rule_id=rule_id,
                message=f"Fragment '{fragment.display_name}' healed.",
                diff=diff,
                purified_code=new_code,
            ),
            fragment=fragment,
            healed_fragment=healed_fragment,
            old_lotus_address=old_address,
            new_lotus_address=new_address,
            maya_synced=False,
        )

        logger.info(
            f"[HEALER] Healed {fragment.display_name} "
            f"(0x{old_address:08X} → 0x{new_address:08X}) "
            f"rule={rule_id}"
        )

        return result

    # =========================================================================
    # FILE-LEVEL: Heal all violations in a file
    # =========================================================================

    def heal_file(
        self,
        file_path: Path,
        rule_id: str,
        dry_run: bool = False,
        governed: bool = False,
    ) -> List[CellularHealingResult]:
        """
        Heal all fragments in a file that match a given rule.

        1. Parse file into fragments
        2. Apply remedy to each fragment independently
        3. Maya-Sync: reconstruct file from healed fragments

        Args:
            file_path: Path to the Python file.
            rule_id: Which violation to heal.
            dry_run: If True, don't write to disk.
            governed: If True, Maya-Sync goes through Srivasa gate
                      (EnforceGateProvider.write_source) with RAJAS Guna.
                      If False, raw Path.write_text (legacy path).

        Returns:
            List of CellularHealingResult (one per fragment that was touched).
        """
        # Parse file into fragments (cached)
        file_frags = self._get_file_fragments(file_path)

        results: List[CellularHealingResult] = []
        any_healed = False

        for frag in file_frags.fragments:
            result = self.heal_fragment(frag, rule_id, dry_run=True)
            results.append(result)

            if result.status == ShuddhiStatus.PURIFIED and result.healed_fragment:
                any_healed = True
                # Replace fragment in our working copy
                file_frags = file_frags.replace_fragment(frag, result.healed_fragment)

        # Maya-Sync: write reconstructed file
        if any_healed and not dry_run:
            self._maya_sync(file_frags, governed=governed)
            for r in results:
                if r.status == ShuddhiStatus.PURIFIED:
                    r.maya_synced = True

            # Invalidate cache (file changed)
            self._file_fragments_cache.pop(file_path, None)

        return results

    # =========================================================================
    # MAYA-SYNC: Reconstruct file from fragments and write to disk
    # =========================================================================

    def _maya_sync(self, file_frags: FileFragments, governed: bool = False) -> bool:
        """
        Reconstruct the full file from its fragments and write to disk.

        This is the write-behind to Maya (filesystem).
        The Inner World (CellRouter) already has the healed cells.

        Args:
            file_frags: FileFragments with healed fragments.
            governed: If True, write through Srivasa gate (RAJAS-authorized).
                      If False, raw Path.write_text (legacy path).

        Returns:
            True if write succeeded.
        """
        try:
            reconstructed = file_frags.reconstruct()

            # Verify the full reconstructed file compiles
            compile(reconstructed, str(file_frags.file_path), "exec")

            if governed:
                # ── GOVERNED PATH: Srivasa gate authorizes the write ──
                from vibe_core.mahamantra.substrate.gate_providers import get_sync_gate
                from vibe_core.mahamantra.substrate.guna import Guna

                gate = get_sync_gate()
                result = gate.write_source(
                    file_path=file_frags.file_path,
                    content=reconstructed,
                    actor="shuddhi_healer",
                    guna=Guna.RAJAS,  # Healing commit = act of creation
                )
                if not result["success"]:
                    logger.error(
                        f"[MAYA-SYNC] Srivasa gate DENIED write to "
                        f"{file_frags.file_path}: {result['reason']}"
                    )
                    return False
            else:
                # ── LEGACY PATH: Raw write (backward compat) ──
                file_frags.file_path.write_text(reconstructed, encoding="utf-8")

            logger.info(
                f"[MAYA-SYNC] Written {file_frags.file_path.name} "
                f"({file_frags.count} fragments)"
                f"{' [GOVERNED]' if governed else ''}"
            )
            return True

        except SyntaxError as e:
            logger.error(
                f"[MAYA-SYNC] Reconstructed file fails compilation: "
                f"{file_frags.file_path}: {e}"
            )
            return False
        except OSError as e:
            logger.error(
                f"[MAYA-SYNC] Cannot write {file_frags.file_path}: {e}"
            )
            return False

    # =========================================================================
    # HELPERS
    # =========================================================================

    def _get_file_fragments(self, file_path: Path) -> FileFragments:
        """Get or parse file fragments (cached)."""
        if file_path not in self._file_fragments_cache:
            self._file_fragments_cache[file_path] = parse_file_to_fragments(file_path)
        return self._file_fragments_cache[file_path]

    def _get_lotus_address(self, source_code: str) -> int:
        """Compute Lotus address for source code via MahaCompression."""
        try:
            from vibe_core.mahamantra.adapters.compression import MahaCompression
            compression = MahaCompression()
            result = compression.compress(source_code)
            return result.seed
        except Exception:
            return 0

    def _register_healed_cell(self, fragment: CSTFragment, address: int) -> None:
        """Register a healed fragment as a new MahaCellUnified in the CellRouter."""
        try:
            from vibe_core.mahamantra.substrate.cell import MahaCellUnified
            cell = MahaCellUnified.from_content(
                content=fragment.source_code,
                initial_state=fragment,
                register=True,
            )
            logger.debug(
                f"[HEALER] Registered healed cell "
                f"'{fragment.display_name}' @ 0x{cell.header.sravanam:08X}"
            )
        except Exception as e:
            logger.warning(f"[HEALER] Failed to register healed cell: {e}")

    def _emit_vibration(self, result: CellularHealingResult) -> None:
        """Emit healing vibration to Mahamantra (Akash)."""
        try:
            from vibe_core.mahamantra import mahamantra
            if hasattr(mahamantra, "akash"):
                akash = mahamantra.akash
                if hasattr(akash, "record"):
                    akash.record(
                        event="shuddhi_cellular",
                        data={
                            "status": result.status.value,
                            "fragment": result.fragment.display_name if result.fragment else "unknown",
                            "rule_id": result.shuddhi_result.rule_id,
                            "old_address": f"0x{result.old_lotus_address:08X}",
                            "new_address": f"0x{result.new_lotus_address:08X}",
                            "maya_synced": result.maya_synced,
                        },
                    )
        except Exception:
            pass  # Vibration is best-effort, never blocks healing


# =============================================================================
# SINGLETON
# =============================================================================

_healer: Optional[CellularHealer] = None


def get_cellular_healer() -> CellularHealer:
    """Get the singleton CellularHealer instance."""
    global _healer
    if _healer is None:
        _healer = CellularHealer()
    return _healer


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "CellularHealingResult",
    "CellularHealer",
    "get_cellular_healer",
]
