"""
WORDNET BRIDGE — Semantic Graph Layer for Resonance Ranking
============================================================

"nāma cintāmaṇiḥ" — The Name is the touchstone.

The existing resonance ranker works in 7 dimensions — all phonetic/structural.
This module adds the 8th dimension: SEMANTIC GRAPH DISTANCE via WordNet.

ARCHITECTURE:
    WordNet = 117K synsets linked by hypernym/hyponym edges = a GRAPH.
    Each Gita word's English meaning → WordNet synset(s) → position in graph.
    Each user input → English tokens → WordNet synset(s) → position in graph.
    Semantic similarity = Jaccard overlap of hypernym ancestor chains.

    This is NOT pattern matching. This is GRAPH DISTANCE.

DATA (precomputed, data/wordnet_bridge.json, 446 KB):
    - "synsets": list of 4259 synset IDs (index → string ID)
    - "words": {packed_hex: {"t": [tokens], "d": [direct synset ints], "c": [chain ints]}}
    - "d" = direct synsets the word belongs to
    - "c" = full hypernym ancestor chain (precomputed, all ancestors to root)
    - Chain Jaccard = set overlap on integer arrays. No WN runtime needed.

RUNTIME (zero external dependencies):
    1. Load bridge data → integer chain sets (once, ~1ms)
    2. Input tokens → exact match against stored tokens (Layer 1)
    3. Input tokens → inverse index (token→chain ints) → Jaccard overlap (Layer 2)
    4. Input stems → morphological overlap (Layer 3)

NO HARDCODED LISTS. NO PATTERN MATCHING. PURE GRAPH MATHEMATICS.
Built from Open English WordNet (BSD license, 117K synsets).
"""

from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Dict, Final, FrozenSet, List, Optional, Sequence, Set

from vibe_core.mahamantra.protocols._seed import PARAMPARA

__mahajana__ = "narada"
__position__ = 2
__genesis__ = "0x2c80316d"

assert int(__genesis__, 16) % PARAMPARA == 0, "BROKEN LINEAGE"

# =============================================================================
# DATA
# =============================================================================

from vibe_core.mahamantra.substrate._paths import DATA_DIR

_DATA_PATH: Final[Path] = DATA_DIR / "wordnet_bridge.json"

# Loaded state
_synset_list: Optional[List[str]] = None  # index → synset_id
_sid_to_int: Optional[Dict[str, int]] = None  # synset_id → index
_word_entries: Optional[Dict[str, dict]] = None  # packed_hex → entry
_word_chain_sets: Dict[str, FrozenSet[int]] = {}  # packed_hex → frozenset of ints
_token_to_chains: Optional[Dict[str, FrozenSet[int]]] = None  # inverse index: token → chain ints


def _ensure_loaded() -> None:
    """Load bridge data. Fast — no WN dependency, pure JSON."""
    global _synset_list, _sid_to_int, _word_entries
    if _word_entries is not None:
        return

    if not _DATA_PATH.exists():
        _synset_list = []
        _sid_to_int = {}
        _word_entries = {}
        return

    with open(_DATA_PATH) as f:
        raw = json.load(f)

    _synset_list = raw.get("synsets", [])
    _sid_to_int = {sid: i for i, sid in enumerate(_synset_list)}
    _word_entries = raw.get("words", {})


def _get_word_chain(packed_hex: str) -> FrozenSet[int]:
    """Get precomputed chain for a Gita word. O(1) after first call."""
    if packed_hex in _word_chain_sets:
        return _word_chain_sets[packed_hex]

    _ensure_loaded()
    entry = _word_entries.get(packed_hex)
    if not entry or "c" not in entry:
        result: FrozenSet[int] = frozenset()
    else:
        result = frozenset(entry["c"])

    _word_chain_sets[packed_hex] = result
    return result


def _build_token_index() -> Dict[str, FrozenSet[int]]:
    """Build inverse index: English token → chain integers from pre-baked data.

    2199 unique tokens, all from Gita word meanings. No external dependency.
    """
    _ensure_loaded()
    idx: Dict[str, Set[int]] = {}
    for entry in (_word_entries or {}).values():
        chains = entry.get("c", [])
        for t in entry.get("t", []):
            if t not in idx:
                idx[t] = set()
            idx[t].update(chains)
    return {k: frozenset(v) for k, v in idx.items()}


def _get_token_index() -> Dict[str, FrozenSet[int]]:
    """Lazy singleton for the token→chain inverse index."""
    global _token_to_chains
    if _token_to_chains is None:
        _token_to_chains = _build_token_index()
    return _token_to_chains


# =============================================================================
# INPUT PROCESSING
# =============================================================================

_TOKEN_RE = re.compile(r"[a-zA-Z]{3,}")


def _input_tokens(text: str) -> List[str]:
    """Extract meaningful English tokens from input text."""
    return [m.group().lower() for m in _TOKEN_RE.finditer(text)]


@lru_cache(maxsize=256)
def _input_chain_ints(text: str) -> FrozenSet[int]:
    """Build integer chain for user input from pre-baked inverse index.

    No external dependency. Uses token→chain mapping built from
    the same wordnet_bridge.json that stores Gita word data.
    """
    tokens = _input_tokens(text)
    if not tokens:
        return frozenset()

    idx = _get_token_index()
    combined: Set[int] = set()
    for token in tokens:
        chains = idx.get(token)
        if chains:
            combined.update(chains)
    return frozenset(combined)


@lru_cache(maxsize=256)
def _input_stems(text: str) -> FrozenSet[str]:
    """Extract morphological stems from input (min 4 chars)."""
    tokens = _input_tokens(text)
    stems: Set[str] = set()
    for t in tokens:
        stems.add(t)
        if len(t) >= 4:
            stems.add(t[:4])
    return frozenset(stems)


# =============================================================================
# SCORING
# =============================================================================


def semantic_score(text: str, packed_hex: str) -> float:
    """
    Semantic similarity between input text and a Gita word.

    Three layers (highest wins):
        Layer 1 — EXACT: Input token in Gita word's English meaning → 1.0
        Layer 2 — GRAPH: Jaccard of hypernym chains (integers) → [0, 0.8]
        Layer 3 — MORPH: Shared morphological stems → [0, 0.5]

    Returns: score in [0, 1].
    """
    _ensure_loaded()
    entry = _word_entries.get(packed_hex)
    if not entry:
        return 0.0

    word_tokens = set(entry.get("t", []))
    input_toks = set(_input_tokens(text))

    if not input_toks:
        return 0.0

    # Layer 1: EXACT token match
    exact = input_toks & word_tokens
    if exact:
        return min(1.0, len(exact) / len(input_toks))

    # Layer 2: GRAPH (integer chain Jaccard)
    if "c" in entry:
        ic = _input_chain_ints(text)
        if ic:
            wc = _get_word_chain(packed_hex)
            if wc:
                inter = len(ic & wc)
                union = len(ic | wc)
                if union > 0:
                    jaccard = inter / union
                    if jaccard > 0.01:
                        return min(0.8, jaccard * 2.0)

    # Layer 3: MORPH stem overlap
    stems = _input_stems(text)
    word_stems = frozenset(t[:4] for t in word_tokens if len(t) >= 4) | word_tokens
    morph = stems & word_stems
    if morph:
        return min(0.5, len(morph) * 0.15)

    return 0.0


def semantic_scores_batch(
    text: str,
    packed_hexes: Sequence[str],
) -> List[float]:
    """Score multiple Gita words against input text."""
    _ensure_loaded()
    input_toks = set(_input_tokens(text))
    if not input_toks:
        return [0.0] * len(packed_hexes)

    # Precompute once
    ic = _input_chain_ints(text)
    stems = _input_stems(text)

    scores: List[float] = []
    for phex in packed_hexes:
        entry = _word_entries.get(phex)
        if not entry:
            scores.append(0.0)
            continue

        word_tokens = set(entry.get("t", []))

        # Layer 1
        exact = input_toks & word_tokens
        if exact:
            scores.append(min(1.0, len(exact) / len(input_toks)))
            continue

        # Layer 2
        if ic and "c" in entry:
            wc = _get_word_chain(phex)
            if wc:
                inter = len(ic & wc)
                union = len(ic | wc)
                if union > 0:
                    j = inter / union
                    if j > 0.01:
                        scores.append(min(0.8, j * 2.0))
                        continue

        # Layer 3
        word_stems = frozenset(t[:4] for t in word_tokens if len(t) >= 4) | word_tokens
        morph = stems & word_stems
        if morph:
            scores.append(min(0.5, len(morph) * 0.15))
            continue

        scores.append(0.0)

    return scores


# =============================================================================
# DIAGNOSTIC
# =============================================================================


def diagnose(text: str, top_n: int = 10) -> None:
    """Print semantic analysis for debugging."""
    from vibe_core.mahamantra.substrate.semantic_index import get_index

    idx = get_index()
    idx._ensure_loaded()

    tokens = _input_tokens(text)
    chain = _input_chain_ints(text)

    print(f'Input: "{text}"')
    print(f"Tokens: {tokens}")
    print(f"Chain size: {len(chain)} integer nodes")
    print(f"Token index size: {len(_get_token_index())}")
    print()

    results = []
    for word in idx.words:
        score = semantic_score(text, word.packed_hex)
        if score > 0:
            meaning = word.meanings[0] if word.meanings else "?"
            results.append((word.sanskrit, meaning, score))

    results.sort(key=lambda x: x[2], reverse=True)
    print(f"{'Sanskrit':20s} {'Meaning':35s} {'Score':>6s}")
    print("─" * 65)
    for s, m, sc in results[:top_n]:
        print(f"{s:20s} {m:35s} {sc:6.3f}")
    print(f"\nTotal with score > 0: {len(results)}")
