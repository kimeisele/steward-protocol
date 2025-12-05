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
