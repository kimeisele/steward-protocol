"""
SHABDA ALIGNER — Viterbi Forced Alignment + Tiny ASR
=====================================================

"śravaṇaṁ kīrtanaṁ viṣṇoḥ" — Hearing and chanting are the first steps.

Given audio + known transcript → precise phoneme-level alignment.
Uses a Tiny Acoustic Model (2-layer MLP, 21K params, seed=137) to produce
per-frame phoneme probabilities, then Viterbi decoding constrained by the
transcript's phoneme sequence to find optimal frame-to-phoneme assignment.

Architecture:
    Audio (ShabdaStream)
        → log-Mel spectrogram (26 bins, 10ms hop)
        → context frames (±2 neighbors → 130D input)
        → Tiny ASR (130→128→N_CLASSES softmax)
        → per-frame emission probabilities
    Transcript (word list)
        → CMU ARPAbet phoneme sequence (with silence between words)
        → Viterbi state machine (self-transition + advance)
        → optimal frame-to-state alignment
    Result:
        → per-frame phoneme labels (guaranteed correct order)
        → word boundaries (start_ms, end_ms per word)
        → per-word RAMA coordinates

No external ML models. Pure NumPy. Weights seed-initialized (MAHA_QUANTUM=137)
and calibrated on audio via forced alignment training loop.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Final, List, Optional, Sequence, Tuple

import numpy as np
from scipy.fft import fft

from vibe_core.mahamantra.protocols._seed import MAHA_QUANTUM
from vibe_core.mahamantra.sound.shabda_intake import (
    N_FFT,
    ShabdaStream,
    _mel_filterbank,
)
from vibe_core.mahamantra.substrate.encoding.phonetic_bridge import (
    ARPABET_TO_RAMA,
)

logger = logging.getLogger("SHABDA_ALIGNER")

# =============================================================================
# CONSTANTS
# =============================================================================

N_MELS: Final[int] = 26
CONTEXT_FRAMES: Final[int] = 2  # ±2 neighbors
SILENCE_PHONE: Final[str] = "SIL"
SELF_TRANSITION_PROB: Final[float] = 0.7
ADVANCE_PROB: Final[float] = 0.3
SILENCE_SKIP_PENALTY: Final[float] = 1.0

# Weights file location (relative to this module)
_WEIGHTS_DIR = Path(__file__).parent.parent.parent / "mahamantra_research" / "shabda_recognition"
_WEIGHTS_V2 = _WEIGHTS_DIR / "tiny_asr_weights_v2.npz"
_WEIGHTS_V1 = _WEIGHTS_DIR / "tiny_asr_weights.npz"


# =============================================================================
# DATA TYPES
# =============================================================================


@dataclass(frozen=True)
class AlignedWord:
    """A word with precise timing from forced alignment."""

    word: str
    phonemes: Tuple[str, ...]
    rama_coords: Tuple[int, ...]
    start_ms: int
    end_ms: int
    confidence: float


@dataclass(frozen=True)
class AlignmentResult:
    """Complete forced alignment result."""

    words: Tuple[AlignedWord, ...]
    frame_labels: Tuple[str, ...]  # per-frame phoneme label
    frame_words: Tuple[str, ...]  # per-frame word label
    phoneme_sequence: Tuple[str, ...]  # collapsed phoneme sequence
    duration_ms: int
    per: float  # phoneme error rate vs expected


# =============================================================================
# TINY ASR MODEL
# =============================================================================


class TinyASR:
    """Minimal 2-layer MLP for frame-level phoneme classification.

    Architecture: input_dim → 128 hidden (ReLU) → n_classes (softmax)
    Weights: seed-initialized from MAHA_QUANTUM=137, calibrated on audio.

    Input: log-Mel spectrogram with ±2 context frames (130D).
    Output: per-frame probability distribution over ARPAbet phonemes.
    """

    __slots__ = (
        "_W1",
        "_b1",
        "_W2",
        "_b2",
        "_X_mean",
        "_X_std",
        "_classes",
        "_class_to_idx",
        "_context",
    )

    def __init__(self, weights_path: Optional[Path] = None) -> None:
        """Load trained weights or initialize from seed."""
        path = weights_path or _WEIGHTS_V2
        if not path.exists():
            path = _WEIGHTS_V1
        if not path.exists():
            raise FileNotFoundError(
                f"No Tiny ASR weights found at {_WEIGHTS_V2} or {_WEIGHTS_V1}. "
                "Run experiment_38_viterbi_align.py first to generate weights."
            )

        data = np.load(str(path), allow_pickle=True)
        self._W1 = data["W1"]
        self._b1 = data["b1"]
        self._W2 = data["W2"]
        self._b2 = data["b2"]
        self._X_mean = data["X_mean"]
        self._X_std = data["X_std"]
        self._classes = list(data["classes"])
        self._context = int(data["context"])
        self._class_to_idx = {c: i for i, c in enumerate(self._classes)}

        logger.info(
            "TinyASR loaded: %d→%d→%d (%d params, ctx=±%d)",
            self._W1.shape[0],
            self._W1.shape[1],
            self._W2.shape[1],
            self._W1.size + self._b1.size + self._W2.size + self._b2.size,
            self._context,
        )

    @property
    def classes(self) -> List[str]:
        return list(self._classes)

    @property
    def n_classes(self) -> int:
        return len(self._classes)

    @property
    def context(self) -> int:
        return self._context

    def class_index(self, phone: str) -> Optional[int]:
        """Get class index for a phoneme, or None if unknown."""
        return self._class_to_idx.get(phone)

    def predict_probs(self, X_raw: np.ndarray) -> np.ndarray:
        """Predict phoneme probabilities for all frames.

        Args:
            X_raw: (N, n_mels) log-Mel features, NOT yet context-expanded.

        Returns:
            (N, n_classes) probability matrix.
        """
        X_ctx = _add_context(X_raw, self._context)
        X_norm = (X_ctx - self._X_mean) / self._X_std

        N = X_norm.shape[0]
        probs = np.zeros((N, self.n_classes))

        for i in range(N):
            h = np.maximum(0, X_norm[i] @ self._W1 + self._b1)
            logits = h @ self._W2 + self._b2
            e = np.exp(logits - logits.max())
            probs[i] = e / e.sum()

        return probs


# =============================================================================
# FEATURE EXTRACTION
# =============================================================================


def extract_log_mel(
    audio_frame: np.ndarray,
    sr: int = 44100,
    n_fft: int = N_FFT,
    n_mels: int = N_MELS,
) -> np.ndarray:
    """Extract log-Mel spectrogram from one audio frame."""
    if len(audio_frame) < n_fft:
        return np.zeros(n_mels)
    emphasized = np.append(audio_frame[0], audio_frame[1:] - 0.97 * audio_frame[:-1])
    windowed = emphasized[:n_fft] * np.hanning(n_fft)
    spec = np.abs(fft(windowed))[: n_fft // 2]
    power = (spec**2) / n_fft
    if np.sum(power) < 1e-10:
        return np.zeros(n_mels)
    fb = _mel_filterbank(sr, n_fft, n_mels)
    mel_energies = fb @ power
    mel_energies = np.maximum(mel_energies, 1e-10)
    return np.log(mel_energies)


def extract_mel_features(stream: ShabdaStream) -> np.ndarray:
    """Extract log-Mel features for all frames in a ShabdaStream.

    Returns: (N, N_MELS) array of log-Mel vectors.
    """
    sr = stream.sample_rate
    hop = int(sr * stream.hop_ms / 1000)
    n_frames = len(stream.frames)

    features = np.zeros((n_frames, N_MELS))

    if stream.raw_samples is None:
        logger.warning("No raw_samples in stream, returning zero features")
        return features

    for i in range(n_frames):
        start = i * hop
        end = start + stream.n_fft
        if end <= len(stream.raw_samples):
            features[i] = extract_log_mel(
                stream.raw_samples[start:end],
                sr,
                stream.n_fft,
                N_MELS,
            )

    return features


def _add_context(X: np.ndarray, ctx: int = CONTEXT_FRAMES) -> np.ndarray:
    """Stack ±ctx neighbor frames for temporal context."""
    N, D = X.shape
    X_ctx = np.zeros((N, (2 * ctx + 1) * D))
    for i in range(N):
        for k in range(-ctx, ctx + 1):
            j = max(0, min(N - 1, i + k))
            X_ctx[i, (k + ctx) * D : (k + ctx + 1) * D] = X[j]
    return X_ctx


# =============================================================================
# CMU PRONUNCIATION LOOKUP
# =============================================================================

# Inline pronunciation table for common words (no NLTK dependency on hot path).
# Extended at runtime via _load_cmu_pronunciations().
_BUILTIN_PRONUNCIATIONS: Final[Dict[str, Tuple[str, ...]]] = {
    "a": ("AH",),
    "an": ("AE", "N"),
    "the": ("DH", "AH"),
    "i": ("AY",),
    "is": ("IH", "Z"),
    "am": ("AE", "M"),
    "are": ("AA", "R"),
    "was": ("W", "AA", "Z"),
    "not": ("N", "AA", "T"),
    "but": ("B", "AH", "T"),
    "and": ("AE", "N", "D"),
    "or": ("AO", "R"),
    "to": ("T", "UW"),
    "of": ("AH", "V"),
    "in": ("IH", "N"),
    "it": ("IH", "T"),
    "he": ("HH", "IY"),
    "she": ("SH", "IY"),
    "we": ("W", "IY"),
    "you": ("Y", "UW"),
    "they": ("DH", "EY"),
    "this": ("DH", "IH", "S"),
    "that": ("DH", "AE", "T"),
    "so": ("S", "OW"),
    "yes": ("Y", "EH", "S"),
    "no": ("N", "OW"),
    "come": ("K", "AH", "M"),
    "came": ("K", "EY", "M"),
    "go": ("G", "OW"),
    "went": ("W", "EH", "N", "T"),
    "say": ("S", "EY"),
    "said": ("S", "EH", "D"),
    "preach": ("P", "R", "IY", "CH"),
    "preached": ("P", "R", "IY", "CH", "T"),
    "preaching": ("P", "R", "IY", "CH", "IH", "NG"),
    "gospel": ("G", "AA", "S", "P", "AH", "L"),
    "exactly": ("IH", "G", "Z", "AE", "K", "T", "L", "IY"),
    "consciousness": ("K", "AA", "N", "SH", "AH", "S", "N", "AH", "S"),
    "krishna": ("K", "R", "IH", "SH", "N", "AH"),
    "met": ("M", "EH", "T"),
    "some": ("S", "AH", "M"),
    "enthusiastic": ("EH", "N", "TH", "UW", "Z", "IY", "AE", "S", "T", "IH", "K"),
    "young": ("Y", "AH", "NG"),
    "boys": ("B", "OY", "Z"),
    "girls": ("G", "ER", "L", "Z"),
    "fortunately": ("F", "AO", "R", "CH", "AH", "N", "AH", "T", "L", "IY"),
    "eh": ("EH",),
    # Mahamantra words
    "hare": ("HH", "AA", "R", "EY"),
    "rama": ("R", "AA", "M", "AH"),
}

# Runtime-loaded CMU dict (lazy)
_CMU_DICT: Optional[Dict[str, Tuple[str, ...]]] = None


def _load_cmu_pronunciations() -> Dict[str, Tuple[str, ...]]:
    """Lazy-load CMU Pronouncing Dictionary via NLTK."""
    global _CMU_DICT
    if _CMU_DICT is not None:
        return _CMU_DICT

    _CMU_DICT = dict(_BUILTIN_PRONUNCIATIONS)

    try:
        from nltk.corpus import cmudict

        cmu = cmudict.dict()
        for word, pronunciations in cmu.items():
            if word not in _CMU_DICT:
                # Strip stress markers
                phones = tuple(p.rstrip("012") for p in pronunciations[0])
                _CMU_DICT[word] = phones
        logger.info("CMU dict loaded: %d entries", len(_CMU_DICT))
    except Exception:
        logger.warning("CMU dict not available, using builtin pronunciations only")

    return _CMU_DICT


def get_pronunciation(word: str) -> Optional[Tuple[str, ...]]:
    """Get ARPAbet pronunciation for a word."""
    pdict = _load_cmu_pronunciations()
    return pdict.get(word.lower())


# =============================================================================
# VITERBI FORCED ALIGNMENT
# =============================================================================


def _build_state_sequence(
    transcript: Sequence[str],
    pdict: Dict[str, Tuple[str, ...]],
) -> List[Tuple[str, str, str]]:
    """Build Viterbi state sequence from transcript words.

    Returns list of (phoneme, word, state_type) tuples.
    state_type is "phoneme" or "silence".
    """
    states: List[Tuple[str, str, str]] = []

    for wi, word in enumerate(transcript):
        if wi > 0:
            states.append((SILENCE_PHONE, "_pause_", "silence"))

        phones = pdict.get(word.lower())
        if phones is None:
            logger.warning("No pronunciation for '%s', skipping", word)
            continue

        for p in phones:
            states.append((p, word, "phoneme"))

    return states


def viterbi_align(
    frame_probs: np.ndarray,
    states: Sequence[Tuple[str, str, str]],
    class_to_idx: Dict[str, Optional[int]],
    hop_ms: int = 10,
) -> Tuple[np.ndarray, List[Tuple[int, str]]]:
    """Run Viterbi forced alignment.

    Args:
        frame_probs: (N, C) per-frame phoneme probabilities from TinyASR.
        states: State sequence from _build_state_sequence().
        class_to_idx: Mapping phoneme → class index (from TinyASR).
        hop_ms: Milliseconds per frame.

    Returns:
        state_path: (N,) array of state indices per frame.
        word_boundaries: List of (start_frame, word) tuples.
    """
    N = frame_probs.shape[0]
    S = len(states)

    if S == 0 or N == 0:
        return np.zeros(N, dtype=np.int32), []

    log_probs = np.log(frame_probs + 1e-30)
    log_self = np.log(SELF_TRANSITION_PROB)
    log_advance = np.log(ADVANCE_PROB)

    # Emission lookup
    def emission(t: int, s: int) -> float:
        phone = states[s][0]
        idx = class_to_idx.get(phone)
        if idx is not None:
            return log_probs[t, idx]
        return -10.0

    # Viterbi forward pass
    V = np.full((N, S), -np.inf)
    BP = np.zeros((N, S), dtype=np.int32)

    V[0, 0] = emission(0, 0)

    for t in range(1, N):
        for s in range(S):
            # Self-transition
            score_self = V[t - 1, s] + log_self + emission(t, s)

            # Advance from previous state
            score_adv = -np.inf
            if s > 0:
                score_adv = V[t - 1, s - 1] + log_advance + emission(t, s)

            if score_self >= score_adv:
                V[t, s] = score_self
                BP[t, s] = s
            else:
                V[t, s] = score_adv
                BP[t, s] = s - 1

            # Skip silence states (jump from s-2 to s over a silence)
            if s >= 2 and states[s - 1][2] == "silence":
                score_skip = V[t - 1, s - 2] + log_advance + emission(t, s) - SILENCE_SKIP_PENALTY
                if score_skip > V[t, s]:
                    V[t, s] = score_skip
                    BP[t, s] = s - 2

    # Backtrace — find best ending state
    best_end = S - 1
    for s in range(max(0, S - 5), S):
        if V[-1, s] > V[-1, best_end]:
            best_end = s

    state_path = np.zeros(N, dtype=np.int32)
    state_path[-1] = best_end

    for t in range(N - 2, -1, -1):
        state_path[t] = BP[t + 1, state_path[t + 1]]

    # Extract word boundaries
    word_boundaries: List[Tuple[int, str]] = []
    prev_word = ""
    for i in range(N):
        w = states[state_path[i]][1]
        if w != prev_word and w != "_pause_":
            word_boundaries.append((i, w))
            prev_word = w if w != "_pause_" else prev_word

    return state_path, word_boundaries


# =============================================================================
# PUBLIC API
# =============================================================================


def align_stream(
    stream: ShabdaStream,
    transcript: Sequence[str],
    model: Optional[TinyASR] = None,
) -> AlignmentResult:
    """Forced-align a ShabdaStream against a known transcript.

    This is the main entry point. Given audio and the words spoken in it,
    returns precise per-frame phoneme labels and word boundaries.

    Args:
        stream: Audio stream from ShabdaIntake.
        transcript: List of words in speaking order (e.g. ["not", "exactly", ...]).
        model: Pre-loaded TinyASR model (created if None).

    Returns:
        AlignmentResult with word timings, phoneme labels, and RAMA coords.
    """
    if model is None:
        model = TinyASR()

    # 1. Extract features
    mel_features = extract_mel_features(stream)

    # 2. Get emission probabilities
    frame_probs = model.predict_probs(mel_features)

    # 3. Build state sequence from transcript
    pdict = _load_cmu_pronunciations()
    states = _build_state_sequence(transcript, pdict)

    if not states:
        return AlignmentResult(
            words=(),
            frame_labels=(),
            frame_words=(),
            phoneme_sequence=(),
            duration_ms=stream.duration_ms,
            per=1.0,
        )

    # 4. Viterbi alignment
    c2i = {phone: model.class_index(phone) for phone, _, _ in states}
    state_path, word_boundaries = viterbi_align(frame_probs, states, c2i, stream.hop_ms)

    # 5. Extract results
    N = len(stream.frames)
    frame_labels = tuple(states[s][0] for s in state_path)
    frame_words = tuple(states[s][1] for s in state_path)

    # Collapse to phoneme sequence (skip silence)
    phoneme_seq: List[str] = []
    prev_p = ""
    for p in frame_labels:
        if p != prev_p and p != SILENCE_PHONE:
            phoneme_seq.append(p)
            prev_p = p
        elif p == SILENCE_PHONE:
            prev_p = p

    # Build expected phoneme sequence
    expected: List[str] = []
    for w in transcript:
        phones = pdict.get(w.lower())
        if phones:
            expected.extend(phones)

    per = _levenshtein(phoneme_seq, expected) / max(len(expected), 1)

    # Build AlignedWord list
    aligned_words: List[AlignedWord] = []
    for idx, (start_frame, word) in enumerate(word_boundaries):
        # Find end frame
        end_frame = start_frame
        while end_frame < N and frame_words[end_frame] == word:
            end_frame += 1

        # Get phonemes for this word
        phones = pdict.get(word.lower(), ())
        rama = tuple(ARPABET_TO_RAMA[p] for p in phones if p in ARPABET_TO_RAMA)

        # Confidence: average emission prob for correct phonemes in this span
        conf_sum = 0.0
        conf_count = 0
        for f in range(start_frame, min(end_frame, N)):
            phone = states[state_path[f]][0]
            ci = model.class_index(phone)
            if ci is not None:
                conf_sum += frame_probs[f, ci]
                conf_count += 1
        confidence = conf_sum / max(conf_count, 1)

        aligned_words.append(
            AlignedWord(
                word=word,
                phonemes=phones,
                rama_coords=rama,
                start_ms=start_frame * stream.hop_ms,
                end_ms=end_frame * stream.hop_ms,
                confidence=confidence,
            )
        )

    return AlignmentResult(
        words=tuple(aligned_words),
        frame_labels=frame_labels,
        frame_words=frame_words,
        phoneme_sequence=tuple(phoneme_seq),
        duration_ms=stream.duration_ms,
        per=per,
    )


def _levenshtein(s1: Sequence[str], s2: Sequence[str]) -> int:
    """Levenshtein edit distance between two sequences."""
    n, m = len(s1), len(s2)
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n + 1):
        dp[i][0] = i
    for j in range(m + 1):
        dp[0][j] = j
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            cost = 0 if s1[i - 1] == s2[j - 1] else 1
            dp[i][j] = min(dp[i - 1][j] + 1, dp[i][j - 1] + 1, dp[i - 1][j - 1] + cost)
    return dp[n][m]


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "TinyASR",
    "AlignedWord",
    "AlignmentResult",
    "align_stream",
    "extract_log_mel",
    "extract_mel_features",
    "get_pronunciation",
    "viterbi_align",
]
