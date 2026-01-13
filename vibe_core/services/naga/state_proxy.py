"""
NAGA State Proxy - The Consecrated Nerve (Nadi Shuddhi).
=========================================================

Naga ist nicht mehr nur ein Polizist. Er wurde geweiht (`Pratishta`).
Er dient nun Yamaraja (dem Gesetz) und verbindet die Glieder (State/Services)
mit dem Kopf (Universal Governance).

Architecture:
    Agent ("legacy") -> CommandContext -> [SetuBandha] -> SovereignContext (Dirty/Clean)
                                                                ↓
                                                         [YamarajaGate]
                                                                ↓
    Verdict: ALLOW/ATONE/ELEVATED/DENY -------------------------|

    If ALLOW/ATONE/ELEVATED -> StateService.save()
    If DENY                 -> Raise StateCorruptionAttempt
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "janaka"
__position__ = 10
__genesis__ = "0x4941b980"  # GenesisByte: parampara % 37 == 0

import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from vibe_core.di import ServiceRegistry
from vibe_core.protocols import StateServiceProtocol
from vibe_core.protocols.command import CommandContext
from vibe_core.protocols.naga.takshaka import TakshakaProtocol, VajraViolation
from vibe_core.protocols.universal.bridge import SetuBandha
# Yamaraja = Position 15 in Mahamantra (ONE source)
from vibe_core.protocols.mahajanas.yamaraja import Verdict
# ONE Yamaraja - all aspects in mahajanas/yamaraja (acintya)
from vibe_core.protocols.mahajanas.yamaraja import YamarajaGate

logger = logging.getLogger("NAGA.STATE_PROXY")


@dataclass
class DharmaVerdict:
    """Legacy wrapper for Universal Verdicts (Adapter Pattern)."""

    allowed: bool
    reason: str
    verdict: Verdict
    karma_cost: float


class StateCorruptionAttempt(Exception):
    """Raised when Yamaraja says DENY."""

    def __init__(self, message: str, verdict: Verdict):
        self.verdict = verdict
        super().__init__(f"NAGA BLOCKED (Yamaraja={verdict}): {message}")


class NagaStateProxy:
    """
    Der Geweihte Nerv.
    Verbindet State-Ops mit Universal Governance.
    """

    def __init__(
        self,
        state_service: StateServiceProtocol,
        takshaka: Optional[TakshakaProtocol] = None,
        strict_mode: bool = True,
    ):
        self._state = state_service
        self._takshaka = takshaka
        self._strict_mode = strict_mode

        # UNIVERSAL CONNECTION
        self.gate = YamarajaGate()

        # Metrics
        self._blocked_count = 0
        self._allowed_count = 0
        self._atoned_count = 0
        self._elevated_count = 0

        logger.info("🐍 NagaStateProxy consecrated. Yamaraja is watching.")

    @classmethod
    def wrap(cls, state_service: StateServiceProtocol, strict_mode: bool = True) -> "NagaStateProxy":
        """Factory method."""
        takshaka = ServiceRegistry.get(TakshakaProtocol)
        return cls(state_service, takshaka, strict_mode)

    # =========================================================================
    # UNIVERSAL JUDGMENT LOOPS
    # =========================================================================

    def _consult_yamaraja(self, agent_id: str, action: str, payload: Any) -> DharmaVerdict:
        """
        The Core Loop: Agent -> Bridge -> Yamaraja.
        """
        # 1. THE BRIDGE (Identity Transformation)
        # Wir bauen einen temporären CommandContext für den Caller.
        # Legacy Agent IDs sind "unverified", daher landen sie meist als Jiva/Legacy.
        legacy_ctx = CommandContext(
            caller=agent_id,
            metadata={"source": "naga_proxy"},  # Mark as internal proxy call
        )

        # Setu Bandha wandelt es in SovereignContext
        # (Legacy -> Dirty Context, Kernel/Tokens -> Clean)
        context = SetuBandha.cross_bridge(legacy_ctx)

        # 2. THE JUDGMENT (Yamaraja)
        judgment = self.gate.judge_action(context, action, payload)

        # 3. MAPPING (Universal -> Local)
        allowed = judgment.verdict != Verdict.DENY

        return DharmaVerdict(
            allowed=allowed, reason=judgment.reason, verdict=judgment.verdict, karma_cost=judgment.karma_cost
        )

    def _enforce(self, verdict: DharmaVerdict, agent_id: str, filename: str):
        """
        Enforce the verdict. Log Karma. Raise on DENY.
        """
        if not verdict.allowed:
            self._blocked_count += 1
            msg = f"Yamaraja DENIED save to '{filename}': {verdict.reason}"
            logger.warning(f"🐍🚫 {msg}")

            # Report to Takshaka (The Snake bites)
            if self._takshaka:
                self._takshaka.bite(
                    VajraViolation(
                        violation_type="GOVERNANCE_DENY",
                        source=agent_id,
                        details={"file": filename, "reason": verdict.reason},
                    )
                )

            if self._strict_mode:
                raise StateCorruptionAttempt(verdict.reason, verdict.verdict)
            return

        # HANDLE GRACE & PENANCE
        if verdict.verdict == Verdict.ATONE:
            self._atoned_count += 1
            logger.warning(
                f"🐍⚠️ ATONEMENT: {agent_id} allowed to save '{filename}' with Karma cost {verdict.karma_cost}. Reason: {verdict.reason}"
            )
            # TODO: Deduct Prana/Credits here

        elif verdict.verdict == Verdict.ELEVATED:
            self._elevated_count += 1
            logger.info(f"🐍✨ GRACE: {agent_id} granted ELEVATED access to '{filename}'. Reason: {verdict.reason}")

        else:
            self._allowed_count += 1
            logger.debug(f"🐍✅ ALLOW: {agent_id} writes to '{filename}'.")

    # =========================================================================
    # WRAPPED OPERATIONS
    # =========================================================================

    def save(
        self,
        filename: str,
        data: Any,
        create_backup: bool = True,
        indent: int = 2,
        agent_id: str = "unknown",
    ):
        """
        Save with Yamaraja's blessing.
        """
        # JUDGE
        verdict = self._consult_yamaraja(agent_id, f"save {filename}", data)

        # ENFORCE
        self._enforce(verdict, agent_id, filename)

        # ACT
        return self._state.save(filename, data, create_backup, indent)

    def append(
        self,
        filename: str,
        entry: Dict[str, Any],
        agent_id: str = "unknown",
    ):
        """
        Append with Yamaraja's blessing.
        """
        # JUDGE
        verdict = self._consult_yamaraja(agent_id, f"append {filename}", entry)

        # ENFORCE
        self._enforce(verdict, agent_id, filename)

        # ACT
        return self._state.append(filename, entry)

    # =========================================================================
    # PROXY PASS-THROUGH (Read Ops are Free - mostly)
    # =========================================================================

    # Reads are technically 'Sattva' (Knowledge).
    # Yamaraja usually allows reads unless documents are 'Confidential'.
    # For now, we perform direct pass-through for reads to avoid IO overhead.

    def load(self, filename: str, default: Any = None) -> Any:
        return self._state.load(filename, default)

    def load_jsonl(self, filename: str) -> List[Dict[str, Any]]:
        return self._state.load_jsonl(filename)

    def mark_dirty(self, path: Path, agent_id: str = "unknown") -> None:
        return self._state.mark_dirty(path)

    def clear_dirty_flags(self) -> None:
        return self._state.clear_dirty_flags()

    # Properties
    @property
    def workspace(self) -> Path:
        return self._state.workspace

    @property
    def state_root(self) -> Path:
        return self._state.state_root

    def get_dirty_files(self) -> List[Path]:
        return self._state.get_dirty_files()

    def get_stats(self) -> Dict[str, Any]:
        stats = self._state.get_stats()
        stats["naga"] = {
            "blocked": self._blocked_count,
            "allowed": self._allowed_count,
            "atoned": self._atoned_count,
            "elevated": self._elevated_count,
            "mode": "universal_yamaraja",
        }
        return stats

    def cleanup_backups(self) -> int:
        return self._state.cleanup_backups()

    def start_background_worker(self) -> None:
        return self._state.start_background_worker()

    @property
    def _worker_task(self):
        return self._state._worker_task

    @property
    def _commit_event(self):
        return self._state._commit_event


# =============================================================================
# FACTORY
# =============================================================================


def get_naga_state_proxy(
    workspace: Optional[Path] = None,
    agent_id: Optional[str] = None,
    plugin_id: Optional[str] = None,
    strict_mode: bool = True,
) -> NagaStateProxy:
    """
    Get a Consecrated StateService.
    """
    from vibe_core.state.state_service import get_state_service

    real_service = get_state_service(workspace, agent_id, plugin_id)
    return NagaStateProxy.wrap(real_service, strict_mode)
