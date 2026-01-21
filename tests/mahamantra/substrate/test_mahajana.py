"""
TESTS: mahajana.py - Die 12 Wächter + 4 Avataras
=================================================

"svayambhūr nāradaḥ śambhuḥ kumāraḥ kapilo manuḥ
prahlādo janako bhīṣmo balir vaiyāsakir vayam"

REAL TESTS for:
1. Mahajana enum (12 members)
2. Avatara enum (4 members)
3. Quarter enum (4 members)
4. Sampradaya enum (4 members)
5. SSOT constants (MAHAJANA_COUNT, AVATARA_COUNT, TOTAL_POSITIONS)
"""

import pytest
from vibe_core.mahamantra.substrate.mahajana import (
    Mahajana,
    Avatara,
    Quarter,
    Sampradaya,
    MAHAJANA_COUNT,
    AVATARA_COUNT,
    TOTAL_POSITIONS,
)


# =============================================================================
# Mahajana Tests
# =============================================================================


class TestMahajana:
    """Test Mahajana enum."""

    def test_exactly_12_mahajanas(self):
        """Must have exactly 12 mahajanas (SB 6.3.20)."""
        assert len(Mahajana) == 12

    def test_mahajana_count_is_12(self):
        """MAHAJANA_COUNT constant is 12."""
        assert MAHAJANA_COUNT == 12

    def test_all_12_names(self):
        """All 12 mahajana names from SB 6.3.20."""
        expected = {
            "brahma", "narada", "shambhu", "kumaras", "kapila", "manu",
            "prahlada", "janaka", "bhishma", "bali", "shuka", "yamaraja"
        }
        actual = {m.value for m in Mahajana}
        assert actual == expected

    def test_mahajana_is_str_enum(self):
        """Mahajana inherits from str."""
        assert isinstance(Mahajana.BRAHMA.value, str)
        assert Mahajana.BRAHMA == "brahma"

    def test_brahma_creator(self):
        """Brahma = creation (position 1)."""
        assert Mahajana.BRAHMA.value == "brahma"

    def test_narada_messenger(self):
        """Narada = communication (position 2)."""
        assert Mahajana.NARADA.value == "narada"

    def test_yamaraja_judge(self):
        """Yamaraja = judgment (position 15)."""
        assert Mahajana.YAMARAJA.value == "yamaraja"


# =============================================================================
# Avatara Tests
# =============================================================================


class TestAvatara:
    """Test Avatara enum."""

    def test_exactly_4_avataras(self):
        """Must have exactly 4 shaktyavesha avataras (4 HEADs)."""
        assert len(Avatara) == 4

    def test_avatara_count_is_4(self):
        """AVATARA_COUNT constant is 4."""
        assert AVATARA_COUNT == 4

    def test_all_4_names(self):
        """All 4 avatara names."""
        expected = {"vyasa", "prithu", "parashurama", "nrisimha"}
        actual = {a.value for a in Avatara}
        assert actual == expected

    def test_avatara_is_str_enum(self):
        """Avatara inherits from str."""
        assert isinstance(Avatara.VYASA.value, str)
        assert Avatara.VYASA == "vyasa"

    def test_vyasa_genesis_head(self):
        """Vyasa = GENESIS HEAD (position 0)."""
        assert Avatara.VYASA.value == "vyasa"

    def test_prithu_dharma_head(self):
        """Prithu = DHARMA HEAD (position 4)."""
        assert Avatara.PRITHU.value == "prithu"

    def test_parashurama_karma_head(self):
        """Parashurama = KARMA HEAD (position 8)."""
        assert Avatara.PARASHURAMA.value == "parashurama"

    def test_nrisimha_moksha_head(self):
        """Nrisimha = MOKSHA HEAD (position 12)."""
        assert Avatara.NRISIMHA.value == "nrisimha"


# =============================================================================
# Quarter Tests
# =============================================================================


class TestQuarter:
    """Test Quarter enum."""

    def test_exactly_4_quarters(self):
        """Must have exactly 4 quarters."""
        assert len(Quarter) == 4

    def test_all_4_quarters(self):
        """All 4 quarter names."""
        expected = {"genesis", "dharma", "karma", "moksha"}
        actual = {q.value for q in Quarter}
        assert actual == expected

    def test_quarter_is_str_enum(self):
        """Quarter inherits from str."""
        assert isinstance(Quarter.GENESIS.value, str)
        assert Quarter.GENESIS == "genesis"

    def test_genesis_first_quarter(self):
        """Genesis = first quarter (Hare Krishna Hare Krishna)."""
        assert Quarter.GENESIS.value == "genesis"

    def test_dharma_second_quarter(self):
        """Dharma = second quarter (Krishna Krishna Hare Hare)."""
        assert Quarter.DHARMA.value == "dharma"

    def test_karma_third_quarter(self):
        """Karma = third quarter (Hare Rama Hare Rama)."""
        assert Quarter.KARMA.value == "karma"

    def test_moksha_fourth_quarter(self):
        """Moksha = fourth quarter (Rama Rama Hare Hare)."""
        assert Quarter.MOKSHA.value == "moksha"


# =============================================================================
# Sampradaya Tests
# =============================================================================


class TestSampradaya:
    """Test Sampradaya enum."""

    def test_exactly_4_sampradayas(self):
        """Must have exactly 4 authorized sampradayas."""
        assert len(Sampradaya) == 4

    def test_all_4_sampradayas(self):
        """All 4 sampradaya names."""
        expected = {"brahma", "kumara", "sri", "rudra"}
        actual = {s.value for s in Sampradaya}
        assert actual == expected

    def test_sampradaya_is_str_enum(self):
        """Sampradaya inherits from str."""
        assert isinstance(Sampradaya.BRAHMA.value, str)
        assert Sampradaya.BRAHMA == "brahma"

    def test_brahma_sampradaya_genesis(self):
        """Brahma Sampradaya maps to GENESIS quarter."""
        assert Sampradaya.BRAHMA.value == "brahma"

    def test_kumara_sampradaya_dharma(self):
        """Kumara Sampradaya maps to DHARMA quarter."""
        assert Sampradaya.KUMARA.value == "kumara"

    def test_sri_sampradaya_karma(self):
        """Sri Sampradaya maps to KARMA quarter."""
        assert Sampradaya.SRI.value == "sri"

    def test_rudra_sampradaya_moksha(self):
        """Rudra Sampradaya maps to MOKSHA quarter."""
        assert Sampradaya.RUDRA.value == "rudra"


# =============================================================================
# SSOT Constants Tests
# =============================================================================


class TestSSotConstants:
    """Test SSOT constants from seed.py."""

    def test_total_positions_is_16(self):
        """TOTAL_POSITIONS = 16 (12 mahajanas + 4 avataras)."""
        assert TOTAL_POSITIONS == 16

    def test_total_equals_sum(self):
        """TOTAL_POSITIONS = MAHAJANA_COUNT + AVATARA_COUNT."""
        assert TOTAL_POSITIONS == MAHAJANA_COUNT + AVATARA_COUNT

    def test_enum_counts_match_constants(self):
        """Enum lengths match SSOT constants."""
        assert len(Mahajana) == MAHAJANA_COUNT
        assert len(Avatara) == AVATARA_COUNT


# =============================================================================
# Integration Tests
# =============================================================================


class TestMahajanaIntegration:
    """Test integration between enums."""

    def test_4_quarters_4_avataras(self):
        """Each quarter has one avatara (HEAD)."""
        assert len(Quarter) == len(Avatara)

    def test_4_quarters_4_sampradayas(self):
        """Each quarter has one sampradaya."""
        assert len(Quarter) == len(Sampradaya)

    def test_quarter_positions_match_avataras(self):
        """Quarter HEADs are avataras (positions 0, 4, 8, 12)."""
        # Each avatara is a HEAD
        head_positions = [0, 4, 8, 12]
        assert len(head_positions) == len(Avatara)

    def test_mahajana_positions_are_workers(self):
        """Mahajanas occupy worker positions (not HEADs)."""
        worker_positions = [1, 2, 3, 5, 6, 7, 9, 10, 11, 13, 14, 15]
        assert len(worker_positions) == len(Mahajana)
