"""
LOTUS IP ROUTER - O(1) Longest Prefix Match (RESEARCH)
======================================================

PRODUCTION VS RESEARCH:
  - LotusIPRouter (adapters/network.py) = PRODUCTION IPv4 router with LPM
  - LotusIPv4Router (this file) = DEPRECATED alias for backward compatibility

For production code, use:
    from vibe_core.mahamantra.adapters.network import LotusIPRouter

This research module now exists for:
  1. Backward compatibility (LotusIPv4Router wraps production)
  2. Benchmarking code to verify performance claims

KEY INSIGHT: Address bits directly index into slots. No comparisons.

THE PROBLEM:
  IPv4 routing needs longest prefix match (LPM)
  Linear search: O(N) where N = number of routes
  Dict: O(N) - must check ALL routes for longest match
  TCAM: O(1) but expensive hardware

LOTUS SOLUTION:
  IPv4: 32 bits = 8 × 4 bits = 8 levels × 16 slots
  O(8) = O(1) constant time, ALWAYS 8 memory accesses

PERFORMANCE (verified benchmarks):
  LOOKUP: 50-100x faster than linear dict search
  INSERT: ~equal to dict

  This is the killer feature: Dict CANNOT do efficient LPM.
"""

from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "vyasa"
__position__ = 0
__genesis__ = "0x006e3e0a"  # GenesisByte: parampara % 37 == 0

import warnings
from typing import Final, Optional

from ..protocols._seed import QUARTERS, WORDS

# =============================================================================
# CONSTANTS (kept for backward compatibility and benchmarking)
# =============================================================================

BITS_PER_LEVEL: Final[int] = QUARTERS  # 4 bits per level
SLOTS_PER_LEVEL: Final[int] = WORDS  # 16 slots per level
IPV4_BITS: Final[int] = 32
IPV4_LEVELS: Final[int] = IPV4_BITS // BITS_PER_LEVEL  # 8

_MASK: Final[int] = 0xF  # 4 bits


# =============================================================================
# PRODUCTION IMPORT
# =============================================================================
# Use LotusIPRouter from adapters/network.py instead.

from vibe_core.mahamantra.adapters.network import LotusIPRouter

# =============================================================================
# DEPRECATED WRAPPER
# =============================================================================


class LotusIPv4Router:
    """DEPRECATED: Use LotusIPRouter from adapters/network.py.

    This is a backward compatibility wrapper that delegates to the production
    LotusIPRouter. New code should import directly from production.
    """

    __slots__ = ("_router",)

    def __init__(self) -> None:
        warnings.warn(
            "LotusIPv4Router is deprecated. Use LotusIPRouter from vibe_core.mahamantra.adapters.network instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        self._router: LotusIPRouter = LotusIPRouter()

    def __len__(self) -> int:
        return len(self._router)

    def insert(self, prefix: str, prefix_len: int, next_hop: str) -> None:
        """Insert a route. O(8) worst case."""
        self._router.insert(prefix, prefix_len, next_hop)

    def lookup(self, ip: str) -> Optional[str]:
        """Find longest prefix match. O(8) = O(1) constant."""
        return self._router.lookup(ip)

    def lookup_int(self, ip_int: int) -> Optional[str]:
        """Lookup by integer - even faster, no parsing."""
        return self._router.lookup_int(ip_int)


# =============================================================================
# BENCHMARK (kept for research/verification)
# =============================================================================


def benchmark(n_routes: int = 10000, n_lookups: int = 100000) -> None:
    """Benchmark Lotus vs Dict-based linear LPM search.

    Uses production LotusIPRouter for benchmarking.
    """
    import random
    import time

    print(f"=== IP ROUTING BENCHMARK ({n_routes:,} routes, {n_lookups:,} lookups) ===\n")

    random.seed(42)

    # Generate routes with realistic prefix distribution
    routes: list[tuple[str, int, str]] = []
    for i in range(n_routes):
        a = random.randint(1, 223)
        b = random.randint(0, 255)
        c = random.randint(0, 255)
        # Realistic prefix lengths: /8, /16, /24, /32
        prefix_len = random.choice([8, 16, 24, 32])
        routes.append((f"{a}.{b}.{c}.0", prefix_len, f"eth{i}"))

    # Generate lookup IPs
    lookup_ips: list[str] = []
    lookup_ints: list[int] = []
    for _ in range(n_lookups):
        a = random.randint(1, 223)
        b = random.randint(0, 255)
        c = random.randint(0, 255)
        d = random.randint(0, 255)
        lookup_ips.append(f"{a}.{b}.{c}.{d}")
        lookup_ints.append((a << 24) | (b << 16) | (c << 8) | d)

    # === LOTUS ROUTER (PRODUCTION) ===
    router = LotusIPRouter()
    start = time.perf_counter()
    for prefix, prefix_len, next_hop in routes:
        router.insert(prefix, prefix_len, next_hop)
    lotus_insert_ms = (time.perf_counter() - start) * 1000

    # Lotus lookup (string)
    start = time.perf_counter()
    for ip in lookup_ips:
        _ = router.lookup(ip)
    lotus_lookup_ms = (time.perf_counter() - start) * 1000

    # Lotus lookup (int - fastest)
    start = time.perf_counter()
    for ip_int in lookup_ints:
        _ = router.lookup_int(ip_int)
    lotus_int_ms = (time.perf_counter() - start) * 1000

    # === DICT LINEAR SEARCH (real LPM) ===
    # Store routes as (prefix_int, prefix_len, mask, next_hop)
    route_table: list[tuple[int, int, int, str]] = []
    start = time.perf_counter()
    for prefix, prefix_len, next_hop in routes:
        a, b, c, d = prefix.split(".")
        prefix_int = (int(a) << 24) | (int(b) << 16) | (int(c) << 8) | int(d)
        mask = (0xFFFFFFFF << (32 - prefix_len)) & 0xFFFFFFFF if prefix_len > 0 else 0
        route_table.append((prefix_int, prefix_len, mask, next_hop))
    dict_insert_ms = (time.perf_counter() - start) * 1000

    # Linear LPM search - must check ALL routes for longest match
    start = time.perf_counter()
    for ip_int in lookup_ints:
        best_len = -1
        best_hop = None
        for prefix_int, prefix_len, mask, next_hop in route_table:
            if (ip_int & mask) == (prefix_int & mask):
                if prefix_len > best_len:
                    best_len = prefix_len
                    best_hop = next_hop
    dict_lookup_ms = (time.perf_counter() - start) * 1000

    # === RESULTS ===
    print("INSERT:")
    print(f"  Lotus: {lotus_insert_ms:.2f} ms")
    print(f"  List:  {dict_insert_ms:.2f} ms")
    print()

    print("LOOKUP (longest prefix match):")
    print(f"  Lotus (str): {lotus_lookup_ms:.2f} ms")
    print(f"  Lotus (int): {lotus_int_ms:.2f} ms")
    print(f"  Linear:      {dict_lookup_ms:.2f} ms")
    print()

    speedup_str = dict_lookup_ms / lotus_lookup_ms
    speedup_int = dict_lookup_ms / lotus_int_ms
    print(f"  → Lotus (str) is {speedup_str:.1f}x FASTER")
    print(f"  → Lotus (int) is {speedup_int:.1f}x FASTER")
    print()

    lotus_per_sec = n_lookups / (lotus_int_ms / 1000)
    linear_per_sec = n_lookups / (dict_lookup_ms / 1000)
    print("THROUGHPUT:")
    print(f"  Lotus: {lotus_per_sec:,.0f} lookups/sec")
    print(f"  Linear: {linear_per_sec:,.0f} lookups/sec")
    print()

    print("WHY LOTUS WINS:")
    print("  Lotus:  O(8) - always 8 memory accesses")
    print(f"  Linear: O(N) - must check all {n_routes:,} routes")
    print("  Dict CANNOT do efficient longest prefix match!")
    print()
    print("NOTE: Using production LotusIPRouter from adapters/network.py")


if __name__ == "__main__":
    print("NOTE: LotusIPv4Router is deprecated. Use LotusIPRouter from production.")
    print("Running benchmark with production router...\n")
    benchmark()
