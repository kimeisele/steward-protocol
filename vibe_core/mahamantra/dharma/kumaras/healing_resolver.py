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

    def resolve(self, intent: "MantraIntent") -> "IntentResult":
        """
        Resolve a HEAL intent through the 5-gate pipeline.

        Intent params:
            - file_path (str): Path to the file to heal
            - rule_id (str): Which violation to heal
            - dry_run (bool): If True, analysis only (no Maya-Sync)
            - violation_id (str): Optional KG violation node ID

        Returns:
            IntentResult with List[CellularHealingResult] as value.
        """
        from vibe_core.mahamantra.kernel.intent import (
            IntentResult,
            IntentStatus,
        )
        from vibe_core.mahamantra.substrate.pancha_tattva import TattvaGate
        from vibe_core.mahamantra.substrate.guna import Guna
        from vibe_core.mahamantra import Mahajana

        # ── Extract params ──
        file_path_str = intent.params.get("file_path", "")
        rule_id = intent.params.get("rule_id", "")
        dry_run = bool(intent.params.get("dry_run", False))
        violation_id = intent.params.get("violation_id")

        if not file_path_str or not rule_id:
            return IntentResult(
                intent=intent,
                status=IntentStatus.FAILED,
                error="HEAL intent requires 'file_path' and 'rule_id' params",
                resolved_by=Mahajana.SHAMBHU,
            )

        file_path = Path(str(file_path_str))
        if not file_path.exists():
            return IntentResult(
                intent=intent,
                status=IntentStatus.FAILED,
                error=f"File not found: {file_path}",
                resolved_by=Mahajana.SHAMBHU,
            )

        # ── Get Lotus for gate firing ──
        lotus = self._get_lotus()
        healer = get_cellular_healer()

        if not healer.can_heal(str(rule_id)):
            return IntentResult(
                intent=intent,
                status=IntentStatus.FAILED,
                error=f"No remedy registered for rule '{rule_id}'",
                resolved_by=Mahajana.SHAMBHU,
            )

        # =================================================================
        # PHASE 1: SATTVA — Analysis in RAM (Gates 0-3)
        # =================================================================
        # No side effects. No disk writes. Pure observation.

        # ── GATE 0: PARSE (Dharma/Chaitanya) ──
        # "Does this file exist? Is the intent valid?"
        parse_ctx: Dict[str, object] = {
            "input_data": str(file_path),
            "intent_type": "HEAL",
            "rule_id": rule_id,
        }
        self._fire_gate_safe(lotus, TattvaGate.PARSE, parse_ctx)

        # ── GATE 1: VALIDATE (Jnana/Nityananda) ──
        # "Is the remedy available? Are fragments valid?"
        seed = self._compute_seed(str(file_path) + str(rule_id))
        validate_ctx: Dict[str, object] = {
            "seed": seed,
            "rule_id": rule_id,
            "file_path": str(file_path),
            "remedy_available": True,
        }
        self._fire_gate_safe(lotus, TattvaGate.VALIDATE, validate_ctx)

        # ── GATE 2: EXECUTE (Advaita) ──
        # "Apply the CSTRemedy to fragments in RAM."
        attractor = seed % 108  # Vedic attractor
        execute_ctx: Dict[str, object] = {
            "seed": seed,
            "attractor": attractor,
            "operation": "cellular_healing",
            "rule_id": rule_id,
        }
        self._fire_gate_safe(lotus, TattvaGate.EXECUTE, execute_ctx)

        # ── Perform the actual CST surgery (in RAM — SATTVA safe) ──
        try:
            cell_results = healer.heal_file(
                file_path=file_path,
                rule_id=str(rule_id),
                dry_run=True,  # Always dry_run in SATTVA phase
                governed=False,
            )
        except Exception as exc:
            logger.error("[RESOLVER] CST surgery failed: %s", exc)
            return IntentResult(
                intent=intent,
                status=IntentStatus.FAILED,
                error=f"CST surgery failed: {exc}",
                resolved_by=Mahajana.SHAMBHU,
            )

        # ── GATE 3: RESULT (Gadadhara) ──
        # "What did the surgery produce?"
        purified = [r for r in cell_results if r.status == ShuddhiStatus.PURIFIED]
        result_ctx: Dict[str, object] = {
            "attractor": attractor,
            "fragments_total": len(cell_results),
            "fragments_purified": len(purified),
            "dry_run": dry_run,
        }
        self._fire_gate_safe(lotus, TattvaGate.RESULT, result_ctx)

        # ── If nothing to heal, return early ──
        if not purified:
            logger.info(
                "[RESOLVER] No violations found for rule '%s' in %s",
                rule_id, file_path.name,
            )
            return IntentResult(
                intent=intent,
                status=IntentStatus.RESOLVED,
                value=cell_results,
                resolved_by=Mahajana.SHAMBHU,
                parampara_verified=intent.is_connected,
            )

        # =================================================================
        # PHASE 2: RAJAS — Authorized Commit (Gate 4)
        # =================================================================
        # The Guna ESCALATES from SATTVA to RAJAS for the write.

        if dry_run:
            # Dry run: fire SYNC gate for observability, but skip write
            sync_ctx: Dict[str, object] = {
                "position": attractor % 16,
                "seed": seed,
                "attractor": attractor,
                "opcode": None,
                "guna": Guna.SATTVA,  # Dry run stays SATTVA
            }
            self._fire_gate_safe(lotus, TattvaGate.SYNC, sync_ctx)

            logger.info(
                "[RESOLVER] DRY RUN: %d fragments would be healed in %s",
                len(purified), file_path.name,
            )
            return IntentResult(
                intent=intent,
                status=IntentStatus.RESOLVED,
                value=cell_results,
                resolved_by=Mahajana.SHAMBHU,
                parampara_verified=intent.is_connected,
            )

        # ── GATE 4: SYNC (Srivasa) — RAJAS authorized commit ──
        from vibe_core.mahamantra.substrate.opcode import MantraOpCode

        sync_ctx = {
            "position": attractor % 16,
            "seed": seed,
            "attractor": attractor,
            "opcode": MantraOpCode.EXEC_OP,  # RAJAS opcode for commit
            "guna": Guna.RAJAS,  # Guna escalation!
        }
        self._fire_gate_safe(lotus, TattvaGate.SYNC, sync_ctx)

        # ── Now perform the governed write (Maya-Sync through Srivasa) ──
        try:
            governed_results = healer.heal_file(
                file_path=file_path,
                rule_id=str(rule_id),
                dry_run=False,
                governed=True,  # Goes through EnforceGateProvider.write_source()
            )
        except Exception as exc:
            logger.error("[RESOLVER] Governed Maya-Sync failed: %s", exc)
            return IntentResult(
                intent=intent,
                status=IntentStatus.FAILED,
                error=f"Maya-Sync failed: {exc}",
                resolved_by=Mahajana.SHAMBHU,
            )

        # Count actual healings
        actual_purified = [
            r for r in governed_results
            if r.status == ShuddhiStatus.PURIFIED and r.maya_synced
        ]

        logger.info(
            "[RESOLVER] ✅ Healed %d/%d fragments in %s through 5-gate pipeline",
            len(actual_purified), len(governed_results), file_path.name,
        )

        return IntentResult(
            intent=intent,
            status=IntentStatus.RESOLVED,
            value=governed_results,
            resolved_by=Mahajana.SHAMBHU,
            parampara_verified=intent.is_connected,
        )

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
