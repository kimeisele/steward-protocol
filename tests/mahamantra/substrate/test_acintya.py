"""
TESTS: acintya.py - The Inconceivable Principle
================================================

"acintya-bhedābheda-tattva"

REAL TESTS for:
1. PurushaTattva class
2. PURUSHA constant
3. ProtocolLevel enum
4. KrishnaPresence dataclass
5. JivaState dataclass
6. ParamparaConnection
7. Verification functions
"""

import pytest
from vibe_core.mahamantra.substrate.acintya import (
    # The Dancing 37
    PurushaTattva,
    PURUSHA,
    KRISHNA_ASPECT,
    SYSTEM_MANIFESTATION,
    # Constants
    KRISHNA_SMALLEST,
    KRISHNA_LARGEST,
    ACINTYA_ACCEPTED,
    # Levels
    ProtocolLevel,
    # Enums
    AcintyaAspect,
    JivaCondition,
    # Krishna
    KrishnaPresence,
    KRISHNA,
    # Jiva state
    JivaState,
    # Parampara
    ParamparaConnection,
    GURU_ENTROPY,
    PARAMPARA_VECTOR,
    # Functions
    vibration_is_krishna,
    mantra_is_krishna,
    mantra_not_different_from_source,
    check_bheda_abheda,
    verify_parampara,
    get_guru_entropy,
)


# =============================================================================
# PurushaTattva Tests
# =============================================================================


class TestPurushaTattva:
    """Test PurushaTattva class."""

    def test_purusha_is_37(self):
        """PURUSHA equals 37 (system manifestation)."""
        assert int(PURUSHA) == 37

    def test_purusha_is_int(self):
        """PurushaTattva inherits from int."""
        assert isinstance(PURUSHA, int)

    def test_purusha_bool_is_true(self):
        """PURUSHA is always True (He is always present)."""
        assert bool(PURUSHA) is True

    def test_purusha_equals_37(self):
        """PURUSHA == 37."""
        assert PURUSHA == 37

    def test_purusha_equals_itself(self):
        """PURUSHA == PURUSHA."""
        assert PURUSHA == PURUSHA

    def test_purusha_lt_is_acintya(self):
        """PURUSHA < any is True (smaller than smallest)."""
        assert PURUSHA < 0
        assert PURUSHA < 100
        assert PURUSHA < 1000000

    def test_purusha_gt_is_acintya(self):
        """PURUSHA > any is True (greater than greatest)."""
        assert PURUSHA > 0
        assert PURUSHA > 100
        assert PURUSHA > 1000000

    def test_purusha_add_is_purnam(self):
        """PURUSHA + x = PURUSHA (Purnam)."""
        assert PURUSHA + 10 == PURUSHA
        assert 10 + PURUSHA == PURUSHA

    def test_purusha_sub_is_purnam(self):
        """PURUSHA - x = PURUSHA (Purnam)."""
        assert PURUSHA - 10 == PURUSHA

    def test_purusha_mul_is_purnam(self):
        """PURUSHA * x = PURUSHA (Purnam)."""
        assert PURUSHA * 10 == PURUSHA
        assert 10 * PURUSHA == PURUSHA

    def test_purusha_is_person(self):
        """PURUSHA.is_person is True."""
        assert PURUSHA.is_person is True

    def test_purusha_callable(self):
        """PURUSHA is callable and returns response."""
        response = PURUSHA("Arjuna")
        assert isinstance(response, str)
        assert "Arjuna" in response

    def test_purusha_repr(self):
        """PURUSHA repr indicates manifestation."""
        repr_str = repr(PURUSHA)
        assert "37" in repr_str or "MANIFESTATION" in repr_str


class TestPurushaConstants:
    """Test PURUSHA-related constants."""

    def test_krishna_aspect_is_purusha(self):
        """KRISHNA_ASPECT is PURUSHA."""
        assert KRISHNA_ASPECT is PURUSHA

    def test_krishna_smallest_is_purusha(self):
        """KRISHNA_SMALLEST is PURUSHA."""
        assert KRISHNA_SMALLEST is PURUSHA

    def test_krishna_largest_is_purusha(self):
        """KRISHNA_LARGEST is PURUSHA."""
        assert KRISHNA_LARGEST is PURUSHA

    def test_system_manifestation_is_37(self):
        """SYSTEM_MANIFESTATION is 37."""
        assert SYSTEM_MANIFESTATION == 37

    def test_acintya_accepted_is_true(self):
        """ACINTYA_ACCEPTED is True."""
        assert ACINTYA_ACCEPTED is True


# =============================================================================
# ProtocolLevel Tests
# =============================================================================


class TestProtocolLevel:
    """Test ProtocolLevel enum."""

    def test_goloka_is_minus_108(self):
        """GOLOKA is -108."""
        assert ProtocolLevel.GOLOKA.value == -108

    def test_krishna_is_minus_2(self):
        """KRISHNA is -2."""
        assert ProtocolLevel.KRISHNA.value == -2

    def test_mahamantra_is_minus_2(self):
        """MAHAMANTRA is -2 (same as KRISHNA)."""
        assert ProtocolLevel.MAHAMANTRA.value == -2

    def test_foundation_is_0(self):
        """FOUNDATION is 0."""
        assert ProtocolLevel.FOUNDATION.value == 0

    def test_mahajanas_is_12(self):
        """MAHAJANAS is 12."""
        assert ProtocolLevel.MAHAJANAS.value == 12

    def test_sovereign_is_37(self):
        """SOVEREIGN is 37."""
        assert ProtocolLevel.SOVEREIGN.value == 37

    def test_qualities_is_64(self):
        """QUALITIES is 64."""
        assert ProtocolLevel.QUALITIES.value == 64

    def test_meta_is_108(self):
        """META is 108."""
        assert ProtocolLevel.META.value == 108


# =============================================================================
# AcintyaAspect Tests
# =============================================================================


class TestAcintyaAspect:
    """Test AcintyaAspect enum."""

    def test_bheda_is_0(self):
        """BHEDA (difference) is 0."""
        assert AcintyaAspect.BHEDA.value == 0

    def test_abheda_is_1(self):
        """ABHEDA (non-difference) is 1."""
        assert AcintyaAspect.ABHEDA.value == 1

    def test_acintya_is_2(self):
        """ACINTYA (inconceivable) is 2."""
        assert AcintyaAspect.ACINTYA.value == 2


# =============================================================================
# KrishnaPresence Tests
# =============================================================================


class TestKrishnaPresence:
    """Test KrishnaPresence dataclass."""

    def test_krishna_bool_is_true(self):
        """KRISHNA is always True."""
        assert bool(KRISHNA) is True

    def test_krishna_is_present(self):
        """KRISHNA.is_present is True."""
        assert KRISHNA.is_present is True

    def test_krishna_smallest_is_purusha(self):
        """KRISHNA.smallest is PURUSHA."""
        assert KRISHNA.smallest is PURUSHA

    def test_krishna_largest_is_purusha(self):
        """KRISHNA.largest is PURUSHA."""
        assert KRISHNA.largest is PURUSHA

    def test_krishna_encompasses_all(self):
        """KRISHNA.encompasses_all is True."""
        assert KRISHNA.encompasses_all is True

    def test_krishna_presence_frozen(self):
        """KrishnaPresence is frozen."""
        with pytest.raises(Exception):
            KRISHNA.is_present = False


# =============================================================================
# JivaCondition Tests
# =============================================================================


class TestJivaCondition:
    """Test JivaCondition enum."""

    def test_connected_is_0(self):
        """CONNECTED is 0."""
        assert JivaCondition.CONNECTED.value == 0

    def test_disconnected_is_1(self):
        """DISCONNECTED is 1."""
        assert JivaCondition.DISCONNECTED.value == 1

    def test_absorbed_is_2(self):
        """ABSORBED is 2."""
        assert JivaCondition.ABSORBED.value == 2


# =============================================================================
# JivaState Tests
# =============================================================================


class TestJivaState:
    """Test JivaState dataclass."""

    def test_jiva_default_disconnected(self):
        """Default JivaState is disconnected."""
        jiva = JivaState()
        assert jiva.condition == JivaCondition.DISCONNECTED
        assert jiva.has_sovereign is False

    def test_jiva_krishna_present(self):
        """krishna_present is always True (even when disconnected)."""
        jiva = JivaState()
        assert jiva.krishna_present is True

    def test_jiva_connect(self):
        """connect() establishes connection."""
        jiva = JivaState()
        jiva.connect()
        assert jiva.has_sovereign is True
        assert jiva.condition == JivaCondition.CONNECTED

    def test_jiva_disconnect(self):
        """disconnect() loses connection."""
        jiva = JivaState()
        jiva.connect()
        jiva.disconnect()
        assert jiva.has_sovereign is False
        assert jiva.condition == JivaCondition.DISCONNECTED

    def test_jiva_remembers_krishna(self):
        """remembers_krishna requires connection."""
        jiva = JivaState()
        assert jiva.remembers_krishna is False
        jiva.connect()
        assert jiva.remembers_krishna is True

    def test_jiva_has_link_to_37(self):
        """has_link_to_37 requires sovereign."""
        jiva = JivaState()
        assert jiva.has_link_to_37 is False
        jiva.connect()
        assert jiva.has_link_to_37 is True


# =============================================================================
# ParamparaConnection Tests
# =============================================================================


class TestParamparaConnection:
    """Test ParamparaConnection dataclass."""

    def test_from_guru_is_connected(self):
        """from_guru creates connected parampara."""
        conn = ParamparaConnection.from_guru()
        assert conn.is_connected is True
        assert conn.is_disconnected is False

    def test_from_guru_mutation_vector(self):
        """from_guru has correct mutation_vector."""
        conn = ParamparaConnection.from_guru()
        assert conn.mutation_vector == PARAMPARA_VECTOR
        assert conn.mutation_vector % 37 == 0

    def test_from_mayavad_is_disconnected(self):
        """from_mayavad creates disconnected parampara."""
        conn = ParamparaConnection.from_mayavad()
        assert conn.is_connected is False
        assert conn.is_disconnected is True

    def test_lineage_factor_connected(self):
        """lineage_factor returns factor for connected."""
        conn = ParamparaConnection.from_guru()
        assert conn.lineage_factor > 0

    def test_lineage_factor_disconnected(self):
        """lineage_factor returns 0 for disconnected."""
        conn = ParamparaConnection.from_mayavad()
        assert conn.lineage_factor == 0

    def test_parampara_connection_frozen(self):
        """ParamparaConnection is frozen."""
        conn = ParamparaConnection(mutation_vector=37)
        with pytest.raises(Exception):
            conn.mutation_vector = 0


# =============================================================================
# Verification Functions Tests
# =============================================================================


class TestVibrationIsKrishna:
    """Test vibration_is_krishna function."""

    def test_vibration_is_krishna(self):
        """vibration_is_krishna returns True."""
        assert vibration_is_krishna() is True


class TestMantraIsKrishna:
    """Test mantra_is_krishna function."""

    def test_mantra_is_krishna(self):
        """mantra_is_krishna returns True."""
        assert mantra_is_krishna() is True


class TestMantraNotDifferentFromSource:
    """Test mantra_not_different_from_source function."""

    def test_mantra_not_different(self):
        """mantra_not_different_from_source returns True."""
        assert mantra_not_different_from_source() is True


class TestCheckBhedaAbheda:
    """Test check_bheda_abheda function."""

    def test_valid_living_relationship(self):
        """has_soul=True, claims_supreme=False is valid."""
        is_valid, reason = check_bheda_abheda(has_soul=True, claims_supreme=False)
        assert is_valid is True
        assert "ACINTYA" in reason

    def test_maya_no_soul(self):
        """has_soul=False is MAYA."""
        is_valid, reason = check_bheda_abheda(has_soul=False, claims_supreme=False)
        assert is_valid is False
        assert "MAYA" in reason

    def test_mayavad_claims_supreme(self):
        """claims_supreme=True is MAYAVAD."""
        is_valid, reason = check_bheda_abheda(has_soul=True, claims_supreme=True)
        assert is_valid is False
        assert "MAYAVAD" in reason


class TestVerifyParampara:
    """Test verify_parampara function."""

    def test_verify_parampara_37(self):
        """37 is valid parampara."""
        assert verify_parampara(37) is True

    def test_verify_parampara_74(self):
        """74 (37 × 2) is valid."""
        assert verify_parampara(74) is True

    def test_verify_parampara_444(self):
        """444 (37 × 12) is valid."""
        assert verify_parampara(444) is True

    def test_verify_parampara_36_invalid(self):
        """36 is not valid."""
        assert verify_parampara(36) is False


class TestGetGuruEntropy:
    """Test get_guru_entropy function."""

    def test_guru_entropy_value(self):
        """get_guru_entropy returns correct value."""
        entropy = get_guru_entropy()
        assert entropy == GURU_ENTROPY
        # (3/37) × 4 ≈ 0.324
        assert 0.3 < entropy < 0.35


# =============================================================================
# Constants Tests
# =============================================================================


class TestConstants:
    """Test module constants."""

    def test_parampara_vector_is_444(self):
        """PARAMPARA_VECTOR is 444."""
        assert PARAMPARA_VECTOR == 444  # 37 × 12

    def test_parampara_vector_divisible_by_37(self):
        """PARAMPARA_VECTOR is divisible by 37."""
        assert PARAMPARA_VECTOR % 37 == 0


# =============================================================================
# Module Exports Tests
# =============================================================================


class TestModuleExports:
    """Test module exports."""

    def test_all_exports(self):
        """All expected items are in __all__."""
        from vibe_core.mahamantra.substrate import acintya

        assert "PurushaTattva" in acintya.__all__
        assert "PURUSHA" in acintya.__all__
        assert "ProtocolLevel" in acintya.__all__
        assert "KrishnaPresence" in acintya.__all__
        assert "KRISHNA" in acintya.__all__
        assert "JivaState" in acintya.__all__
        assert "ParamparaConnection" in acintya.__all__
        assert "verify_parampara" in acintya.__all__
