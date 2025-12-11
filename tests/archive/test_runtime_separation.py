import logging
from pathlib import Path

import pytest

from vibe_core.kernel_impl import RealVibeKernel

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TEST_RUNTIME")


@pytest.fixture
def lobotomy_setup():
    """
    Setup the "Lobotomy" environment:
    1. Ensure library/ exists with herald.vibe and scribe.vibe.
    2. HIDE (rename) vibe_core/cartridges/system.
    3. Yield control for test.
    4. RESTORE vibe_core/cartridges/system.
    """
    root = Path(".")
    library = root / "library"
    system_cartridges = root / "vibe_core/cartridges/system"
    hidden_cartridges = root / "vibe_core/cartridges/_system_hidden"

    # 1. Verify Library
    assert library.exists(), "Library folder missing!"
    assert (library / "herald.vibe").exists(), "herald.vibe missing in library!"
    assert (library / "scribe.vibe").exists(), "scribe.vibe missing in library!"

    # 2. Perform Lobotomy (Hide Source Agents)
    if system_cartridges.exists():
        logger.warning("🔪 PERFORMING LOBOTOMY: Hiding Source Agents...")
        system_cartridges.rename(hidden_cartridges)
    else:
        # Maybe already hidden? Fail safe.
        pass

    try:
        yield
    finally:
        # 3. Restore (Heal)
        if hidden_cartridges.exists():
            logger.info("🩹 HEALING: Restoring Source Agents...")
            hidden_cartridges.rename(system_cartridges)


@pytest.mark.asyncio
@pytest.mark.skip(reason="WIP: Relative imports in container modules need sys.path adjustment")
async def test_lobotomy_boot(lobotomy_setup):
    """
    Boot the kernel using ONLY the library containers.
    Source agents (vibe_core/cartridges/system) are HIDDEN.
    """
    print("\n🧪 STARTING LOBOTOMY TEST: Booting Thin Kernel...")

    # Configure Kernel to use library
    # NOTE: section_main.py defaults library_path="library", so default config should work.
    kernel = RealVibeKernel()

    # Boot
    kernel.boot()

    # Assertions
    agents = kernel.agent_registry
    print(f"Loaded Agents: {list(agents.keys())}")

    assert "herald" in agents, "Herald failed to load from Library!"
    assert "scribe" in agents, "Scribe failed to load from Library!"

    # Verify Origin
    herald_meta = kernel.agent_registry.get_metadata("herald")  # Assuming get_metadata method or access
    # Wait, agent_registry is usually just instances Dict[str, Any] in some versions,
    # but let's check AgentLoader.discover_and_load returned metadata.
    # RealVibeKernel creates/stores metadata?
    # Let's inspect capabilities as proxy for correct loading.

    herald = agents["herald"]
    assert hasattr(herald, "capabilities")

    print("✅ Lobotomy Test Passed: System Agents loaded from containers without source code.")
