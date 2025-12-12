"""
OPUS Assistant - OPUS Generator Tests

Tests for OpusGenerator functionality.
"""

from pathlib import Path


class TestOpusGenerator:
    """Tests for OpusGenerator."""

    def test_generator_importable(self):
        """OpusGenerator can be imported."""
        from vibe_core.plugins.opus_assistant.core.opus_generator import OpusGenerator

        assert OpusGenerator is not None

    def test_generator_instantiation(self):
        """OpusGenerator can be instantiated."""
        from vibe_core.plugins.opus_assistant.core.opus_generator import OpusGenerator

        generator = OpusGenerator(workspace_root=Path("."))
        assert generator is not None

    def test_opus_data_structure(self):
        """OpusData has correct fields."""
        from vibe_core.plugins.opus_assistant.core.opus_generator import OpusData

        data = OpusData(
            generated_at="2025-01-01T00:00:00",
            workspace="/test",
        )

        assert data.generated_at == "2025-01-01T00:00:00"
        assert data.workspace == "/test"
        assert data.version == "1.0.0"
        assert data.verification == {}
        assert data.preserved_sections == {}

    def test_generate_returns_opus_data(self):
        """generate() returns OpusData."""
        from vibe_core.plugins.opus_assistant.core.opus_generator import (
            OpusData,
            OpusGenerator,
        )

        # Use project root (tests/ → opus_assistant/ → plugins/ → vibe_core/ → root)
        workspace = Path(__file__).parent.parent.parent.parent.parent
        generator = OpusGenerator(workspace_root=workspace)

        data = generator.generate(include_verification=False)

        assert isinstance(data, OpusData)
        assert data.workspace == str(workspace)
        assert data.generated_at is not None

    def test_section_preservation_markers(self):
        """Section markers are defined correctly."""
        from vibe_core.plugins.opus_assistant.core.opus_generator import OpusGenerator

        assert "HUMAN" in OpusGenerator.HUMAN_START
        assert "HUMAN" in OpusGenerator.HUMAN_END
        assert "AI" in OpusGenerator.AI_START
        assert "AI" in OpusGenerator.AI_END
        assert "AUTO-GENERATED" in OpusGenerator.AUTO_START

    def test_extract_preserved_sections(self, tmp_path):
        """_extract_preserved_sections extracts HUMAN and AI sections."""
        from vibe_core.plugins.opus_assistant.core.opus_generator import OpusGenerator

        # Create test OPUS.md with sections
        opus_content = """
# OPUS.md

<!-- @AUTO-GENERATED START -->
Auto content here
<!-- @AUTO-GENERATED END -->

<!-- @HUMAN START -->
Important human notes that should NEVER be deleted!
<!-- @HUMAN END -->

<!-- @AI START -->
AI assistant observations
<!-- @AI END -->
"""
        opus_path = tmp_path / "OPUS.md"
        opus_path.write_text(opus_content)

        generator = OpusGenerator(workspace_root=tmp_path)
        preserved = generator._extract_preserved_sections()

        assert "human_0" in preserved
        assert "Important human notes" in preserved["human_0"]
        assert "ai_0" in preserved
        assert "AI assistant observations" in preserved["ai_0"]

    def test_has_existing_opus(self, tmp_path):
        """has_existing_opus correctly detects OPUS.md."""
        from vibe_core.plugins.opus_assistant.core.opus_generator import OpusGenerator

        generator = OpusGenerator(workspace_root=tmp_path)

        # No OPUS.md yet
        assert generator.has_existing_opus() is False

        # Create OPUS.md
        (tmp_path / "OPUS.md").write_text("# Test")

        # Now exists
        assert generator.has_existing_opus() is True

    def test_collect_plugin_status(self):
        """_collect_plugin_status returns plugin info."""
        from vibe_core.plugins.opus_assistant.core.opus_generator import OpusGenerator

        # Use project root (tests/ → opus_assistant/ → plugins/ → vibe_core/ → root)
        workspace = Path(__file__).parent.parent.parent.parent.parent
        generator = OpusGenerator(workspace_root=workspace)

        plugins = generator._collect_plugin_status()

        assert isinstance(plugins, list)
        assert len(plugins) > 0

        # Should include opus_assistant itself
        plugin_ids = [p.get("id") for p in plugins]
        assert "opus_assistant" in plugin_ids

    def test_no_rendering_in_generator(self):
        """OpusGenerator has no rich/UI imports."""
        generator_path = Path(__file__).parent.parent / "core" / "opus_generator.py"
        content = generator_path.read_text()

        assert "from rich" not in content
        assert "import rich" not in content
        assert "BasePanel" not in content
        assert ".render(" not in content  # No render methods
