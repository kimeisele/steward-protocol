"""
STEWARD PROTOCOL - Test Configuration
=====================================

Professional pytest configuration for Kernel-Grade testing.

Test Categories (Markers):
    - fast: Unit tests (<1s)
    - slow: Long-running tests (>5s)
    - integration: Tests requiring kernel boot
    - hardening: Stress/chaos tests
    - security: Penetration/crypto tests

Usage:
    pytest -m "fast"              # Run only fast tests
    pytest -m "not slow"          # Exclude slow tests
    pytest -m "integration"       # Run integration tests only
    pytest --durations=10         # Show 10 slowest tests
"""

import logging
import os
import tempfile
from pathlib import Path
from typing import Generator

import pytest

# Configure logging for tests
logging.basicConfig(
    level=logging.WARNING,
    format="%(name)s - %(levelname)s - %(message)s",
)


# ============================================================================
# FIXTURES: Shared test resources
# ============================================================================


@pytest.fixture(scope="session")
def project_root() -> Path:
    """Return the project root directory."""
    return Path(__file__).parent.parent


@pytest.fixture(scope="session")
def constitution_path(project_root: Path) -> Path:
    """Return path to CONSTITUTION.md."""
    return project_root / "CONSTITUTION.md"


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for test artifacts."""
    with tempfile.TemporaryDirectory(prefix="steward_test_") as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def clean_env() -> Generator[None, None, None]:
    """Reset environment variables for isolated testing."""
    old_env = os.environ.copy()
    yield
    os.environ.clear()
    os.environ.update(old_env)


# ============================================================================
# HOOKS: Test lifecycle management
# ============================================================================


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line("markers", "fast: Quick unit tests (<1s)")
    config.addinivalue_line("markers", "slow: Slow tests (>5s)")
    config.addinivalue_line("markers", "integration: Integration tests requiring kernel")
    config.addinivalue_line("markers", "hardening: Stress/chaos/security tests")
    config.addinivalue_line("markers", "security: Penetration and crypto tests")
    config.addinivalue_line("markers", "vibe_plugins(plugins): List of plugin IDs to load for this test")


def pytest_collection_modifyitems(config, items):
    """Auto-mark tests based on location and duration hints."""
    for item in items:
        # Auto-mark tests in hardening/ directory
        if "hardening" in str(item.fspath):
            item.add_marker(pytest.mark.hardening)
            item.add_marker(pytest.mark.slow)

        # Auto-mark tests in integration/ directory
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)

        # Mark tests with "slow" or "stress" in name
        if "slow" in item.name.lower() or "stress" in item.name.lower():
            item.add_marker(pytest.mark.slow)

        # Mark tests with "security" or "penetration" in name
        if "security" in item.name.lower() or "penetration" in item.name.lower():
            item.add_marker(pytest.mark.security)


# ============================================================================
# KERNEL FIXTURES (for integration tests)
# ============================================================================


@pytest.fixture
def mock_kernel():
    """Create a minimal mock kernel for unit tests.

    For full kernel, use the kernel fixture from integration tests.
    """

    class MinimalMockKernel:
        def __init__(self):
            self.agent_registry = {}
            self._agent_capabilities = {}
            self._task_results = {}

        def register_agent(self, agent, spawn_process=False):
            self.agent_registry[agent.agent_id] = agent

        def get_status(self):
            return {"agents": len(self.agent_registry), "status": "RUNNING"}

        def submit_task(self, task):
            return f"task_{id(task)}"

        def get_task_result(self, task_id):
            return self._task_results.get(task_id)

    return MinimalMockKernel()


# ============================================================================
# CACHED KERNEL FIXTURE (for fast integration tests)
# ============================================================================

# Module-level kernel cache (shared across tests in same module)
_kernel_cache = {}


@pytest.fixture(scope="module")
def cached_kernel():
    """
    Create a CACHED kernel instance shared across tests in the same module.

    This dramatically speeds up integration tests by reusing the kernel
    initialization (which takes 3-5 seconds each time).

    The kernel uses in-memory SQLite and skips slow operations.

    Usage:
        def test_something(cached_kernel):
            kernel = cached_kernel
            # Use kernel...
    """
    from vibe_core.kernel_impl import RealVibeKernel

    # Check cache
    cache_key = "default"
    if cache_key not in _kernel_cache:
        # Create kernel with in-memory ledger (faster)
        kernel = RealVibeKernel(ledger_path=":memory:")
        _kernel_cache[cache_key] = kernel

    return _kernel_cache[cache_key]


@pytest.fixture
def fresh_kernel():
    """
    Create a FRESH kernel instance for tests that modify kernel state.

    Use this when you need isolation from other tests.
    Slower than cached_kernel but provides clean state.
    """
    from vibe_core.kernel_impl import RealVibeKernel

    return RealVibeKernel(ledger_path=":memory:")


def pytest_sessionfinish(session, exitstatus):
    """Clean up cached kernels at end of test session."""
    global _kernel_cache
    for kernel in _kernel_cache.values():
        try:
            if hasattr(kernel, "shutdown"):
                kernel.shutdown(reason="Test session ended")
        except Exception:
            pass
    _kernel_cache.clear()


# ============================================================================
# FRACTAL PATTERN SUPPORT
# ============================================================================


@pytest.fixture(scope="function", autouse=True)
def configure_plugins(request):
    """
    Fractal Plugin Loader:
    Configures PluginLoader to load ONLY the plugins requested by the test.

    Usage:
        @pytest.mark.vibe_plugins("interface", "governance")
        def test_something(kernel):
            ...

    Default:
        If no marker is present, loads NO plugins (lightweight default).
    """
    from unittest.mock import patch


    # Get requested plugins from marker
    marker = request.node.get_closest_marker("vibe_plugins")
    requested_plugins = marker.args if marker else ()

    # Define a side_effect for discover() that returns only requested plugins
    def discover_filtered(*args, **kwargs):
        # If specific plugins requested, instantiate and return them
        # We need to map plugin IDs to their classes/modules
        # This is a bit tricky since we don't have a central registry of ID -> Class
        # But PluginLoader.discover usually scans directories.

        # Strategy: Let the real discover run, but filter the results!
        # This assumes discover() is fast enough if we don't boot them?
        # No, discover() imports modules which might be slow.
        # But we want to avoid importing heavy stuff if not needed.

        # Better Strategy:
        # If requested_plugins is empty, return [].
        # If not empty, we need to know how to load them.
        # For now, let's assume we can import them by convention or hardcode common ones.

        plugins = []

        if "interface" in requested_plugins:
            from vibe_core.plugins.interface.plugin_main import InterfacePlugin

            plugins.append(InterfacePlugin())

        if "governance" in requested_plugins:
            from vibe_core.plugins.vedic_governance.plugin_main import VedicGovernancePlugin

            plugins.append(VedicGovernancePlugin())

        if "test_orchestration" in requested_plugins:
            from vibe_core.plugins.test_orchestration.plugin_main import TestOrchestrationPlugin

            plugins.append(TestOrchestrationPlugin())

        # Add other plugins as needed...

        return plugins

    # Patch discover
    with patch("vibe_core.plugin_loader.PluginLoader.discover", side_effect=discover_filtered):
        yield
