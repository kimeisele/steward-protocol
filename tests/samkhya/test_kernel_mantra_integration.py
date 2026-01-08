from unittest.mock import MagicMock, patch

import pytest

from vibe_core.kernel_impl import RealVibeKernel
from vibe_core.protocols.substrate import MantraOpCode
from vibe_core.protocols.universal import SovereignContext
from vibe_core.services.watchdog import NrisimhaWatchdog


@pytest.mark.asyncio
async def test_kernel_mantra_wiring():
    """
    Verify that the RealVibeKernel is correctly wired to the NrisimhaWatchdog
    and that the Mantra is chanted during pulse.
    """
    # 1. Instantiate Kernel in Test Mode (Headless)
    kernel = RealVibeKernel(test_mode=True, load_plugins=False, ledger_path=":memory:")

    # 2. Check Watchdog Existence
    assert hasattr(kernel, "watchdog")
    assert isinstance(kernel.watchdog, NrisimhaWatchdog)
    assert isinstance(kernel.watchdog._anchor, SovereignContext)
    assert kernel.watchdog._anchor.identity_id == "KERNEL_PRIME"

    # 3. Check OpCode Handlers
    handlers = kernel.watchdog._handlers
    assert MantraOpCode.ASSERT_TRUTH in handlers
    assert MantraOpCode.EXEC_SERVICE in handlers

    # 4. Verify Pulse Integration
    # We spy on the chant_mahamantra method
    with patch.object(kernel.watchdog, "chant_mahamantra", wraps=kernel.watchdog.chant_mahamantra) as mock_chant:
        # Run Pulse
        await kernel.pulse()

        # Verify Chant was called
        mock_chant.assert_called_once()

        # Verify it passed the sovereign context
        call_args = mock_chant.call_args
        assert isinstance(call_args[0][0], SovereignContext)
        assert call_args[0][0].identity_id == "KERNEL_PRIME"

    # 5. Verify Execution of Handlers (Indirectly)
    # We can patch the handler for EXEC_SERVICE to ensure it gets called
    mock_service_handler = MagicMock(return_value=True)
    kernel.watchdog._handlers[MantraOpCode.EXEC_SERVICE] = mock_service_handler

    await kernel.pulse()
    mock_service_handler.assert_called()

    print("\n✅ Kernel <-> Mantra Wiring Verified!")
