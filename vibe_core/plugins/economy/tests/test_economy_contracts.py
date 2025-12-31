"""
TEST: EconomyPlugin Contract Tests
===================================
Target: vibe_core/plugins/economy/plugin_main.py
Standard: GAD-5000 (Plugin Contract Testing)

Tests verify:
1. Plugin identity and protocol compliance
2. on_boot lifecycle hook
3. PluginStateContract implementation (OPUS-210)
4. Bank/Vault factory methods
5. ServiceRegistry integration
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from vibe_core.plugin_protocol import HookResult, KernelPlugin, PluginResult
from vibe_core.plugins.economy.plugin_main import EconomyPlugin


class TestEconomyPluginInit:
    """Test plugin initialization and identity."""

    def test_plugin_can_be_instantiated(self):
        """Plugin should instantiate without errors."""
        plugin = EconomyPlugin()
        assert plugin is not None

    def test_plugin_has_correct_id(self):
        """Plugin ID should be 'economy'."""
        plugin = EconomyPlugin()
        assert plugin.plugin_id == "economy"

    def test_plugin_inherits_from_kernel_plugin(self):
        """Plugin should inherit from KernelPlugin."""
        plugin = EconomyPlugin()
        assert isinstance(plugin, KernelPlugin)

    def test_plugin_starts_with_no_bank(self):
        """Plugin should start with no bank instance."""
        plugin = EconomyPlugin()
        assert plugin._bank is None

    def test_plugin_starts_with_no_vault(self):
        """Plugin should start with no vault instance."""
        plugin = EconomyPlugin()
        assert plugin._vault is None

    def test_plugin_starts_with_no_db_path(self):
        """Plugin should start with no database path."""
        plugin = EconomyPlugin()
        assert plugin._db_path is None

    def test_plugin_starts_with_zero_transactions(self):
        """Plugin should start with zero transaction count."""
        plugin = EconomyPlugin()
        assert plugin._transaction_count == 0


class TestEconomyOnBoot:
    """Test on_boot behavior."""

    @patch("vibe_core.plugins.economy.plugin_main.ServiceRegistry.register_factory")
    def test_on_boot_returns_hook_result(self, mock_register):
        """on_boot should return HookResult."""
        plugin = EconomyPlugin()
        kernel = MagicMock()

        result = plugin.on_boot(kernel, config=None)

        assert isinstance(result, HookResult)
        assert result.status == PluginResult.OK

    @patch("vibe_core.plugins.economy.plugin_main.ServiceRegistry.register_factory")
    def test_on_boot_sets_db_path(self, mock_register):
        """on_boot should set database path."""
        plugin = EconomyPlugin()
        kernel = MagicMock()

        plugin.on_boot(kernel, config=None)

        assert plugin._db_path is not None
        assert isinstance(plugin._db_path, Path)

    @patch("vibe_core.plugins.economy.plugin_main.ServiceRegistry.register_factory")
    def test_on_boot_creates_db_parent_directory(self, mock_register):
        """on_boot should create parent directory for database."""
        plugin = EconomyPlugin()
        kernel = MagicMock()

        plugin.on_boot(kernel, config=None)

        # Should not raise - directory created
        assert plugin._db_path.parent.exists()

    @patch("vibe_core.plugins.economy.plugin_main.ServiceRegistry.register_factory")
    def test_on_boot_registers_bank_factory(self, mock_register):
        """on_boot should register bank factory."""
        plugin = EconomyPlugin()
        kernel = MagicMock()

        plugin.on_boot(kernel, config=None)

        # Should have been called at least once for BankProtocol
        assert mock_register.call_count == 2  # Bank and Vault

    @patch("vibe_core.plugins.economy.plugin_main.ServiceRegistry.register_factory")
    def test_on_boot_registers_vault_factory(self, mock_register):
        """on_boot should register vault factory."""
        plugin = EconomyPlugin()
        kernel = MagicMock()

        plugin.on_boot(kernel, config=None)

        # Should have been called twice (Bank + Vault)
        assert mock_register.call_count == 2

    @patch("vibe_core.plugins.economy.plugin_main.ServiceRegistry.register_factory")
    def test_on_boot_handles_exceptions(self, mock_register):
        """on_boot should handle exceptions gracefully."""
        mock_register.side_effect = Exception("Registration failed")

        plugin = EconomyPlugin()
        kernel = MagicMock()

        result = plugin.on_boot(kernel, config=None)

        assert isinstance(result, HookResult)
        assert result.status == PluginResult.ERROR


class TestEconomyStateContract:
    """Test PluginStateContract implementation (OPUS-210)."""

    def test_get_state_paths_returns_list(self):
        """get_state_paths should return list of paths."""
        plugin = EconomyPlugin()

        paths = plugin.get_state_paths()

        assert isinstance(paths, list)
        assert len(paths) >= 1

    def test_get_state_paths_includes_state_dir(self):
        """get_state_paths should include STATE_DIR."""
        plugin = EconomyPlugin()

        paths = plugin.get_state_paths()

        assert EconomyPlugin.STATE_DIR in paths

    @patch("vibe_core.plugins.economy.plugin_main.ServiceRegistry.register_factory")
    def test_get_state_paths_includes_db_path_after_boot(self, mock_register):
        """get_state_paths should include db_path after boot."""
        plugin = EconomyPlugin()
        kernel = MagicMock()
        plugin.on_boot(kernel)

        paths = plugin.get_state_paths()

        assert plugin._db_path in paths
        assert len(paths) == 2

    def test_snapshot_state_returns_dict(self):
        """snapshot_state should return dictionary."""
        plugin = EconomyPlugin()

        snapshot = plugin.snapshot_state()

        assert isinstance(snapshot, dict)

    def test_snapshot_state_includes_version(self):
        """snapshot_state should include version."""
        plugin = EconomyPlugin()

        snapshot = plugin.snapshot_state()

        assert "version" in snapshot
        assert snapshot["version"] == 1

    def test_snapshot_state_includes_db_path(self):
        """snapshot_state should include db_path."""
        plugin = EconomyPlugin()

        snapshot = plugin.snapshot_state()

        assert "db_path" in snapshot

    def test_snapshot_state_includes_bank_status(self):
        """snapshot_state should include bank active status."""
        plugin = EconomyPlugin()

        snapshot = plugin.snapshot_state()

        assert "bank_active" in snapshot
        assert snapshot["bank_active"] is False

    def test_snapshot_state_includes_vault_status(self):
        """snapshot_state should include vault active status."""
        plugin = EconomyPlugin()

        snapshot = plugin.snapshot_state()

        assert "vault_active" in snapshot
        assert snapshot["vault_active"] is False

    def test_snapshot_state_includes_transaction_count(self):
        """snapshot_state should include transaction count."""
        plugin = EconomyPlugin()
        plugin._transaction_count = 42

        snapshot = plugin.snapshot_state()

        assert "transaction_count" in snapshot
        assert snapshot["transaction_count"] == 42

    def test_snapshot_state_includes_timestamp(self):
        """snapshot_state should include timestamp."""
        plugin = EconomyPlugin()

        snapshot = plugin.snapshot_state()

        assert "timestamp" in snapshot
        assert isinstance(snapshot["timestamp"], str)

    def test_restore_state_restores_transaction_count(self):
        """restore_state should restore transaction count."""
        plugin = EconomyPlugin()

        snapshot = {"version": 1, "transaction_count": 100}

        plugin.restore_state(snapshot)

        assert plugin._transaction_count == 100

    def test_restore_state_handles_missing_transaction_count(self):
        """restore_state should handle missing transaction_count."""
        plugin = EconomyPlugin()
        plugin._transaction_count = 50

        snapshot = {"version": 1}

        plugin.restore_state(snapshot)

        assert plugin._transaction_count == 0

    def test_restore_state_ignores_wrong_version(self):
        """restore_state should ignore wrong version."""
        plugin = EconomyPlugin()
        plugin._transaction_count = 50

        snapshot = {"version": 999, "transaction_count": 100}

        plugin.restore_state(snapshot)

        # Should not change (wrong version)
        assert plugin._transaction_count == 50


class TestEconomyFactoryMethods:
    """Test bank and vault factory methods."""

    @patch("vibe_core.plugins.economy.plugin_main.ServiceRegistry.register_factory")
    def test_get_bank_returns_bank_instance(self, mock_register):
        """get_bank should return bank instance."""
        plugin = EconomyPlugin()
        kernel = MagicMock()
        plugin.on_boot(kernel)

        with patch("vibe_core.cartridges.system.civic.tools.economy.CivicBank") as mock_bank_class:
            mock_bank = MagicMock()
            mock_bank_class.return_value = mock_bank

            bank = plugin.get_bank()

            assert bank is mock_bank

    @patch("vibe_core.plugins.economy.plugin_main.ServiceRegistry.register_factory")
    def test_get_bank_creates_bank_only_once(self, mock_register):
        """get_bank should only create bank once (singleton)."""
        plugin = EconomyPlugin()
        kernel = MagicMock()
        plugin.on_boot(kernel)

        with patch("vibe_core.cartridges.system.civic.tools.economy.CivicBank") as mock_bank_class:
            mock_bank = MagicMock()
            mock_bank_class.return_value = mock_bank

            bank1 = plugin.get_bank()
            bank2 = plugin.get_bank()

            assert bank1 is bank2
            mock_bank_class.assert_called_once()

    @patch("vibe_core.plugins.economy.plugin_main.ServiceRegistry.register_factory")
    def test_get_vault_returns_vault_instance(self, mock_register):
        """get_vault should return vault instance."""
        plugin = EconomyPlugin()
        kernel = MagicMock()
        plugin.on_boot(kernel)

        with patch("vibe_core.cartridges.system.civic.tools.economy.CivicBank") as mock_bank_class:
            mock_bank = MagicMock()
            mock_bank.conn = MagicMock()
            mock_bank_class.return_value = mock_bank

            with patch("vibe_core.cartridges.system.civic.tools.vault.CivicVault") as mock_vault_class:
                mock_vault = MagicMock()
                mock_vault_class.return_value = mock_vault

                vault = plugin.get_vault()

                assert vault is mock_vault

    @patch("vibe_core.plugins.economy.plugin_main.ServiceRegistry.register_factory")
    def test_get_vault_creates_bank_first(self, mock_register):
        """get_vault should create bank first."""
        plugin = EconomyPlugin()
        kernel = MagicMock()
        plugin.on_boot(kernel)

        with patch("vibe_core.cartridges.system.civic.tools.economy.CivicBank") as mock_bank_class:
            mock_bank = MagicMock()
            mock_bank.conn = MagicMock()
            mock_bank_class.return_value = mock_bank

            with patch("vibe_core.cartridges.system.civic.tools.vault.CivicVault") as mock_vault_class:
                mock_vault = MagicMock()
                mock_vault_class.return_value = mock_vault

                plugin.get_vault()

                # Bank should be created first
                mock_bank_class.assert_called_once()

    @patch("vibe_core.plugins.economy.plugin_main.ServiceRegistry.register_factory")
    def test_create_bank_handles_import_error(self, mock_register):
        """_create_bank should handle import errors gracefully."""
        plugin = EconomyPlugin()
        kernel = MagicMock()
        plugin.on_boot(kernel)

        # Simulate import error by making the import fail
        import sys

        with patch.dict(sys.modules, {"vibe_core.cartridges.system.civic.tools.economy": None}):
            bank = plugin._create_bank()
            # When import fails, bank should be None or the method should handle it
            # The actual implementation catches ImportError and returns None

    @patch("vibe_core.plugins.economy.plugin_main.ServiceRegistry.register_factory")
    def test_create_vault_handles_import_error(self, mock_register):
        """_create_vault should handle import errors gracefully."""
        plugin = EconomyPlugin()
        kernel = MagicMock()
        plugin.on_boot(kernel)

        # Simulate import error by making the import fail
        import sys

        with patch.dict(sys.modules, {"vibe_core.cartridges.system.civic.tools.vault": None}):
            vault = plugin._create_vault()
            # When import fails, vault should be None or the method should handle it
            # The actual implementation catches ImportError and returns None


class TestEconomyGetAPI:
    """Test get_api method."""

    @patch("vibe_core.plugins.economy.plugin_main.ServiceRegistry.register_factory")
    def test_get_api_returns_dict(self, mock_register):
        """get_api should return dictionary."""
        plugin = EconomyPlugin()
        kernel = MagicMock()
        plugin.on_boot(kernel)

        api = plugin.get_api()

        assert isinstance(api, dict)

    @patch("vibe_core.plugins.economy.plugin_main.ServiceRegistry.register_factory")
    def test_get_api_includes_bank(self, mock_register):
        """get_api should include bank."""
        plugin = EconomyPlugin()
        kernel = MagicMock()
        plugin.on_boot(kernel)

        with patch("vibe_core.cartridges.system.civic.tools.economy.CivicBank") as mock_bank_class:
            mock_bank = MagicMock()
            mock_bank_class.return_value = mock_bank

            api = plugin.get_api()

            assert "bank" in api
            assert api["bank"] is mock_bank

    @patch("vibe_core.plugins.economy.plugin_main.ServiceRegistry.register_factory")
    def test_get_api_includes_vault(self, mock_register):
        """get_api should include vault."""
        plugin = EconomyPlugin()
        kernel = MagicMock()
        plugin.on_boot(kernel)

        with patch("vibe_core.cartridges.system.civic.tools.economy.CivicBank") as mock_bank_class:
            mock_bank = MagicMock()
            mock_bank.conn = MagicMock()
            mock_bank_class.return_value = mock_bank

            with patch("vibe_core.cartridges.system.civic.tools.vault.CivicVault") as mock_vault_class:
                mock_vault = MagicMock()
                mock_vault_class.return_value = mock_vault

                api = plugin.get_api()

                assert "vault" in api
                assert api["vault"] is mock_vault
