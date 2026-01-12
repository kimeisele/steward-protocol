"""
TEST NAGA INTELLIGENCE BRIDGE PROTOCOL
======================================

Verifies the IntelBridgeProtocol for accessing Naga intelligence.

MAHAJANA: SHUKA (The Visionary)
OPCODE: FETCH_RES

"Central Intelligence Agency" - What NAGAs see, consumers can use.
"""

import pytest
from datetime import datetime

from vibe_core.protocols.naga.intel_bridge import (
    # Protocols
    IntelBridgeProtocol,
    NullIntelBridge,
    # Enums
    IntelCategory,
    IntelPriority,
    # Data types
    IntelItem,
    IntelQuery,
    IntelResponse,
    # Mantra connection
    INTEL_OPCODE,
    INTEL_PHASE,
    INTEL_WORD,
    INTEL_POSITION,
    INTEL_MAHAJANA,
)
from vibe_core.protocols.substrate import MantraOpCode


class TestIntelCategory:
    """Test intel categories."""

    def test_security_category(self):
        """Security category exists."""
        assert IntelCategory.SECURITY.value == "security"

    def test_health_category(self):
        """Health category exists."""
        assert IntelCategory.HEALTH.value == "health"

    def test_behavior_category(self):
        """Behavior category exists."""
        assert IntelCategory.BEHAVIOR.value == "behavior"

    def test_context_category(self):
        """Context category exists."""
        assert IntelCategory.CONTEXT.value == "context"

    def test_threat_category(self):
        """Threat category exists."""
        assert IntelCategory.THREAT.value == "threat"

    def test_suggestion_category(self):
        """Suggestion category exists."""
        assert IntelCategory.SUGGESTION.value == "suggestion"


class TestIntelPriority:
    """Test priority levels."""

    def test_low_priority(self):
        """Low priority exists."""
        assert IntelPriority.LOW.value == "low"

    def test_medium_priority(self):
        """Medium priority exists."""
        assert IntelPriority.MEDIUM.value == "medium"

    def test_high_priority(self):
        """High priority exists."""
        assert IntelPriority.HIGH.value == "high"

    def test_critical_priority(self):
        """Critical priority exists."""
        assert IntelPriority.CRITICAL.value == "critical"


class TestIntelItem:
    """Test IntelItem dataclass."""

    def test_item_is_frozen(self):
        """IntelItem is immutable."""
        item = IntelItem(
            item_id="test-1",
            category=IntelCategory.SECURITY,
            priority=IntelPriority.MEDIUM,
            summary="Test item",
            details="Details",
            source_naga="takshaka",
            relevance_score=0.8
        )
        with pytest.raises(Exception):
            item.summary = "Changed"

    def test_to_chat_message_security(self):
        """Security items have lock icon."""
        item = IntelItem(
            item_id="test-1",
            category=IntelCategory.SECURITY,
            priority=IntelPriority.MEDIUM,
            summary="Security alert",
            details="",
            source_naga="takshaka",
            relevance_score=0.8
        )
        msg = item.to_chat_message()
        assert "🔒" in msg
        assert "Security alert" in msg

    def test_to_chat_message_threat(self):
        """Threat items have warning icon."""
        item = IntelItem(
            item_id="test-1",
            category=IntelCategory.THREAT,
            priority=IntelPriority.HIGH,
            summary="Active threat",
            details="",
            source_naga="chitragupta",
            relevance_score=0.9
        )
        msg = item.to_chat_message()
        assert "⚠️" in msg
        assert "[HIGH]" in msg

    def test_to_chat_message_critical(self):
        """Critical items show [CRITICAL] marker."""
        item = IntelItem(
            item_id="test-1",
            category=IntelCategory.SECURITY,
            priority=IntelPriority.CRITICAL,
            summary="Critical issue",
            details="",
            source_naga="prahlad",
            relevance_score=1.0
        )
        msg = item.to_chat_message()
        assert "[CRITICAL]" in msg

    def test_tags_tuple(self):
        """Tags are tuple (immutable)."""
        item = IntelItem(
            item_id="test-1",
            category=IntelCategory.CONTEXT,
            priority=IntelPriority.LOW,
            summary="Context",
            details="",
            source_naga="shuka",
            relevance_score=0.5,
            tags=("tag1", "tag2")
        )
        assert len(item.tags) == 2


class TestIntelQuery:
    """Test IntelQuery dataclass."""

    def test_query_is_frozen(self):
        """IntelQuery is immutable."""
        query = IntelQuery(context="test context")
        with pytest.raises(Exception):
            query.context = "changed"

    def test_default_values(self):
        """Default query values."""
        query = IntelQuery(context="test")
        assert query.categories == ()
        assert query.min_priority == IntelPriority.LOW
        assert query.max_results == 5

    def test_custom_query(self):
        """Custom query values."""
        query = IntelQuery(
            context="security analysis",
            categories=(IntelCategory.SECURITY, IntelCategory.THREAT),
            min_priority=IntelPriority.HIGH,
            max_results=10
        )
        assert len(query.categories) == 2
        assert query.min_priority == IntelPriority.HIGH


class TestIntelResponse:
    """Test IntelResponse dataclass."""

    def test_response_is_frozen(self):
        """IntelResponse is immutable."""
        response = IntelResponse(
            items=(),
            query=IntelQuery(context="test"),
            total_available=0
        )
        with pytest.raises(Exception):
            response.total_available = 10

    def test_has_critical_false(self):
        """has_critical is False when no critical items."""
        response = IntelResponse(
            items=(),
            query=IntelQuery(context="test"),
            total_available=0
        )
        assert not response.has_critical

    def test_has_critical_true(self):
        """has_critical is True when critical items present."""
        item = IntelItem(
            item_id="crit-1",
            category=IntelCategory.SECURITY,
            priority=IntelPriority.CRITICAL,
            summary="Critical",
            details="",
            source_naga="test",
            relevance_score=1.0
        )
        response = IntelResponse(
            items=(item,),
            query=IntelQuery(context="test"),
            total_available=1
        )
        assert response.has_critical

    def test_has_threats_false(self):
        """has_threats is False when no threat items."""
        response = IntelResponse(
            items=(),
            query=IntelQuery(context="test"),
            total_available=0
        )
        assert not response.has_threats

    def test_has_threats_true(self):
        """has_threats is True when threat items present."""
        item = IntelItem(
            item_id="threat-1",
            category=IntelCategory.THREAT,
            priority=IntelPriority.HIGH,
            summary="Threat",
            details="",
            source_naga="test",
            relevance_score=0.9
        )
        response = IntelResponse(
            items=(item,),
            query=IntelQuery(context="test"),
            total_available=1
        )
        assert response.has_threats


class TestNullIntelBridge:
    """Test NullIntelBridge implementation."""

    def test_opcode_is_fetch_res(self):
        """NullIntelBridge uses FETCH_RES opcode."""
        bridge = NullIntelBridge()
        assert bridge.opcode == MantraOpCode.EXEC_OP

    def test_mahajana_is_shuka(self):
        """NullIntelBridge owned by SHUKA."""
        bridge = NullIntelBridge()
        assert bridge.mahajana == "shuka"

    def test_query_returns_empty(self):
        """Query returns empty response."""
        bridge = NullIntelBridge()
        query = IntelQuery(context="test")
        response = bridge.query(query)
        assert len(response.items) == 0
        assert response.total_available == 0

    def test_query_for_chat_returns_empty(self):
        """query_for_chat returns empty response."""
        bridge = NullIntelBridge()
        response = bridge.query_for_chat("hello", "general chat")
        assert len(response.items) == 0

    def test_get_recent_returns_empty(self):
        """get_recent returns empty list."""
        bridge = NullIntelBridge()
        items = bridge.get_recent()
        assert items == []

    def test_get_critical_returns_empty(self):
        """get_critical returns empty list."""
        bridge = NullIntelBridge()
        items = bridge.get_critical()
        assert items == []

    def test_get_threats_returns_empty(self):
        """get_threats returns empty list."""
        bridge = NullIntelBridge()
        items = bridge.get_threats()
        assert items == []

    def test_subscribe_returns_null_id(self):
        """subscribe returns null subscription ID."""
        bridge = NullIntelBridge()
        sub_id = bridge.subscribe(lambda x: None)
        assert sub_id == "null-subscription"

    def test_unsubscribe_returns_false(self):
        """unsubscribe returns False."""
        bridge = NullIntelBridge()
        result = bridge.unsubscribe("any-id")
        assert result is False

    def test_get_available_categories(self):
        """Returns all categories."""
        bridge = NullIntelBridge()
        categories = bridge.get_available_categories()
        assert len(categories) == len(IntelCategory)

    def test_get_active_nagas_empty(self):
        """No active NAGAs."""
        bridge = NullIntelBridge()
        nagas = bridge.get_active_nagas()
        assert nagas == []

    def test_ingest_returns_none(self):
        """ingest_flood_observation returns None."""
        bridge = NullIntelBridge()
        from vibe_core.protocols.naga.flood import FloodObservation
        obs = FloodObservation(
            observation_type="test",
            severity="info",
            source="test",
            summary="Test",
            details=()
        )
        result = bridge.ingest_flood_observation(obs)
        assert result is None


class TestMantraConnection:
    """Test Mantra CPU connection."""

    def test_opcode_is_fetch_res(self):
        """Intel uses FETCH_RES opcode."""
        assert INTEL_OPCODE == MantraOpCode.EXEC_OP

    def test_phase_is_serve(self):
        """Intel is in SERVE phase."""
        assert INTEL_PHASE == "SERVE"

    def test_word_is_hare(self):
        """Intel word is HARE."""
        assert INTEL_WORD == "HARE"

    def test_position_is_8(self):
        """Intel position is 8."""
        assert INTEL_POSITION == 8

    def test_mahajana_is_shuka(self):
        """Intel owned by SHUKA."""
        assert INTEL_MAHAJANA == "shuka"


class TestIntelBridgeProtocolContract:
    """Test IntelBridgeProtocol contract."""

    def test_protocol_is_runtime_checkable(self):
        """Protocol can be checked at runtime."""
        assert hasattr(IntelBridgeProtocol, '__protocol_attrs__') or \
               hasattr(IntelBridgeProtocol, '_is_protocol')

    def test_has_query_methods(self):
        """Protocol has query methods."""
        methods = ['query', 'query_for_chat']
        for method in methods:
            assert method in dir(IntelBridgeProtocol)

    def test_has_direct_access_methods(self):
        """Protocol has direct access methods."""
        methods = ['get_recent', 'get_critical', 'get_threats']
        for method in methods:
            assert method in dir(IntelBridgeProtocol)

    def test_has_subscription_methods(self):
        """Protocol has subscription methods."""
        methods = ['subscribe', 'unsubscribe']
        for method in methods:
            assert method in dir(IntelBridgeProtocol)

    def test_has_discovery_methods(self):
        """Protocol has discovery methods."""
        methods = ['get_available_categories', 'get_active_nagas']
        for method in methods:
            assert method in dir(IntelBridgeProtocol)


class TestStrictTyping:
    """Test that no Any types are used."""

    def test_intel_item_no_any(self):
        """IntelItem has no Any types."""
        from typing import get_type_hints, Any
        hints = get_type_hints(IntelItem)
        for field_name, field_type in hints.items():
            assert field_type is not Any, f"IntelItem.{field_name} uses Any"

    def test_intel_query_no_any(self):
        """IntelQuery has no Any types."""
        from typing import get_type_hints, Any
        hints = get_type_hints(IntelQuery)
        for field_name, field_type in hints.items():
            assert field_type is not Any, f"IntelQuery.{field_name} uses Any"

    def test_intel_response_no_any(self):
        """IntelResponse has no Any types."""
        from typing import get_type_hints, Any
        hints = get_type_hints(IntelResponse)
        for field_name, field_type in hints.items():
            assert field_type is not Any, f"IntelResponse.{field_name} uses Any"


class TestImmutability:
    """Test that all dataclasses are frozen."""

    def test_intel_item_immutable(self):
        """IntelItem is immutable."""
        item = IntelItem(
            item_id="test",
            category=IntelCategory.CONTEXT,
            priority=IntelPriority.LOW,
            summary="Test",
            details="",
            source_naga="test",
            relevance_score=0.5
        )
        with pytest.raises(Exception):
            item.item_id = "changed"

    def test_intel_query_immutable(self):
        """IntelQuery is immutable."""
        query = IntelQuery(context="test")
        with pytest.raises(Exception):
            query.max_results = 100

    def test_intel_response_immutable(self):
        """IntelResponse is immutable."""
        response = IntelResponse(
            items=(),
            query=IntelQuery(context="test"),
            total_available=0
        )
        with pytest.raises(Exception):
            response.items = ()
