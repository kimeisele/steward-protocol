"""
Tests for Sravanam — Fractal Cell Scanner.

Tests the atomic scan_cell() path and the SravanamScanner/Listener.
"""

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from vibe_core.mahamantra.dharma.kumaras.engine import ShuddhiEngine
from vibe_core.mahamantra.dharma.kumaras.sravanam import (
    GUARDIAN_RULE_MAP,
    SravanamListener,
    SravanamReport,
    SravanamScanner,
)
from vibe_core.mahamantra.substrate.shuddhi import ShuddhiStatus


# =============================================================================
# scan_cell() — Atomic Scan Unit Tests
# =============================================================================


class TestScanCell:
    """Tests for ShuddhiEngine.scan_cell()."""

    def setup_method(self):
        self.engine = ShuddhiEngine()

    def test_scan_cell_finds_any_type_usage(self):
        """scan_cell detects unused Any import."""
        source = "import logging\nfrom typing import Any\n\nlogger = logging.getLogger(__name__)\n"
        result = self.engine.scan_cell(source, "any_type_usage")
        assert result is not None
        assert result.status == ShuddhiStatus.PURIFIED
        assert result.rule_id == "any_type_usage"
        assert "Any" in result.diff

    def test_scan_cell_clean_source_returns_none(self):
        """scan_cell returns None for clean source."""
        source = "import logging\n\nlogger = logging.getLogger(__name__)\n"
        result = self.engine.scan_cell(source, "any_type_usage")
        assert result is None

    def test_scan_cell_unknown_rule_returns_none(self):
        """scan_cell returns None for unknown rule_id."""
        source = "x = 1\n"
        result = self.engine.scan_cell(source, "nonexistent_rule_xyz")
        assert result is None

    def test_scan_cell_invalid_syntax_returns_none(self):
        """scan_cell returns None for unparseable source."""
        source = "def foo(:\n  pass\n"
        result = self.engine.scan_cell(source, "any_type_usage")
        assert result is None

    def test_scan_cell_with_file_path(self):
        """scan_cell uses provided file_path in result."""
        source = "from typing import Any\nx = 1\n"
        path = Path("/fake/test.py")
        result = self.engine.scan_cell(source, "any_type_usage", file_path=path)
        assert result is not None
        assert result.file_path == path

    def test_scan_cell_purified_code_compiles(self):
        """scan_cell only returns results where purified code compiles."""
        source = "from typing import Any\nx = 1\n"
        result = self.engine.scan_cell(source, "any_type_usage")
        assert result is not None
        # Purified code must compile
        compile(result.purified_code, "<test>", "exec")


# =============================================================================
# SravanamScanner Tests
# =============================================================================


class TestSravanamScanner:
    """Tests for SravanamScanner."""

    def test_scanner_creates_engine_lazily(self):
        """Engine is not created until accessed."""
        scanner = SravanamScanner()
        assert scanner._engine is None
        _ = scanner.engine
        assert scanner._engine is not None

    def test_scanner_stats_start_at_zero(self):
        """Stats are zero initially."""
        scanner = SravanamScanner()
        assert scanner.stats == {"total_scanned": 0, "total_violations": 0}


# =============================================================================
# GUARDIAN_RULE_MAP Tests
# =============================================================================


class TestGuardianRuleMap:
    """Tests for the Guardian → Rule mapping."""

    def test_all_16_guardians_mapped(self):
        """All 16 guardians have rule mappings."""
        assert len(GUARDIAN_RULE_MAP) == 16

    def test_kumaras_maps_to_fractal_routing(self):
        """Kumaras (position 5) maps to missing_fractal_routing."""
        assert "missing_fractal_routing" in GUARDIAN_RULE_MAP["kumaras"]

    def test_narada_maps_to_silent_failure(self):
        """Narada (position 2) maps to silent_failure."""
        assert "silent_failure" in GUARDIAN_RULE_MAP["narada"]

    def test_vyasa_maps_to_identity_rules(self):
        """Vyasa (position 0) maps to identity rules."""
        assert "missing_mahajana" in GUARDIAN_RULE_MAP["vyasa"]
        assert "broken_genesis" in GUARDIAN_RULE_MAP["vyasa"]

    def test_all_rules_are_valid(self):
        """Every rule in the map is a registered remedy."""
        engine = ShuddhiEngine()
        valid_rules = set(engine.list_remedies())
        for guardian, rules in GUARDIAN_RULE_MAP.items():
            for rule in rules:
                assert rule in valid_rules, f"{guardian} has invalid rule: {rule}"


# =============================================================================
# SravanamListener Tests
# =============================================================================


class TestSravanamListener:
    """Tests for SravanamListener."""

    def test_listener_is_callable(self):
        """Listener is callable (can be used as tick callback)."""
        listener = SravanamListener()
        assert callable(listener)

    def test_listener_disabled_skips_scan(self):
        """Disabled listener doesn't scan."""
        listener = SravanamListener()
        listener.disable()
        tick_state = MagicMock(position=5)
        listener(tick_state)
        assert listener.total_violations == 0

    def test_listener_enable_disable(self):
        """Enable/disable works."""
        listener = SravanamListener()
        assert listener._enabled is True
        listener.disable()
        assert listener._enabled is False
        listener.enable()
        assert listener._enabled is True

    def test_listener_handles_missing_position(self):
        """Listener handles tick_state without position gracefully."""
        listener = SravanamListener()
        tick_state = MagicMock(spec=[])  # No position attribute
        listener(tick_state)  # Should not raise
        assert listener.total_violations == 0


# =============================================================================
# SravanamReport Tests
# =============================================================================


class TestSravanamReport:
    """Tests for SravanamReport dataclass."""

    def test_report_creation(self):
        """Report can be created with required fields."""
        report = SravanamReport(
            position=5,
            guardian="kumaras",
            cells_scanned=1,
            violations_found=0,
        )
        assert report.position == 5
        assert report.guardian == "kumaras"
        assert report.results == []

    def test_report_frozen(self):
        """Report is frozen (immutable)."""
        report = SravanamReport(
            position=0, guardian="vyasa", cells_scanned=0, violations_found=0
        )
        with pytest.raises(AttributeError):
            report.position = 1
