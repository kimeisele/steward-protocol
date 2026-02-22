"""
Benchmark: rank_words() and lotus_core latency.
Run: python -m vibe_core.mahamantra.research.bench_rank_words
"""

import sys
import time


def p(msg):
    print(msg, flush=True)


def main():
    # 1. Index load
    t0 = time.perf_counter()
    from vibe_core.mahamantra.substrate.semantic_index import get_index

    idx = get_index()
    t1 = time.perf_counter()
    p(f"Index load: {(t1 - t0) * 1000:.1f}ms ({len(idx.words)} words)")

    # 2. rank_words vectorized (cold)
    from vibe_core.mahamantra.substrate.resonance_ranker import rank_words, resonate

    coords = [0, 5, 10, 15, 20, 25, 30]

    t0 = time.perf_counter()
    rank_words(coords, top_n=10)
    t1 = time.perf_counter()
    p(f"rank_words (vectorized, cold): {(t1 - t0) * 1000:.1f}ms")

    # 3. rank_words vectorized (warm)
    t0 = time.perf_counter()
    rank_words(coords, top_n=10)
    t1 = time.perf_counter()
    p(f"rank_words (vectorized, warm): {(t1 - t0) * 1000:.1f}ms")

    # 4. resonate() full pipeline
    t0 = time.perf_counter()
    resonate("dharma", top_n=5)
    t1 = time.perf_counter()
    p(f"resonate('dharma'): {(t1 - t0) * 1000:.1f}ms")

    t0 = time.perf_counter()
    resonate("fire and water", top_n=5)
    t1 = time.perf_counter()
    p(f"resonate('fire and water'): {(t1 - t0) * 1000:.1f}ms")

    # 5. lotus_core __call__
    from vibe_core.mahamantra import mahamantra

    t0 = time.perf_counter()
    mahamantra("test input")
    t1 = time.perf_counter()
    p(f"lotus_core('test input') cold: {(t1 - t0) * 1000:.1f}ms")

    t0 = time.perf_counter()
    mahamantra("test input")
    t1 = time.perf_counter()
    p(f"lotus_core('test input') warm: {(t1 - t0) * 1000:.1f}ms")

    # 6. tick() latency
    t0 = time.perf_counter()
    for _ in range(100):
        mahamantra.tick()
    t1 = time.perf_counter()
    p(f"tick() x100: {(t1 - t0) * 1000:.1f}ms ({(t1 - t0) * 10:.3f}ms/tick)")


if __name__ == "__main__":
    main()
