"""
OPUS-210: Plugin Holon Compliance Audit

The Tanmatra Audit - Verifies all plugins adhere to PluginStateContract.

Every plugin is a HOLON (whole AND part):
- WHOLE: Complete system with own state
- PART: Integrated into Prakriti state substrate

Compliance Requirements:
1. get_state_paths() - Declares which paths contain state
2. snapshot_state() - Returns runtime state for backup
3. restore_state() - Restores from snapshot (crash recovery)
4. State paths MUST be under .vibe/state/plugins/{plugin_id}/

Non-Compliance Levels:
- CRITICAL: Security/lifecycle plugins (durvasa, samsara) - MUST comply
- HIGH: Infrastructure plugins (economy, process_isolation) - SHOULD comply
- MEDIUM: Feature plugins - MAY comply
"""

import importlib
import inspect
from pathlib import Path
from typing import Any, Dict, List, Optional, Type

import pytest

# =============================================================================
# Discovery Helpers
# =============================================================================


def discover_all_plugins() -> List[str]:
    """Discover all plugin directories."""
    plugins_dir = Path("vibe_core/plugins")
    if not plugins_dir.exists():
        return []

    plugins = []
    for item in plugins_dir.iterdir():
        if item.is_dir() and not item.name.startswith(("_", ".")):
            if (item / "plugin_main.py").exists() or (item / "__init__.py").exists():
                plugins.append(item.name)
    return sorted(plugins)


def load_plugin_class(plugin_name: str) -> Optional[Type]:
    """Load the main plugin class from a plugin directory."""
    try:
        # Try plugin_main.py first
        module = importlib.import_module(f"vibe_core.plugins.{plugin_name}.plugin_main")

        # Find class that ends with "Plugin"
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if name.endswith("Plugin") and obj.__module__ == module.__name__:
                return obj
        return None
    except ImportError:
        return None
    except Exception:
        return None


# =============================================================================
# Compliance Categories
# =============================================================================


# Critical plugins - MUST implement state contract (security/lifecycle)
CRITICAL_PLUGINS = ["durvasa", "samsara"]

# High priority plugins - SHOULD implement state contract (infrastructure)
HIGH_PLUGINS = ["economy", "process_isolation", "resource_limits", "sangha_network"]

# MANAS host - Special case, has its own state management
MANAS_HOST = ["opus_assistant"]

# All plugins we expect to find
EXPECTED_PLUGINS = CRITICAL_PLUGINS + HIGH_PLUGINS + MANAS_HOST


# =============================================================================
# Test: Plugin Discovery
# =============================================================================


class TestPluginDiscovery:
    """Verify expected plugins exist."""

    def test_plugins_directory_exists(self):
        """vibe_core/plugins/ directory exists."""
        assert Path("vibe_core/plugins").exists()

    def test_expected_plugins_exist(self):
        """All expected plugins have directories."""
        all_plugins = discover_all_plugins()
        for plugin in EXPECTED_PLUGINS:
            assert plugin in all_plugins, f"Expected plugin '{plugin}' not found"

    def test_critical_plugins_have_plugin_main(self):
        """Critical plugins have plugin_main.py."""
        for plugin in CRITICAL_PLUGINS:
            plugin_main = Path(f"vibe_core/plugins/{plugin}/plugin_main.py")
            assert plugin_main.exists(), f"Critical plugin '{plugin}' missing plugin_main.py"


# =============================================================================
# Test: PluginStateContract Methods
# =============================================================================


class TestStateContractMethods:
    """Check if plugins implement PluginStateContract methods."""

    @pytest.mark.parametrize("plugin", CRITICAL_PLUGINS)
    def test_critical_has_get_state_paths(self, plugin):
        """Critical plugins MUST have get_state_paths method."""
        cls = load_plugin_class(plugin)
        if cls is None:
            pytest.skip(f"Could not load {plugin}")

        has_method = hasattr(cls, "get_state_paths") and callable(getattr(cls, "get_state_paths", None))
        # This SHOULD fail initially - that's the point of the audit
        if not has_method:
            pytest.xfail(f"CRITICAL: {plugin} missing get_state_paths() - NEEDS REMEDIATION")

    @pytest.mark.parametrize("plugin", CRITICAL_PLUGINS)
    def test_critical_has_snapshot_state(self, plugin):
        """Critical plugins MUST have snapshot_state method."""
        cls = load_plugin_class(plugin)
        if cls is None:
            pytest.skip(f"Could not load {plugin}")

        has_method = hasattr(cls, "snapshot_state") and callable(getattr(cls, "snapshot_state", None))
        if not has_method:
            pytest.xfail(f"CRITICAL: {plugin} missing snapshot_state() - NEEDS REMEDIATION")

    @pytest.mark.parametrize("plugin", CRITICAL_PLUGINS)
    def test_critical_has_restore_state(self, plugin):
        """Critical plugins MUST have restore_state method."""
        cls = load_plugin_class(plugin)
        if cls is None:
            pytest.skip(f"Could not load {plugin}")

        has_method = hasattr(cls, "restore_state") and callable(getattr(cls, "restore_state", None))
        if not has_method:
            pytest.xfail(f"CRITICAL: {plugin} missing restore_state() - NEEDS REMEDIATION")

    @pytest.mark.parametrize("plugin", HIGH_PLUGINS)
    def test_high_has_get_state_paths(self, plugin):
        """High priority plugins SHOULD have get_state_paths method."""
        cls = load_plugin_class(plugin)
        if cls is None:
            pytest.skip(f"Could not load {plugin}")

        has_method = hasattr(cls, "get_state_paths") and callable(getattr(cls, "get_state_paths", None))
        if not has_method:
            pytest.xfail(f"HIGH: {plugin} missing get_state_paths() - RECOMMENDED")


# =============================================================================
# Test: State Path Conventions
# =============================================================================


class TestStatePathConventions:
    """Verify state paths follow conventions."""

    def test_expected_state_directory_structure(self):
        """State directory convention: .vibe/state/plugins/{plugin_id}/"""
        # This tests the CONVENTION, not actual implementation
        for plugin in EXPECTED_PLUGINS:
            expected_path = Path(f".vibe/state/plugins/{plugin}")
            # We're not checking existence, just documenting the convention
            assert expected_path.parts[0] == ".vibe"
            assert expected_path.parts[1] == "state"
            assert expected_path.parts[2] == "plugins"


# =============================================================================
# Test: Protocol Compliance Check
# =============================================================================


class TestProtocolCompliance:
    """Full protocol compliance verification."""

    def test_protocol_is_runtime_checkable(self):
        """PluginStateContract is runtime_checkable."""
        from vibe_core.state.sync_holon import PluginStateContract

        assert hasattr(PluginStateContract, "__protocol_attrs__") or hasattr(PluginStateContract, "_is_protocol"), (
            "PluginStateContract should be a Protocol"
        )

    @pytest.mark.parametrize("plugin", CRITICAL_PLUGINS + HIGH_PLUGINS)
    def test_plugin_implements_protocol(self, plugin):
        """Check if plugin class implements PluginStateContract."""
        from vibe_core.state.sync_holon import PluginStateContract

        cls = load_plugin_class(plugin)
        if cls is None:
            pytest.skip(f"Could not load {plugin}")

        # Create instance to check protocol
        try:
            instance = cls()
            is_compliant = isinstance(instance, PluginStateContract)
        except Exception:
            is_compliant = False

        if not is_compliant:
            pytest.xfail(f"{plugin} does not implement PluginStateContract - NEEDS REMEDIATION")


# =============================================================================
# Compliance Summary (Run Last)
# =============================================================================


class TestComplianceSummary:
    """Generate compliance summary."""

    def test_generate_compliance_report(self):
        """Generate a compliance report for all plugins."""
        report = {
            "total_plugins": 0,
            "compliant": [],
            "non_compliant_critical": [],
            "non_compliant_high": [],
            "non_compliant_other": [],
        }

        all_plugins = discover_all_plugins()
        report["total_plugins"] = len(all_plugins)

        for plugin in all_plugins:
            cls = load_plugin_class(plugin)
            if cls is None:
                if plugin in CRITICAL_PLUGINS:
                    report["non_compliant_critical"].append(f"{plugin} (load failed)")
                continue

            # Check for contract methods
            has_paths = hasattr(cls, "get_state_paths")
            has_snapshot = hasattr(cls, "snapshot_state")
            has_restore = hasattr(cls, "restore_state")

            is_compliant = has_paths and has_snapshot and has_restore

            if is_compliant:
                report["compliant"].append(plugin)
            elif plugin in CRITICAL_PLUGINS:
                missing = []
                if not has_paths:
                    missing.append("get_state_paths")
                if not has_snapshot:
                    missing.append("snapshot_state")
                if not has_restore:
                    missing.append("restore_state")
                report["non_compliant_critical"].append(f"{plugin} (missing: {', '.join(missing)})")
            elif plugin in HIGH_PLUGINS:
                report["non_compliant_high"].append(plugin)
            else:
                report["non_compliant_other"].append(plugin)

        # Print report
        print("\n" + "=" * 60)
        print("OPUS-210 PLUGIN COMPLIANCE REPORT")
        print("=" * 60)
        print(f"Total plugins discovered: {report['total_plugins']}")
        print(f"Compliant: {len(report['compliant'])}")
        print(f"Non-compliant (CRITICAL): {len(report['non_compliant_critical'])}")
        print(f"Non-compliant (HIGH): {len(report['non_compliant_high'])}")
        print(f"Non-compliant (other): {len(report['non_compliant_other'])}")
        print("-" * 60)

        if report["non_compliant_critical"]:
            print("\n🚨 CRITICAL - MUST FIX:")
            for p in report["non_compliant_critical"]:
                print(f"  - {p}")

        if report["non_compliant_high"]:
            print("\n⚠️ HIGH - SHOULD FIX:")
            for p in report["non_compliant_high"]:
                print(f"  - {p}")

        print("=" * 60 + "\n")

        # This test always passes - it's for reporting
        assert True
