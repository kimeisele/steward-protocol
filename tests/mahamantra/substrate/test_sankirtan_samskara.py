"""
Tests for SankirtanSamskara - Protocol-based DNA Injection Pipeline.

Tests verify:
1. SankirtanSamskara implements SamskaraProtocol
2. FilePayload dataclass
3. 4-Phase pipeline execution
4. Already-owned file handling (Kali Yuga Grace)
5. Non-Python file handling
6. Integration with PipelineExecutor
"""

import pytest
import tempfile
from pathlib import Path
from typing import Optional

from vibe_core.mahamantra.substrate.sankirtan import (
    SankirtanSamskara,
    FilePayload,
    InjectionResult,
    has_declaration,
    get_mahajana_for_path,
    FOLDER_MAHAJANA_MAP,
)
from vibe_core.protocols.substrate.samskara import (
    SamskaraProtocol,
    PipelineExecutor,
    Phase,
    PhaseStatus,
    PipelineContext,
)


class TestFilePayload:
    """Test FilePayload dataclass."""

    def test_create_payload(self):
        """Should create payload with path."""
        path = Path("/tmp/test.py")
        payload = FilePayload(file_path=path)

        assert payload.file_path == path
        assert payload.content is None
        assert payload.mahajana is None
        assert payload.position is None
        assert payload.was_already_owned is False

    def test_payload_with_content(self):
        """Should store content when provided."""
        payload = FilePayload(
            file_path=Path("/tmp/test.py"),
            content="print('hello')",
            mahajana="brahma",
            position=1,
        )

        assert payload.content == "print('hello')"
        assert payload.mahajana == "brahma"
        assert payload.position == 1


class TestSankirtanSamskaraProtocolCompliance:
    """Test that SankirtanSamskara implements SamskaraProtocol."""

    def test_has_all_methods(self):
        """Should have genesis, dharma, karma, moksha methods."""
        samskara = SankirtanSamskara(dry_run=True)

        assert hasattr(samskara, "genesis")
        assert hasattr(samskara, "dharma")
        assert hasattr(samskara, "karma")
        assert hasattr(samskara, "moksha")

        assert callable(samskara.genesis)
        assert callable(samskara.dharma)
        assert callable(samskara.karma)
        assert callable(samskara.moksha)

    def test_isinstance_check(self):
        """Should pass isinstance check for SamskaraProtocol."""
        samskara = SankirtanSamskara(dry_run=True)
        assert isinstance(samskara, SamskaraProtocol)


class TestSankirtanSamskaraGenesis:
    """Test genesis phase."""

    def test_genesis_with_existing_file(self):
        """Should load file and determine mahajana."""
        # Create a temp Python file
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False
        ) as f:
            f.write('"""Test module."""\n\ndef hello():\n    pass\n')
            temp_path = Path(f.name)

        try:
            samskara = SankirtanSamskara(dry_run=True)
            ctx = samskara.genesis(temp_path)

            assert ctx.is_valid is True
            assert ctx.payload.content is not None
            assert ctx.payload.mahajana is not None
            assert ctx.payload.position is not None
        finally:
            temp_path.unlink()

    def test_genesis_with_nonexistent_file(self):
        """Should mark context invalid for missing file."""
        samskara = SankirtanSamskara(dry_run=True)
        ctx = samskara.genesis(Path("/nonexistent/path/file.py"))

        assert ctx.is_valid is False
        assert ctx.error is not None

    def test_genesis_accepts_string_path(self):
        """Should accept string path and convert to Path."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False
        ) as f:
            f.write("# test\n")
            temp_path = f.name

        try:
            samskara = SankirtanSamskara(dry_run=True)
            ctx = samskara.genesis(temp_path)  # String, not Path

            assert ctx.payload.file_path == Path(temp_path)
        finally:
            Path(temp_path).unlink()


class TestSankirtanSamskaraDharma:
    """Test dharma phase (validation)."""

    def test_dharma_valid_python_file(self):
        """Should return True for valid Python file without declaration."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False
        ) as f:
            f.write('"""Module."""\n\ndef foo():\n    return 42\n')
            temp_path = Path(f.name)

        try:
            samskara = SankirtanSamskara(dry_run=True)
            ctx = samskara.genesis(temp_path)
            result = samskara.dharma(ctx)

            assert result is True
        finally:
            temp_path.unlink()

    def test_dharma_already_owned(self):
        """Should return True for already-owned files (karma handles it)."""
        content = '''"""Test."""
# === MAHAJANA DECLARATION ===
__mahajana__ = "brahma"
__position__ = 1
__genesis__ = "0x00000000"

def test():
    pass
'''
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False
        ) as f:
            f.write(content)
            temp_path = Path(f.name)

        try:
            samskara = SankirtanSamskara(dry_run=True)
            ctx = samskara.genesis(temp_path)
            result = samskara.dharma(ctx)

            # Should return True so karma runs and returns "Already owned"
            assert result is True
            assert ctx.payload.was_already_owned is True
        finally:
            temp_path.unlink()

    def test_dharma_syntax_error_graceful(self):
        """Should handle syntax errors gracefully (Kali Yuga Grace)."""
        content = '''"""Module with bad syntax."""
def broken(
    # Missing closing paren and body
'''
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False
        ) as f:
            f.write(content)
            temp_path = Path(f.name)

        try:
            samskara = SankirtanSamskara(dry_run=True)
            ctx = samskara.genesis(temp_path)
            # Should NOT raise, should handle gracefully
            result = samskara.dharma(ctx)

            # Syntax errors are graceful - still return True
            assert result is True
        finally:
            temp_path.unlink()


class TestSankirtanSamskaraKarma:
    """Test karma phase (execution)."""

    def test_karma_would_inject(self):
        """Should return 'Would inject' result in dry-run mode."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False
        ) as f:
            f.write('"""Module."""\n\ndef foo(): pass\n')
            temp_path = Path(f.name)

        try:
            samskara = SankirtanSamskara(dry_run=True)
            ctx = samskara.genesis(temp_path)
            samskara.dharma(ctx)
            result = samskara.karma(ctx)

            assert isinstance(result, InjectionResult)
            assert result.success is True
            assert result.was_dry_run is True
            assert "Would inject" in result.message
        finally:
            temp_path.unlink()

    def test_karma_already_owned(self):
        """Should return 'Already owned' for already-owned files."""
        content = '''"""Test."""
__mahajana__ = "yamaraja"
__position__ = 15
__genesis__ = "0x00000000"
'''
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False
        ) as f:
            f.write(content)
            temp_path = Path(f.name)

        try:
            samskara = SankirtanSamskara(dry_run=True)
            ctx = samskara.genesis(temp_path)
            samskara.dharma(ctx)
            result = samskara.karma(ctx)

            assert result.message == "Already owned"
        finally:
            temp_path.unlink()


class TestSankirtanSamskaraMoksha:
    """Test moksha phase (cleanup)."""

    def test_moksha_does_not_raise(self):
        """Moksha should not raise exceptions."""
        samskara = SankirtanSamskara(dry_run=True)
        ctx = PipelineContext(payload=FilePayload(file_path=Path("/tmp/test.py")))
        result = InjectionResult(
            file_path="/tmp/test.py",
            mahajana="test",
            position=0,
            success=True,
            was_dry_run=True,
            message="test",
        )

        # Should not raise
        samskara.moksha(ctx, result)


class TestSankirtanSamskaraWithExecutor:
    """Test full pipeline with PipelineExecutor."""

    def test_full_pipeline_new_file(self):
        """Should execute all 4 phases for new file."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False
        ) as f:
            f.write('"""New module."""\n\ndef test(): pass\n')
            temp_path = Path(f.name)

        try:
            samskara = SankirtanSamskara(dry_run=True)
            executor = PipelineExecutor(samskara)

            ctx, result = executor.run(temp_path)

            assert len(ctx.phases) == 4
            assert ctx.phases[0].phase == Phase.GENESIS
            assert ctx.phases[1].phase == Phase.DHARMA
            assert ctx.phases[2].phase == Phase.KARMA
            assert ctx.phases[3].phase == Phase.MOKSHA
            assert result is not None
            assert result.success is True
        finally:
            temp_path.unlink()

    def test_full_pipeline_already_owned(self):
        """Should handle already-owned files correctly."""
        content = '''"""Owned."""
__mahajana__ = "kapila"
__position__ = 6
__genesis__ = "0x00000000"
'''
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False
        ) as f:
            f.write(content)
            temp_path = Path(f.name)

        try:
            samskara = SankirtanSamskara(dry_run=True)
            executor = PipelineExecutor(samskara)

            ctx, result = executor.run(temp_path)

            assert result.message == "Already owned"
            assert ctx.all_phases_ok is True
        finally:
            temp_path.unlink()

    def test_iterate_pipeline(self):
        """Should iterate through all phases."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False
        ) as f:
            f.write("# test\n")
            temp_path = Path(f.name)

        try:
            samskara = SankirtanSamskara(dry_run=True)
            executor = PipelineExecutor(samskara)

            phases_seen = []
            for phase, ctx in executor.iterate(temp_path):
                phases_seen.append(phase)

            assert phases_seen == [
                Phase.GENESIS,
                Phase.DHARMA,
                Phase.KARMA,
                Phase.MOKSHA,
            ]
        finally:
            temp_path.unlink()


class TestHasDeclaration:
    """Test has_declaration helper function."""

    def test_detects_mahajana(self):
        """Should detect __mahajana__ declaration."""
        content = '__mahajana__ = "brahma"'
        assert has_declaration(content) is True

    def test_no_declaration(self):
        """Should return False for files without declaration."""
        content = "def hello(): pass"
        assert has_declaration(content) is False


class TestGetMahajanaForPath:
    """Test path-to-mahajana mapping."""

    def test_naga_folder_maps_to_yamaraja(self):
        """Files in naga/ should map to yamaraja."""
        path = Path("/project/vibe_core/naga/some_module.py")
        mahajana, position = get_mahajana_for_path(path)
        assert mahajana == "yamaraja"
        assert position == 15

    def test_cli_folder_maps_to_narada(self):
        """Files in cli/ should map to narada."""
        path = Path("/project/vibe_core/cli/entry.py")
        mahajana, position = get_mahajana_for_path(path)
        assert mahajana == "narada"
        assert position == 2

    def test_plugins_folder_maps_to_prahlada(self):
        """Files in plugins/ should map to prahlada."""
        path = Path("/project/vibe_core/plugins/my_plugin.py")
        mahajana, position = get_mahajana_for_path(path)
        assert mahajana == "prahlada"
        assert position == 9

    def test_unknown_path_uses_hash(self):
        """Unknown paths should use deterministic hash mapping."""
        path = Path("/some/random/path/file.py")
        result = get_mahajana_for_path(path)
        assert result is not None
        mahajana, position = result
        assert 0 <= position < 16
