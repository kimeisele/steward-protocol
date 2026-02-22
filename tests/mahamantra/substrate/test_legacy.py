"""
TESTS: _legacy.py - Legacy Bridge (Balarama Pattern)
====================================================

"Opfern (Wrappen): Lade das fremde System durch den Balarama Proxy."

REAL TESTS for:
1. Re-exported scanner types
2. Re-exported samskara types
3. Re-exported tattva types
4. Module exports
"""

import pytest
from vibe_core.mahamantra.substrate._legacy import (
    # Scanner re-exports
    Declaration,
    DeclarationType,
    FileStatus,
    ScanConfig,
    ScannedFile,
    ScannerProtocol,
    ScanProgress,
    ScanResult,
    extract_declarations,
    get_default_config,
    path_to_module,
    # Samskara re-exports
    Phase,
    PhaseStatus,
    PipelineExecutor,
    SamskaraProtocol,
    PipelineContext,
    # Tattva re-exports
    LEGACY_PURUSHOTTAMA,
)


# =============================================================================
# Scanner Re-exports Tests
# =============================================================================


class TestScannerReexports:
    """Test scanner type re-exports."""

    def test_declaration_type_exists(self):
        """DeclarationType exists."""
        assert DeclarationType is not None

    def test_declaration_exists(self):
        """Declaration exists."""
        assert Declaration is not None

    def test_file_status_exists(self):
        """FileStatus exists."""
        assert FileStatus is not None

    def test_scan_config_exists(self):
        """ScanConfig exists."""
        assert ScanConfig is not None

    def test_scanned_file_exists(self):
        """ScannedFile exists."""
        assert ScannedFile is not None

    def test_scanner_protocol_exists(self):
        """ScannerProtocol exists."""
        assert ScannerProtocol is not None

    def test_scan_progress_exists(self):
        """ScanProgress exists."""
        assert ScanProgress is not None

    def test_scan_result_exists(self):
        """ScanResult exists."""
        assert ScanResult is not None

    def test_extract_declarations_exists(self):
        """extract_declarations function exists."""
        assert extract_declarations is not None
        assert callable(extract_declarations)

    def test_get_default_config_exists(self):
        """get_default_config function exists."""
        assert get_default_config is not None
        assert callable(get_default_config)

    def test_path_to_module_exists(self):
        """path_to_module function exists."""
        assert path_to_module is not None
        assert callable(path_to_module)


# =============================================================================
# Samskara Re-exports Tests
# =============================================================================


class TestSamskaraReexports:
    """Test samskara type re-exports."""

    def test_phase_exists(self):
        """Phase exists."""
        assert Phase is not None

    def test_phase_status_exists(self):
        """PhaseStatus exists."""
        assert PhaseStatus is not None

    def test_pipeline_executor_exists(self):
        """PipelineExecutor exists."""
        assert PipelineExecutor is not None

    def test_samskara_protocol_exists(self):
        """SamskaraProtocol exists."""
        assert SamskaraProtocol is not None

    def test_pipeline_context_exists(self):
        """PipelineContext exists."""
        assert PipelineContext is not None


# =============================================================================
# Tattva Re-exports Tests
# =============================================================================


class TestTattvaReexports:
    """Test tattva type re-exports."""

    def test_legacy_purushottama_exists(self):
        """LEGACY_PURUSHOTTAMA exists."""
        assert LEGACY_PURUSHOTTAMA is not None


# =============================================================================
# DeclarationType Enum Tests
# =============================================================================


class TestDeclarationType:
    """Test DeclarationType enum."""

    def test_declaration_type_is_enum(self):
        """DeclarationType is an Enum."""
        from enum import Enum

        assert issubclass(DeclarationType, Enum)

    def test_declaration_type_has_mahajana(self):
        """DeclarationType has MAHAJANA."""
        assert hasattr(DeclarationType, "MAHAJANA")

    def test_declaration_type_has_position(self):
        """DeclarationType has POSITION."""
        assert hasattr(DeclarationType, "POSITION")


# =============================================================================
# FileStatus Enum Tests
# =============================================================================


class TestFileStatus:
    """Test FileStatus enum."""

    def test_file_status_is_enum(self):
        """FileStatus is an Enum."""
        from enum import Enum

        assert issubclass(FileStatus, Enum)


# =============================================================================
# Phase Enum Tests
# =============================================================================


class TestPhase:
    """Test Phase enum."""

    def test_phase_has_genesis(self):
        """Phase has GENESIS."""
        assert hasattr(Phase, "GENESIS")

    def test_phase_has_dharma(self):
        """Phase has DHARMA."""
        assert hasattr(Phase, "DHARMA")

    def test_phase_has_karma(self):
        """Phase has KARMA."""
        assert hasattr(Phase, "KARMA")

    def test_phase_has_moksha(self):
        """Phase has MOKSHA."""
        assert hasattr(Phase, "MOKSHA")


# =============================================================================
# PhaseStatus Enum Tests
# =============================================================================


class TestPhaseStatus:
    """Test PhaseStatus enum."""

    def test_phase_status_has_pending(self):
        """PhaseStatus has PENDING."""
        assert hasattr(PhaseStatus, "PENDING")

    def test_phase_status_has_success(self):
        """PhaseStatus has SUCCESS."""
        assert hasattr(PhaseStatus, "SUCCESS")


# =============================================================================
# get_default_config Function Tests
# =============================================================================


class TestGetDefaultConfig:
    """Test get_default_config function."""

    def test_get_default_config_returns_dict(self):
        """get_default_config returns dict (ScanConfig TypedDict)."""
        config = get_default_config()
        assert isinstance(config, dict)
        assert "base_path" in config
        assert "include_dirs" in config


# =============================================================================
# path_to_module Function Tests
# =============================================================================


class TestPathToModule:
    """Test path_to_module function."""

    def test_path_to_module_basic(self):
        """path_to_module converts path to module name."""
        from pathlib import Path

        # path_to_module requires (file_path, base_path)
        module_name = path_to_module(Path("vibe_core/mahamantra/substrate/seed.py"), Path("."))
        assert "." in module_name  # Should be dotted module path
        assert ".py" not in module_name  # Should not have .py extension


# =============================================================================
# Module Attributes Tests
# =============================================================================


class TestModuleAttributes:
    """Test module-level attributes."""

    def test_mahajana_declaration(self):
        """Module has __mahajana__ declaration."""
        from vibe_core.mahamantra.substrate import _legacy

        assert hasattr(_legacy, "__mahajana__")
        assert _legacy.__mahajana__ == "nityananda"

    def test_position_declaration(self):
        """Module has __position__ declaration."""
        from vibe_core.mahamantra.substrate import _legacy

        assert hasattr(_legacy, "__position__")
        assert _legacy.__position__ == 1

    def test_genesis_declaration(self):
        """Module has __genesis__ declaration."""
        from vibe_core.mahamantra.substrate import _legacy

        assert hasattr(_legacy, "__genesis__")
        assert _legacy.__genesis__.startswith("0x")


# =============================================================================
# Module Exports Tests
# =============================================================================


class TestModuleExports:
    """Test module exports."""

    def test_all_exports(self):
        """All expected items are in __all__."""
        from vibe_core.mahamantra.substrate import _legacy

        expected = [
            # Scanner
            "Declaration",
            "DeclarationType",
            "FileStatus",
            "ScanConfig",
            "ScannedFile",
            "ScannerProtocol",
            "ScanProgress",
            "ScanResult",
            "extract_declarations",
            "get_default_config",
            "path_to_module",
            # Samskara
            "Phase",
            "PhaseStatus",
            "PipelineExecutor",
            "SamskaraProtocol",
            "PipelineContext",
            # Tattva
            "LEGACY_PURUSHOTTAMA",
        ]
        for item in expected:
            assert item in _legacy.__all__, f"{item} should be in __all__"

    def test_export_count_matches_all(self):
        """Number of exports matches __all__ length."""
        from vibe_core.mahamantra.substrate import _legacy

        assert len(_legacy.__all__) == 17  # Total expected exports
