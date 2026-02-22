"""
TESTS: LotusIPRouter - O(1) IPv4 Routing
========================================

"yānti deva-vratā devān pitṝn yānti pitṛ-vratāḥ"
"Those who worship the demigods will go to the demigods."
— Bhagavad Gita 9.25

These tests make LotusIPRouter ALTAR-WORTHY.
"""

import pytest

from vibe_core.mahamantra.adapters.network import (
    LotusIPRouter,
    RouteResult,
    RouterStats,
    create_ip_router,
    BITS_PER_LEVEL,
    SLOTS_PER_LEVEL,
    IPV4_BITS,
    IPV4_LEVELS,
)
from vibe_core.mahamantra.protocols._seed import QUARTERS, WORDS, AKSARA_COUNT


# =============================================================================
# CONSTANTS TESTS
# =============================================================================


class TestNetworkConstants:
    """Test constants are derived from seed."""

    def test_bits_per_level_is_quarters(self):
        """BITS_PER_LEVEL must equal QUARTERS (4)."""
        assert BITS_PER_LEVEL == QUARTERS == 4

    def test_slots_per_level_is_words(self):
        """SLOTS_PER_LEVEL must equal WORDS (16)."""
        assert SLOTS_PER_LEVEL == WORDS == 16

    def test_ipv4_bits_is_aksara(self):
        """IPV4_BITS must equal AKSARA_COUNT (32)."""
        assert IPV4_BITS == AKSARA_COUNT == 32

    def test_ipv4_levels_is_8(self):
        """IPV4_LEVELS must be 8 (32 / 4)."""
        assert IPV4_LEVELS == IPV4_BITS // BITS_PER_LEVEL == 8


# =============================================================================
# RESULT TYPE TESTS
# =============================================================================


class TestRouteResult:
    """Test RouteResult dataclass."""

    def test_create_route_result(self):
        """Can create RouteResult."""
        result = RouteResult(
            ip="192.168.1.100",
            ip_int=3232235876,
            next_hop="gateway_a",
            matched_prefix="192.168.1.0",
            matched_prefix_len=24,
            ops=8,
        )
        assert result.ip == "192.168.1.100"
        assert result.next_hop == "gateway_a"
        assert result.matched_prefix_len == 24
        assert result.ops == 8


class TestRouterStats:
    """Test RouterStats dataclass."""

    def test_create_router_stats(self):
        """Can create RouterStats."""
        stats = RouterStats(
            routes=100,
            levels=8,
            bits_per_level=4,
            max_capacity="2^32 IPv4 addresses",
        )
        assert stats.routes == 100
        assert stats.levels == 8


# =============================================================================
# IP CONVERSION TESTS
# =============================================================================


class TestIPConversion:
    """Test IP conversion utilities."""

    def test_ip_to_int_simple(self):
        """IP to int conversion works."""
        router = LotusIPRouter()
        assert router._ip_to_int("0.0.0.0") == 0
        assert router._ip_to_int("255.255.255.255") == 0xFFFFFFFF
        assert router._ip_to_int("192.168.1.1") == 0xC0A80101

    def test_int_to_ip_simple(self):
        """Int to IP conversion works."""
        router = LotusIPRouter()
        assert router._int_to_ip(0) == "0.0.0.0"
        assert router._int_to_ip(0xFFFFFFFF) == "255.255.255.255"
        assert router._int_to_ip(0xC0A80101) == "192.168.1.1"

    def test_roundtrip_conversion(self):
        """IP -> int -> IP roundtrip."""
        router = LotusIPRouter()
        test_ips = ["192.168.1.1", "10.0.0.1", "172.16.0.1", "8.8.8.8"]
        for ip in test_ips:
            assert router._int_to_ip(router._ip_to_int(ip)) == ip

    def test_invalid_ip_raises(self):
        """Invalid IP raises ValueError."""
        router = LotusIPRouter()
        with pytest.raises(ValueError):
            router._ip_to_int("192.168.1")  # Too few parts
        with pytest.raises(ValueError):
            router._ip_to_int("192.168.1.1.1")  # Too many parts


# =============================================================================
# ROUTER INIT TESTS
# =============================================================================


class TestLotusIPRouterInit:
    """Test router initialization."""

    def test_create_empty_router(self):
        """Can create empty router."""
        router = LotusIPRouter()
        assert len(router) == 0

    def test_len_empty(self):
        """Empty router has length 0."""
        router = LotusIPRouter()
        assert len(router) == 0


# =============================================================================
# INSERT TESTS
# =============================================================================


class TestLotusIPRouterInsert:
    """Test insert methods."""

    def test_insert_route(self):
        """Can insert a route."""
        router = LotusIPRouter()
        router.insert("192.168.0.0", 16, "gateway_a")
        assert len(router) == 1

    def test_insert_cidr(self):
        """Can insert using CIDR notation."""
        router = LotusIPRouter()
        router.insert_cidr("192.168.0.0/16", "gateway_a")
        assert len(router) == 1

    def test_insert_multiple_routes(self):
        """Can insert multiple routes."""
        router = LotusIPRouter()
        router.insert("192.168.0.0", 16, "gateway_a")
        router.insert("10.0.0.0", 8, "gateway_b")
        router.insert("172.16.0.0", 12, "gateway_c")
        assert len(router) == 3

    def test_insert_invalid_prefix_len_raises(self):
        """Invalid prefix length raises ValueError."""
        router = LotusIPRouter()
        with pytest.raises(ValueError):
            router.insert("192.168.0.0", -1, "gw")
        with pytest.raises(ValueError):
            router.insert("192.168.0.0", 33, "gw")

    def test_insert_default_route(self):
        """Can insert default route (0.0.0.0/0)."""
        router = LotusIPRouter()
        router.insert("0.0.0.0", 0, "default_gw")
        assert len(router) == 1


# =============================================================================
# LOOKUP TESTS
# =============================================================================


class TestLotusIPRouterLookup:
    """Test lookup methods."""

    @pytest.fixture
    def router_with_routes(self) -> LotusIPRouter:
        """Create router with test routes."""
        router = LotusIPRouter()
        router.insert("192.168.0.0", 16, "gateway_a")
        router.insert("192.168.1.0", 24, "gateway_b")
        router.insert("10.0.0.0", 8, "gateway_c")
        return router

    def test_lookup_exact_match(self, router_with_routes: LotusIPRouter):
        """Lookup finds exact match."""
        # 192.168.1.0/24 is more specific than 192.168.0.0/16
        result = router_with_routes.lookup("192.168.1.100")
        assert result == "gateway_b"

    def test_lookup_prefix_match(self, router_with_routes: LotusIPRouter):
        """Lookup finds prefix match."""
        # 192.168.2.100 matches 192.168.0.0/16
        result = router_with_routes.lookup("192.168.2.100")
        assert result == "gateway_a"

    def test_lookup_no_match(self, router_with_routes: LotusIPRouter):
        """Lookup returns None for no match."""
        result = router_with_routes.lookup("8.8.8.8")
        assert result is None

    def test_lookup_int(self, router_with_routes: LotusIPRouter):
        """lookup_int works with integer IP."""
        ip_int = router_with_routes._ip_to_int("192.168.1.100")
        result = router_with_routes.lookup_int(ip_int)
        assert result == "gateway_b"


# =============================================================================
# LONGEST PREFIX MATCH TESTS
# =============================================================================


class TestLongestPrefixMatch:
    """Test longest prefix match behavior."""

    def test_lpm_chooses_longest(self):
        """LPM chooses longest matching prefix."""
        router = LotusIPRouter()
        router.insert("0.0.0.0", 0, "default")
        router.insert("192.0.0.0", 8, "class_c")
        router.insert("192.168.0.0", 16, "local")
        router.insert("192.168.1.0", 24, "subnet")
        router.insert("192.168.1.128", 25, "half_subnet")

        # Should match most specific
        assert router.lookup("192.168.1.200") == "half_subnet"
        assert router.lookup("192.168.1.50") == "subnet"
        assert router.lookup("192.168.2.1") == "local"
        assert router.lookup("192.0.1.1") == "class_c"
        assert router.lookup("8.8.8.8") == "default"

    def test_lpm_with_host_route(self):
        """LPM handles /32 host routes."""
        router = LotusIPRouter()
        router.insert("192.168.1.0", 24, "subnet")
        router.insert("192.168.1.100", 32, "specific_host")

        assert router.lookup("192.168.1.100") == "specific_host"
        assert router.lookup("192.168.1.99") == "subnet"


# =============================================================================
# QUERY TESTS
# =============================================================================


class TestLotusIPRouterQuery:
    """Test query method with full result."""

    def test_query_returns_route_result(self):
        """query() returns RouteResult."""
        router = LotusIPRouter()
        router.insert("192.168.1.0", 24, "gateway")

        result = router.query("192.168.1.100")
        assert isinstance(result, RouteResult)
        assert result.ip == "192.168.1.100"
        assert result.next_hop == "gateway"
        assert result.matched_prefix == "192.168.1.0"
        assert result.matched_prefix_len == 24
        assert result.ops == 8

    def test_query_no_match(self):
        """query() handles no match."""
        router = LotusIPRouter()
        result = router.query("8.8.8.8")

        assert result.next_hop is None
        assert result.matched_prefix is None


# =============================================================================
# BATCH OPERATION TESTS
# =============================================================================


class TestLotusIPRouterBatch:
    """Test batch operations."""

    def test_insert_batch(self):
        """insert_batch() inserts multiple routes."""
        router = LotusIPRouter()
        routes = [
            ("192.168.0.0", 16, "gw_a"),
            ("10.0.0.0", 8, "gw_b"),
            ("172.16.0.0", 12, "gw_c"),
        ]
        count = router.insert_batch(routes)

        assert count == 3
        assert len(router) == 3

    def test_lookup_batch(self):
        """lookup_batch() looks up multiple IPs."""
        router = LotusIPRouter()
        router.insert("192.168.0.0", 16, "gw_a")
        router.insert("10.0.0.0", 8, "gw_b")

        results = router.lookup_batch(
            [
                "192.168.1.1",
                "10.0.0.1",
                "8.8.8.8",
            ]
        )

        assert results == ["gw_a", "gw_b", None]


# =============================================================================
# STATS TESTS
# =============================================================================


class TestLotusIPRouterStats:
    """Test stats method."""

    def test_stats_empty_router(self):
        """stats() on empty router."""
        router = LotusIPRouter()
        stats = router.stats()

        assert isinstance(stats, RouterStats)
        assert stats.routes == 0
        assert stats.levels == 8
        assert stats.bits_per_level == 4

    def test_stats_with_routes(self):
        """stats() tracks route count."""
        router = LotusIPRouter()
        router.insert("192.168.0.0", 16, "gw")
        router.insert("10.0.0.0", 8, "gw")

        stats = router.stats()
        assert stats.routes == 2


# =============================================================================
# FACTORY FUNCTION TESTS
# =============================================================================


class TestCreateIPRouter:
    """Test factory function."""

    def test_create_ip_router(self):
        """create_ip_router() creates LotusIPRouter."""
        router = create_ip_router()
        assert isinstance(router, LotusIPRouter)
        assert len(router) == 0


# =============================================================================
# INTEGRATION TESTS
# =============================================================================


class TestLotusIPRouterIntegration:
    """Integration tests for LotusIPRouter."""

    def test_realistic_routing_table(self):
        """Realistic routing table scenario."""
        router = LotusIPRouter()

        # Default route
        router.insert("0.0.0.0", 0, "internet")

        # Private networks
        router.insert("10.0.0.0", 8, "datacenter")
        router.insert("172.16.0.0", 12, "office")
        router.insert("192.168.0.0", 16, "home")

        # More specific subnets
        router.insert("10.1.0.0", 16, "db_cluster")
        router.insert("10.1.1.0", 24, "db_primary")
        router.insert("192.168.1.0", 24, "guest_wifi")

        # Verify LPM works correctly
        assert router.lookup("10.1.1.5") == "db_primary"
        assert router.lookup("10.1.2.5") == "db_cluster"
        assert router.lookup("10.2.0.1") == "datacenter"
        assert router.lookup("192.168.1.50") == "guest_wifi"
        assert router.lookup("192.168.2.50") == "home"
        assert router.lookup("172.16.5.5") == "office"
        assert router.lookup("8.8.8.8") == "internet"

    def test_bgp_style_prefixes(self):
        """BGP-style overlapping prefixes."""
        router = LotusIPRouter()

        # Simulate ISP routing
        router.insert("0.0.0.0", 0, "upstream")
        router.insert("1.0.0.0", 8, "apnic")
        router.insert("1.1.0.0", 16, "cloudflare_range")
        router.insert("1.1.1.0", 24, "cloudflare_dns")

        assert router.lookup("1.1.1.1") == "cloudflare_dns"
        assert router.lookup("1.1.2.1") == "cloudflare_range"
        assert router.lookup("1.2.3.4") == "apnic"

    def test_constant_time_guarantee(self):
        """O(8) constant time regardless of table size."""
        router = LotusIPRouter()

        # Insert many routes
        for i in range(256):
            router.insert(f"{i}.0.0.0", 8, f"gateway_{i}")

        # Every lookup is still O(8)
        result = router.query("100.50.25.12")
        assert result.ops == 8  # Always 8 operations
        assert result.next_hop == "gateway_100"
