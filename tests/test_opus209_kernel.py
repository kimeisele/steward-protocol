"""OPUS-209: Kernel Architecture Tests - Fast, Static Checks."""

import ast
from pathlib import Path

import pytest


class TestImportIsolation:
    """Kernel has no cartridge dependencies."""

    def test_no_cartridge_imports(self):
        """kernel_impl.py has zero cartridge imports."""
        content = Path("vibe_core/kernel_impl.py").read_text()
        tree = ast.parse(content)
        bad = [
            n.module for n in ast.walk(tree) if isinstance(n, ast.ImportFrom) and n.module and "cartridge" in n.module
        ]
        assert bad == [], f"Cartridge imports found: {bad}"

    def test_kernel_loc_under_2000(self):
        """Kernel stays under 2000 LOC."""
        content = Path("vibe_core/kernel_impl.py").read_text()
        loc = len([l for l in content.splitlines() if l.strip() and not l.strip().startswith("#")])
        assert loc < 2000, f"Kernel is {loc} LOC, should be <2000"


class TestPluginStructure:
    """Extracted plugins exist and have correct structure."""

    @pytest.mark.parametrize(
        "plugin", ["durvasa", "samsara", "economy", "process_isolation", "resource_limits", "sangha_network"]
    )
    def test_plugin_exists(self, plugin):
        """Plugin directory exists with plugin_main.py."""
        plugin_dir = Path(f"vibe_core/plugins/{plugin}")
        assert plugin_dir.exists(), f"Plugin {plugin} missing"
        assert (plugin_dir / "plugin_main.py").exists() or (plugin_dir / "__init__.py").exists()


class TestServiceRegistry:
    """DI container works."""

    def test_registry_exists(self):
        """ServiceRegistry module exists."""
        di_path = Path("vibe_core/di.py")
        assert di_path.exists()

    def test_registry_has_core_methods(self):
        """ServiceRegistry has register/get methods."""
        content = Path("vibe_core/di.py").read_text()
        assert "def register" in content
        assert "def get" in content


class TestProtocols:
    """Protocol files exist for DI."""

    @pytest.mark.parametrize("protocol", ["process", "economy"])
    def test_protocol_exists(self, protocol):
        """Protocol file exists."""
        assert Path(f"vibe_core/protocols/{protocol}.py").exists()
