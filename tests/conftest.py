"""
STEWARD PROTOCOL - Test Configuration
=====================================

Reads test configuration from config/quality.yaml (Phoenix Config).
NO hardcoded values - everything comes from the config.

Usage:
    pytest                      # Uses default profile (fast)
    pytest --profile=full       # Uses full profile
    pytest --profile=ci         # Uses CI profile
"""

import logging
import os
import tempfile
from pathlib import Path
from typing import Generator

import pytest

# Configure minimal logging for tests
logging.basicConfig(level=logging.WARNING, format="%(name)s - %(levelname)s - %(message)s")


# =============================================================================
# LOAD CONFIG FROM PHOENIX (quality.yaml)
# =============================================================================


def _load_quality_config():
    """Load QualityConfig from config/quality.yaml."""
    try:
        import yaml

        from vibe_core.phoenix.sections.quality.section_main import QualityConfig

        config_path = Path(__file__).parent.parent / "config" / "quality.yaml"
        if config_path.exists():
            data = yaml.safe_load(config_path.read_text())
            return QualityConfig.from_dict(data)
    except Exception as e:
        logging.warning(f"Failed to load quality config: {e}")

    # Fallback to defaults
    from vibe_core.phoenix.sections.quality.section_main import get_default_quality_config

    return get_default_quality_config()


# Load once at module level
_quality_config = _load_quality_config()


# =============================================================================
# PYTEST HOOKS - Connect to Phoenix Config
# =============================================================================


def pytest_addoption(parser):
    """Add --test-profile option to select test profile from config."""
    parser.addoption(
        "--test-profile",
        action="store",
        default=_quality_config.test.default_profile,
        help=f"Test profile to use. Available: {_quality_config.test.list_profiles()}",
    )


def pytest_configure(config):
    """Configure pytest from quality.yaml."""
    # Register markers from config
    config.addinivalue_line("markers", "fast: Quick unit tests (<1s)")
    config.addinivalue_line("markers", "slow: Slow tests (>5s)")
    config.addinivalue_line("markers", "integration: Integration tests requiring kernel")
    config.addinivalue_line("markers", "hardening: Stress/chaos/security tests")
    config.addinivalue_line("markers", "security: Penetration and crypto tests")
    config.addinivalue_line("markers", "smoke: Quick sanity check tests")
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "e2e: End-to-end tests")

    # Get selected profile
    profile_name = config.getoption("--test-profile")
    profile = _quality_config.test.get_profile(profile_name)

    # Set timeout from profile
    if profile.timeout and hasattr(config, "_inicache"):
        config._inicache["timeout"] = profile.timeout


def pytest_collection_modifyitems(config, items):
    """Auto-mark tests based on location."""
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


# =============================================================================
# FIXTURES
# =============================================================================


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


@pytest.fixture
def mock_kernel():
    """Create a minimal mock kernel for unit tests."""

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


# Module-level kernel cache
_kernel_cache = {}


@pytest.fixture(scope="module")
def cached_kernel():
    """Cached kernel instance shared across tests in the same module."""
    from vibe_core.kernel_impl import RealVibeKernel

    cache_key = "default"
    if cache_key not in _kernel_cache:
        kernel = RealVibeKernel(ledger_path=":memory:")
        _kernel_cache[cache_key] = kernel

    return _kernel_cache[cache_key]


@pytest.fixture
def fresh_kernel():
    """Fresh kernel instance for tests that modify kernel state."""
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


# =============================================================================
# QUALITY CONFIG FIXTURE (for tests that need config access)
# =============================================================================


@pytest.fixture(scope="session")
def quality_config():
    """Provide access to quality config in tests."""
    return _quality_config


# =============================================================================
# STANDARDIZED TEST FIXTURES (from test_orchestration)
# =============================================================================
# USE THESE instead of creating custom mocks or direct RealVibeKernel!
# =============================================================================


@pytest.fixture
def test_kernel():
    """
    Minimal kernel for isolated unit tests.

    USAGE:
        def test_something(test_kernel):
            test_kernel.register_agent(...)

    This is the RECOMMENDED way to get a kernel in tests.
    Uses in-memory ledger, no plugins.
    """
    from vibe_core.plugins.test_orchestration.fixtures import TestKernel

    return TestKernel.minimal()


@pytest.fixture
def permissive_kernel():
    """
    Kernel that allows all operations (no governance restrictions).

    USAGE:
        def test_feature_without_governance(permissive_kernel):
            # No oath required, all tasks allowed
            permissive_kernel.register_agent(agent)
    """
    from vibe_core.plugins.test_orchestration.fixtures import TestKernel

    return TestKernel.permissive()


@pytest.fixture
def governance_kernel():
    """
    Kernel with full governance stack (StewardProtocol).

    USAGE:
        def test_governance_enforcement(governance_kernel):
            # Only oath-sworn agents can register
            governance_kernel.register_agent(compliant_agent)
    """
    from vibe_core.plugins.test_orchestration.fixtures import TestKernel

    return TestKernel.with_governance()


@pytest.fixture
def recording_kernel():
    """
    Kernel with recording plugin for assertions.

    USAGE:
        def test_hooks_called(recording_kernel):
            kernel, recorder = recording_kernel
            kernel.register_agent(agent)
            assert recorder.get_calls("on_agent_registered")
    """
    from vibe_core.plugins.test_orchestration.fixtures import TestKernel

    return TestKernel.with_recording()


@pytest.fixture
def compliant_agent():
    """
    Fully compliant agent with valid oath.

    USAGE:
        def test_with_agent(test_kernel, compliant_agent):
            test_kernel.register_agent(compliant_agent)
    """
    from vibe_core.plugins.test_orchestration.fixtures import TestAgents

    return TestAgents.compliant("test-agent")


@pytest.fixture
def no_oath_agent():
    """
    Agent WITHOUT oath (governance gate MUST reject).

    USAGE:
        def test_governance_rejection(governance_kernel, no_oath_agent):
            with pytest.raises(GovernanceError):
                governance_kernel.register_agent(no_oath_agent)
    """
    from vibe_core.plugins.test_orchestration.fixtures import TestAgents

    return TestAgents.without_oath("test-no-oath")


@pytest.fixture
def false_oath_agent():
    """
    Agent with oath_sworn=False (governance gate MUST reject).

    USAGE:
        def test_unsworn_rejection(governance_kernel, false_oath_agent):
            # Has attributes but hasn't sworn
            assert not governance_kernel.register_agent(false_oath_agent)
    """
    from vibe_core.plugins.test_orchestration.fixtures import TestAgents

    return TestAgents.with_false_oath("test-false-oath")


@pytest.fixture
def test_context():
    """
    Full test context with isolation and cleanup.

    USAGE:
        def test_with_context(test_context):
            with test_context as ctx:
                ctx.register_compliant_agent("my-agent")
                ctx.kernel.boot()
                assert ctx.recorder.get_calls("on_boot")
            # Auto-cleanup after context exits
    """
    from vibe_core.plugins.test_orchestration.fixtures import TestContext

    return TestContext()


@pytest.fixture
def test_task():
    """
    Simple test task factory.

    USAGE:
        def test_task_submission(test_kernel, test_task, compliant_agent):
            test_kernel.register_agent(compliant_agent)
            task = test_task(compliant_agent.agent_id)
            test_kernel.submit_task(task)
    """
    from vibe_core.plugins.test_orchestration.fixtures import TestTasks

    return TestTasks.simple
