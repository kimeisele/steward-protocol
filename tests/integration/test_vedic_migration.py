import logging

import pytest

from vibe_core.cartridges.system.discoverer.agent import Discoverer
from vibe_core.kernel_impl import RealVibeKernel
from vibe_core.steward import AgentLoader

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TEST_MIGRATION")


@pytest.mark.asyncio
async def test_vedic_migration_boot():
    """
    Verify that Herald and Scribe are loaded from their new .vibe containers.
    """
    kernel = RealVibeKernel(load_plugins=False)  # Minimal boot

    # Manually trigger Discoverer to use AgentLoader
    # We want to verify that AgentLoader picks up the .vibe files

    # 1. Inspect Loader Discovery Logic
    print("\n--- Scanning for Agents ---")
    instances, metadata = AgentLoader.discover_and_load()

    assert "herald" in instances, "Herald not found!"
    assert "scribe" in instances, "Scribe not found!"

    herald_meta = metadata["herald"]
    scribe_meta = metadata["scribe"]

    print(f"Herald manifest path: {herald_meta.manifest_path}")
    print(f"Scribe manifest path: {scribe_meta.manifest_path}")

    # Verify Container Precedence
    assert str(herald_meta.manifest_path).endswith(".vibe"), "Herald loaded from FOLDER, expected CONTAINER (.vibe)"
    assert str(scribe_meta.manifest_path).endswith(".vibe"), "Scribe loaded from FOLDER, expected CONTAINER (.vibe)"

    # 2. Register with Kernel
    discoverer = Discoverer(kernel=kernel)
    kernel.register_agent(discoverer, spawn_process=False)

    count = discoverer.discover_agents()
    print(f"Discoverer registered {count} agents.")

    assert "herald" in kernel.agent_registry
    assert "scribe" in kernel.agent_registry

    herald = kernel.agent_registry["herald"]
    assert hasattr(herald, "capabilities")
    assert "broadcasting" in herald.capabilities

    print("✅ Vedic Migration Verified: System Agents are Cloud-Native.")
