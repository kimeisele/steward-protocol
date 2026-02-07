"""
SHADOW ORACLE - The Lightweight Gita 13.35 Pre-Filter
=====================================================

"kṣetra-kṣetrajñayor evam antaraṁ jñāna-cakṣuṣā
bhūta-prakṛti-mokṣaṁ ca ye vidur yānti te param"

"Those who see with eyes of knowledge the difference between the field
and the knower of the field, and can also understand the process of
liberation from bondage in material nature, attain the supreme goal."
— Bhagavad Gita 13.35

ARCHITECTURE:
=============

    MahaOracle (research)  = Full research class with all lenses
    ShadowOracle (reactor) = Lightweight pre-filter for hot paths

    The ShadowOracle is:
    - RAM-efficient: Minimal state, no heavy objects
    - Protocol-based: Implements MahaOracleProtocol
    - PARAMPARA-first: Gita 13.35 as mandatory pre-filter
    - Backfoldable: Results fold into ShadowState

DERIVATION FROM MAHAMANTRA:
===========================

    PARAMPARA = 37 = KSHETRA + MAHAJANA + KSETRAJNA = 24 + 12 + 1
    The TRINITY (3) attractors at mod 37 represent the Parampara channels:
      - 12 = MAHAJANA_COUNT (the 12 authorities)
      - 26 = 2 × Chapter 13 (transmission doubled)
      - 34 = GURU_VERSE (stable principle)

    SEVEN = 7 (axioms) - from _seed.py
    TEN = 10 (senses) - from _seed.py

    The transform: HARE (×SEVEN), KRISHNA (+TEN), RAMA (×value)

WATERTIGHT: No Any types. Protocol statt Klassen.
ALL CONSTANTS FROM SSOT (_seed.py) - NO HARDCODING!
"""

from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "shuka"  # Position 14 - Vision/Narration
__position__ = 14
__genesis__ = "0xcdd640f9"  # GenesisByte: parampara % 37 == 0

from typing import (
    Dict,
    Final,
    Optional,
)

# =============================================================================
# SSOT IMPORTS - All constants from single source of truth
# =============================================================================
# Core constants from _seed.py (THE LAW)
from vibe_core.mahamantra.protocols._seed import (
    COSMIC_FRAME,
    KSETRA_KSETRAJNA_CHAPTER,
    KSETRA_KSETRAJNA_VERSE,
    KSETRAJNA,
    MAHA_QUANTUM,
    PARAMPARA,
    SEVEN,
    TEN,
    TRINITY,
    WORDS,
)

# THE ALGORITHM - imported from SSOT, not reimplemented!
from vibe_core.mahamantra.substrate.algorithm import maha_oscillate_optimized as maha_oscillate

# Parampara channels from _seed.py (via shadow_protocol)
from vibe_core.mahamantra.reactor.shadow_protocol import (
    PARAMPARA_CHANNEL_NAMES,
    PARAMPARA_CHANNELS,
    MahaOracleProtocol,
    OracleValidationResult,
    ShadowState,
)

# NOTE: Pattern no longer needed - using maha_oscillate from algorithm/

# PRABHUPADA constants from substrate resonance
from vibe_core.mahamantra.substrate.resonance import (
    PRABHUPADA_BUILD,
    PRABHUPADA_KEY_YEARS,
    PRABHUPADA_RUNTIME_END,
)

# =============================================================================
# DERIVED CONSTANTS (computed from SSOT, not hardcoded)
# =============================================================================
PRABHUPADA_RUNTIME_YEARS: Final[int] = PRABHUPADA_RUNTIME_END - PRABHUPADA_BUILD + 1  # 82


# =============================================================================
# SHADOW ORACLE - Lightweight Implementation
# =============================================================================


class ShadowOracle:
    """
    The Shadow Oracle - Lightweight Gita 13.35 Pre-Filter.

    RAM-EFFICIENT:
        - No heavy resonator objects
        - Inline transform logic
        - Stateless validation

    GITA 13.35 PRINCIPLE:
        Without authentic Guru (Parampara), true knowledge is not possible.
        Therefore: PARAMPARA (mod 37) is the MANDATORY FIRST LENS.

    INTEGRATION POINTS:
        1. validate()     → Call BEFORE compute (MANDATORY)
        2. validate_fast() → Hot path boolean check
        3. backfold()     → Merge results into ShadowState

    Usage:
        oracle = ShadowOracle()

        # Before any computation in ShadowReactor:
        validation = oracle.validate(seed)
        if not validation["parampara_validated"]:
            # Proceed with warning (knowledge may be incomplete)
            state["dissonance_report"] = "PARAMPARA WARNING: Not in valid channel"

        # During PRASADAM phase:
        state = oracle.backfold(validation, state)
    """

    __slots__ = ()  # No instance state - fully stateless

    def _oscillate_parampara(self, value: int) -> int:
        """
        Single oscillation through 16-step Mahamantra at mod PARAMPARA (37).

        DELEGATES to algorithm/ - no duplication!
        """
        return maha_oscillate(value, PARAMPARA)

    def _find_attractor_parampara(self, seed: int, max_cycles: int = 50) -> tuple[int, int]:
        """
        Find attractor at mod 37 (PARAMPARA).

        Returns (attractor, cycles_to_converge).
        """
        seen: dict[int, int] = {}
        value = seed % PARAMPARA

        for cycle in range(max_cycles):
            if value in seen:
                return value, seen[value]
            seen[value] = cycle
            value = self._oscillate_parampara(value)

        return value, max_cycles

    def _get_channel(self, attractor: int) -> int:
        """
        Get Parampara channel (0-4) from attractor.

        Returns -1 if not in any valid channel (void).
        """
        if attractor in PARAMPARA_CHANNELS:
            return PARAMPARA_CHANNELS.index(attractor)
        return -1

    def _check_prabhupada_year(self, seed: int) -> int | None:
        """
        Check if seed resonates with Prabhupada Lila year.

        Returns the year if resonant, None otherwise.
        """
        # Direct year match
        if PRABHUPADA_BUILD <= seed <= PRABHUPADA_RUNTIME_END:
            return seed

        # Delta-based resonance with key years
        delta = seed % PRABHUPADA_RUNTIME_YEARS
        potential_year = PRABHUPADA_BUILD + delta
        if potential_year in PRABHUPADA_KEY_YEARS:
            return potential_year

        return None

    def validate(self, seed: int) -> OracleValidationResult:
        """
        MANDATORY PRE-FILTER: Validate Parampara connection (Gita 13.35).

        This MUST be called BEFORE any computation in the ShadowReactor.

        Args:
            seed: The intent/data encoded as integer

        Returns:
            OracleValidationResult with:
                - parampara_validated: True if in valid disciplic channel
                - parampara_channel: Which of 5 channels (-1 if void)
                - parampara_attractor: The attractor value
                - coherence: Integer coherence scaled by COSMIC_FRAME
                - prabhupada_year: Resonant year or None
        """
        # Find attractor at mod 37
        attractor, cycles = self._find_attractor_parampara(seed)

        # Check if in valid channel
        channel = self._get_channel(attractor)
        validated = channel >= 0

        # Compute coherence (inverse of cycles to converge)
        # High coherence = fast convergence to valid channel
        if cycles == 0:
            coherence = COSMIC_FRAME  # Maximum
        else:
            coherence = COSMIC_FRAME // (cycles + 1)

        # Boost coherence if in valid channel
        if validated:
            coherence = min(COSMIC_FRAME, coherence + COSMIC_FRAME // PARAMPARA)

        # Check Prabhupada year resonance
        prabhupada_year = self._check_prabhupada_year(seed)

        return OracleValidationResult(
            parampara_validated=validated,
            parampara_channel=channel,
            parampara_attractor=attractor,
            coherence=coherence,
            prabhupada_year=prabhupada_year,
        )

    def validate_fast(self, seed: int) -> bool:
        """
        FAST VALIDATION: Returns only boolean.

        For hot paths where full result is not needed.
        """
        attractor, _ = self._find_attractor_parampara(seed)
        return attractor in PARAMPARA_CHANNELS

    def consult_seed(self, seed: int) -> Dict:
        """
        Lightweight consultation - just Parampara lens.

        For full multi-lens analysis, use MahaOracle from research module.
        """
        validation = self.validate(seed)
        channel = validation["parampara_channel"]
        channel_name = PARAMPARA_CHANNEL_NAMES[channel] if channel >= 0 else "VOID"

        return {
            "seed": seed,
            "parampara_validated": validation["parampara_validated"],
            "parampara_channel": channel,
            "parampara_channel_name": channel_name,
            "parampara_attractor": validation["parampara_attractor"],
            "coherence": validation["coherence"],
            "prabhupada_year": validation["prabhupada_year"],
            "gita_verse": "13.35",  # The mandatory principle
        }

    def backfold(
        self,
        validation: OracleValidationResult,
        state: ShadowState,
    ) -> ShadowState:
        """
        Backfold Oracle validation into ShadowState.

        Called during PRASADAM phase to merge Oracle insight.
        Does NOT mutate input - creates new state dict.

        Args:
            validation: Result from validate()
            state: Current ShadowState

        Returns:
            New ShadowState with Oracle data in dissonance_report
        """
        # Create new state (shallow copy is sufficient for TypedDict)
        new_state = ShadowState(
            position=state["position"],
            previous=state["previous"],
            phase=state["phase"],
            quarter=state["quarter"],
            guardian=state["guardian"],
            opcode=state["opcode"],
            cycle_count=state["cycle_count"],
            switch_count=state["switch_count"],
            return_count=state["return_count"],
            dissonance_report=state["dissonance_report"],
        )

        # Build Oracle report
        if validation["parampara_validated"]:
            channel = validation["parampara_channel"]
            channel_name = PARAMPARA_CHANNEL_NAMES[channel] if channel >= 0 else "VOID"
            oracle_report = f"✓ GITA 13.35: {channel_name} channel (#{channel + 1})"

            if validation["prabhupada_year"]:
                delta = validation["prabhupada_year"] - PRABHUPADA_BUILD
                oracle_report += f" | Prabhupada Lila {validation['prabhupada_year']} (Δ={delta})"
        else:
            oracle_report = "⚠ GITA 13.35 WARNING: Not in valid Parampara channel"

        # Merge with existing dissonance report
        existing = state.get("dissonance_report")
        if existing:
            new_state["dissonance_report"] = f"{existing} | {oracle_report}"
        else:
            new_state["dissonance_report"] = oracle_report

        return new_state


# =============================================================================
# SINGLETON FACTORY (RAM-efficient)
# =============================================================================
# ShadowOracle is stateless, so one instance is sufficient.

_shadow_oracle: ShadowOracle | None = None


def get_shadow_oracle() -> ShadowOracle:
    """
    Get the ShadowOracle singleton.

    RAM-efficient: ShadowOracle is stateless, so sharing is safe.
    """
    global _shadow_oracle
    if _shadow_oracle is None:
        _shadow_oracle = ShadowOracle()
    return _shadow_oracle


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Implementation
    "ShadowOracle",
    # Factory
    "get_shadow_oracle",
    # NOTE: Constants are NOT re-exported here!
    # Import PARAMPARA_CHANNELS from _seed.py or shadow_protocol.py
    # Import PRABHUPADA_* from maha_algorithm.py
    # This is SSOT - no duplication!
]
