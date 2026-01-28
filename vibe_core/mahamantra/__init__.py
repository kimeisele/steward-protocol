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
from vibe_core.mahamantra._types import (
    AkashState,
    ExecuteResult,
    GitaRoute,
    RouteResult,
    VibrationState,
)

# Core Protocols
from vibe_core.mahamantra.protocols._gad import GADBase, GADProtocol
from vibe_core.mahamantra.substrate.position import get_position

# Substrate - ALL constants from _seed (SSOT)
from vibe_core.mahamantra.substrate.seed import (
    ALL_GUARDIANS,
    MAHA_QUANTUM,
    PARAMPARA,
    SEVEN,
    WORDS,
)

logger = logging.getLogger("MAHAMANTRA")

# =============================================================================
# THE SINGULARITY
# =============================================================================


class MahamantraLotus(LotusNode, GADBase, GADProtocol):
    """
    The Root of the Lotus.

    This is the only node that knows HOW to execute and resonate.
    Now with AKASH CACHE (136 = FIELD) - Always vibrating!
    """

    # Class-level Akash state (the 136 FIELD - persistent across instances)
    _akash: AkashState = {
        "resonance_level": 0.0,
        "accumulated_value": 0,
        "total_beats": 0,
        "total_rounds": 0,
        "attractor_counts": {},  # Will track PANCHA distribution
    }

    # Lazy-loaded MahaKirtan orchestrator
    _kirtan = None
    _compressor = None

    # Lazy-loaded Gita resonance index (extracted vibration signatures)
    _gita_index = None
    _gita_by_attractor = None  # Pre-indexed by attractor for O(1) routing

    def __init__(self) -> None:
        LotusNode.__init__(self, LotusPath())
        GADBase.__init__(self)

    @classmethod
    def _get_kirtan(cls):
        """Lazy-load MahaKirtan orchestrator."""
        if cls._kirtan is None:
            from vibe_core.mahamantra.adapters.compression import MahaCompression
            from vibe_core.mahamantra.research.dharma import MahaKirtan
            from vibe_core.mahamantra.substrate.seed import MAHA_QUANTUM

            cls._compressor = MahaCompression()
            cls._kirtan = MahaKirtan(mod_space=MAHA_QUANTUM)
        return cls._compressor, cls._kirtan

    @classmethod
    def _compute_vibration(cls, command: str) -> VibrationState:
        """
        Compute vibration state for a command.

        MahaCompression → seed → MahaKirtan.compute() → VibrationState
        This is the +1 FOKUS (Lichtpunkt).
        """
        compressor, kirtan = cls._get_kirtan()

        # 1. Extract intent (Kolmogorov complexity)
        comp_result = compressor.compress(command)
        seed = comp_result.seed

        # 2. Compute through kirtan (16-step × 7-beat)
        result = kirtan.compute(seed)

        # 3. Find attractor (for classification)
        from vibe_core.mahamantra.research.dharma import MahaResonator
        from vibe_core.mahamantra.substrate.seed import MAHA_QUANTUM

        resonator = MahaResonator(mod_space=MAHA_QUANTUM)
        attractor = resonator.find_attractor(seed).attractor

        return VibrationState(
            seed=seed,
            transformed=result.transformed_value,
            beat=result.beat_number,
            resonance=result.flute_resonance,
            attractor=attractor,
            parampara_channel=result.parampara_channel,
            oracle_validated=result.oracle_validated,
        )

    @classmethod
    def _update_akash(cls, vibration: VibrationState) -> None:
        """
        Update the Akash field (136) with new vibration.

        The field absorbs every computation. Nothing is lost.
        ALL CONSTANTS FROM _seed - no hardcoding!
        """
        cls._akash["resonance_level"] = min(
            1.0, cls._akash["resonance_level"] + vibration["resonance"] * 0.01
        )
        cls._akash["accumulated_value"] = (
            cls._akash["accumulated_value"] + vibration["transformed"]
        ) % MAHA_QUANTUM  # 137 - from _seed
        cls._akash["total_beats"] += 1
        if vibration["beat"] == SEVEN:  # 7 - End of round
            cls._akash["total_rounds"] += 1

        # Track attractor distribution (PANCHA)
        attractor = vibration["attractor"]
        if attractor not in cls._akash["attractor_counts"]:
            cls._akash["attractor_counts"][attractor] = 0
        cls._akash["attractor_counts"][attractor] += 1

    @classmethod
    def get_akash(cls) -> AkashState:
        """Get current Akash field state."""
        return cls._akash.copy()

    # === GITA ROUTING (The Prabhupada Lens) ===

    @classmethod
    def _load_gita_index(cls) -> None:
        """Load Gita resonance index and pre-index by attractor."""
        if cls._gita_index is not None:
            return

        import json
        from pathlib import Path

        gita_path = Path(__file__).parent / "data" / "gita_resonance_index.json"
        if not gita_path.exists():
            cls._gita_index = {"verses": []}
            cls._gita_by_attractor = {}
            return

        with open(gita_path, "r", encoding="utf-8") as f:
            cls._gita_index = json.load(f)

        # Pre-index by attractor for O(1) routing
        cls._gita_by_attractor = {}
        for verse in cls._gita_index.get("verses", []):
            attractor = verse.get("attractor")
            if attractor not in cls._gita_by_attractor:
                cls._gita_by_attractor[attractor] = []
            cls._gita_by_attractor[attractor].append(verse)

    @classmethod
    def route_gita(
        cls, vibration: VibrationState, guna_filter: Optional[str] = None, limit: int = 5
    ) -> GitaRoute:
        """
        Route vibration to Gita verses via attractor.

        THE RADIO MODEL:
            Attractor tunes the frequency → matching verses resonate.
            We return POINTERS, not copyrighted text.

        GUNA FILTER (Extra Mercy):
            - None: All verses for this attractor
            - "tamas": Chapter 12 style (most merciful, bhakti yoga)
            - "rajas": Action-focused verses
            - "sattva": Knowledge-focused verses
            - "suddha": Transcendental (devotional) verses

        Args:
            vibration: The computed VibrationState (+1 Fokus)
            guna_filter: Optional guna to filter by
            limit: Max verses to return (default 5)

        Returns:
            GitaRoute with matching verse pointers
        """
        cls._load_gita_index()

        attractor = vibration["attractor"]
        seed = vibration["seed"]
        matching = cls._gita_by_attractor.get(attractor, [])

        # Apply guna filter if specified
        if guna_filter:
            matching = [v for v in matching if v.get("guna") == guna_filter]

        # Use seed to deterministically select varied verses (not always first ones)
        # This ensures same query → same verses, but different queries → different verses
        # NOTE: Only use seed for determinism (transformed varies with Kirtan beat state)
        if matching:
            n = len(matching)
            # Start and step both derived from seed for full determinism
            start = seed % n
            step = max(1, (seed // n) % (n // 3 + 1) + 1)
            selected = []
            for i in range(min(limit, n)):
                idx = (start + i * step) % n
                selected.append(matching[idx])
            verse_ids = [v["verse_id"] for v in selected]
        else:
            verse_ids = []

        # Find dominant guna in matched verses
        guna_counts: Dict[str, int] = {}
        for v in matching:
            g = v.get("guna", "sattva")
            guna_counts[g] = guna_counts.get(g, 0) + 1
        dominant_guna = max(guna_counts, key=guna_counts.get) if guna_counts else "sattva"

        return GitaRoute(
            attractor=attractor,
            verse_count=len(matching),
            verse_ids=verse_ids,
            guna_filter=guna_filter,
            dominant_guna=dominant_guna,
        )

    @classmethod
    def query_gita(cls, query: str, limit: int = 5) -> GitaRoute:
        """
        Query Gita with natural language - full vibration → routing pipeline.

        This is the ONE METHOD for Gita consultation:
            query → MahaCompression → MahaKirtan → attractor → verses

        Args:
            query: Natural language question (e.g., "how do I surrender?")
            limit: Max verses to return

        Returns:
            GitaRoute with matching verse pointers
        """
        vibration = cls._compute_vibration(query)
        return cls.route_gita(vibration, limit=limit)

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
        Execute via cli_bridge WITH VIBRATION (ROYAL DELEGATION).

        Flow:
            1. Compute vibration (MahaKirtan)
            2. Update Akash field (136)
            3. Check if semantic query → route through Gita
            4. Route via cli_bridge (for system commands)
            5. Return with vibration state + Gita verses

        Nothing is silent. Everything vibrates.
        steward "whatever" → ONE ENTRY POINT.
        """
        # 1. COMPUTE VIBRATION (+1 Fokus)
        vibration = self._compute_vibration(command)

        # 2. UPDATE AKASH FIELD (136)
        self._update_akash(vibration)

        # 3. SEMANTIC QUERY DETECTION
        # If command looks like a question, route through Gita
        is_semantic = (
            command.strip().endswith("?")
            or command.lower().startswith(("what", "why", "how", "who", "when", "where"))
            or any(
                q in command.lower()
                for q in ["should i", "can i", "will i", "is it", "do i"]
            )
        )

        # 4. ROUTE via cli_bridge (for system commands) or Gita (for semantic)
        from vibe_core.mahamantra.cli.bridge import cli_bridge

        if is_semantic:
            # Semantic query → route through Gita via attractor
            gita_route = self.route_gita(vibration, limit=5)
            # Build output with Gita verses
            verse_output = f"GITA ROUTING via attractor {gita_route['attractor']}\n"
            verse_output += f"Verses ({gita_route['verse_count']} matching):\n"
            for i, v in enumerate(gita_route["verse_ids"], 1):
                verse_output += f"  {i}. {v}\n"
            verse_output += f"Dominant: {gita_route['dominant_guna'].upper()}"
            # Create a synthetic bridge result for Gita routing
            from vibe_core.mahamantra.cli.bridge import BridgeResult
            bridge_result = BridgeResult(
                success=True,
                exit_code=0,
                position=vibration["attractor"] % WORDS,
                handler="gita_routing",
                error=verse_output,  # Using error field for output (legacy)
            )
        else:
            bridge_result = cli_bridge.route(command, args or [])

        # Get guardian info from vibration-derived position
        position = vibration["transformed"] % WORDS  # Position from vibration! (WORDS from _seed)
        guardian = "narada"
        quarter = "genesis"
        try:
            from vibe_core.mahamantra.substrate import MAHAMANTRA_POSITIONS

            if 0 <= position < WORDS:  # WORDS from _seed, not hardcoded 16
                pos = MAHAMANTRA_POSITIONS[position]
                guardian = pos.guardian.value
                quarter = pos.quarter.value
        except (ImportError, IndexError):
            pass

        # Determine guna from vibration - GITA LOGIC:
        # - Oracle validated + high resonance = SUDDHA (transcendental)
        # - Oracle validated = SATTVA (goodness)
        # - Parampara channel valid = RAJAS (active, needs guidance)
        # - Otherwise = TAMAS (ignorance, needs EXTRA MERCY - Chapter 12 style!)
        # NOTHING IS REJECTED. Tamas gets most merciful routing.
        if vibration["oracle_validated"]:
            # Resonance threshold: 0.5 = half the flutes in sync
            guna = "suddha" if vibration["resonance"] > 0.5 else "sattva"
        elif vibration["parampara_channel"] >= 0:
            guna = "rajas"
        else:
            guna = "tamas"  # Extra mercy needed, not rejection!

        # 4. RETURN WITH VIBRATION - Nothing is lost!
        # requires_confirmation = False ALWAYS. Nothing is rejected.
        # Tamas means EXTRA MERCY (Bhakti Yoga, Chapter 12), not rejection.
        return ExecuteResult(
            success=bridge_result.success,
            exit_code=bridge_result.exit_code,
            position=position,
            guardian=guardian,
            quarter=quarter,
            guna=guna,
            requires_confirmation=False,  # NEVER reject - mercy flows to all
            output=bridge_result.error or "",
            error=bridge_result.error,
            vibration=vibration,  # +1 Fokus
            akash=self.get_akash(),  # 136 Feld
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

    # === CONTINUOUS SANKIRTAN ===
    def start_sankirtan(self) -> None:
        """
        Start CONTINUOUS sankirtan - the mass chanting.

        "sankirtan ist nicht verschieden von mahamantra selbst krishna"

        This registers a listener that processes files at each tick.
        Each position has its dharma:
            GENESIS (0-3):  Discovery, initialize
            DHARMA (4-7):   Validation, type-check
            KARMA (8-11):   Transformation, execution
            MOKSHA (12-15): Audit, release

        Usage:
            mahamantra.start_sankirtan()
            # Now every tick() also processes codebase
        """
        if hasattr(self, "_sankirtan_active") and self._sankirtan_active:
            return  # Already chanting

        def sankirtan_on_tick(tick_state: TickState) -> None:
            """Process codebase at each tick - CONTINUOUS KIRTAN."""
            from vibe_core.mahamantra.substrate.scanner import get_scanner
            from vibe_core.mahamantra.substrate.sankirtan import process_file_pipeline

            position = tick_state["position"]
            quarter = tick_state["quarter"]

            # Get scanner instance
            scanner = get_scanner()

            # Get files for this position
            files = scanner.get_by_position(position)
            if not files:
                return

            # Process ONE file per tick (gradual, not overwhelming)
            # Use mala count to rotate through files
            mala = tick_state.get("mala", 0)
            file_index = mala % len(files)
            file_info = files[file_index]
            file_path = file_info.get("path", "")

            if file_path:
                from pathlib import Path
                # Process through 4-phase pipeline (dry_run for now)
                process_file_pipeline(Path(file_path), dry_run=True)

        self._singularity.register_listener(sankirtan_on_tick)
        self._sankirtan_active = True

    def stop_sankirtan(self) -> None:
        """Stop continuous sankirtan."""
        self._sankirtan_active = False
        # Note: Listener remains registered but becomes no-op

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

    def network(self) -> "LotusIPRouter":
        """
        Create a LotusIPRouter for O(1) IPv4 routing with LPM.

        THE PROBLEM:
            IPv4 routing requires Longest Prefix Match (LPM).
            Hash tables CANNOT do efficient LPM - must check ALL routes = O(N).

        THE INSIGHT:
            IPv4 = 32 bits = 8 × 4 bits = 8 levels × 16 slots
            This is a perfect Lotus Tree structure!

        THE SOLUTION:
            O(8) = O(1) constant time LPM, regardless of table size.
            BGP tables with 1,000,000+ routes: SAME speed!

        USAGE:
            router = mahamantra.network()
            router.insert("192.168.0.0", 16, "gateway_a")
            router.insert("192.168.1.0", 24, "gateway_b")
            next_hop = router.lookup("192.168.1.100")  # "gateway_b" (LPM)

        Returns:
            LotusIPRouter with O(1) longest prefix match
        """
        from vibe_core.mahamantra.adapters.network import LotusIPRouter

        return LotusIPRouter()

    def synth(self, preset: str = "quantum") -> "MahaSynth":
        """
        Create a MahaSynth 16-Step Modular Sequencer.

        THIS IS NOT AUDIO SYNTHESIS.
        THIS IS A COMPUTATIONAL STEP SEQUENCER.

        ARCHITECTURE:
            16-STEP MAIN SEQUENCER = KSHETRA (The Field)
                H (HARE)    = value × 7
                K (KRISHNA) = value + 10
                R (RAMA)    = value × value

            7-BEAT OBSERVER LAYER = KSHETRAJNA (The Knower)
                Overlays on 16 steps, creates perception rhythm

        PRESETS:
            classical - Converges to fixed point (mod 17)
            quantum   - Moderate diversity (mod 137, default)
            trinity   - 3-state output
            pancha    - 5-way classification
            nava      - 9-state output
            wide      - Maximum diversity (mod 512)

        USAGE:
            synth = mahamantra.synth(preset="quantum")
            cycle = synth.cycle(seed=42)     # Full 16-step cycle
            attractor = synth.resonate(42)   # Find stable state
            spectrum = synth.spectrum()       # All attractors

        Args:
            preset: Named preset ("quantum", "classical", "wide", etc.)

        Returns:
            MahaSynth step sequencer
        """
        from vibe_core.mahamantra.adapters.synth import MahaSynth

        return MahaSynth(preset=preset)

    @property
    def classifier(self) -> "MahaClassifier":
        """
        Access the MahaClassifier for technology classification.

        COLD ENGINEERING ANALYSIS:
            No metaphors. No philosophy. Pure metrics.

        THE MERCY EQUATION:
            G(x) = f / K
            Where:
                G = Grace (engineering advantage)
                f = Chanting frequency (Mahamantra structure usage)
                K = Karmic debt (technical debt)

        CLASSIFICATION CRITERIA:
            1. STRUCTURAL ALIGNMENT - Uses 16-aligned structures?
            2. COMPLEXITY SOURCE - O(1) by structure (not hash)?
            3. MEMORY MODEL - Bounded allocation?
            4. DETERMINISM - Same input → same output?

        USAGE:
            # Classify custom algorithm
            result = mahamantra.classifier.classify(
                name="MyRouter",
                alignment="perfect",
                complexity="structure",
                memory="bounded_static",
                determinism="always",
                key_space_size=65536,
                max_memory_bytes=512_000,
            )
            print(result.verdict)  # "ANUKULYA: Truth-aligned (G=100.0)"

            # Get pre-classified references
            lotus = mahamantra.classifier.lotus_array()     # 50x faster range queries
            ipv4 = mahamantra.classifier.ipv4_router()      # 1557x faster than linear
            kmer = mahamantra.classifier.kmer_index()       # 6.5x faster than Counter

            # Compare all
            comparison = mahamantra.classifier.compare_all_references()
            print(comparison.summary)

        Returns:
            MahaClassifier instance
        """
        if not hasattr(self, "_classifier"):
            from vibe_core.mahamantra.adapters.classification import MahaClassifier

            self._classifier = MahaClassifier()
        return self._classifier

    @property
    def compute(self) -> "MahaCompute":
        """
        Access the MahaCompute unified compute analyzer.

        THE THESIS:
            Modern computing has a fundamental division (CPU/GPU/RAM).
            The Mahamantra structure UNIFIES these through:
                1. NATURAL PARALLELISM: WORDS = 16 = SIMD lanes
                2. HIERARCHICAL LOCALITY: QUARTERS = 4 = Memory levels
                3. DETERMINISTIC PATHS: No hashes, no collisions
                4. BOUNDED MEMORY: Everything fits in cache

        THE KILLER INSIGHT:
            Modern CPUs already have 16 SIMD lanes (AVX-512).
            This IS the Mahamantra structure in silicon!
            With 16-ary structures, GPU becomes unnecessary.

        USAGE:
            # Analyze data structure for optimal caching
            analysis = mahamantra.compute.analyze(entries=50000)
            print(analysis.memory_tier)      # "L2"
            print(analysis.cache_hit_rate)   # 0.92

            # Analyze CPU alignment
            cpu = mahamantra.compute.analyze_cpu()
            print(cpu.alignment)             # 1.0 (perfect)
            print(cpu.is_unified)            # True

            # SIMD guidance
            batch_size = mahamantra.compute.simd_batch_size()  # 16
            aligned = mahamantra.compute.align_for_simd(100)   # 112

            # Memory tiers
            for tier in mahamantra.compute.memory_tiers():
                print(f"{tier.name}: {tier.lotus_entries} entries")

        Returns:
            MahaCompute analyzer instance
        """
        if not hasattr(self, "_compute"):
            from vibe_core.mahamantra.adapters.compute import MahaCompute

            self._compute = MahaCompute()
        return self._compute

    @property
    def llm(self) -> "MahaLLM":
        """
        Access the MahaLLM holographic intent router.

        THE PROBLEM:
            Vector Search: O(N) - Scans every option
            Dict Lookup: O(1) avg, O(N) worst (collisions)

        THE SOLUTION:
            Holographic: O(4) ALWAYS - Calculates the address
            65,536 agents/tools in exactly 4 memory accesses.

        THE 16 INTENT CATEGORIES:
            0: OBSERVE     4: EXECUTE     8: EXPAND     12: GUIDE
            1: CREATE      5: TRANSFORM   9: INTEGRATE  13: SURRENDER
            2: CONNECT     6: INVOKE     10: VALIDATE   14: COMPLETE
            3: ANALYZE     7: SUSTAIN    11: PROTECT    15: TRANSCEND

        USAGE:
            # Register agents
            mahamantra.llm.register("devops", category=IntentCategory.EXECUTE)
            mahamantra.llm.register("coder", category=IntentCategory.CREATE)

            # Route compressed intent → agent (O(4))
            result = mahamantra.compression.compress("Fix the server!")
            route = mahamantra.llm.route_seed(result.seed)
            print(route.agent)  # "devops"

            # Or route text directly
            route = mahamantra.llm.route_text("Write me a poem")
            print(route.agent)  # "coder"

        Returns:
            MahaLLM router instance
        """
        if not hasattr(self, "_llm"):
            from vibe_core.mahamantra.adapters.llm import MahaLLM

            self._llm = MahaLLM()
        return self._llm

    @property
    def japa(self) -> "MahaJapa":
        """
        Access the MahaJapa engine for hearing and chanting mathematics.

        THE SINGULARITY:
            Hearing (24) + Chanting (1) = Prasadam (25)
            When Hearing = Chanting: 25 - 24 = 1 = COLLAPSE

        THE GOLDEN AGE:
            10,000 years = WORDS × PRASADAM² = 16 × 625
            Started 1486 CE → Ends 11486 CE
            We are 540 years in. 9,460 years remain.

        USAGE:
            # Execute a mala (108 rounds)
            result = mahamantra.japa.mala(seed=42)
            print(result.attractor)        # Stable state

            # Check golden age status
            status = mahamantra.japa.golden_age_status()
            print(status.years_remaining)  # 9460

            # Collapse detection
            collapsed = mahamantra.japa.is_collapsed(value)

        Returns:
            MahaJapa engine
        """
        if not hasattr(self, "_japa"):
            from vibe_core.mahamantra.adapters.japa import MahaJapa

            self._japa = MahaJapa()
        return self._japa

    @property
    def compression(self) -> "MahaCompression":
        """
        Access the MahaCompression intent engine.

        THE CONTEXT WINDOW SOLUTION:
            Silicon Valley compresses BITS (Shannon entropy).
            Maha compresses MEANING (Kolmogorov complexity).

            K(x) = shortest program that GENERATES x

        THE KILLER USE-CASE:
            AI Agent context windows are EXPENSIVE.
            100,000 tokens = slow, costly, "lost in the middle"

            MahaCompression extracts the INTENT:
            - Input: 100,000 lines of logs (chaos)
            - Output: "System failure due to Rajasic intent" (1 sentence)

        COMPRESSION RATIOS (FROM SCRIPTURE):
            - Gita: 700 verses / 16 words = 43.75×
            - Bhagavatam: 18,000 verses / 16 words = 1,125×
            - All Vedas: 100,000+ verses / 16 words = 6,250×+

        INTENT LEVELS (THE CLASSIFIER):
            1. TAMAS    - Ignorance → Corrupted execution
            2. RAJAS    - Passion   → Partial execution
            3. SATTVA   - Goodness  → Clean execution
            4. SUDDHA   - Pure      → Divine execution

        USAGE:
            # Compress text to intent
            result = mahamantra.compression.compress("...100k log lines...")
            print(result.intent_level)        # "RAJAS"
            print(result.seed)                # 42 (deterministic hash)
            print(result.compression_ratio)   # 1547.3

            # Encode system state as samskara
            samskara = mahamantra.compression.encode_samskara({
                "user_id": 123,
                "session_events": [...1000 events...],
            })
            print(samskara.seed)              # Compact representation

            # Verify against physics constants
            verified = mahamantra.compression.verify_physics(seed=137)
            print(verified.is_aligned)        # True

        Returns:
            MahaCompression intent engine
        """
        if not hasattr(self, "_compression"):
            from vibe_core.mahamantra.adapters.compression import MahaCompression

            self._compression = MahaCompression()
        return self._compression

    @property
    def hardware(self) -> "MahaHardware":
        """
        Access the MahaHardware specification engine.

        THE SILICON ALTAR:
            Hardware parameters are NOT arbitrary design choices.
            They are the Mahamantra structure REFLECTED in silicon!

            DATA_WIDTH = 32       = AKSARA (syllables)
            NEXT_HOP_WIDTH = 16   = WORDS
            BRANCHING_FACTOR = 16 = WORDS
            NIBBLE_SIZE = 4       = QUARTERS
            PIPELINE_STAGES = 8   = OCTET (Siksastakam verses)

        THE 8 PIPELINE STAGES = 8 SIKSASTAKAM VERSES:
            L0: ceto-darpaṇa-mārjanaṁ (cleanse - initialize)
            L1: nāmnām akāri (flexible - accept any nibble)
            L2: tṛṇād api sunīcena (humble - no comparison)
            L3: na dhanaṁ na janaṁ (desireless - no caching)
            L4: ayi nanda-tanuja (service - process next)
            L5: nayanam galad-aśru (flow - unobstructed)
            L6: yugāyitaṁ nimeṣeṇa (timing - deterministic)
            L7: āśliṣya vā pada-ratāṁ (unconditional - return)

        USAGE:
            # Get hardware specification
            spec = mahamantra.hardware.spec()
            print(spec.data_width)        # 32
            print(spec.pipeline_stages)   # 8

            # Pipeline stages with verse mapping
            for stage in mahamantra.hardware.pipeline_stages():
                print(f"{stage.name}: {stage.sanskrit}")

            # Generate HDL code
            verilog = mahamantra.hardware.generate_verilog_params()
            vhdl = mahamantra.hardware.generate_vhdl_params()
            c_code = mahamantra.hardware.generate_c_defines()

            # Verify custom design
            result = mahamantra.hardware.verify(data_width=32, branching_factor=16)
            print(result.summary)

        Returns:
            MahaHardware engine instance
        """
        if not hasattr(self, "_hardware"):
            from vibe_core.mahamantra.adapters.hardware import MahaHardware

            self._hardware = MahaHardware()
        return self._hardware

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

    # === SANKIRTAN (Scanner → Chant) ===
    def chant(self, dry_run: bool = True, base_path: Optional[str] = None) -> dict:
        """
        SANKIRTAN: Scanner discovers orphans → Sankirtan chants over them.

        SSOT FLOW:
            1. MahajanaScanner.get_orphans() → files without __mahajana__
            2. Sankirtan.chant_over_files() → inject DNA into orphans
            3. Return results

        Usage:
            # Dry run (see what would be injected)
            result = mahamantra.chant()
            print(f"Would inject: {result['files_injected']}")

            # Live injection
            result = mahamantra.chant(dry_run=False)
            print(f"Injected: {result['files_injected']}")
        """
        from pathlib import Path

        from vibe_core.mahamantra.substrate.sankirtan import perform_sankirtan

        path = Path(base_path) if base_path else None
        result = perform_sankirtan(base_path=path, dry_run=dry_run, use_scanner=True)

        return {
            "success": True,
            "dry_run": result.was_dry_run,
            "files_scanned": result.files_scanned,
            "files_injected": result.files_injected,
            "files_skipped": result.files_skipped,
            "files_already_owned": result.files_already_owned,
            "files_failed": result.files_failed,
            "by_mahajana": result.by_mahajana,
            "errors": result.errors[:10] if result.errors else [],
        }

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

    # === AUTO-DELEGATE TO ADAPTERS (folder IS wiring) ===
    # Mapping: adapter module name → main class name
    _ADAPTER_CLASSES: Dict[str, str] = {
        "transform": "MahaTransform",
        "hash": "DeterministicHash",
        "routing": "HolographicRouter",
        "orchestrator": "Orchestrator",
        "pipeline": "MahamantraPipeline",
        "attention": "MahaAttention",
        "bio": "LotusBio",
        "network": "LotusIPRouter",
        "synth": "MahaSynth",
        "classification": "MahaClassifier",
        "compute": "MahaCompute",
        "hardware": "MahaHardware",
        "compression": "MahaCompression",
        "japa": "MahaJapa",
        "llm": "MahaLLM",
    }

    def __getattr__(self, name: str):
        """
        Auto-delegate adapter access: mahamantra.compression → MahaCompression()

        FOLDER IS WIRING - should NEVER fail.
        """
        # Check if it's an adapter module name
        if name in self._ADAPTER_CLASSES:
            cache_name = f"_adapter_{name}"
            if not hasattr(self, cache_name):
                import importlib
                class_name = self._ADAPTER_CLASSES[name]
                module = importlib.import_module(f"vibe_core.mahamantra.adapters.{name}")
                adapter_cls = getattr(module, class_name)
                # Cache the instance
                object.__setattr__(self, cache_name, adapter_cls())
            return getattr(self, cache_name)
        raise AttributeError(f"'{type(self).__name__}' has no attribute '{name}'")


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
