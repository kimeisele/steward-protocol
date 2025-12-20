"""
OPUS-150: Truth-Revealing Architecture Tests

These tests expose the architectural fragmentation documented in OPUS-150.
They are designed to FAIL until the architecture is fixed.

Run with: pytest tests/hardening/test_opus150_architecture_truth.py -v
"""

import ast
import re
from pathlib import Path

import pytest


class TestStateServiceViolations:
    """Tests that expose direct .opus_state writes (violating StateService)."""

    def get_direct_opus_state_writes(self) -> list:
        """Find all files that write directly to .opus_state."""
        violations = []
        vibe_core = Path("vibe_core")

        # Pattern: Path(".opus_state/...") or open(.opus_state/...)
        pattern = re.compile(r'\.opus_state["\'/]')

        for py_file in vibe_core.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue

            try:
                content = py_file.read_text()
                if pattern.search(content):
                    # Check if it's a write operation
                    if any(
                        write_pattern in content
                        for write_pattern in [
                            ".write_text(",
                            ".write_bytes(",
                            "open(",  # Could be write mode
                            "json.dump(",
                            "Path(",  # Creating path for potential write
                        ]
                    ):
                        # Exclude StateService itself
                        if "state_service.py" not in str(py_file):
                            violations.append(str(py_file))
            except Exception:
                pass

        return list(set(violations))

    @pytest.mark.xfail(reason="OPUS-150: Known architecture debt - direct .opus_state writes exist")
    def test_no_direct_opus_state_writes(self):
        """All .opus_state writes should go through StateService."""
        violations = self.get_direct_opus_state_writes()

        assert len(violations) == 0, (
            f"Found {len(violations)} files writing directly to .opus_state:\n"
            + "\n".join(f"  - {v}" for v in sorted(violations))
            + "\n\nAll writes should use StateService.save()"
        )


class TestRendererPatternChaos:
    """Tests that expose the three different rendering patterns."""

    def get_renderers_using_generate_content(self) -> list:
        """Find renderers using generate_content with hardcoded strings."""
        renderers = []
        renderer_dir = Path("vibe_core/plugins/interface/renderers")

        for py_file in renderer_dir.glob("*.py"):
            if py_file.name in ("__init__.py", "base.py"):
                continue

            content = py_file.read_text()
            if "def generate_content" in content and "lines.append" in content:
                renderers.append(py_file.name)

        return renderers

    def get_renderers_using_jinja2(self) -> list:
        """Find renderers using Jinja2 templates."""
        jinja_users = []
        vibe_core = Path("vibe_core")

        pattern = re.compile(r"from jinja2|import jinja2|Jinja|\.j2")

        for py_file in vibe_core.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue

            try:
                content = py_file.read_text()
                if pattern.search(content):
                    jinja_users.append(str(py_file))
            except Exception:
                pass

        return jinja_users

    def get_renderers_using_render_sections(self) -> list:
        """Find renderers actually using render_sections()."""
        users = []
        renderer_dir = Path("vibe_core/plugins/interface/renderers")

        for py_file in renderer_dir.rglob("*.py"):
            if py_file.name in ("__init__.py", "base.py"):
                continue

            content = py_file.read_text()
            if "render_sections()" in content:
                users.append(str(py_file))

        return users

    @pytest.mark.xfail(reason="OPUS-150: Known architecture debt - multiple rendering patterns")
    def test_single_rendering_pattern(self):
        """All renderers should use the same pattern."""
        hardcoded = self.get_renderers_using_generate_content()
        jinja = self.get_renderers_using_jinja2()
        config_driven = self.get_renderers_using_render_sections()

        patterns_used = 0
        if hardcoded:
            patterns_used += 1
        if jinja:
            patterns_used += 1
        if config_driven:
            patterns_used += 1

        assert patterns_used <= 1, (
            f"Found {patterns_used} different rendering patterns:\n"
            f"  Hardcoded (lines.append): {len(hardcoded)} renderers\n"
            f"  Jinja2 templates: {len(jinja)} files\n"
            f"  Config-driven (render_sections): {len(config_driven)} renderers\n"
            f"\nShould be unified into ONE pattern."
        )


class TestOpusAssistantSize:
    """Tests that expose opus_assistant's monstrous size."""

    def count_loc(self, path: Path) -> int:
        """Count lines of code in a directory."""
        total = 0
        for py_file in path.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue
            try:
                total += len(py_file.read_text().splitlines())
            except Exception:
                pass
        return total

    @pytest.mark.xfail(reason="OPUS-150: Known architecture debt - opus_assistant is too big")
    def test_opus_assistant_not_bigger_than_state(self):
        """opus_assistant should not be bigger than state/ module."""
        opus_loc = self.count_loc(Path("vibe_core/plugins/opus_assistant"))
        state_loc = self.count_loc(Path("vibe_core/state"))

        ratio = opus_loc / state_loc if state_loc > 0 else float("inf")

        assert ratio <= 2.0, (
            f"opus_assistant ({opus_loc} LOC) is {ratio:.1f}x bigger than state/ ({state_loc} LOC)\n"
            "A plugin should not be bigger than core state management."
        )

    @pytest.mark.xfail(reason="OPUS-150: Known architecture debt - manas should be extracted")
    def test_manas_should_be_toplevel(self):
        """manas/ should be a top-level module, not inside a plugin."""
        manas_path = Path("vibe_core/plugins/opus_assistant/manas")
        toplevel_manas = Path("vibe_core/manas")

        manas_exists_in_plugin = manas_path.exists()
        manas_exists_toplevel = toplevel_manas.exists()

        assert not manas_exists_in_plugin or manas_exists_toplevel, (
            f"manas/ ({self.count_loc(manas_path)} LOC) is buried in opus_assistant.\n"
            "It should be extracted to vibe_core/manas/ as a first-class module."
        )


class TestOpusAssistantDependencies:
    """Tests that expose opus_assistant's central role (not a true plugin)."""

    def get_opus_assistant_importers(self) -> list:
        """Find files outside opus_assistant that import from it."""
        importers = []
        vibe_core = Path("vibe_core")

        pattern = re.compile(r"from vibe_core\.plugins\.opus_assistant|import vibe_core\.plugins\.opus_assistant")

        for py_file in vibe_core.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue
            if "opus_assistant" in str(py_file):
                continue

            try:
                content = py_file.read_text()
                if pattern.search(content):
                    importers.append(str(py_file))
            except Exception:
                pass

        return importers

    @pytest.mark.xfail(reason="OPUS-150: Known architecture debt - opus_assistant is not optional")
    def test_opus_assistant_is_optional_plugin(self):
        """A plugin should be removable without breaking core functionality."""
        importers = self.get_opus_assistant_importers()

        # Core modules that should NOT depend on plugins
        core_violations = [
            i
            for i in importers
            if any(
                core in i
                for core in [
                    "vibe_core/cli/",
                    "vibe_core/kernel",
                    "vibe_core/state/",
                    "vibe_core/event",
                    "vibe_core/cartridges/",
                ]
            )
        ]

        assert len(core_violations) == 0, (
            f"Found {len(core_violations)} core modules depending on opus_assistant plugin:\n"
            + "\n".join(f"  - {v}" for v in sorted(core_violations))
            + "\n\nA plugin should be optional, not a core dependency."
        )


class TestConfigSectionsIgnored:
    """Tests that expose ignored config/interface.yaml sections."""

    def get_configured_renderers_with_sections(self) -> dict:
        """Get renderers that have sections defined in config."""
        import yaml

        config_path = Path("config/interface.yaml")
        if not config_path.exists():
            return {}

        config = yaml.safe_load(config_path.read_text())
        renderers = config.get("renderers", {})

        return {name: cfg for name, cfg in renderers.items() if cfg.get("sections")}

    def get_renderers_using_sections_config(self) -> list:
        """Get renderers that actually read their section config."""
        users = []
        renderer_dir = Path("vibe_core/plugins/interface/renderers")

        for py_file in renderer_dir.rglob("*.py"):
            if py_file.name in ("__init__.py", "base.py"):
                continue

            content = py_file.read_text()
            # Check for patterns that indicate using config sections
            if "config.sections" in content or "get_config().sections" in content:
                users.append(py_file.stem)

        return users

    @pytest.mark.xfail(reason="OPUS-150: Known architecture debt - interface.yaml sections ignored")
    def test_section_configs_are_used(self):
        """Renderers should use their section configs from interface.yaml."""
        configured = self.get_configured_renderers_with_sections()
        using_config = set(self.get_renderers_using_sections_config())

        not_using_config = [name for name in configured.keys() if name not in using_config]

        assert len(not_using_config) == 0, (
            f"Found {len(not_using_config)} renderers with section configs they IGNORE:\n"
            + "\n".join(f"  - {name}" for name in sorted(not_using_config))
            + "\n\nconfig/interface.yaml defines sections that are never used."
        )
