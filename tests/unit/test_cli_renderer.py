"""
TEST: CLI Renderer
==================
Tests for GAD-000 compliant output rendering.
"""

from vibe_core.cli.protocol import CLIResponse, ExecutionMode
from vibe_core.cli.renderer import CLIRenderer, get_renderer


class TestCLIRenderer:
    """Test renderer functionality."""

    def test_init(self):
        """Should initialize with correct format."""
        renderer = CLIRenderer("json")
        assert renderer.output_format == "json"

    def test_factory(self):
        """Factory should return instance."""
        renderer = get_renderer("yaml")
        assert isinstance(renderer, CLIRenderer)
        assert renderer.output_format == "yaml"

    def test_render_json_structure(self, capsys):
        """JSON output should be valid JSON."""
        renderer = CLIRenderer("json")
        response = CLIResponse(success=True, data={"foo": "bar"}, execution_mode=ExecutionMode.OFFLINE)

        renderer.render(response)
        captured = capsys.readouterr()

        import json

        data = json.loads(captured.out)
        assert data["success"] is True
        assert data["data"]["foo"] == "bar"
