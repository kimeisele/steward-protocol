"""
MAHA ORACLE - The Intent-to-Resonance Interface
===============================================

"Those who see with eyes of knowledge..." - BG 13.35

Receives a question (intent) and returns a reading by viewing it 
through multiple sacred lenses (mod-spaces).
"""

from __future__ import annotations

# === MAHAJANA DECLARATION ===
__mahajana__ = "vyasa"
__position__ = 0
__genesis__ = "0x672435f8"

from dataclasses import dataclass
from typing import Final, Tuple, Dict, Optional, List

from vibe_core.mahamantra.protocols._seed import (
    MAHA_QUANTUM,
    PARAMPARA,
    HALVES,
    SEVEN,
    TEN,
    POSITION_SUM_KRISHNA,
    MALA_COMPLETE,
    PARAMPARA_CHANNELS,
    PARAMPARA_CHANNEL_NAMES,
    TRINITY,
    WORDS,
    MAHAMANTRA_WORD_PATTERN as PATTERN,
    MAHAMANTRA_NAME_HARE,
    MAHAMANTRA_NAME_KRISHNA,
)

from vibe_core.mahamantra.substrate.algorithm.maha import triangular
from vibe_core.mahamantra.substrate.resonance.resonator import MahaResonator


@dataclass(frozen=True)
class OracleLens:
    """A single lens (mod-space) for viewing an intent."""
    name: str
    mod_space: int
    meaning: str
    resonance: int
    is_fixed_point: bool
    attractor: int
    cycles: int


@dataclass(frozen=True)
class OracleReading:
    """Complete oracle reading."""
    intent: str
    seed: int
    lenses: Tuple[OracleLens, ...]
    gita_resonance: int
    primary_attractor: int
    holographic_factors: Tuple[int, ...]
    interpretation: str
    parampara_validated: bool
    parampara_channel: int
    prabhupada_year_resonance: Optional[int]


# Constants
PRABHUPADA_BUILD: Final[int] = 1896
PRABHUPADA_RUNTIME_END: Final[int] = 1977
PRABHUPADA_RUNTIME_YEARS: Final[int] = 82
PRABHUPADA_KEY_YEARS: Final[Tuple[int, ...]] = (1896, 1922, 1932, 1944, 1959, 1965, 1966, 1977)

ORACLE_LENSES: Final[Tuple[Tuple[str, int, str], ...]] = (
    ("PARAMPARA", PARAMPARA, "MANDATORY: Disciplic channel"),
    ("BINARY", HALVES, "Mridanga rhythm"),
    ("AXIOM", SEVEN, "Pure structure"),
    ("TETRAD", TEN, "Embodied senses"),
    ("KRISHNA", POSITION_SUM_KRISHNA, "All-attractive"),
    ("MALA", MALA_COMPLETE, "Complete japa"),
    ("QUANTUM", MAHA_QUANTUM, "Maximum diversity"),
)


class MahaOracle:
    """The Maha Oracle - Intent-to-Resonance Interface."""
    
    def __init__(self) -> None:
        self._resonators: Dict[int, MahaResonator] = {}
        for _name, mod_space, _meaning in ORACLE_LENSES:
            self._resonators[mod_space] = MahaResonator(mod_space)
            
    def encode_intent(self, intent: str) -> int:
        """Encode intent string to integer using Mahamantra weights."""
        if not intent:
            return 0
        value = 0
        for i, char in enumerate(intent):
            char_val = ord(char)
            pos = (i % WORDS) + 1
            t_pos = triangular(pos)
            pattern_char = PATTERN[i % WORDS]
            
            if pattern_char == MAHAMANTRA_NAME_HARE:
                contribution = (char_val * t_pos * SEVEN) % MAHA_QUANTUM
            elif pattern_char == MAHAMANTRA_NAME_KRISHNA:
                contribution = (char_val + t_pos + TEN) % MAHA_QUANTUM
            else:
                contribution = (char_val * t_pos) % MAHA_QUANTUM
            value = (value + contribution) % MAHA_QUANTUM
            
        return self._resonators[MAHA_QUANTUM].oscillate_once(value)

    def _analyze_lens(self, seed: int, name: str, mod_space: int, meaning: str) -> OracleLens:
        resonator = self._resonators[mod_space]
        result = resonator.find_attractor(seed)
        return OracleLens(
            name=name,
            mod_space=mod_space,
            meaning=meaning,
            resonance=seed % mod_space,
            is_fixed_point=(result.cycle_length == 1 and result.cycles_to_converge == 0),
            attractor=result.attractor,
            cycles=result.cycles_to_converge,
        )

    def _interpret(self, reading_data: dict) -> str:
        lines = []
        if reading_data.get("parampara_validated"):
             lines.append("✓ PARAMPARA VALIDATED")
        else:
             lines.append("⚠ PARAMPARA WARNING")
        
        if reading_data.get("holographic_factors"):
             lines.append(f"HOLOGRAPHIC: {reading_data['holographic_factors']}")
             
        return "\n".join(lines)

    def consult_seed(self, seed: int) -> OracleReading:
        lenses = []
        lenses_by_name = {}
        for name, mod_space, meaning in ORACLE_LENSES:
            lens = self._analyze_lens(seed, name, mod_space, meaning)
            lenses.append(lens)
            lenses_by_name[name] = lens
            
        parampara_lens = lenses_by_name.get("PARAMPARA")
        parampara_validated = False
        parampara_channel = -1
        if parampara_lens and parampara_lens.attractor in PARAMPARA_CHANNELS:
            parampara_validated = True
            parampara_channel = PARAMPARA_CHANNELS.index(parampara_lens.attractor)

        # Simplified logic for now
        gita_resonance = lenses_by_name["TETRAD"].attractor if "TETRAD" in lenses_by_name else 0
        primary = lenses_by_name["QUANTUM"].attractor if "QUANTUM" in lenses_by_name else 0
        
        # Find holographic
        counts: Dict[int, int] = {}
        for l in lenses:
            counts[l.attractor] = counts.get(l.attractor, 0) + 1
        holographic = tuple(sorted([v for v, c in counts.items() if c > 1]))
        
        reading = {
            "parampara_validated": parampara_validated,
            "holographic_factors": holographic
        }
        
        return OracleReading(
            intent=f"seed:{seed}",
            seed=seed,
            lenses=tuple(lenses),
            gita_resonance=gita_resonance,
            primary_attractor=primary,
            holographic_factors=holographic,
            interpretation=self._interpret(reading),
            parampara_validated=parampara_validated,
            parampara_channel=parampara_channel,
            prabhupada_year_resonance=None # Simplified
        )

    def consult(self, intent: str) -> OracleReading:
        seed = self.encode_intent(intent)
        reading = self.consult_seed(seed)
        # Return new reading with intent string
        return OracleReading(
            intent=intent,
            seed=seed,
            lenses=reading.lenses,
            gita_resonance=reading.gita_resonance,
            primary_attractor=reading.primary_attractor,
            holographic_factors=reading.holographic_factors,
            interpretation=reading.interpretation,
            parampara_validated=reading.parampara_validated,
            parampara_channel=reading.parampara_channel,
            prabhupada_year_resonance=reading.prabhupada_year_resonance
        )
