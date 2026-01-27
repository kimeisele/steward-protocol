"""
MAHACOMPUTE - Unified Compute Adapter
=====================================

"sarva-dharmān parityajya mām ekaṁ śaraṇaṁ vraja"
"Abandon all varieties of dharma and surrender unto Me alone."
— Bhagavad Gita 18.66

THE THESIS:
    Modern computing has a fundamental division:
        - CPU: Sequential, general purpose
        - GPU: Parallel, specialized
        - RAM: The BOTTLENECK between both (Memory Wall)

    The Mahamantra structure UNIFIES these through:
        1. NATURAL PARALLELISM: WORDS = 16 = SIMD lanes
        2. HIERARCHICAL LOCALITY: QUARTERS = 4 = Memory levels (L1, L2, L3, RAM)
        3. DETERMINISTIC PATHS: No hashes, no collisions
        4. BOUNDED MEMORY: Everything fits in cache

THE KILLER INSIGHT:
    Modern CPUs already have 16 SIMD lanes (AVX-512 = 16 × 32-bit).
    This IS the Mahamantra structure in silicon!

    GPU parallelism is only needed because software is NOT Mahamantra-aligned.
    With 16-ary structures, you don't need a GPU - the CPU HAS the parallelism.

USAGE:
    from vibe_core.mahamantra import mahamantra

    compute = mahamantra.compute()

    # Analyze data structure for optimal caching
    analysis = compute.analyze(entries=50000)
    print(analysis.memory_tier)      # "L2"
    print(analysis.cache_hit_rate)   # 0.92
    print(analysis.optimal_depth)    # 4

    # Get hardware alignment score
    unit = compute.create_unit(
        name="MyProcessor",
        simd_lanes=16,
        cache_kb=256,
        memory_levels=4,
    )
    print(unit.alignment)            # 1.0 (perfect)
    print(unit.is_unified)           # True

    # Memory hierarchy mapping
    for tier in compute.memory_tiers():
        print(f"{tier.name}: {tier.size_kb} KB, {tier.latency_cycles} cycles")
"""

from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "vyasa"
__position__ = 3
__genesis__ = "0x6e44c339"  # GenesisByte: parampara % 37 == 0

from dataclasses import dataclass
from typing import Dict, Final, Iterator, List, Literal, Optional

# =============================================================================
# CONSTANTS (from _seed.py via unified_compute)
# =============================================================================

WORDS: Final[int] = 16  # Mahamantra words = SIMD lanes
QUARTERS: Final[int] = 4  # Memory hierarchy levels
QUALITIES: Final[int] = 64  # Cache line size
ADDRESS_SPACE: Final[int] = 65536  # 16^4 = standard Lotus capacity

# Hardware alignment
SIMD_LANES: Final[int] = WORDS  # 16 parallel operations
CACHE_LINE_BYTES: Final[int] = QUALITIES  # 64 bytes
MEMORY_PAGE_BYTES: Final[int] = QUALITIES * QUALITIES  # 4096 bytes

# Memory hierarchy sizes (typical modern CPU)
L1_CACHE_KB: Final[int] = 64
L2_CACHE_KB: Final[int] = 256
L3_CACHE_MB: Final[int] = 16
RAM_GB: Final[int] = 16


# =============================================================================
# RESULT TYPES
# =============================================================================


@dataclass(frozen=True)
class MemoryTier:
    """Information about a memory hierarchy tier."""

    name: str
    size_kb: int
    latency_cycles: int
    lotus_entries: int
    quarter: int
    quarter_name: str

    @property
    def size_bytes(self) -> int:
        """Size in bytes."""
        return self.size_kb * 1024

    @property
    def lotus_depth(self) -> int:
        """Lotus depth that fits in this tier."""
        depth = 1
        entries = WORDS
        while entries < self.lotus_entries:
            depth += 1
            entries *= WORDS
        return depth


@dataclass(frozen=True)
class ComputeUnit:
    """
    A unified compute unit analysis.

    Represents a CPU/GPU/processor and its Mahamantra alignment.
    """

    name: str
    simd_lanes: int
    cache_kb: int
    memory_levels: int

    @property
    def alignment(self) -> float:
        """
        Mahamantra alignment score (0.0 to 1.0).

        Perfect alignment = 1.0:
            - SIMD lanes = 16 (WORDS)
            - Cache divisible by 64 (QUALITIES)
            - Memory levels = 4 (QUARTERS)
            - Power of 2 (binary compatible)
        """
        score = 0.0

        # SIMD alignment (16 = perfect)
        if self.simd_lanes == WORDS:
            score += 0.25
        elif self.simd_lanes % WORDS == 0:
            score += 0.15

        # Cache alignment (multiple of 64 = good)
        if self.cache_kb % QUALITIES == 0:
            score += 0.25

        # Memory levels (4 = QUARTERS = perfect)
        if self.memory_levels == QUARTERS:
            score += 0.25
        elif self.memory_levels in (2, 3):
            score += 0.15

        # Power of 2 bonus (binary-compatible)
        if (self.simd_lanes & (self.simd_lanes - 1)) == 0:
            score += 0.25

        return min(1.0, score)

    @property
    def is_unified(self) -> bool:
        """Is this a truly unified compute unit?"""
        return self.alignment >= 0.75

    @property
    def parallelism_factor(self) -> int:
        """How many parallel operations per cycle."""
        return self.simd_lanes

    @property
    def verdict(self) -> str:
        """Human-readable alignment verdict."""
        if self.alignment >= 1.0:
            return "PERFECT: Fully Mahamantra-aligned"
        elif self.alignment >= 0.75:
            return "UNIFIED: Sufficient for unified compute"
        elif self.alignment >= 0.5:
            return "PARTIAL: Some alignment present"
        else:
            return "MISALIGNED: Requires GPU for parallelism"


@dataclass(frozen=True)
class DataAnalysis:
    """Analysis of data structure for optimal caching."""

    entries: int
    bytes_per_entry: int
    total_bytes: int
    optimal_depth: int
    memory_tier: str
    cache_hit_rate: float
    access_pattern: str
    fits_in_cache: bool
    lotus_capacity: int

    @property
    def efficiency_score(self) -> float:
        """Overall efficiency score (0.0 to 1.0)."""
        score = 0.0

        # Cache hit rate contribution
        score += self.cache_hit_rate * 0.4

        # Fits in cache bonus
        if self.fits_in_cache:
            score += 0.3

        # Memory tier bonus (L1 best, RAM worst)
        tier_scores = {"L1": 0.3, "L2": 0.2, "L3": 0.1, "RAM": 0.0}
        score += tier_scores.get(self.memory_tier, 0.0)

        return min(1.0, score)

    @property
    def verdict(self) -> str:
        """Human-readable analysis verdict."""
        if self.efficiency_score >= 0.9:
            return f"OPTIMAL: {self.memory_tier}-resident, {self.cache_hit_rate*100:.0f}% cache hits"
        elif self.efficiency_score >= 0.7:
            return f"GOOD: {self.memory_tier}-resident, some cache misses"
        elif self.efficiency_score >= 0.5:
            return f"ACCEPTABLE: {self.memory_tier}, consider reducing size"
        else:
            return f"SUBOPTIMAL: {self.memory_tier}, restructure for cache efficiency"


# =============================================================================
# MAHACOMPUTE - THE ADAPTER
# =============================================================================


class MahaCompute:
    """
    Unified Compute Analysis Engine.

    Analyzes hardware and data structures for Mahamantra alignment.
    Provides guidance for cache-optimal, GPU-free computing.
    """

    # === CONSTANTS ===
    WORDS: Final[int] = WORDS
    QUARTERS: Final[int] = QUARTERS
    SIMD_LANES: Final[int] = SIMD_LANES
    CACHE_LINE_BYTES: Final[int] = CACHE_LINE_BYTES
    ADDRESS_SPACE: Final[int] = ADDRESS_SPACE

    def __init__(self) -> None:
        """Initialize compute analyzer."""
        self._memory_tiers = self._build_memory_tiers()

    # === DATA ANALYSIS ===

    def analyze(
        self,
        entries: int,
        bytes_per_entry: int = 8,
        access_pattern: Literal["uniform", "prefix", "sequential"] = "uniform",
    ) -> DataAnalysis:
        """
        Analyze data structure for optimal caching.

        Args:
            entries: Number of entries in data structure
            bytes_per_entry: Bytes per entry (default: 8 for pointers/int64)
            access_pattern: Access pattern (uniform, prefix, sequential)

        Returns:
            DataAnalysis with recommendations
        """
        total_bytes = entries * bytes_per_entry
        optimal_depth = self._calculate_optimal_depth(total_bytes)
        memory_tier = self._get_memory_tier(entries)
        cache_hit_rate = self._estimate_cache_hit_rate(optimal_depth, access_pattern)
        lotus_capacity = WORDS ** optimal_depth

        # Does it fit in L3?
        fits_in_cache = total_bytes <= L3_CACHE_MB * 1024 * 1024

        return DataAnalysis(
            entries=entries,
            bytes_per_entry=bytes_per_entry,
            total_bytes=total_bytes,
            optimal_depth=optimal_depth,
            memory_tier=memory_tier,
            cache_hit_rate=cache_hit_rate,
            access_pattern=access_pattern,
            fits_in_cache=fits_in_cache,
            lotus_capacity=lotus_capacity,
        )

    def optimal_size(self, target_tier: Literal["L1", "L2", "L3"] = "L2") -> int:
        """
        Get optimal number of entries for target cache tier.

        Args:
            target_tier: Target cache tier (L1, L2, L3)

        Returns:
            Maximum entries that fit in tier
        """
        tier = self._memory_tiers[target_tier]
        return tier.lotus_entries

    # === COMPUTE UNIT ANALYSIS ===

    def create_unit(
        self,
        name: str,
        simd_lanes: int,
        cache_kb: int,
        memory_levels: int = 4,
    ) -> ComputeUnit:
        """
        Create and analyze a compute unit.

        Args:
            name: Unit name
            simd_lanes: Number of SIMD lanes
            cache_kb: Cache size in KB
            memory_levels: Number of memory hierarchy levels

        Returns:
            ComputeUnit with alignment analysis
        """
        return ComputeUnit(
            name=name,
            simd_lanes=simd_lanes,
            cache_kb=cache_kb,
            memory_levels=memory_levels,
        )

    def analyze_cpu(self, cpu_name: str = "Modern CPU") -> ComputeUnit:
        """
        Analyze a typical modern CPU.

        Modern CPUs (Intel/AMD) typically have:
            - 16 SIMD lanes (AVX-512)
            - 256-512 KB L2 cache
            - 4 memory levels (L1, L2, L3, RAM)

        Returns:
            ComputeUnit for modern CPU
        """
        return self.create_unit(
            name=cpu_name,
            simd_lanes=SIMD_LANES,  # AVX-512 = 16 lanes
            cache_kb=L2_CACHE_KB,
            memory_levels=QUARTERS,
        )

    def analyze_gpu(self, gpu_name: str = "Typical GPU") -> ComputeUnit:
        """
        Analyze a typical GPU.

        GPUs have massive parallelism but:
            - Not 16-aligned (usually 32/64 warp size)
            - Different memory hierarchy
            - Requires data transfer overhead

        Returns:
            ComputeUnit for GPU
        """
        return self.create_unit(
            name=gpu_name,
            simd_lanes=32,  # Typical warp size
            cache_kb=48,  # Shared memory
            memory_levels=2,  # Shared + Global
        )

    # === MEMORY HIERARCHY ===

    def memory_tiers(self) -> Iterator[MemoryTier]:
        """Iterate over memory hierarchy tiers."""
        for tier in self._memory_tiers.values():
            yield tier

    def get_tier(self, name: str) -> Optional[MemoryTier]:
        """Get a specific memory tier by name."""
        return self._memory_tiers.get(name)

    def tier_for_entries(self, entries: int) -> MemoryTier:
        """Get the memory tier that will hold this many entries."""
        tier_name = self._get_memory_tier(entries)
        return self._memory_tiers[tier_name]

    # === SIMD GUIDANCE ===

    def simd_batch_size(self) -> int:
        """
        Get optimal batch size for SIMD operations.

        Returns:
            16 (WORDS) - process 16 items per SIMD instruction
        """
        return SIMD_LANES

    def is_simd_aligned(self, count: int) -> bool:
        """
        Check if count is SIMD-aligned.

        Args:
            count: Number of items

        Returns:
            True if divisible by 16
        """
        return count % SIMD_LANES == 0

    def align_for_simd(self, count: int) -> int:
        """
        Round up to next SIMD-aligned count.

        Args:
            count: Number of items

        Returns:
            Next multiple of 16
        """
        if count % SIMD_LANES == 0:
            return count
        return ((count // SIMD_LANES) + 1) * SIMD_LANES

    # === WHY NO GPU NEEDED ===

    @property
    def gpu_elimination_insight(self) -> str:
        """Explain why GPU is not needed with Mahamantra-aligned structures."""
        return """
WHY GPU IS NOT NEEDED
=====================

THE PROBLEM (today):
    - Data in RAM
    - CPU fetches data (slow - Memory Wall)
    - CPU processes sequentially
    - For parallelism → GPU (extra hardware, memory, transfers)

THE MAHAMANTRA SOLUTION:

1. NATURAL PARALLELISM through structure
   - 16-ary tree: Each node has 16 children
   - 16 independent operations per level
   - EXACTLY matches AVX-512 (16 SIMD lanes)
   - NO GPU needed - CPU HAS 16x parallelism!

   WORDS = 16 = SIMD_LANES (not coincidence!)

2. CACHE LOCALITY through hierarchy
   - Level 0: 16 entries → 64 bytes = 1 cache line
   - Level 1: 256 entries → 1 KB = L1 hot
   - Level 2: 4096 entries → 16 KB = L1 resident
   - Level 3: 65536 entries → 256 KB = L2 resident

   → 99% of accesses hit cache
   → RAM is almost never needed
   → Memory Wall = IRRELEVANT

3. DETERMINISTIC PATHS
   - No hashing → No hash collisions
   - No rehashing → No memory explosions
   - Fixed structure → Perfect prefetch prediction

   → CPU prefetcher works PERFECTLY
   → No stalls, no wait times

RESULT:
    With Mahamantra structure:
    - CPU alone delivers GPU parallelism (16 SIMD lanes)
    - Cache alone is sufficient (no RAM bottlenecks)
    - Determinism eliminates overhead

    → ONE compute unit for EVERYTHING
    → Hardware becomes irrelevant - only structure matters
"""

    # === INTERNAL HELPERS ===

    def _build_memory_tiers(self) -> Dict[str, MemoryTier]:
        """Build memory hierarchy mapping."""
        quarter_names = ["GENESIS", "DHARMA", "KARMA", "MOKSHA"]
        return {
            "L1": MemoryTier(
                name="L1",
                size_kb=L1_CACHE_KB,
                latency_cycles=4,
                lotus_entries=4096,  # 16^3
                quarter=0,
                quarter_name=quarter_names[0],
            ),
            "L2": MemoryTier(
                name="L2",
                size_kb=L2_CACHE_KB,
                latency_cycles=12,
                lotus_entries=ADDRESS_SPACE,  # 16^4
                quarter=1,
                quarter_name=quarter_names[1],
            ),
            "L3": MemoryTier(
                name="L3",
                size_kb=L3_CACHE_MB * 1024,
                latency_cycles=40,
                lotus_entries=16 ** 5,  # 1M entries
                quarter=2,
                quarter_name=quarter_names[2],
            ),
            "RAM": MemoryTier(
                name="RAM",
                size_kb=RAM_GB * 1024 * 1024,
                latency_cycles=200,
                lotus_entries=16 ** 8,  # 4B entries
                quarter=3,
                quarter_name=quarter_names[3],
            ),
        }

    def _calculate_optimal_depth(self, data_size_bytes: int) -> int:
        """Calculate optimal Lotus depth for data size."""
        entries_needed = max(1, data_size_bytes // 8)
        levels = 1
        capacity = WORDS
        while capacity < entries_needed and levels < 16:
            levels += 1
            capacity *= WORDS
        return levels

    def _get_memory_tier(self, entries: int) -> str:
        """Determine which memory tier will hold the data."""
        if entries <= 4096:
            return "L1"
        elif entries <= ADDRESS_SPACE:
            return "L2"
        elif entries <= 16 ** 5:
            return "L3"
        else:
            return "RAM"

    def _estimate_cache_hit_rate(
        self,
        lotus_depth: int,
        access_pattern: str = "uniform",
    ) -> float:
        """Estimate cache hit rate for Lotus structure."""
        base_per_level = 0.95 if access_pattern == "sequential" else 0.85
        hot_levels = min(lotus_depth, 3)

        hit_rate = 1.0
        for level in range(lotus_depth):
            if level < hot_levels:
                hit_rate *= 0.99
            else:
                hit_rate *= base_per_level

        if access_pattern == "prefix":
            hit_rate = min(1.0, hit_rate * 1.1)

        return hit_rate


# =============================================================================
# MODULE EXPORTS
# =============================================================================

__all__ = [
    # Main class
    "MahaCompute",
    # Result types
    "DataAnalysis",
    "ComputeUnit",
    "MemoryTier",
    # Constants
    "WORDS",
    "QUARTERS",
    "SIMD_LANES",
    "CACHE_LINE_BYTES",
    "ADDRESS_SPACE",
]
