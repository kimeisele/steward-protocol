"""
TESTS: _singularity.py - The Chaitanya Singularity Protocol
============================================================

REAL TESTS for:
1. Yuga time constants
2. Chaitanya Lila constants
3. Singularity probability
4. Mercy equation
5. 12 Mahajanas
6. The 37th Formula
7. ReceiverState
8. SingularityProtocol
"""

import pytest
from vibe_core.mahamantra.protocols._singularity import (
    # Yuga Time Constants
    T_SATYA,
    T_TRETA,
    T_DVAPARA,
    T_KALI,
    T_CHATURYUGA,
    T_BRAHMA,
    GOLDEN_PERIOD,
    YEARS_INTO_KALI,
    # Singularity Probability
    P_SINGULARITY_PER_KALI,
    P_WITHIN_GOLDEN_PERIOD,
    P_NOW,
    IS_BLACK_SWAN,
    SingularityProbability,
    SINGULARITY_PROBABILITY,
    # Mercy Equation
    mercy_equation,
    mercy_transcends_justice,
    # 12 Mahajanas
    Mahajana,
    MahajanaMapping,
    MAHAJANA_MAPPINGS,
    get_mahajana_mapping,
    # The 37th Formula
    The37thFormula,
    THE_37TH_FORMULA,
    # Receiver Architecture
    ReceiverState,
    # Protocol
    SingularityProtocol,
    # Convenience
    get_years_remaining_in_golden_period,
    is_in_golden_period,
    get_singularity_summary,
)


# =============================================================================
# Yuga Time Constants Tests
# =============================================================================


class TestYugaTimeConstants:
    """Test Yuga time constants."""

    def test_t_satya(self):
        """T_SATYA is 1,728,000."""
        assert T_SATYA == 1_728_000

    def test_t_treta(self):
        """T_TRETA is 1,296,000."""
        assert T_TRETA == 1_296_000

    def test_t_dvapara(self):
        """T_DVAPARA is 864,000."""
        assert T_DVAPARA == 864_000

    def test_t_kali(self):
        """T_KALI is 432,000."""
        assert T_KALI == 432_000

    def test_t_chaturyuga(self):
        """T_CHATURYUGA is sum of 4 yugas."""
        assert T_CHATURYUGA == T_SATYA + T_TRETA + T_DVAPARA + T_KALI
        assert T_CHATURYUGA == 4_320_000

    def test_t_brahma(self):
        """T_BRAHMA is 1000 chaturyugas."""
        assert T_BRAHMA == T_CHATURYUGA * 1000
        assert T_BRAHMA == 4_320_000_000

    def test_golden_period(self):
        """GOLDEN_PERIOD is 10,000."""
        assert GOLDEN_PERIOD == 10_000


# =============================================================================
# Singularity Probability Tests
# =============================================================================


class TestSingularityProbability:
    """Test singularity probability constants."""

    def test_p_singularity_per_kali(self):
        """P_SINGULARITY_PER_KALI is 1/1000."""
        assert P_SINGULARITY_PER_KALI == 0.001

    def test_p_within_golden_period(self):
        """P_WITHIN_GOLDEN_PERIOD is ~0.023."""
        assert P_WITHIN_GOLDEN_PERIOD == pytest.approx(0.023, rel=0.1)

    def test_is_black_swan(self):
        """IS_BLACK_SWAN is True."""
        assert IS_BLACK_SWAN is True
        assert P_NOW < 0.0001

    def test_singularity_probability_dataclass(self):
        """SingularityProbability dataclass works."""
        prob = SINGULARITY_PROBABILITY
        assert prob.per_kali_yuga == P_SINGULARITY_PER_KALI
        assert prob.within_golden == P_WITHIN_GOLDEN_PERIOD
        assert prob.is_black_swan is True


# =============================================================================
# Mercy Equation Tests
# =============================================================================


class TestMercyEquation:
    """Test mercy equation."""

    def test_mercy_equation_no_chanting(self):
        """Returns 0.0 with no chanting."""
        assert mercy_equation(0.0, 100.0) == 0.0

    def test_mercy_equation_no_debt(self):
        """Returns infinity with no debt."""
        result = mercy_equation(1.0, 0.0)
        assert result == float("inf")

    def test_mercy_equation_ratio(self):
        """Returns f/K for normal case."""
        assert mercy_equation(10.0, 5.0) == 2.0

    def test_mercy_transcends_justice_true(self):
        """Returns True when chanting."""
        assert mercy_transcends_justice(1.0) is True
        assert mercy_transcends_justice(0.1) is True

    def test_mercy_transcends_justice_false(self):
        """Returns False with no chanting."""
        assert mercy_transcends_justice(0.0) is False


# =============================================================================
# 12 Mahajanas Tests
# =============================================================================


class TestMahajanas:
    """Test 12 Mahajanas."""

    def test_mahajana_count(self):
        """There are 12 Mahajanas."""
        assert len(Mahajana) == 12

    def test_mahajana_brahma(self):
        """Mahajana.BRAHMA is 1."""
        assert Mahajana.BRAHMA == 1

    def test_mahajana_yamaraja(self):
        """Mahajana.YAMARAJA is 12."""
        assert Mahajana.YAMARAJA == 12

    def test_mahajana_mappings_count(self):
        """MAHAJANA_MAPPINGS has 12 entries."""
        assert len(MAHAJANA_MAPPINGS) == 12

    def test_get_mahajana_mapping(self):
        """get_mahajana_mapping returns mapping."""
        mapping = get_mahajana_mapping(Mahajana.BRAHMA)
        assert mapping.mahajana == Mahajana.BRAHMA
        assert mapping.principle == "Creation"

    def test_mahajana_mapping_dataclass(self):
        """MahajanaMapping dataclass works."""
        mapping = MAHAJANA_MAPPINGS[0]
        assert isinstance(mapping, MahajanaMapping)
        assert mapping.mahajana is not None
        assert mapping.principle is not None


# =============================================================================
# The 37th Formula Tests
# =============================================================================


class TestThe37thFormula:
    """Test The 37th Formula."""

    def test_formula_values(self):
        """THE_37TH_FORMULA has correct values."""
        formula = THE_37TH_FORMULA
        assert formula.ksetra == 24
        assert formula.mahajanas == 12
        assert formula.ksetrajna == 1
        assert formula.parampara == 37

    def test_formula_sum(self):
        """24 + 12 + 1 = 37."""
        formula = THE_37TH_FORMULA
        assert formula.ksetra + formula.mahajanas + formula.ksetrajna == formula.parampara

    def test_verify_connection_valid(self):
        """verify_connection returns True for multiples of 37."""
        formula = THE_37TH_FORMULA
        assert formula.verify_connection(37) is True
        assert formula.verify_connection(74) is True
        assert formula.verify_connection(111) is True

    def test_verify_connection_invalid(self):
        """verify_connection returns False for non-multiples."""
        formula = THE_37TH_FORMULA
        assert formula.verify_connection(36) is False
        assert formula.verify_connection(38) is False


# =============================================================================
# ReceiverState Tests
# =============================================================================


class TestReceiverState:
    """Test ReceiverState dataclass."""

    def test_receiver_state_creation(self):
        """ReceiverState can be created."""
        state = ReceiverState(
            is_chanting=True,
            is_connected=True,
            karmic_debt=0.0,
        )
        assert state.is_chanting is True
        assert state.is_connected is True

    def test_can_receive_true(self):
        """can_receive True when chanting and connected."""
        state = ReceiverState(
            is_chanting=True,
            is_connected=True,
            karmic_debt=0.0,
        )
        assert state.can_receive is True

    def test_can_receive_false_not_chanting(self):
        """can_receive False when not chanting."""
        state = ReceiverState(
            is_chanting=False,
            is_connected=True,
            karmic_debt=0.0,
        )
        assert state.can_receive is False

    def test_can_receive_false_not_connected(self):
        """can_receive False when not connected."""
        state = ReceiverState(
            is_chanting=True,
            is_connected=False,
            karmic_debt=0.0,
        )
        assert state.can_receive is False

    def test_grace_level_not_chanting(self):
        """grace_level 0.0 when not chanting."""
        state = ReceiverState(
            is_chanting=False,
            is_connected=True,
            karmic_debt=10.0,
        )
        assert state.grace_level == 0.0

    def test_is_liberated(self):
        """is_liberated True when can_receive and no debt."""
        state = ReceiverState(
            is_chanting=True,
            is_connected=True,
            karmic_debt=0.0,
        )
        assert state.is_liberated is True


# =============================================================================
# SingularityProtocol Tests
# =============================================================================


class TestSingularityProtocol:
    """Test SingularityProtocol."""

    def test_singularity_protocol_validates(self):
        """SingularityProtocol validates."""
        valid, violations = SingularityProtocol.validate()
        assert valid is True

    def test_singularity_protocol_identity(self):
        """SingularityProtocol has correct identity."""
        identity = SingularityProtocol.get_identity()
        assert identity.name == "SingularityProtocol"
        assert identity.mahajana == "prithu"
        assert identity.position == 0

    def test_singularity_protocol_provides(self):
        """SingularityProtocol provides singularity capabilities."""
        cap = SingularityProtocol.get_capability()
        assert "singularity_mathematics" in cap.provides
        assert "mercy_equation" in cap.provides
        assert "mahajana_mappings" in cap.provides


# =============================================================================
# Convenience Functions Tests
# =============================================================================


class TestConvenienceFunctions:
    """Test convenience functions."""

    def test_is_in_golden_period(self):
        """is_in_golden_period returns True."""
        assert is_in_golden_period() is True

    def test_get_years_remaining_in_golden_period(self):
        """get_years_remaining returns positive value."""
        remaining = get_years_remaining_in_golden_period()
        assert remaining > 0
        assert remaining < GOLDEN_PERIOD

    def test_get_singularity_summary(self):
        """get_singularity_summary returns dict."""
        summary = get_singularity_summary()
        assert isinstance(summary, dict)
        assert "yuga" in summary
        assert "probability" in summary
        assert "formula" in summary
        assert "chaitanya" in summary


# =============================================================================
# Module Exports Tests
# =============================================================================


class TestModuleExports:
    """Test module exports."""

    def test_all_exports(self):
        """All expected items are in __all__."""
        from vibe_core.mahamantra.protocols import _singularity

        expected = [
            "T_KALI",
            "T_BRAHMA",
            "GOLDEN_PERIOD",
            "SingularityProbability",
            "mercy_equation",
            "Mahajana",
            "The37thFormula",
            "ReceiverState",
            "SingularityProtocol",
        ]
        for item in expected:
            assert item in _singularity.__all__, f"{item} should be in __all__"
