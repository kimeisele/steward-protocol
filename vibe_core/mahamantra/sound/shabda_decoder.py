"""
SHABDA DECODER — Deterministic Speech-to-Text
===============================================

"śabda-brahma" — Sound is the ultimate reality.

Audio → uint32 frames → ARPAbet phonemes → RAMA coordinates → dictionary → transcript.

Pipeline:
    Audio Frames (10ms, uint32)
        → unpack_frame() → RMS, Varga, F0, Centroid  [shabda_intake.py]
    Per-frame features
        → score_frame() against PhonemeTemplates       [this file]
        → top-1 ARPAbet → ARPABET_TO_RAMA             [this file]
    Per-frame RAMA coords
        → CTC-dedup → phoneme-level sequence           [this file]
        → segment by silence/energy dips               [this file]
    Word-length segments
        → RAMA edit distance vs PronunciationDict      [this file]
        → greedy best match per segment
    Transcript: "not exactly but I came to preach..."

No ML models. No external APIs. Pure phonetic algebra + dictionary lookup.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Dict, Final, List, Optional, Sequence, Tuple

from vibe_core.mahamantra.protocols._seed import PANCHA, WORDS
from vibe_core.mahamantra.sound.shabda_intake import (
    ShabdaStream,
    unpack_frame,
)
from vibe_core.mahamantra.substrate.encoding.pancha_walk import (
    COORD_ELEMENT,
    COORD_VARGA,
)
from vibe_core.mahamantra.substrate.encoding.phonetic_bridge import (
    ARPABET_TO_RAMA,
    ARPABET_TO_STHANA,
    ARPABET_TO_VARGA,
    SthanaIndex,
    VargaIndex,
)

logger = logging.getLogger("SHABDA_DECODER")


# =============================================================================
# PHONEME TEMPLATES (acoustic fingerprints for each ARPAbet phoneme)
# =============================================================================

@dataclass(frozen=True)
class PhonemeTemplate:
    """Acoustic template for a single ARPAbet phoneme."""

    arpabet: str
    rama_coord: int
    varga: int           # 0-4 (VargaIndex)
    sthana: int          # 0-4 (SthanaIndex)
    sound_class: int     # 0=svara, 1=sparsha, 2=shesha
    f0_required: bool    # voiced?
    f1_center: int       # Hz (0=don't care)
    f2_center: int       # Hz (0=don't care)
    centroid_min: int     # centroid/100 low bound
    centroid_max: int     # centroid/100 high bound


# Standard F1/F2 centers from acoustic phonetics (adult male, typical)
_VOWEL_FORMANTS: Final[Dict[str, Tuple[int, int]]] = {
    "AA": (750, 1200),   # /ɑ/ father
    "AE": (660, 1700),   # /æ/ bat
    "AH": (520, 1200),   # /ʌ/ but
    "AO": (570, 850),    # /ɔ/ bought
    "AW": (700, 1100),   # /aʊ/ bout
    "AY": (700, 1200),   # /aɪ/ bite
    "EH": (530, 1850),   # /ɛ/ bet
    "EY": (400, 2200),   # /eɪ/ bait
    "ER": (490, 1350),   # /ɝ/ bird
    "IH": (390, 1950),   # /ɪ/ bit
    "IY": (280, 2300),   # /i/ beat
    "OW": (450, 850),    # /oʊ/ boat
    "OY": (450, 850),    # /ɔɪ/ boy
    "UH": (350, 1000),   # /ʊ/ book
    "UW": (300, 900),    # /u/ boot
}

# Centroid ranges (centroid/100) for consonant classes
_CONSONANT_CENTROID: Final[Dict[str, Tuple[int, int]]] = {
    # Stops: broad energy onset
    "K": (20, 200), "G": (20, 200), "NG": (10, 80),
    "CH": (40, 250), "JH": (40, 200),
    "T": (30, 250), "D": (30, 200), "TH": (40, 300), "DH": (30, 200), "N": (10, 80),
    "P": (10, 150), "B": (10, 150), "F": (80, 350), "M": (10, 60),
    # Semivowels
    "Y": (30, 200), "R": (20, 180), "L": (20, 160),
    "V": (20, 180), "W": (20, 150),
    # Sibilants / Fricatives
    "S": (150, 400), "SH": (100, 350), "Z": (100, 350),
    "ZH": (80, 300), "HH": (30, 250),
}


def _build_templates() -> Tuple[PhonemeTemplate, ...]:
    """Build phoneme templates from ARPABET mapping tables."""
    templates: List[PhonemeTemplate] = []

    for arpabet, rama in ARPABET_TO_RAMA.items():
        varga_idx = ARPABET_TO_VARGA.get(arpabet, VargaIndex.KANTHYA)
        sthana_idx = ARPABET_TO_STHANA.get(arpabet, SthanaIndex.GHOSHAVAT)

        if rama < WORDS:
            sound_class = 0
        elif rama < WORDS + PANCHA * PANCHA:
            sound_class = 1
        else:
            sound_class = 2

        f0_required = sthana_idx != SthanaIndex.SPARSHA
        f1, f2 = _VOWEL_FORMANTS.get(arpabet, (0, 0))
        c_min, c_max = _CONSONANT_CENTROID.get(arpabet, (0, 511))
        if sound_class == 0:
            c_min, c_max = 0, 511

        templates.append(PhonemeTemplate(
            arpabet=arpabet,
            rama_coord=rama,
            varga=int(varga_idx),
            sthana=int(sthana_idx),
            sound_class=sound_class,
            f0_required=f0_required,
            f1_center=f1,
            f2_center=f2,
            centroid_min=c_min,
            centroid_max=c_max,
        ))

    return tuple(templates)


PHONEME_TEMPLATES: Final[Tuple[PhonemeTemplate, ...]] = _build_templates()

# Pre-index: varga → list of template indices (for fast filtering)
_TEMPLATES_BY_VARGA: Final[Dict[int, List[int]]] = {}
for _i, _t in enumerate(PHONEME_TEMPLATES):
    _TEMPLATES_BY_VARGA.setdefault(_t.varga, []).append(_i)


# =============================================================================
# FRAME SCORING (audio frame → phoneme candidates)
# =============================================================================


def score_frame(
    packed: int,
    f1: int = 0,
    f2: int = 0,
) -> List[Tuple[str, float]]:
    """Score an audio frame against all phoneme templates.

    Returns top-3 (arpabet, score) candidates sorted by score descending.
    Score range: 0.0 (no match) to 1.0 (perfect match).
    """
    rms, varga, f0_x10, centroid_100 = unpack_frame(packed)

    if rms < 20:
        return []  # silence

    is_voiced = f0_x10 > 0
    candidates: List[Tuple[str, float]] = []

    # Pre-filter: only templates matching frame varga (± 1 neighbor)
    check_vargas = {varga}
    if varga > 0:
        check_vargas.add(varga - 1)
    if varga < 4:
        check_vargas.add(varga + 1)

    check_indices: List[int] = []
    for v in check_vargas:
        check_indices.extend(_TEMPLATES_BY_VARGA.get(v, []))

    for idx in check_indices:
        t = PHONEME_TEMPLATES[idx]
        score = 0.0

        # Voicing match (0.3 weight)
        if t.f0_required == is_voiced:
            score += 0.3
        elif not t.f0_required and not is_voiced:
            score += 0.3

        # Varga match (0.2 weight)
        if t.varga == varga:
            score += 0.2
        else:
            score += 0.05

        # Centroid range (0.2 weight)
        if t.centroid_min <= centroid_100 <= t.centroid_max:
            score += 0.2
        elif centroid_100 < t.centroid_min:
            dist = t.centroid_min - centroid_100
            score += max(0.0, 0.2 - dist * 0.002)
        else:
            dist = centroid_100 - t.centroid_max
            score += max(0.0, 0.2 - dist * 0.002)

        # Formant match (0.3 weight — only for vowels with formant data)
        if t.f1_center > 0 and f1 > 0 and f2 > 0:
            f1_err = abs(f1 - t.f1_center) / max(t.f1_center, 1)
            f2_err = abs(f2 - t.f2_center) / max(t.f2_center, 1)
            formant_score = max(0.0, 1.0 - (f1_err + f2_err))
            score += 0.3 * formant_score
        elif t.f1_center == 0:
            # Consonant: no formant penalty, give partial credit
            score += 0.15

        candidates.append((t.arpabet, score))

    candidates.sort(key=lambda x: x[1], reverse=True)
    return candidates[:3]


def _frames_to_phoneme_coords(
    frames: Sequence[int],
    raw_samples: object = None,
    sample_rate: int = 44100,
    hop_ms: int = 10,
    n_fft: int = 1024,
) -> Tuple[int, ...]:
    """Convert packed audio frames to RAMA coords via ARPAbet template scoring.

    For each voiced frame:
        1. Extract formants from raw_samples (if available)
        2. score_frame(packed, f1, f2) → top-1 ARPAbet phoneme
        3. ARPABET_TO_RAMA[phoneme] → RAMA coordinate
        4. Majority-vote smoothing (window=5) to reduce frame-level noise

    This is the PHONEME DETECTION path (not the resonance path).
    """
    import numpy as np
    from vibe_core.mahamantra.sound.shabda_intake import extract_formants

    hop = int(sample_rate * hop_ms / 1000)
    has_raw = raw_samples is not None and isinstance(raw_samples, np.ndarray)

    # Phase 1: Per-frame best phoneme
    raw_arpabets: List[str] = []
    for i, frame in enumerate(frames):
        rms = frame & 0xFF
        if rms < 15:
            raw_arpabets.append("")  # silence marker
            continue

        # Extract formants if raw audio available
        f1, f2 = 0, 0
        if has_raw:
            start_sample = i * hop
            end_sample = start_sample + n_fft
            if end_sample <= len(raw_samples):
                audio_frame = raw_samples[start_sample:end_sample]
                f1, f2 = extract_formants(audio_frame, sample_rate)

        candidates = score_frame(frame, f1, f2)
        if candidates:
            raw_arpabets.append(candidates[0][0])
        else:
            raw_arpabets.append("")

    if not raw_arpabets:
        return ()

    # Phase 2: Majority-vote smoothing (window=5)
    smoothed: List[str] = []
    window = 5
    half_w = window // 2
    for i in range(len(raw_arpabets)):
        if not raw_arpabets[i]:
            smoothed.append("")
            continue
        # Count phonemes in window
        counts: Dict[str, int] = {}
        for j in range(max(0, i - half_w), min(len(raw_arpabets), i + half_w + 1)):
            p = raw_arpabets[j]
            if p:
                counts[p] = counts.get(p, 0) + 1
        if counts:
            best = max(counts, key=lambda k: counts[k])
            smoothed.append(best)
        else:
            smoothed.append("")

    # Phase 3: Convert to RAMA coords
    coords: List[int] = []
    for arpabet in smoothed:
        if not arpabet:
            continue
        rama = ARPABET_TO_RAMA.get(arpabet)
        if rama is not None:
            coords.append(rama)
    return tuple(coords)


# =============================================================================
# SEGMENTATION (stream → word-length segments)
# =============================================================================

@dataclass(frozen=True)
class Segment:
    """A word-length segment of audio frames."""

    start: int       # frame index (inclusive)
    end: int         # frame index (exclusive)
    frames: Tuple[int, ...]

    @property
    def length(self) -> int:
        return self.end - self.start

    @property
    def duration_ms(self) -> int:
        return self.length * 10


# Segmentation thresholds — tuned for Prabhupada's speaking style
_SILENCE_RMS = 15         # lower threshold catches quieter pauses
_SILENCE_GAP = 2          # 2+ silent frames = word boundary (20ms)
_ENERGY_DIP_RMS = 50      # energy dip at 50 (was 80) — more sensitive
_ENERGY_DIP_GAP = 5       # 5+ low-energy frames = boundary (was 8)
_MIN_SEGMENT_FRAMES = 5   # 50ms minimum (discard shorter)
_MAX_SEGMENT_FRAMES = 80  # 800ms maximum (was 2s — force split earlier)


def segment_stream(frames: Sequence[int]) -> List[Segment]:
    """Segment audio frames into word-length chunks.

    Word boundaries detected by:
    - Silence (2+ frames with RMS < 15)
    - Energy dip (5+ frames with RMS < 50)
    - Max length (force split at 80 frames / 800ms)

    Returns list of Segments, each containing the packed frames.
    """
    if not frames:
        return []

    segments: List[Segment] = []
    seg_start = -1
    silence_count = 0
    dip_count = 0

    for i, frame in enumerate(frames):
        rms = frame & 0xFF

        if rms < _SILENCE_RMS:
            silence_count += 1
            dip_count += 1
        elif rms < _ENERGY_DIP_RMS:
            silence_count = 0
            dip_count += 1
        else:
            silence_count = 0
            dip_count = 0

        if seg_start < 0 and rms >= _SILENCE_RMS:
            seg_start = i
            silence_count = 0
            dip_count = 0
            continue

        if seg_start < 0:
            continue

        is_boundary = (
            silence_count >= _SILENCE_GAP
            or dip_count >= _ENERGY_DIP_GAP
            or (i - seg_start) >= _MAX_SEGMENT_FRAMES
        )

        if is_boundary:
            seg_end = i - silence_count + 1
            if seg_end <= seg_start:
                seg_end = seg_start + 1

            if seg_end - seg_start >= _MIN_SEGMENT_FRAMES:
                segments.append(Segment(
                    start=seg_start,
                    end=seg_end,
                    frames=tuple(frames[seg_start:seg_end]),
                ))
            seg_start = -1
            silence_count = 0
            dip_count = 0

    # Flush final segment
    if seg_start >= 0:
        seg_end = len(frames)
        while seg_end > seg_start and (frames[seg_end - 1] & 0xFF) < _SILENCE_RMS:
            seg_end -= 1
        if seg_end - seg_start >= _MIN_SEGMENT_FRAMES:
            segments.append(Segment(
                start=seg_start,
                end=seg_end,
                frames=tuple(frames[seg_start:seg_end]),
            ))

    return segments


# =============================================================================
# COMMON ENGLISH VOCABULARY (top ~350 words for spoken English coverage)
# =============================================================================

_COMMON_ENGLISH: Final[Tuple[str, ...]] = (
    # Function words (articles, pronouns, prepositions, conjunctions)
    "a", "an", "the", "this", "that", "these", "those",
    "i", "me", "my", "we", "us", "our", "you", "your",
    "he", "him", "his", "she", "her", "it", "its", "they", "them", "their",
    "who", "what", "which", "where", "when", "how", "why",
    "in", "on", "at", "to", "for", "of", "with", "from", "by", "as",
    "up", "out", "about", "into", "over", "after", "under", "between",
    "and", "or", "but", "not", "no", "so", "if", "then", "than", "because",
    # Common verbs
    "is", "am", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "shall",
    "should", "can", "could", "may", "might", "must",
    "say", "said", "go", "went", "gone", "come", "came",
    "get", "got", "give", "gave", "take", "took", "make", "made",
    "know", "knew", "think", "thought", "see", "saw", "want", "wanted",
    "look", "looked", "find", "found", "tell", "told", "ask", "asked",
    "use", "used", "try", "tried", "leave", "left", "call", "called",
    "keep", "kept", "let", "begin", "began", "seem", "seemed",
    "help", "show", "hear", "heard", "play", "run", "ran",
    "move", "live", "believe", "bring", "brought", "happen",
    "write", "wrote", "sit", "sat", "stand", "stood", "lose", "lost",
    "pay", "paid", "meet", "met", "set", "learn", "learned",
    "lead", "led", "understand", "understood", "watch", "follow",
    "stop", "stopped", "speak", "spoke", "read", "spend", "spent",
    "grow", "grew", "open", "opened", "walk", "walked",
    "win", "won", "teach", "develop", "preach", "preached",
    # Common nouns
    "time", "year", "people", "way", "day", "man", "woman",
    "child", "children", "world", "life", "hand", "part", "place",
    "case", "week", "company", "system", "program", "question",
    "work", "government", "number", "night", "point", "home", "water",
    "room", "mother", "area", "money", "story", "fact", "month",
    "lot", "right", "study", "book", "eye", "job", "word",
    "business", "issue", "side", "kind", "head", "house", "service",
    "friend", "father", "power", "hour", "game", "line", "end",
    "members", "family", "law", "car", "city", "community", "name",
    "boy", "boys", "girl", "girls", "group", "country", "problem",
    "god", "lord", "soul", "spirit", "mind", "body", "heart",
    "love", "truth", "peace", "light", "faith", "hope",
    # Common adjectives
    "good", "new", "first", "last", "long", "great", "little",
    "own", "other", "old", "right", "big", "high", "different",
    "small", "large", "next", "early", "young", "important", "few",
    "public", "bad", "same", "able", "real", "best", "better",
    "sure", "free", "true", "whole", "nice", "dear",
    # Common adverbs
    "just", "also", "very", "often", "however", "too", "usually",
    "really", "already", "always", "never", "sometimes", "together",
    "likely", "simply", "generally", "instead", "actually", "exactly",
    "enough", "well", "here", "there", "now", "only", "quite",
    "still", "back", "even", "ever", "ago", "once", "much",
    "far", "away", "again", "perhaps", "maybe", "soon",
    "fortunately", "unfortunately", "certainly", "definitely",
    # Prabhupada-specific vocabulary
    "consciousness", "spiritual", "material", "devotional",
    "transcendental", "transcendentalists", "supreme", "absolute",
    "devotee", "devotees", "temple", "chanting", "mantra",
    "meditation", "philosophy", "knowledge", "ignorance",
    "liberation", "bondage", "karma", "dharma", "yoga",
    "guru", "master", "disciple", "student", "teacher",
    "preaching", "mission", "movement", "society", "international",
    "enthusiastic", "wonderful", "beautiful", "merciful",
    "gospel", "message", "instruction", "scripture",
    "bhagavad", "gita", "vedic", "vedas", "upanishad",
    "india", "america", "new", "york", "san", "francisco",
    "eh", "ehm", "um", "uh", "oh", "yes", "no",
    "some", "every", "many", "much", "more", "most", "any",
    "all", "each", "both", "few", "several",
)


# =============================================================================
# PRONUNCIATION DICTIONARY (word → RAMA coords)
# =============================================================================


class PronunciationDict:
    """Pronunciation dictionary mapping words to RAMA coordinate sequences.

    Sanskrit words loaded from rama_lexicon.json (4,127 entries, exact coords).
    English words from lexicon meanings + common English vocabulary.

    Lazy-initialized, cached.
    """

    def __init__(self) -> None:
        self._sanskrit: Optional[Dict[str, Tuple[int, ...]]] = None
        self._english: Optional[Dict[str, Tuple[int, ...]]] = None
        self._by_first_coord: Optional[Dict[int, List[str]]] = None
        self._by_length: Optional[Dict[int, List[str]]] = None

    def _add_english_word(self, token: str, coords: Tuple[int, ...]) -> None:
        """Register a single English word in the dictionary."""
        assert self._english is not None
        assert self._by_first_coord is not None
        assert self._by_length is not None
        self._english[token] = coords
        fc = coords[0]
        self._by_first_coord.setdefault(fc, []).append(token)
        self._by_length.setdefault(len(coords), []).append(token)

    def _ensure_loaded(self) -> None:
        if self._sanskrit is not None:
            return

        self._sanskrit = {}
        self._english = {}
        self._by_first_coord = {}
        self._by_length = {}

        # 1. Load Sanskrit from SemanticIndex
        from vibe_core.mahamantra.substrate.encoding.semantic_index import get_index

        index = get_index()
        for coord in range(49):
            for word in index.by_rama_position(coord):
                self._sanskrit[word.sanskrit] = word.coords
                fc = word.coords[0] if word.coords else -1
                self._by_first_coord.setdefault(fc, []).append(word.sanskrit)
                self._by_length.setdefault(len(word.coords), []).append(word.sanskrit)

        # 2. English from lexicon meanings
        from vibe_core.mahamantra.substrate.encoding.phonetic_encoder import encode_text

        seen_english: set = set()
        for coord in range(49):
            for word in index.by_rama_position(coord):
                for meaning in word.meanings:
                    for token in meaning.lower().split():
                        token = token.strip(".,;:()[]\"'!?")
                        if len(token) < 2 or token in seen_english:
                            continue
                        seen_english.add(token)
                        coords = encode_text(token)
                        if coords:
                            self._add_english_word(token, coords)

        # 3. Common English vocabulary
        for token in _COMMON_ENGLISH:
            if token not in seen_english and token not in self._english:
                coords = encode_text(token)
                if coords:
                    self._add_english_word(token, coords)

        logger.info(
            "PronunciationDict loaded: %d Sanskrit, %d English",
            len(self._sanskrit), len(self._english),
        )

    def lookup(self, word: str) -> Optional[Tuple[int, ...]]:
        """Get RAMA coords for a word."""
        self._ensure_loaded()
        assert self._sanskrit is not None and self._english is not None
        return self._sanskrit.get(word) or self._english.get(word.lower())

    def candidates_for_segment(
        self,
        first_coord: int,
        length: int,
        length_tolerance: int = 2,
    ) -> List[Tuple[str, Tuple[int, ...]]]:
        """Get candidate words matching first coordinate and approximate length."""
        self._ensure_loaded()
        assert self._by_first_coord is not None and self._by_length is not None
        assert self._sanskrit is not None and self._english is not None

        by_coord = set(self._by_first_coord.get(first_coord, []))

        by_len: set = set()
        for l in range(max(1, length - length_tolerance), length + length_tolerance + 1):
            by_len.update(self._by_length.get(l, []))

        matches = by_coord & by_len
        result: List[Tuple[str, Tuple[int, ...]]] = []
        for w in matches:
            coords = self._sanskrit.get(w) or self._english.get(w.lower())
            if coords is not None:
                result.append((w, coords))

        return result

    def all_candidates_for_length(
        self,
        length: int,
        length_tolerance: int = 2,
    ) -> List[Tuple[str, Tuple[int, ...]]]:
        """Get ALL candidate words matching approximate length (no coord filter)."""
        self._ensure_loaded()
        assert self._by_length is not None
        assert self._sanskrit is not None and self._english is not None

        result: List[Tuple[str, Tuple[int, ...]]] = []
        seen: set = set()
        for l in range(max(1, length - length_tolerance), length + length_tolerance + 1):
            for w in self._by_length.get(l, []):
                if w in seen:
                    continue
                seen.add(w)
                coords = self._sanskrit.get(w) or self._english.get(w.lower())
                if coords is not None:
                    result.append((w, coords))
        return result

    @property
    def sanskrit_count(self) -> int:
        self._ensure_loaded()
        assert self._sanskrit is not None
        return len(self._sanskrit)

    @property
    def english_count(self) -> int:
        self._ensure_loaded()
        assert self._english is not None
        return len(self._english)

    @property
    def total_count(self) -> int:
        return self.sanskrit_count + self.english_count


# Module-level singleton
_DICT: Optional[PronunciationDict] = None


def get_pronunciation_dict() -> PronunciationDict:
    """Get or create the global PronunciationDict singleton."""
    global _DICT
    if _DICT is None:
        _DICT = PronunciationDict()
    return _DICT


# =============================================================================
# SCORING (RAMA edit distance between observed and candidate)
# =============================================================================


def _score_candidate(
    observed: Tuple[int, ...],
    candidate: Tuple[int, ...],
) -> float:
    """Element-weighted edit distance between observed RAMA coords and candidate.

    Scoring:
        Same coord: cost 0
        Same element: cost 0.3
        Same varga class: cost 0.6
        Different: cost 1.0
        Length penalty: min(n,m)/max(n,m) factor

    Returns: score in [0.0, 1.0], higher = better match.
    """
    n = len(observed)
    m = len(candidate)

    if n == 0 or m == 0:
        return 0.0

    # Dynamic programming edit distance with weighted substitution costs
    # Use integer-scaled costs (*10) to avoid float accumulation
    prev = list(range(0, (m + 1) * 10, 10))
    curr = [0] * (m + 1)

    for i in range(1, n + 1):
        curr[0] = i * 10
        for j in range(1, m + 1):
            if observed[i - 1] == candidate[j - 1]:
                sub_cost = 0
            elif COORD_ELEMENT[observed[i - 1]] == COORD_ELEMENT[candidate[j - 1]]:
                sub_cost = 3
            elif COORD_VARGA[observed[i - 1]] == COORD_VARGA[candidate[j - 1]]:
                sub_cost = 6
            else:
                sub_cost = 10

            curr[j] = min(
                prev[j] + 10,          # deletion
                curr[j - 1] + 10,      # insertion
                prev[j - 1] + sub_cost,  # substitution
            )
        prev, curr = curr, prev

    edit_dist = prev[m] / 10.0
    max_len = max(n, m)
    length_ratio = min(n, m) / max_len

    raw_score = 1.0 - (edit_dist / max_len)
    return max(0.0, raw_score * length_ratio)


# =============================================================================
# CTC-STYLE DEDUPLICATION (frame-level → phoneme-level)
# =============================================================================


def _dedup_coords(coords: Tuple[int, ...]) -> Tuple[int, ...]:
    """Collapse consecutive identical RAMA coordinates.

    Frame-level coords repeat the same value for the duration of each phoneme.
    A 300ms /a/ at 10ms/frame → 30× coord 0. This collapses to 1× coord 0.

    Standard CTC (Connectionist Temporal Classification) approach:
    (5, 5, 5, 12, 12, 12, 12, 42, 42) → (5, 12, 42)
    """
    if not coords:
        return ()
    result: List[int] = [coords[0]]
    for c in coords[1:]:
        if c != result[-1]:
            result.append(c)
    return tuple(result)


# =============================================================================
# TRANSCRIPT DATA TYPES
# =============================================================================


@dataclass(frozen=True)
class TranscriptWord:
    """A single recognized word in the transcript."""

    word: str
    confidence: float     # 0-1
    language: str         # "sanskrit" / "english"
    rama_coords: Tuple[int, ...]
    start_ms: int
    end_ms: int


@dataclass(frozen=True)
class Transcript:
    """Complete transcription result."""

    words: Tuple[TranscriptWord, ...]
    duration_ms: int
    source: str

    @property
    def text(self) -> str:
        return " ".join(w.word for w in self.words)


# =============================================================================
# SHABDA DECODER (main class)
# =============================================================================


class ShabdaDecoder:
    """Deterministic speech-to-text decoder.

    Uses RAMA coordinate space to match audio segments against a pronunciation
    dictionary of Sanskrit (from Gita lexicon) and English words.

    No ML models. No external APIs. Pure phonetic algebra.

    Usage:
        decoder = ShabdaDecoder()
        transcript = decoder.transcribe(stream)
        print(transcript.text)
    """

    def __init__(
        self,
        language: str = "both",
        min_confidence: float = 0.3,
        use_formants: bool = True,
    ) -> None:
        self._language = language
        self._min_confidence = min_confidence
        self._use_formants = use_formants
        self._dict = get_pronunciation_dict()

    def transcribe(self, stream: ShabdaStream) -> Transcript:
        """Transcribe a full ShabdaStream to text."""
        segments = segment_stream(stream.frames)
        words: List[TranscriptWord] = []

        for seg in segments:
            result = self._decode_segment(
                seg,
                raw_samples=stream.raw_samples,
                sample_rate=stream.sample_rate,
                hop_ms=stream.hop_ms,
                n_fft=stream.n_fft,
            )
            if result is not None:
                words.append(result)

        return Transcript(
            words=tuple(words),
            duration_ms=stream.duration_ms,
            source=stream.source,
        )

    def transcribe_segment(
        self,
        frames: Sequence[int],
        raw_samples: object = None,
        sr: int = 44100,
    ) -> List[TranscriptWord]:
        """Transcribe a pre-segmented sequence of packed frames."""
        segments = segment_stream(frames)
        words: List[TranscriptWord] = []
        for seg in segments:
            result = self._decode_segment(seg)
            if result is not None:
                words.append(result)
        return words

    def _decode_segment(
        self,
        seg: Segment,
        raw_samples: object = None,
        sample_rate: int = 44100,
        hop_ms: int = 10,
        n_fft: int = 1024,
    ) -> Optional[TranscriptWord]:
        """Decode a single segment into a word.

        Uses the PHONEME TEMPLATE path with formant extraction:
            score_frame(packed, f1, f2) → top-1 ARPAbet → ARPABET_TO_RAMA
            → majority-vote smoothing → CTC-dedup → dictionary lookup
        """
        import numpy as np

        # Slice raw samples for this segment (if available)
        seg_raw = None
        if raw_samples is not None and isinstance(raw_samples, np.ndarray):
            hop = int(sample_rate * hop_ms / 1000)
            start_sample = seg.start * hop
            end_sample = (seg.end + 1) * hop + n_fft
            if end_sample <= len(raw_samples):
                seg_raw = raw_samples[start_sample:end_sample]

        raw_coords = _frames_to_phoneme_coords(
            seg.frames, seg_raw, sample_rate, hop_ms, n_fft,
        )
        if not raw_coords:
            return None

        # CTC-style dedup: collapse consecutive identical coords → phoneme-level
        rama_coords = _dedup_coords(raw_coords)
        if not rama_coords:
            return None

        # Get candidates from dictionary — try coord-filtered first, then broad
        first_coord = rama_coords[0]
        coord_len = len(rama_coords)
        candidates: List[Tuple[str, Tuple[int, ...]]] = []

        # Primary: match by first coord + length
        for fc in (first_coord, first_coord - 1, first_coord + 1):
            if 0 <= fc < 49:
                candidates.extend(
                    self._dict.candidates_for_segment(fc, coord_len, length_tolerance=3)
                )

        # Fallback: if too few candidates, search by length only
        if len(candidates) < 10:
            candidates.extend(
                self._dict.all_candidates_for_length(coord_len, length_tolerance=2)
            )

        if not candidates:
            return None

        # Score all candidates
        best_word = ""
        best_score = 0.0
        best_coords: Tuple[int, ...] = ()

        seen: set = set()
        for word, word_coords in candidates:
            if word in seen:
                continue
            seen.add(word)
            score = _score_candidate(rama_coords, word_coords)
            if score > best_score:
                best_score = score
                best_word = word
                best_coords = word_coords

        if best_score < self._min_confidence:
            return None

        # Determine language
        assert self._dict._sanskrit is not None
        lang = "sanskrit" if best_word in self._dict._sanskrit else "english"

        return TranscriptWord(
            word=best_word,
            confidence=best_score,
            language=lang,
            rama_coords=best_coords,
            start_ms=seg.start * 10,
            end_ms=seg.end * 10,
        )


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "PhonemeTemplate",
    "PHONEME_TEMPLATES",
    "Segment",
    "TranscriptWord",
    "Transcript",
    "ShabdaDecoder",
    "PronunciationDict",
    "get_pronunciation_dict",
    "score_frame",
    "segment_stream",
    "_dedup_coords",
    "_frames_to_phoneme_coords",
]
