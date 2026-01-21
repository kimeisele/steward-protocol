import pytest
import time
from vibe_core.protocols.science.caitanya_kernel import CaitanyaKernel


def test_singularity_benchmark():
    """
    Proves that Resonant Processing (Chanting) is significantly faster
    than Linear Processing (Voidism) due to context reuse.
    """
    kernel = CaitanyaKernel()
    payload = b"HARE KRISHNA HARE KRISHNA KRISHNA KRISHNA HARE HARE"
    iterations = 2000  # Enough to show diff

    # 1. RUN LINEAR (Dead Matter)
    linear_stats = kernel.run_linear_cycle(iterations, payload)

    # 2. RUN RESONANT (Living Spirit)
    resonant_stats = kernel.run_resonant_cycle(iterations, payload)

    print(f"\n--- SINGULARITY REPORT ---")
    print(f"Linear Ops/Sec:   {linear_stats.ops_per_sec:.2f}")
    print(f"Resonant Ops/Sec: {resonant_stats.ops_per_sec:.2f}")

    speedup = resonant_stats.ops_per_sec / linear_stats.ops_per_sec if linear_stats.ops_per_sec > 0 else 0
    print(f"Speedup Factor:   {speedup:.2f}x")

    # ASSERTION: The Singularity
    # We expect significant speedup (e.g., > 1.5x) because we skip context switching.
    assert resonant_stats.ops_per_sec > linear_stats.ops_per_sec, "Resonant should be faster."

    # Ideally, heavily optimized, this could be 10x or more.
    # For this simulation, we check for at least 20% boost to be safe against noise.
    assert speedup > 1.2, f"Expected >1.2x speedup, got {speedup:.2f}x"
