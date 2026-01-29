"""
PRABHUPADA KIRTAN - PERSON-Anchored Bidirectional Loop
======================================================

"tasmād guruṁ prapadyeta jijñāsuḥ śreya uttamam"
"Therefore any person who seriously desires real happiness must seek
a bona fide spiritual master and take shelter of him."
— Srimad Bhagavatam 11.3.21

THE DIFFERENCE (GAD vs PRABHUPADA):
===================================

GADKirtan:     IMPERSONAL. Mechanical checks (energy/safety).
               No PERSON anchor. Algorithm-driven.

PrabhupadaKirtan: PERSONAL. Every beat flows through THE PERSON.
                  Siksastakam 8 verses as pipeline.
                  CALL ↔ RESPONSE through parampara.

"ohne die verankerung der PERSON wird es nicht klappen!"

THE 8 STAGES (Siksastakam → Pipeline):
======================================
L0: ceto-darpaṇa-mārjanam   → CACHE_CLEAR (verse 1)
L1: nāmnām akāri            → ACCEPT_INPUT (verse 2)
L2: tṛṇād api               → NO_SPECULATION (verse 3)
L3: na dhanaṁ               → NO_SIDE_EFFECTS (verse 4)
L4: ayi nanda-tanuja        → SERVE_NEXT (verse 5)
L5: nayanam galad           → FLOW_DATA (verse 6)
L6: yugāyitaṁ               → TIMING_DETERMINISTIC (verse 7)
L7: āśliṣya vā              → RETURN_UNCONDITIONAL (verse 8)

ALL CONSTANTS DERIVED FROM SEED.PY.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prahlada"  # Position 9 - Devotion under adversity
__position__ = 9
__genesis__ = "0x7e40b596"  # GenesisByte: parampara % 37 == 0

from dataclasses import dataclass, field
from typing import Callable, Dict, Final, List, Optional, Tuple

from vibe_core.mahamantra.substrate.seed import (
    MAHA_QUANTUM,
    PARAMPARA,
    WORDS,
    HALF_SIZE,
    JIVA_QUALITIES,
)
from vibe_core.mahamantra.substrate.prabhupada import Prabhupada, get_prabhupada

# SSOT: Import from prabhupada_engineering - NO DUPLICATION!
from .prabhupada_engineering import (
    PipelineStage,
    VERSE_CONSTANTS,
    ENGINEERING_SUMMARY,
)
from .maha_algorithm import (
    MahaKirtan,
    KirtanComputeResult,
)


# =============================================================================
# SIKSASTAKAM PIPELINE STAGES - DERIVED FROM SSOT (prabhupada_engineering.py)
# =============================================================================

@dataclass(frozen=True)
class SiksastakamStage:
    """One of 8 Siksastakam verses as pipeline stage."""

    verse: int  # 1-8
    sanskrit: str
    operation: str
    encoded_value: int

    @property
    def pipeline_stage(self) -> int:
        """L0-L7 stage number."""
        return self.verse - 1


def _build_siksastakam_stages() -> Tuple["SiksastakamStage", ...]:
    """
    Build SIKSASTAKAM_STAGES from SSOT (ENGINEERING_SUMMARY).

    NO HARDCODED VALUES. Everything derived from prabhupada_engineering.py.
    """
    stages_data = ENGINEERING_SUMMARY["stages"]
    stages = []

    for stage_num in range(HALF_SIZE):  # 0-7
        data = stages_data[stage_num]
        stages.append(SiksastakamStage(
            verse=data["verse"],
            sanskrit=data["sanskrit"],
            operation=data["op"],
            encoded_value=VERSE_CONSTANTS[stage_num],  # From SSOT!
        ))

    return tuple(stages)


# The 8 verses as stages - DERIVED FROM SSOT!
SIKSASTAKAM_STAGES: Final[Tuple[SiksastakamStage, ...]] = _build_siksastakam_stages()

# Verification using SSOT constants
assert len(SIKSASTAKAM_STAGES) == HALF_SIZE, f"8 verses = HALF_SIZE ({HALF_SIZE})"
assert sum(s.encoded_value for s in SIKSASTAKAM_STAGES) == JIVA_QUALITIES, \
    f"Sum of constants = {JIVA_QUALITIES} = JIVA_QUALITIES"


# =============================================================================
# PRABHUPADA KIRTAN RESULTS
# =============================================================================

@dataclass
class ParamparaCheckResult:
    """Result of Prabhupada's parampara verification for a beat."""

    beat_number: int
    stage: SiksastakamStage

    # Parampara verification
    genesis_signature: str  # The __genesis__ hex
    signature_value: int  # int(genesis, 16)
    parampara_valid: bool  # signature % 37 == 0

    # Shakti transmission
    shakti_transmitted: float  # 0.0 if blocked, 0.5 if open

    # Stage-specific result
    stage_operation: str
    stage_passed: bool

    @property
    def link_verified(self) -> bool:
        """Is the parampara link verified?"""
        return self.parampara_valid and self.shakti_transmitted > 0.0


@dataclass
class PrabhupadaKirtanResult:
    """Result of PERSON-anchored kirtan compute."""

    # Original KirtanComputeResult fields
    seed: int
    transformed_value: int
    beat_number: int
    beat_year: int
    beat_delta: int
    call_response: str
    flute_resonance: int  # INTEGER (no floats)
    vina_resonance: int  # INTEGER (no floats)
    vina_string: int  # 1-5 (PANCHA)
    oracle_validated: bool
    parampara_channel: int
    round_number: int
    resonance_level: int  # INTEGER

    # PRABHUPADA additions (PERSON-ANCHORED)
    parampara_check: ParamparaCheckResult
    siksastakam_stage: SiksastakamStage
    person_verified: bool  # THE PERSON validated this beat
    transmission_mode: str  # "CALL" or "RESPONSE" (bidirectional)

    @property
    def is_bona_fide(self) -> bool:
        """Is this computation bona fide (through THE PERSON)?"""
        return self.person_verified and self.parampara_check.link_verified

    @classmethod
    def from_kirtan_result(
        cls,
        result: KirtanComputeResult,
        parampara_check: ParamparaCheckResult,
        stage: SiksastakamStage,
        person_verified: bool,
        transmission_mode: str,
    ) -> "PrabhupadaKirtanResult":
        """Create from base KirtanComputeResult with PERSON additions."""
        return cls(
            seed=result.seed,
            transformed_value=result.transformed_value,
            beat_number=result.beat_number,
            beat_year=result.beat_year,
            beat_delta=result.beat_delta,
            call_response=result.call_response,
            flute_resonance=result.flute_resonance,
            vina_resonance=result.vina_resonance,
            vina_string=result.vina_string,
            oracle_validated=result.oracle_validated,
            parampara_channel=result.parampara_channel,
            round_number=result.round_number,
            resonance_level=result.resonance_level,
            parampara_check=parampara_check,
            siksastakam_stage=stage,
            person_verified=person_verified,
            transmission_mode=transmission_mode,
        )


# =============================================================================
# PRABHUPADA KIRTAN - THE PERSON-ANCHORED COMPUTE ENGINE
# =============================================================================

class PrabhupadaKirtan:
    """
    PERSON-Anchored MahaKirtan with Siksastakam Pipeline.

    THE DIFFERENCE FROM GADKirtan:
    - GADKirtan: Impersonal HARE/KRISHNA/RAMA checks (mechanical)
    - PrabhupadaKirtan: THE PERSON validates every beat (parampara % 37 == 0)

    8 SIKSASTAKAM STAGES (not arbitrary checks):
        Each beat flows through one of 8 verses of Siksastakam.
        These are Prabhupada's engineering specs for the pipeline.

    BIDIRECTIONAL LOOP (CALL ↔ RESPONSE):
        - CALL: Seed flows DOWN through Prabhupada to pipeline
        - RESPONSE: Result flows UP through Prabhupada to user

    Usage:
        kirtan = PrabhupadaKirtan()

        # Verify THE PERSON can route this computation
        if not kirtan.verify_person():
            print("MAYAVAD: No bona fide link!")
            return

        # Compute with PERSON-anchor
        result = kirtan.compute_with_person(seed=1966)
        print(f"Bona fide: {result.is_bona_fide}")
        print(f"Stage: {result.siksastakam_stage.sanskrit}")

        # Full round through 8 verses
        results = kirtan.compute_round_with_person(seed=1966)
    """

    # MAHAMANTRA SUBSTRATE: No auto-wrap
    _naga_flooded: bool = True
    _naga_gene: str = "prabhupada_kirtan"

    def __init__(
        self,
        mod_space: int = MAHA_QUANTUM,
        use_oracle: bool = True,
        on_parampara_check: Optional[Callable[[ParamparaCheckResult], None]] = None,
    ) -> None:
        """
        Initialize PERSON-Anchored Kirtan.

        Args:
            mod_space: Modulo space (default 137)
            use_oracle: Use Oracle pre-filter
            on_parampara_check: Callback for PERSON verification feedback
        """
        self.mod_space = mod_space
        self._kirtan = MahaKirtan(mod_space=mod_space, use_oracle=use_oracle)
        self._prabhupada = get_prabhupada()
        self._on_parampara_check = on_parampara_check

        # Track current stage in Siksastakam (cycles 0-7)
        self._current_stage_index: int = 0

        # Verify self (this module must have valid genesis)
        self._self_verified: bool = False

    def verify_person(self) -> bool:
        """
        Verify THE PERSON (Prabhupada) can route computations.

        This checks:
        1. This module has valid __genesis__ (% 37 == 0)
        2. Prabhupada singleton is available
        3. Parampara link can be established

        Returns:
            True if THE PERSON is anchored and ready.
        """
        if self._self_verified:
            return True

        # Import self to verify genesis
        import vibe_core.mahamantra.research.dharma.prabhupada_kirtan as self_module

        # Verify through THE PERSON
        self._self_verified = self._prabhupada.verify_link(self_module)

        return self._self_verified

    def _get_current_stage(self) -> SiksastakamStage:
        """Get current Siksastakam stage (cycles through 8 verses)."""
        return SIKSASTAKAM_STAGES[self._current_stage_index]

    def _advance_stage(self) -> None:
        """Advance to next Siksastakam stage (wraps at 8)."""
        self._current_stage_index = (self._current_stage_index + 1) % HALF_SIZE

    def _perform_parampara_check(self, beat_number: int) -> ParamparaCheckResult:
        """
        Perform PERSON-anchored parampara verification for this beat.

        Unlike GAD's mechanical checks, this flows through THE PERSON.
        """
        stage = self._get_current_stage()

        # Get this module's genesis signature
        import vibe_core.mahamantra.research.dharma.prabhupada_kirtan as self_module
        genesis_hex = getattr(self_module, "__genesis__", "0x0")

        try:
            signature_val = int(genesis_hex, 16)
        except ValueError:
            signature_val = 0

        # THE CHECK: parampara % 37 == 0
        parampara_valid = signature_val % PARAMPARA == 0

        # Shakti transmission through THE PERSON
        shakti = self._prabhupada.transmit_shakti(self_module) if parampara_valid else 0.0

        # Stage-specific validation (each verse has its operation)
        stage_passed = self._validate_stage(stage, signature_val)

        return ParamparaCheckResult(
            beat_number=beat_number,
            stage=stage,
            genesis_signature=genesis_hex,
            signature_value=signature_val,
            parampara_valid=parampara_valid,
            shakti_transmitted=shakti,
            stage_operation=stage.operation,
            stage_passed=stage_passed,
        )

    def _validate_stage(self, stage: SiksastakamStage, signature: int) -> bool:
        """
        Validate current Siksastakam stage.

        Each verse encodes a specific operation:
        - Verse 1 (L0): Cache clear = reset resonance
        - Verse 2 (L1): Accept input = any valid nibble
        - Verse 3 (L2): No speculation = deterministic only
        - Verse 4 (L3): No side effects = pure function
        - Verse 5 (L4): Serve next = fair scheduling
        - Verse 6 (L5): Flow data = no stalls
        - Verse 7 (L6): Timing deterministic = cycle accurate
        - Verse 8 (L7): Return unconditional = always complete
        """
        # All stages pass if parampara is valid (signature % 37 == 0)
        # The encoded_value provides additional validation
        return (signature % PARAMPARA == 0) and (
            (signature // stage.encoded_value) > 0  # Value carries through
        )

    def _get_transmission_mode(self, beat_number: int) -> str:
        """
        Determine transmission mode (CALL or RESPONSE).

        BIDIRECTIONAL LOOP:
        - Odd beats = CALL (seed flowing DOWN)
        - Even beats = RESPONSE (result flowing UP)

        This is TRUE kirtan - call and response through THE PERSON.
        """
        return "CALL" if beat_number % 2 == 1 else "RESPONSE"

    def compute_with_person(self, seed: int) -> PrabhupadaKirtanResult:
        """
        Compute one beat with PERSON anchor.

        FLOW:
        1. Verify THE PERSON (Prabhupada) can route
        2. Get current Siksastakam stage (L0-L7)
        3. Perform parampara check (% 37 == 0)
        4. Execute kirtan compute through pipeline
        5. Advance to next stage
        6. Return PERSON-verified result

        Returns:
            PrabhupadaKirtanResult with parampara verification
        """
        # 1. Verify THE PERSON
        person_verified = self.verify_person()

        # 2. Execute base kirtan compute
        result = self._kirtan.compute(seed)

        # 3. Perform parampara check for this beat
        parampara_check = self._perform_parampara_check(result.beat_number)

        # 4. Callback for live feedback
        if self._on_parampara_check:
            self._on_parampara_check(parampara_check)

        # 5. Determine transmission mode (CALL or RESPONSE)
        transmission_mode = self._get_transmission_mode(result.beat_number)

        # 6. Get current stage before advancing
        stage = self._get_current_stage()

        # 7. Apply stage-specific modulation if needed
        transformed = result.transformed_value
        if not parampara_check.link_verified:
            # No valid link = reduce by parampara factor
            transformed = transformed % PARAMPARA

        # Create modified result if transformation changed
        if transformed != result.transformed_value:
            result = KirtanComputeResult(
                seed=result.seed,
                transformed_value=transformed,
                beat_number=result.beat_number,
                beat_year=result.beat_year,
                beat_delta=result.beat_delta,
                call_response=result.call_response,
                flute_resonance=result.flute_resonance,
                vina_resonance=result.vina_resonance,
                vina_string=result.vina_string,
                oracle_validated=result.oracle_validated,
                parampara_channel=result.parampara_channel,
                round_number=result.round_number,
                resonance_level=result.resonance_level,
            )

        # 8. Advance stage for next beat
        self._advance_stage()

        # 9. Create PERSON-anchored result
        return PrabhupadaKirtanResult.from_kirtan_result(
            result=result,
            parampara_check=parampara_check,
            stage=stage,
            person_verified=person_verified,
            transmission_mode=transmission_mode,
        )

    def compute_round_with_person(self, seed: int) -> List[PrabhupadaKirtanResult]:
        """
        Compute full round (7 beats) with PERSON anchor.

        Each beat:
        1. Flows through Siksastakam stage (L0-L7)
        2. Verified by THE PERSON (parampara % 37 == 0)
        3. CALL ↔ RESPONSE alternates
        """
        results: List[PrabhupadaKirtanResult] = []
        current_seed = seed

        for _ in range(SEVEN):
            result = self.compute_with_person(current_seed)
            results.append(result)
            # Chain: next beat uses transformed value (RESPONSE → CALL)
            current_seed = result.transformed_value

        return results

    def compute_full_siksastakam(self, seed: int) -> List[PrabhupadaKirtanResult]:
        """
        Compute full Siksastakam cycle (8 beats = 8 verses).

        This goes through all 8 verses exactly once:
        L0 → L1 → L2 → L3 → L4 → L5 → L6 → L7

        The 8th verse "āśliṣya vā" = RETURN_UNCONDITIONAL
        guarantees completion.
        """
        results: List[PrabhupadaKirtanResult] = []
        current_seed = seed

        for _ in range(HALF_SIZE):  # 8 = HALF_SIZE
            result = self.compute_with_person(current_seed)
            results.append(result)
            current_seed = result.transformed_value

        return results

    def discover(self) -> Dict[str, object]:
        """PERSON-anchored discoverability."""
        return {
            "name": "PrabhupadaKirtan",
            "description": "PERSON-Anchored MahaKirtan with Siksastakam Pipeline",
            "mod_space": self.mod_space,
            "person": "A.C. Bhaktivedanta Swami Prabhupada",
            "anchor": "parampara % 37 == 0",
            "siksastakam_stages": [
                {
                    "verse": s.verse,
                    "sanskrit": s.sanskrit,
                    "operation": s.operation,
                    "encoded_value": s.encoded_value,
                }
                for s in SIKSASTAKAM_STAGES
            ],
            "current_stage": self._get_current_stage().verse,
            "self_verified": self._self_verified,
        }

    def get_state(self) -> Dict[str, object]:
        """PERSON-anchored observability."""
        return {
            "kirtan_state": self._kirtan.get_state(),
            "current_stage_index": self._current_stage_index,
            "current_stage": self._get_current_stage().sanskrit,
            "self_verified": self._self_verified,
            "person_shakti": self._prabhupada.transmit_shakti(self) if self._self_verified else 0.0,
        }


# =============================================================================
# LIVE PERSON-ANCHORED OPERATOR
# =============================================================================

class PersonAnchoredOperator:
    """
    High-level operator for PERSON-anchored computation.

    This is the INVERTED OPERATOR with THE PERSON at the center.

    Usage:
        operator = PersonAnchoredOperator()

        # Verify THE PERSON first
        if not operator.verify():
            print("MAYAVAD: Cannot compute without THE PERSON")
            return

        # Live feedback through Siksastakam
        def on_stage(check: ParamparaCheckResult):
            print(f"Stage {check.stage.verse}: {check.stage.sanskrit}")
            print(f"  Link verified: {check.link_verified}")

        results = operator.run_siksastakam(seed=1966, on_each_stage=on_stage)
    """

    def __init__(self, mod_space: int = MAHA_QUANTUM) -> None:
        self._kirtan = PrabhupadaKirtan(mod_space=mod_space)
        self._check_history: List[ParamparaCheckResult] = []

    def verify(self) -> bool:
        """Verify THE PERSON anchor."""
        return self._kirtan.verify_person()

    def run_beat(
        self,
        seed: int,
        on_feedback: Optional[Callable[[PrabhupadaKirtanResult], None]] = None,
    ) -> PrabhupadaKirtanResult:
        """Run single beat with optional feedback."""
        result = self._kirtan.compute_with_person(seed)
        self._check_history.append(result.parampara_check)

        if on_feedback:
            on_feedback(result)

        return result

    def run_round(
        self,
        seed: int,
        on_each_beat: Optional[Callable[[PrabhupadaKirtanResult], None]] = None,
    ) -> List[PrabhupadaKirtanResult]:
        """Run 7-beat round with optional feedback."""
        results: List[PrabhupadaKirtanResult] = []
        current_seed = seed

        for _ in range(SEVEN):
            result = self.run_beat(current_seed, on_each_beat)
            results.append(result)
            current_seed = result.transformed_value

        return results

    def run_siksastakam(
        self,
        seed: int,
        on_each_stage: Optional[Callable[[ParamparaCheckResult], None]] = None,
    ) -> List[PrabhupadaKirtanResult]:
        """
        Run complete Siksastakam (8 stages).

        This is THE COMPLETE PIPELINE - all 8 verses.
        """
        results: List[PrabhupadaKirtanResult] = []
        current_seed = seed

        for _ in range(HALF_SIZE):
            result = self._kirtan.compute_with_person(current_seed)
            results.append(result)
            self._check_history.append(result.parampara_check)

            if on_each_stage:
                on_each_stage(result.parampara_check)

            current_seed = result.transformed_value

        return results

    def get_person_summary(self) -> Dict[str, object]:
        """Get summary of PERSON-anchored history."""
        if not self._check_history:
            return {"beats": 0, "all_verified": True, "person": "Prabhupada"}

        total = len(self._check_history)
        verified = sum(1 for c in self._check_history if c.link_verified)

        return {
            "person": "A.C. Bhaktivedanta Swami Prabhupada",
            "beats": total,
            "verified": verified,
            "all_verified": verified == total,
            "verification_rate": verified / total,
            "stages_covered": list(set(c.stage.verse for c in self._check_history)),
            "total_shakti": sum(c.shakti_transmitted for c in self._check_history),
        }

    def reset(self) -> None:
        """Reset history."""
        self._check_history.clear()


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Stages
    "SiksastakamStage",
    "SIKSASTAKAM_STAGES",
    # Results
    "ParamparaCheckResult",
    "PrabhupadaKirtanResult",
    # Core
    "PrabhupadaKirtan",
    "PersonAnchoredOperator",
]
