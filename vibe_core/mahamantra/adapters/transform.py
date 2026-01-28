"""
MAHA TRANSFORM - Standard Transformation Interface
===================================================

Enterprise-compatible wrapper for MahaAlgorithm/MahaKirtan.

WHAT IT IS:
    A deterministic 16-step transformation function with:
    - Configurable mod space (default: 137)
    - Attractor discovery (finds stable states)
    - Batch processing support

WHAT IT'S NOT:
    Not a black box. Every operation is derived from the
    Mahamantra structure. See maha_algorithm.py for full derivation.

THE MATH (Senior Engineer Summary):
    1. Input seed normalized to mod space
    2. 16 operations applied in sequence:
       - 8× multiply by 7 (HARE positions)
       - 4× add 10 (KRISHNA positions)
       - 4× square (RAMA positions)
    3. Each operation includes position weight + feedback
    4. Output: integer in [0, mod_space)

ATTRACTORS:
    Repeated iteration converges to 5 stable states:
    - 136 (77% - the "field", sum of positions 1-16)
    - 49, 22, 18, 87 (remaining 23%)

USAGE:
    transform = MahaTransform()

    # Single transformation
    result = transform.compute(42)
    print(result.value)  # transformed value

    # Find attractor (stable state)
    attractor = transform.find_attractor(42)
    print(attractor.stable_value)

    # Batch processing
    results = transform.compute_batch([1, 2, 3, 4, 5])
"""

# === MAHAJANA DECLARATION ===
__mahajana__ = "narada"
__position__ = 3
__genesis__ = "0xTRAN5F0"

from dataclasses import dataclass
from typing import Final, List, Optional, Tuple

from vibe_core.mahamantra.protocols._seed import (
    MAHA_QUANTUM,
    WORDS,
    SEVEN,
    TEN,
    TRINITY,
    HALVES,
    NAVA,
)


# =============================================================================
# RESULT TYPES (Standard CS naming)
# =============================================================================

@dataclass(frozen=True)
class TransformResult:
    """Result of a single transformation."""
    seed: int
    value: int
    mod_space: int
    iterations: int = 1


@dataclass(frozen=True)
class AttractorResult:
    """Result of attractor discovery."""
    seed: int
    stable_value: int
    cycles_to_converge: int
    is_fixed_point: bool
    trajectory: Tuple[int, ...]


@dataclass(frozen=True)
class BatchResult:
    """Result of batch transformation."""
    results: Tuple[TransformResult, ...]
    unique_outputs: int
    entropy: float  # diversity measure


# =============================================================================
# CONSTANTS (Derived from Mahamantra - see _seed.py)
# =============================================================================

# The 16-step pattern: H K H K | K K H H | H R H R | R R H H
# H = multiply by SEVEN (7)
# K = add TEN (10)
# R = square
PATTERN: Final[str] = "HKHKKKHHHRHRRRHHH"[:WORDS]  # 16 characters

# Default mod space (Maha Quantum = 137)
DEFAULT_MOD: Final[int] = MAHA_QUANTUM


# =============================================================================
# THE ADAPTER
# =============================================================================

class MahaTransform:
    """
    Deterministic 16-Step Transformation Engine.

    Enterprise-compatible interface to the Mahamantra algorithm.

    Args:
        mod_space: Modular arithmetic space (default: 137)
        feedback: State preservation factor (default: 1)
        preset: Named configuration ("classical", "quantum", "wide")
    """

    # Naga substrate markers (required)
    _naga_flooded: bool = True
    _naga_gene: str = "maha_transform_adapter"

    # Presets map to mod spaces (DERIVED from _seed.py)
    PRESETS: Final[dict] = {
        "classical": SEVEN + TEN,      # 17 - Prime, fast convergence
        "quantum": MAHA_QUANTUM,       # 137 - Maha Quantum, balanced
        "wide": HALVES ** NAVA,        # 2^9 = 512 - Large space, more diversity
        "trinity": TRINITY,            # 3 - Minimal (H, K, R only)
    }

    def __init__(
        self,
        mod_space: int = DEFAULT_MOD,
        feedback: int = 1,
        preset: Optional[str] = None,
    ) -> None:
        if preset and preset in self.PRESETS:
            mod_space = self.PRESETS[preset]

        self.mod_space = mod_space
        self.feedback = feedback
        self._feedback_acc = 0

    def compute(self, seed: int) -> TransformResult:
        """
        Apply 16-step transformation to seed.

        Args:
            seed: Input integer (any size, will be normalized)

        Returns:
            TransformResult with transformed value
        """
        value = seed % self.mod_space
        self._feedback_acc = 0

        for i, op in enumerate(PATTERN):
            position = i + 1  # 1-indexed

            if op == "H":
                # HARE: Multiply by SEVEN
                value = (value * SEVEN + self._feedback_acc) % self.mod_space
            elif op == "K":
                # KRISHNA: Add TEN + position
                value = (value + TEN + position + self._feedback_acc) % self.mod_space
            else:
                # RAMA: Square
                value = (value * value + self._feedback_acc) % self.mod_space

            # Accumulate feedback
            self._feedback_acc = (self._feedback_acc + value * self.feedback) % self.mod_space

        return TransformResult(
            seed=seed,
            value=value,
            mod_space=self.mod_space,
        )

    def find_attractor(self, seed: int, max_iterations: int = 137) -> AttractorResult:
        """
        Iterate transformation until stable state (attractor) reached.

        Args:
            seed: Starting value
            max_iterations: Safety limit (default: 137)

        Returns:
            AttractorResult with stable value and convergence info
        """
        trajectory = [seed]
        value = seed
        seen = {seed}

        for i in range(max_iterations):
            result = self.compute(value)
            value = result.value

            if value in seen:
                # Found attractor or cycle
                return AttractorResult(
                    seed=seed,
                    stable_value=value,
                    cycles_to_converge=i + 1,
                    is_fixed_point=(value == trajectory[-1]),
                    trajectory=tuple(trajectory),
                )

            seen.add(value)
            trajectory.append(value)

        # Max iterations reached
        return AttractorResult(
            seed=seed,
            stable_value=value,
            cycles_to_converge=max_iterations,
            is_fixed_point=False,
            trajectory=tuple(trajectory),
        )

    def compute_batch(self, seeds: List[int]) -> BatchResult:
        """
        Transform multiple seeds efficiently.

        Args:
            seeds: List of input seeds

        Returns:
            BatchResult with all results and statistics
        """
        results = tuple(self.compute(s) for s in seeds)
        unique = len(set(r.value for r in results))

        # Entropy: how spread out are the outputs?
        entropy = unique / len(results) if results else 0.0

        return BatchResult(
            results=results,
            unique_outputs=unique,
            entropy=entropy,
        )

    def analyze_distribution(self, sample_size: int = 1000) -> dict:
        """
        Analyze output distribution over sample space.

        Returns:
            Dictionary with distribution statistics
        """
        from collections import Counter

        outputs = [self.compute(i).value for i in range(sample_size)]
        counts = Counter(outputs)

        return {
            "sample_size": sample_size,
            "unique_outputs": len(counts),
            "most_common": counts.most_common(5),
            "coverage": len(counts) / self.mod_space,
        }


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def transform(seed: int, mod_space: int = DEFAULT_MOD) -> int:
    """Quick transformation. Returns just the value."""
    return MahaTransform(mod_space=mod_space).compute(seed).value


def find_attractor(seed: int, mod_space: int = DEFAULT_MOD) -> int:
    """Quick attractor discovery. Returns stable value."""
    return MahaTransform(mod_space=mod_space).find_attractor(seed).stable_value


__all__ = [
    "MahaTransform",
    "TransformResult",
    "AttractorResult",
    "BatchResult",
    "transform",
    "find_attractor",
]
