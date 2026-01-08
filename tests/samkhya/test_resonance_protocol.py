"""
TEST_RESONANCE_PROTOCOL.py - The Acintya Bhedabheda Tests

Tests the Iron Rod principle: Z = a + bi (Structure + Substance).

QUADRANTS:
- 0 + 0i = MAYAVAD (Void)
- 1 + 0i = DRY_LOGIC (Iron without fire)
- 0 + 1i = SENTIMENTAL (Fire without form)
- 1 + 1i = PURE_DEVOTION (Iron acts as fire)
"""

import pytest

from vibe_core.protocols.substrate import HolyName, MantraOpCode
from vibe_core.protocols.universal.resonance import (
    AcintyaState,
    NullResonance,
    Quality,
    SemanticVibration,
    StructuralIntegrity,
    SystemAction,
    create_structure,
    create_substance,
    get_quality_from_vector,
)

# =============================================================================
# TESTS: STRUCTURAL INTEGRITY (The Real Part)
# =============================================================================


class TestStructuralIntegrity:
    """Das Eisen (a)."""

    def test_valid_with_full_coverage(self):
        """Valid code + 80%+ coverage = 1.0"""
        iron = StructuralIntegrity(
            is_valid=True,
            complexity=10.0,
            test_coverage=0.85,
            has_docstrings=True,
        )
        assert iron.value == 1.0

    def test_invalid_code(self):
        """Invalid syntax = 0.0"""
        iron = StructuralIntegrity(
            is_valid=False,
            complexity=5.0,
            test_coverage=0.95,
            has_docstrings=True,
        )
        assert iron.value == 0.0

    def test_low_coverage(self):
        """< 50% coverage = 0.5"""
        iron = StructuralIntegrity(
            is_valid=True,
            complexity=10.0,
            test_coverage=0.4,
            has_docstrings=True,
        )
        assert iron.value == 0.5


# =============================================================================
# TESTS: SEMANTIC VIBRATION (The Imaginary Part)
# =============================================================================


class TestSemanticVibration:
    """Das Feuer (b)."""

    def test_signed_with_clear_intent(self):
        """Mantra + signer + clarity = 1.0"""
        fire = SemanticVibration(
            has_mantra=True,
            signer_id="sovereign-001",
            intent_clarity=0.9,
            holy_name=HolyName.KRISHNA,
        )
        assert fire.value == 1.0

    def test_unsigned(self):
        """No mantra = 0.0"""
        fire = SemanticVibration(
            has_mantra=False,
            signer_id="someone",
            intent_clarity=1.0,
        )
        assert fire.value == 0.0

    def test_no_signer(self):
        """No signer = 0.0"""
        fire = SemanticVibration(
            has_mantra=True,
            signer_id="",
            intent_clarity=1.0,
        )
        assert fire.value == 0.0


# =============================================================================
# TESTS: ACINTYA STATE (The Complex Vector)
# =============================================================================


class TestAcintyaState:
    """Z = a + bi"""

    @pytest.fixture
    def pure_devotion(self) -> AcintyaState:
        """1 + 1i (Iron acts as fire)."""
        return AcintyaState(
            structure=create_structure(is_valid=True, test_coverage=0.9),
            substance=create_substance(has_mantra=True, signer_id="sovereign"),
        )

    @pytest.fixture
    def dry_logic(self) -> AcintyaState:
        """1 + 0i (Iron without fire)."""
        return AcintyaState(
            structure=create_structure(is_valid=True, test_coverage=0.9),
            substance=create_substance(has_mantra=False, signer_id=""),
        )

    @pytest.fixture
    def sentimental(self) -> AcintyaState:
        """0 + 1i (Fire without form)."""
        return AcintyaState(
            structure=create_structure(is_valid=False, test_coverage=0.0),
            substance=create_substance(has_mantra=True, signer_id="dreamer"),
        )

    @pytest.fixture
    def mayavad(self) -> AcintyaState:
        """0 + 0i (Void)."""
        return AcintyaState(
            structure=create_structure(is_valid=False, test_coverage=0.0),
            substance=create_substance(has_mantra=False, signer_id=""),
        )

    def test_pure_devotion_is_transparent(self, pure_devotion: AcintyaState):
        """Iron rod test: 1+1i = transparent."""
        assert pure_devotion.is_transparent()
        assert pure_devotion.get_quality() == Quality.PURE_DEVOTION
        assert pure_devotion.get_action() == SystemAction.EXECUTE

    def test_dry_logic_warns(self, dry_logic: AcintyaState):
        """1+0i warns about missing intent."""
        assert not dry_logic.is_transparent()
        assert dry_logic.get_quality() == Quality.DRY_LOGIC
        assert dry_logic.get_action() == SystemAction.WARN

    def test_sentimental_blocks(self, sentimental: AcintyaState):
        """0+1i blocks unsafe code."""
        assert not sentimental.is_transparent()
        assert sentimental.get_quality() == Quality.SENTIMENTAL
        assert sentimental.get_action() == SystemAction.BLOCK

    def test_mayavad_annihilates(self, mayavad: AcintyaState):
        """0+0i is removed from system."""
        assert not mayavad.is_transparent()
        assert mayavad.get_quality() == Quality.MAYAVAD
        assert mayavad.get_action() == SystemAction.ANNIHILATE

    def test_vector_complex(self, pure_devotion: AcintyaState):
        """Z = a + bi is a complex number."""
        z = pure_devotion.vector
        assert isinstance(z, complex)
        assert z.real == 1.0
        assert z.imag == 1.0


# =============================================================================
# TESTS: NULL RESONANCE
# =============================================================================


class TestNullResonance:
    """The void fallback."""

    def test_returns_mayavad(self):
        """Null returns 0+0i."""
        null = NullResonance()
        state = null.get_ontological_state()

        assert state.get_quality() == Quality.MAYAVAD
        assert not state.is_transparent()

    def test_cannot_instill(self):
        """Cannot instill life into void."""
        null = NullResonance()
        assert not null.instill_intent(MantraOpCode.LOAD_ROOT, "test")

    def test_never_transparent(self):
        """Void is never transparent."""
        null = NullResonance()
        assert not null.verify_transparency()


# =============================================================================
# TESTS: QUALITY FROM VECTOR
# =============================================================================


class TestQualityFromVector:
    """The quadrant detection."""

    def test_pure_devotion_quadrant(self):
        assert get_quality_from_vector(complex(1.0, 1.0)) == Quality.PURE_DEVOTION
        assert get_quality_from_vector(complex(0.8, 0.9)) == Quality.PURE_DEVOTION

    def test_dry_logic_quadrant(self):
        assert get_quality_from_vector(complex(1.0, 0.0)) == Quality.DRY_LOGIC
        assert get_quality_from_vector(complex(0.9, 0.3)) == Quality.DRY_LOGIC

    def test_sentimental_quadrant(self):
        assert get_quality_from_vector(complex(0.0, 1.0)) == Quality.SENTIMENTAL
        assert get_quality_from_vector(complex(0.3, 0.9)) == Quality.SENTIMENTAL

    def test_mayavad_quadrant(self):
        assert get_quality_from_vector(complex(0.0, 0.0)) == Quality.MAYAVAD
        assert get_quality_from_vector(complex(0.3, 0.3)) == Quality.MAYAVAD
