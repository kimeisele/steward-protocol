"""
SHABDA DECODER — Deterministic Speech-to-Text
===============================================

"śabda-brahma" — Sound is the ultimate reality.

Audio → uint32 frames → RAMA coordinates → pronunciation dictionary → transcript.

NOT resonance matching (that's ResonanceRanker). This is LITERAL TRANSCRIPTION:
"So Krishna consciousness is not something artificial..."

Pipeline:
    Audio Frames (10ms, uint32)
        → unpack_frame() → RMS, Varga, F0, Centroid  [shabda_intake.py]
        → extract_formants() → F1, F2               [shabda_intake.py]
    Enhanced Features
        → score_frame() against PhonemeTemplates      [this file]
    Per-frame phoneme candidates (top-3 ARPAbet)
        → segment_stream()                            [this file]
    Word-length segments (bounded by silence/energy dips)
        → RAMA edit distance vs PronunciationDict     [this file]
    Scored word candidates per segment
        → greedy selection
    Transcript: "dharma yoga consciousness..."

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
    """Acoustic template for a single ARPAbet phoneme.

    Used to score how well an audio frame matches this phoneme.
    """

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

        # Determine sound class from RAMA coordinate
        if rama < WORDS:  # 0-15 = svara
            sound_class = 0
        elif rama < WORDS + PANCHA * PANCHA:  # 16-40 = sparsha
            sound_class = 1
        else:  # 41-48 = shesha
            sound_class = 2

        # F0 required = voiced
        f0_required = sthana_idx != SthanaIndex.SPARSHA

        # Formant centers
        f1, f2 = _VOWEL_FORMANTS.get(arpabet, (0, 0))

        # Centroid range
        c_min, c_max = _CONSONANT_CENTROID.get(arpabet, (0, 511))
        if sound_class == 0:
            c_min, c_max = 0, 511  # vowels have broad centroid

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
        # Mismatch: don't add

        # Varga match (0.2 weight)
        if t.varga == varga:
            score += 0.2
        else:
            score += 0.05  # neighbor varga, small credit

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
        return self.length * 10  # 10ms per frame


# Segmentation thresholds
_SILENCE_RMS = 20         # frames below this = silence
_SILENCE_GAP = 3          # 3+ silent frames = word boundary
_ENERGY_DIP_RMS = 80      # energy dip threshold
_ENERGY_DIP_GAP = 8       # 8+ low-energy frames = word boundary
_MIN_SEGMENT_FRAMES = 5   # 50ms minimum (discard shorter)
_MAX_SEGMENT_FRAMES = 200 # 2s maximum (force split)


def segment_stream(frames: Sequence[int]) -> List[Segment]:
    """Segment audio frames into word-length chunks.

    Word boundaries detected by:
    - Silence (3+ frames with RMS < 20)
    - Energy dip (8+ frames with RMS < 80)
    - Max length (force split at 200 frames / 2s)

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

        # Start a segment on voiced frame
        if seg_start < 0 and rms >= _SILENCE_RMS:
            seg_start = i
            silence_count = 0
            dip_count = 0
            continue

        if seg_start < 0:
            continue

        # Check boundary conditions
        is_boundary = (
            silence_count >= _SILENCE_GAP
            or dip_count >= _ENERGY_DIP_GAP
            or (i - seg_start) >= _MAX_SEGMENT_FRAMES
        )

        if is_boundary:
            # Trim trailing silence from segment end
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
        # Trim trailing silence
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
# PRONUNCIATION DICTIONARY (word → RAMA coords)
# =============================================================================


class PronunciationDict:
    """Pronunciation dictionary mapping words to RAMA coordinate sequences.

    Sanskrit words loaded from rama_lexicon.json (4,127 entries, exact coords).
    English words derived via encode_text() from lexicon meanings.

    Lazy-initialized, cached.
    """

    def __init__(self) -> None:
        self._sanskrit: Optional[Dict[str, Tuple[int, ...]]] = None
        self._english: Optional[Dict[str, Tuple[int, ...]]] = None
        self._by_first_coord: Optional[Dict[int, List[str]]] = None
        self._by_length: Optional[Dict[int, List[str]]] = None

    def _ensure_loaded(self) -> None:
        if self._sanskrit is not None:
            return

        self._sanskrit = {}
        self._english = {}
        self._by_first_coord = {}
        self._by_length = {}

        # Load Sanskrit from SemanticIndex
        from vibe_core.mahamantra.substrate.encoding.semantic_index import get_index

        index = get_index()
        for coord in range(49):
            for word in index.by_rama_position(coord):
                self._sanskrit[word.sanskrit] = word.coords
                fc = word.coords[0] if word.coords else -1
                self._by_first_coord.setdefault(fc, []).append(word.sanskrit)
                self._by_length.setdefault(len(word.coords), []).append(word.sanskrit)

        # Derive English from lexicon meanings
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
                            self._english[token] = coords
                            fc = coords[0]
                            self._by_first_coord.setdefault(fc, []).append(token)
                            self._by_length.setdefault(len(coords), []).append(token)

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
        """Get candidate words matching first coordinate and approximate length.

        Prefilter: words starting at first_coord with length ± tolerance.
        Returns list of (word, coords) pairs.
        """
        self._ensure_loaded()
        assert self._by_first_coord is not None and self._by_length is not None
        assert self._sanskrit is not None and self._english is not None

        # Words matching first coordinate
        by_coord = set(self._by_first_coord.get(first_coord, []))

        # Words matching length range
        by_len: set = set()
        for l in range(max(1, length - length_tolerance), length + length_tolerance + 1):
            by_len.update(self._by_length.get(l, []))

        # Intersection
        matches = by_coord & by_len
        result: List[Tuple[str, Tuple[int, ...]]] = []
        for w in matches:
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
    INF = (n + m + 1) * 10
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
        """Transcribe a full ShabdaStream to text.

        Args:
            stream: ShabdaStream from ShabdaIntake

        Returns:
            Transcript with recognized words and confidence scores.
        """
        segments = segment_stream(stream.frames)
        words: List[TranscriptWord] = []

        for seg in segments:
            result = self._decode_segment(seg)
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
        """Transcribe a pre-segmented sequence of packed frames.

        Args:
            frames: packed uint32 audio frames
            raw_samples: optional raw audio for formant extraction
            sr: sample rate

        Returns:
            List of TranscriptWord (may be empty).
        """
        segments = segment_stream(frames)
        words: List[TranscriptWord] = []
        for seg in segments:
            result = self._decode_segment(seg)
            if result is not None:
                words.append(result)
        return words

    def _decode_segment(self, seg: Segment) -> Optional[TranscriptWord]:
        """Decode a single segment into a word.

        Steps:
        1. Extract RAMA coords from frames (via shabda_processor)
        2. Get candidates from PronunciationDict (prefiltered)
        3. Score candidates via weighted edit distance
        4. Return best match above confidence threshold
        """
        from vibe_core.mahamantra.sound.shabda_processor import stream_to_rama

        # Extract RAMA coordinates from segment frames
        rama_coords = stream_to_rama(seg.frames)
        if not rama_coords:
            return None

        # Get candidates from dictionary
        first_coord = rama_coords[0]
        coord_len = len(rama_coords)
        candidates = self._dict.candidates_for_segment(
            first_coord, coord_len, length_tolerance=2,
        )

        # Also try neighbors of first coord (acoustic noise tolerance)
        for neighbor in (first_coord - 1, first_coord + 1):
            if 0 <= neighbor < 49:
                candidates.extend(
                    self._dict.candidates_for_segment(
                        neighbor, coord_len, length_tolerance=2,
                    )
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
]
