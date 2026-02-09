"""
TESTS: seed.py - Das Ursubstrat (THE MAHA ALGORITHM)
=====================================================

"bījaṁ māṁ sarva-bhūtānāṁ viddhi pārtha sanātanam"

REAL TESTS for:
1. HolyName enum
2. MAHAMANTRA tuple
3. All derived constants (WORDS, TRINITY, QUARTERS, etc.)
4. SharanagatiLimb, NavaBhakti, Quarter, DharmaPillar enums
5. Lotus routing functions
"""

import pytest
from vibe_core.mahamantra.substrate.seed import (
    # The Source
    KRISHNA_IS,
    MAHAMANTRA,
    HolyName,
    # Primary Derivations
    WORDS,
    TRINITY,
    HARE_COUNT,
    KRISHNA_COUNT,
    RAMA_COUNT,
    HALVES,
    HALF_SIZE,
    # Pancha (5)
    MAHAMANTRA_PAIRS,
    UNIQUE_PAIRS,
    PANCHA,
    PANCHA_PAIR_NAMES,
    # Quarters (4)
    Quarter,
    QUARTERS,
    QUARTER_NAMES,
    WORDS_PER_QUARTER,
    # Sharanagati (6)
    SharanagatiLimb,
    SHARANAGATI,
    # Nava (9)
    NavaBhakti,
    NAVA,
    # Gita Chapters (18)
    GITA_CHAPTERS,
    # Kshetra (24)
    KSHETRA,
    KSETRAJNA,
    # Parampara (37)
    PARAMPARA,
    MAHAJANA_COUNT,
    # Guardians (16)
    AVATAR_COUNT,
    AVATARAS,
    AVATARS,
    MAHAJANAS,
    ALL_GUARDIANS,
    MAHAJANA_TO_POSITION,
    POSITION_TO_MAHAJANA,
    # Lila (48)
    LILA,
    NAVADVIPA,
    PURI,
    # Dharma (4)
    DharmaPillar,
    DHARMA_PILLARS,
    KALI_YUGA_LEG,
    # Qualities (64)
    QUALITIES,
    HIDDEN_RESERVE,
    AKSARA_COUNT,
    # Mala (108)
    MALA,
    ROUNDS,
    DAILY_MANTRAS,
    # Jiva (50)
    JIVA_CYCLE,
    JIVA_QUALITIES,
    # Prana (Timing)
    SECONDS_PER_DAY,
    PRANA_DURATION_S,
    PRANA_DURATION_MS,
    TICK_INTERVAL_MS,
    # Cosmic Frame
    COSMIC_FRAME,
    # Acoustic Constitution
    ACOUSTIC_RATIO,
    END_CORRECTION,
    VENU_FREQ,
    VAMSI_FREQ,
    MURALI_FREQ,
    CUTOFF_CONSTANT,
    # Three Flutes
    VENU_HOLES,
    VAMSI_HOLES,
    MURALI_HOLES,
    FLUTE_HOLES_SUM,
    FLUTE_HOLES_PRODUCT,
    # Harmonic Resonances
    NADI_RESONANCE,
    FIELD_RESONANCE,
    # Lotus Functions
    get_quarter,
    get_quarter_name,
    get_positions_in_quarter,
    get_word_at,
    get_pair_at,
    verify_parampara,
    get_mahajana_position,
    get_position_mahajana,
    get_guardian_quarter,
    lotus_declaration,
    verify_lotus,
)


# =============================================================================
# The Source Tests
# =============================================================================


class TestKrishnaIs:
    """Test KRISHNA_IS constant."""

    def test_krishna_is_always_true(self):
        """KRISHNA_IS is always True."""
        assert KRISHNA_IS is True


class TestHolyNameEnum:
    """Test HolyName IntEnum."""

    def test_hare_is_0(self):
        """HARE = 0 (Shakti/Energy)."""
        assert HolyName.HARE.value == 0

    def test_krishna_is_1(self):
        """KRISHNA = 1 (Source/Identity)."""
        assert HolyName.KRISHNA.value == 1

    def test_rama_is_2(self):
        """RAMA = 2 (Ananda/Stability)."""
        assert HolyName.RAMA.value == 2

    def test_exactly_4_enum_members(self):
        """3 Holy Names + VOID (Maya) for binary encoding = 4 members."""
        assert len(HolyName) == 4


class TestMahamantra:
    """Test MAHAMANTRA tuple."""

    def test_mahamantra_has_16_words(self):
        """MAHAMANTRA has exactly 16 words."""
        assert len(MAHAMANTRA) == 16

    def test_first_word_is_hare(self):
        """First word is HARE."""
        assert MAHAMANTRA[0] == HolyName.HARE

    def test_second_word_is_krishna(self):
        """Second word is KRISHNA."""
        assert MAHAMANTRA[1] == HolyName.KRISHNA

    def test_first_quarter_pattern(self):
        """First quarter: Hare Krishna Hare Krishna."""
        assert MAHAMANTRA[0:4] == (
            HolyName.HARE, HolyName.KRISHNA, HolyName.HARE, HolyName.KRISHNA
        )

    def test_second_quarter_pattern(self):
        """Second quarter: Krishna Krishna Hare Hare."""
        assert MAHAMANTRA[4:8] == (
            HolyName.KRISHNA, HolyName.KRISHNA, HolyName.HARE, HolyName.HARE
        )

    def test_third_quarter_pattern(self):
        """Third quarter: Hare Rama Hare Rama."""
        assert MAHAMANTRA[8:12] == (
            HolyName.HARE, HolyName.RAMA, HolyName.HARE, HolyName.RAMA
        )

    def test_fourth_quarter_pattern(self):
        """Fourth quarter: Rama Rama Hare Hare."""
        assert MAHAMANTRA[12:16] == (
            HolyName.RAMA, HolyName.RAMA, HolyName.HARE, HolyName.HARE
        )


# =============================================================================
# Primary Derivations Tests
# =============================================================================


class TestPrimaryDerivations:
    """Test primary derived constants."""

    def test_words_is_16(self):
        """WORDS = 16."""
        assert WORDS == 16
        assert WORDS == len(MAHAMANTRA)

    def test_trinity_is_3(self):
        """TRINITY = 3 (number of unique names)."""
        assert TRINITY == 3
        assert TRINITY == len(set(MAHAMANTRA))

    def test_hare_count_is_8(self):
        """HARE_COUNT = 8."""
        assert HARE_COUNT == 8
        assert HARE_COUNT == sum(1 for w in MAHAMANTRA if w == HolyName.HARE)

    def test_krishna_count_is_4(self):
        """KRISHNA_COUNT = 4."""
        assert KRISHNA_COUNT == 4
        assert KRISHNA_COUNT == sum(1 for w in MAHAMANTRA if w == HolyName.KRISHNA)

    def test_rama_count_is_4(self):
        """RAMA_COUNT = 4."""
        assert RAMA_COUNT == 4
        assert RAMA_COUNT == sum(1 for w in MAHAMANTRA if w == HolyName.RAMA)

    def test_counts_sum_to_16(self):
        """Name counts sum to 16."""
        assert HARE_COUNT + KRISHNA_COUNT + RAMA_COUNT == WORDS

    def test_halves_is_2(self):
        """HALVES = 2."""
        assert HALVES == 2

    def test_half_size_is_8(self):
        """HALF_SIZE = 8."""
        assert HALF_SIZE == 8
        assert HALF_SIZE == WORDS // HALVES


# =============================================================================
# Pancha Tests
# =============================================================================


class TestPancha:
    """Test Pancha (5 unique pairs)."""

    def test_pancha_is_5(self):
        """PANCHA = 5 unique pairs."""
        assert PANCHA == 5
        assert PANCHA == len(UNIQUE_PAIRS)

    def test_mahamantra_pairs_has_8(self):
        """MAHAMANTRA_PAIRS has 8 pairs."""
        assert len(MAHAMANTRA_PAIRS) == 8

    def test_pancha_pair_names_has_5(self):
        """PANCHA_PAIR_NAMES has 5 names."""
        assert len(PANCHA_PAIR_NAMES) == 5

    def test_unique_pairs_content(self):
        """UNIQUE_PAIRS has the 5 correct pairs."""
        expected_pairs = {
            (HolyName.HARE, HolyName.KRISHNA),
            (HolyName.HARE, HolyName.RAMA),
            (HolyName.HARE, HolyName.HARE),
            (HolyName.KRISHNA, HolyName.KRISHNA),
            (HolyName.RAMA, HolyName.RAMA),
        }
        assert UNIQUE_PAIRS == expected_pairs


# =============================================================================
# Quarter Tests
# =============================================================================


class TestQuarters:
    """Test Quarter enum and constants."""

    def test_quarters_is_4(self):
        """QUARTERS = 4."""
        assert QUARTERS == 4
        assert QUARTERS == len(Quarter)

    def test_quarter_values(self):
        """Quarter values are 0, 1, 2, 3."""
        assert Quarter.GENESIS.value == 0
        assert Quarter.DHARMA.value == 1
        assert Quarter.KARMA.value == 2
        assert Quarter.MOKSHA.value == 3

    def test_quarter_names(self):
        """QUARTER_NAMES has correct values."""
        assert QUARTER_NAMES == ("genesis", "dharma", "karma", "moksha")

    def test_words_per_quarter_is_4(self):
        """WORDS_PER_QUARTER = 4."""
        assert WORDS_PER_QUARTER == 4
        assert WORDS_PER_QUARTER == WORDS // QUARTERS


# =============================================================================
# Sharanagati Tests
# =============================================================================


class TestSharanagati:
    """Test Sharanagati (6 limbs)."""

    def test_sharanagati_is_6(self):
        """SHARANAGATI = 6."""
        assert SHARANAGATI == 6

    def test_sharanagati_limb_count(self):
        """SharanagatiLimb has 6 members."""
        assert len(SharanagatiLimb) == 6

    def test_sharanagati_limb_names(self):
        """SharanagatiLimb has correct names."""
        assert SharanagatiLimb.ANUKULYA.value == "acceptance"
        assert SharanagatiLimb.PRATIKULYA.value == "rejection"
        assert SharanagatiLimb.VISHVASA.value == "faith"
        assert SharanagatiLimb.VARANAM.value == "guardianship"
        assert SharanagatiLimb.NIKSHEPA.value == "surrender"
        assert SharanagatiLimb.KARPANYA.value == "humility"


# =============================================================================
# Nava Tests
# =============================================================================


class TestNava:
    """Test Nava (9 processes)."""

    def test_nava_is_9(self):
        """NAVA = 9."""
        assert NAVA == 9

    def test_nava_formula(self):
        """NAVA = HARE_COUNT + KSETRAJNA."""
        assert NAVA == HARE_COUNT + KSETRAJNA

    def test_nava_bhakti_count(self):
        """NavaBhakti has 9 members."""
        assert len(NavaBhakti) == 9


# =============================================================================
# Higher Derivations Tests
# =============================================================================


class TestHigherDerivations:
    """Test higher derived constants."""

    def test_gita_chapters_is_18(self):
        """GITA_CHAPTERS = 18."""
        assert GITA_CHAPTERS == 18
        assert GITA_CHAPTERS == SHARANAGATI * TRINITY

    def test_kshetra_is_24(self):
        """KSHETRA = 24."""
        assert KSHETRA == 24
        assert KSHETRA == WORDS + HARE_COUNT

    def test_ksetrajna_is_1(self):
        """KSETRAJNA = 1 (Krishna)."""
        assert KSETRAJNA == 1

    def test_parampara_is_37(self):
        """PARAMPARA = 37."""
        assert PARAMPARA == 37
        assert PARAMPARA == KSHETRA + MAHAJANA_COUNT + KSETRAJNA

    def test_mahajana_count_is_12(self):
        """MAHAJANA_COUNT = 12."""
        assert MAHAJANA_COUNT == 12

    def test_lila_is_48(self):
        """LILA = 48."""
        assert LILA == 48
        assert LILA == WORDS * TRINITY

    def test_navadvipa_is_24(self):
        """NAVADVIPA = 24."""
        assert NAVADVIPA == 24
        assert NAVADVIPA == LILA // HALVES

    def test_puri_is_24(self):
        """PURI = 24."""
        assert PURI == 24
        assert PURI == LILA // HALVES

    def test_qualities_is_64(self):
        """QUALITIES = 64."""
        assert QUALITIES == 64
        assert QUALITIES == WORDS * QUARTERS

    def test_hidden_reserve_is_16(self):
        """HIDDEN_RESERVE = 16."""
        assert HIDDEN_RESERVE == 16
        assert HIDDEN_RESERVE == QUALITIES - LILA
        assert HIDDEN_RESERVE == WORDS

    def test_mala_is_108(self):
        """MALA = 108."""
        assert MALA == 108
        assert MALA == MAHAJANA_COUNT * NAVA

    def test_rounds_is_16(self):
        """ROUNDS = 16."""
        assert ROUNDS == 16
        assert ROUNDS == WORDS

    def test_daily_mantras_is_1728(self):
        """DAILY_MANTRAS = 1728."""
        assert DAILY_MANTRAS == 1728
        assert DAILY_MANTRAS == MALA * ROUNDS

    def test_jiva_cycle_is_432(self):
        """JIVA_CYCLE = 432."""
        assert JIVA_CYCLE == 432
        assert JIVA_CYCLE == MALA * QUARTERS

    def test_jiva_qualities_is_50(self):
        """JIVA_QUALITIES = 50."""
        assert JIVA_QUALITIES == 50
        assert JIVA_QUALITIES == COSMIC_FRAME // JIVA_CYCLE

    def test_aksara_count_is_32(self):
        """AKSARA_COUNT = 32."""
        assert AKSARA_COUNT == 32
        assert AKSARA_COUNT == WORDS * 2


# =============================================================================
# Dharma Tests
# =============================================================================


class TestDharma:
    """Test Dharma constants."""

    def test_dharma_pillars_is_4(self):
        """DHARMA_PILLARS = 4."""
        assert DHARMA_PILLARS == 4
        assert DHARMA_PILLARS == len(DharmaPillar)

    def test_kali_yuga_leg_is_truth(self):
        """KALI_YUGA_LEG = 'truth'."""
        assert KALI_YUGA_LEG == "truth"
        assert KALI_YUGA_LEG == DharmaPillar.SATYAM.value


# =============================================================================
# Guardian Tests
# =============================================================================


class TestGuardians:
    """Test Guardian constants."""

    def test_avatar_count_is_4(self):
        """AVATAR_COUNT = 4."""
        assert AVATAR_COUNT == 4

    def test_avataras_has_4(self):
        """AVATARAS has 4 members."""
        assert len(AVATARAS) == 4

    def test_avatars_alias(self):
        """AVATARS is alias for AVATARAS."""
        assert AVATARS == AVATARAS

    def test_mahajanas_has_12(self):
        """MAHAJANAS has 12 members."""
        assert len(MAHAJANAS) == 12

    def test_all_guardians_has_16(self):
        """ALL_GUARDIANS has 16 members."""
        assert len(ALL_GUARDIANS) == 16

    def test_guardians_sum(self):
        """AVATAR_COUNT + MAHAJANA_COUNT = 16."""
        assert AVATAR_COUNT + MAHAJANA_COUNT == WORDS

    def test_mahajana_to_position_complete(self):
        """MAHAJANA_TO_POSITION has all 16 guardians."""
        assert len(MAHAJANA_TO_POSITION) == 16

    def test_position_to_mahajana_complete(self):
        """POSITION_TO_MAHAJANA has all 16 positions."""
        assert len(POSITION_TO_MAHAJANA) == 16


# =============================================================================
# Prana (Timing) Tests
# =============================================================================


class TestPrana:
    """Test Prana timing constants."""

    def test_seconds_per_day(self):
        """SECONDS_PER_DAY = 86400."""
        assert SECONDS_PER_DAY == 86400

    def test_prana_duration_s_is_4(self):
        """PRANA_DURATION_S = 4 seconds."""
        assert PRANA_DURATION_S == 4

    def test_prana_duration_ms_is_4000(self):
        """PRANA_DURATION_MS = 4000 ms."""
        assert PRANA_DURATION_MS == 4000

    def test_tick_interval_ms_is_250(self):
        """TICK_INTERVAL_MS = 250 ms."""
        assert TICK_INTERVAL_MS == 250

    def test_timing_formula(self):
        """Timing formula: PRANA_DURATION_MS // WORDS = TICK_INTERVAL_MS."""
        assert PRANA_DURATION_MS // WORDS == TICK_INTERVAL_MS


# =============================================================================
# Acoustic Constitution Tests
# =============================================================================


class TestAcousticConstitution:
    """Test Acoustic Constitution constants."""

    def test_acoustic_ratio_is_18(self):
        """ACOUSTIC_RATIO = 18."""
        assert ACOUSTIC_RATIO == 18
        assert ACOUSTIC_RATIO == SHARANAGATI * TRINITY

    def test_end_correction_is_8(self):
        """END_CORRECTION = 8."""
        assert END_CORRECTION == 8
        assert END_CORRECTION == HARE_COUNT

    def test_venu_freq_is_72(self):
        """VENU_FREQ = 72."""
        assert VENU_FREQ == 72
        assert VENU_FREQ == JIVA_CYCLE // SHARANAGATI

    def test_vamsi_freq_is_48(self):
        """VAMSI_FREQ = 48."""
        assert VAMSI_FREQ == 48
        assert VAMSI_FREQ == JIVA_CYCLE // NAVA

    def test_murali_freq_is_108(self):
        """MURALI_FREQ = 108."""
        assert MURALI_FREQ == 108
        assert MURALI_FREQ == JIVA_CYCLE // QUARTERS

    def test_cutoff_constant_is_72(self):
        """CUTOFF_CONSTANT = 72."""
        assert CUTOFF_CONSTANT == 72

    def test_quinten_kette(self):
        """Perfect Fifth Chain verification."""
        assert MURALI_FREQ * 2 == VENU_FREQ * 3  # 108×2 = 72×3 = 216
        assert VENU_FREQ * 2 == VAMSI_FREQ * 3  # 72×2 = 48×3 = 144


# =============================================================================
# Three Flutes Tests
# =============================================================================


class TestThreeFlutes:
    """Test Three Flutes constants."""

    def test_venu_holes_is_6(self):
        """VENU_HOLES = 6."""
        assert VENU_HOLES == 6

    def test_vamsi_holes_is_9(self):
        """VAMSI_HOLES = 9."""
        assert VAMSI_HOLES == 9

    def test_murali_holes_is_4(self):
        """MURALI_HOLES = 4."""
        assert MURALI_HOLES == 4

    def test_flute_holes_sum_is_19(self):
        """FLUTE_HOLES_SUM = 19."""
        assert FLUTE_HOLES_SUM == 19
        assert FLUTE_HOLES_SUM == VENU_HOLES + VAMSI_HOLES + MURALI_HOLES

    def test_nadi_resonance_is_72(self):
        """NADI_RESONANCE = 72."""
        assert NADI_RESONANCE == 72


# =============================================================================
# Lotus Function Tests
# =============================================================================


class TestGetQuarter:
    """Test get_quarter function."""

    def test_position_0_is_genesis(self):
        """Position 0 is GENESIS."""
        assert get_quarter(0) == Quarter.GENESIS

    def test_position_4_is_dharma(self):
        """Position 4 is DHARMA."""
        assert get_quarter(4) == Quarter.DHARMA

    def test_position_8_is_karma(self):
        """Position 8 is KARMA."""
        assert get_quarter(8) == Quarter.KARMA

    def test_position_12_is_moksha(self):
        """Position 12 is MOKSHA."""
        assert get_quarter(12) == Quarter.MOKSHA

    def test_invalid_position_raises(self):
        """Invalid position raises ValueError."""
        with pytest.raises(ValueError):
            get_quarter(16)
        with pytest.raises(ValueError):
            get_quarter(-1)


class TestGetQuarterName:
    """Test get_quarter_name function."""

    def test_position_0_is_genesis(self):
        """Position 0 name is 'genesis'."""
        assert get_quarter_name(0) == "genesis"

    def test_position_4_is_dharma(self):
        """Position 4 name is 'dharma'."""
        assert get_quarter_name(4) == "dharma"


class TestGetPositionsInQuarter:
    """Test get_positions_in_quarter function."""

    def test_genesis_positions(self):
        """GENESIS positions are 0, 1, 2, 3."""
        assert get_positions_in_quarter(Quarter.GENESIS) == (0, 1, 2, 3)

    def test_dharma_positions(self):
        """DHARMA positions are 4, 5, 6, 7."""
        assert get_positions_in_quarter(Quarter.DHARMA) == (4, 5, 6, 7)

    def test_karma_positions(self):
        """KARMA positions are 8, 9, 10, 11."""
        assert get_positions_in_quarter(Quarter.KARMA) == (8, 9, 10, 11)

    def test_moksha_positions(self):
        """MOKSHA positions are 12, 13, 14, 15."""
        assert get_positions_in_quarter(Quarter.MOKSHA) == (12, 13, 14, 15)


class TestGetWordAt:
    """Test get_word_at function."""

    def test_position_0_is_hare(self):
        """Position 0 is HARE."""
        assert get_word_at(0) == HolyName.HARE

    def test_position_1_is_krishna(self):
        """Position 1 is KRISHNA."""
        assert get_word_at(1) == HolyName.KRISHNA

    def test_position_9_is_rama(self):
        """Position 9 is RAMA."""
        assert get_word_at(9) == HolyName.RAMA

    def test_invalid_position_raises(self):
        """Invalid position raises ValueError."""
        with pytest.raises(ValueError):
            get_word_at(16)


class TestGetPairAt:
    """Test get_pair_at function."""

    def test_position_0_pair(self):
        """Position 0 pair is (HARE, KRISHNA)."""
        assert get_pair_at(0) == (HolyName.HARE, HolyName.KRISHNA)

    def test_position_8_pair(self):
        """Position 8 pair is (HARE, RAMA)."""
        assert get_pair_at(8) == (HolyName.HARE, HolyName.RAMA)

    def test_odd_position_raises(self):
        """Odd position raises ValueError."""
        with pytest.raises(ValueError):
            get_pair_at(1)


class TestVerifyParampara:
    """Test verify_parampara function."""

    def test_37_is_valid(self):
        """37 is valid parampara."""
        assert verify_parampara(37) is True

    def test_74_is_valid(self):
        """74 (37 × 2) is valid."""
        assert verify_parampara(74) is True

    def test_0_is_valid(self):
        """0 is valid (0 % 37 == 0)."""
        assert verify_parampara(0) is True

    def test_36_is_invalid(self):
        """36 is not valid."""
        assert verify_parampara(36) is False


class TestMahajanaPositionFunctions:
    """Test mahajana position functions."""

    def test_get_mahajana_position_vyasa(self):
        """vyasa is at position 0."""
        assert get_mahajana_position("vyasa") == 0

    def test_get_mahajana_position_yamaraja(self):
        """yamaraja is at position 15."""
        assert get_mahajana_position("yamaraja") == 15

    def test_get_mahajana_position_case_insensitive(self):
        """get_mahajana_position is case insensitive."""
        assert get_mahajana_position("VYASA") == 0
        assert get_mahajana_position("Vyasa") == 0

    def test_get_position_mahajana_0(self):
        """Position 0 is vyasa."""
        assert get_position_mahajana(0) == "vyasa"

    def test_get_position_mahajana_15(self):
        """Position 15 is yamaraja."""
        assert get_position_mahajana(15) == "yamaraja"

    def test_get_guardian_quarter_vyasa(self):
        """vyasa is in genesis quarter."""
        assert get_guardian_quarter("vyasa") == "genesis"

    def test_get_guardian_quarter_yamaraja(self):
        """yamaraja is in moksha quarter."""
        assert get_guardian_quarter("yamaraja") == "moksha"

    def test_get_guardian_quarter_unknown(self):
        """Unknown guardian returns None."""
        assert get_guardian_quarter("unknown") is None


class TestLotusDeclaration:
    """Test lotus_declaration function."""

    def test_lotus_declaration_position_0(self):
        """lotus_declaration for position 0."""
        decl = lotus_declaration(0)
        assert decl["position"] == 0
        assert decl["quarter"] == Quarter.GENESIS
        assert decl["quarter_name"] == "genesis"
        assert decl["word"] == "HARE"
        assert decl["mahajana"] == "vyasa"
        assert decl["parampara_valid"] is True

    def test_lotus_declaration_has_genesis(self):
        """lotus_declaration has genesis byte."""
        decl = lotus_declaration(5)
        assert "genesis" in decl
        assert decl["genesis"].startswith("0x")


class TestVerifyLotus:
    """Test verify_lotus function."""

    def test_verify_lotus_valid_hex(self):
        """verify_lotus with valid parampara hex."""
        # 37 in hex = 0x25
        assert verify_lotus("0x25") is True
        assert verify_lotus("0x4a") is True  # 74

    def test_verify_lotus_invalid_hex(self):
        """verify_lotus with invalid parampara hex."""
        assert verify_lotus("0x24") is False  # 36

    def test_verify_lotus_invalid_format(self):
        """verify_lotus with invalid format returns False."""
        assert verify_lotus("invalid") is False
