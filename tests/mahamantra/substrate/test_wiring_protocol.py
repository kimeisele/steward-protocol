"""
TESTS: wiring_protocol.py - The Enforcement Layer
==================================================

"dharma-kṣetre kuru-kṣetre samavetā yuyutsavaḥ"

REAL TESTS for:
1. ViolationType constants
2. Violation and ValidationResult TypedDicts
3. EXPECTED_* SSOT-derived constants
4. WiringEnforcementProtocol
5. WiringEnforcer implementation
6. enforce_wiring convenience function
"""

import pytest
import tempfile
from pathlib import Path
from typing import get_type_hints
from vibe_core.mahamantra.substrate.wiring_protocol import (
    # Types
    ViolationType,
    Violation,
    ValidationResult,
    # SSOT expectations
    EXPECTED_QUARTERS,
    EXPECTED_POSITIONS,
    EXPECTED_PATHS,
    # Protocol
    WiringEnforcementProtocol,
    # Implementation
    WiringEnforcer,
    # Convenience
    enforce_wiring,
)
from vibe_core.mahamantra.substrate.mahajana import Quarter


# =============================================================================
# ViolationType Tests
# =============================================================================


class TestViolationType:
    """Test ViolationType constants."""

    def test_orphan_folder_constant(self):
        """ORPHAN_FOLDER is 'orphan_folder'."""
        assert ViolationType.ORPHAN_FOLDER == "orphan_folder"

    def test_missing_folder_constant(self):
        """MISSING_FOLDER is 'missing_folder'."""
        assert ViolationType.MISSING_FOLDER == "missing_folder"

    def test_missing_declaration_constant(self):
        """MISSING_DECLARATION is 'missing_decl'."""
        assert ViolationType.MISSING_DECLARATION == "missing_decl"

    def test_wrong_position_constant(self):
        """WRONG_POSITION is 'wrong_position'."""
        assert ViolationType.WRONG_POSITION == "wrong_position"

    def test_wrong_quarter_constant(self):
        """WRONG_QUARTER is 'wrong_quarter'."""
        assert ViolationType.WRONG_QUARTER == "wrong_quarter"

    def test_no_protocol_constant(self):
        """NO_PROTOCOL is 'no_protocol'."""
        assert ViolationType.NO_PROTOCOL == "no_protocol"

    def test_no_null_constant(self):
        """NO_NULL is 'no_null'."""
        assert ViolationType.NO_NULL == "no_null"


# =============================================================================
# TypedDict Tests
# =============================================================================


class TestViolationTypedDict:
    """Test Violation TypedDict."""

    def test_violation_keys(self):
        """Violation has correct keys."""
        hints = get_type_hints(Violation)
        expected_keys = {"type", "path", "expected", "actual", "severity"}
        assert set(hints.keys()) == expected_keys

    def test_violation_can_be_created(self):
        """Violation can be instantiated."""
        v: Violation = {
            "type": ViolationType.MISSING_FOLDER,
            "path": "/some/path",
            "expected": "brahma",
            "actual": "<missing>",
            "severity": "error",
        }
        assert v["type"] == ViolationType.MISSING_FOLDER
        assert v["severity"] == "error"


class TestValidationResultTypedDict:
    """Test ValidationResult TypedDict."""

    def test_validation_result_keys(self):
        """ValidationResult has correct keys."""
        hints = get_type_hints(ValidationResult)
        expected_keys = {
            "valid", "violations", "wired_count",
            "orphan_count", "missing_count", "coverage"
        }
        assert set(hints.keys()) == expected_keys

    def test_validation_result_can_be_created(self):
        """ValidationResult can be instantiated."""
        result: ValidationResult = {
            "valid": True,
            "violations": [],
            "wired_count": 16,
            "orphan_count": 0,
            "missing_count": 0,
            "coverage": 1.0,
        }
        assert result["valid"] is True
        assert result["coverage"] == 1.0


# =============================================================================
# SSOT Expectations Tests
# =============================================================================


class TestExpectedQuarters:
    """Test EXPECTED_QUARTERS derived from SSOT."""

    def test_exactly_4_quarters(self):
        """EXPECTED_QUARTERS has exactly 4 quarters."""
        assert len(EXPECTED_QUARTERS) == 4

    def test_quarter_values(self):
        """EXPECTED_QUARTERS has correct values."""
        expected = {"genesis", "dharma", "karma", "moksha"}
        assert EXPECTED_QUARTERS == expected

    def test_quarters_match_enum(self):
        """EXPECTED_QUARTERS matches Quarter enum."""
        enum_values = {q.value for q in Quarter}
        assert EXPECTED_QUARTERS == enum_values


class TestExpectedPositions:
    """Test EXPECTED_POSITIONS derived from SSOT."""

    def test_has_4_quarters(self):
        """EXPECTED_POSITIONS has 4 quarters as keys."""
        assert len(EXPECTED_POSITIONS) == 4
        assert "genesis" in EXPECTED_POSITIONS
        assert "dharma" in EXPECTED_POSITIONS
        assert "karma" in EXPECTED_POSITIONS
        assert "moksha" in EXPECTED_POSITIONS

    def test_each_quarter_has_4_positions(self):
        """Each quarter has 4 positions (4 guardians each)."""
        for quarter, positions in EXPECTED_POSITIONS.items():
            assert len(positions) == 4, f"{quarter} should have 4 positions"

    def test_total_16_positions(self):
        """Total of 16 positions across all quarters."""
        total = sum(len(pos) for pos in EXPECTED_POSITIONS.values())
        assert total == 16

    def test_genesis_has_vyasa(self):
        """Genesis quarter has vyasa (position 0)."""
        assert "vyasa" in EXPECTED_POSITIONS["genesis"]

    def test_dharma_has_prithu(self):
        """Dharma quarter has prithu (position 4)."""
        assert "prithu" in EXPECTED_POSITIONS["dharma"]

    def test_karma_has_parashurama(self):
        """Karma quarter has parashurama (position 8)."""
        assert "parashurama" in EXPECTED_POSITIONS["karma"]

    def test_moksha_has_nrisimha(self):
        """Moksha quarter has nrisimha (position 12)."""
        assert "nrisimha" in EXPECTED_POSITIONS["moksha"]


class TestExpectedPaths:
    """Test EXPECTED_PATHS derived from SSOT."""

    def test_exactly_16_paths(self):
        """EXPECTED_PATHS has exactly 16 entries."""
        assert len(EXPECTED_PATHS) == 16

    def test_path_format(self):
        """Paths follow 'quarter/guardian' format."""
        for path in EXPECTED_PATHS.keys():
            assert "/" in path
            parts = path.split("/")
            assert len(parts) == 2

    def test_vyasa_path_index_0(self):
        """genesis/vyasa maps to index 0."""
        assert EXPECTED_PATHS["genesis/vyasa"] == 0

    def test_prithu_path_index_4(self):
        """dharma/prithu maps to index 4."""
        assert EXPECTED_PATHS["dharma/prithu"] == 4

    def test_parashurama_path_index_8(self):
        """karma/parashurama maps to index 8."""
        assert EXPECTED_PATHS["karma/parashurama"] == 8

    def test_nrisimha_path_index_12(self):
        """moksha/nrisimha maps to index 12."""
        assert EXPECTED_PATHS["moksha/nrisimha"] == 12

    def test_yamaraja_path_index_15(self):
        """moksha/yamaraja maps to index 15."""
        assert EXPECTED_PATHS["moksha/yamaraja"] == 15


# =============================================================================
# WiringEnforcementProtocol Tests
# =============================================================================


class TestWiringEnforcementProtocol:
    """Test WiringEnforcementProtocol."""

    def test_protocol_is_runtime_checkable(self):
        """WiringEnforcementProtocol is runtime checkable."""
        # WiringEnforcer should satisfy the protocol
        assert isinstance(WiringEnforcer(Path(".")), WiringEnforcementProtocol)

    def test_protocol_has_validate_method(self):
        """Protocol defines validate method."""
        assert hasattr(WiringEnforcementProtocol, "validate")

    def test_protocol_has_is_wired_method(self):
        """Protocol defines is_wired method."""
        assert hasattr(WiringEnforcementProtocol, "is_wired")

    def test_protocol_has_get_violations_method(self):
        """Protocol defines get_violations method."""
        assert hasattr(WiringEnforcementProtocol, "get_violations")

    def test_protocol_has_get_expected_structure_method(self):
        """Protocol defines get_expected_structure method."""
        assert hasattr(WiringEnforcementProtocol, "get_expected_structure")


# =============================================================================
# WiringEnforcer Tests
# =============================================================================


class TestWiringEnforcerInit:
    """Test WiringEnforcer initialization."""

    def test_init_stores_path(self):
        """__init__ stores base path."""
        path = Path("/some/path")
        enforcer = WiringEnforcer(path)
        assert enforcer._base == path

    def test_init_empty_violations(self):
        """__init__ starts with empty violations."""
        enforcer = WiringEnforcer(Path("."))
        assert enforcer._violations == []

    def test_init_empty_wired_set(self):
        """__init__ starts with empty wired set."""
        enforcer = WiringEnforcer(Path("."))
        assert enforcer._wired == set()


class TestWiringEnforcerIsWired:
    """Test WiringEnforcer.is_wired method."""

    def test_is_wired_valid_path(self):
        """is_wired returns True for valid SSOT paths."""
        enforcer = WiringEnforcer(Path("."))
        assert enforcer.is_wired("genesis/vyasa") is True
        assert enforcer.is_wired("dharma/prithu") is True
        assert enforcer.is_wired("karma/parashurama") is True
        assert enforcer.is_wired("moksha/nrisimha") is True

    def test_is_wired_invalid_path(self):
        """is_wired returns False for invalid paths."""
        enforcer = WiringEnforcer(Path("."))
        assert enforcer.is_wired("invalid/path") is False
        assert enforcer.is_wired("genesis/invalid") is False
        assert enforcer.is_wired("") is False


class TestWiringEnforcerGetExpectedStructure:
    """Test WiringEnforcer.get_expected_structure method."""

    def test_get_expected_structure_returns_dict(self):
        """get_expected_structure returns dict."""
        enforcer = WiringEnforcer(Path("."))
        structure = enforcer.get_expected_structure()
        assert isinstance(structure, dict)

    def test_get_expected_structure_has_4_quarters(self):
        """get_expected_structure has 4 quarters."""
        enforcer = WiringEnforcer(Path("."))
        structure = enforcer.get_expected_structure()
        assert len(structure) == 4

    def test_get_expected_structure_matches_ssot(self):
        """get_expected_structure matches EXPECTED_POSITIONS."""
        enforcer = WiringEnforcer(Path("."))
        structure = enforcer.get_expected_structure()
        assert structure == EXPECTED_POSITIONS


class TestWiringEnforcerValidate:
    """Test WiringEnforcer.validate method."""

    def test_validate_empty_directory(self):
        """validate reports all missing for empty directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            enforcer = WiringEnforcer(Path(tmpdir))
            result = enforcer.validate()

            assert result["valid"] is False
            assert result["wired_count"] == 0
            assert result["missing_count"] > 0
            assert result["coverage"] == 0.0

    def test_validate_returns_validation_result(self):
        """validate returns ValidationResult TypedDict."""
        with tempfile.TemporaryDirectory() as tmpdir:
            enforcer = WiringEnforcer(Path(tmpdir))
            result = enforcer.validate()

            # Check all required keys exist
            assert "valid" in result
            assert "violations" in result
            assert "wired_count" in result
            assert "orphan_count" in result
            assert "missing_count" in result
            assert "coverage" in result

    def test_validate_missing_quarters(self):
        """validate detects missing quarters."""
        with tempfile.TemporaryDirectory() as tmpdir:
            enforcer = WiringEnforcer(Path(tmpdir))
            result = enforcer.validate()

            # Should have violations for missing quarters
            missing_folders = [
                v for v in result["violations"]
                if v["type"] == ViolationType.MISSING_FOLDER
            ]
            assert len(missing_folders) >= 4  # At least the 4 quarters

    def test_validate_detects_orphans(self):
        """validate detects orphan folders."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            # Create genesis quarter with orphan
            genesis_path = base / "genesis"
            genesis_path.mkdir()
            orphan_path = genesis_path / "orphan_folder"
            orphan_path.mkdir()

            enforcer = WiringEnforcer(base)
            result = enforcer.validate()

            orphans = [
                v for v in result["violations"]
                if v["type"] == ViolationType.ORPHAN_FOLDER
            ]
            assert len(orphans) >= 1
            assert result["orphan_count"] >= 1


class TestWiringEnforcerWithStructure:
    """Test WiringEnforcer with partial structure."""

    def test_validate_quarter_without_positions(self):
        """Quarter without positions reports missing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            # Create just the quarters, no positions
            for quarter in EXPECTED_QUARTERS:
                (base / quarter).mkdir()

            enforcer = WiringEnforcer(base)
            result = enforcer.validate()

            assert result["valid"] is False
            assert result["wired_count"] == 0
            # Should have missing folder violations for positions
            assert result["missing_count"] >= 16

    def test_validate_position_without_init(self):
        """Position without __init__.py reports missing declaration."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            # Create genesis/vyasa without __init__.py
            vyasa_path = base / "genesis" / "vyasa"
            vyasa_path.mkdir(parents=True)

            enforcer = WiringEnforcer(base)
            result = enforcer.validate()

            missing_decl = [
                v for v in result["violations"]
                if v["type"] == ViolationType.MISSING_DECLARATION
            ]
            assert len(missing_decl) >= 1

    def test_validate_correct_wiring(self):
        """Position with correct __init__.py is wired."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            # Create genesis/vyasa with correct declarations
            vyasa_path = base / "genesis" / "vyasa"
            vyasa_path.mkdir(parents=True)
            init_file = vyasa_path / "__init__.py"
            init_file.write_text('''
__mahajana__ = "vyasa"
__position__ = 0
''')

            enforcer = WiringEnforcer(base)
            result = enforcer.validate()

            # vyasa should be wired
            assert "genesis/vyasa" in enforcer._wired

    def test_validate_wrong_position_number(self):
        """Wrong __position__ reports violation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            # Create genesis/vyasa with wrong position
            vyasa_path = base / "genesis" / "vyasa"
            vyasa_path.mkdir(parents=True)
            init_file = vyasa_path / "__init__.py"
            init_file.write_text('''
__mahajana__ = "vyasa"
__position__ = 99
''')

            enforcer = WiringEnforcer(base)
            result = enforcer.validate()

            wrong_pos = [
                v for v in result["violations"]
                if v["type"] == ViolationType.WRONG_POSITION
            ]
            assert len(wrong_pos) >= 1

    def test_validate_wrong_mahajana_name(self):
        """Wrong __mahajana__ reports violation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            # Create genesis/vyasa with wrong name
            vyasa_path = base / "genesis" / "vyasa"
            vyasa_path.mkdir(parents=True)
            init_file = vyasa_path / "__init__.py"
            init_file.write_text('''
__mahajana__ = "wrong_name"
__position__ = 0
''')

            enforcer = WiringEnforcer(base)
            result = enforcer.validate()

            missing_decl = [
                v for v in result["violations"]
                if v["type"] == ViolationType.MISSING_DECLARATION
            ]
            assert len(missing_decl) >= 1


class TestWiringEnforcerGetViolations:
    """Test WiringEnforcer.get_violations method."""

    def test_get_violations_empty_before_validate(self):
        """get_violations returns empty list before validate."""
        enforcer = WiringEnforcer(Path("."))
        assert enforcer.get_violations() == []

    def test_get_violations_after_validate(self):
        """get_violations returns violations after validate."""
        with tempfile.TemporaryDirectory() as tmpdir:
            enforcer = WiringEnforcer(Path(tmpdir))
            enforcer.validate()
            violations = enforcer.get_violations()
            assert len(violations) > 0


class TestWiringEnforcerCoverage:
    """Test WiringEnforcer coverage calculation."""

    def test_coverage_zero_for_empty(self):
        """Coverage is 0 for empty structure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            enforcer = WiringEnforcer(Path(tmpdir))
            result = enforcer.validate()
            assert result["coverage"] == 0.0

    def test_coverage_calculation(self):
        """Coverage is wired_count / 16."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            # Create one correctly wired position
            vyasa_path = base / "genesis" / "vyasa"
            vyasa_path.mkdir(parents=True)
            init_file = vyasa_path / "__init__.py"
            init_file.write_text('''
__mahajana__ = "vyasa"
__position__ = 0
''')

            enforcer = WiringEnforcer(base)
            result = enforcer.validate()

            assert result["wired_count"] == 1
            assert result["coverage"] == 1.0 / 16.0


# =============================================================================
# enforce_wiring Convenience Function Tests
# =============================================================================


class TestEnforceWiring:
    """Test enforce_wiring convenience function."""

    def test_enforce_wiring_returns_validation_result(self):
        """enforce_wiring returns ValidationResult."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = enforce_wiring(Path(tmpdir))

            assert "valid" in result
            assert "violations" in result
            assert "coverage" in result

    def test_enforce_wiring_empty_is_invalid(self):
        """enforce_wiring reports invalid for empty."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = enforce_wiring(Path(tmpdir))
            assert result["valid"] is False

    def test_enforce_wiring_equivalent_to_class(self):
        """enforce_wiring is equivalent to WiringEnforcer().validate()."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create some structure
            base = Path(tmpdir)
            (base / "genesis").mkdir()

            result1 = enforce_wiring(base)

            enforcer = WiringEnforcer(base)
            result2 = enforcer.validate()

            assert result1["valid"] == result2["valid"]
            assert result1["wired_count"] == result2["wired_count"]
            assert result1["coverage"] == result2["coverage"]


# =============================================================================
# Integration Tests
# =============================================================================


class TestWiringIntegration:
    """Integration tests for wiring protocol."""

    def test_full_valid_structure(self):
        """Full valid structure passes validation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)

            # Create all 16 positions correctly
            for path, index in EXPECTED_PATHS.items():
                quarter, guardian = path.split("/")
                pos_path = base / quarter / guardian
                pos_path.mkdir(parents=True)
                init_file = pos_path / "__init__.py"
                init_file.write_text(f'''
__mahajana__ = "{guardian}"
__position__ = {index}
''')

            result = enforce_wiring(base)

            assert result["valid"] is True
            assert result["wired_count"] == 16
            assert result["coverage"] == 1.0
            assert result["orphan_count"] == 0
            assert result["missing_count"] == 0

    def test_underscore_folders_ignored(self):
        """Folders starting with _ are ignored (not orphans)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            # Create quarter with underscore folder
            genesis_path = base / "genesis"
            genesis_path.mkdir()
            pycache_path = genesis_path / "__pycache__"
            pycache_path.mkdir()

            enforcer = WiringEnforcer(base)
            result = enforcer.validate()

            # __pycache__ should NOT be reported as orphan
            orphans = [
                v for v in result["violations"]
                if v["type"] == ViolationType.ORPHAN_FOLDER and "__pycache__" in v["path"]
            ]
            assert len(orphans) == 0

    def test_files_not_counted_as_orphans(self):
        """Regular files are not counted as orphan folders."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            # Create quarter with regular file
            genesis_path = base / "genesis"
            genesis_path.mkdir()
            some_file = genesis_path / "some_file.py"
            some_file.write_text("# not a folder")

            enforcer = WiringEnforcer(base)
            result = enforcer.validate()

            # File should NOT be reported as orphan folder
            orphans = [
                v for v in result["violations"]
                if v["type"] == ViolationType.ORPHAN_FOLDER and "some_file" in v["path"]
            ]
            assert len(orphans) == 0

    def test_single_quote_mahajana_accepted(self):
        """__mahajana__ with single quotes is accepted."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            vyasa_path = base / "genesis" / "vyasa"
            vyasa_path.mkdir(parents=True)
            init_file = vyasa_path / "__init__.py"
            init_file.write_text("""
__mahajana__ = 'vyasa'
__position__ = 0
""")

            enforcer = WiringEnforcer(base)
            result = enforcer.validate()

            # Should be wired (single quotes accepted)
            assert "genesis/vyasa" in enforcer._wired


# =============================================================================
# Module Exports Test
# =============================================================================


class TestModuleExports:
    """Test module exports."""

    def test_all_types_exported(self):
        """All types are in __all__."""
        from vibe_core.mahamantra.substrate import wiring_protocol
        assert "ViolationType" in wiring_protocol.__all__
        assert "Violation" in wiring_protocol.__all__
        assert "ValidationResult" in wiring_protocol.__all__

    def test_ssot_expectations_exported(self):
        """SSOT expectations are exported."""
        from vibe_core.mahamantra.substrate import wiring_protocol
        assert "EXPECTED_QUARTERS" in wiring_protocol.__all__
        assert "EXPECTED_POSITIONS" in wiring_protocol.__all__
        assert "EXPECTED_PATHS" in wiring_protocol.__all__

    def test_protocol_exported(self):
        """Protocol is exported."""
        from vibe_core.mahamantra.substrate import wiring_protocol
        assert "WiringEnforcementProtocol" in wiring_protocol.__all__

    def test_implementation_exported(self):
        """Implementation is exported."""
        from vibe_core.mahamantra.substrate import wiring_protocol
        assert "WiringEnforcer" in wiring_protocol.__all__

    def test_convenience_exported(self):
        """Convenience function is exported."""
        from vibe_core.mahamantra.substrate import wiring_protocol
        assert "enforce_wiring" in wiring_protocol.__all__
