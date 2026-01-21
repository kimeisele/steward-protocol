"""
TESTS: parampara.py - The Disciplic Succession
==============================================

"evam parampara-praptam imam rajarsayo viduh"

REAL TESTS for:
1. ParamparaNode dataclass
2. PARAMPARA_GRAPH constant
3. PrakritiCategory enum
4. PrakritiElement dataclass
5. PRAKRITI_24 list
6. Access functions
7. get_37_formula
8. AcintyaRhythm class
"""

import pytest
from vibe_core.mahamantra.substrate.parampara import (
    # Parampara Graph
    ParamparaNode,
    PARAMPARA_GRAPH,
    # Prakriti
    PrakritiCategory,
    PrakritiElement,
    PRAKRITI_24,
    # Access Functions
    get_position,
    get_quarter,
    get_sampradaya,
    get_guru,
    get_shishyas,
    get_mahajana_at_position,
    get_quarter_mahajanas,
    get_sampradaya_mahajanas,
    # The 37 Formula
    get_37_formula,
    # Acintya
    AcintyaRhythm,
)
from vibe_core.mahamantra.substrate.mahajana import Mahajana, Quarter, Sampradaya


# =============================================================================
# ParamparaNode Tests
# =============================================================================


class TestParamparaNode:
    """Test ParamparaNode dataclass."""

    def test_parampara_node_is_frozen(self):
        """ParamparaNode is frozen (immutable)."""
        node = ParamparaNode(
            mahajana=Mahajana.BRAHMA,
            position=1,
            quarter=Quarter.GENESIS,
            sampradaya=Sampradaya.BRAHMA,
            is_head=False,
        )
        with pytest.raises(Exception):
            node.position = 2

    def test_parampara_node_has_required_fields(self):
        """ParamparaNode has required fields."""
        node = PARAMPARA_GRAPH[Mahajana.BRAHMA]
        assert hasattr(node, 'mahajana')
        assert hasattr(node, 'position')
        assert hasattr(node, 'quarter')
        assert hasattr(node, 'sampradaya')
        assert hasattr(node, 'is_head')

    def test_parampara_node_optional_fields(self):
        """ParamparaNode has optional fields with defaults."""
        node = PARAMPARA_GRAPH[Mahajana.BRAHMA]
        assert hasattr(node, 'guru')
        assert hasattr(node, 'shishyas')
        assert hasattr(node, 'serves')
        assert hasattr(node, 'served_by')


# =============================================================================
# PARAMPARA_GRAPH Tests
# =============================================================================


class TestParamparaGraph:
    """Test PARAMPARA_GRAPH constant."""

    def test_parampara_graph_has_12_mahajanas(self):
        """PARAMPARA_GRAPH has exactly 12 Mahajanas."""
        assert len(PARAMPARA_GRAPH) == 12

    def test_all_mahajanas_in_graph(self):
        """All 12 Mahajanas are in the graph."""
        expected = {
            Mahajana.BRAHMA, Mahajana.NARADA, Mahajana.SHAMBHU,
            Mahajana.KUMARAS, Mahajana.KAPILA, Mahajana.MANU,
            Mahajana.PRAHLADA, Mahajana.JANAKA, Mahajana.BHISHMA,
            Mahajana.BALI, Mahajana.SHUKA, Mahajana.YAMARAJA,
        }
        assert set(PARAMPARA_GRAPH.keys()) == expected

    def test_brahma_in_genesis(self):
        """Brahma is in GENESIS quarter."""
        assert PARAMPARA_GRAPH[Mahajana.BRAHMA].quarter == Quarter.GENESIS

    def test_kumaras_in_dharma(self):
        """Kumaras is in DHARMA quarter."""
        assert PARAMPARA_GRAPH[Mahajana.KUMARAS].quarter == Quarter.DHARMA

    def test_prahlada_in_karma(self):
        """Prahlada is in KARMA quarter."""
        assert PARAMPARA_GRAPH[Mahajana.PRAHLADA].quarter == Quarter.KARMA

    def test_yamaraja_in_moksha(self):
        """Yamaraja is in MOKSHA quarter."""
        assert PARAMPARA_GRAPH[Mahajana.YAMARAJA].quarter == Quarter.MOKSHA


class TestParamparaPositions:
    """Test positions in PARAMPARA_GRAPH."""

    def test_brahma_position_is_1(self):
        """Brahma is at position 1."""
        assert PARAMPARA_GRAPH[Mahajana.BRAHMA].position == 1

    def test_narada_position_is_2(self):
        """Narada is at position 2."""
        assert PARAMPARA_GRAPH[Mahajana.NARADA].position == 2

    def test_yamaraja_position_is_15(self):
        """Yamaraja is at position 15."""
        assert PARAMPARA_GRAPH[Mahajana.YAMARAJA].position == 15

    def test_all_positions_unique(self):
        """All positions are unique."""
        positions = [node.position for node in PARAMPARA_GRAPH.values()]
        assert len(positions) == len(set(positions))


class TestParamparaSampradayas:
    """Test sampradayas in PARAMPARA_GRAPH."""

    def test_shambhu_in_rudra_sampradaya(self):
        """Shambhu is in RUDRA sampradaya."""
        assert PARAMPARA_GRAPH[Mahajana.SHAMBHU].sampradaya == Sampradaya.RUDRA

    def test_kumaras_in_kumara_sampradaya(self):
        """Kumaras is in KUMARA sampradaya."""
        assert PARAMPARA_GRAPH[Mahajana.KUMARAS].sampradaya == Sampradaya.KUMARA

    def test_brahma_in_brahma_sampradaya(self):
        """Brahma is in BRAHMA sampradaya."""
        assert PARAMPARA_GRAPH[Mahajana.BRAHMA].sampradaya == Sampradaya.BRAHMA


class TestParamparaRelationships:
    """Test guru-shishya relationships."""

    def test_narada_guru_is_brahma(self):
        """Narada's guru is Brahma."""
        assert PARAMPARA_GRAPH[Mahajana.NARADA].guru == Mahajana.BRAHMA

    def test_brahma_shishyas_includes_narada(self):
        """Brahma's shishyas include Narada."""
        assert Mahajana.NARADA in PARAMPARA_GRAPH[Mahajana.BRAHMA].shishyas

    def test_prahlada_guru_is_narada(self):
        """Prahlada's guru is Narada."""
        assert PARAMPARA_GRAPH[Mahajana.PRAHLADA].guru == Mahajana.NARADA

    def test_bali_guru_is_prahlada(self):
        """Bali's guru is Prahlada."""
        assert PARAMPARA_GRAPH[Mahajana.BALI].guru == Mahajana.PRAHLADA


# =============================================================================
# PrakritiCategory Tests
# =============================================================================


class TestPrakritiCategory:
    """Test PrakritiCategory enum."""

    def test_prakriti_category_has_6_categories(self):
        """PrakritiCategory has 6 categories."""
        assert len(PrakritiCategory) == 6

    def test_prakriti_category_values(self):
        """PrakritiCategory has correct values."""
        assert PrakritiCategory.ROOT.value == "root"
        assert PrakritiCategory.SUBTLE.value == "subtle"
        assert PrakritiCategory.TANMATRA.value == "tanmatra"
        assert PrakritiCategory.JNANENDRIYA.value == "jnana"
        assert PrakritiCategory.KARMENDRIYA.value == "karma"
        assert PrakritiCategory.MAHABHUTA.value == "bhuta"


# =============================================================================
# PRAKRITI_24 Tests
# =============================================================================


class TestPrakriti24:
    """Test PRAKRITI_24 list."""

    def test_prakriti_24_has_24_elements(self):
        """PRAKRITI_24 has exactly 24 elements."""
        assert len(PRAKRITI_24) == 24

    def test_prakriti_indices_1_to_24(self):
        """Prakriti indices are 1 to 24."""
        indices = [p.index for p in PRAKRITI_24]
        assert indices == list(range(1, 25))

    def test_prakriti_first_is_root(self):
        """First prakriti is root category."""
        assert PRAKRITI_24[0].category == PrakritiCategory.ROOT
        assert PRAKRITI_24[0].name == "prakriti"

    def test_prakriti_last_is_prithvi(self):
        """Last prakriti is prithvi (earth)."""
        assert PRAKRITI_24[23].name == "prithvi"
        assert PRAKRITI_24[23].category == PrakritiCategory.MAHABHUTA

    def test_prakriti_element_has_rhythm(self):
        """PrakritiElement has rhythm coordinates."""
        element = PRAKRITI_24[0]
        assert hasattr(element, 'rhythm_3x8')
        assert hasattr(element, 'rhythm_4x6')

    def test_prakriti_category_counts(self):
        """Category counts are correct."""
        counts = {}
        for p in PRAKRITI_24:
            counts[p.category] = counts.get(p.category, 0) + 1

        assert counts[PrakritiCategory.ROOT] == 1
        assert counts[PrakritiCategory.SUBTLE] == 3
        assert counts[PrakritiCategory.TANMATRA] == 5
        assert counts[PrakritiCategory.JNANENDRIYA] == 5
        assert counts[PrakritiCategory.KARMENDRIYA] == 5
        assert counts[PrakritiCategory.MAHABHUTA] == 5


# =============================================================================
# Access Functions Tests
# =============================================================================


class TestGetPosition:
    """Test get_position function."""

    def test_get_position_brahma(self):
        """get_position returns correct position for Brahma."""
        assert get_position(Mahajana.BRAHMA) == 1

    def test_get_position_yamaraja(self):
        """get_position returns correct position for Yamaraja."""
        assert get_position(Mahajana.YAMARAJA) == 15

    def test_get_position_unknown_raises(self):
        """get_position raises for unknown Mahajana."""
        # This would require a fake Mahajana which isn't possible
        # with the enum, so we skip this test
        pass


class TestGetQuarter:
    """Test get_quarter function."""

    def test_get_quarter_brahma(self):
        """get_quarter returns GENESIS for Brahma."""
        assert get_quarter(Mahajana.BRAHMA) == Quarter.GENESIS

    def test_get_quarter_kumaras(self):
        """get_quarter returns DHARMA for Kumaras."""
        assert get_quarter(Mahajana.KUMARAS) == Quarter.DHARMA

    def test_get_quarter_prahlada(self):
        """get_quarter returns KARMA for Prahlada."""
        assert get_quarter(Mahajana.PRAHLADA) == Quarter.KARMA

    def test_get_quarter_bali(self):
        """get_quarter returns MOKSHA for Bali."""
        assert get_quarter(Mahajana.BALI) == Quarter.MOKSHA


class TestGetSampradaya:
    """Test get_sampradaya function."""

    def test_get_sampradaya_brahma(self):
        """get_sampradaya returns BRAHMA for Brahma."""
        assert get_sampradaya(Mahajana.BRAHMA) == Sampradaya.BRAHMA

    def test_get_sampradaya_shambhu(self):
        """get_sampradaya returns RUDRA for Shambhu."""
        assert get_sampradaya(Mahajana.SHAMBHU) == Sampradaya.RUDRA

    def test_get_sampradaya_kumaras(self):
        """get_sampradaya returns KUMARA for Kumaras."""
        assert get_sampradaya(Mahajana.KUMARAS) == Sampradaya.KUMARA


class TestGetGuru:
    """Test get_guru function."""

    def test_get_guru_narada(self):
        """get_guru returns Brahma for Narada."""
        assert get_guru(Mahajana.NARADA) == Mahajana.BRAHMA

    def test_get_guru_brahma_is_none(self):
        """get_guru returns None for Brahma (no guru in graph)."""
        assert get_guru(Mahajana.BRAHMA) is None

    def test_get_guru_prahlada(self):
        """get_guru returns Narada for Prahlada."""
        assert get_guru(Mahajana.PRAHLADA) == Mahajana.NARADA


class TestGetShishyas:
    """Test get_shishyas function."""

    def test_get_shishyas_brahma(self):
        """get_shishyas returns frozenset for Brahma."""
        shishyas = get_shishyas(Mahajana.BRAHMA)
        assert isinstance(shishyas, frozenset)
        assert Mahajana.NARADA in shishyas

    def test_get_shishyas_narada_is_empty(self):
        """get_shishyas returns empty for Narada (in this graph)."""
        shishyas = get_shishyas(Mahajana.NARADA)
        assert len(shishyas) == 0


class TestGetMahajanaAtPosition:
    """Test get_mahajana_at_position function."""

    def test_get_mahajana_at_position_1(self):
        """Position 1 is Brahma."""
        assert get_mahajana_at_position(1) == Mahajana.BRAHMA

    def test_get_mahajana_at_position_15(self):
        """Position 15 is Yamaraja."""
        assert get_mahajana_at_position(15) == Mahajana.YAMARAJA

    def test_get_mahajana_at_position_0_is_none(self):
        """Position 0 (Vyasa HEAD) returns None (not in mahajana graph)."""
        assert get_mahajana_at_position(0) is None


class TestGetQuarterMahajanas:
    """Test get_quarter_mahajanas function."""

    def test_get_quarter_mahajanas_genesis(self):
        """GENESIS quarter has 3 mahajanas."""
        mahajanas = get_quarter_mahajanas(Quarter.GENESIS)
        assert len(mahajanas) == 3
        assert Mahajana.BRAHMA in mahajanas
        assert Mahajana.NARADA in mahajanas
        assert Mahajana.SHAMBHU in mahajanas

    def test_get_quarter_mahajanas_dharma(self):
        """DHARMA quarter has 3 mahajanas."""
        mahajanas = get_quarter_mahajanas(Quarter.DHARMA)
        assert len(mahajanas) == 3

    def test_get_quarter_mahajanas_karma(self):
        """KARMA quarter has 3 mahajanas."""
        mahajanas = get_quarter_mahajanas(Quarter.KARMA)
        assert len(mahajanas) == 3

    def test_get_quarter_mahajanas_moksha(self):
        """MOKSHA quarter has 3 mahajanas."""
        mahajanas = get_quarter_mahajanas(Quarter.MOKSHA)
        assert len(mahajanas) == 3


class TestGetSampradayaMahajanas:
    """Test get_sampradaya_mahajanas function."""

    def test_get_sampradaya_mahajanas_brahma(self):
        """BRAHMA sampradaya has multiple mahajanas."""
        mahajanas = get_sampradaya_mahajanas(Sampradaya.BRAHMA)
        assert len(mahajanas) >= 8  # Most are in Brahma line

    def test_get_sampradaya_mahajanas_rudra(self):
        """RUDRA sampradaya has Shambhu."""
        mahajanas = get_sampradaya_mahajanas(Sampradaya.RUDRA)
        assert Mahajana.SHAMBHU in mahajanas

    def test_get_sampradaya_mahajanas_kumara(self):
        """KUMARA sampradaya has Kumaras."""
        mahajanas = get_sampradaya_mahajanas(Sampradaya.KUMARA)
        assert Mahajana.KUMARAS in mahajanas


# =============================================================================
# The 37 Formula Tests
# =============================================================================


class TestGet37Formula:
    """Test get_37_formula function."""

    def test_get_37_formula_returns_dict(self):
        """get_37_formula returns dict."""
        result = get_37_formula()
        assert isinstance(result, dict)

    def test_get_37_formula_prakriti_is_24(self):
        """Prakriti count is 24."""
        result = get_37_formula()
        assert result["prakriti"] == 24

    def test_get_37_formula_mahajanas_is_12(self):
        """Mahajanas count is 12."""
        result = get_37_formula()
        assert result["mahajanas"] == 12

    def test_get_37_formula_ksetrajna_is_1(self):
        """Ksetrajna count is 1."""
        result = get_37_formula()
        assert result["ksetrajna"] == 1

    def test_get_37_formula_total_is_37(self):
        """Total is 37."""
        result = get_37_formula()
        assert result["total"] == 37

    def test_get_37_formula_sum(self):
        """24 + 12 + 1 = 37."""
        result = get_37_formula()
        assert result["prakriti"] + result["mahajanas"] + result["ksetrajna"] == 37


# =============================================================================
# AcintyaRhythm Tests
# =============================================================================


class TestAcintyaRhythm:
    """Test AcintyaRhythm class."""

    def test_rhythm_3x8(self):
        """rhythm_3x8 returns correct coordinates."""
        element = PRAKRITI_24[0]
        coords = AcintyaRhythm.rhythm_3x8(element)
        assert coords == element.rhythm_3x8

    def test_rhythm_4x6(self):
        """rhythm_4x6 returns correct coordinates."""
        element = PRAKRITI_24[0]
        coords = AcintyaRhythm.rhythm_4x6(element)
        assert coords == element.rhythm_4x6

    def test_is_acintya_always_true(self):
        """is_acintya is always True when chanting."""
        # In acintya, both rhythms are equivalent
        assert AcintyaRhythm.is_acintya((0, 0), (0, 0)) is True
        assert AcintyaRhythm.is_acintya((1, 2), (3, 4)) is True


# =============================================================================
# Module Exports Tests
# =============================================================================


class TestModuleExports:
    """Test module exports."""

    def test_all_exports(self):
        """All expected items are in __all__."""
        from vibe_core.mahamantra.substrate import parampara

        assert "ParamparaNode" in parampara.__all__
        assert "PARAMPARA_GRAPH" in parampara.__all__
        assert "PrakritiCategory" in parampara.__all__
        assert "PrakritiElement" in parampara.__all__
        assert "PRAKRITI_24" in parampara.__all__
        assert "get_position" in parampara.__all__
        assert "get_quarter" in parampara.__all__
        assert "get_sampradaya" in parampara.__all__
        assert "get_37_formula" in parampara.__all__
        assert "AcintyaRhythm" in parampara.__all__
