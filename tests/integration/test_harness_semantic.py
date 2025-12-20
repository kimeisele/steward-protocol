"""
OPUS-162: Semantic HARNESS Tests

These tests verify that the wiring actually WORKS, not just that patterns exist.
Layer 2 of the HARNESS Prüfstelle.
"""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


class TestGenesisFlowSemantic:
    """Semantic tests for the Genesis flow."""

    def test_genesis_service_is_callable(self):
        """SEMANTIC: GenesisService can be instantiated and used."""
        from vibe_core.genesis import GenesisService, ModuleType

        # Reset singleton for clean test
        GenesisService.reset_instance()

        with tempfile.TemporaryDirectory() as tmpdir:
            workspace = Path(tmpdir)
            genesis = GenesisService.get_instance(workspace=workspace)

            assert genesis is not None
            assert genesis.compliance is not None
            assert genesis.templates is not None
            assert genesis.builder is not None

    def test_genesis_quick_check_returns_boolean(self):
        """SEMANTIC: quick_check returns True/False for compliance."""
        from vibe_core.genesis import GenesisService

        GenesisService.reset_instance()

        with tempfile.TemporaryDirectory() as tmpdir:
            workspace = Path(tmpdir)
            genesis = GenesisService.get_instance(workspace=workspace)

            # Non-existent path should return True (unknown type)
            result = genesis.quick_check(workspace / "nonexistent")
            assert isinstance(result, bool)

    def test_genesis_scaffold_creates_files(self):
        """SEMANTIC: scaffold_new actually creates files on disk."""
        from vibe_core.genesis import GenesisService, ModuleType

        GenesisService.reset_instance()

        with tempfile.TemporaryDirectory() as tmpdir:
            workspace = Path(tmpdir)
            genesis = GenesisService.get_instance(workspace=workspace)

            # Create a plugin directory
            plugin_dir = workspace / "plugins" / "test_plugin"
            plugin_dir.mkdir(parents=True)

            result = genesis.scaffold_new(
                path=plugin_dir,
                module_type=ModuleType.PLUGIN,
                context={
                    "id": "test",
                    "name": "Test Plugin",
                    "description": "A test plugin",
                    "class_name": "Test",
                },
            )

            # Verify files were created
            assert (plugin_dir / "__init__.py").exists()
            assert (plugin_dir / "manifest.json").exists()
            assert (plugin_dir / "plugin_main.py").exists()


class TestZollamtFlowSemantic:
    """Semantic tests for the Zollamt (compliance gate) flow."""

    def test_zollamt_blocks_non_compliant_in_block_mode(self):
        """SEMANTIC: Block mode actually prevents loading."""
        from vibe_core.loaders.base_loader import UnifiedLoader

        with tempfile.TemporaryDirectory() as tmpdir:
            module_dir = Path(tmpdir) / "bad_module"
            module_dir.mkdir()
            # Intentionally empty - non-compliant

            manifest = {"id": "bad", "type": "plugin"}
            config = {"loader": {"compliance_mode": "block"}}

            # Mock genesis to return non-compliant
            with patch("vibe_core.genesis.GenesisService") as mock_genesis:
                mock_instance = MagicMock()
                mock_instance.quick_check.return_value = False
                mock_genesis.get_instance.return_value = mock_instance

                import sys

                mock_module = MagicMock()
                mock_module.GenesisService = mock_genesis

                with patch.dict(sys.modules, {"vibe_core.genesis": mock_module}):
                    result = UnifiedLoader._check_gad000_compliance(module_dir, manifest, config)

                    assert result["passed"] is False
                    assert result["mode"] == "block"


class TestWiringIntegration:
    """Test that OPUS-160 wiring is actually functional."""

    def test_engineer_builder_tool_import_works(self):
        """SEMANTIC: Engineer can import GenesisService."""
        # This tests that the import path is correct
        try:
            from vibe_core.cartridges.system.engineer.tools.builder_tool import BuilderTool

            # If we get here, the import works
            assert BuilderTool is not None
        except ImportError as e:
            pytest.fail(f"Engineer BuilderTool import failed: {e}")

    def test_manas_cognitive_kernel_import_works(self):
        """SEMANTIC: MANAS can import GenesisService."""
        try:
            from vibe_core.plugins.opus_assistant.manas.cognitive_kernel import CognitiveKernel

            assert CognitiveKernel is not None
        except ImportError as e:
            pytest.fail(f"MANAS CognitiveKernel import failed: {e}")


class TestHarnessValidatorSemantic:
    """Test the HARNESS validator itself."""

    def test_harness_validator_parses_tags(self):
        """SEMANTIC: Validator can parse @HARNESS YAML."""
        from vibe_core.governance.harness_validator import extract_harness_tags

        content = """
# Some OPUS Document

<!-- @HARNESS
files:
  - path: some/file.py
    required: true
wiring:
  - pattern: "class Foo"
    in: some/file.py
-->

Some text after.
"""
        tags = extract_harness_tags(content)

        assert len(tags) == 1
        assert "files" in tags[0]
        assert "wiring" in tags[0]
        assert tags[0]["files"][0]["path"] == "some/file.py"

    def test_harness_validator_finds_patterns(self):
        """SEMANTIC: Validator finds patterns in actual files."""
        from vibe_core.governance.harness_validator import validate_harness

        with tempfile.TemporaryDirectory() as tmpdir:
            workspace = Path(tmpdir)

            # Create target file with pattern
            target = workspace / "target.py"
            target.write_text("from module import Class\n\nclass Foo:\n    pass\n")

            # Create OPUS doc with HARNESS tag
            doc = workspace / "OPUS-TEST.md"
            doc.write_text(
                """# Test

<!-- @HARNESS
files:
  - path: target.py
    required: true
wiring:
  - pattern: "from module import Class"
    in: target.py
  - pattern: "class Foo"
    in: target.py
-->
"""
            )

            result = validate_harness(doc, workspace)

            assert result.passed is True
            assert len(result.checks) == 3  # 1 file + 2 wiring

    def test_harness_validator_fails_on_missing_pattern(self):
        """SEMANTIC: Validator fails when pattern is missing."""
        from vibe_core.governance.harness_validator import validate_harness

        with tempfile.TemporaryDirectory() as tmpdir:
            workspace = Path(tmpdir)

            # Create target file WITHOUT the expected pattern
            target = workspace / "target.py"
            target.write_text("# Empty file\n")

            # Create OPUS doc expecting a pattern
            doc = workspace / "OPUS-TEST.md"
            doc.write_text(
                """# Test

<!-- @HARNESS
wiring:
  - pattern: "class ExpectedClass"
    in: target.py
-->
"""
            )

            result = validate_harness(doc, workspace)

            assert result.passed is False
            assert len(result.failed_checks) == 1
            assert "Pattern not found" in result.failed_checks[0].error
