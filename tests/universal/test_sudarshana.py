"""
TEST SUDARSHANA - The Fractal Hull Verification
===============================================
"Dead Matter becomes Living Spirit."

Proves that the @mantra_governed decorator successfully wraps legacy code.
"""

import pytest
from vibe_core.protocols.universal.sudarshana import mantra_governed
from vibe_core.protocols.universal.mantra import MantraOpCode
from vibe_core.protocols.universal.types import SovereignContext, TranscendentalQuality

# SIMULATION EINES LEGACY SERVICES (Tote Materie)
class DeadLegacyService:
    def read_file(self, path: str):
        return f"legacy_data_from_{path}"

# DER HULL (Das Leben)
class LivingServiceAdapter:
    def __init__(self, old):
        self.old = old

    @mantra_governed(MantraOpCode.SYS_WAKE) # HARE (Erde/Read)
    def read(self, context: SovereignContext, path: str):
        # We pass context just to satisfy Sudarshana lookup, 
        # though legacy doesn't use it.
        return self.old.read_file(path)

def test_sudarshana_spin():
    """
    Verifies that the wheel spins (Execution succeeds).
    """
    # 1. Setup
    legacy = DeadLegacyService()
    adapter = LivingServiceAdapter(legacy)
    
    ctx = SovereignContext(identity_id="did:test:user", signature="sig", tattva_level=TranscendentalQuality.EXISTENCE)
    
    # 2. Execute via Mantra
    # This should trigger SudarshanaChakra.spin(SYS_WAKE, ctx)
    result = adapter.read(ctx, "test.txt")
    
    # 3. Verify Result
    assert result == "legacy_data_from_test.txt"
    print("\n🌀 Sudarshana Spin Successful: Legacy Code Animated.")

def test_sudarshana_autodiscovery():
    """
    Verifies that Sudarshana finds context even if not first arg.
    """
    class MultiArgService:
        @mantra_governed(MantraOpCode.ASSERT_TRUTH)
        def sync(self, path: str, context: SovereignContext):
            return True
            
    service = MultiArgService()
    ctx = SovereignContext(identity_id="did:test:user", signature="sig", tattva_level=TranscendentalQuality.TRUTHFULNESS)
    
    assert service.sync("path", context=ctx) is True
