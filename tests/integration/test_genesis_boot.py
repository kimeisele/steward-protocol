import os
from pathlib import Path

import pytest

from vibe_core.kernel_impl import RealVibeKernel

# Compute project root once at module level (absolute path)
PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()


@pytest.mark.xfail(reason="OPUS-307: Genesis path set during boot_async() - test needs async refactor")
def test_genesis_boot_loading():
    """
    Verify that the kernel boots and loads the Genesis Cognitive Pack.

    NOTE: This test uses RealVibeKernel with load_plugins=True but does NOT
    call boot(), so the gateway is NOT started. This is intentional - we only
    need to verify plugin discovery and genesis loading.

    KNOWN ISSUE (OPUS-307): genesis_path is now set during boot_async() in the
    plugin loading phase, not during kernel construction. This test needs to be
    refactored to use boot_async() or accept that genesis loading requires boot.

    Checks:
    1. PluginLoader discovers 'genesis_knowledge'.
    2. RealVibeKernel sets kernel.genesis_path.
    3. EnvoyPlugin loads circuits from the genesis pack.
    """
    # Pre-check: Skip if genesis pack doesn't exist (CI without artifacts)
    genesis_manifest = PROJECT_ROOT / "knowledge" / "genesis" / "manifest.json"
    if not genesis_manifest.exists():
        pytest.skip(f"Genesis pack not found: {genesis_manifest}")

    # Save and restore CWD to avoid affecting other tests
    original_cwd = Path.cwd()
    kernel = None
    try:
        os.chdir(PROJECT_ROOT)

        # Create kernel with plugins but do NOT boot (no gateway)
        kernel = RealVibeKernel(load_plugins=True)

        # Check Genesis Path
        assert hasattr(kernel, "genesis_path"), "Kernel missing genesis_path attribute"
        assert kernel.genesis_path is not None, "Kernel failed to load Genesis Pack (genesis_path is None)"

        # Verify it points to a valid genesis pack (has circuits/)
        assert (kernel.genesis_path / "circuits").exists(), "Genesis path does not contain circuits/"

        # Check Envoy Integration
        assert hasattr(kernel, "envoy"), "Envoy plugin not registered"
        assert kernel.envoy is not None, "kernel.envoy is None"

        # Check if circuits are loaded
        circuits = kernel.envoy._circuits
        assert len(circuits) > 0, f"Envoy failed to load any circuits. envoy._circuits={circuits}"

    finally:
        if kernel:
            kernel.shutdown()
        os.chdir(original_cwd)
