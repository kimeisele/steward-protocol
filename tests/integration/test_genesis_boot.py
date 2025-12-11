import os
from pathlib import Path

import pytest

from vibe_core.kernel_impl import RealVibeKernel


@pytest.mark.asyncio
async def test_genesis_boot_loading():
    """
    Verify that the kernel boots and loads the Genesis Cognitive Pack.

    Checks:
    1. PluginLoader discovers 'genesis_knowledge'.
    2. RealVibeKernel sets kernel.genesis_path.
    3. EnvoyPlugin loads circuits from the genesis pack.
    """

    # 1. Initialize Kernel (triggers plugin discovery)
    # Ensure we are in the project root so finding knowledge/ works
    os.chdir(Path(__file__).parent.parent.parent)

    print(f"CWD: {os.getcwd()}")

    kernel = RealVibeKernel(load_plugins=True)

    # 2. Check Genesis Path
    assert hasattr(kernel, "genesis_path"), "Kernel missing genesis_path attribute"
    assert kernel.genesis_path is not None, "Kernel failed to load Genesis Pack (genesis_path is None)"

    print(f"Genesis Path: {kernel.genesis_path}")

    # Verify it points to a valid genesis pack (has circuits/)
    assert (kernel.genesis_path / "circuits").exists(), "Genesis path does not contain circuits/"

    # 3. Check Envoy Integration
    assert hasattr(kernel, "envoy"), "Envoy plugin not registered"
    assert kernel.envoy is not None, "kernel.envoy is None"

    # Check if circuits are loaded
    circuits = kernel.envoy._circuits
    assert len(circuits) > 0, "Envoy failed to load any circuits"

    # Verify circuits were loaded
    circuit_names = list(circuits.keys())
    print(f"Available circuits: {circuit_names}")
    assert len(circuit_names) > 0, "No circuits loaded"

    print("Genesis Boot Verification Successful!")
