"""
OPUS Assistant Plugin - Sanity Tests

OPUS-029: Phase 0 verification that:
1. Plugin loads without errors
2. VerificationEngine works standalone
3. Plugin has correct properties
"""

import json
from pathlib import Path


class TestOpusAssistantSanity:
    """Sanity checks for opus_assistant plugin."""

    def test_manifest_valid(self):
        """Manifest.json is valid JSON with required fields."""
        manifest_path = Path(__file__).parent.parent / "manifest.json"
        assert manifest_path.exists(), "manifest.json must exist"

        data = json.loads(manifest_path.read_text())

        assert data["id"] == "opus_assistant"
        assert data["type"] == "plugin"
        assert "entry_point" in data
        assert "entry_class" in data

    def test_plugin_importable(self):
        """Plugin module can be imported."""
        from vibe_core.plugins.opus_assistant import OpusAssistantPlugin

        assert OpusAssistantPlugin is not None

    def test_plugin_instantiation(self):
        """Plugin can be instantiated without kernel."""
        from vibe_core.plugins.opus_assistant import OpusAssistantPlugin

        plugin = OpusAssistantPlugin()

        assert plugin.plugin_id == "opus_assistant"
        assert plugin.priority == 50

    def test_verification_engine_importable(self):
        """VerificationEngine can be imported."""
        from vibe_core.plugins.opus_assistant.core.verification_logic import (
            VerificationEngine,
        )

        assert VerificationEngine is not None

    def test_verification_engine_standalone(self):
        """VerificationEngine works without kernel."""
        from vibe_core.plugins.opus_assistant.core.verification_logic import (
            VerificationEngine,
        )

        # Use project root
        workspace = Path(__file__).parent.parent.parent.parent.parent.parent
        engine = VerificationEngine(workspace_root=workspace)

        # Should not crash
        report = engine.run_verification(quick=True)

        assert "docs" in report
        assert "total_score" in report
        assert "docs_with_harness" in report
        assert "docs_without_harness" in report

    def test_no_rich_in_verification_logic(self):
        """VerificationEngine has no rich/UI dependencies."""
        logic_path = Path(__file__).parent.parent / "core" / "verification_logic.py"
        content = logic_path.read_text()

        # Must NOT have rich imports
        assert "from rich" not in content, "verification_logic.py must not import rich"
        assert "import rich" not in content, "verification_logic.py must not import rich"

        # Must NOT have BasePanel
        assert "BasePanel" not in content, "verification_logic.py must not reference BasePanel"

    def test_plugin_capabilities(self):
        """Plugin reports correct capabilities."""
        from vibe_core.plugins.opus_assistant import OpusAssistantPlugin

        plugin = OpusAssistantPlugin()
        caps = plugin.get_capabilities()

        assert "version" in caps
        assert "operations" in caps
        assert "verify" in caps["operations"]


class TestVerificationEngineLogic:
    """Test VerificationEngine logic in isolation."""

    def test_extract_harness_valid(self):
        """Extract @HARNESS from valid markdown."""
        from vibe_core.plugins.opus_assistant.core.verification_logic import (
            VerificationEngine,
        )

        engine = VerificationEngine(workspace_root=Path("."))

        content = """
# Test Doc

<!-- @HARNESS
files:
  - path: test.py
    required: true
tests:
  - tests/test_*.py
-->

Some content.
"""
        harness = engine._extract_harness(content, "@HARNESS")

        assert harness is not None
        assert "files" in harness
        assert len(harness["files"]) == 1
        assert harness["files"][0]["path"] == "test.py"

    def test_extract_harness_missing(self):
        """Return None for markdown without @HARNESS."""
        from vibe_core.plugins.opus_assistant.core.verification_logic import (
            VerificationEngine,
        )

        engine = VerificationEngine(workspace_root=Path("."))

        content = "# Test Doc\n\nNo harness here."
        harness = engine._extract_harness(content, "@HARNESS")

        assert harness is None

    def test_verify_files_found(self, tmp_path):
        """Verify files returns found for existing files."""
        from vibe_core.plugins.opus_assistant.core.verification_logic import (
            VerificationEngine,
        )

        # Create test file
        test_file = tmp_path / "test.py"
        test_file.write_text("# test")

        engine = VerificationEngine(workspace_root=tmp_path)
        result = engine._verify_files([{"path": "test.py", "required": True}])

        assert result["passed"] is True
        assert "test.py" in result["found"]
        assert len(result["missing"]) == 0

    def test_verify_files_missing(self, tmp_path):
        """Verify files returns missing for non-existent files."""
        from vibe_core.plugins.opus_assistant.core.verification_logic import (
            VerificationEngine,
        )

        engine = VerificationEngine(workspace_root=tmp_path)
        result = engine._verify_files([{"path": "nonexistent.py", "required": True}])

        assert result["passed"] is False
        assert "nonexistent.py" in result["missing"]
