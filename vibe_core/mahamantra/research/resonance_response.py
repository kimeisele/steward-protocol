"""
RESONANCE RESPONSE - The Complete Intent-to-Syllable Pipeline
==============================================================

"harer nama harer nama harer namaiva kevalam"
"In this age of Kali there is no other way than chanting the holy name."

This module UNIFIES all existing components into a single response pipeline:
    Intent (Text) -> Resonance -> Syllables -> Response

NO NEW LOGIC. Just integration of existing production modules.

COMPONENTS USED:
    - MahaCompression: Text -> Seed + Guna
    - MahaResonator: Seed -> Attractor
    - MahaOracle: Seed -> OracleReading (7 lenses)
    - GitaResonance: Attractor -> VerseMatch
    - MahaKirtan: Seed -> KirtanComputeResult (7-beat)
    - rama_grid: Position -> RAMA[0-48] -> Phoneme
    - Shabda: Text -> VibrationSignature

THE FLOW:
    1. Compress intent to seed
    2. Find attractor via resonator
    3. Match to Gita verse
    4. Run through MahaKirtan (7-beat)
    5. Extract syllables via rama_to_phoneme
    6. Return complete ResonanceResponse
"""

from __future__ import annotations

# === MAHAJANA DECLARATION ===
__mahajana__ = "narada"  # The Messenger - connects all
__position__ = 2
__genesis__ = "0x2c80316d"

from dataclasses import dataclass, field
from typing import Final, List, Optional, Tuple

# === EXISTING PRODUCTION IMPORTS (NO MODIFICATION) ===
# Compression: Text -> Seed
from vibe_core.mahamantra.adapters.compression import MahaCompression

# Gita: Attractor -> Verse
from vibe_core.mahamantra.adapters.gita_resonance import GitaResonance, MatchResult
from vibe_core.mahamantra.protocols._seed import (
    MAHA_QUANTUM,
    PARAMPARA,
    WORDS,
)

# Resonance: Seed -> Attractor (PRODUCTION: MahaModularSynth, not MahaResonator)
from vibe_core.mahamantra.substrate.algorithm.maha import MahaModularSynth

# Kirtan: Seed -> Compute (7-beat)
from vibe_core.mahamantra.substrate.mantra.kirtan import KirtanComputeResult, MahaKirtan

# Shabda: Vibration signatures
from vibe_core.mahamantra.substrate.phonetics.shabda import (
    SANSKRIT_PHONEME_MAP,
    VibrationSignature,
    text_to_vibration,
)

# RAMA Grid: Position -> Phoneme
from vibe_core.mahamantra.substrate.rama_grid import (
    SVARAS,
    krishna_route,
    rama_to_phoneme,
)

# Oracle: Seed -> OracleReading
from vibe_core.mahamantra.substrate.resonance.oracle import MahaOracle, OracleReading

# Verify parampara
assert int(__genesis__, 16) % PARAMPARA == 0, "BROKEN LINEAGE"


# =============================================================================
# RESPONSE DATA STRUCTURES
# =============================================================================


@dataclass(frozen=True)
class SyllableSequence:
    """A sequence of syllables derived from resonance."""

    syllables: Tuple[str, ...]  # The actual syllables
    rama_indices: Tuple[int, ...]  # RAMA[0-48] indices
    positions: Tuple[int, ...]  # Mahamantra positions (1-16)

    @property
    def as_string(self) -> str:
        """Join syllables with hyphens."""
        return "-".join(self.syllables)

    @property
    def as_devanagari(self) -> str:
        """Placeholder for Devanagari output."""
        # Future: Convert to Devanagari script
        return self.as_string


@dataclass(frozen=True)
class ResonanceResponse:
    """
    Complete response from the resonance pipeline.

    Contains:
        - Input: The original intent
        - Seed: Compressed integer representation
        - Attractor: The resonance attractor (136=VAIKUNTHA or cycle)
        - Verse: Matched Gita verse
        - Syllables: Derived syllable sequence
        - Oracle: Full oracle reading
        - Kirtan: Kirtan compute result
        - Vibrations: VibrationSignatures for the response
    """

    # Input
    intent: str

    # Compression
    seed: int
    position: int  # 0-15 lotus position
    guna: str  # TAMAS/RAJAS/SATTVA/SUDDHA

    # Resonance
    attractor: int
    trajectory_class: str  # "vaikuntha" or "samsara"
    cycles_to_converge: int

    # Gita
    verse_id: Optional[str]  # e.g., "BG.18.66"
    verse_guna: Optional[str]
    dominant_name: Optional[str]  # HARE/KRISHNA/RAMA

    # Syllables
    syllables: SyllableSequence

    # Full data (optional, for deep analysis)
    trajectory: Tuple[int, ...] = field(default_factory=tuple)  # The actual path to attractor
    oracle_reading: Optional[OracleReading] = None
    kirtan_result: Optional[KirtanComputeResult] = None
    vibrations: Tuple[VibrationSignature, ...] = field(default_factory=tuple)

    @property
    def is_vaikuntha(self) -> bool:
        """True if attractor is 136 (VAIKUNTHA/Liberation)."""
        return self.attractor == 136

    @property
    def parampara_validated(self) -> bool:
        """True if oracle validated parampara connection."""
        if self.oracle_reading:
            return self.oracle_reading.parampara_validated
        return False

    def summary(self) -> str:
        """Human-readable summary."""
        traj_type = "VAIKUNTHA" if self.is_vaikuntha else "SAMSARA"
        traj_preview = str(self.trajectory[:5]) + "..." if len(self.trajectory) > 5 else str(self.trajectory)
        lines = [
            f"Intent: {self.intent[:50]}{'...' if len(self.intent) > 50 else ''}",
            f"Seed: {self.seed} | Guna: {self.guna.upper()}",
            f"Attractor: {self.attractor} ({traj_type}) | Cycles: {self.cycles_to_converge}",
            f"Trajectory: {traj_preview}",
            f"Verse: {self.verse_id or 'N/A'} | Dominant: {self.dominant_name or 'N/A'}",
            f"Syllables: {self.syllables.as_string} (Positions: {self.syllables.positions})",
        ]
        return "\n".join(lines)


# =============================================================================
# RESONANCE RESPONDER
# =============================================================================


class ResonanceResponder:
    """
    The Complete Intent-to-Syllable Pipeline.

    USAGE:
        responder = ResonanceResponder()
        response = responder.respond("What is the meaning of life?")
        print(response.syllables.as_string)  # e.g., "ka-ma-ra-ha"
        print(response.verse_id)              # e.g., "BG.18.66"
    """

    _naga_flooded: bool = True
    _naga_gene: str = "resonance_responder"

    def __init__(
        self,
        mod_space: int = MAHA_QUANTUM,
        use_oracle: bool = True,
        use_kirtan: bool = True,
    ) -> None:
        """
        Initialize the responder.

        Args:
            mod_space: Resonance mod space (default: 137)
            use_oracle: Whether to use MahaOracle for validation
            use_kirtan: Whether to use MahaKirtan for 7-beat pattern
        """
        self.mod_space = mod_space
        self.use_oracle = use_oracle
        self.use_kirtan = use_kirtan

        # Initialize components
        self._compression = MahaCompression()
        # PRODUCTION: Use MahaModularSynth.transform() not MahaResonator.find_attractor()
        self._synth = MahaModularSynth(default_preset="quantum")
        self._gita = GitaResonance()
        self._oracle = MahaOracle() if use_oracle else None
        self._kirtan = MahaKirtan(mod_space=mod_space, use_oracle=use_oracle) if use_kirtan else None

    def _derive_syllables(self, seed: int, positions: Optional[Tuple[int, ...]] = None) -> SyllableSequence:
        """
        Derive syllables from seed via RAMA grid.

        Uses krishna_route() to map positions to RAMA coordinates,
        then rama_to_phoneme() to get the actual syllables.
        """
        if positions is None:
            # Default: derive positions from seed
            # Use 4 positions based on seed nibbles
            positions = tuple(((seed >> (i * 4)) % WORDS) + 1 for i in range(4))

        rama_indices = []
        syllables = []

        for pos in positions:
            rama_idx = krishna_route(pos - 1)  # 0-indexed
            phoneme = rama_to_phoneme(rama_idx)
            rama_indices.append(rama_idx)
            syllables.append(phoneme)

        return SyllableSequence(
            syllables=tuple(syllables),
            rama_indices=tuple(rama_indices),
            positions=positions,
        )

    def _derive_from_attractor(
        self,
        attractor: int,
        dominant_name: Optional[str] = None,
    ) -> SyllableSequence:
        """
        Derive syllables from the ATTRACTOR via krishna_route().

        MATHEMATICALLY DERIVED FROM MANTRA:
            krishna_route(position) = position × 17 mod 49
            where: 17 = SEVEN + TEN = POSITION_SUM_KRISHNA
                   49 = SEVEN² = POSITION_SUM_RAMA (VARNAMALA)

        This is the ONLY routing formula in the codebase - no speculation.

        Args:
            attractor: The resonance attractor (136=VAIKUNTHA or cycle value)
            dominant_name: HARE/KRISHNA/RAMA from GitaResonance

        The dominant_name determines the NUMBER of syllables (from axioms):
            HARE: 8 syllables (HARE_COUNT = 8)
            KRISHNA: 4 syllables (KRISHNA_COUNT = 4)
            RAMA: 4 syllables (RAMA_COUNT = 4)
            None: 4 syllables (default)
        """
        # BRANCHLESS: Lookup table derived from axioms
        # HARE_COUNT=8, KRISHNA_COUNT=4, RAMA_COUNT=4
        _SYLLABLE_COUNT = {"HARE": 8, "KRISHNA": 4, "RAMA": 4}
        num_syllables = _SYLLABLE_COUNT.get(dominant_name or "", 4)

        # Base position from attractor (like production: attractor % WORDS)
        base_position = attractor % WORDS

        rama_indices = []
        syllables = []
        positions = []

        for i in range(num_syllables):
            # Step through Mahamantra positions starting from base
            pos_0indexed = (base_position + i) % WORDS
            pos_1indexed = pos_0indexed + 1

            # KRISHNA ROUTING: The mathematically derived formula
            # krishna_route(pos) = pos × 17 mod 49
            rama_idx = krishna_route(pos_0indexed)

            # Get phoneme from RAMA grid
            phoneme = rama_to_phoneme(rama_idx)

            positions.append(pos_1indexed)
            rama_indices.append(rama_idx)
            syllables.append(phoneme)

        return SyllableSequence(
            syllables=tuple(syllables),
            rama_indices=tuple(rama_indices),
            positions=tuple(positions),
        )

    def respond(self, intent: str) -> ResonanceResponse:
        """
        Generate a complete resonance response for the given intent.

        Args:
            intent: The input text/question/intent

        Returns:
            ResonanceResponse with seed, attractor, verse, syllables
        """
        # 1. Compress intent to seed
        compression = self._compression.compress(intent)
        seed = compression.seed
        position = compression.position
        guna = compression.intent_level.guna.value

        # 2. Find attractor via PRODUCTION method (MahaModularSynth.transform)
        attractor = self._synth.transform(seed)
        trajectory_class = "vaikuntha" if attractor == 136 else "samsara"

        # 3. Match to Gita verse - USE SEED TO SELECT (like production!)
        # FIX: Don't use best_match (= first), use seed % len(matches)
        # See _mahamantra_lotus.py line 305 for the production fix
        gita_result = self._gita.match(attractor)
        verse_id = None
        verse_guna = None
        dominant_name = None
        if gita_result.matches:
            # COMPUTED verse selection - NOT first match!
            verse_index = seed % len(gita_result.matches)
            selected_verse = gita_result.matches[verse_index]
            verse_id = selected_verse.verse_id
            verse_guna = selected_verse.guna
            dominant_name = selected_verse.dominant_name

        # 4. Oracle reading (optional)
        oracle_reading = None
        if self._oracle:
            oracle_reading = self._oracle.consult(intent)

        # 5. Kirtan compute (optional)
        kirtan_result = None
        if self._kirtan:
            kirtan_result = self._kirtan.compute(seed)

        # 6. Derive syllables from ATTRACTOR via proper Mahamantra routing
        # FOLLOWS PRODUCTION: position = attractor % WORDS, then krishna_route()
        syllables = self._derive_from_attractor(
            attractor=attractor,
            dominant_name=dominant_name,
        )

        # 7. Get vibration signatures for syllables
        vibrations = tuple(
            SANSKRIT_PHONEME_MAP.get(s, SANSKRIT_PHONEME_MAP.get("a"))
            for s in syllables.syllables
            if s in SANSKRIT_PHONEME_MAP or "a" in SANSKRIT_PHONEME_MAP
        )

        return ResonanceResponse(
            intent=intent,
            seed=seed,
            position=position,
            guna=guna,
            attractor=attractor,
            trajectory_class=trajectory_class,
            cycles_to_converge=WORDS,  # MahaModularSynth runs 16 steps
            trajectory=(seed, attractor),  # Simplified: input → output
            verse_id=verse_id,
            verse_guna=verse_guna,
            dominant_name=dominant_name,
            syllables=syllables,
            oracle_reading=oracle_reading,
            kirtan_result=kirtan_result,
            vibrations=vibrations,
        )

    def respond_seed(self, seed: int) -> ResonanceResponse:
        """
        Generate response from a numeric seed (skip compression).
        """
        # Use seed directly via PRODUCTION method (MahaModularSynth.transform)
        attractor = self._synth.transform(seed)
        trajectory_class = "vaikuntha" if attractor == 136 else "samsara"

        # Gita match - USE SEED TO SELECT (like production!)
        gita_result = self._gita.match(attractor)
        verse_id = None
        verse_guna = None
        dominant_name = None
        if gita_result.matches:
            # COMPUTED verse selection - NOT first match!
            verse_index = seed % len(gita_result.matches)
            selected_verse = gita_result.matches[verse_index]
            verse_id = selected_verse.verse_id
            verse_guna = selected_verse.guna
            dominant_name = selected_verse.dominant_name

        # Oracle
        oracle_reading = None
        if self._oracle:
            oracle_reading = self._oracle.consult_seed(seed)

        # Kirtan
        kirtan_result = None
        if self._kirtan:
            kirtan_result = self._kirtan.compute(seed)

        # Syllables - from ATTRACTOR via proper Mahamantra routing
        syllables = self._derive_from_attractor(
            attractor=attractor,
            dominant_name=dominant_name,
        )

        # Vibrations
        vibrations = tuple(
            SANSKRIT_PHONEME_MAP.get(s, SANSKRIT_PHONEME_MAP.get("a"))
            for s in syllables.syllables
            if s in SANSKRIT_PHONEME_MAP or "a" in SANSKRIT_PHONEME_MAP
        )

        return ResonanceResponse(
            intent=f"seed:{seed}",
            seed=seed,
            position=seed % WORDS,
            guna="computed",
            attractor=attractor,
            trajectory_class=trajectory_class,
            cycles_to_converge=WORDS,  # MahaModularSynth runs 16 steps
            trajectory=(seed, attractor),  # Simplified: input → output
            verse_id=verse_id,
            verse_guna=verse_guna,
            dominant_name=dominant_name,
            syllables=syllables,
            oracle_reading=oracle_reading,
            kirtan_result=kirtan_result,
            vibrations=vibrations,
        )


# =============================================================================
# CONVENIENCE FUNCTION
# =============================================================================


# Singleton instance for simple usage
_default_responder: Optional[ResonanceResponder] = None


def respond(intent: str) -> ResonanceResponse:
    """
    Generate a resonance response for the given intent.

    This is the main entry point for simple usage:

        from vibe_core.mahamantra.research.resonance_response import respond

        response = respond("What is the meaning of life?")
        print(response.syllables.as_string)  # e.g., "a-kha-dha-u"
        print(response.verse_id)              # e.g., "BG.18.66"
        print(response.summary())
    """
    global _default_responder
    if _default_responder is None:
        _default_responder = ResonanceResponder()
    return _default_responder.respond(intent)


# =============================================================================
# DEMO / TEST
# =============================================================================


if __name__ == "__main__":
    print("=" * 70)
    print("RESONANCE RESPONSE - Intent to Syllables")
    print("=" * 70)
    print()

    # Test with various intents
    test_intents = [
        "What is the meaning of life?",
        "Hare Krishna Hare Krishna Krishna Krishna Hare Hare",
        "Build a web server",
        "sarva-dharman parityajya mam ekam saranam vraja",
    ]

    responder = ResonanceResponder()

    for intent in test_intents:
        print(f"INPUT: {intent}")
        print("-" * 70)

        response = responder.respond(intent)
        print(response.summary())

        if response.oracle_reading:
            print(f"Parampara: {'VALIDATED' if response.parampara_validated else 'WARNING'}")

        if response.kirtan_result:
            print(f"Beat: {response.kirtan_result.beat_number}/7 | Call: {response.kirtan_result.call_response}")

        print()
        print("=" * 70)
        print()
