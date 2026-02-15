"""
PHONETICS — 3D Syllable Vectors
================================

Each syllable = (stress, height, weight):
    stress: primary (1), secondary (2), or unstressed (0)
    height: vowel height from articulatory phonetics (1-5)
    weight: consonant cluster mass (onset + coda + 1)

Zero external dependencies. Vowel-group heuristic for syllabification.
ARPAbet parsing available for callers that supply phoneme lists directly.
"""

from __future__ import annotations

import re
from typing import Final, List, Tuple

from vibe_core.mahamantra.protocols._seed import (
    HALVES,
    KSETRAJNA,
)
from vibe_core.mahamantra.substrate.language.types import (
    RhythmProfile,
    SyllableVector,
)
from vibe_core.mahamantra.substrate.phonetic_bridge import (
    ARPABET_TO_VARGA,
    VargaIndex,
)

_WORD_TOKEN_RE: Final = re.compile(r"[A-Za-z']+")
_VOWEL_GROUP_RE: Final = re.compile(r"[aeiouy]+")


def _varga_height(varga: VargaIndex) -> int:
    """Map VargaIndex to height 1-5 (PANCHA scale, protocol-derived).

    KANTHYA(0)=1 (throat=low), OSHTHYA(4)=5 (lips=high).
    """
    return varga.value + KSETRAJNA


def syllable_vectors_for_word(word: str) -> Tuple[SyllableVector, ...]:
    """Extract 3D syllable vectors from vowel-group heuristic.

    Zero external dependencies. For callers with ARPAbet phoneme lists,
    use parse_arpabet() directly.
    """
    return _fallback_vectors(word)


def parse_arpabet(phones: List[str]) -> Tuple[SyllableVector, ...]:
    """Parse ARPAbet phoneme list into 3D syllable vectors.

    Public API for callers that already have phoneme data.
    """
    syllables: List[SyllableVector] = []
    onset_consonants = 0

    for p in phones:
        base = p.rstrip("012")
        stress_char = p[-1] if p[-1].isdigit() else None

        if stress_char is not None:  # vowel nucleus
            stress = int(stress_char)
            varga = ARPABET_TO_VARGA.get(base, VargaIndex.MURDHANYA)
            height = _varga_height(varga)
            weight = onset_consonants + KSETRAJNA
            syllables.append(SyllableVector(stress=stress, height=height, weight=weight))
            onset_consonants = 0
        else:
            onset_consonants += KSETRAJNA

    # Trailing consonants (coda) add to last syllable weight
    if syllables and onset_consonants > 0:
        last = syllables[-1]
        syllables[-1] = SyllableVector(
            stress=last.stress,
            height=last.height,
            weight=last.weight + onset_consonants,
        )

    return tuple(syllables)


def _fallback_vectors(word: str) -> Tuple[SyllableVector, ...]:
    """Fallback when CMU is unavailable: vowel groups → approximate vectors."""
    groups = _VOWEL_GROUP_RE.findall(word.lower())
    if not groups:
        return ()
    if len(groups) == KSETRAJNA:
        return (SyllableVector(stress=KSETRAJNA, height=3, weight=max(KSETRAJNA, len(word) - len(groups[0]) + KSETRAJNA)),)
    return tuple(
        SyllableVector(
            stress=KSETRAJNA if i == 0 else 0,
            height=3,
            weight=HALVES,
        )
        for i in range(len(groups))
    )


def stress_for_word(word: str) -> Tuple[int, ...]:
    """Extract stress digits (backward compat)."""
    return tuple(sv.stress for sv in syllable_vectors_for_word(word))


def scan_syllable_rhythm(text: str) -> RhythmProfile:
    """Convert input into 3D syllable vectors aligned to the 32-step mantra grid.

    Imports mantra_grid lazily to avoid circular dependency.
    """
    from vibe_core.mahamantra.substrate.language.mantra_grid import (
        align_syllables_to_grid,
        build_mantra_grid,
    )

    tokens = _WORD_TOKEN_RE.findall(text)
    all_vectors: List[SyllableVector] = []
    for token in tokens:
        all_vectors.extend(syllable_vectors_for_word(token))

    if not all_vectors:
        return RhythmProfile(
            syllable_count=0,
            stress_pattern=(),
            sequencer_steps=(),
            signature="-",
        )

    vectors = tuple(all_vectors)
    steps = align_syllables_to_grid(vectors)
    grid = build_mantra_grid()
    modes = tuple(grid[s].mode for s in steps)
    stress_pattern = tuple(sv.stress for sv in vectors)
    signature = "".join(str(s) for s in stress_pattern)

    return RhythmProfile(
        syllable_count=len(vectors),
        stress_pattern=stress_pattern,
        sequencer_steps=steps,
        signature=signature,
        vectors=vectors,
        grid_modes=modes,
    )
