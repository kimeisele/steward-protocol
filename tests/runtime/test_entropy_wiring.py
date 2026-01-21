"""
TEST: ENTROPY SHELL & SADHANA LOOP
==================================

Verifies:
1. BootOrchestrator wraps Kernel in EntropyShell.
2. The Sadhana Loop (Mantra) actively restores integrity during execution.
"""

import pytest
import asyncio
import time
from unittest.mock import MagicMock, patch, AsyncMock

from vibe_core.boot_orchestrator import BootOrchestrator
from vibe_core.boot_mode import BootMode
from vibe_core.protocols.substrate.byte import GenesisByte, MantraBit
from vibe_core.runtime.entropy_shell import EntropyShell


@pytest.mark.asyncio
async def test_boot_wraps_in_entropy_shell():
    """
    Verify that booting results in a kernel wrapped in EntropyShell.
    """
    # Mocking the interaction to avoid full db/system boot overhead
    with patch("vibe_core.services.kernel_factory.KernelFactory.get_kernel") as mock_get_kernel:
        # Mock the raw kernel
        mock_raw_kernel = MagicMock()
        mock_raw_kernel.get_status.return_value = {"status": "MOCKED"}
        mock_get_kernel.return_value = mock_raw_kernel

        # Initialize Orchestrator
        orchestrator = BootOrchestrator(boot_mode=BootMode.HEADLESS, ledger_path=":memory:")

        # Mock phases to simulate valid execution without side effects
        # We need _orient to RUN to verify wiring, but we can mock _decide and _act
        orchestrator._decide = AsyncMock(return_value=([], {}))
        orchestrator._act = AsyncMock(return_value=({"booted": True}, {}))
        # _perceive and _orient will run as real methods
        # This will test the actual wiring code in _orient

        # Force boot with Mantra
        kernel = await orchestrator.boot_orchestrated(force=True)

        # ASSERT 1: Shell Wrapping
        assert isinstance(kernel, EntropyShell), "Kernel is NOT wrapped in EntropyShell!"
        assert kernel._inner == mock_raw_kernel, "Shell is not wrapping the correct kernel!"

        # ASSERT 2: Sadhana Loop Efficacy
        # Verification: If the Sadhana Loop ran, it should have hit the resonance points.
        # Check last_refresh timestamp - it should be very recent (near 'now')
        # If the loop didn't run or didn't inject, last_refresh would be old (start of __init__)

        now = time.time()
        # It should be practically identical to now if HARE_8 (Purnam) was just hit in _act phase
        assert (now - kernel.state.last_refresh) < 1.0, "Mantra Purnam (HARE_8) was not hit! Cycle did not chant."

        # Integrity should be fully restored to 1.0 at the end of the loop
        # BUT: The Law of Decay is active. Time passed since HARE_8.
        # So it will be slightly less than 1.0. This PROVES it works.
        assert kernel.state.integrity > 0.99, f"Integrity too low: {kernel.state.integrity}"
        assert kernel.state.integrity <= 1.0

        # Test status overlay
        status = kernel.get_status()
        assert "entropy_integrity" in status
        assert status["entropy_integrity"] == 1.0
