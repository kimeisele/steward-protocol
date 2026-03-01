"""
CAPTCHA CHAMBER — Multi-Strategy Self-Experimenting Solver
==========================================================

"eka-cittena" — with one-pointed focus

Architecture: Generate → Score → Decide. No fallback chains. No API calls.

4 STRATEGIES decode the challenge text with different aggression levels.
  Each strategy tries multiple window sizes → up to 10 candidates total.
6 SCORERS evaluate each candidate answer for confidence.
CONSENSUS decides: high confidence → answer. Low confidence → None (skip).

None = "I don't know, skip this one."
Not "0". Not a guess. SKIP. Better to skip one comment than get banned.

Uses: RAMA phonemic coordinates (VarnaFilter, AksharaCollapse),
composition scoring pattern (additive, pluggable, observable).

NO LLM. NO EXTERNAL API. DETERMINISTIC.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from typing import Dict, Final, List, Optional, Sequence, Tuple

from vibe_core.mahamantra.substrate.core.basin_map import basin_cosine, hkr_similarity
from vibe_core.mahamantra.substrate.encoding.phonetic_encoder import encode_text

logger = logging.getLogger("CAPTCHA_CHAMBER")


# =============================================================================
# CONFIDENCE THRESHOLD
# =============================================================================

CONFIDENCE_THRESHOLD: Final[float] = 2.25  # Out of max 6.0 (37.5%)


# =============================================================================
# CANDIDATE
# =============================================================================


@dataclass
class CaptchaCandidate:
    """One candidate answer from one strategy."""

    answer: str  # "27"
    expression: str  # "23 + 4"
    decoded_text: str  # "twenty three plus four"
    strategy: str  # "collapse"
    scores: Dict[str, float] = field(default_factory=dict)
    total_score: float = 0.0


# =============================================================================
# MATH VOCABULARY (shared across all strategies)
# =============================================================================

_NUMBER_WORDS: Final[Dict[str, int]] = {
    "zero": 0,
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
    "eleven": 11,
    "twelve": 12,
    "thirteen": 13,
    "fourteen": 14,
    "fifteen": 15,
    "sixteen": 16,
    "seventeen": 17,
    "eighteen": 18,
    "nineteen": 19,
    "twenty": 20,
    "thirty": 30,
    "forty": 40,
    "fifty": 50,
    "sixty": 60,
    "seventy": 70,
    "eighty": 80,
    "ninety": 90,
    "hundred": 100,
    "thousand": 1000,
}

_OPERATOR_WORDS: Final[Dict[str, str]] = {
    "plus": "+",
    "add": "+",
    "sum": "+",
    "minus": "-",
    "subtract": "-",
    "difference": "-",
    "times": "*",
    "multiply": "*",
    "divided": "/",
    "divide": "/",
    "modulo": "%",
    "mod": "%",
    "remainder": "%",
}

_CONTEXT_WORDS: Final[Tuple[str, ...]] = (
    "total",
    "combined",
    "altogether",
    "together",
)


# =============================================================================
# RAMA VOCABULARY (pre-computed coordinates for matching)
# =============================================================================

_VOCAB_COORDS: Dict[str, Tuple[int, ...]] = {}
_VOCAB_COLLAPSED: Dict[str, str] = {}
_vocab_initialized: bool = False


def _ensure_vocab() -> None:
    """Pre-encode math vocabulary into RAMA coordinates. Lazy init."""
    global _vocab_initialized
    if _vocab_initialized:
        return
    all_words = list(_NUMBER_WORDS.keys()) + list(_OPERATOR_WORDS.keys()) + list(_CONTEXT_WORDS)
    for word in all_words:
        _VOCAB_COORDS[word] = encode_text(word)
        collapsed = _collapse_all(word)
        _VOCAB_COLLAPSED[collapsed] = word
        _VOCAB_COLLAPSED[word] = word
    _vocab_initialized = True


# =============================================================================
# SHARED PIPELINE STAGES (used by all strategies)
# =============================================================================


def _varna_filter(text: str) -> str:
    """RAMA phonemic noise strip. Alpha → lowercase, digits survive, rest → space."""
    result: list[str] = []
    for ch in text:
        if ch.isalpha():
            result.append(ch.lower())
        elif ch.isdigit():
            result.append(ch)
        else:
            result.append(" ")
    return " ".join("".join(result).split())


def _akshara_collapse(text: str) -> str:
    """Collapse runs of 3+ identical chars → single. Preserves doubles (ee in three)."""
    if len(text) < 3:
        return text
    result: list[str] = []
    i = 0
    while i < len(text):
        ch = text[i]
        j = i + 1
        while j < len(text) and text[j] == ch:
            j += 1
        run_len = j - i
        if run_len >= 3:
            result.append(ch)
        else:
            result.extend(ch for _ in range(run_len))
        i = j
    return "".join(result)


def _collapse_all(s: str) -> str:
    """Collapse ALL consecutive identical chars → single. 'foorty' → 'forty'."""
    if not s:
        return s
    result = [s[0]]
    for ch in s[1:]:
        if ch != result[-1]:
            result.append(ch)
    return "".join(result)


# =============================================================================
# PADA REASSEMBLY VARIANTS (differentiate strategies)
# =============================================================================


def _pada_exact(tokens: List[str], max_window: int = 6) -> List[str]:
    """Reassemble fragments using exact vocabulary match only."""
    _ensure_vocab()
    result: list[str] = []
    i = 0
    while i < len(tokens):
        best_word: Optional[str] = None
        best_len = 0
        for window in range(min(max_window, len(tokens) - i), 1, -1):
            candidate = "".join(tokens[i : i + window])
            if len(candidate) > 12:
                continue
            if candidate in _VOCAB_COORDS:
                best_word = candidate
                best_len = window
                break
        if best_word and best_len > 1:
            result.append(best_word)
            i += best_len
        else:
            result.append(tokens[i])
            i += 1
    return result


def _pada_collapse(tokens: List[str], max_window: int = 8) -> List[str]:
    """DP-based reassembly: maximize recognized token coverage, minimize segments.

    Unlike greedy, DP considers ALL segmentations to find the one that
    recognizes the most input tokens. This prevents greedy over-consumption
    (e.g. "times" eating 3 tokens when 2 suffice, stealing "s" from "seventeen").

    Objective: maximize (covered_tokens, -segment_count).
    covered_tokens = number of input tokens consumed by recognized matches.
    Fewer segments = longer compound matches preferred (e.g. "seventeen" > "seven"+"ten").
    """
    _ensure_vocab()
    n = len(tokens)
    if n == 0:
        return []

    # dp[i] = (score_tuple, word_list) for optimal segmentation of tokens[i:]
    # score_tuple = (covered_tokens, -segment_count)
    _WORST: tuple[int, int] = (-1, -n - 1)
    dp: list[tuple[tuple[int, int], list[str]]] = [(_WORST, [])] * (n + 1)
    dp[n] = ((0, 0), [])

    for i in range(n - 1, -1, -1):
        best_score = _WORST
        best_words: list[str] = []
        mw = min(max_window, n - i)

        for w in range(1, mw + 1):
            future_score, future_words = dp[i + w]
            if future_score == _WORST:
                continue

            candidate = "".join(tokens[i : i + w])
            if len(candidate) > 14:
                continue

            word: Optional[str] = None
            is_rec = False

            # Exact match
            if candidate in _VOCAB_COORDS:
                word = candidate
                is_rec = True
            else:
                # Collapse match
                collapsed = _collapse_all(candidate)
                if collapsed in _VOCAB_COLLAPSED:
                    word = _VOCAB_COLLAPSED[collapsed]
                    is_rec = True

            if word is None:
                word = candidate

            covered = (w if is_rec else 0) + future_score[0]
            segs = -1 + future_score[1]
            score = (covered, segs)

            if score > best_score:
                best_score = score
                best_words = [word] + future_words

        dp[i] = (best_score, best_words)

    result = dp[0][1]

    # Post-process: fix corrupted individual tokens
    final: list[str] = []
    for w in result:
        if w in _VOCAB_COORDS:
            final.append(w)
        else:
            collapsed = _collapse_all(w)
            if collapsed in _VOCAB_COLLAPSED:
                final.append(_VOCAB_COLLAPSED[collapsed])
            else:
                final.append(w)
    return final


def _pada_aggressive(tokens: List[str], max_window: int = 10) -> List[str]:
    """DP-based aggressive reassembly: collapse + RAMA fuzzy for unmatched tokens."""
    _ensure_vocab()
    n = len(tokens)
    if n == 0:
        return []

    # DP: same objective as _pada_collapse but with RAMA fuzzy for single tokens
    _WORST: tuple[int, int] = (-1, -n - 1)
    dp: list[tuple[tuple[int, int], list[str]]] = [(_WORST, [])] * (n + 1)
    dp[n] = ((0, 0), [])

    for i in range(n - 1, -1, -1):
        best_score = _WORST
        best_words: list[str] = []
        mw = min(max_window, n - i)

        for w in range(1, mw + 1):
            future_score, future_words = dp[i + w]
            if future_score == _WORST:
                continue

            candidate = "".join(tokens[i : i + w])
            if len(candidate) > 16:
                continue

            word: Optional[str] = None
            is_rec = False

            # Exact match
            if candidate in _VOCAB_COORDS:
                word = candidate
                is_rec = True
            else:
                # Collapse match
                collapsed = _collapse_all(candidate)
                if collapsed in _VOCAB_COLLAPSED:
                    word = _VOCAB_COLLAPSED[collapsed]
                    is_rec = True

            # RAMA fuzzy (only for single long tokens with no other match)
            if word is None and w == 1 and len(tokens[i]) >= 6:
                coords = encode_text(tokens[i])
                if len(coords) >= 5:
                    best_sim = 0.95
                    for vword, vcoords in _VOCAB_COORDS.items():
                        if abs(len(coords) - len(vcoords)) > 1:
                            continue
                        sim = 0.4 * basin_cosine(coords, vcoords) + 0.6 * hkr_similarity(coords, vcoords)
                        if sim > best_sim:
                            best_sim = sim
                            word = vword
                            is_rec = True

            if word is None:
                word = candidate

            covered = (w if is_rec else 0) + future_score[0]
            segs = -1 + future_score[1]
            score = (covered, segs)

            if score > best_score:
                best_score = score
                best_words = [word] + future_words

        dp[i] = (best_score, best_words)

    result = dp[0][1]

    # Post-process
    final: list[str] = []
    for w in result:
        if w in _VOCAB_COORDS:
            final.append(w)
        else:
            collapsed = _collapse_all(w)
            if collapsed in _VOCAB_COLLAPSED:
                final.append(_VOCAB_COLLAPSED[collapsed])
            else:
                final.append(w)
    return final


# =============================================================================
# COMPOUND NUMBER MERGE
# =============================================================================

_TENS_WORDS: Final[frozenset[str]] = frozenset(
    {
        "twenty",
        "thirty",
        "forty",
        "fifty",
        "sixty",
        "seventy",
        "eighty",
        "ninety",
    }
)
_ONES_WORDS: Final[frozenset[str]] = frozenset(
    {
        "one",
        "two",
        "three",
        "four",
        "five",
        "six",
        "seven",
        "eight",
        "nine",
    }
)


def _merge_compounds(words: List[str]) -> List[str]:
    """Merge adjacent tens + ones into hyphenated compounds.

    After varna_filter strips hyphens, "eighty-four" → ["eighty", "four"].
    This step restores them: ["eighty", "four"] → ["eighty-four"].
    ChallengeSolver._normalize_text then handles "eighty-four" → "84".
    """
    result: list[str] = []
    i = 0
    while i < len(words):
        if i + 1 < len(words) and words[i] in _TENS_WORDS and words[i + 1] in _ONES_WORDS:
            result.append(f"{words[i]}-{words[i + 1]}")
            i += 2
        else:
            result.append(words[i])
            i += 1
    return result


# =============================================================================
# MATH EXTRACTION (shared)
# =============================================================================


def _extract_math(decoded_text: str) -> Optional[str]:
    """Extract math expression from decoded text.

    Each strategy is responsible for its own domain:
    - Pada strategies decode obfuscated text → this function extracts math from decoded words.
    - Direct strategy handles raw text via ChallengeSolver.solve() separately.

    Uses ChallengeSolver._normalize_text for word→digit conversion,
    then tries word-problem extraction with operation inference.
    """
    from vibe_core.mahamantra.adapters.moltbook import ChallengeSolver

    # Path 1: Decoded text normalization
    expr = ChallengeSolver._normalize_text(decoded_text)
    if expr:
        result = ChallengeSolver._safe_eval(expr)
        if result is not None:
            return expr

    # Path 3: Word problem — extract numbers, infer operation
    search_text = expr if expr else decoded_text
    numbers = re.findall(r"\d+\.?\d*", search_text)
    if not numbers:
        return None
    if len(numbers) == 1:
        return numbers[0]

    text_lower = decoded_text.lower()

    # Explicit operator words trump context words
    _EXP_MINUS = ("minus", "subtract")
    _EXP_TIMES = ("times", "multiply")
    _EXP_DIV = ("divided", "divide")
    _EXP_PLUS = ("plus", "add")
    if any(w in text_lower for w in _EXP_MINUS):
        return " - ".join(numbers)
    if any(w in text_lower for w in _EXP_TIMES):
        return " * ".join(numbers)
    if any(w in text_lower for w in _EXP_DIV):
        return " / ".join(numbers)
    if any(w in text_lower for w in _EXP_PLUS):
        return " + ".join(numbers)

    # Context words (no explicit operator found)
    _SUM = ("total", "sum", "altogether", "combined", "together", "all", "both")
    _DIFF = ("difference", "less", "fewer", "remaining", "left")
    _PROD = ("product",)
    if any(w in text_lower for w in _SUM):
        return " + ".join(numbers)
    if any(w in text_lower for w in _DIFF):
        return " - ".join(numbers)
    if any(w in text_lower for w in _PROD):
        return " * ".join(numbers)

    # No operator found → ambiguous. Return None, let _strategy_direct handle clean captchas.
    return None


def _safe_eval(expr: str) -> Optional[str]:
    """Evaluate expression → answer string. None if invalid."""
    from vibe_core.mahamantra.adapters.moltbook import ChallengeSolver

    result = ChallengeSolver._safe_eval(expr)
    if result is None:
        return None
    if isinstance(result, float) and result == int(result):
        return str(int(result))
    return str(result)


# =============================================================================
# STRATEGIES
# =============================================================================


def _strategy_exact(challenge: str) -> List[CaptchaCandidate]:
    """Conservative: exact vocab match only. Windows: 4, 6, 8."""
    clean = _varna_filter(challenge)
    clean = _akshara_collapse(clean)
    tokens = clean.split()
    results: list[CaptchaCandidate] = []
    seen_answers: set[str] = set()
    for w in (4, 6, 8):
        words = _merge_compounds(_pada_exact(tokens, max_window=w))
        decoded = " ".join(words)
        expr = _extract_math(decoded)
        if not expr:
            continue
        answer = _safe_eval(expr)
        if answer is None or answer in seen_answers:
            continue
        seen_answers.add(answer)
        results.append(
            CaptchaCandidate(
                answer=answer,
                expression=expr,
                decoded_text=decoded,
                strategy=f"exact_w{w}",
            )
        )
    return results


def _strategy_collapse(challenge: str) -> List[CaptchaCandidate]:
    """Moderate: exact-first + collapse-all matching. Windows: 6, 8, 10."""
    clean = _varna_filter(challenge)
    clean = _akshara_collapse(clean)
    tokens = clean.split()
    results: list[CaptchaCandidate] = []
    seen_answers: set[str] = set()
    for w in (6, 8, 10):
        words = _merge_compounds(_pada_collapse(tokens, max_window=w))
        decoded = " ".join(words)
        expr = _extract_math(decoded)
        if not expr:
            continue
        answer = _safe_eval(expr)
        if answer is None or answer in seen_answers:
            continue
        seen_answers.add(answer)
        results.append(
            CaptchaCandidate(
                answer=answer,
                expression=expr,
                decoded_text=decoded,
                strategy=f"collapse_w{w}",
            )
        )
    return results


def _strategy_aggressive(challenge: str) -> List[CaptchaCandidate]:
    """Aggressive: wide window, collapse, RAMA fuzzy. Windows: 8, 10, 12."""
    clean = _varna_filter(challenge)
    clean = _akshara_collapse(clean)
    tokens = clean.split()
    results: list[CaptchaCandidate] = []
    seen_answers: set[str] = set()
    for w in (8, 10, 12):
        words = _merge_compounds(_pada_aggressive(tokens, max_window=w))
        decoded = " ".join(words)
        expr = _extract_math(decoded)
        if not expr:
            continue
        answer = _safe_eval(expr)
        if answer is None or answer in seen_answers:
            continue
        seen_answers.add(answer)
        results.append(
            CaptchaCandidate(
                answer=answer,
                expression=expr,
                decoded_text=decoded,
                strategy=f"aggressive_w{w}",
            )
        )
    return results


def _strategy_direct(challenge: str) -> List[CaptchaCandidate]:
    """Direct: ChallengeSolver on raw text. For clean captchas."""
    from vibe_core.mahamantra.adapters.moltbook import ChallengeSolver

    result = ChallengeSolver.solve(challenge)
    if result == "0":
        return []
    return [
        CaptchaCandidate(
            answer=result,
            expression="(direct)",
            decoded_text=challenge,
            strategy="direct",
        )
    ]


_STRATEGIES = (_strategy_exact, _strategy_collapse, _strategy_aggressive, _strategy_direct)


# =============================================================================
# SCORERS
# =============================================================================


def _score_expression(candidate: CaptchaCandidate, _challenge: str) -> float:
    """Valid math expression with 2+ numbers and operator → high score."""
    expr = candidate.expression
    if expr == "(direct)":
        return 0.6  # Direct solve — moderate confidence
    numbers = re.findall(r"\d+\.?\d*", expr)
    has_operator = bool(re.search(r"[+\-*/%]", expr))
    if len(numbers) >= 2 and has_operator:
        return 1.0
    if len(numbers) == 1:
        return 0.3
    return 0.0


def _score_consensus(
    candidate: CaptchaCandidate, _challenge: str, all_candidates: Sequence[CaptchaCandidate] = ()
) -> float:
    """How many strategies agree on this answer?

    Single candidate = 0.25 (consensus of 1 is meaningless).
    Requires at least 2 candidates agreeing for meaningful consensus.
    """
    if len(all_candidates) < 2:
        return 0.25
    agree = sum(1 for c in all_candidates if c.answer == candidate.answer)
    return agree / len(all_candidates)


def _score_range(candidate: CaptchaCandidate, _challenge: str) -> float:
    """Is the answer in a reasonable range for a captcha?"""
    try:
        val = float(candidate.answer)
    except (ValueError, TypeError):
        return 0.0
    if val < 0 or val > 100000:
        return 0.0
    if val != int(val):
        return 0.5  # Decimal — captchas usually want integers
    if 0 <= val <= 10000:
        return 1.0
    return 0.5


def _is_number_word(word: str) -> bool:
    """Check if word is a recognized number (simple or compound)."""
    if word in _NUMBER_WORDS or word.isdigit():
        return True
    if "-" in word:
        parts = word.split("-", 1)
        if len(parts) == 2 and parts[0] in _NUMBER_WORDS and parts[1] in _NUMBER_WORDS:
            return True
    return False


def _score_completeness(candidate: CaptchaCandidate, _challenge: str) -> float:
    """Did the decoder find a sensible math structure?

    Context words ('total', 'combined') count as operator signals —
    they imply addition. Expressions with 4+ numbers are penalized
    (captchas are simple: A op B, not A + B + C + D).
    """
    text = candidate.decoded_text.lower()
    found_numbers = 0
    found_operator = False
    for word in text.split():
        if _is_number_word(word):
            found_numbers += 1
        if word in _OPERATOR_WORDS or word in _CONTEXT_WORDS:
            found_operator = True

    # Penalize expressions with too many numbers (false positive signal)
    expr_numbers = re.findall(r"\d+\.?\d*", candidate.expression)
    if len(expr_numbers) >= 4:
        return 0.3  # Suspicious: captchas are simple

    if found_numbers >= 2 and found_operator:
        return 1.0
    if found_numbers >= 1:
        return 0.5
    return 0.0


def _score_decode_fidelity(candidate: CaptchaCandidate, _challenge: str) -> float:
    """Fraction of decoded words recognized as math vocabulary.

    Higher = better decode quality. Fragments like 'e i g h t' score low.
    Recognized numbers, operators, context words, and compound numbers
    (e.g., 'eighty-four') all count. Direct strategy → 0.6 baseline.
    """
    if candidate.strategy == "direct":
        return 0.6
    words = candidate.decoded_text.lower().split()
    if not words:
        return 0.0
    recognized = 0
    for w in words:
        if _is_number_word(w):
            recognized += 1
        elif w in _OPERATOR_WORDS or w in _CONTEXT_WORDS:
            recognized += 1
    return min(recognized / len(words), 1.0)


def _score_structural_conformity(candidate: CaptchaCandidate, _challenge: str) -> float:
    """Does expression follow captcha convention (A op B)?

    2 numbers + 1 operator → 1.0 (standard captcha).
    Single number → 0.3 (unusual but possible).
    3+ numbers → 0.2 (suspicious complexity).
    Direct strategy → 0.6 baseline.
    """
    expr = candidate.expression
    if expr == "(direct)":
        return 0.6
    numbers = re.findall(r"\d+\.?\d*", expr)
    has_operator = bool(re.search(r"[+\-*/%]", expr))
    if len(numbers) == 2 and has_operator:
        return 1.0
    if len(numbers) == 1:
        return 0.3
    if len(numbers) >= 3:
        return 0.2
    return 0.0


# =============================================================================
# CAPTCHA CHAMBER — Orchestrator
# =============================================================================


class CaptchaChamber:
    """Multi-strategy self-experimenting captcha solver.

    Generate candidates → Score → Decide. No fallback chains. No API calls.
    Returns Optional[str]: answer with high confidence, or None to skip.

    Architecture follows MahaComposition pattern:
    - Strategies are pluggable (add/remove without touching core)
    - Scorers are additive (each contributes 0.0–1.0)
    - Confidence threshold gates submission (below → None → skip)
    """

    @classmethod
    def solve(cls, challenge_text: str) -> Optional[str]:
        """Solve challenge or return None if confidence too low.

        None means: "I don't know, skip this comment."
        This prevents wrong submissions that count toward a ban.
        """
        if not challenge_text or not challenge_text.strip():
            return None

        # Generate candidates from all strategies (each returns a list)
        candidates: list[CaptchaCandidate] = []
        for strategy_fn in _STRATEGIES:
            try:
                results = strategy_fn(challenge_text)
                candidates.extend(results)
            except Exception as exc:
                logger.debug("Strategy %s failed: %s", strategy_fn.__name__, exc)

        if not candidates:
            return None

        # Score each candidate
        for candidate in candidates:
            candidate.scores["expression"] = _score_expression(candidate, challenge_text)
            candidate.scores["consensus"] = _score_consensus(
                candidate,
                challenge_text,
                all_candidates=candidates,
            )
            candidate.scores["range"] = _score_range(candidate, challenge_text)
            candidate.scores["completeness"] = _score_completeness(candidate, challenge_text)
            candidate.scores["decode_fidelity"] = _score_decode_fidelity(candidate, challenge_text)
            candidate.scores["structural_conformity"] = _score_structural_conformity(candidate, challenge_text)
            candidate.total_score = sum(candidate.scores.values())

        # Sort by total score, pick best
        candidates.sort(key=lambda c: c.total_score, reverse=True)
        best = candidates[0]

        logger.debug(
            "CaptchaChamber: best=%s score=%.2f scores=%s strategies=%d",
            best.answer,
            best.total_score,
            best.scores,
            len(candidates),
        )

        if best.total_score < CONFIDENCE_THRESHOLD:
            logger.warning(
                "CaptchaChamber: low confidence (%.2f < %.2f), skipping. Best candidate: answer=%s strategy=%s",
                best.total_score,
                CONFIDENCE_THRESHOLD,
                best.answer,
                best.strategy,
            )
            return None

        return best.answer


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "CaptchaChamber",
    "CaptchaCandidate",
    "CONFIDENCE_THRESHOLD",
]
