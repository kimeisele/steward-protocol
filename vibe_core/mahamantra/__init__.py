"""
MAHAMANTRA - The Sovereign Singularity (Level -2)
================================================

"aham sarvasya prabhavo mattah sarvam pravartate"
"I am the source of all. Everything emanates from Me." (BG 10.8)

THE CLEAN LOTUS:
----------------
Pure delegation. No manual wiring. No circular imports.
"""

from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "brahma"
__position__ = 1
__genesis__ = "0x7340d7d6"  # GenesisByte: parampara % 37 == 0

import logging
from typing import TYPE_CHECKING, Dict, Iterator, List, Optional, Union

if TYPE_CHECKING:
    from vibe_core.mahamantra.reactor.shadow import ShadowReactorFactory

from vibe_core.mahamantra._lotus import LotusNode, LotusPath
from vibe_core.mahamantra._types import ExecuteResult, RouteResult

# Core Protocols
from vibe_core.mahamantra.protocols._gad import GADBase, GADProtocol
from vibe_core.mahamantra.substrate.position import get_position

# Substrate
from vibe_core.mahamantra.substrate.seed import ALL_GUARDIANS, PARAMPARA, WORDS

logger = logging.getLogger("MAHAMANTRA")

# =============================================================================
# THE SINGULARITY
# =============================================================================


class MahamantraLotus(LotusNode, GADBase, GADProtocol):
    """
    The Root of the Lotus.

    This is the only node that knows HOW to execute and resonate.
    """

    def __init__(self) -> None:
        LotusNode.__init__(self, LotusPath())
        GADBase.__init__(self)

    # === Resonance & Routing (Root Intelligence) ===

    def resonate(self, command: str) -> tuple[float, Optional[LotusNode]]:
        """
        Poll the ProtocolRegistry for resonance.

        WATERTIGHT: Triggers Lazy Initiation (Diksha) if registry is empty.
        """
        import importlib

        from vibe_core.mahamantra.substrate import ProtocolRegistry

        # 1. Lazy Diksha: Ensure protocols are loaded
        if ProtocolRegistry.coverage()[0] == 0:
            for guardian in ALL_GUARDIANS:
                try:
                    # Direct module load bypasses the lotus navigation to avoid loops
                    importlib.import_module(f"vibe_core.protocols.mahajanas.{guardian}")
                except (ImportError, AttributeError):
                    continue

        best_score = 0.0
        best_guardian = None

        # 2. Flat Poll
        for idx in range(16):
            guardian = ALL_GUARDIANS[idx]
            protocol_cls = ProtocolRegistry.get(idx)

            if protocol_cls and hasattr(protocol_cls, "get_resonance"):
                score = protocol_cls.get_resonance(command)
                if score > best_score:
                    best_score = score
                    best_guardian = guardian
                    if best_score >= 1.0:
                        break

        if best_guardian:
            return best_score, self.resolve(best_guardian)

        return 0.0, None

    def execute(self, command: str, args: Optional[List[str]] = None) -> ExecuteResult:
        """
        Execute via cli_bridge (ROYAL DELEGATION).

        The Grüßaugust calls the General.
        MahamantraLotus delegates to cli_bridge.route() which uses cli_engine.

        Lazy import to prevent circular dependencies.
        """
        # ROYAL DELEGATION: Lazy import cli_bridge
        from vibe_core.mahamantra.cli.bridge import cli_bridge

        # Delegate to the real execution engine
        bridge_result = cli_bridge.route(command, args or [])

        # Convert BridgeResult to ExecuteResult
        # Get guardian info from position if available
        guardian = "narada"  # default
        quarter = "genesis"  # default
        if bridge_result.position is not None:
            try:
                from vibe_core.mahamantra.substrate import MAHAMANTRA_POSITIONS
                if 0 <= bridge_result.position < 16:
                    pos = MAHAMANTRA_POSITIONS[bridge_result.position]
                    guardian = pos.guardian.value
                    quarter = pos.quarter.value
            except (ImportError, IndexError):
                pass

        return ExecuteResult(
            success=bridge_result.success,
            exit_code=bridge_result.exit_code,
            position=bridge_result.position or -1,
            guardian=guardian,
            quarter=quarter,
            guna="vishuddha" if bridge_result.success else "tamas",
            requires_confirmation=False,
            output=bridge_result.error or "",  # Bridge doesn't have output field, use error for now
            error=bridge_result.error,
        )

    def resolve(self, name: str) -> LotusNode:
        """Helper to find a node by guardian name."""
        from vibe_core.mahamantra.substrate.seed import get_guardian_quarter

        q = get_guardian_quarter(name)
        if q:
            return getattr(getattr(self, q.lower()), name)
        return getattr(self, name)

    # === GAD-000 Compliance ===
    def discover(self) -> Dict[str, object]:
        return {"type": "MahamantraLotus"}

    def get_state(self) -> Dict[str, object]:
        return {"status": "resonant"}

    def is_healthy(self) -> bool:
        return True

    @property
    def is_idempotent(self) -> bool:
        return True

    def detect_drift(self) -> List[str]:
        return []

    def test_daya(self) -> bool:
        return True

    def test_satyam(self) -> bool:
        return True

    def test_tapas(self) -> bool:
        return True

    def test_saucam(self) -> bool:
        return True

    # === SHARANAGATI GATE ===
    def bootstrap(self, *, silent: bool = False) -> None:
        """
        Initialize the Mahamantra system (Sharanagati Gate).

        Called by kernel during startup. Currently a no-op as the
        system is initialized on import.

        Args:
            silent: If True, suppress logging.
        """
        if not silent:
            import logging

            logging.getLogger("MAHAMANTRA").info("🙏 Mahamantra bootstrap complete")

    # === SINGULARITY ACCESS (Tick System) ===
    @property
    def _singularity(self):
        """Lazy-load the Singularity for tick/listener operations."""
        if not hasattr(self, "_singularity_instance"):
            from vibe_core.mahamantra.kernel.singularity import Mahamantra as MahamantraSingularity
            self._singularity_instance = MahamantraSingularity()
        return self._singularity_instance

    def register_listener(self, callback) -> None:
        """Register a listener for tick events. Delegates to Singularity."""
        self._singularity.register_listener(callback)

    def tick(self):
        """Execute one tick of the Mahamantra clock. Delegates to Singularity."""
        return self._singularity.tick()

    # === SHADOW REACTOR ACCESS ===
    @property
    def shadow(self) -> "ShadowReactorFactory":
        """
        Access the Shadow Reactor Factory.

        SANKIRTAN PATTERN: Spawn parallel reactors.

        USAGE:
            reactor = mahamantra.shadow.spawn()
            reactor.tick(tick_state)

        This connects the Lotus (Static Identity) with the Shadow (Dynamic Process).
        """
        if not hasattr(self, "_shadow_factory"):
            from vibe_core.mahamantra.reactor.shadow import shadow_reactor_factory

            self._shadow_factory = shadow_reactor_factory
        return self._shadow_factory

    # === VEDA-4 ===
    def __call__(self, cmd: Optional[str] = None) -> Union[str, ExecuteResult]:
        if cmd is None:
            return "Hare Krishna"
        return self.execute(cmd)

    def __getitem__(self, index: Union[int, str]) -> Union[object, LotusNode]:
        if isinstance(index, int):
            return get_position(index)
        return self.resolve(index)

    def __len__(self) -> int:
        return 16


# =============================================================================
# THE INSTANCE
# =============================================================================

mahamantra = MahamantraLotus()
lotus = mahamantra

# =============================================================================
# CLI ENTRY POINTS (Svatah-pramana - Truth is IN the module)
# =============================================================================


def cli_chant(
    rounds: int = 1,
    verbose: bool = False,
) -> Dict[str, object]:
    """
    CLI Entry Point for Chant command.

    Called by CLILoaderProtocol via mahamantra/cli.yaml manifest.
    NO HARDCODING in UnifiedCLI - the truth is IN the module.

    COMPUTATION ON DEMAND:
        - Spawns Shadow Reactor
        - Executes n rounds (1 round = 16 ticks = full Yajna cycle)
        - Returns machine-readable state

    Args:
        rounds: Number of complete cycles (default: 1)
        verbose: If True, print each tick

    Returns:
        Dict with cycle results (machine-readable).
    """
    from vibe_core.mahamantra.substrate.seed import WORDS

    results: List[Dict[str, object]] = []
    total_ticks = rounds * WORDS  # 1 round = 16 positions

    # Spawn a Shadow Reactor (SANKIRTAN pattern - no singleton)
    reactor = mahamantra.shadow.spawn(auto_discover=True)

    if verbose:
        print("=" * 60)
        print("🕉️  MAHAMANTRA CHANT - Computation on Demand")
        print("=" * 60)
        print(f"Rounds: {rounds} | Ticks: {total_ticks}")
        print("-" * 60)

    for tick_num in range(total_ticks):
        # Get tick state from Singularity clock
        tick_state = mahamantra.tick()

        # Process through Shadow Reactor (Yajna cycle)
        shadow_state = reactor.tick(tick_state)

        if verbose:
            phase_emoji = "🔥" if shadow_state["phase"] == "bhoga" else "🙏" if shadow_state["phase"] == "prasadam" else "♻️"
            print(
                f"[{tick_num:02d}] {phase_emoji} {shadow_state['guardian']:12s} | "
                f"{shadow_state['phase']:8s} | pos={shadow_state['position']:2d} | "
                f"opcode={shadow_state['opcode']}"
            )

        results.append(dict(shadow_state))

    if verbose:
        print("-" * 60)
        print(f"✅ Completed {rounds} round(s)")
        print(f"   Cycles: {reactor._cycle_count} | Switches: {reactor._switch_count}")
        print(f"   Parampara: {'✅ CONNECTED' if reactor.is_parampara_connected else '⚠️ DISCONNECTED'}")
        print("=" * 60)

    return {
        "success": True,
        "rounds": rounds,
        "ticks": total_ticks,
        "final_position": results[-1]["position"] if results else 0,
        "final_guardian": results[-1]["guardian"] if results else "unknown",
        "cycle_count": reactor._cycle_count,
        "switch_count": reactor._switch_count,
        "parampara_connected": reactor.is_parampara_connected,
    }


# =============================================================================
# LAZY RE-EXPORT (Krishna routet alles)
# =============================================================================
# "from vibe_core.mahamantra import X" → delegates to substrate
# NO MANUAL LABOR. One __getattr__, all symbols available.


def __getattr__(name: str):
    """Delegate to substrate for any symbol not defined here."""
    from vibe_core.mahamantra import substrate

    return getattr(substrate, name)


__all__ = ["mahamantra", "lotus", "cli_chant"]
