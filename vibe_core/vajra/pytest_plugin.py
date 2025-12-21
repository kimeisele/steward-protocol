"""
⚡ VAJRA Pytest Plugin - Test Fixtures for Wiring
=================================================

Provides pytest fixtures for:
- Auto-wiring components in tests
- Wiring validation
- Strict wiring enforcement

Usage in conftest.py:
    pytest_plugins = ["vibe_core.vajra.pytest_plugin"]

Or import fixtures directly:
    from vibe_core.vajra.pytest_plugin import wired_kernel, assert_wired_context
"""

from typing import TYPE_CHECKING, Generator

import pytest

if TYPE_CHECKING:
    from vibe_core.kernel_impl import RealVibeKernel


@pytest.fixture
def wired_kernel() -> Generator["RealVibeKernel", None, None]:
    """
    Kernel fixture that auto-wires common components.

    Creates a fresh kernel with in-memory ledger and wires:
    - MANAS components (if available)
    - Analyst tools (if available)
    - Archivist tools (if available)
    """
    from vibe_core.kernel_impl import RealVibeKernel
    from vibe_core.vajra import wire_all

    kernel = RealVibeKernel(ledger_path=":memory:", load_plugins=False)

    # Wire any components that need kernel access
    # These are lazily imported to avoid circular deps

    try:
        from vibe_core.plugins.opus_assistant.manas.intent_router import IntentRouter
        from vibe_core.plugins.opus_assistant.manas.validator import SrutiValidator

        router = IntentRouter()
        validator = SrutiValidator()
        wire_all(kernel, router, validator)
    except ImportError:
        pass

    try:
        from vibe_core.plugins.opus_assistant.manas.cognitive_kernel import CognitiveKernel

        # OPUS-167: Use singleton pattern (reset first for test isolation)
        CognitiveKernel.reset_instance()
        ck = CognitiveKernel.get_instance()
        wire_all(kernel, ck)
    except ImportError:
        pass

    yield kernel

    # Cleanup
    try:
        kernel.shutdown(reason="Test complete")
    except Exception:
        pass


@pytest.fixture
def strict_wiring():
    """
    Context fixture for strict wiring enforcement.

    Any component that uses @assert_wired decorator will FAIL
    if called without kernel injection.
    """
    from vibe_core.vajra.enforcement import StrictWiringContext

    with StrictWiringContext():
        yield


@pytest.fixture
def wiring_scanner():
    """
    Fixture that provides a VAJRA scanner for wiring audits in tests.
    """
    from pathlib import Path

    from vibe_core.vajra.scanner import VAJRAScanner

    project_root = Path(__file__).parent.parent.parent
    return VAJRAScanner(project_root)


def pytest_configure(config):
    """Register VAJRA markers."""
    config.addinivalue_line(
        "markers", "require_wiring: mark test as requiring kernel wiring (use wired_kernel fixture)"
    )
    config.addinivalue_line("markers", "strict_wiring: mark test as requiring strict wiring enforcement")


def pytest_collection_modifyitems(config, items):
    """Auto-add fixtures to marked tests."""
    for item in items:
        # Auto-add wired_kernel fixture to tests marked with require_wiring
        if item.get_closest_marker("require_wiring"):
            if "wired_kernel" not in item.fixturenames:
                item.fixturenames.append("wired_kernel")

        # Auto-add strict_wiring fixture to tests marked with strict_wiring
        if item.get_closest_marker("strict_wiring"):
            if "strict_wiring" not in item.fixturenames:
                item.fixturenames.append("strict_wiring")
