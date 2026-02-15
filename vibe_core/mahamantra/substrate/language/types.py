"""
LANGUAGE TYPES — Pure data structures for the language engine.
==============================================================

No logic. No imports beyond typing and stdlib.
"""

from __future__ import annotations

from typing import NamedTuple, Optional, Tuple


class SyllableVector(NamedTuple):
    """3D phonetic vector for a single syllable.

    stress: 0=unstressed, 1=primary, 2=secondary (ARPAbet)
    height: vowel height 1-5 (low→high, articulatory)
    weight: consonant cluster mass (onset + coda + 1 for vowel)
    """

    stress: int
    height: int
    weight: int


class RhythmProfile(NamedTuple):
    """Temporal profile for a text input — 3D syllable vectors on mantra grid."""

    syllable_count: int
    stress_pattern: Tuple[int, ...]
    sequencer_steps: Tuple[int, ...]
    signature: str
    vectors: Tuple[SyllableVector, ...] = ()
    grid_modes: Tuple[str, ...] = ()


class StateVector(NamedTuple):
    """Numeric summary of system state for semantic injection into composer.

    Extracted from MahaState.get_status(). All fields are numeric —
    no strings, no keywords. The composer uses these to bias word selection
    toward tokens that describe reality.

    guna: 0=TAMAS (inert), 1=RAJAS (active), 2=SATTVA (harmonious)
    entry_count: sovereign state entries (0..72)
    boot_count: system boot cycles
    uptime_ratio: uptime / max_stale, clamped to [0, 1]
    systems_alive: wrapped subsystems available (0..6)
    dirty: unsaved state changes pending
    prana_level: total antaranga prana from engine resonance stage
    """

    guna: int = 1             # Default RAJAS (active)
    entry_count: int = 0
    boot_count: int = 0
    uptime_ratio: float = 0.0
    systems_alive: int = 0
    dirty: bool = False
    prana_level: int = 0


class EngineResult(NamedTuple):
    """Complete result from the Maha Language Engine."""

    input_text: str
    seed: int
    attractor: int
    guardian_name: str
    guardian_function: str
    intent_category: str
    section_name: str
    section_mode: str
    verse_ref: str
    resonant_words: Tuple[Tuple[str, str, float], ...]  # (sanskrit, meaning, score)
    template_words: Tuple[Tuple[str, str, str], ...]  # (sanskrit, meaning, role)
    antaranga_active: int
    antaranga_prana: int
    output: str
    derivation: str
    # === Extended fields ===
    attention_cached: bool = False
    expansion_depth: int = 0
    expanded_names: Tuple[str, ...] = ()
    synth_walk_words: Tuple[Tuple[str, str], ...] = ()
    diw_applied: int = 0
    shabda_spawns: int = 0
    phoneme_trajectory: str = ""
    syllable_count: int = 0
    stress_pattern: Tuple[int, ...] = ()
    sequencer_steps: Tuple[int, ...] = ()
