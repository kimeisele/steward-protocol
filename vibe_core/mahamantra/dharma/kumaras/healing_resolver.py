"""
HEALING RESOLVER — The 5-Gate Healing Pipeline
================================================

"cikitsitam auṣadhaṁ pathyam āhāraś ca yathā-vidhi"
"Treatment, medicine, diet — all according to proper method."
— Charaka Samhita

This module implements the IntentResolver for healing intents.
Healing flows through ALL 5 Tattva Gates, ensuring governance:

    PHASE 1 (SATTVA — RAM analysis, no side effects):
        Gate 0: CHAITANYA (PARSE)    → Validate intent, parse file
        Gate 1: NITYANANDA (VALIDATE) → Verify remedy exists
        Gate 2: ADVAITA (EXECUTE)    → Apply CSTRemedy in RAM
        Gate 3: GADADHARA (RESULT)   → Build healing result

    PHASE 2 (RAJAS — authorized commit):
        Gate 4: SRIVASA (SYNC)       → Authorize Maya-Sync via write_source()

2-PHASE GUNA MODEL:
    The healing intent maps to TYPE_CHECK (SATTVA) for analysis.
    But the disk write is RAJAS (act of creation).
    Gates 0-3 fire with SATTVA context.
    Gate 4 fires with RAJAS context (Guna escalation).

    This resolves the paradox:
        Observation = SATTVA (safe, no locking)
        Commit = RAJAS (transactional, requires authorization)
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "kumaras"
__position__ = 5
__genesis__ = "0xfe9a70b8"

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Dict

if TYPE_CHECKING:
    from vibe_core.mahamantra.kernel.intent import MantraIntent, IntentResult
    from vibe_core.mahamantra.substrate.lotus_core import MahamantraLotus
    from vibe_core.mahamantra.substrate.pancha_tattva import TattvaGate


from vibe_core.mahamantra.dharma.kumaras.healing_intent import (
    get_cellular_healer,
)
from vibe_core.mahamantra.substrate.shuddhi import ShuddhiStatus

logger = logging.getLogger("SHUDDHI.RESOLVER")


# =============================================================================
# HEALING INTENT RESOLVER
# =============================================================================


class HealingIntentResolver:
    """
    IntentResolver for IntentType.HEAL.

    Routes healing through the Pancha Tattva 5-gate pipeline:
        PARSE → VALIDATE → EXECUTE → RESULT → SYNC

    2-Phase Guna:
        Gates 0-3: SATTVA (analysis in RAM)
        Gate 4: RAJAS (authorized commit to Maya)

    Registered in MantraKernel at boot via wire_healing_resolver().
    """

    def can_resolve(self, intent: "MantraIntent") -> bool:
        """Can resolve IntentType.HEAL."""
        from vibe_core.mahamantra.kernel.intent import IntentType
        return intent.type == IntentType.HEAL

    # =========================================================================
    # RESOLVE STEPS — Atomic, granular, individually callable
    # PHASE 1 (SATTVA): validate → analyze → surgery
    # PHASE 2 (RAJAS): commit
    # =========================================================================

    def _resolve_validate(self, intent: "MantraIntent") -> tuple:
        """Resolve Step 1: Extract + validate params. Returns (file_path, rule_id, dry_run) or IntentResult."""
        from vibe_core.mahamantra.kernel.intent import IntentResult, IntentStatus
        from vibe_core.mahamantra import Mahajana

        file_path_str = intent.params.get("file_path", "")
        rule_id = intent.params.get("rule_id", "")
        dry_run = bool(intent.params.get("dry_run", False))

        if not file_path_str or not rule_id:
            return IntentResult(intent=intent, status=IntentStatus.FAILED,
                                error="HEAL intent requires 'file_path' and 'rule_id' params",
                                resolved_by=Mahajana.SHAMBHU)

        file_path = Path(str(file_path_str))
        if not file_path.exists():
            return IntentResult(intent=intent, status=IntentStatus.FAILED,
                                error=f"File not found: {file_path}", resolved_by=Mahajana.SHAMBHU)

        healer = get_cellular_healer()
        if not healer.can_heal(str(rule_id)):
            return IntentResult(intent=intent, status=IntentStatus.FAILED,
                                error=f"No remedy registered for rule '{rule_id}'",
                                resolved_by=Mahajana.SHAMBHU)

        return file_path, rule_id, dry_run

    def _resolve_sattva(self, intent: "MantraIntent", file_path: Path, rule_id: str) -> tuple:
        """Resolve Step 2: SATTVA phase — Gates 0-3, CST surgery in RAM.
        Returns (cell_results, purified, seed, attractor) or IntentResult on failure."""
        from vibe_core.mahamantra.kernel.intent import IntentResult, IntentStatus
        from vibe_core.mahamantra.substrate.pancha_tattva import TattvaGate
        from vibe_core.mahamantra import Mahajana

        lotus = self._get_lotus()
        healer = get_cellular_healer()

        self._fire_gate_safe(lotus, TattvaGate.PARSE, {
            "input_data": str(file_path), "intent_type": "HEAL", "rule_id": rule_id})

        seed = self._compute_seed(str(file_path) + str(rule_id))
        self._fire_gate_safe(lotus, TattvaGate.VALIDATE, {
            "seed": seed, "rule_id": rule_id, "file_path": str(file_path), "remedy_available": True})

        attractor = seed % 108
        self._fire_gate_safe(lotus, TattvaGate.EXECUTE, {
            "seed": seed, "attractor": attractor, "operation": "cellular_healing", "rule_id": rule_id})

        try:
            cell_results = healer.heal_file(file_path=file_path, rule_id=str(rule_id),
                                            dry_run=True, governed=False)
        except Exception as exc:
            logger.error("[RESOLVER] CST surgery failed: %s", exc)
            return IntentResult(intent=intent, status=IntentStatus.FAILED,
                                error=f"CST surgery failed: {exc}", resolved_by=Mahajana.SHAMBHU)

        purified = [r for r in cell_results if r.status == ShuddhiStatus.PURIFIED]
        self._fire_gate_safe(lotus, TattvaGate.RESULT, {
            "attractor": attractor, "fragments_total": len(cell_results),
            "fragments_purified": len(purified), "dry_run": False})

        return cell_results, purified, seed, attractor

    def _resolve_rajas(self, intent: "MantraIntent", file_path: Path, rule_id: str,
                       seed: int, attractor: int, dry_run: bool, cell_results: list) -> "IntentResult":
        """Resolve Step 3: RAJAS phase — Gate 4 SYNC, governed write.
        Returns IntentResult (dry_run or committed)."""
        from vibe_core.mahamantra.kernel.intent import IntentResult, IntentStatus
        from vibe_core.mahamantra.substrate.pancha_tattva import TattvaGate
        from vibe_core.mahamantra.substrate.guna import Guna
        from vibe_core.mahamantra import Mahajana

        lotus = self._get_lotus()

        if dry_run:
            self._fire_gate_safe(lotus, TattvaGate.SYNC, {
                "position": attractor % 16, "seed": seed, "attractor": attractor,
                "opcode": None, "guna": Guna.SATTVA})
            logger.info("[RESOLVER] DRY RUN: %d fragments would be healed in %s",
                        len(cell_results), file_path.name)
            return IntentResult(intent=intent, status=IntentStatus.RESOLVED, value=cell_results,
                                resolved_by=Mahajana.SHAMBHU, parampara_verified=intent.is_connected)

        from vibe_core.mahamantra.substrate.opcode import MantraOpCode
        self._fire_gate_safe(lotus, TattvaGate.SYNC, {
            "position": attractor % 16, "seed": seed, "attractor": attractor,
            "opcode": MantraOpCode.EXEC_OP, "guna": Guna.RAJAS})

        try:
            governed_results = get_cellular_healer().heal_file(
                file_path=file_path, rule_id=str(rule_id), dry_run=False, governed=True)
        except Exception as exc:
            logger.error("[RESOLVER] Governed Maya-Sync failed: %s", exc)
            return IntentResult(intent=intent, status=IntentStatus.FAILED,
                                error=f"Maya-Sync failed: {exc}", resolved_by=Mahajana.SHAMBHU)

        actual_purified = [r for r in governed_results if r.status == ShuddhiStatus.PURIFIED and r.maya_synced]
        logger.info("[RESOLVER] ✅ Healed %d/%d fragments in %s through 5-gate pipeline",
                    len(actual_purified), len(governed_results), file_path.name)

        return IntentResult(intent=intent, status=IntentStatus.RESOLVED, value=governed_results,
                            resolved_by=Mahajana.SHAMBHU, parampara_verified=intent.is_connected)

    def resolve(self, intent: "MantraIntent") -> "IntentResult":
        """Resolve a HEAL intent through the 5-gate pipeline. Chains _resolve_* steps."""
        from vibe_core.mahamantra.kernel.intent import IntentResult, IntentStatus
        from vibe_core.mahamantra import Mahajana

        validated = self._resolve_validate(intent)
        if isinstance(validated, IntentResult):
            return validated
        file_path, rule_id, dry_run = validated

        analyzed = self._resolve_sattva(intent, file_path, rule_id)
        if isinstance(analyzed, IntentResult):
            return analyzed
        cell_results, purified, seed, attractor = analyzed

        if not purified:
            logger.info("[RESOLVER] No violations found for rule '%s' in %s", rule_id, file_path.name)
            return IntentResult(intent=intent, status=IntentStatus.RESOLVED, value=cell_results,
                                resolved_by=Mahajana.SHAMBHU, parampara_verified=intent.is_connected)

        return self._resolve_rajas(intent, file_path, rule_id, seed, attractor, dry_run, cell_results)

    # =========================================================================
    # HELPERS
    # =========================================================================

    @staticmethod
    def _get_lotus() -> "MahamantraLotus":
        """Get the singleton MahamantraLotus."""
        from vibe_core.mahamantra.substrate.lotus_core import get_mahamantra
        return get_mahamantra()

    @staticmethod
    def _fire_gate_safe(
        lotus: "MahamantraLotus",
        gate: "TattvaGate",
        ctx: Dict[str, object],
    ) -> None:
        """Fire a gate with error isolation."""
        try:
            lotus._fire_gate(gate, ctx)
        except Exception as exc:
            logger.warning(
                "[RESOLVER] Gate %s fire failed (non-fatal): %s",
                gate.name, exc,
            )

    @staticmethod
    def _compute_seed(text: str) -> int:
        """Compute a deterministic seed from text."""
        h = 0
        for ch in text:
            h = (h * 31 + ord(ch)) & 0xFFFFFFFF
        return h


# =============================================================================
# WIRING — Register resolver in MantraKernel
# =============================================================================


_resolver_wired: bool = False


def wire_healing_resolver() -> bool:
    """
    Register HealingIntentResolver in the MantraKernel.

    Called once at boot. Idempotent.

    Returns:
        True if successfully registered.
    """
    global _resolver_wired
    if _resolver_wired:
        return True

    try:
        from vibe_core.mahamantra.kernel.intent import IntentType, get_kernel

        kernel = get_kernel()
        resolver = HealingIntentResolver()
        kernel.register_resolver(IntentType.HEAL, resolver)
        _resolver_wired = True
        logger.info("🔧 HealingIntentResolver wired to MantraKernel")
        return True

    except Exception as exc:
        logger.warning("Failed to wire HealingIntentResolver: %s", exc)
        return False


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "HealingIntentResolver",
    "wire_healing_resolver",
]
