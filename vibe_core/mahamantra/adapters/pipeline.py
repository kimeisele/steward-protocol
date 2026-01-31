"""
MAHAMANTRA PIPELINE - The 4-Phase Architecture
===============================================

"catur-vidhā bhajante māṁ janāḥ sukṛtino 'rjuna"
"Four kinds of pious men render devotional service unto Me."
— Bhagavad Gita 7.16

THE 4 PHASES (from Mahamantra Quarters):
========================================

Q1: GENESIS  - "Hare Krishna Hare Krishna" - CREATION/INTENT
    Adapter: DeterministicHash (hash.py)
    Function: Determine the nature (guna/karma) of input
    Sampradaya: Brahma (creation lineage)

Q2: DHARMA   - "Krishna Krishna Hare Hare" - LAW/VALIDATION
    Adapter: MahaTransform (transform.py)
    Function: Process through 16-step algorithm, find attractor
    Sampradaya: Kumara (knowledge lineage)

Q3: KARMA    - "Hare Rama Hare Rama" - ACTION/ROUTING
    Adapter: HolographicRouter (routing.py)
    Function: Route to destination via O(1) lookup
    Sampradaya: Sri (service lineage)

Q4: MOKSHA   - "Rama Rama Hare Hare" - LIBERATION/COMPLETION
    Adapter: Orchestrator (orchestrator.py)
    Function: Complete the cycle, record result, build resonance
    Sampradaya: Rudra (transformation lineage)

THE PIPELINE:
=============
    INPUT → GENESIS(hash) → DHARMA(transform) → KARMA(route) → MOKSHA(complete) → OUTPUT

Each phase produces a result that feeds into the next phase.
The complete pipeline transforms raw input into a resonant output.

USAGE:
    from vibe_core.mahamantra import mahamantra

    # Execute full pipeline
    result = mahamantra.pipeline.execute("my input")

    # Or step by step
    intent = mahamantra.pipeline.genesis("my input")
    processed = mahamantra.pipeline.dharma(intent.hash_value)
    routed = mahamantra.pipeline.karma(processed.value)
    complete = mahamantra.pipeline.moksha(routed)
"""

# === MAHAJANA DECLARATION ===
__mahajana__ = "vyasa"
__position__ = 0
__genesis__ = "0xc1739dcf"  # GenesisByte: parampara % 37 == 0

from typing import Any, Final, Optional

from vibe_core.mahamantra.substrate.mahajana import Quarter, Sampradaya
from vibe_core.mahamantra.protocols._seed import (
    MAHA_QUANTUM,
    QUARTERS,
    WORDS,
)
from vibe_core.mahamantra.protocols.pipeline import (
    MahaPipelineProtocol,
    PipelineResult,
    GenesisResult,
    DharmaResult,
    KarmaResult,
    MokshaResult,
    PhaseSpec,
)


# =============================================================================
# PHASE METADATA
# =============================================================================

PHASE_SPECS: Final[dict[Quarter, PhaseSpec]] = {
    Quarter.GENESIS: PhaseSpec(
        quarter=Quarter.GENESIS,
        sampradaya=Sampradaya.BRAHMA,
        sounds="Hare Krishna Hare Krishna",
        positions=(1, 2, 3, 4),
        function="determine_intent",
        adapter_name="hash",
    ),
    Quarter.DHARMA: PhaseSpec(
        quarter=Quarter.DHARMA,
        sampradaya=Sampradaya.KUMARA,
        sounds="Krishna Krishna Hare Hare",
        positions=(5, 6, 7, 8),
        function="process_transform",
        adapter_name="transform",
    ),
    Quarter.KARMA: PhaseSpec(
        quarter=Quarter.KARMA,
        sampradaya=Sampradaya.SRI,
        sounds="Hare Rama Hare Rama",
        positions=(9, 10, 11, 12),
        function="route_action",
        adapter_name="router",
    ),
    Quarter.MOKSHA: PhaseSpec(
        quarter=Quarter.MOKSHA,
        sampradaya=Sampradaya.RUDRA,
        sounds="Rama Rama Hare Hare",
        positions=(13, 14, 15, 16),
        function="complete_cycle",
        adapter_name="orchestrator",
    ),
}

# Verify structure
assert len(PHASE_SPECS) == QUARTERS, f"Must have {QUARTERS} phases"


# =============================================================================
# THE PIPELINE
# =============================================================================

class MahamantraPipeline(MahaPipelineProtocol):
    """
    The 4-Phase Pipeline: Genesis → Dharma → Karma → Moksha

    Each phase is a quarter of the Mahamantra, mapped to an adapter.
    The pipeline can be executed as a whole or phase by phase.
    """

    _naga_flooded: bool = True
    _naga_gene: str = "mahamantra_pipeline"

    def __init__(self) -> None:
        # Lazy-load adapters to avoid circular imports
        self._hash = None
        self._transform = None
        self._router = None
        self._orchestrator = None

    @property
    def _get_hash(self):
        if self._hash is None:
            from vibe_core.mahamantra.adapters.hash import DeterministicHash
            self._hash = DeterministicHash()
        return self._hash

    @property
    def _get_transform(self):
        if self._transform is None:
            from vibe_core.mahamantra.adapters.transform import MahaTransform
            self._transform = MahaTransform()
        return self._transform

    @property
    def _get_router(self):
        if self._router is None:
            from vibe_core.mahamantra.adapters.routing import HolographicRouter
            self._router = HolographicRouter()
        return self._router

    @property
    def _get_orchestrator(self):
        if self._orchestrator is None:
            from vibe_core.mahamantra.adapters.orchestrator import Orchestrator
            self._orchestrator = Orchestrator()
        return self._orchestrator

    # =========================================================================
    # PHASE 1: GENESIS - Determine Intent
    # =========================================================================

    def genesis(self, value: Any) -> GenesisResult:
        """
        Phase 1: GENESIS - Determine the intent/nature of input.

        "Hare Krishna Hare Krishna" - Creation quarter.
        Maps input to quantum space through 7-lens hash.

        Args:
            value: Any input (string, int, bytes)

        Returns:
            GenesisResult with hash_value in [0, MAHA_QUANTUM)
        """
        analysis = self._get_hash.analyze(value)
        # Extract lens values as tuple of ints
        lens_values = tuple(lens.value for lens in analysis.lenses)
        return GenesisResult(
            input_value=value,
            hash_value=analysis.primary_hash,
            lens_scores=lens_values,
            quarter=Quarter.GENESIS,
            metrics={"lenses": len(lens_values), "bits": analysis.primary_hash.bit_length()},
        )

    # =========================================================================
    # PHASE 2: DHARMA - Process/Validate
    # =========================================================================

    def dharma(self, value: int) -> DharmaResult:
        """
        Phase 2: DHARMA - Process through 16-step transformation.

        "Krishna Krishna Hare Hare" - Law quarter.
        Applies the Maha algorithm to find the attractor.

        Args:
            value: Integer from Genesis phase

        Returns:
            DharmaResult with transformed value and attractor
        """
        compute_result = self._get_transform.compute(value)
        attractor_result = self._get_transform.find_attractor(value)
        return DharmaResult(
            input_value=value,
            output_value=compute_result.value,
            attractor=attractor_result.stable_value,
            steps=attractor_result.cycles_to_converge,
            quarter=Quarter.DHARMA,
            metrics={"algorithm": "maha_16", "converged": True},
        )

    # =========================================================================
    # PHASE 3: KARMA - Route/Execute
    # =========================================================================

    def karma(self, value: int, payload: Any = None) -> KarmaResult:
        """
        Phase 3: KARMA - Route to destination.

        "Hare Rama Hare Rama" - Action quarter.
        Uses O(1) holographic routing to dispatch value.

        Args:
            value: Integer key for routing
            payload: Optional payload to store

        Returns:
            KarmaResult with routing status
        """
        key = value % self._get_router.key_space
        if payload is not None:
            self._get_router.insert(key, payload)

        existing = self._get_router.get(key)
        return KarmaResult(
            key=key,
            value=existing if existing is not None else payload,
            routed=existing is not None or payload is not None,
            quarter=Quarter.KARMA,
            metrics={"key_space": self._get_router.key_space, "is_new": existing is None},
        )

    # =========================================================================
    # PHASE 4: MOKSHA - Complete/Release
    # =========================================================================

    def moksha(self, value: int) -> MokshaResult:
        """
        Phase 4: MOKSHA - Complete the cycle.

        "Rama Rama Hare Hare" - Liberation quarter.
        Records result in rhythmic orchestrator, builds resonance.

        Args:
            value: Integer seed for tick

        Returns:
            MokshaResult with beat, round, and resonance
        """
        tick_result = self._get_orchestrator.tick(value)
        return MokshaResult(
            input_value=value,
            beat=tick_result.beat,
            round_num=tick_result.round_num,
            resonance=tick_result.resonance,
            quarter=Quarter.MOKSHA,
            metrics={"tick_delta": tick_result.beat_delta},
        )

    # =========================================================================
    # FULL PIPELINE
    # =========================================================================

    def execute(self, value: Any) -> PipelineResult:
        """
        Execute the complete 4-phase pipeline.

        INPUT → GENESIS → DHARMA → KARMA → MOKSHA → OUTPUT

        Args:
            value: Any input value

        Returns:
            PipelineResult with all phase results
        """
        # Phase 1: Genesis - Determine intent
        genesis_result = self.genesis(value)

        # Phase 2: Dharma - Transform
        dharma_result = self.dharma(genesis_result.hash_value)

        # Phase 3: Karma - Route (store the full result)
        karma_result = self.karma(dharma_result.attractor, payload={
            "input": value,
            "hash": genesis_result.hash_value,
            "attractor": dharma_result.attractor,
        })

        # Phase 4: Moksha - Complete
        moksha_result = self.moksha(dharma_result.attractor)

        return PipelineResult(
            genesis=genesis_result,
            dharma=dharma_result,
            karma=karma_result,
            moksha=moksha_result,
            final_value=dharma_result.attractor,
            total_resonance=moksha_result.resonance,
        )

    def reset(self) -> None:
        """Reset all stateful components."""
        if self._orchestrator is not None:
            self._orchestrator.reset()
        if self._router is not None:
            # Create fresh router
            from vibe_core.mahamantra.adapters.routing import HolographicRouter
            self._router = HolographicRouter()

    def get_phase_spec(self, quarter: Quarter) -> PhaseSpec:
        """Get specification for a phase."""
        return PHASE_SPECS[quarter]

    def describe(self) -> dict:
        """Describe the pipeline structure."""
        return {
            "phases": QUARTERS,
            "total_positions": WORDS,
            "quantum_space": MAHA_QUANTUM,
            "phase_details": {
                q.value: {
                    "sounds": spec.sounds,
                    "positions": spec.positions,
                    "adapter": spec.adapter_name,
                    "function": spec.function,
                    "sampradaya": spec.sampradaya.value,
                }
                for q, spec in PHASE_SPECS.items()
            },
        }


# =============================================================================
# SINGLETON INSTANCE
# =============================================================================

_pipeline_instance: Optional[MahamantraPipeline] = None


def get_pipeline() -> MahamantraPipeline:
    """Get or create the pipeline singleton."""
    global _pipeline_instance
    if _pipeline_instance is None:
        _pipeline_instance = MahamantraPipeline()
    return _pipeline_instance


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "MahamantraPipeline",
    "PipelineResult",
    "GenesisResult",
    "DharmaResult",
    "KarmaResult",
    "MokshaResult",
    "PhaseSpec",
    "PHASE_SPECS",
    "get_pipeline",
]
