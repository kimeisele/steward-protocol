"""
TEST: ENTROPY SHELL WIRING
==========================

Verifies that the BootOrchestrator correctly wraps the Kernel in the Kurukshetra Shell.
"""

import pytest
import asyncio
import time
from unittest.mock import MagicMock, patch

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
        orchestrator = BootOrchestrator(
            boot_mode=BootMode.HEADLESS,
            ledger_path=":memory:"
        )
        
        # Ignite!
        genesis = GenesisByte(
            signature="tester",
            resonance=MantraBit.full_resonance(),
            timestamp=time.time()
        )
        
        # Run ignite (which calls boot)
        # Note: ignite calls self.boot() which runs async loop. 
        # But since we are already in async test, we might need to handle the loop carefully.
        # BootOrchestrator.boot() uses asyncio.run(). 
        # We should call orchestrator.boot_orchestrated directly to avoid nested event loop issues in tests.
        
        # Override ignite to call boot_orchestrated directly for testing context if needed, 
        # or just call boot_orchestrated directly.
        # But we want to test 'ignite' -> 'boot' flow if possible. 
        # Since boot() calls asyncio.run(), it will fail inside an existing loop.
        
        # Let's bypass ignite/boot wrapper and call boot_orchestrated directly, 
        # simulating what ignite does (calls boot). 
        # But wait, ignite -> boot -> asyncio.run(boot_orchestrated).
        # We'll test boot_orchestrated directly.
        
        # Manually validate genesis first (simulate ignite check)
        assert genesis.is_valid
        
        # Boot
        kernel = await orchestrator.boot_orchestrated(force=True)
        
        # ASSERT: The returned kernel must be an EntropyShell
        assert isinstance(kernel, EntropyShell), "Kernel is NOT wrapped in EntropyShell!"
        
        # Verify internal kernel is our mock
        assert kernel._inner == mock_raw_kernel, "Shell is not wrapping the correct kernel!"
        
        # Verify entropy works
        assert hasattr(kernel, "entropy"), "Shell missing entropy engine"
        # Integrity might have decayed during boot (proof of life!)
        assert 0.0 < kernel.state.integrity <= 1.0, f"Integrity out of bounds: {kernel.state.integrity}"
        
        # Test status overlay
        status = kernel.get_status()
        assert "entropy_integrity" in status, "Status missing entropy overlay"
        assert 0.0 < status["entropy_integrity"] <= 1.0

