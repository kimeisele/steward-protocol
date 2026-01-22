"""
TESTS: _lila.py - The Lila Boundary Protocol
=============================================

REAL TESTS for:
1. Lila constants
2. LilaPhase enum
3. LilaBoundaryViolation exception
4. ParamparaDisconnection exception
5. LilaBoundary dataclass
6. LilaBoundedOutput dataclass
7. LilaProtocol
"""

import pytest
from vibe_core.mahamantra.protocols._lila import (
    # Constants
    LILA_BOUNDARY,
    LILA_CYCLES,
    LILA_LIMIT,
    # Phase
    LilaPhase,
    # Exceptions
    LilaBoundaryViolation,
    ParamparaDisconnection,
    # Enforcer
    LilaBoundary,
    LilaBoundedOutput,
    # Protocol
    LilaProtocol,
)
from vibe_core.mahamantra.substrate.seed import PARAMPARA


# =============================================================================
# Constants Tests
# =============================================================================


class TestLilaConstants:
    """Test Lila constants."""

    def test_lila_boundary_is_24(self):
        """LILA_BOUNDARY is 24."""
        assert LILA_BOUNDARY == 24

    def test_lila_limit_is_48(self):
        """LILA_LIMIT is 48."""
        assert LILA_LIMIT == 48

    def test_lila_cycles_is_3(self):
        """LILA_CYCLES is 3."""
        assert LILA_CYCLES == 3


# =============================================================================
# LilaPhase Enum Tests
# =============================================================================


class TestLilaPhase:
    """Test LilaPhase enum."""

    def test_lila_phase_navadvipa(self):
        """LilaPhase has NAVADVIPA."""
        assert LilaPhase.NAVADVIPA.value == "navadvipa"

    def test_lila_phase_puri(self):
        """LilaPhase has PURI."""
        assert LilaPhase.PURI.value == "puri"

    def test_lila_phase_complete(self):
        """LilaPhase has COMPLETE."""
        assert LilaPhase.COMPLETE.value == "complete"

    def test_from_index_navadvipa(self):
        """from_index returns NAVADVIPA for 0-23."""
        assert LilaPhase.from_index(0) == LilaPhase.NAVADVIPA
        assert LilaPhase.from_index(23) == LilaPhase.NAVADVIPA

    def test_from_index_puri(self):
        """from_index returns PURI for 24-47."""
        assert LilaPhase.from_index(24) == LilaPhase.PURI
        assert LilaPhase.from_index(47) == LilaPhase.PURI

    def test_from_index_complete(self):
        """from_index returns COMPLETE for 48+."""
        assert LilaPhase.from_index(48) == LilaPhase.COMPLETE
        assert LilaPhase.from_index(100) == LilaPhase.COMPLETE

    def test_from_index_negative_raises(self):
        """from_index raises for negative index."""
        with pytest.raises(LilaBoundaryViolation):
            LilaPhase.from_index(-1)

    def test_get_limit_navadvipa(self):
        """get_limit returns 24 for NAVADVIPA."""
        assert LilaPhase.get_limit(LilaPhase.NAVADVIPA) == 24

    def test_get_limit_puri(self):
        """get_limit returns 48 for PURI."""
        assert LilaPhase.get_limit(LilaPhase.PURI) == 48


# =============================================================================
# Exception Tests
# =============================================================================


class TestLilaBoundaryViolation:
    """Test LilaBoundaryViolation exception."""

    def test_lila_boundary_violation_message(self):
        """LilaBoundaryViolation has correct message."""
        exc = LilaBoundaryViolation(
            "test message",
            current_count=25,
            boundary=24,
            phase=LilaPhase.NAVADVIPA,
        )
        assert "LILA BOUNDARY VIOLATION" in str(exc)
        assert "test message" in str(exc)
        assert "25" in str(exc)
        assert "24" in str(exc)


class TestParamparaDisconnection:
    """Test ParamparaDisconnection exception."""

    def test_parampara_disconnection_message(self):
        """ParamparaDisconnection has correct message."""
        exc = ParamparaDisconnection(signature=38)
        assert "PARAMPARA DISCONNECTION" in str(exc)
        assert "38" in str(exc)


# =============================================================================
# LilaBoundary Tests
# =============================================================================


class TestLilaBoundary:
    """Test LilaBoundary dataclass."""

    def test_lila_boundary_creation_valid(self):
        """LilaBoundary can be created with valid signature."""
        boundary = LilaBoundary[str](signature=37)
        assert boundary.signature == 37
        assert len(boundary.items) == 0

    def test_lila_boundary_creation_invalid_signature(self):
        """LilaBoundary raises with invalid signature."""
        with pytest.raises(ParamparaDisconnection):
            LilaBoundary[str](signature=38)

    def test_lila_boundary_add_strict(self):
        """add with strict=True enforces 24 limit."""
        boundary = LilaBoundary[str](signature=37)
        for i in range(24):
            boundary.add(f"item_{i}", strict=True)
        assert len(boundary) == 24

        with pytest.raises(LilaBoundaryViolation):
            boundary.add("one_more", strict=True)

    def test_lila_boundary_add_non_strict(self):
        """add with strict=False advances phases."""
        boundary = LilaBoundary[str](signature=37)
        for i in range(25):
            boundary.add(f"item_{i}", strict=False)
        assert len(boundary) == 25
        assert boundary.phase == LilaPhase.PURI

    def test_lila_boundary_advance_phase(self):
        """advance_phase manually advances."""
        boundary = LilaBoundary[str](signature=37)
        assert boundary.phase == LilaPhase.NAVADVIPA
        boundary.advance_phase()
        assert boundary.phase == LilaPhase.PURI
        boundary.advance_phase()
        assert boundary.phase == LilaPhase.COMPLETE

    def test_lila_boundary_validate(self):
        """validate returns (bool, violations)."""
        boundary = LilaBoundary[str](signature=37)
        valid, violations = boundary.validate()
        assert valid is True
        assert len(violations) == 0

    def test_lila_boundary_validate_strict(self):
        """validate_strict raises on violation."""
        boundary = LilaBoundary[str](signature=37)
        boundary.validate_strict()  # Should not raise

    def test_lila_boundary_count(self):
        """count returns item count."""
        boundary = LilaBoundary[str](signature=37)
        boundary.add("a", strict=False)
        boundary.add("b", strict=False)
        assert boundary.count == 2

    def test_lila_boundary_overflow(self):
        """Items beyond 48 go to overflow."""
        boundary = LilaBoundary[str](signature=37)
        for i in range(50):
            boundary.add(f"item_{i}", strict=False)
        assert len(boundary.items) == 48
        assert boundary.overflow_count == 2
        assert boundary.has_overflow is True

    def test_lila_boundary_is_at_boundary(self):
        """is_at_boundary checks current phase limit."""
        boundary = LilaBoundary[str](signature=37)
        assert boundary.is_at_boundary is False
        for i in range(24):
            boundary.add(f"item_{i}", strict=False)
        assert boundary.is_at_boundary is True

    def test_lila_boundary_iterable(self):
        """LilaBoundary is iterable."""
        boundary = LilaBoundary[str](signature=37)
        boundary.add("a", strict=False)
        boundary.add("b", strict=False)
        items = list(boundary)
        assert items == ["a", "b"]


# =============================================================================
# LilaBoundedOutput Tests
# =============================================================================


class TestLilaBoundedOutput:
    """Test LilaBoundedOutput dataclass."""

    def test_lila_bounded_output_create(self):
        """LilaBoundedOutput.create works."""
        output = LilaBoundedOutput.create()
        assert output.count == 0

    def test_lila_bounded_output_add(self):
        """add adds key-value pairs."""
        output = LilaBoundedOutput.create()
        output.add("key1", "value1")
        output.add("key2", "value2")
        assert output.count == 2
        assert output.total == 2

    def test_lila_bounded_output_has_more(self):
        """has_more indicates overflow."""
        output = LilaBoundedOutput.create()
        for i in range(50):
            output.add(f"key_{i}", f"value_{i}")
        assert output.has_more is True

    def test_lila_bounded_output_to_dict(self):
        """to_dict serializes correctly."""
        output = LilaBoundedOutput.create()
        output.add("key1", "value1")
        data = output.to_dict()
        assert "items" in data
        assert "count" in data
        assert "parampara_verified" in data
        assert data["parampara_verified"] is True


# =============================================================================
# LilaProtocol Tests
# =============================================================================


class TestLilaProtocol:
    """Test LilaProtocol."""

    def test_lila_protocol_validates(self):
        """LilaProtocol validates."""
        valid, violations = LilaProtocol.validate()
        assert valid is True

    def test_lila_protocol_identity(self):
        """LilaProtocol has correct identity."""
        identity = LilaProtocol.get_identity()
        assert identity.name == "LilaProtocol"
        assert identity.mahajana == "kapila"
        assert identity.position == 6

    def test_lila_protocol_provides(self):
        """LilaProtocol provides lila capabilities."""
        cap = LilaProtocol.get_capability()
        assert "lila_boundary_enforcement" in cap.provides
        assert "parampara_verification" in cap.provides


# =============================================================================
# Module Exports Tests
# =============================================================================


class TestModuleExports:
    """Test module exports."""

    def test_all_exports(self):
        """All expected items are in __all__."""
        from vibe_core.mahamantra.protocols import _lila
        expected = [
            "LILA_BOUNDARY",
            "LILA_LIMIT",
            "LilaPhase",
            "LilaBoundaryViolation",
            "ParamparaDisconnection",
            "LilaBoundary",
            "LilaBoundedOutput",
            "LilaProtocol",
        ]
        for item in expected:
            assert item in _lila.__all__, f"{item} should be in __all__"
