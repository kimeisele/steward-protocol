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
    """
    mock_pool = MagicMock()
    mock_async = MagicMock()
    mock_pool.apply_async.return_value = mock_async
    
    # Mock Future behavior
    mock_async.get.return_value = "legacy_data_from_test.txt"
    mock_async.ready.return_value = True
    
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
    Verifies that the wheel spins (Submission succeeds) AND we get a Result Future.
    """
    # 1. Setup
    legacy = DeadLegacyService()
    adapter = LivingServiceAdapter(legacy)
    
    ctx = SovereignContext(identity_id="did:test:user", signature="sig", tattva_level=TranscendentalQuality.EXISTENCE)
    
    # 2. Execute via Mantra (Async)
    # This returns a PranaFuture now
    future = adapter.read(ctx, "test.txt")
    
    # 3. Verify Submission (The "Prana Injection")
    print(f"\n🌀 Kernel Future: {future}")
    assert future is not None
    
    # 4. Verify Nervous System (Future.get())
    # The mock returns "legacy_data_from_test.txt"
    result = future.get()
    print(f"✨ Resolved Result: {result}")
    assert result == "legacy_data_from_test.txt"
    
    # Check Kernel Logic ran
    assert mock_kernel_pool.apply_async.call_count == 1
    
    assert len(KERNEL.active_manifestations) > 0


def test_sudarshana_autodiscovery(mock_kernel_pool):
    """
    Verifies that Sudarshana finds context even if not first arg.
    """
    service = MultiArgService()
    ctx = SovereignContext(identity_id="did:test:user", signature="sig", tattva_level=TranscendentalQuality.TRUTHFULNESS)
    
    # Execute
    future = service.sync("path", context=ctx)
    
    # Verify
    assert future is not None
    assert mock_kernel_pool.apply_async.call_count == 1
    
    # service.sync("path", context=ctx) 
    # args=(self, "path"), kwargs={'context': ctx}
    
    call_args = mock_kernel_pool.apply_async.call_args
    target_args = call_args.kwargs.get('args')
    
    assert isinstance(target_args[0], MultiArgService)
    assert target_args[1] == "path"
