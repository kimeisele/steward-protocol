import os
from pathlib import Path

import pytest

from vibe_core.kernel_impl import RealVibeKernel

# Compute project root once at module level (absolute path)
PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()


def test_genesis_boot_loading():
    """
    Verify that the kernel boots and loads the Genesis Cognitive Pack.

    NOTE: This test uses RealVibeKernel with load_plugins=True but does NOT
    call boot(), so the gateway is NOT started. This is intentional - we only
    need to verify plugin discovery and genesis loading.

    Checks:
    1. PluginLoader discovers 'genesis_knowledge'.
    2. RealVibeKernel sets kernel.genesis_path.
    3. EnvoyPlugin loads circuits from the genesis pack.
    """
    # Pre-check: Skip if genesis pack doesn't exist (CI without artifacts)
    genesis_manifest = PROJECT_ROOT / "knowledge" / "genesis" / "manifest.json"
    if not genesis_manifest.exists():
        pytest.skip(f"Genesis pack not found: {genesis_manifest}")

    # Verify knowledge directory structure before creating kernel
    knowledge_dir = PROJECT_ROOT / "knowledge"
    genesis_dir = PROJECT_ROOT / "knowledge" / "genesis"
    circuits_dir = genesis_dir / "circuits"

    print(f"PROJECT_ROOT: {PROJECT_ROOT}")
    print(f"knowledge_dir exists: {knowledge_dir.exists()}")
    print(f"genesis_dir exists: {genesis_dir.exists()}")
    print(f"circuits_dir exists: {circuits_dir.exists()}")

    if circuits_dir.exists():
        print(f"circuits: {list(circuits_dir.glob('*.yaml'))[:5]}")

    # Save and restore CWD to avoid affecting other tests
    original_cwd = Path.cwd()
    kernel = None
    try:
        os.chdir(PROJECT_ROOT)
        print(f"CWD after chdir: {os.getcwd()}")

        # Create kernel with plugins but do NOT boot (no gateway)
        kernel = RealVibeKernel(load_plugins=True)

        # Debug: Show what plugins were loaded
        print(f"Plugins loaded: {[p.plugin_id for p in kernel._plugins]}")
        print(f"Plugin metadata keys: {list(kernel._plugin_metadata.keys())}")

        # CRITICAL DEBUG: Trace genesis_knowledge metadata
        genesis_meta = kernel._plugin_metadata.get("genesis_knowledge")
        print("=== GENESIS METADATA DEBUG ===")
        print(f"genesis_meta exists: {genesis_meta is not None}")
        if genesis_meta:
            print(f"  item_id: {genesis_meta.item_id}")
            print(f"  item_type: {genesis_meta.item_type}")
            print(f"  loaded_successfully: {genesis_meta.loaded_successfully}")
            print(f"  error: {genesis_meta.error}")
            print(f"  manifest_path: {genesis_meta.manifest_path}")
            print(f"  manifest_path type: {type(genesis_meta.manifest_path)}")
            if genesis_meta.manifest_path:
                print(f"  manifest_path.parent: {genesis_meta.manifest_path.parent}")
                print(f"  manifest_path.name: {genesis_meta.manifest_path.name}")
                print(f"  manifest_path exists: {genesis_meta.manifest_path.exists()}")
            print(f"  manifest content: {genesis_meta.manifest}")
        print("=== END GENESIS DEBUG ===")

        # Check Genesis Path
        assert hasattr(kernel, "genesis_path"), "Kernel missing genesis_path attribute"
        if kernel.genesis_path is None:
            pytest.fail("Kernel failed to load Genesis Pack (genesis_path is None)")

        print(f"Genesis Path: {kernel.genesis_path}")
        print(f"Genesis Path type: {type(kernel.genesis_path)}")

        # Verify it points to a valid genesis pack (has circuits/)
        assert (kernel.genesis_path / "circuits").exists(), "Genesis path does not contain circuits/"

        # Check Envoy Integration
        assert hasattr(kernel, "envoy"), "Envoy plugin not registered"
        assert kernel.envoy is not None, "kernel.envoy is None"

        # Check if circuits are loaded
        circuits = kernel.envoy._circuits
        assert len(circuits) > 0, f"Envoy failed to load any circuits. envoy._circuits={circuits}"

        circuit_names = list(circuits.keys())
        print(f"Available circuits: {circuit_names}")

        print("Genesis Boot Verification Successful!")
    finally:
        # Shutdown cleans up resources (no gateway was started since boot() wasn't called)
        if kernel:
            kernel.shutdown()
        os.chdir(original_cwd)
