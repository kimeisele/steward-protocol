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
    
    # Unwrap the PranaTask from the _guarded_execution call
    call_args = mock_kernel_pool.apply_async.call_args
    # args[0] passed to apply_async is the PranaTask object (because of _guarded_execution wrapper)
    prana_task = call_args.kwargs.get('args')[0]
    
    from vibe_core.protocols.universal.sudarshana import PranaTask
    assert isinstance(prana_task, PranaTask)
    
    # Inspect the logic inside the Task
    # service.sync("path", context=ctx)
    # The actual args captured by wrapper:
    assert isinstance(prana_task.args[0], MultiArgService) # self
    assert prana_task.args[1] == "path"
    assert prana_task.kwargs['context'] == ctx

def test_sudarshana_immune_response(mock_kernel_pool):
    """
    Verifies that if the worker returns a PranaFailure, 
    the Nervous System (Future) raises the Exception locally.
    """
    # 1. Setup - Mock the Pool to return a PranaFailure
    from vibe_core.protocols.universal.sudarshana import PranaFailure
    
    mock_async = MagicMock()
    mock_kernel_pool.apply_async.return_value = mock_async
    
    # Simulate a crash in the worker (Legacy code failure)
    simulated_error = ValueError("Kali Yuga Error: Calculation Impossible")
    failure_payload = PranaFailure(
        error=simulated_error, 
        traceback="Mock Traceback", 
        task_id="test_crash_id"
    )
    
    # The Future.get() call returns the payload (PranaFailure)
    mock_async.get.return_value = failure_payload
    mock_async.ready.return_value = True
    
    service = MultiArgService()
    ctx = SovereignContext(identity_id="did:test_immune", signature="sig", tattva_level=TranscendentalQuality.EXISTENCE)
    
    # 2. Execute 
    future = service.sync("risky_path", context=ctx) # Dummy call to get a future
    
    # 3. Verify Immune Response
    # Calling .get() should RAISE the ValueError, unwrapped from PranaFailure
    print("\n🛡️ Verifying Immune Response...")
    with pytest.raises(ValueError) as excinfo:
        future.get()
    
    assert "Kali Yuga Error" in str(excinfo.value)
    print(f"✅ Safe! Caught expected error: {excinfo.value}")
