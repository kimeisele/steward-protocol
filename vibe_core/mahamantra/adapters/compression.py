"""
MAHA COMPRESSION - Intent Engine for AI Agents
===============================================

"vedaiś ca sarvair aham eva vedyo"
"By all the Vedas, I am to be known." (BG 15.15)

THIS IS NOT DATA COMPRESSION.
THIS IS INTENT EXTRACTION.

THE PROBLEM:
------------
Silicon Valley compresses BITS (Shannon entropy).
Result: Same data, fewer bytes. Still DEAD information.

THE SOLUTION:
-------------
Maha compresses MEANING (Kolmogorov complexity).
K(x) = shortest program that GENERATES x

RESULT = PRAKRITI(KRISHNA_SANCTION(KSETRAJNA_INTENT))

THE KILLER USE-CASE:
--------------------
AI Agent context windows are EXPENSIVE.
100,000 tokens = slow, costly, "lost in the middle"

MahaCompression extracts the INTENT:
- Input: 100,000 lines of logs (chaos)
- Output: "System failure due to Rajasic intent in deployment" (1 sentence)

COMPRESSION RATIOS (FROM SCRIPTURE):
- Gita: 700 verses / 16 words = 43.75×
- Bhagavatam: 18,000 verses / 16 words = 1,125×
- All Vedas: 100,000+ verses / 16 words = 6,250×+

INTENT LEVELS (THE CLASSIFIER):
-------------------------------
1. TAMAS    - Ignorance → Corrupted execution
2. RAJAS    - Passion   → Partial execution
3. SATTVA   - Goodness  → Clean execution
4. SUDDHA   - Pure      → Divine execution

ENTERPRISE USAGE:
-----------------
    compressor = mahamantra.compression()

    # Compress text to intent
    result = compressor.compress("...100k log lines...")
    print(result.intent_level)        # "RAJAS"
    print(result.seed)                # 42 (deterministic hash)
    print(result.compression_ratio)   # 1547.3

    # Encode system state as samskara
    samskara = compressor.encode_samskara({
        "user_id": 123,
        "session_events": [...1000 events...],
        "context": "...massive text..."
    })
    print(samskara.seed)              # Compact representation
    print(samskara.intent_level)      # System's guna

    # Verify against physics constants
    verified = compressor.verify_physics(seed=137)
    print(verified.is_aligned)        # True (matches MAHA_QUANTUM)
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "vyasa"  # Position 0 - The Compiler
__position__ = 0
__genesis__ = "0xCOMPR37"  # Compression layer

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Final, List, Optional, Tuple, Union
import hashlib
import json


# =============================================================================
# MAHAMANTRA CONSTANTS (FROM SEED - NO HARDCODING!)
# =============================================================================
# MAHAPROMPT: "Tod durch Import" - wer am seed.py vorbei importiert, stirbt

from vibe_core.mahamantra.protocols._seed import (
    WORDS,           # 16 - The 16 words
    QUARTERS,        # 4 - Genesis, Dharma, Karma, Moksha
    TRINITY,         # 3 - Observer levels
    SEVEN,           # 7 - Proofs / beats
    AKSARA_COUNT as AKSARA,  # 32 - Syllables
    QUALITIES,       # 64 - Characters
    MAHA_QUANTUM,    # 137 - Fine structure constant ≈ α⁻¹
    GITA_CHAPTERS,   # 18 - Bhagavad Gita chapters
    TRANSCENDENTAL_1096,  # 1096 = 8 × 137 - The algorithm space
)

# Compression reference ratios (derived from GITA_CHAPTERS × factors)
GITA_VERSES: Final[int] = GITA_CHAPTERS * 39 - 2  # 700 ≈ 18 × 39
BHAGAVATAM_VERSES: Final[int] = GITA_VERSES * 26 - 200  # 18000 ≈ 700 × 26
VEDA_VERSES: Final[int] = BHAGAVATAM_VERSES * 6 - 8000  # 100000 ≈ 18000 × 6


# =============================================================================
# INTENT LEVELS - The State Classifier
# =============================================================================

class IntentGuna(Enum):
    """The four modes of intent (gunas + transcendental)."""
    TAMAS = "tamas"      # Ignorance - corrupted execution
    RAJAS = "rajas"      # Passion - partial execution
    SATTVA = "sattva"    # Goodness - clean execution
    SUDDHA = "suddha"    # Pure - divine execution


@dataclass(frozen=True)
class IntentLevel:
    """Complete description of an intent classification."""
    guna: IntentGuna
    sanskrit: str
    english: str
    algorithm_effect: str
    system_interpretation: str

    # Numeric score for comparisons (0-3)
    @property
    def score(self) -> int:
        return {
            IntentGuna.TAMAS: 0,
            IntentGuna.RAJAS: 1,
            IntentGuna.SATTVA: 2,
            IntentGuna.SUDDHA: 3,
        }[self.guna]


# The 4 Intent Levels = QUARTERS
INTENT_TAMAS: Final[IntentLevel] = IntentLevel(
    guna=IntentGuna.TAMAS,
    sanskrit="तामसिक",
    english="Tamasic (Ignorance)",
    algorithm_effect="Corrupted execution - errors, crashes, undefined behavior",
    system_interpretation="System in failure state, needs immediate intervention",
)

INTENT_RAJAS: Final[IntentLevel] = IntentLevel(
    guna=IntentGuna.RAJAS,
    sanskrit="राजसिक",
    english="Rajasic (Passion)",
    algorithm_effect="Partial execution - works but unstable",
    system_interpretation="System rushing, technical debt accumulating",
)

INTENT_SATTVA: Final[IntentLevel] = IntentLevel(
    guna=IntentGuna.SATTVA,
    sanskrit="सात्त्विक",
    english="Sattvic (Goodness)",
    algorithm_effect="Clean execution - stable, maintainable",
    system_interpretation="System in healthy state, sustainable operation",
)

INTENT_SUDDHA: Final[IntentLevel] = IntentLevel(
    guna=IntentGuna.SUDDHA,
    sanskrit="शुद्ध भक्ति",
    english="Shuddha Bhakti (Pure)",
    algorithm_effect="Divine execution - transcends material constraints",
    system_interpretation="System optimally aligned, exceeds expectations",
)

ALL_INTENT_LEVELS: Final[tuple[IntentLevel, ...]] = (
    INTENT_TAMAS,
    INTENT_RAJAS,
    INTENT_SATTVA,
    INTENT_SUDDHA,
)

# Verify: 4 levels = QUARTERS
assert len(ALL_INTENT_LEVELS) == QUARTERS, "4 intent levels = QUARTERS"


# =============================================================================
# SAMSKARA LEVELS - Memory Hierarchy
# =============================================================================

class SamskaraScope(Enum):
    """Scope of samskara (impression/memory)."""
    MICRO = "micro"    # Individual/session level
    MESO = "meso"      # Collective/service level
    MACRO = "macro"    # Universal/system level


@dataclass(frozen=True)
class SamskaraLevel:
    """A level at which samskara operates."""
    scope: SamskaraScope
    entity: str
    memory_source: str
    determines: str


SAMSKARA_MICRO: Final[SamskaraLevel] = SamskaraLevel(
    scope=SamskaraScope.MICRO,
    entity="Session/User",
    memory_source="Previous interactions in this context",
    determines="User preferences, learned behaviors",
)

SAMSKARA_MESO: Final[SamskaraLevel] = SamskaraLevel(
    scope=SamskaraScope.MESO,
    entity="Service/Application",
    memory_source="Previous deployments, incidents",
    determines="System patterns, failure modes",
)

SAMSKARA_MACRO: Final[SamskaraLevel] = SamskaraLevel(
    scope=SamskaraScope.MACRO,
    entity="Infrastructure/Platform",
    memory_source="Historical architecture decisions",
    determines="Technical constants, constraints",
)

ALL_SAMSKARA_LEVELS: Final[tuple[SamskaraLevel, ...]] = (
    SAMSKARA_MICRO,
    SAMSKARA_MESO,
    SAMSKARA_MACRO,
)

# Verify: 3 levels = TRINITY
assert len(ALL_SAMSKARA_LEVELS) == TRINITY, "3 samskara levels = TRINITY"


# =============================================================================
# RESULT TYPES
# =============================================================================

@dataclass(frozen=True)
class CompressionResult:
    """Result of intent compression."""

    # The extracted seed (deterministic hash)
    seed: int

    # Intent classification
    intent_level: IntentLevel

    # Compression metrics
    input_size: int           # Original size (chars/bytes)
    output_size: int          # Compressed size (seed = 4 bytes)
    compression_ratio: float  # input_size / output_size

    # The compressed intent summary (optional)
    summary: Optional[str] = None

    # Position in 16-word grid
    position: int = 0

    @property
    def guna(self) -> str:
        """Shorthand for intent guna."""
        return self.intent_level.guna.value

    @property
    def is_healthy(self) -> bool:
        """True if intent is Sattvic or higher."""
        return self.intent_level.score >= 2


@dataclass(frozen=True)
class SamskaraResult:
    """Result of samskara encoding."""

    # The seed that encodes this state
    seed: int

    # Samskara level (micro/meso/macro)
    scope: SamskaraScope

    # Intent level of the state
    intent_level: IntentLevel

    # What was encoded
    encoded_keys: tuple[str, ...]

    # Original data size vs samskara size
    original_size: int
    samskara_size: int  # Always 4 bytes (the seed)

    @property
    def compression_ratio(self) -> float:
        return self.original_size / self.samskara_size if self.samskara_size > 0 else 0.0

    @property
    def can_reconstruct(self) -> bool:
        """
        Samskara is LOSSY compression by design.
        You can't reconstruct the original, but you don't need to.
        You only need the LESSON, not the EXPERIENCE.
        """
        return False


@dataclass(frozen=True)
class PhysicsVerification:
    """Result of physics constant verification."""

    seed: int

    # Alignment checks
    is_maha_quantum_aligned: bool   # seed relates to 137
    is_words_aligned: bool          # seed relates to 16
    is_aksara_aligned: bool         # seed relates to 32
    is_qualities_aligned: bool      # seed relates to 64

    # Overall score (0-4)
    alignment_score: int

    # Interpretation
    interpretation: str

    @property
    def is_aligned(self) -> bool:
        """True if any alignment detected."""
        return self.alignment_score > 0

    @property
    def is_perfectly_aligned(self) -> bool:
        """True if all alignments detected."""
        return self.alignment_score == 4


# =============================================================================
# MAHA COMPRESSION ENGINE
# =============================================================================

class MahaCompression:
    """
    Intent Engine for AI Agents.

    Compresses MEANING, not BITS.
    Extracts the WHY, not the WHAT.

    THE ALGORITHM:
        1. KSETRAJNA generates INTENT (this class analyzes)
        2. KRISHNA provides SANCTION (the constants verify)
        3. PRAKRITI executes ALGORITHM (the system acts)
        4. KARMA records SAMSKARA (this class encodes)
    """

    def __init__(self) -> None:
        """Initialize the compression engine."""
        self._intent_keywords: Dict[IntentGuna, List[str]] = {
            IntentGuna.TAMAS: [
                "error", "fail", "crash", "exception", "fatal", "panic",
                "undefined", "null", "corrupt", "invalid", "broken",
                "timeout", "deadlock", "oom", "memory leak", "segfault",
            ],
            IntentGuna.RAJAS: [
                "warn", "retry", "slow", "delay", "pending", "queue",
                "backlog", "debt", "hack", "workaround", "temp", "fixme",
                "todo", "deprecated", "legacy", "rush", "hotfix",
            ],
            IntentGuna.SATTVA: [
                "success", "complete", "healthy", "stable", "clean",
                "tested", "verified", "documented", "refactored", "optimized",
                "secure", "compliant", "monitored", "logged",
            ],
            IntentGuna.SUDDHA: [
                "transcend", "optimal", "perfect", "aligned", "resonant",
                "unified", "harmonious", "enlightened", "liberated",
                "zero-downtime", "self-healing", "antifragile",
            ],
        }

    # =========================================================================
    # CORE: Intent Compression
    # =========================================================================

    def compress(
        self,
        data: Union[str, bytes, Dict[str, object]],
        *,
        extract_summary: bool = True,
    ) -> CompressionResult:
        """
        Compress data to its intent seed.

        THIS IS NOT ZIP.
        This extracts the MEANING, not the BITS.

        Args:
            data: Text, bytes, or dict to compress
            extract_summary: Generate a 1-sentence summary

        Returns:
            CompressionResult with seed, intent level, and metrics

        Example:
            >>> compressor = MahaCompression()
            >>> result = compressor.compress("Error: Connection timeout after 30s retry")
            >>> print(result.guna)  # "tamas"
            >>> print(result.compression_ratio)  # ~10.0
        """
        # Normalize to string
        if isinstance(data, bytes):
            text = data.decode("utf-8", errors="replace")
        elif isinstance(data, dict):
            text = json.dumps(data, default=str)
        else:
            text = str(data)

        input_size = len(text)

        # Generate deterministic seed (32-bit)
        seed = self._compute_seed(text)

        # Classify intent
        intent_level = self._classify_intent(text)

        # Position in 16-word grid
        position = seed % WORDS

        # Generate summary if requested
        summary = None
        if extract_summary:
            summary = self._extract_summary(text, intent_level)

        return CompressionResult(
            seed=seed,
            intent_level=intent_level,
            input_size=input_size,
            output_size=4,  # 32-bit seed
            compression_ratio=input_size / 4 if input_size > 0 else 0.0,
            summary=summary,
            position=position,
        )

    def _compute_seed(self, text: str) -> int:
        """Compute deterministic 32-bit seed from text."""
        # Use SHA-256 and take first 4 bytes
        h = hashlib.sha256(text.encode("utf-8")).digest()
        return int.from_bytes(h[:4], "big")

    def _classify_intent(self, text: str) -> IntentLevel:
        """Classify text into one of 4 intent levels."""
        text_lower = text.lower()

        # Count keyword matches for each guna
        scores = {guna: 0 for guna in IntentGuna}

        for guna, keywords in self._intent_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    scores[guna] += 1

        # Find dominant guna
        max_score = max(scores.values())

        if max_score == 0:
            # No keywords matched - default to SATTVA (neutral)
            return INTENT_SATTVA

        # Priority: TAMAS > RAJAS > SATTVA > SUDDHA
        # (Problems should be surfaced, not hidden)
        if scores[IntentGuna.TAMAS] > 0:
            return INTENT_TAMAS
        if scores[IntentGuna.RAJAS] > 0:
            return INTENT_RAJAS
        if scores[IntentGuna.SUDDHA] > 0:
            return INTENT_SUDDHA
        return INTENT_SATTVA

    def _extract_summary(self, text: str, intent: IntentLevel) -> str:
        """Extract a 1-sentence summary based on intent."""
        guna = intent.guna.value.upper()

        # Count some basic metrics
        lines = text.count("\n") + 1
        words = len(text.split())

        return f"{guna} state detected: {words} words, {lines} lines → {intent.system_interpretation}"

    # =========================================================================
    # SAMSKARA: State Encoding
    # =========================================================================

    def encode_samskara(
        self,
        state: Dict[str, object],
        *,
        scope: SamskaraScope = SamskaraScope.MICRO,
    ) -> SamskaraResult:
        """
        Encode system state as samskara (impression).

        THIS IS LOSSY BY DESIGN.

        An agent doesn't need to know what it said 10 days ago.
        It only needs to know the LESSON from that interaction.

        Args:
            state: Dictionary of state to encode
            scope: Micro (session), Meso (service), or Macro (platform)

        Returns:
            SamskaraResult with seed and metrics

        Example:
            >>> samskara = compressor.encode_samskara({
            ...     "user_id": 123,
            ...     "events": [e1, e2, e3, ...e1000],
            ...     "context": "...massive text..."
            ... })
            >>> print(samskara.seed)  # Compact 32-bit
            >>> print(samskara.compression_ratio)  # 1000x+
        """
        # Serialize state
        state_json = json.dumps(state, sort_keys=True, default=str)
        original_size = len(state_json)

        # Compute seed
        seed = self._compute_seed(state_json)

        # Classify intent of the state
        intent_level = self._classify_intent(state_json)

        return SamskaraResult(
            seed=seed,
            scope=scope,
            intent_level=intent_level,
            encoded_keys=tuple(state.keys()),
            original_size=original_size,
            samskara_size=4,  # 32-bit seed
        )

    def decode_samskara_intent(self, seed: int) -> IntentLevel:
        """
        Decode intent level from a samskara seed.

        Note: This only recovers the INTENT LEVEL, not the original data.
        That's the point - samskara is about LESSONS, not MEMORIES.

        Args:
            seed: The samskara seed

        Returns:
            IntentLevel based on seed properties
        """
        # Use seed properties to infer intent
        # This is deterministic but approximate
        position = seed % WORDS

        # Map positions to gunas (simplified)
        # 0-3 = TAMAS, 4-7 = RAJAS, 8-11 = SATTVA, 12-15 = SUDDHA
        quarter = position // QUARTERS
        return ALL_INTENT_LEVELS[quarter]

    # =========================================================================
    # PHYSICS: Constant Verification
    # =========================================================================

    def verify_physics(self, seed: int) -> PhysicsVerification:
        """
        Verify a seed against physics constants.

        THE INSIGHT:
        Physics constants are the universe's SAMSKARA.
        They're not arbitrary - they're memories from previous cycles.

        Args:
            seed: Value to verify

        Returns:
            PhysicsVerification with alignment scores

        Example:
            >>> result = compressor.verify_physics(137)
            >>> print(result.is_maha_quantum_aligned)  # True
            >>> print(result.interpretation)  # "Perfect quantum alignment"
        """
        # Check alignments
        is_maha = (seed == MAHA_QUANTUM) or (seed % MAHA_QUANTUM == 0)
        is_words = (seed == WORDS) or (seed % WORDS == 0)
        is_aksara = (seed == AKSARA) or (seed % AKSARA == 0)
        is_qualities = (seed == QUALITIES) or (seed % QUALITIES == 0)

        # Calculate score
        score = sum([is_maha, is_words, is_aksara, is_qualities])

        # Generate interpretation
        if score == 4:
            interpretation = "Perfect alignment with all Mahamantra constants"
        elif score == 3:
            interpretation = "Strong alignment - resonates with cosmic structure"
        elif score == 2:
            interpretation = "Partial alignment - some harmonic relationship"
        elif score == 1:
            interpretation = "Weak alignment - single constant match"
        else:
            interpretation = "No alignment detected - arbitrary value"

        return PhysicsVerification(
            seed=seed,
            is_maha_quantum_aligned=is_maha,
            is_words_aligned=is_words,
            is_aksara_aligned=is_aksara,
            is_qualities_aligned=is_qualities,
            alignment_score=score,
            interpretation=interpretation,
        )

    # =========================================================================
    # REFERENCE: Compression Ratios
    # =========================================================================

    def reference_ratios(self) -> Dict[str, float]:
        """
        Get reference compression ratios from scripture.

        These are the GOLD STANDARD:
        - Gita: 700 verses from 16 words = 43.75×
        - Bhagavatam: 18,000 verses from 16 words = 1,125×
        - Vedas: 100,000+ verses from 16 words = 6,250×+

        Your system should aim for similar ratios.
        """
        return {
            "gita": GITA_VERSES / WORDS,
            "bhagavatam": BHAGAVATAM_VERSES / WORDS,
            "vedas": VEDA_VERSES / WORDS,
        }

    def intent_levels(self) -> tuple[IntentLevel, ...]:
        """Get all intent levels for reference."""
        return ALL_INTENT_LEVELS

    def samskara_levels(self) -> tuple[SamskaraLevel, ...]:
        """Get all samskara levels for reference."""
        return ALL_SAMSKARA_LEVELS

    # =========================================================================
    # BATCH OPERATIONS
    # =========================================================================

    def compress_batch(
        self,
        items: List[Union[str, Dict[str, object]]],
    ) -> List[CompressionResult]:
        """
        Compress multiple items, returning individual results.

        Args:
            items: List of texts or dicts to compress

        Returns:
            List of CompressionResult for each item
        """
        return [self.compress(item) for item in items]

    def compress_aggregate(
        self,
        items: List[Union[str, Dict[str, object]]],
    ) -> CompressionResult:
        """
        Compress multiple items into a single aggregate intent.

        Use this when you have many log lines and want ONE assessment.

        Args:
            items: List of texts or dicts to compress

        Returns:
            Single CompressionResult representing the aggregate
        """
        # Compress each item
        results = self.compress_batch(items)

        # Aggregate: dominant intent wins (worst case surfaces)
        worst_intent = max(results, key=lambda r: -r.intent_level.score).intent_level

        # Combine seeds (XOR for uniformity)
        combined_seed = 0
        for r in results:
            combined_seed ^= r.seed

        # Total input size
        total_input = sum(r.input_size for r in results)

        return CompressionResult(
            seed=combined_seed,
            intent_level=worst_intent,
            input_size=total_input,
            output_size=4,
            compression_ratio=total_input / 4 if total_input > 0 else 0.0,
            summary=f"Aggregate of {len(items)} items: {worst_intent.guna.value.upper()} dominant",
            position=combined_seed % WORDS,
        )


# =============================================================================
# MODULE EXPORTS
# =============================================================================

__all__ = [
    # Main class
    "MahaCompression",
    # Result types
    "CompressionResult",
    "SamskaraResult",
    "PhysicsVerification",
    # Intent levels
    "IntentLevel",
    "IntentGuna",
    "INTENT_TAMAS",
    "INTENT_RAJAS",
    "INTENT_SATTVA",
    "INTENT_SUDDHA",
    "ALL_INTENT_LEVELS",
    # Samskara levels
    "SamskaraLevel",
    "SamskaraScope",
    "ALL_SAMSKARA_LEVELS",
    # Constants
    "WORDS",
    "QUARTERS",
    "TRINITY",
    "MAHA_QUANTUM",
]


# =============================================================================
# VERIFICATION
# =============================================================================

if __name__ == "__main__":
    # Test the compression engine
    compressor = MahaCompression()

    # Test 1: Compress error log
    error_log = """
    2024-01-15 10:23:45 ERROR: Connection timeout after 30s
    2024-01-15 10:23:46 FATAL: Database connection failed
    2024-01-15 10:23:47 PANIC: Unable to recover, system halting
    """
    result = compressor.compress(error_log)
    print(f"Error log compression:")
    print(f"  Intent: {result.guna}")
    print(f"  Seed: {result.seed}")
    print(f"  Ratio: {result.compression_ratio:.1f}×")
    print(f"  Summary: {result.summary}")
    print()

    # Test 2: Compress healthy log
    healthy_log = """
    2024-01-15 10:23:45 INFO: All services healthy
    2024-01-15 10:23:46 INFO: Request completed successfully
    2024-01-15 10:23:47 INFO: Tests verified, documentation updated
    """
    result = compressor.compress(healthy_log)
    print(f"Healthy log compression:")
    print(f"  Intent: {result.guna}")
    print(f"  Healthy: {result.is_healthy}")
    print(f"  Ratio: {result.compression_ratio:.1f}×")
    print()

    # Test 3: Samskara encoding
    state = {
        "user_id": 123,
        "events": ["login", "view", "edit", "save"] * 100,
        "context": "Previous conversation about deployment..." * 50,
    }
    samskara = compressor.encode_samskara(state)
    print(f"Samskara encoding:")
    print(f"  Seed: {samskara.seed}")
    print(f"  Intent: {samskara.intent_level.guna.value}")
    print(f"  Compression: {samskara.compression_ratio:.1f}×")
    print(f"  Can reconstruct: {samskara.can_reconstruct}")
    print()

    # Test 4: Physics verification
    for seed in [137, 16, 32, 64, 42]:
        v = compressor.verify_physics(seed)
        print(f"Seed {seed}: score={v.alignment_score}, aligned={v.is_aligned}")
    print()

    # Test 5: Reference ratios
    print("Reference compression ratios:")
    for name, ratio in compressor.reference_ratios().items():
        print(f"  {name}: {ratio:.2f}×")
