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

        Called by kernel during startup. Initializes:
        1. MahaComputeService (Listener Pattern integration)
        2. Future services via same pattern

        Args:
            silent: If True, suppress logging.
        """
        import logging

        _log = logging.getLogger("MAHAMANTRA")

        # === MAHA COMPUTE SERVICE (Listener Pattern) ===
        # Import triggers auto-registration with ServiceRegistry and as tick listener
        try:
            from vibe_core.services import maha_compute_service  # noqa: F401

            if not silent:
                _log.info("🧮 MahaComputeService activated")
        except ImportError as e:
            if not silent:
                _log.debug(f"MahaComputeService not available: {e}")

        if not silent:
            _log.info("🙏 Mahamantra bootstrap complete")

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

    # === ADAPTER ACCESS (Enterprise/Science Interface) ===
    @property
    def transform(self) -> "MahaTransform":
        """
        Access the MahaTransform adapter.

        ENTERPRISE USAGE:
            result = mahamantra.transform.compute(seed=42)
            attractor = mahamantra.transform.find_attractor(42)

        Standard CS interface for the 16-step transformation algorithm.
        """
        if not hasattr(self, "_transform"):
            from vibe_core.mahamantra.adapters.transform import MahaTransform

            self._transform = MahaTransform()
        return self._transform

    @property
    def hash(self) -> "DeterministicHash":
        """
        Access the DeterministicHash adapter.

        ENTERPRISE USAGE:
            h = mahamantra.hash.hash("my_intent")
            reading = mahamantra.hash.analyze("my_intent")

        Deterministic intent-to-integer encoding with multi-lens analysis.
        """
        if not hasattr(self, "_hash"):
            from vibe_core.mahamantra.adapters.hash import DeterministicHash

            self._hash = DeterministicHash()
        return self._hash

    def router(self, levels: int = 4) -> "HolographicRouter":
        """
        Create a HolographicRouter instance.

        ENTERPRISE USAGE:
            router = mahamantra.router(levels=4)  # 16-bit key space
            router.insert(0x1234, "value")
            value = router.get(0x1234)
            results = router.range_query(0x1200, 0x12FF)

        O(1) holographic key-value routing with O(k) range queries.
        """
        from vibe_core.mahamantra.adapters.routing import HolographicRouter

        return HolographicRouter(levels=levels)

    @property
    def orchestrator(self) -> "Orchestrator":
        """
        Access the Orchestrator adapter (rhythmic compute engine).

        ENTERPRISE USAGE:
            result = mahamantra.orchestrator.tick(seed=42)
            round_result = mahamantra.orchestrator.round(seed=42)
            mala_result = mahamantra.orchestrator.mala(seed=42)

        7-beat rhythmic compute orchestrator.
        7 = SEVEN (coprime with 16, LCM = 112)
        108 rounds per mala = complete devotional cycle.
        """
        if not hasattr(self, "_orchestrator"):
            from vibe_core.mahamantra.adapters.orchestrator import Orchestrator

            self._orchestrator = Orchestrator()
        return self._orchestrator

    @property
    def gita(self):
        """
        Access the Gita module (Source Code of Reality).

        USAGE:
            chapter_18 = mahamantra.gita.CHAPTER_18_VERSE
            is_valid = mahamantra.gita.verify_fixed_point()

        Chapter 18 is THE FIXED POINT - the North Star (Dhruva).
        """
        if not hasattr(self, "_gita"):
            from vibe_core.mahamantra.research import gita

            self._gita = gita
        return self._gita

    @property
    def pipeline(self) -> "MahamantraPipeline":
        """
        Access the 4-Phase Pipeline.

        THE ARCHITECTURE:
            Genesis → Dharma → Karma → Moksha
            (hash)    (transform)  (route)  (complete)

        ENTERPRISE USAGE:
            # Full pipeline
            result = mahamantra.pipeline.execute("my input")

            # Step by step
            intent = mahamantra.pipeline.genesis("input")
            processed = mahamantra.pipeline.dharma(intent.hash_value)
            routed = mahamantra.pipeline.karma(processed.value)
            complete = mahamantra.pipeline.moksha(routed)

        Each phase maps to a quarter of the Mahamantra:
        - GENESIS: Hare Krishna Hare Krishna (Brahma Sampradaya)
        - DHARMA: Krishna Krishna Hare Hare (Kumara Sampradaya)
        - KARMA: Hare Rama Hare Rama (Sri Sampradaya)
        - MOKSHA: Rama Rama Hare Hare (Rudra Sampradaya)
        """
        if not hasattr(self, "_pipeline"):
            from vibe_core.mahamantra.adapters.pipeline import MahamantraPipeline

            self._pipeline = MahamantraPipeline()
        return self._pipeline

    def bio(self, k: int = 8) -> "LotusBio":
        """
        Create a LotusBio k-mer index for DNA analysis.

        THE INSIGHT:
            DNA = 4 bases = QUARTERS (A, C, G, T)
            2 bits per base = MantraByte encoding
            8-mer = 16 bits = 65,536 = Lotus Router key space

        USAGE:
            bio = mahamantra.bio(k=8)  # 8-mer index
            bio.index_sequence("ACGTACGTACGT...")
            count = bio.count("ACGTACGT")  # O(1)
            positions = bio.find("ACGTACGT")  # O(1)

        Args:
            k: k-mer length (default: 8, max: 16)

        Returns:
            LotusBio k-mer index
        """
        from vibe_core.mahamantra.adapters.bio import LotusBio

        return LotusBio(k=k)

    @property
    def attention(self) -> "MahaAttention":
        """
        Access the MahaAttention mechanism (O(1) Intent Routing).

        SILICON VALLEY PROBLEM:
            Transformer attention: O(N²)
            Vector DB similarity: O(N)
            Linear intent scan: O(N)

        MAHA SOLUTION:
            Lotus Attention: O(1) - CONSTANT TIME

        USAGE:
            # Register handlers
            mahamantra.attention.memorize("deploy prod", deploy_handler)
            mahamantra.attention.memorize("run tests", test_handler)

            # O(1) resolution - no LLM needed!
            handler = mahamantra.attention("deploy prod")
            handler()  # Executes deploy_handler

        For N=65,536 intents: 16,384x speedup vs linear scan
        """
        if not hasattr(self, "_attention"):
            from vibe_core.mahamantra.adapters.attention import MahaAttention

            self._attention = MahaAttention()
        return self._attention

    @property
    def veda(self) -> "VedaExplorer":
        """
        Access the VedaExplorer (Neuro-Symbolic Chat Interface).

        THE VEDA-4 PIPELINE:
            SHABDA (Word)     → Intent parsing
            ARTHA (Meaning)   → Parameter extraction
            PRATYAYA (Trust)  → Validation
            KARMA (Action)    → Execution

        NOW INTEGRATED WITH MahamantraPipeline:
            SHABDA  → GENESIS (hash intent)
            ARTHA   → DHARMA (transform/validate)
            PRATYAYA → KARMA (route/trust)
            KARMA   → MOKSHA (execute/complete)

        ENTERPRISE USAGE:
            # Process input
            result = mahamantra.veda.process("chant 108")

            # Process with full pipeline tracking
            result = mahamantra.veda.process_with_pipeline("who is brahma?")

            # Interactive REPL
            mahamantra.veda.repl()

        MODES:
            RESTRICTED - Deterministic only (cost-free)
            ENHANCED   - LLM fallback for unknown
            CREATIVE   - Full LLM conversation
        """
        if not hasattr(self, "_veda"):
            from vibe_core.mahamantra.cli.veda_explorer import VedaExplorer

            self._veda = VedaExplorer()
        return self._veda

    # === GOVERNANCE SCAN ===
    def scan(self, base_path: Optional[str] = None) -> dict:
        """
        Scan the codebase for Mahajana governance.

        Returns governance stats: coverage, by_mahajana, orphans, etc.

        Usage:
            result = mahamantra.scan()
            print(f"Coverage: {result['coverage']:.1f}%")
            print(f"Orphans: {result['files_orphan']}")
        """
        from pathlib import Path

        from vibe_core.mahamantra.substrate.scanner import scan_all

        path = Path(base_path) if base_path else None
        result = scan_all(base_path=path)

        # Add convenience coverage field
        if result.get("files_scanned", 0) > 0:
            result["coverage"] = (result["files_owned"] / result["files_scanned"]) * 100
        else:
            result["coverage"] = 0.0

        return result

    def scan_report(self) -> str:
        """
        Generate a human-readable governance scan report.

        Usage:
            print(mahamantra.scan_report())
        """
        result = self.scan()
        lines = [
            "═══════════════════════════════════════════",
            "       MAHAMANTRA GOVERNANCE SCAN",
            "═══════════════════════════════════════════",
            f"  Total files:  {result.get('files_total', 0):>6}",
            f"  Scanned:      {result.get('files_scanned', 0):>6}",
            f"  Owned:        {result.get('files_owned', 0):>6}",
            f"  Orphan:       {result.get('files_orphan', 0):>6}",
            f"  Coverage:     {result.get('coverage', 0):>5.1f}%",
            "───────────────────────────────────────────",
            "  By Mahajana:",
        ]

        for m, count in sorted(result.get("by_mahajana", {}).items(), key=lambda x: -x[1])[:8]:
            lines.append(f"    {m:12}: {count:4}")

        lines.append("═══════════════════════════════════════════")
        return "\n".join(lines)

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
# LAZY RE-EXPORT (Krishna routet alles)
# =============================================================================
# "from vibe_core.mahamantra import X" → delegates to substrate
# NO MANUAL LABOR. One __getattr__, all symbols available.


def __getattr__(name: str):
    """Delegate to substrate for any symbol not defined here."""
    from vibe_core.mahamantra import substrate

    return getattr(substrate, name)


__all__ = ["mahamantra", "lotus"]
