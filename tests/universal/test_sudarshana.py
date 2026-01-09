"""
TEST SUDARSHANA - The Fractal Hull Verification
===============================================
"Dead Matter becomes Living Spirit."

Proves that the @mantra_governed decorator successfully wraps legacy code.
"""

import pytest
import time
from unittest.mock import MagicMock
from vibe_core.protocols.universal.sudarshana import mantra_governed, KERNEL
from vibe_core.protocols.universal.mantra import MantraOpCode
from vibe_core.protocols.universal.types import SovereignContext, TranscendentalQuality

# --- MODULE LEVEL CLASSES (Pickle-Safe) ---

class DeadLegacyService:
    def read_file(self, path: str):
        return f"legacy_data_from_{path}"

class LivingServiceAdapter:
    def __init__(self, legacy):
        self.legacy = legacy

    @mantra_governed(MantraOpCode.SYS_WAKE) # HARE (Erde/Read)
    def read(self, context: SovereignContext, path: str):
        # We pass context just to satisfy Sudarshana lookup
        return self.legacy.read_file(path)

class MultiArgService:
    @mantra_governed(MantraOpCode.ASSERT_TRUTH)
    def sync(self, path: str, context: SovereignContext):
        return True

# --- FIXTURES ---

@pytest.fixture(autouse=True)
def mock_kernel_pool():
    """
    Patches the global KERNEL.pool to avoid spawning real processes during unit tests.
    Real multiprocessing is fragile in test runners.
    """
    mock_pool = MagicMock()
    mock_async = MagicMock()
    mock_pool.apply_async.return_value = mock_async
    
    original_pool = KERNEL.pool
    KERNEL.pool = mock_pool
    KERNEL.active_manifestations.clear()
    
    yield mock_pool
    
    # Teardown
    KERNEL.pool = original_pool
    KERNEL.active_manifestations.clear()

# --- TESTS ---

def test_sudarshana_spin(mock_kernel_pool):
    """
    Verifies that the wheel spins (Submission succeeds).
    """
    # 1. Setup
    legacy = DeadLegacyService()
    adapter = LivingServiceAdapter(legacy)
    
    ctx = SovereignContext(identity_id="did:test:user", signature="sig", tattva_level=TranscendentalQuality.EXISTENCE)
    
    # 2. Execute via Mantra (Async)
    # This should trigger Kernel Injection
    result_msg = adapter.read(ctx, "test.txt")
    
    # 3. Verify Submission (The "Prana Injection")
    print(f"\n🌀 Kernel Response: {result_msg}")
    assert "submitted to the Wheel" in result_msg
    
    # Check Kernel Logic ran
    # Only ONE call expected
    assert mock_kernel_pool.apply_async.call_count == 1
    
    # Verify arguments passed to pool match expected
    call_args = mock_kernel_pool.apply_async.call_args
    # call_args.kwargs['kwds'] contains the kwargs passed to the target function
    # The 'args' passed to apply_async is the tuple of args for the target function
    target_args = call_args.kwargs.get('args')
    target_kwargs = call_args.kwargs.get('kwds')
    
    # LivingServiceAdapter.read(ctx, "test.txt")
    # args includes 'self' because it's a bound method call intercepted by wrapper
    # args = (self, ctx, "test.txt")
    
    assert isinstance(target_args[0], LivingServiceAdapter) # self
    assert target_args[1] == ctx
    assert target_args[2] == "test.txt"
    
    assert len(KERNEL.active_manifestations) > 0


def test_sudarshana_autodiscovery(mock_kernel_pool):
    """
    Verifies that Sudarshana finds context even if not first arg.
    """
    service = MultiArgService()
    ctx = SovereignContext(identity_id="did:test:user", signature="sig", tattva_level=TranscendentalQuality.TRUTHFULNESS)
    
    # Execute
    result_msg = service.sync("path", context=ctx)
    
    # Verify
    assert "submitted to the Wheel" in result_msg
    assert mock_kernel_pool.apply_async.call_count == 1
    
    # Check args alignment
    call_args = mock_kernel_pool.apply_async.call_args
    target_args = call_args.kwargs.get('args')
    target_kwargs = call_args.kwargs.get('kwds')
    
    # service.sync("path", context=ctx) 
    # args=(self, "path"), kwargs={'context': ctx}
    
    assert isinstance(target_args[0], MultiArgService) # self
    assert target_args[1] == "path"
    assert target_kwargs['context'] == ctx
