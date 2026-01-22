"""
TESTS: _core.py - The Core Protocol
====================================

REAL TESTS for:
1. Level enum
2. Quarter enum
3. ProtocolIdentity dataclass
4. ProtocolCapability dataclass
5. MahamantraProtocolBase class
6. CoreProtocol
7. Constants (PARAMPARA, etc.)
"""

import pytest
from vibe_core.mahamantra.protocols._core import (
    # Constants
    PARAMPARA,
    KSETRA_COUNT,
    MAHAJANA_COUNT,
    KSETRAJNA_COUNT,
    # Enums
    Level,
    Quarter,
    # Dataclasses
    ProtocolIdentity,
    ProtocolCapability,
    # Protocol base
    MahamantraProtocolBase,
    MahamantraProtocol,
    # Core protocol
    CoreProtocol,
)


# =============================================================================
# Constants Tests
# =============================================================================


class TestCoreConstants:
    """Test core constants."""

    def test_parampara_is_37(self):
        """PARAMPARA = 24 + 12 + 1 = 37."""
        assert PARAMPARA == 37

    def test_ksetra_count_is_24(self):
        """KSETRA_COUNT is 24 (the field/prakriti elements)."""
        assert KSETRA_COUNT == 24

    def test_mahajana_count_is_12(self):
        """MAHAJANA_COUNT is 12 (the authorities)."""
        assert MAHAJANA_COUNT == 12

    def test_ksetrajna_count_is_1(self):
        """KSETRAJNA_COUNT is 1 (Krishna)."""
        assert KSETRAJNA_COUNT == 1

    def test_parampara_formula(self):
        """PARAMPARA = KSETRA + MAHAJANA + KSETRAJNA."""
        assert PARAMPARA == KSETRA_COUNT + MAHAJANA_COUNT + KSETRAJNA_COUNT


# =============================================================================
# Level Enum Tests
# =============================================================================


class TestLevel:
    """Test Level enum."""

    def test_level_has_acintya(self):
        """Level has ACINTYA (-2)."""
        assert hasattr(Level, "ACINTYA")
        assert Level.ACINTYA.value == -2

    def test_level_has_substrate(self):
        """Level has SUBSTRATE (-1)."""
        assert hasattr(Level, "SUBSTRATE")
        assert Level.SUBSTRATE.value == -1

    def test_level_has_contract(self):
        """Level has CONTRACT (0)."""
        assert hasattr(Level, "CONTRACT")
        assert Level.CONTRACT.value == 0

    def test_level_has_router(self):
        """Level has ROUTER (1)."""
        assert hasattr(Level, "ROUTER")
        assert Level.ROUTER.value == 1

    def test_level_has_runtime(self):
        """Level has RUNTIME (2)."""
        assert hasattr(Level, "RUNTIME")
        assert Level.RUNTIME.value == 2

    def test_level_has_interface(self):
        """Level has INTERFACE (3)."""
        assert hasattr(Level, "INTERFACE")
        assert Level.INTERFACE.value == 3

    def test_level_has_governance(self):
        """Level has GOVERNANCE (4)."""
        assert hasattr(Level, "GOVERNANCE")
        assert Level.GOVERNANCE.value == 4

    def test_level_ordering(self):
        """Levels are ordered from ACINTYA to GOVERNANCE."""
        assert Level.ACINTYA.value < Level.SUBSTRATE.value
        assert Level.SUBSTRATE.value < Level.CONTRACT.value
        assert Level.CONTRACT.value < Level.ROUTER.value
        assert Level.ROUTER.value < Level.RUNTIME.value
        assert Level.RUNTIME.value < Level.INTERFACE.value
        assert Level.INTERFACE.value < Level.GOVERNANCE.value


# =============================================================================
# Quarter Enum Tests
# =============================================================================


class TestQuarter:
    """Test Quarter enum."""

    def test_quarter_has_genesis(self):
        """Quarter has GENESIS."""
        assert hasattr(Quarter, "GENESIS")
        assert Quarter.GENESIS.value == "genesis"

    def test_quarter_has_dharma(self):
        """Quarter has DHARMA."""
        assert hasattr(Quarter, "DHARMA")
        assert Quarter.DHARMA.value == "dharma"

    def test_quarter_has_karma(self):
        """Quarter has KARMA."""
        assert hasattr(Quarter, "KARMA")
        assert Quarter.KARMA.value == "karma"

    def test_quarter_has_moksha(self):
        """Quarter has MOKSHA."""
        assert hasattr(Quarter, "MOKSHA")
        assert Quarter.MOKSHA.value == "moksha"

    def test_quarter_count(self):
        """There are 4 quarters."""
        assert len(Quarter) == 4

    def test_from_position_genesis(self):
        """Positions 0-3 are GENESIS."""
        for i in range(4):
            assert Quarter.from_position(i) == Quarter.GENESIS

    def test_from_position_dharma(self):
        """Positions 4-7 are DHARMA."""
        for i in range(4, 8):
            assert Quarter.from_position(i) == Quarter.DHARMA

    def test_from_position_karma(self):
        """Positions 8-11 are KARMA."""
        for i in range(8, 12):
            assert Quarter.from_position(i) == Quarter.KARMA

    def test_from_position_moksha(self):
        """Positions 12-15 are MOKSHA."""
        for i in range(12, 16):
            assert Quarter.from_position(i) == Quarter.MOKSHA


# =============================================================================
# ProtocolIdentity Tests
# =============================================================================


class TestProtocolIdentity:
    """Test ProtocolIdentity dataclass."""

    def test_protocol_identity_creation(self):
        """ProtocolIdentity can be created."""
        identity = ProtocolIdentity(
            name="TestProtocol",
            mahajana="vyasa",
            position=0,
            level=Level.SUBSTRATE,
            quarter=Quarter.GENESIS,
        )
        assert identity.name == "TestProtocol"
        assert identity.mahajana == "vyasa"
        assert identity.position == 0

    def test_protocol_identity_parampara_vector(self):
        """parampara_vector is computed correctly."""
        identity = ProtocolIdentity(
            name="Test",
            mahajana="brahma",
            position=1,
            level=Level.SUBSTRATE,
            quarter=Quarter.GENESIS,
        )
        # parampara_vector = (position + 1) * PARAMPARA
        expected = (1 + 1) * PARAMPARA
        assert identity.parampara_vector == expected

    def test_protocol_identity_is_head(self):
        """is_head is True for position 0."""
        identity = ProtocolIdentity(
            name="Test",
            mahajana="vyasa",
            position=0,
            level=Level.SUBSTRATE,
            quarter=Quarter.GENESIS,
        )
        assert identity.is_head() is True

    def test_protocol_identity_is_worker(self):
        """is_worker is True for position > 0."""
        identity = ProtocolIdentity(
            name="Test",
            mahajana="brahma",
            position=1,
            level=Level.SUBSTRATE,
            quarter=Quarter.GENESIS,
        )
        assert identity.is_worker() is True

    def test_protocol_identity_is_frozen(self):
        """ProtocolIdentity is frozen (immutable)."""
        identity = ProtocolIdentity(
            name="Test",
            mahajana="vyasa",
            position=0,
            level=Level.SUBSTRATE,
            quarter=Quarter.GENESIS,
        )
        with pytest.raises(Exception):
            identity.name = "Changed"


# =============================================================================
# ProtocolCapability Tests
# =============================================================================


class TestProtocolCapability:
    """Test ProtocolCapability dataclass."""

    def test_protocol_capability_create(self):
        """ProtocolCapability.create works."""
        cap = ProtocolCapability.create(
            provides=["feature1", "feature2"],
            requires=["CoreProtocol"],
            opcodes=["SYS_WAKE"],
        )
        assert "feature1" in cap.provides
        assert "feature2" in cap.provides
        assert "CoreProtocol" in cap.requires
        assert "SYS_WAKE" in cap.opcodes

    def test_protocol_capability_provides_is_frozenset(self):
        """provides is a frozenset."""
        cap = ProtocolCapability.create(
            provides=["a", "b"],
            requires=[],
            opcodes=[],
        )
        assert isinstance(cap.provides, frozenset)

    def test_protocol_capability_requires_is_frozenset(self):
        """requires is a frozenset."""
        cap = ProtocolCapability.create(
            provides=[],
            requires=["CoreProtocol"],
            opcodes=[],
        )
        assert isinstance(cap.requires, frozenset)

    def test_protocol_capability_can_provide(self):
        """can_provide checks capability."""
        cap = ProtocolCapability.create(
            provides=["feature1"],
            requires=[],
            opcodes=[],
        )
        assert cap.can_provide("feature1") is True
        assert cap.can_provide("feature2") is False

    def test_protocol_capability_needs(self):
        """needs checks requirements."""
        cap = ProtocolCapability.create(
            provides=[],
            requires=["CoreProtocol"],
            opcodes=[],
        )
        assert cap.needs("CoreProtocol") is True
        assert cap.needs("OtherProtocol") is False


# =============================================================================
# MahamantraProtocolBase Tests
# =============================================================================


class TestMahamantraProtocolBase:
    """Test MahamantraProtocolBase class."""

    def test_core_protocol_is_mahamantra_protocol_base(self):
        """CoreProtocol inherits from MahamantraProtocolBase."""
        assert issubclass(CoreProtocol, MahamantraProtocolBase)

    def test_get_identity(self):
        """get_identity returns ProtocolIdentity."""
        identity = CoreProtocol.get_identity()
        assert isinstance(identity, ProtocolIdentity)

    def test_get_capability(self):
        """get_capability returns ProtocolCapability."""
        capability = CoreProtocol.get_capability()
        assert isinstance(capability, ProtocolCapability)

    def test_validate_returns_tuple(self):
        """validate returns (bool, list)."""
        valid, violations = CoreProtocol.validate()
        assert isinstance(valid, bool)
        assert isinstance(violations, list)

    def test_core_protocol_validates(self):
        """CoreProtocol validates successfully."""
        valid, violations = CoreProtocol.validate()
        assert valid is True
        assert len(violations) == 0


# =============================================================================
# CoreProtocol Tests
# =============================================================================


class TestCoreProtocol:
    """Test CoreProtocol."""

    def test_core_protocol_identity_name(self):
        """CoreProtocol has correct name."""
        identity = CoreProtocol.get_identity()
        assert identity.name == "CoreProtocol"

    def test_core_protocol_identity_mahajana(self):
        """CoreProtocol has correct mahajana."""
        identity = CoreProtocol.get_identity()
        assert identity.mahajana == "prithu"

    def test_core_protocol_identity_position(self):
        """CoreProtocol has position 0."""
        identity = CoreProtocol.get_identity()
        assert identity.position == 0

    def test_core_protocol_identity_level(self):
        """CoreProtocol is at ACINTYA level."""
        identity = CoreProtocol.get_identity()
        assert identity.level == Level.ACINTYA

    def test_core_protocol_identity_quarter(self):
        """CoreProtocol is in GENESIS quarter."""
        identity = CoreProtocol.get_identity()
        assert identity.quarter == Quarter.GENESIS

    def test_core_protocol_is_head(self):
        """CoreProtocol is head (position 0)."""
        identity = CoreProtocol.get_identity()
        assert identity.is_head() is True

    def test_core_protocol_provides_basics(self):
        """CoreProtocol provides core capabilities."""
        cap = CoreProtocol.get_capability()
        assert "holographic_reflection" in cap.provides
        assert "validation" in cap.provides
        assert "capability_management" in cap.provides
        assert "protocol_definition" in cap.provides
        assert "fractal_growth" in cap.provides
        assert "identity_management" in cap.provides


# =============================================================================
# Module Exports Tests
# =============================================================================


class TestModuleExports:
    """Test module exports."""

    def test_all_exports(self):
        """All expected items are in __all__."""
        from vibe_core.mahamantra.protocols import _core
        expected = [
            "Level",
            "Quarter",
            "ProtocolIdentity",
            "ProtocolCapability",
            "MahamantraProtocol",
            "MahamantraProtocolBase",
            "CoreProtocol",
        ]
        for item in expected:
            assert item in _core.__all__, f"{item} should be in __all__"
