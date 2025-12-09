import logging
from pathlib import Path

import pytest

from vibe_core.kernel_impl import RealVibeKernel

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TEST_PERSISTENCE")


@pytest.mark.asyncio
async def test_prakriti_persistence():
    """
    THE MEMENTO TEST (OPUS-009)

    Verifies that the system retains state across kernel restarts.
    1. Boot Kernel A
    2. Set persistent variable 'meaning_of_life' = 42 via Test Agent
    3. Shutdown Kernel A
    4. Boot Kernel B (fresh instance)
    5. Read 'meaning_of_life'
    6. Assert value is 42
    """

    # Setup Paths
    # Use localized data path to avoid polluting global state
    test_db_path = Path("data/test_persistence.db")
    if test_db_path.exists():
        test_db_path.unlink()

    config_overrides = {"paths": {"data": {"vibe_ledger": str(test_db_path)}}}

    print("\n--- 1. BOOT COMPLETED (KERNEL A) ---")
    kernel_a = RealVibeKernel(load_plugins=False)  # Minimal boot
    # Mock config injection if needed, or rely on defaults logic we add later
    # For now, we assume Kernel will load Prakriti.
    # Since we haven't implemented Kernel Integration yet,
    # we expect this test to FAIL or behave transiently.

    # Simulate Agent Action: Writing to State
    test_key = "meaning_of_life"
    test_value = 42

    print(f"--- 2. WRITING MEMORY: {test_key} = {test_value} ---")
    # Using internal API for test: kernel.prakriti.machine.set(key, value)
    # This API represents what we WANT to exist.
    if hasattr(kernel_a, "prakriti"):
        await kernel_a.prakriti.machine.set(test_key, test_value)
        # Verify it was written in this session
        val_a = await kernel_a.prakriti.machine.get(test_key)
        assert val_a == test_value, "Immediate readback failed"
    else:
        pytest.fail("Kernel has no Prakriti engine! (Integration missing)")

    print("--- 3. KILLING KERNEL A ---")
    del kernel_a

    print("--- 4. BOOTING KERNEL B (REINCARNATION) ---")
    kernel_b = RealVibeKernel(load_plugins=False)

    print("--- 5. READING MEMORY ---")
    if hasattr(kernel_b, "prakriti"):
        val_b = await kernel_b.prakriti.machine.get(test_key)
        print(f"Read Value: {val_b}")

        assert val_b == test_value, f"Amnesia detected! Expected {test_value}, got {val_b}"
    else:
        pytest.fail("Kernel B has no Prakriti engine!")

    print("✅ TEST PASSED: State survived death.")
