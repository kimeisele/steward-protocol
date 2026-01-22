"""
TESTS: _declaration.py - The Declaration Protocol
==================================================

REAL TESTS for:
1. DeclarationType enum
2. MahajanaCard dataclass
3. ModuleDeclaration dataclass
4. DeclarationRegistry class
5. DeclarationProtocol
"""

import pytest
from vibe_core.mahamantra.protocols._declaration import (
    # Types
    DeclarationType,
    # Card
    MahajanaCard,
    # Module Declaration
    ModuleDeclaration,
    # Registry
    DeclarationRegistry,
    # Protocol
    DeclarationProtocol,
    # Helper
    read_declaration,
)
from vibe_core.mahamantra.protocols._core import Level, Quarter, PARAMPARA


# =============================================================================
# DeclarationType Enum Tests
# =============================================================================


class TestDeclarationType:
    """Test DeclarationType enum."""

    def test_declaration_type_module(self):
        """DeclarationType has MODULE."""
        assert DeclarationType.MODULE.value == "module"

    def test_declaration_type_class(self):
        """DeclarationType has CLASS."""
        assert DeclarationType.CLASS.value == "class"

    def test_declaration_type_protocol(self):
        """DeclarationType has PROTOCOL."""
        assert DeclarationType.PROTOCOL.value == "protocol"

    def test_declaration_type_service(self):
        """DeclarationType has SERVICE."""
        assert DeclarationType.SERVICE.value == "service"

    def test_declaration_type_type(self):
        """DeclarationType has TYPE."""
        assert DeclarationType.TYPE.value == "type"

    def test_declaration_type_function(self):
        """DeclarationType has FUNCTION."""
        assert DeclarationType.FUNCTION.value == "function"

    def test_declaration_type_constant(self):
        """DeclarationType has CONSTANT."""
        assert DeclarationType.CONSTANT.value == "constant"


# =============================================================================
# MahajanaCard Tests
# =============================================================================


class TestMahajanaCard:
    """Test MahajanaCard dataclass."""

    def test_mahajana_card_creation(self):
        """MahajanaCard can be created."""
        card = MahajanaCard(
            name="test",
            mahajana="brahma",
            position=1,
            declaration_type=DeclarationType.MODULE,
        )
        assert card.name == "test"
        assert card.mahajana == "brahma"
        assert card.position == 1

    def test_mahajana_card_quarter_derived(self):
        """Quarter is derived from position."""
        card = MahajanaCard(
            name="test",
            mahajana="brahma",
            position=0,
            declaration_type=DeclarationType.MODULE,
        )
        assert card.quarter == Quarter.GENESIS

    def test_mahajana_card_parampara_vector(self):
        """parampara_vector is computed correctly."""
        card = MahajanaCard(
            name="test",
            mahajana="brahma",
            position=1,
            declaration_type=DeclarationType.MODULE,
        )
        expected = (1 + 1) * PARAMPARA
        assert card.parampara_vector == expected

    def test_mahajana_card_full_name(self):
        """full_name is computed correctly."""
        card = MahajanaCard(
            name="test",
            mahajana="brahma",
            position=1,
            declaration_type=DeclarationType.MODULE,
        )
        assert card.full_name == "brahma.test"

    def test_mahajana_card_invalid_position(self):
        """Invalid position raises ValueError."""
        with pytest.raises(ValueError):
            MahajanaCard(
                name="test",
                mahajana="brahma",
                position=20,  # Invalid - must be 0-15
                declaration_type=DeclarationType.MODULE,
            )

    def test_mahajana_card_create_factory(self):
        """MahajanaCard.create factory method works."""
        card = MahajanaCard.create(
            name="test",
            mahajana="brahma",
            position=1,
            provides=["feature1", "feature2"],
            requires=["CoreProtocol"],
        )
        assert "feature1" in card.provides
        assert "feature2" in card.provides
        assert "CoreProtocol" in card.requires

    def test_mahajana_card_is_head(self):
        """is_head returns True for position divisible by 4."""
        card = MahajanaCard.create(name="test", mahajana="brahma", position=0)
        assert card.is_head() is True

        card4 = MahajanaCard.create(name="test", mahajana="brahma", position=4)
        assert card4.is_head() is True

    def test_mahajana_card_is_worker(self):
        """is_worker returns True for non-head positions."""
        card = MahajanaCard.create(name="test", mahajana="brahma", position=1)
        assert card.is_worker() is True

    def test_mahajana_card_can_provide(self):
        """can_provide checks capabilities."""
        card = MahajanaCard.create(
            name="test",
            mahajana="brahma",
            position=1,
            provides=["feature1"],
        )
        assert card.can_provide("feature1") is True
        assert card.can_provide("feature2") is False

    def test_mahajana_card_needs(self):
        """needs checks requirements."""
        card = MahajanaCard.create(
            name="test",
            mahajana="brahma",
            position=1,
            requires=["CoreProtocol"],
        )
        assert card.needs("CoreProtocol") is True
        assert card.needs("OtherProtocol") is False

    def test_mahajana_card_to_dict(self):
        """to_dict serializes correctly."""
        card = MahajanaCard.create(
            name="test",
            mahajana="brahma",
            position=1,
            provides=["feature1"],
        )
        data = card.to_dict()
        assert data["name"] == "test"
        assert data["mahajana"] == "brahma"
        assert data["position"] == 1

    def test_mahajana_card_from_dict(self):
        """from_dict deserializes correctly."""
        data = {
            "name": "test",
            "mahajana": "brahma",
            "position": 1,
            "provides": ["feature1"],
        }
        card = MahajanaCard.from_dict(data)
        assert card.name == "test"
        assert card.mahajana == "brahma"

    def test_mahajana_card_is_frozen(self):
        """MahajanaCard is frozen."""
        card = MahajanaCard.create(name="test", mahajana="brahma", position=1)
        with pytest.raises(Exception):
            card.name = "changed"


# =============================================================================
# DeclarationRegistry Tests
# =============================================================================


class TestDeclarationRegistry:
    """Test DeclarationRegistry class."""

    def test_declaration_registry_singleton(self):
        """DeclarationRegistry is singleton."""
        reg1 = DeclarationRegistry()
        reg2 = DeclarationRegistry()
        assert reg1 is reg2

    def test_declaration_registry_register(self):
        """register adds card to registry."""
        registry = DeclarationRegistry()
        registry.clear()  # Clean state

        card = MahajanaCard.create(
            name="test_reg",
            mahajana="brahma",
            position=1,
            provides=["test_feature"],
        )
        registry.register(card)
        assert registry.get("brahma.test_reg") is card

    def test_declaration_registry_get_by_mahajana(self):
        """get_by_mahajana returns cards for mahajana."""
        registry = DeclarationRegistry()
        registry.clear()

        card = MahajanaCard.create(name="test", mahajana="narada", position=1)
        registry.register(card)

        cards = registry.get_by_mahajana("narada")
        assert len(cards) >= 1
        assert card in cards

    def test_declaration_registry_get_by_position(self):
        """get_by_position returns cards at position."""
        registry = DeclarationRegistry()
        registry.clear()

        card = MahajanaCard.create(name="test", mahajana="brahma", position=2)
        registry.register(card)

        cards = registry.get_by_position(2)
        assert card in cards

    def test_declaration_registry_get_by_capability(self):
        """get_by_capability returns cards with capability."""
        registry = DeclarationRegistry()
        registry.clear()

        card = MahajanaCard.create(
            name="test",
            mahajana="brahma",
            position=1,
            provides=["unique_capability"],
        )
        registry.register(card)

        cards = registry.get_by_capability("unique_capability")
        assert card in cards

    def test_declaration_registry_find_provider(self):
        """find_provider finds card that provides capability."""
        registry = DeclarationRegistry()
        registry.clear()

        card = MahajanaCard.create(
            name="test",
            mahajana="brahma",
            position=1,
            provides=["special_provider"],
        )
        registry.register(card)

        provider = registry.find_provider("special_provider")
        assert provider is card

    def test_declaration_registry_clear(self):
        """clear empties the registry."""
        registry = DeclarationRegistry()
        card = MahajanaCard.create(name="test", mahajana="brahma", position=1)
        registry.register(card)
        registry.clear()
        assert len(registry.all_cards()) == 0


# =============================================================================
# DeclarationProtocol Tests
# =============================================================================


class TestDeclarationProtocol:
    """Test DeclarationProtocol."""

    def test_declaration_protocol_validates(self):
        """DeclarationProtocol validates."""
        valid, violations = DeclarationProtocol.validate()
        assert valid is True

    def test_declaration_protocol_identity(self):
        """DeclarationProtocol has correct identity."""
        identity = DeclarationProtocol.get_identity()
        assert identity.name == "DeclarationProtocol"
        assert identity.mahajana == "brahma"

    def test_declaration_protocol_provides(self):
        """DeclarationProtocol provides declaration capabilities."""
        cap = DeclarationProtocol.get_capability()
        assert "declaration_format" in cap.provides
        assert "mahajana_card" in cap.provides
        assert "declaration_registry" in cap.provides


# =============================================================================
# Module Exports Tests
# =============================================================================


class TestModuleExports:
    """Test module exports."""

    def test_all_exports(self):
        """All expected items are in __all__."""
        from vibe_core.mahamantra.protocols import _declaration
        expected = [
            "DeclarationType",
            "MahajanaCard",
            "ModuleDeclaration",
            "DeclarationRegistry",
            "DeclarationProtocol",
            "read_declaration",
        ]
        for item in expected:
            assert item in _declaration.__all__, f"{item} should be in __all__"
