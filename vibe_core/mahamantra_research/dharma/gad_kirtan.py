"""
GAD KIRTAN - Live Feedback Operator Inversion
==============================================

"idaṁ śarīraṁ kaunteya kṣetram ity abhidhīyate"
"This body, O son of Kunti, is called the field."
— Bhagavad Gita 13.2

GAD-000 OPERATOR INVERSION:
If it does not exist as protocol, it does not exist.

This module implements TRUE operator inversion:
- Each compute beat triggers MantraHeartbeat checks
- GAD checks MODULATE synth parameters in real-time
- Live feedback exchange between operator and computation

THE MAPPING (7 beats ↔ 16 words):
=================================
Beat 1: HARE KRISHNA     (words 0-1)   → Energy + Source check
Beat 2: HARE KRISHNA     (words 2-3)   → Energy + Source check
Beat 3: KRISHNA KRISHNA  (words 4-5)   → Source + Source check
Beat 4: HARE HARE        (words 6-7)   → Energy + Energy check
Beat 5: HARE RAMA        (words 8-9)   → Energy + Safety check
Beat 6: HARE RAMA        (words 10-11) → Energy + Safety check
Beat 7: RAMA RAMA HARE HARE (12-15)    → Safety + Safety + Energy + Energy

FEEDBACK MODULATION:
====================
- HARE check (energy) → if fails, reduce feedback (preserve energy)
- KRISHNA check (always passes) → confirms transform validity
- RAMA check (safety) → if fails, apply safety modulo

ALL CONSTANTS DERIVED FROM SEED.PY.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prahlada"
__position__ = 9
__genesis__ = "0x9f5278d7"  # GenesisByte: parampara % 37 == 0

from dataclasses import dataclass, field
from typing import Callable, Dict, Final, List, Optional, Tuple

from vibe_core.mahamantra.protocols._gad import (
    GADBase,
    GADCriterion,
    HolyName,
    JapaState,
    MantraHeartbeat,
)
from vibe_core.mahamantra.substrate.seed import (
    MAHA_QUANTUM,
    PARAMPARA,
    SEVEN,
    WORDS,
)

from vibe_core.mahamantra.substrate.mantra import (
    KirtanComputeResult,
    MahaKirtan,
)
from vibe_core.mahamantra.substrate.mantra.siksastakam import CHAITANYA_512_B
from vibe_core.mahamantra.substrate.algorithm.maha import (
    SYNTH_PRESETS,
    MahaSynthParams,
)

# =============================================================================
# BEAT-TO-WORD MAPPING (Derived from structure)
# =============================================================================

# Each beat covers approximately 16/7 ≈ 2.3 words
# We map beats to word ranges that align with the Mahamantra quarters

BEAT_WORD_RANGES: Final[Dict[int, Tuple[int, int]]] = {
    1: (0, 2),  # HARE KRISHNA
    2: (2, 4),  # HARE KRISHNA
    3: (4, 6),  # KRISHNA KRISHNA
    4: (6, 8),  # HARE HARE
    5: (8, 10),  # HARE RAMA
    6: (10, 12),  # HARE RAMA
    7: (12, 16),  # RAMA RAMA HARE HARE (4 words for completeness)
}

# Pre-computed word types per beat (derived from MantraHeartbeat.MAHAMANTRA_SEQUENCE)
BEAT_WORD_TYPES: Final[Dict[int, Tuple[HolyName, ...]]] = {
    1: (HolyName.HARE, HolyName.KRISHNA),
    2: (HolyName.HARE, HolyName.KRISHNA),
    3: (HolyName.KRISHNA, HolyName.KRISHNA),
    4: (HolyName.HARE, HolyName.HARE),
    5: (HolyName.HARE, HolyName.RAMA),
    6: (HolyName.HARE, HolyName.RAMA),
    7: (HolyName.RAMA, HolyName.RAMA, HolyName.HARE, HolyName.HARE),
}


# =============================================================================
# GAD CHECK RESULTS - Live Feedback Data
# =============================================================================


@dataclass
class GADCheckResult:
    """Result of GAD checks for a beat."""

    beat_number: int
    words_chanted: Tuple[HolyName, ...]

    # Individual check results
    hare_checks: List[bool]  # Energy checks (can fail)
    krishna_checks: List[bool]  # Source checks (always True)
    rama_checks: List[bool]  # Safety checks (can fail)

    # Aggregated
    energy_ok: bool  # All HARE checks passed
    source_ok: bool  # All KRISHNA checks passed (always True)
    safety_ok: bool  # All RAMA checks passed

    # Feedback modulation values (derived)
    feedback_modifier: float  # 0.0-1.0, reduces if energy fails
    safety_modifier: float  # 0.0-1.0, reduces if safety fails

    @property
    def all_checks_passed(self) -> bool:
        """Did all checks pass?"""
        return self.energy_ok and self.source_ok and self.safety_ok

    @property
    def modulation_factor(self) -> float:
        """Combined modulation factor (0.0-1.0)."""
        return self.feedback_modifier * self.safety_modifier


@dataclass
class GADKirtanResult:
    """Result of GAD-integrated kirtan compute."""

    # Original KirtanComputeResult fields
    seed: int
    transformed_value: int
    beat_number: int
    beat_year: int
    beat_delta: int
    call_response: str
    flute_resonance: float
    oracle_validated: bool
    parampara_channel: int
    round_number: int
    resonance_level: float

    # GAD additions
    gad_check: GADCheckResult
    japa_state: JapaState
    words_chanted_total: int
    modulated_by_gad: bool  # Was transform affected by GAD?

    @classmethod
    def from_kirtan_result(
        cls,
        result: KirtanComputeResult,
        gad_check: GADCheckResult,
        japa_state: JapaState,
        words_chanted_total: int,
        modulated: bool,
    ) -> "GADKirtanResult":
        """Create from KirtanComputeResult with GAD additions."""
        return cls(
            seed=result.seed,
            transformed_value=result.transformed_value,
            beat_number=result.beat_number,
            beat_year=result.beat_year,
            beat_delta=result.beat_delta,
            call_response=result.call_response,
            flute_resonance=result.flute_resonance,
            oracle_validated=result.oracle_validated,
            parampara_channel=result.parampara_channel,
            round_number=result.round_number,
            resonance_level=result.resonance_level,
            gad_check=gad_check,
            japa_state=japa_state,
            words_chanted_total=words_chanted_total,
            modulated_by_gad=modulated,
        )


# =============================================================================
# GAD KIRTAN - The Live Feedback Compute Engine
# =============================================================================


class GADKirtan(GADBase):
    """
    GAD-integrated MahaKirtan with live feedback.

    OPERATOR INVERSION:
    - Each beat advances the MantraHeartbeat
    - GAD checks (HARE/KRISHNA/RAMA) modulate computation
    - Real-time feedback exchange

    Usage:
        gad_kirtan = GADKirtan()

        # Compute with live feedback
        result = gad_kirtan.compute_with_gad(seed=1966)
        print(f"GAD checks passed: {result.gad_check.all_checks_passed}")
        print(f"Modulated: {result.modulated_by_gad}")

        # Full round with feedback
        results = gad_kirtan.compute_round_with_gad(seed=1966)
        for r in results:
            print(f"Beat {r.beat_number}: {r.gad_check.energy_ok}")
    """

    # MAHAMANTRA SUBSTRATE: No auto-wrap
    _naga_flooded: bool = True
    _naga_gene: str = "gad_kirtan"

    def __init__(
        self,
        mod_space: int = MAHA_QUANTUM,
        use_oracle: bool = True,
        on_gad_check: Optional[Callable[[GADCheckResult], None]] = None,
    ) -> None:
        """
        Initialize GAD Kirtan.

        Args:
            mod_space: Modulo space (default 137)
            use_oracle: Use Oracle pre-filter
            on_gad_check: Callback for live GAD check feedback
        """
        super().__init__()  # Initialize GADBase with MantraHeartbeat

        self.mod_space = mod_space
        self._kirtan = MahaKirtan(mod_space=mod_space, use_oracle=use_oracle)
        self._on_gad_check = on_gad_check

        # Energy and safety check implementations (can be overridden)
        self._energy_check: Callable[[], bool] = lambda: True
        self._safety_check: Callable[[], bool] = lambda: True

    def set_energy_check(self, check: Callable[[], bool]) -> None:
        """Set custom energy check (HARE)."""
        self._energy_check = check

    def set_safety_check(self, check: Callable[[], bool]) -> None:
        """Set custom safety check (RAMA)."""
        self._safety_check = check

    def _check_hare(self) -> bool:
        """HARE = Energy check. Override from MantraHeartbeat."""
        return self._energy_check()

    def _check_rama(self) -> bool:
        """RAMA = Safety check. Override from MantraHeartbeat."""
        return self._safety_check()

    def _perform_beat_checks(self, beat_number: int) -> GADCheckResult:
        """
        Perform GAD checks for a beat.

        Advances MantraHeartbeat by the words in this beat,
        collecting check results.
        """
        word_types = BEAT_WORD_TYPES.get(beat_number, (HolyName.HARE,))

        hare_checks: List[bool] = []
        krishna_checks: List[bool] = []
        rama_checks: List[bool] = []

        # Chant each word in the beat
        for word in word_types:
            # Manually perform the check for this word type
            if word == HolyName.HARE:
                check_result = self._check_hare()
                hare_checks.append(check_result)
            elif word == HolyName.KRISHNA:
                check_result = True  # KRISHNA always passes (acintya)
                krishna_checks.append(check_result)
            elif word == HolyName.RAMA:
                check_result = self._check_rama()
                rama_checks.append(check_result)

            # Advance the heartbeat
            self._heartbeat.chant_word()

        # Compute aggregates
        energy_ok = all(hare_checks) if hare_checks else True
        source_ok = all(krishna_checks) if krishna_checks else True
        safety_ok = all(rama_checks) if rama_checks else True

        # Compute modulation factors
        # Energy failure → reduce feedback (preserve resources)
        feedback_modifier = 1.0 if energy_ok else 0.5
        # Safety failure → apply safety modulo
        safety_modifier = 1.0 if safety_ok else 0.7

        return GADCheckResult(
            beat_number=beat_number,
            words_chanted=word_types,
            hare_checks=hare_checks,
            krishna_checks=krishna_checks,
            rama_checks=rama_checks,
            energy_ok=energy_ok,
            source_ok=source_ok,
            safety_ok=safety_ok,
            feedback_modifier=feedback_modifier,
            safety_modifier=safety_modifier,
        )

    def compute_with_gad(self, seed: int) -> GADKirtanResult:
        """
        Compute one beat with GAD live feedback.

        1. Execute kirtan compute FIRST (to get actual beat number)
        2. Perform GAD checks for the beat
        3. Apply modulation to result if needed
        4. Return combined result
        """
        # Execute kirtan compute FIRST to get actual beat number
        result = self._kirtan.compute(seed)

        # Now perform GAD checks for THIS beat
        gad_check = self._perform_beat_checks(result.beat_number)

        # Callback for live feedback
        if self._on_gad_check:
            self._on_gad_check(gad_check)

        # Determine if we need to modulate
        modulated = not gad_check.all_checks_passed

        # If modulated, adjust the transformed value
        transformed = result.transformed_value
        if modulated:
            # Apply modulation factor to result
            factor = gad_check.modulation_factor
            transformed = int(transformed * factor) % self.mod_space

        # Create modified result if needed
        if modulated:
            # Create new result with modulated value
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

        # Create combined result
        return GADKirtanResult.from_kirtan_result(
            result=result,
            gad_check=gad_check,
            japa_state=self._heartbeat.state,
            words_chanted_total=self._heartbeat.total_words,
            modulated=modulated,
        )

    def compute_round_with_gad(self, seed: int) -> List[GADKirtanResult]:
        """
        Compute full round (7 beats) with GAD live feedback.

        Each beat:
        1. GAD checks modulate the computation
        2. Result feeds into next beat
        3. Live feedback for each step
        """
        results: List[GADKirtanResult] = []
        current_seed = seed

        for _ in range(SEVEN):
            result = self.compute_with_gad(current_seed)
            results.append(result)
            # Chain: next beat uses transformed value
            current_seed = result.transformed_value

        return results

    def discover(self) -> Dict[str, object]:
        """GAD discoverability."""
        return {
            "name": "GADKirtan",
            "description": "GAD-integrated MahaKirtan with live feedback",
            "mod_space": self.mod_space,
            "beat_word_mapping": {k: [w.name for w in v] for k, v in BEAT_WORD_TYPES.items()},
            "heartbeat_state": self._heartbeat.get_summary(),
            "operator_inversion": True,
        }

    def get_state(self) -> Dict[str, object]:
        """GAD observability."""
        return {
            "kirtan_state": self._kirtan.get_state(),
            "heartbeat": self._heartbeat.get_summary(),
            "japa_state": self._heartbeat.state.name,
            "words_chanted": self._heartbeat.total_words,
            "malas_complete": self._heartbeat.mala_count,
        }


# =============================================================================
# LIVE FEEDBACK OPERATOR
# =============================================================================


class LiveFeedbackOperator:
    """
    High-level operator for live GAD feedback computing.

    This is the INVERTED OPERATOR - receives feedback, adjusts in real-time.

    Usage:
        operator = LiveFeedbackOperator()

        # Set custom checks
        operator.set_energy_check(lambda: check_memory_usage() < 0.8)
        operator.set_safety_check(lambda: not is_in_error_state())

        # Run with live feedback
        def on_feedback(result):
            print(f"Beat {result.beat_number}: Energy={result.energy_ok}")

        operator.run_round(seed=1966, on_each_beat=on_feedback)
    """

    def __init__(self, mod_space: int = MAHA_QUANTUM) -> None:
        self._gad_kirtan = GADKirtan(mod_space=mod_space)
        self._feedback_history: List[GADCheckResult] = []

    def set_energy_check(self, check: Callable[[], bool]) -> None:
        """Set energy check (HARE) - resource usage."""
        self._gad_kirtan.set_energy_check(check)

    def set_safety_check(self, check: Callable[[], bool]) -> None:
        """Set safety check (RAMA) - state validity."""
        self._gad_kirtan.set_safety_check(check)

    def run_beat(
        self,
        seed: int,
        on_feedback: Optional[Callable[[GADKirtanResult], None]] = None,
    ) -> GADKirtanResult:
        """Run single beat with optional feedback callback."""
        result = self._gad_kirtan.compute_with_gad(seed)
        self._feedback_history.append(result.gad_check)

        if on_feedback:
            on_feedback(result)

        return result

    def run_round(
        self,
        seed: int,
        on_each_beat: Optional[Callable[[GADKirtanResult], None]] = None,
    ) -> List[GADKirtanResult]:
        """Run full round with optional per-beat feedback."""
        results: List[GADKirtanResult] = []
        current_seed = seed

        for _ in range(SEVEN):
            result = self.run_beat(current_seed, on_each_beat)
            results.append(result)
            current_seed = result.transformed_value

        return results

    def get_feedback_summary(self) -> Dict[str, object]:
        """Get summary of all feedback history."""
        if not self._feedback_history:
            return {"beats": 0, "all_passed": True}

        total_beats = len(self._feedback_history)
        all_passed = all(f.all_checks_passed for f in self._feedback_history)
        energy_failures = sum(1 for f in self._feedback_history if not f.energy_ok)
        safety_failures = sum(1 for f in self._feedback_history if not f.safety_ok)

        return {
            "beats": total_beats,
            "all_passed": all_passed,
            "energy_failures": energy_failures,
            "safety_failures": safety_failures,
            "success_rate": sum(1 for f in self._feedback_history if f.all_checks_passed) / total_beats,
        }

    def reset(self) -> None:
        """Reset feedback history."""
        self._feedback_history.clear()


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Constants
    "BEAT_WORD_RANGES",
    "BEAT_WORD_TYPES",
    # Results
    "GADCheckResult",
    "GADKirtanResult",
    # Core
    "GADKirtan",
    "LiveFeedbackOperator",
]
