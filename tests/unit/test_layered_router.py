"""
tests/unit/test_layered_router.py

Unit tests for LayeredRouter - 4-layer routing cascade.
Tests Layer 1 (exact), Layer 2 (semantic), Layer 3 (context), Layer 3.5 (akshara),
and fallback behavior.

OPUS-305: Updated attribute names to match RouteResult schema from state/schema.py:
  - circuit_id -> target_id
  - layer -> reason
  - extracted_params -> params
  - syscall_type/target_agent -> now in params dict
"""

import pytest

from vibe_core.runtime.layered_router import LayeredRouter
from vibe_core.state.schema import RouteResult


@pytest.fixture
def router_with_circuits():
    """Router with test circuits loaded.

    NOTE: semantic_grounding is INSIDE the circuit block, matching real YAML structure.
    """
    router = LayeredRouter()
    router._circuits = {
        "SYSTEM_STATUS_V2": {
            "circuit": {
                "id": "SYSTEM_STATUS_V2",
                "intent_patterns": ["status", "system status", "health"],
            }
        },
        "FEATURE_IMPLEMENT_V2": {
            "circuit": {
                "id": "FEATURE_IMPLEMENT_V2",
                "semantic_grounding": {
                    "syscall_type": "DISPATCH_TASK",
                    "target_agent": "engineer",
                    "intent_patterns": [
                        r"implement\s+(?:a\s+)?(?:new\s+)?feature",
                        r"add\s+(?:a\s+)?(?:new\s+)?(?:feature|functionality)",
                    ],
                    "param_extraction": {
                        "feature_description": {
                            "patterns": [r"implement\s+(.+)", r"add\s+(?:feature\s+)?(.+)"],
                            "required": True,
                        }
                    },
                },
            }
        },
        "DEBUG_FIX_V2": {
            "circuit": {
                "id": "DEBUG_FIX_V2",
                "semantic_grounding": {
                    "intent_patterns": [
                        r"fix\s+(?:the\s+)?(?:bug|error|issue)",
                        r"debug\s+(?:the\s+)?(?:error|failure)",
                    ],
                },
            }
        },
    }
    router._build_indexes()
    return router


class TestLayer1Exact:
    """Layer 1: Exact match tests."""

    def test_exact_match(self, router_with_circuits):
        """Test exact keyword match."""
        result = router_with_circuits.route("status")
        assert result.target_id == "SYSTEM_STATUS_V2"
        assert result.confidence == 1.0
        assert result.reason == "exact"

    def test_exact_match_case_insensitive(self, router_with_circuits):
        """Test exact match is case-insensitive."""
        result = router_with_circuits.route("STATUS")
        assert result.target_id == "SYSTEM_STATUS_V2"
        assert result.confidence == 1.0

    def test_exact_match_mixed_case(self, router_with_circuits):
        """Test exact match with mixed case."""
        result = router_with_circuits.route("Health")
        assert result.target_id == "SYSTEM_STATUS_V2"
        assert result.confidence == 1.0

    def test_exact_prefix_with_args(self, router_with_circuits):
        """Test exact prefix match with arguments."""
        result = router_with_circuits.route("status verbose")
        assert result.target_id == "SYSTEM_STATUS_V2"
        assert result.confidence == 0.95
        assert result.reason == "exact_prefix"
        assert result.params.get("args") == "verbose"

    def test_exact_match_multi_word_pattern(self, router_with_circuits):
        """Test exact match with multi-word patterns."""
        result = router_with_circuits.route("system status")
        assert result.target_id == "SYSTEM_STATUS_V2"
        assert result.confidence == 1.0

    def test_no_partial_exact_match(self, router_with_circuits):
        """Ensure partial substring doesn't match in Layer 1."""
        # "system" alone shouldn't match "system status"
        result = router_with_circuits.route("system")
        # Should fall through to Layer 2/3/fallback, not match Layer 1
        assert result.target_id != "SYSTEM_STATUS_V2" or result.reason != "exact"


class TestLayer2Semantic:
    """Layer 2: Semantic pattern match tests."""

    def test_semantic_match_basic(self, router_with_circuits):
        """Test semantic pattern matching."""
        result = router_with_circuits.route("implement a new feature for logging")
        assert result.target_id == "FEATURE_IMPLEMENT_V2"
        assert result.reason == "semantic"
        assert result.confidence >= 0.7

    def test_semantic_match_variation(self, router_with_circuits):
        """Test semantic pattern with variation."""
        result = router_with_circuits.route("add functionality to track users")
        assert result.target_id == "FEATURE_IMPLEMENT_V2"
        assert result.reason == "semantic"

    def test_semantic_param_extraction(self, router_with_circuits):
        """Test parameter extraction from natural language."""
        result = router_with_circuits.route("implement feature for api call logging")
        assert "feature_description" in result.params
        # Should extract "feature for api call logging" from the input
        desc = result.params["feature_description"]
        assert "api" in desc.lower() or "logging" in desc.lower() or "feature" in desc.lower()

    def test_semantic_debug_match(self, router_with_circuits):
        """Test semantic match for debug patterns."""
        result = router_with_circuits.route("fix the bug in auth module")
        assert result.target_id == "DEBUG_FIX_V2"
        assert result.reason == "semantic"

    def test_semantic_error_match(self, router_with_circuits):
        """Test semantic match for error patterns."""
        result = router_with_circuits.route("debug the error in parser")
        assert result.target_id == "DEBUG_FIX_V2"
        assert result.reason == "semantic"

    def test_semantic_syscall_metadata(self, router_with_circuits):
        """Test that semantic_grounding metadata is included in params."""
        result = router_with_circuits.route("implement new feature")
        assert result.params.get("syscall_type") == "DISPATCH_TASK"
        assert result.params.get("target_agent") == "engineer"

    def test_semantic_pattern_specificity(self, router_with_circuits):
        """Test that more specific patterns get higher scores."""
        # More specific pattern should win
        result = router_with_circuits.route("implement a new feature for api logging")
        assert result.target_id == "FEATURE_IMPLEMENT_V2"
        assert result.confidence >= 0.7


class TestLayer3Context:
    """Layer 3: Context-aware routing tests."""

    def test_context_boost_recent(self, router_with_circuits):
        """Test confidence boost from recent circuit usage."""

        # Mock ephemeral storage
        class MockEphemeral:
            def __init__(self, data):
                self._data = data

            def get(self, key, default=None):
                return self._data.get(key, default)

            def set(self, key, value):
                self._data[key] = value

        router_with_circuits._ephemeral = MockEphemeral(
            {"recent_circuits": ["FEATURE_IMPLEMENT_V2", "FEATURE_IMPLEMENT_V2"]}
        )

        result = router_with_circuits.route("implement new feature for users")
        # Should have boosted confidence due to recent usage
        assert result.confidence > 0.7
        assert result.target_id == "FEATURE_IMPLEMENT_V2"

    def test_concept_extraction(self, router_with_circuits):
        """Test concept extraction from input."""
        concepts = router_with_circuits._extract_concepts("fix security bug in auth")
        # Should extract "security" and "development" concepts
        assert "security" in concepts or "development" in concepts


class TestFallback:
    """Fallback behavior tests."""

    def test_fallback_on_no_match(self, router_with_circuits):
        """Test fallback when no patterns match."""
        result = router_with_circuits.route("xyzzy random gibberish")
        assert result.target_id == "SIMPLE_QUERY"
        assert result.reason == "fallback"
        assert result.confidence == 0.3

    def test_fallback_includes_original_input(self, router_with_circuits):
        """Test that fallback preserves original input."""
        result = router_with_circuits.route("xyzzy")
        assert result.params.get("user_input") == "xyzzy"


class TestIndexBuilding:
    """Tests for index building at boot time."""

    def test_layer1_index_building(self, router_with_circuits):
        """Test that Layer 1 indexes are built correctly."""
        assert "status" in router_with_circuits._exact_index
        assert "health" in router_with_circuits._exact_index
        assert "system status" in router_with_circuits._exact_index

    def test_layer2_index_building(self, router_with_circuits):
        """Test that Layer 2 semantic patterns are compiled."""
        assert "FEATURE_IMPLEMENT_V2" in router_with_circuits._semantic_patterns
        assert "DEBUG_FIX_V2" in router_with_circuits._semantic_patterns

    def test_param_extractors_built(self, router_with_circuits):
        """Test that param extractors are loaded."""
        assert "FEATURE_IMPLEMENT_V2" in router_with_circuits._param_extractors
        extractors = router_with_circuits._param_extractors["FEATURE_IMPLEMENT_V2"]
        assert "feature_description" in extractors


class TestEdgeCases:
    """Edge case tests."""

    def test_empty_input(self, router_with_circuits):
        """Test handling of empty input."""
        result = router_with_circuits.route("")
        assert result.target_id == "SIMPLE_QUERY"
        assert result.reason == "fallback"

    def test_whitespace_only_input(self, router_with_circuits):
        """Test handling of whitespace-only input."""
        result = router_with_circuits.route("   ")
        assert result.target_id == "SIMPLE_QUERY"
        assert result.reason == "fallback"

    def test_very_long_input(self, router_with_circuits):
        """Test handling of very long input."""
        long_input = "implement feature " + "with a very long description " * 50
        result = router_with_circuits.route(long_input)
        # Should still match semantic patterns
        assert result.target_id == "FEATURE_IMPLEMENT_V2"
        assert result.reason == "semantic"

    def test_special_characters(self, router_with_circuits):
        """Test handling of special characters."""
        result = router_with_circuits.route("implement @#$% feature")
        # Should still match despite special chars
        assert result.target_id == "FEATURE_IMPLEMENT_V2" or result.reason == "fallback"

    def test_unicode_characters(self, router_with_circuits):
        """Test handling of unicode characters."""
        result = router_with_circuits.route("implement café feature")
        # Should handle unicode gracefully
        assert isinstance(result, RouteResult)


class TestRouteResult:
    """Tests for RouteResult dataclass from state/schema.py."""

    def test_route_result_construction(self):
        """Test RouteResult can be constructed with correct schema."""
        result = RouteResult(
            target_id="TEST_CIRCUIT",
            target_type="circuit",
            confidence=0.95,
            reason="semantic",
            params={"key": "value", "syscall_type": "TEST_TYPE", "target_agent": "test_agent"},
        )
        assert result.target_id == "TEST_CIRCUIT"
        assert result.target_type == "circuit"
        assert result.confidence == 0.95
        assert result.reason == "semantic"
        assert result.params == {"key": "value", "syscall_type": "TEST_TYPE", "target_agent": "test_agent"}
        assert result.params.get("syscall_type") == "TEST_TYPE"
        assert result.params.get("target_agent") == "test_agent"

    def test_route_result_default_params(self):
        """Test RouteResult defaults."""
        result = RouteResult(target_id="TEST", target_type="circuit", confidence=1.0, reason="exact")
        assert result.params == {}
        assert result.is_fallback is False


class TestLayerCascade:
    """Tests for the 4-layer cascade behavior."""

    def test_layer1_takes_precedence(self, router_with_circuits):
        """Test that Layer 1 results are returned without checking Layer 2."""
        # Add a semantic pattern that would also match
        router_with_circuits._circuits["TEST_SEMANTIC"] = {
            "circuit": {
                "id": "TEST_SEMANTIC",
                "semantic_grounding": {
                    "intent_patterns": [r"status.*"],
                },
            }
        }
        router_with_circuits._build_indexes()

        result = router_with_circuits.route("status")
        # Should return Layer 1 match, not Layer 2
        assert result.reason == "exact"
        assert result.target_id == "SYSTEM_STATUS_V2"

    def test_layer2_used_when_layer1_fails(self, router_with_circuits):
        """Test that Layer 2 is used when Layer 1 finds no match."""
        result = router_with_circuits.route("implement new feature for logging")
        assert result.reason == "semantic"
        assert result.target_id == "FEATURE_IMPLEMENT_V2"

    def test_fallback_used_when_all_fail(self, router_with_circuits):
        """Test that fallback is used when no layers match."""
        result = router_with_circuits.route("completely unrelated gibberish")
        assert result.reason == "fallback"
        assert result.target_id == "SIMPLE_QUERY"


class TestRegexPatterns:
    """Tests for regex pattern compilation and matching."""

    def test_invalid_regex_handling(self):
        """Test that invalid regex patterns are handled gracefully."""
        router = LayeredRouter()
        router._circuits = {
            "TEST_CIRCUIT": {
                "circuit": {
                    "id": "TEST_CIRCUIT",
                    "semantic_grounding": {
                        "intent_patterns": [
                            r"valid\s+pattern",
                            r"[invalid(regex",  # Invalid regex
                            r"another\s+valid",
                        ]
                    },
                }
            }
        }
        # Should not raise exception
        router._build_indexes()
        # Valid patterns should still be loaded
        assert "TEST_CIRCUIT" in router._semantic_patterns

    def test_case_insensitive_regex(self, router_with_circuits):
        """Test that regex patterns are case-insensitive."""
        result = router_with_circuits.route("IMPLEMENT a new FEATURE")
        assert result.target_id == "FEATURE_IMPLEMENT_V2"
        assert result.reason == "semantic"

    def test_regex_with_alternation(self, router_with_circuits):
        """Test regex patterns with alternation."""
        result = router_with_circuits.route("add new functionality")
        assert result.target_id == "FEATURE_IMPLEMENT_V2"

        result = router_with_circuits.route("add feature for tracking")
        assert result.target_id == "FEATURE_IMPLEMENT_V2"


class TestParamExtraction:
    """Tests for parameter extraction."""

    def test_basic_param_extraction(self, router_with_circuits):
        """Test basic parameter extraction."""
        result = router_with_circuits.route("implement feature for user authentication")
        params = result.params
        assert "feature_description" in params
        # Should extract something containing auth or feature
        assert "auth" in params["feature_description"].lower() or "feature" in params["feature_description"].lower()

    def test_param_extraction_with_articles(self, router_with_circuits):
        """Test parameter extraction handles articles correctly."""
        result = router_with_circuits.route("add a new feature for caching")
        params = result.params
        assert "feature_description" in params
        # Should extract "caching" or similar
        assert any(word in params["feature_description"].lower() for word in ["caching", "feature"])

    def test_multiple_param_extractors(self):
        """Test circuits with multiple param extractors."""
        router = LayeredRouter()
        router._circuits = {
            "TEST_CIRCUIT": {
                "circuit": {
                    "id": "TEST_CIRCUIT",
                    "semantic_grounding": {
                        "intent_patterns": [r"action\s+(.+)\s+on\s+(.+)"],
                        "param_extraction": {
                            "action_type": {
                                "patterns": [r"action\s+(\w+)"],
                            },
                            "target": {
                                "patterns": [r"on\s+(\w+)"],
                            },
                        },
                    },
                }
            }
        }
        router._build_indexes()

        result = router.route("action deploy on production")
        params = result.params
        # Should extract both action_type and target
        assert "action_type" in params or "target" in params


class TestConfidenceScoring:
    """Tests for confidence scoring."""

    def test_exact_match_highest_confidence(self, router_with_circuits):
        """Test that exact matches have highest confidence."""
        result = router_with_circuits.route("status")
        assert result.confidence == 1.0
        assert result.reason == "exact"

    def test_exact_prefix_slightly_lower(self, router_with_circuits):
        """Test that exact prefix match has slightly lower confidence."""
        result = router_with_circuits.route("status verbose output")
        # First match is exact prefix which is 0.95
        assert result.confidence == 0.95
        assert result.reason == "exact_prefix"

    def test_semantic_match_lower_confidence(self, router_with_circuits):
        """Test that semantic matches have lower confidence than exact."""
        result = router_with_circuits.route("implement new feature")
        assert result.confidence < 1.0
        assert result.confidence >= 0.7
        assert result.reason == "semantic"

    def test_fallback_lowest_confidence(self, router_with_circuits):
        """Test that fallback has lowest confidence."""
        result = router_with_circuits.route("totally unrelated")
        assert result.confidence == 0.3
        assert result.is_fallback is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
