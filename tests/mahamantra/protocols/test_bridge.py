"""
TESTS: _bridge.py - The Bridge Protocol
========================================

REAL TESTS for:
1. BridgeType, BridgeDirection, BridgeState enums
2. BridgeEndpoint dataclass
3. BridgeSpec dataclass
4. Bridge class
5. BridgeRegistry class
6. BridgeBuilder class
"""

import pytest
from vibe_core.mahamantra.protocols._bridge import (
    # Enums
    BridgeType,
    BridgeDirection,
    BridgeState,
    # Dataclasses
    BridgeEndpoint,
    BridgeSpec,
    Bridge,
    # Registry
    BridgeRegistry,
    get_bridge_registry,
    # Builder
    BridgeBuilder,
    # Protocol
    BridgeProtocolDef,
)
from vibe_core.mahamantra.protocols._core import Level, Quarter


# =============================================================================
# BridgeType Enum Tests
# =============================================================================


class TestBridgeType:
    """Test BridgeType enum."""

    def test_bridge_type_level(self):
        """BridgeType has LEVEL."""
        assert BridgeType.LEVEL.value == "level"

    def test_bridge_type_quarter(self):
        """BridgeType has QUARTER."""
        assert BridgeType.QUARTER.value == "quarter"

    def test_bridge_type_protocol(self):
        """BridgeType has PROTOCOL."""
        assert BridgeType.PROTOCOL.value == "protocol"

    def test_bridge_type_system(self):
        """BridgeType has SYSTEM."""
        assert BridgeType.SYSTEM.value == "system"

    def test_bridge_type_interface(self):
        """BridgeType has INTERFACE."""
        assert BridgeType.INTERFACE.value == "interface"

    def test_bridge_type_migration(self):
        """BridgeType has MIGRATION."""
        assert BridgeType.MIGRATION.value == "migration"


# =============================================================================
# BridgeDirection Enum Tests
# =============================================================================


class TestBridgeDirection:
    """Test BridgeDirection enum."""

    def test_bridge_direction_uni(self):
        """BridgeDirection has UNIDIRECTIONAL."""
        assert BridgeDirection.UNIDIRECTIONAL.value == "uni"

    def test_bridge_direction_bi(self):
        """BridgeDirection has BIDIRECTIONAL."""
        assert BridgeDirection.BIDIRECTIONAL.value == "bi"

    def test_bridge_direction_up(self):
        """BridgeDirection has UPSTREAM."""
        assert BridgeDirection.UPSTREAM.value == "up"

    def test_bridge_direction_down(self):
        """BridgeDirection has DOWNSTREAM."""
        assert BridgeDirection.DOWNSTREAM.value == "down"


# =============================================================================
# BridgeState Enum Tests
# =============================================================================


class TestBridgeState:
    """Test BridgeState enum."""

    def test_bridge_state_blueprint(self):
        """BridgeState has BLUEPRINT."""
        assert BridgeState.BLUEPRINT.value == "blueprint"

    def test_bridge_state_building(self):
        """BridgeState has BUILDING."""
        assert BridgeState.BUILDING.value == "building"

    def test_bridge_state_active(self):
        """BridgeState has ACTIVE."""
        assert BridgeState.ACTIVE.value == "active"

    def test_bridge_state_suspended(self):
        """BridgeState has SUSPENDED."""
        assert BridgeState.SUSPENDED.value == "suspended"

    def test_bridge_state_deprecated(self):
        """BridgeState has DEPRECATED."""
        assert BridgeState.DEPRECATED.value == "deprecated"

    def test_bridge_state_destroyed(self):
        """BridgeState has DESTROYED."""
        assert BridgeState.DESTROYED.value == "destroyed"


# =============================================================================
# BridgeEndpoint Tests
# =============================================================================


class TestBridgeEndpoint:
    """Test BridgeEndpoint dataclass."""

    def test_bridge_endpoint_creation(self):
        """BridgeEndpoint can be created."""
        endpoint = BridgeEndpoint(
            name="test",
            endpoint_type="protocol",
        )
        assert endpoint.name == "test"

    def test_bridge_endpoint_from_level(self):
        """from_level creates level endpoint."""
        endpoint = BridgeEndpoint.from_level(Level.SUBSTRATE)
        assert endpoint.level == Level.SUBSTRATE
        assert endpoint.endpoint_type == "level"

    def test_bridge_endpoint_from_quarter(self):
        """from_quarter creates quarter endpoint."""
        endpoint = BridgeEndpoint.from_quarter(Quarter.GENESIS)
        assert endpoint.quarter == Quarter.GENESIS
        assert endpoint.endpoint_type == "quarter"

    def test_bridge_endpoint_from_protocol(self):
        """from_protocol creates protocol endpoint."""
        endpoint = BridgeEndpoint.from_protocol(
            "TestProto",
            Level.CONTRACT,
            Quarter.DHARMA,
        )
        assert endpoint.name == "TestProto"
        assert endpoint.level == Level.CONTRACT
        assert endpoint.quarter == Quarter.DHARMA

    def test_bridge_endpoint_from_system(self):
        """from_system creates system endpoint."""
        endpoint = BridgeEndpoint.from_system("legacy")
        assert endpoint.name == "legacy"
        assert endpoint.endpoint_type == "system"

    def test_bridge_endpoint_address(self):
        """address property returns full address."""
        endpoint = BridgeEndpoint(
            name="Test",
            endpoint_type="protocol",
            level=Level.SUBSTRATE,
            quarter=Quarter.GENESIS,
        )
        addr = endpoint.address
        assert "protocol" in addr
        assert "Test" in addr

    def test_bridge_endpoint_is_frozen(self):
        """BridgeEndpoint is frozen."""
        endpoint = BridgeEndpoint(name="test", endpoint_type="protocol")
        with pytest.raises(Exception):
            endpoint.name = "changed"


# =============================================================================
# BridgeSpec Tests
# =============================================================================


class TestBridgeSpec:
    """Test BridgeSpec dataclass."""

    def test_bridge_spec_creation(self):
        """BridgeSpec can be created."""
        source = BridgeEndpoint.from_level(Level.SUBSTRATE)
        target = BridgeEndpoint.from_level(Level.CONTRACT)
        spec = BridgeSpec(
            name="test_bridge",
            bridge_type=BridgeType.LEVEL,
            source=source,
            target=target,
        )
        assert spec.name == "test_bridge"

    def test_bridge_spec_is_level_crossing(self):
        """is_level_crossing detects level differences."""
        source = BridgeEndpoint.from_level(Level.SUBSTRATE)
        target = BridgeEndpoint.from_level(Level.CONTRACT)
        spec = BridgeSpec(
            name="test",
            bridge_type=BridgeType.LEVEL,
            source=source,
            target=target,
        )
        assert spec.is_level_crossing is True

    def test_bridge_spec_is_quarter_crossing(self):
        """is_quarter_crossing detects quarter differences."""
        source = BridgeEndpoint.from_quarter(Quarter.GENESIS)
        target = BridgeEndpoint.from_quarter(Quarter.DHARMA)
        spec = BridgeSpec(
            name="test",
            bridge_type=BridgeType.QUARTER,
            source=source,
            target=target,
        )
        assert spec.is_quarter_crossing is True

    def test_bridge_spec_full_name(self):
        """full_name includes parent."""
        source = BridgeEndpoint.from_system("A")
        target = BridgeEndpoint.from_system("B")
        spec = BridgeSpec(
            name="child",
            bridge_type=BridgeType.SYSTEM,
            source=source,
            target=target,
            parent_bridge="parent",
        )
        assert spec.full_name == "parent.child"


# =============================================================================
# Bridge Tests
# =============================================================================


class TestBridge:
    """Test Bridge class."""

    def test_bridge_creation(self):
        """Bridge can be created."""
        source = BridgeEndpoint.from_system("A")
        target = BridgeEndpoint.from_system("B")
        spec = BridgeSpec(
            name="test",
            bridge_type=BridgeType.SYSTEM,
            source=source,
            target=target,
        )
        bridge = Bridge(spec=spec)
        assert bridge.state == BridgeState.BLUEPRINT

    def test_bridge_set_transforms(self):
        """set_transforms sets transform functions."""
        source = BridgeEndpoint.from_system("A")
        target = BridgeEndpoint.from_system("B")
        spec = BridgeSpec(
            name="test",
            bridge_type=BridgeType.SYSTEM,
            source=source,
            target=target,
        )
        bridge = Bridge(spec=spec)
        bridge.set_transforms(
            to_target=lambda x: str(x),
            to_source=lambda x: int(x),
        )
        assert bridge._to_target is not None
        assert bridge._to_source is not None

    def test_bridge_activate(self):
        """activate changes state to ACTIVE."""
        source = BridgeEndpoint.from_system("A")
        target = BridgeEndpoint.from_system("B")
        spec = BridgeSpec(
            name="test",
            bridge_type=BridgeType.SYSTEM,
            source=source,
            target=target,
        )
        bridge = Bridge(spec=spec)
        bridge.set_transforms(to_target=lambda x: x)
        bridge.activate()
        assert bridge.state == BridgeState.ACTIVE

    def test_bridge_activate_no_transform_raises(self):
        """activate without transforms raises."""
        source = BridgeEndpoint.from_system("A")
        target = BridgeEndpoint.from_system("B")
        spec = BridgeSpec(
            name="test",
            bridge_type=BridgeType.SYSTEM,
            source=source,
            target=target,
        )
        bridge = Bridge(spec=spec)
        with pytest.raises(ValueError, match="no transforms"):
            bridge.activate()

    def test_bridge_cross_to_target(self):
        """cross_to_target transforms value."""
        source = BridgeEndpoint.from_system("A")
        target = BridgeEndpoint.from_system("B")
        spec = BridgeSpec(
            name="test",
            bridge_type=BridgeType.SYSTEM,
            source=source,
            target=target,
        )
        bridge = Bridge(spec=spec)
        bridge.set_transforms(to_target=lambda x: x * 2)
        bridge.activate()
        result = bridge.cross_to_target(5)
        assert result == 10

    def test_bridge_cross_not_active_raises(self):
        """cross when not active raises."""
        source = BridgeEndpoint.from_system("A")
        target = BridgeEndpoint.from_system("B")
        spec = BridgeSpec(
            name="test",
            bridge_type=BridgeType.SYSTEM,
            source=source,
            target=target,
        )
        bridge = Bridge(spec=spec)
        bridge.set_transforms(to_target=lambda x: x)
        # Not activated
        with pytest.raises(ValueError, match="not active"):
            bridge.cross_to_target(5)

    def test_bridge_suspend(self):
        """suspend changes state to SUSPENDED."""
        source = BridgeEndpoint.from_system("A")
        target = BridgeEndpoint.from_system("B")
        spec = BridgeSpec(
            name="test",
            bridge_type=BridgeType.SYSTEM,
            source=source,
            target=target,
        )
        bridge = Bridge(spec=spec)
        bridge.set_transforms(to_target=lambda x: x)
        bridge.activate()
        bridge.suspend()
        assert bridge.state == BridgeState.SUSPENDED

    def test_bridge_deprecate(self):
        """deprecate changes state to DEPRECATED."""
        source = BridgeEndpoint.from_system("A")
        target = BridgeEndpoint.from_system("B")
        spec = BridgeSpec(
            name="test",
            bridge_type=BridgeType.SYSTEM,
            source=source,
            target=target,
        )
        bridge = Bridge(spec=spec)
        bridge.deprecate()
        assert bridge.state == BridgeState.DEPRECATED

    def test_bridge_destroy(self):
        """destroy changes state and clears transforms."""
        source = BridgeEndpoint.from_system("A")
        target = BridgeEndpoint.from_system("B")
        spec = BridgeSpec(
            name="test",
            bridge_type=BridgeType.SYSTEM,
            source=source,
            target=target,
        )
        bridge = Bridge(spec=spec)
        bridge.set_transforms(to_target=lambda x: x)
        bridge.destroy()
        assert bridge.state == BridgeState.DESTROYED
        assert bridge._to_target is None

    def test_bridge_add_child(self):
        """add_child adds child bridge."""
        source = BridgeEndpoint.from_system("A")
        target = BridgeEndpoint.from_system("B")
        spec = BridgeSpec(
            name="parent",
            bridge_type=BridgeType.SYSTEM,
            source=source,
            target=target,
        )
        parent = Bridge(spec=spec)

        child_spec = BridgeSpec(
            name="child",
            bridge_type=BridgeType.PROTOCOL,
            source=source,
            target=target,
        )
        child = Bridge(spec=child_spec)
        parent.add_child(child)

        assert parent.get_child("child") is child


# =============================================================================
# BridgeRegistry Tests
# =============================================================================


class TestBridgeRegistry:
    """Test BridgeRegistry class."""

    def test_bridge_registry_singleton(self):
        """BridgeRegistry is singleton."""
        reg1 = BridgeRegistry()
        reg2 = BridgeRegistry()
        assert reg1 is reg2

    def test_bridge_registry_register(self):
        """register adds bridge."""
        reg = get_bridge_registry()
        reg.clear()  # Clean state

        source = BridgeEndpoint.from_system("A")
        target = BridgeEndpoint.from_system("B")
        spec = BridgeSpec(
            name="test_reg",
            bridge_type=BridgeType.SYSTEM,
            source=source,
            target=target,
        )
        bridge = Bridge(spec=spec)
        reg.register(bridge)

        assert reg.get("test_reg") is bridge

    def test_bridge_registry_get_by_type(self):
        """get_by_type returns bridges of type."""
        reg = get_bridge_registry()
        reg.clear()

        source = BridgeEndpoint.from_system("A")
        target = BridgeEndpoint.from_system("B")
        spec = BridgeSpec(
            name="sys_bridge",
            bridge_type=BridgeType.SYSTEM,
            source=source,
            target=target,
        )
        bridge = Bridge(spec=spec)
        reg.register(bridge)

        sys_bridges = reg.get_by_type(BridgeType.SYSTEM)
        assert len(sys_bridges) >= 1

    def test_bridge_registry_get_active(self):
        """get_active returns active bridges."""
        reg = get_bridge_registry()
        reg.clear()

        source = BridgeEndpoint.from_system("A")
        target = BridgeEndpoint.from_system("B")
        spec = BridgeSpec(
            name="active_bridge",
            bridge_type=BridgeType.SYSTEM,
            source=source,
            target=target,
        )
        bridge = Bridge(spec=spec)
        bridge.set_transforms(to_target=lambda x: x)
        bridge.activate()
        reg.register(bridge)

        active = reg.get_active()
        assert bridge in active


# =============================================================================
# BridgeBuilder Tests
# =============================================================================


class TestBridgeBuilder:
    """Test BridgeBuilder class."""

    def test_bridge_builder_basic(self):
        """Basic builder usage."""
        bridge = (
            BridgeBuilder[int, str]("test").from_system("A").to_system("B").with_transform(lambda x: str(x)).build()
        )
        assert bridge.spec.name == "test"

    def test_bridge_builder_from_level(self):
        """from_level sets source and type."""
        bridge = (
            BridgeBuilder[int, int]("level_bridge")
            .from_level(Level.SUBSTRATE)
            .to_level(Level.CONTRACT)
            .with_transform(lambda x: x)
            .build()
        )
        assert bridge.spec.bridge_type == BridgeType.LEVEL

    def test_bridge_builder_from_quarter(self):
        """from_quarter sets source and type."""
        bridge = (
            BridgeBuilder[int, int]("quarter_bridge")
            .from_quarter(Quarter.GENESIS)
            .to_quarter(Quarter.DHARMA)
            .with_transform(lambda x: x)
            .build()
        )
        assert bridge.spec.bridge_type == BridgeType.QUARTER

    def test_bridge_builder_direction(self):
        """direction sets direction."""
        bridge = (
            BridgeBuilder[int, int]("uni_bridge")
            .from_system("A")
            .to_system("B")
            .direction(BridgeDirection.UNIDIRECTIONAL)
            .with_transform(lambda x: x)
            .build()
        )
        assert bridge.spec.direction == BridgeDirection.UNIDIRECTIONAL

    def test_bridge_builder_no_source_raises(self):
        """build without source raises."""
        builder = BridgeBuilder[int, int]("invalid")
        builder.to_system("B")
        with pytest.raises(ValueError, match="source and target"):
            builder.build()


# =============================================================================
# BridgeProtocolDef Tests
# =============================================================================


class TestBridgeProtocolDef:
    """Test BridgeProtocolDef."""

    def test_bridge_protocol_validates(self):
        """BridgeProtocolDef validates."""
        valid, violations = BridgeProtocolDef.validate()
        assert valid is True

    def test_bridge_protocol_identity(self):
        """BridgeProtocolDef has correct identity."""
        identity = BridgeProtocolDef.get_identity()
        assert identity.name == "BridgeProtocol"
        assert identity.mahajana == "narada"


# =============================================================================
# Module Exports Tests
# =============================================================================


class TestModuleExports:
    """Test module exports."""

    def test_all_exports(self):
        """All expected items are in __all__."""
        from vibe_core.mahamantra.protocols import _bridge

        expected = [
            "BridgeType",
            "BridgeDirection",
            "BridgeState",
            "BridgeEndpoint",
            "BridgeSpec",
            "Bridge",
            "BridgeRegistry",
            "BridgeBuilder",
        ]
        for item in expected:
            assert item in _bridge.__all__, f"{item} should be in __all__"
