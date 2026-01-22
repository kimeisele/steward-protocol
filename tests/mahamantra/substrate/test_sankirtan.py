"""
TESTS: sankirtan.py - Mass DNA Injection System
===============================================

"harer nama harer nama harer namaiva kevalam"

REAL TESTS for:
1. FOLDER_MAHAJANA_MAP constant
2. SKIP_PATTERNS constant
3. get_mahajana_for_path function
4. has_declaration function
5. inject_declaration function
6. compute_genesis_hash function
7. PhaseResult, PipelineContext dataclasses
8. InjectionResult, SankirtanResult dataclasses
"""

import pytest
from pathlib import Path
from vibe_core.mahamantra.substrate.sankirtan import (
    # Constants
    FOLDER_MAHAJANA_MAP,
    SKIP_PATTERNS,
    SCAN_DIRECTORIES,
    DNA_TEMPLATE,
    # Functions
    get_mahajana_for_path,
    has_declaration,
    inject_declaration,
    compute_genesis_hash,
    inject_file,
    # Dataclasses
    PhaseResult,
    PipelineContext,
    InjectionResult,
    SankirtanResult,
)
from vibe_core.mahamantra.substrate.mahajana import Quarter


# =============================================================================
# FOLDER_MAHAJANA_MAP Tests
# =============================================================================


class TestFolderMahajanaMap:
    """Test FOLDER_MAHAJANA_MAP constant."""

    def test_folder_mahajana_map_exists(self):
        """FOLDER_MAHAJANA_MAP exists."""
        assert FOLDER_MAHAJANA_MAP is not None

    def test_folder_mahajana_map_is_dict(self):
        """FOLDER_MAHAJANA_MAP is a dict."""
        assert isinstance(FOLDER_MAHAJANA_MAP, dict)

    def test_folder_mahajana_map_has_runtime(self):
        """FOLDER_MAHAJANA_MAP has runtime -> brahma."""
        assert "runtime" in FOLDER_MAHAJANA_MAP
        assert FOLDER_MAHAJANA_MAP["runtime"] == "brahma"

    def test_folder_mahajana_map_has_protocols(self):
        """FOLDER_MAHAJANA_MAP has protocols -> vyasa."""
        assert "protocols" in FOLDER_MAHAJANA_MAP
        assert FOLDER_MAHAJANA_MAP["protocols"] == "vyasa"

    def test_folder_mahajana_map_has_services(self):
        """FOLDER_MAHAJANA_MAP has services -> janaka."""
        assert "services" in FOLDER_MAHAJANA_MAP
        assert FOLDER_MAHAJANA_MAP["services"] == "janaka"

    def test_folder_mahajana_map_has_naga(self):
        """FOLDER_MAHAJANA_MAP has naga -> yamaraja."""
        assert "naga" in FOLDER_MAHAJANA_MAP
        assert FOLDER_MAHAJANA_MAP["naga"] == "yamaraja"


# =============================================================================
# SKIP_PATTERNS Tests
# =============================================================================


class TestSkipPatterns:
    """Test SKIP_PATTERNS constant."""

    def test_skip_patterns_exists(self):
        """SKIP_PATTERNS exists."""
        assert SKIP_PATTERNS is not None

    def test_skip_patterns_is_tuple(self):
        """SKIP_PATTERNS is a tuple."""
        assert isinstance(SKIP_PATTERNS, tuple)

    def test_skip_patterns_has_pycache(self):
        """SKIP_PATTERNS has __pycache__."""
        assert "__pycache__" in SKIP_PATTERNS

    def test_skip_patterns_has_test_(self):
        """SKIP_PATTERNS has test_."""
        assert "test_" in SKIP_PATTERNS


# =============================================================================
# SCAN_DIRECTORIES Tests
# =============================================================================


class TestScanDirectories:
    """Test SCAN_DIRECTORIES constant."""

    def test_scan_directories_exists(self):
        """SCAN_DIRECTORIES exists."""
        assert SCAN_DIRECTORIES is not None

    def test_scan_directories_is_tuple(self):
        """SCAN_DIRECTORIES is a tuple."""
        assert isinstance(SCAN_DIRECTORIES, tuple)

    def test_scan_directories_derived_from_map(self):
        """SCAN_DIRECTORIES derived from FOLDER_MAHAJANA_MAP."""
        # Top-level directories from map should be in SCAN_DIRECTORIES
        for folder in list(FOLDER_MAHAJANA_MAP.keys())[:5]:
            top_level = folder.split("/")[0]
            if top_level != "mahajanas":
                assert top_level in SCAN_DIRECTORIES


# =============================================================================
# get_mahajana_for_path Tests
# =============================================================================


class TestGetMahajanaForPath:
    """Test get_mahajana_for_path function."""

    def test_get_mahajana_for_path_returns_tuple(self):
        """get_mahajana_for_path returns tuple of (name, position)."""
        result = get_mahajana_for_path(Path("vibe_core/services/test.py"))
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_get_mahajana_for_services(self):
        """services folder maps to janaka."""
        result = get_mahajana_for_path(Path("vibe_core/services/some_service.py"))
        assert result is not None
        name, position = result
        assert name == "janaka"

    def test_get_mahajana_for_protocols(self):
        """protocols folder maps to vyasa."""
        result = get_mahajana_for_path(Path("vibe_core/protocols/some_proto.py"))
        assert result is not None
        name, position = result
        assert name == "vyasa"

    def test_get_mahajana_for_naga(self):
        """naga folder maps to yamaraja."""
        result = get_mahajana_for_path(Path("vibe_core/naga/security.py"))
        assert result is not None
        name, position = result
        assert name == "yamaraja"

    def test_get_mahajana_auto_detect_guardian_name(self):
        """Auto-detects guardian name in path."""
        result = get_mahajana_for_path(Path("something/vyasa/module.py"))
        assert result is not None
        name, position = result
        assert name == "vyasa"

    def test_get_mahajana_hash_fallback(self):
        """Unknown paths fall back to hash-based assignment."""
        result = get_mahajana_for_path(Path("unknown/random/path.py"))
        assert result is not None
        name, position = result
        assert isinstance(name, str)
        assert 0 <= position < 16


# =============================================================================
# has_declaration Tests
# =============================================================================


class TestHasDeclaration:
    """Test has_declaration function."""

    def test_has_declaration_true(self):
        """Returns True when __mahajana__ present."""
        content = '''"""Module."""
__mahajana__ = "vyasa"
'''
        assert has_declaration(content) is True

    def test_has_declaration_false(self):
        """Returns False when __mahajana__ absent."""
        content = '''"""Module without declaration."""
def foo():
    pass
'''
        assert has_declaration(content) is False

    def test_has_declaration_empty(self):
        """Returns False for empty content."""
        assert has_declaration("") is False


# =============================================================================
# inject_declaration Tests
# =============================================================================


class TestInjectDeclaration:
    """Test inject_declaration function."""

    def test_inject_declaration_basic(self):
        """Injects declaration into content."""
        content = '''"""Module docstring."""
def foo():
    pass
'''
        result = inject_declaration(content, "vyasa", 4)
        assert "__mahajana__" in result
        assert '"vyasa"' in result
        assert "__position__ = 4" in result

    def test_inject_declaration_has_genesis(self):
        """Injected declaration has __genesis__."""
        content = '''"""Module."""
'''
        result = inject_declaration(content, "brahma", 1)
        assert "__genesis__" in result

    def test_inject_declaration_after_docstring(self):
        """Injection happens after docstring."""
        content = '''"""First line.
Second line.
"""
def foo():
    pass
'''
        result = inject_declaration(content, "narada", 2)
        lines = result.split("\n")
        # Find __mahajana__ line
        maha_line_idx = None
        for i, line in enumerate(lines):
            if "__mahajana__" in line:
                maha_line_idx = i
                break
        assert maha_line_idx is not None
        # Should be after docstring (which ends at line ~3)
        assert maha_line_idx > 2

    def test_inject_declaration_after_future_imports(self):
        """Injection happens after from __future__ imports."""
        content = '''"""Docstring."""
from __future__ import annotations

def foo():
    pass
'''
        result = inject_declaration(content, "shambhu", 3)
        lines = result.split("\n")
        future_idx = None
        maha_idx = None
        for i, line in enumerate(lines):
            if "from __future__" in line:
                future_idx = i
            if "__mahajana__" in line:
                maha_idx = i
        assert future_idx is not None
        assert maha_idx is not None
        assert maha_idx > future_idx


# =============================================================================
# compute_genesis_hash Tests
# =============================================================================


class TestComputeGenesisHash:
    """Test compute_genesis_hash function."""

    def test_compute_genesis_hash_returns_hex(self):
        """compute_genesis_hash returns hex string."""
        result = compute_genesis_hash("vyasa", 4, "test.py")
        assert result.startswith("0x")

    def test_compute_genesis_hash_divisible_by_37(self):
        """Result is divisible by 37."""
        result = compute_genesis_hash("brahma", 1, "module.py")
        value = int(result, 16)
        assert value % 37 == 0

    def test_compute_genesis_hash_deterministic(self):
        """Same inputs produce same hash."""
        hash1 = compute_genesis_hash("narada", 2, "file.py")
        hash2 = compute_genesis_hash("narada", 2, "file.py")
        assert hash1 == hash2

    def test_compute_genesis_hash_different_inputs(self):
        """Different inputs produce different hashes."""
        hash1 = compute_genesis_hash("vyasa", 4, "file1.py")
        hash2 = compute_genesis_hash("vyasa", 4, "file2.py")
        assert hash1 != hash2


# =============================================================================
# PhaseResult Tests
# =============================================================================


class TestPhaseResult:
    """Test PhaseResult dataclass."""

    def test_phase_result_creation(self):
        """PhaseResult can be created."""
        result = PhaseResult(
            phase=Quarter.GENESIS,
            success=True,
            message="Test message",
        )
        assert result.phase == Quarter.GENESIS
        assert result.success is True
        assert result.message == "Test message"

    def test_phase_result_with_data(self):
        """PhaseResult can have data."""
        result = PhaseResult(
            phase=Quarter.DHARMA,
            success=True,
            message="OK",
            data={"key": "value"},
        )
        assert result.data == {"key": "value"}


# =============================================================================
# PipelineContext Tests
# =============================================================================


class TestPipelineContext:
    """Test PipelineContext dataclass."""

    def test_pipeline_context_creation(self):
        """PipelineContext can be created."""
        ctx = PipelineContext(file_path=Path("test.py"))
        assert ctx.file_path == Path("test.py")
        assert ctx.content is None
        assert ctx.is_valid is True

    def test_pipeline_context_log_phase(self):
        """log_phase adds PhaseResult."""
        ctx = PipelineContext(file_path=Path("test.py"))
        ctx.log_phase(Quarter.GENESIS, True, "Loaded")
        assert len(ctx.phases) == 1
        assert ctx.phases[0].phase == Quarter.GENESIS

    def test_pipeline_context_all_phases_ok(self):
        """all_phases_ok returns True when all succeed."""
        ctx = PipelineContext(file_path=Path("test.py"))
        ctx.log_phase(Quarter.GENESIS, True, "OK")
        ctx.log_phase(Quarter.DHARMA, True, "OK")
        assert ctx.all_phases_ok is True

    def test_pipeline_context_all_phases_ok_false(self):
        """all_phases_ok returns False when any fails."""
        ctx = PipelineContext(file_path=Path("test.py"))
        ctx.log_phase(Quarter.GENESIS, True, "OK")
        ctx.log_phase(Quarter.DHARMA, False, "Failed")
        assert ctx.all_phases_ok is False

    def test_pipeline_context_last_phase(self):
        """last_phase returns last executed phase."""
        ctx = PipelineContext(file_path=Path("test.py"))
        ctx.log_phase(Quarter.GENESIS, True, "OK")
        ctx.log_phase(Quarter.DHARMA, True, "OK")
        assert ctx.last_phase == Quarter.DHARMA

    def test_pipeline_context_last_phase_none(self):
        """last_phase returns None when no phases."""
        ctx = PipelineContext(file_path=Path("test.py"))
        assert ctx.last_phase is None


# =============================================================================
# InjectionResult Tests
# =============================================================================


class TestInjectionResult:
    """Test InjectionResult dataclass."""

    def test_injection_result_creation(self):
        """InjectionResult can be created."""
        result = InjectionResult(
            file_path="test.py",
            mahajana="vyasa",
            position=4,
            success=True,
            was_dry_run=True,
            message="Injected",
        )
        assert result.file_path == "test.py"
        assert result.mahajana == "vyasa"
        assert result.success is True


# =============================================================================
# SankirtanResult Tests
# =============================================================================


class TestSankirtanResult:
    """Test SankirtanResult dataclass."""

    def test_sankirtan_result_default_creation(self):
        """SankirtanResult has default values."""
        result = SankirtanResult()
        assert result.files_scanned == 0
        assert result.files_injected == 0
        assert result.files_skipped == 0
        assert result.was_dry_run is True

    def test_sankirtan_result_tracking(self):
        """SankirtanResult tracks injections."""
        result = SankirtanResult()
        result.files_scanned = 10
        result.files_injected = 5
        result.by_mahajana["vyasa"] = 3
        result.by_mahajana["brahma"] = 2
        assert result.files_scanned == 10
        assert result.by_mahajana["vyasa"] == 3


# =============================================================================
# DNA_TEMPLATE Tests
# =============================================================================


class TestDNATemplate:
    """Test DNA_TEMPLATE constant."""

    def test_dna_template_exists(self):
        """DNA_TEMPLATE exists."""
        assert DNA_TEMPLATE is not None

    def test_dna_template_has_mahajana_placeholder(self):
        """DNA_TEMPLATE has {mahajana} placeholder."""
        assert "{mahajana}" in DNA_TEMPLATE

    def test_dna_template_has_position_placeholder(self):
        """DNA_TEMPLATE has {position} placeholder."""
        assert "{position}" in DNA_TEMPLATE

    def test_dna_template_has_genesis_placeholder(self):
        """DNA_TEMPLATE has {genesis_hash} placeholder."""
        assert "{genesis_hash}" in DNA_TEMPLATE


# =============================================================================
# Module Exports Tests
# =============================================================================


class TestModuleExports:
    """Test module exports."""

    def test_all_exports(self):
        """All expected items are in __all__."""
        from vibe_core.mahamantra.substrate import sankirtan
        expected = [
            "get_mahajana_for_path",
            "has_declaration",
            "inject_declaration",
            "inject_file",
            "perform_sankirtan",
            "InjectionResult",
            "SankirtanResult",
            "FOLDER_MAHAJANA_MAP",
        ]
        for item in expected:
            assert item in sankirtan.__all__, f"{item} should be in __all__"
