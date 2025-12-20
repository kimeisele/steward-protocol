"""
OPUS-161: Zollamt Tests

Test the GAD-000 compliance gate in base_loader.py.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


class TestZollamt:
    """Test the Zollamt compliance gate."""

    def test_compliance_check_passes_for_compliant_module(self, tmp_path: Path):
        """Compliant modules should pass the gate."""
        from vibe_core.loaders.base_loader import UnifiedLoader

        # Create a compliant module structure
        module_dir = tmp_path / "test_module"
        module_dir.mkdir()
        (module_dir / "__init__.py").write_text("")
        (module_dir / "manifest.json").write_text('{"id": "test", "name": "Test"}')

        manifest = {"id": "test", "type": "plugin"}

        # Mock GenesisService at the import location
        mock_genesis_class = MagicMock()
        mock_instance = MagicMock()
        mock_instance.quick_check.return_value = True
        mock_genesis_class.get_instance.return_value = mock_instance

        mock_genesis_module = MagicMock()
        mock_genesis_module.GenesisService = mock_genesis_class

        with patch.dict(sys.modules, {"vibe_core.genesis": mock_genesis_module}):
            result = UnifiedLoader._check_gad000_compliance(module_dir, manifest, None)

        assert result["passed"] is True

    def test_compliance_check_fails_for_non_compliant_module(self, tmp_path: Path):
        """Non-compliant modules should fail the gate."""
        from vibe_core.loaders.base_loader import UnifiedLoader

        module_dir = tmp_path / "incomplete_module"
        module_dir.mkdir()
        # Missing required files

        manifest = {"id": "incomplete", "type": "plugin"}

        mock_genesis_class = MagicMock()
        mock_instance = MagicMock()
        mock_instance.quick_check.return_value = False
        mock_genesis_class.get_instance.return_value = mock_instance

        mock_genesis_module = MagicMock()
        mock_genesis_module.GenesisService = mock_genesis_class

        with patch.dict(sys.modules, {"vibe_core.genesis": mock_genesis_module}):
            result = UnifiedLoader._check_gad000_compliance(module_dir, manifest, None)

        assert result["passed"] is False
        assert "GAD-000" in result["reason"]

    def test_compliance_check_graceful_degradation(self, tmp_path: Path):
        """Should gracefully degrade if GenesisService unavailable."""
        from vibe_core.loaders.base_loader import UnifiedLoader

        module_dir = tmp_path / "any_module"
        module_dir.mkdir()

        manifest = {"id": "any", "type": "plugin"}

        # Temporarily remove vibe_core.genesis from sys.modules if it exists
        original = sys.modules.get("vibe_core.genesis")
        try:
            # Remove the module so import fails
            if "vibe_core.genesis" in sys.modules:
                del sys.modules["vibe_core.genesis"]

            # Patch the import to raise ImportError
            with patch.dict(sys.modules, {"vibe_core.genesis": None}):
                result = UnifiedLoader._check_gad000_compliance(module_dir, manifest, None)

            # Should pass anyway - graceful degradation
            assert result["passed"] is True
            assert result["mode"] == "silent"
        finally:
            if original:
                sys.modules["vibe_core.genesis"] = original

    def test_compliance_check_respects_silent_mode(self, tmp_path: Path):
        """Silent mode should skip compliance check."""
        from vibe_core.loaders.base_loader import UnifiedLoader

        module_dir = tmp_path / "any_module"
        module_dir.mkdir()

        manifest = {"id": "any", "type": "plugin"}
        config = {"loader": {"compliance_mode": "silent"}}

        # Create a mock that would fail if called
        mock_genesis_class = MagicMock()
        mock_genesis_module = MagicMock()
        mock_genesis_module.GenesisService = mock_genesis_class

        with patch.dict(sys.modules, {"vibe_core.genesis": mock_genesis_module}):
            result = UnifiedLoader._check_gad000_compliance(module_dir, manifest, config)

        assert result["passed"] is True
        assert result["mode"] == "silent"
        # GenesisService should NOT be called in silent mode
        mock_genesis_class.get_instance.assert_not_called()

    def test_compliance_check_respects_disabled_flag(self, tmp_path: Path):
        """Disabled compliance_check should skip the gate."""
        from vibe_core.loaders.base_loader import UnifiedLoader

        module_dir = tmp_path / "any_module"
        module_dir.mkdir()

        manifest = {"id": "any", "type": "plugin"}
        config = {"loader": {"compliance_check": False}}

        mock_genesis_class = MagicMock()
        mock_genesis_module = MagicMock()
        mock_genesis_module.GenesisService = mock_genesis_class

        with patch.dict(sys.modules, {"vibe_core.genesis": mock_genesis_module}):
            result = UnifiedLoader._check_gad000_compliance(module_dir, manifest, config)

        assert result["passed"] is True
        mock_genesis_class.get_instance.assert_not_called()

    def test_compliance_check_warn_mode_returns_failed_but_warn(self, tmp_path: Path):
        """Warn mode should return failure with warn mode for logging."""
        from vibe_core.loaders.base_loader import UnifiedLoader

        module_dir = tmp_path / "incomplete_module"
        module_dir.mkdir()

        manifest = {"id": "incomplete", "type": "plugin"}
        config = {"loader": {"compliance_mode": "warn"}}

        mock_genesis_class = MagicMock()
        mock_instance = MagicMock()
        mock_instance.quick_check.return_value = False
        mock_genesis_class.get_instance.return_value = mock_instance

        mock_genesis_module = MagicMock()
        mock_genesis_module.GenesisService = mock_genesis_class

        with patch.dict(sys.modules, {"vibe_core.genesis": mock_genesis_module}):
            result = UnifiedLoader._check_gad000_compliance(module_dir, manifest, config)

        assert result["passed"] is False
        assert result["mode"] == "warn"

    def test_compliance_check_block_mode(self, tmp_path: Path):
        """Block mode should return failure with block mode."""
        from vibe_core.loaders.base_loader import UnifiedLoader

        module_dir = tmp_path / "incomplete_module"
        module_dir.mkdir()

        manifest = {"id": "incomplete", "type": "plugin"}
        config = {"loader": {"compliance_mode": "block"}}

        mock_genesis_class = MagicMock()
        mock_instance = MagicMock()
        mock_instance.quick_check.return_value = False
        mock_genesis_class.get_instance.return_value = mock_instance

        mock_genesis_module = MagicMock()
        mock_genesis_module.GenesisService = mock_genesis_class

        with patch.dict(sys.modules, {"vibe_core.genesis": mock_genesis_module}):
            result = UnifiedLoader._check_gad000_compliance(module_dir, manifest, config)

        assert result["passed"] is False
        assert result["mode"] == "block"
