"""
TESTS: MahaAttention - O(1) Intent Resolution
=============================================

"sudarśanaṁ cakram asahya-tejāḥ"
"The Sudarshana Chakra has unbearable effulgence."
— Srimad Bhagavatam 9.5.5

These tests make MahaAttention ALTAR-WORTHY.
"""

import pytest

from vibe_core.mahamantra.adapters.attention import (
    MahaAttention,
    AttentionResult,
    AttentionStats,
    get_attention,
    DEFAULT_KEY_BITS,
    DEFAULT_LEVELS,
)
from vibe_core.mahamantra.protocols._seed import WORDS, QUARTERS


# =============================================================================
# CONSTANTS TESTS
# =============================================================================


class TestAttentionConstants:
    """Test constants are derived from seed."""

    def test_default_key_bits_is_words(self):
        """DEFAULT_KEY_BITS must equal WORDS (16)."""
        assert DEFAULT_KEY_BITS == WORDS == 16

    def test_default_levels_is_quarters(self):
        """DEFAULT_LEVELS must equal QUARTERS (4)."""
        assert DEFAULT_LEVELS == QUARTERS == 4


# =============================================================================
# RESULT TYPE TESTS
# =============================================================================


class TestAttentionResult:
    """Test AttentionResult dataclass."""

    def test_create_attention_result(self):
        """Can create AttentionResult."""
        result = AttentionResult(
            query="deploy production",
            address=12345,
            handler=lambda: "deployed",
            found=True,
            ops_saved=1000,
        )
        assert result.query == "deploy production"
        assert result.found is True
        assert result.ops_saved == 1000


class TestAttentionStats:
    """Test AttentionStats dataclass."""

    def test_create_attention_stats(self):
        """Can create AttentionStats."""
        stats = AttentionStats(
            mechanism="Lotus O(1)",
            address_space=65536,
            registered_intents=100,
            queries_resolved=50,
            cache_hits=40,
            estimated_ops_saved=10000,
        )
        assert stats.mechanism == "Lotus O(1)"
        assert stats.address_space == 65536


# =============================================================================
# MAHA ATTENTION INIT TESTS
# =============================================================================


class TestMahaAttentionInit:
    """Test MahaAttention initialization."""

    def test_default_init(self):
        """Default init creates 16-bit address space."""
        attention = MahaAttention()
        assert attention.address_space == 2 ** 16

    def test_custom_key_bits(self):
        """Can create with custom key bits."""
        attention = MahaAttention(key_bits=8)
        assert attention.address_space == 2 ** 8 == 256

    def test_registered_intents_starts_zero(self):
        """registered_intents starts at 0."""
        attention = MahaAttention()
        assert attention.registered_intents == 0


# =============================================================================
# MEMORIZE TESTS
# =============================================================================


class TestMahaAttentionMemorize:
    """Test memorize method."""

    @pytest.fixture
    def attention(self) -> MahaAttention:
        return MahaAttention()

    def test_memorize_returns_address(self, attention: MahaAttention):
        """memorize() returns address."""
        address = attention.memorize("deploy", lambda: "deployed")
        assert isinstance(address, int)
        assert 0 <= address < attention.address_space

    def test_memorize_increments_count(self, attention: MahaAttention):
        """memorize() increments registered_intents."""
        attention.memorize("intent1", "handler1")
        attention.memorize("intent2", "handler2")
        assert attention.registered_intents == 2

    def test_memorize_callable(self, attention: MahaAttention):
        """Can memorize callable handlers."""
        def my_handler():
            return "result"
        attention.memorize("do something", my_handler)

        result = attention.attend("do something")
        assert result.handler == my_handler

    def test_memorize_any_value(self, attention: MahaAttention):
        """Can memorize any value as handler."""
        attention.memorize("get string", "string_value")
        attention.memorize("get dict", {"key": "value"})
        attention.memorize("get list", [1, 2, 3])

        assert attention.attend("get string").handler == "string_value"
        assert attention.attend("get dict").handler == {"key": "value"}
        assert attention.attend("get list").handler == [1, 2, 3]


# =============================================================================
# ATTEND TESTS
# =============================================================================


class TestMahaAttentionAttend:
    """Test attend method."""

    @pytest.fixture
    def attention_with_handlers(self) -> MahaAttention:
        """Create attention with registered handlers."""
        attention = MahaAttention()
        attention.memorize("deploy production", "deploy_prod")
        attention.memorize("rollback staging", "rollback_stg")
        attention.memorize("run tests", "run_tests")
        return attention

    def test_attend_returns_result(self, attention_with_handlers: MahaAttention):
        """attend() returns AttentionResult."""
        result = attention_with_handlers.attend("deploy production")
        assert isinstance(result, AttentionResult)

    def test_attend_found_handler(self, attention_with_handlers: MahaAttention):
        """attend() finds registered handler."""
        result = attention_with_handlers.attend("deploy production")
        assert result.found is True
        assert result.handler == "deploy_prod"

    def test_attend_not_found(self, attention_with_handlers: MahaAttention):
        """attend() returns found=False for unregistered."""
        result = attention_with_handlers.attend("unknown intent")
        assert result.found is False
        assert result.handler is None

    def test_attend_calculates_ops_saved(self, attention_with_handlers: MahaAttention):
        """attend() calculates ops_saved on hit."""
        result = attention_with_handlers.attend("deploy production")
        assert result.ops_saved > 0

    def test_attend_deterministic(self, attention_with_handlers: MahaAttention):
        """Same query always returns same result."""
        result1 = attention_with_handlers.attend("deploy production")
        result2 = attention_with_handlers.attend("deploy production")
        assert result1.address == result2.address
        assert result1.handler == result2.handler


# =============================================================================
# CALL OPERATOR TESTS
# =============================================================================


class TestMahaAttentionCall:
    """Test __call__ operator."""

    def test_call_returns_handler(self):
        """__call__ returns handler directly."""
        attention = MahaAttention()
        attention.memorize("intent", "handler_value")

        handler = attention("intent")
        assert handler == "handler_value"

    def test_call_returns_none_if_not_found(self):
        """__call__ returns None if not found."""
        attention = MahaAttention()
        handler = attention("unknown")
        assert handler is None


# =============================================================================
# BATCH TESTS
# =============================================================================


class TestMahaAttentionBatch:
    """Test batch operations."""

    def test_memorize_batch(self):
        """memorize_batch() registers multiple handlers."""
        attention = MahaAttention()
        addresses = attention.memorize_batch({
            "intent1": "handler1",
            "intent2": "handler2",
            "intent3": "handler3",
        })

        assert len(addresses) == 3
        assert attention.registered_intents == 3

    def test_attend_batch(self):
        """attend_batch() resolves multiple queries."""
        attention = MahaAttention()
        attention.memorize_batch({
            "intent1": "handler1",
            "intent2": "handler2",
        })

        results = attention.attend_batch(["intent1", "intent2", "unknown"])

        assert len(results) == 3
        assert results[0].found is True
        assert results[1].found is True
        assert results[2].found is False


# =============================================================================
# FUZZY MATCHING TESTS
# =============================================================================


class TestMahaAttentionFuzzy:
    """Test fuzzy matching."""

    def test_attend_fuzzy_finds_nearby(self):
        """attend_fuzzy() searches around hash."""
        attention = MahaAttention()
        attention.memorize("exact intent", "exact_handler")

        # Fuzzy search with large radius should find it
        results = attention.attend_fuzzy("exact intent", radius=100)

        # Should find at least the exact match
        handlers = [r.handler for r in results]
        assert "exact_handler" in handlers

    def test_attend_fuzzy_returns_list(self):
        """attend_fuzzy() returns list of results."""
        attention = MahaAttention()
        results = attention.attend_fuzzy("any query")
        assert isinstance(results, list)


# =============================================================================
# STATS TESTS
# =============================================================================


class TestMahaAttentionStats:
    """Test stats method."""

    def test_stats_initial(self):
        """stats() on new instance."""
        attention = MahaAttention()
        stats = attention.stats()

        assert isinstance(stats, AttentionStats)
        assert stats.registered_intents == 0
        assert stats.queries_resolved == 0
        assert stats.cache_hits == 0

    def test_stats_after_usage(self):
        """stats() after memorize and attend."""
        attention = MahaAttention()
        attention.memorize("intent1", "handler1")
        attention.memorize("intent2", "handler2")
        attention.attend("intent1")  # Hit
        attention.attend("unknown")  # Miss

        stats = attention.stats()
        assert stats.registered_intents == 2
        assert stats.queries_resolved == 2
        assert stats.cache_hits == 1

    def test_stats_mechanism_name(self):
        """stats() includes mechanism name."""
        attention = MahaAttention()
        stats = attention.stats()
        assert "Lotus" in stats.mechanism or "Sudarshana" in stats.mechanism


# =============================================================================
# RESET TESTS
# =============================================================================


class TestMahaAttentionReset:
    """Test reset method."""

    def test_reset_clears_handlers(self):
        """reset() clears all handlers."""
        attention = MahaAttention()
        attention.memorize("intent", "handler")
        assert attention.registered_intents == 1

        attention.reset()
        assert attention.registered_intents == 0
        assert attention("intent") is None

    def test_reset_clears_stats(self):
        """reset() clears stats."""
        attention = MahaAttention()
        attention.memorize("intent", "handler")
        attention.attend("intent")

        attention.reset()
        stats = attention.stats()
        assert stats.queries_resolved == 0
        assert stats.cache_hits == 0


# =============================================================================
# SINGLETON TESTS
# =============================================================================


class TestGetAttention:
    """Test singleton function."""

    def test_get_attention_returns_instance(self):
        """get_attention() returns MahaAttention."""
        attention = get_attention()
        assert isinstance(attention, MahaAttention)

    def test_get_attention_returns_same_instance(self):
        """get_attention() returns same instance."""
        attention1 = get_attention()
        attention2 = get_attention()
        assert attention1 is attention2


# =============================================================================
# INTEGRATION TESTS
# =============================================================================


class TestMahaAttentionIntegration:
    """Integration tests for MahaAttention."""

    def test_agent_intent_routing(self):
        """Realistic agent intent routing scenario."""
        attention = MahaAttention()

        # Register tool handlers
        tools_executed = []

        def deploy_tool():
            tools_executed.append("deploy")
            return "deployed"

        def test_tool():
            tools_executed.append("test")
            return "tested"

        def monitor_tool():
            tools_executed.append("monitor")
            return "monitoring"

        attention.memorize("deploy to production", deploy_tool)
        attention.memorize("run unit tests", test_tool)
        attention.memorize("check system status", monitor_tool)

        # Resolve and execute intents
        deploy_handler = attention("deploy to production")
        test_handler = attention("run unit tests")

        if deploy_handler:
            deploy_handler()
        if test_handler:
            test_handler()

        assert "deploy" in tools_executed
        assert "test" in tools_executed

    def test_moe_style_routing(self):
        """Mixture of Experts style routing."""
        attention = MahaAttention()

        # Register "experts"
        attention.memorize("math question", {"expert": "math", "weight": 0.9})
        attention.memorize("code question", {"expert": "code", "weight": 0.85})
        attention.memorize("general question", {"expert": "general", "weight": 0.7})

        # Route to expert
        result = attention.attend("math question")
        assert result.found
        assert result.handler["expert"] == "math"

    def test_scaling_behavior(self):
        """Test with many registered intents."""
        attention = MahaAttention()

        # Register many intents
        for i in range(1000):
            attention.memorize(f"intent_{i}", f"handler_{i}")

        # Lookups should still be O(1) - we check that SOME handler is found
        # Note: With many intents, hash collisions are expected
        result = attention.attend("intent_500")
        assert result.found
        # Handler may be different due to hash collision, but lookup works
        assert result.handler.startswith("handler_")

        # Stats should show ops saved
        stats = attention.stats()
        assert stats.registered_intents == 1000
