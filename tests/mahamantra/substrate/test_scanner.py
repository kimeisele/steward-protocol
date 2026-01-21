"""
TESTS: scanner.py - Mahajana Declaration Scanner
=================================================

"vedaham samatitani vartamanani carjuna"
"O Arjuna, I know everything that has happened in the past..."
— Bhagavad Gita 7.26

REAL TESTS for:
1. MahajanaAlias - name/position/alias mapping
2. resolve_mahajana - multi-language resolution
3. SimpleDeclaration - basic declaration parsing
4. MahajanaScanner - file scanning (limited, no filesystem mocks)
"""

import pytest
from vibe_core.mahamantra.substrate.scanner import (
    MahajanaAlias,
    MAHAJANA_ALIASES,
    resolve_mahajana,
    get_position,
    get_name,
    SimpleDeclaration,
    MahajanaScanner,
    get_scanner,
)
from pathlib import Path


# =============================================================================
# MahajanaAlias Tests
# =============================================================================


class TestMahajanaAlias:
    """Test MahajanaAlias dataclass."""

    def test_alias_is_frozen(self):
        """MahajanaAlias is immutable (frozen=True)."""
        alias = MAHAJANA_ALIASES[0]  # vyasa
        with pytest.raises(AttributeError):
            alias.name = "changed"

    def test_all_names_includes_primary(self):
        """all_names includes primary name and all aliases."""
        vyasa = MAHAJANA_ALIASES[0]
        assert "vyasa" in vyasa.all_names
        assert "boot" in vyasa.all_names
        assert "system" in vyasa.all_names


class TestMahajanaAliasesSSot:
    """Test MAHAJANA_ALIASES tuple is correct SSOT."""

    def test_exactly_16_aliases(self):
        """Must have exactly 16 mahajana aliases."""
        assert len(MAHAJANA_ALIASES) == 16

    def test_positions_0_to_15(self):
        """Positions are 0-15 in order."""
        for i, alias in enumerate(MAHAJANA_ALIASES):
            assert alias.position == i, f"Position mismatch at index {i}"

    def test_genesis_quarter_positions_0_3(self):
        """Genesis quarter: positions 0-3."""
        genesis = [MAHAJANA_ALIASES[i].name for i in range(0, 4)]
        assert genesis == ["vyasa", "brahma", "narada", "shambhu"]

    def test_dharma_quarter_positions_4_7(self):
        """Dharma quarter: positions 4-7."""
        dharma = [MAHAJANA_ALIASES[i].name for i in range(4, 8)]
        assert dharma == ["prithu", "kumaras", "kapila", "manu"]

    def test_karma_quarter_positions_8_11(self):
        """Karma quarter: positions 8-11."""
        karma = [MAHAJANA_ALIASES[i].name for i in range(8, 12)]
        assert karma == ["parashurama", "prahlada", "janaka", "bhishma"]

    def test_moksha_quarter_positions_12_15(self):
        """Moksha quarter: positions 12-15."""
        moksha = [MAHAJANA_ALIASES[i].name for i in range(12, 16)]
        assert moksha == ["nrisimha", "bali", "shuka", "yamaraja"]

    def test_head_positions_have_avataras(self):
        """Head positions (0, 4, 8, 12) are Avataras."""
        heads = [0, 4, 8, 12]
        head_names = [MAHAJANA_ALIASES[i].name for i in heads]
        assert head_names == ["vyasa", "prithu", "parashurama", "nrisimha"]


# =============================================================================
# resolve_mahajana Tests
# =============================================================================


class TestResolveMahajana:
    """Test resolve_mahajana function."""

    def test_resolve_by_position_int(self):
        """Resolve by integer position."""
        alias = resolve_mahajana(0)
        assert alias.name == "vyasa"
        assert alias.position == 0

    def test_resolve_by_position_str(self):
        """Resolve by string position."""
        alias = resolve_mahajana("1")
        assert alias.name == "brahma"
        assert alias.position == 1

    def test_resolve_by_sanskrit_name(self):
        """Resolve by Sanskrit name."""
        alias = resolve_mahajana("narada")
        assert alias.position == 2

    def test_resolve_by_english_alias(self):
        """Resolve by English alias."""
        alias = resolve_mahajana("messenger")
        assert alias.name == "narada"
        assert alias.position == 2

    def test_resolve_by_german_alias(self):
        """Resolve by German alias."""
        alias = resolve_mahajana("schöpfer")
        assert alias.name == "brahma"
        assert alias.position == 1

    def test_resolve_case_insensitive(self):
        """Resolution is case-insensitive."""
        assert resolve_mahajana("BRAHMA").position == 1
        assert resolve_mahajana("Brahma").position == 1
        assert resolve_mahajana("brahma").position == 1

    def test_resolve_invalid_position_raises(self):
        """Invalid position raises ValueError."""
        with pytest.raises(ValueError):
            resolve_mahajana(16)
        with pytest.raises(ValueError):
            resolve_mahajana(-1)
        with pytest.raises(ValueError):
            resolve_mahajana(100)

    def test_resolve_unknown_name_raises(self):
        """Unknown name raises ValueError."""
        with pytest.raises(ValueError):
            resolve_mahajana("nonexistent")


class TestGetPosition:
    """Test get_position convenience function."""

    def test_get_position_from_name(self):
        """Get position from name."""
        assert get_position("vyasa") == 0
        assert get_position("brahma") == 1
        assert get_position("yamaraja") == 15

    def test_get_position_from_alias(self):
        """Get position from alias."""
        assert get_position("boot") == 0
        assert get_position("creator") == 1
        assert get_position("judge") == 15


class TestGetName:
    """Test get_name convenience function."""

    def test_get_name_from_position(self):
        """Get name from position."""
        assert get_name(0) == "vyasa"
        assert get_name(1) == "brahma"
        assert get_name(15) == "yamaraja"

    def test_get_name_from_alias(self):
        """Get name from alias."""
        assert get_name("boot") == "vyasa"
        assert get_name("messenger") == "narada"


# =============================================================================
# SimpleDeclaration Tests
# =============================================================================


class TestSimpleDeclaration:
    """Test SimpleDeclaration dataclass."""

    def test_valid_with_mahajana(self):
        """Declaration with mahajana is valid."""
        decl = SimpleDeclaration(
            file_path=Path("/test/file.py"),
            module_path="test.file",
            mahajana="brahma",
        )
        assert decl.is_valid
        assert decl.resolve_position() == 1

    def test_valid_with_position(self):
        """Declaration with position is valid."""
        decl = SimpleDeclaration(
            file_path=Path("/test/file.py"),
            module_path="test.file",
            position=5,
        )
        assert decl.is_valid
        assert decl.resolve_position() == 5

    def test_invalid_without_both(self):
        """Declaration without mahajana or position is invalid."""
        decl = SimpleDeclaration(
            file_path=Path("/test/file.py"),
            module_path="test.file",
        )
        assert not decl.is_valid

    def test_position_takes_precedence(self):
        """Position takes precedence over mahajana."""
        decl = SimpleDeclaration(
            file_path=Path("/test/file.py"),
            module_path="test.file",
            mahajana="brahma",  # position 1
            position=5,  # explicit position
        )
        assert decl.resolve_position() == 5

    def test_resolve_position_raises_without_data(self):
        """resolve_position raises ValueError when no data."""
        decl = SimpleDeclaration(
            file_path=Path("/test/file.py"),
            module_path="test.file",
        )
        with pytest.raises(ValueError):
            decl.resolve_position()


# =============================================================================
# MahajanaScanner Tests (Limited - no heavy filesystem)
# =============================================================================


class TestMahajanaScanner:
    """Test MahajanaScanner class."""

    def test_scanner_instantiation(self):
        """Scanner can be instantiated."""
        scanner = MahajanaScanner()
        assert scanner is not None

    def test_scanner_has_config(self):
        """Scanner has default config."""
        scanner = MahajanaScanner()
        config = scanner.get_config()
        assert config is not None
        assert isinstance(config, dict)

    def test_get_scanner_singleton(self):
        """get_scanner returns scanner instance."""
        scanner = get_scanner()
        assert isinstance(scanner, MahajanaScanner)


class TestScannerAliasIntegrity:
    """Test that scanner aliases align with seed.py."""

    def test_vyasa_is_boot_position(self):
        """Vyasa (position 0) has 'boot' alias."""
        alias = resolve_mahajana("boot")
        assert alias.name == "vyasa"
        assert alias.position == 0

    def test_brahma_is_creator_position(self):
        """Brahma (position 1) has 'creator' alias."""
        alias = resolve_mahajana("creator")
        assert alias.name == "brahma"
        assert alias.position == 1

    def test_narada_is_messenger_position(self):
        """Narada (position 2) has 'messenger' alias."""
        alias = resolve_mahajana("messenger")
        assert alias.name == "narada"
        assert alias.position == 2

    def test_kapila_is_analyst_position(self):
        """Kapila (position 6) has 'analyst' alias."""
        alias = resolve_mahajana("analyst")
        assert alias.name == "kapila"
        assert alias.position == 6

    def test_parashurama_is_execute_position(self):
        """Parashurama (position 8) has 'execute' alias."""
        alias = resolve_mahajana("execute")
        assert alias.name == "parashurama"
        assert alias.position == 8

    def test_bhishma_is_commit_position(self):
        """Bhishma (position 11) has 'commit' alias."""
        alias = resolve_mahajana("commit")
        assert alias.name == "bhishma"
        assert alias.position == 11

    def test_yamaraja_is_judge_position(self):
        """Yamaraja (position 15) has 'judge' alias."""
        alias = resolve_mahajana("judge")
        assert alias.name == "yamaraja"
        assert alias.position == 15


class TestAllAliasesResolvable:
    """Test that all defined aliases can be resolved."""

    def test_all_primary_names_resolvable(self):
        """All primary names are resolvable."""
        for alias in MAHAJANA_ALIASES:
            resolved = resolve_mahajana(alias.name)
            assert resolved.position == alias.position

    def test_all_aliases_resolvable(self):
        """All secondary aliases are resolvable."""
        for alias in MAHAJANA_ALIASES:
            for name in alias.aliases:
                resolved = resolve_mahajana(name)
                assert resolved.position == alias.position, f"Alias '{name}' resolved to wrong position"

    def test_all_positions_resolvable(self):
        """All positions 0-15 are resolvable."""
        for pos in range(16):
            resolved = resolve_mahajana(pos)
            assert resolved.position == pos


class TestQuarterMapping:
    """Test that quarters map correctly."""

    def test_genesis_quarter_all_resolvable(self):
        """Genesis quarter aliases (create, communicate, etc.) resolve correctly."""
        # Brahma = create
        assert get_position("create") == 1
        # Narada = communicate
        assert get_position("communicate") == 2
        # Shambhu = cleanup
        assert get_position("cleanup") == 3

    def test_dharma_quarter_all_resolvable(self):
        """Dharma quarter aliases resolve correctly."""
        # Prithu = scan
        assert get_position("scan") == 4
        # Kumaras = knowledge
        assert get_position("knowledge") == 5
        # Kapila = analyze
        assert get_position("analyze") == 6
        # Manu = rules
        assert get_position("rules") == 7

    def test_karma_quarter_all_resolvable(self):
        """Karma quarter aliases resolve correctly."""
        # Parashurama = execute
        assert get_position("execute") == 8
        # Prahlada = serve
        assert get_position("serve") == 9
        # Janaka = duty
        assert get_position("duty") == 10
        # Bhishma = commit
        assert get_position("commit") == 11

    def test_moksha_quarter_all_resolvable(self):
        """Moksha quarter aliases resolve correctly."""
        # Nrisimha = guard
        assert get_position("guard") == 12
        # Bali = yield
        assert get_position("yield") == 13
        # Shuka = vision
        assert get_position("vision") == 14
        # Yamaraja = audit
        assert get_position("audit") == 15
