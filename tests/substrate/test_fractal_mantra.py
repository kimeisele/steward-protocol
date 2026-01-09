import pytest
from vibe_core.protocols.substrate.byte import MantraBit, GenesisByte

def test_infinite_scaling():
    """
    Proves that MantraBit is not limited to 16 bits (Kali Yuga Limit).
    It must scale to Satya Yuga (n=108 or higher).
    """
    # 1. Create a 108-bit Resonance (The Mala)
    mala_resonance = MantraBit.from_n(108)
    
    # 2. Verify it is "Purnam" (Complete)
    assert mala_resonance.is_purnam
    
    # 3. Verify value is massive (2^108 - 1)
    # Python ints scale infinitely by default
    assert mala_resonance.value > 0xFFFFFFFFFFFFFFFF # Bigger than 64-bit CPU
    
    print(f"🕉️  108-Bit Mantra Resonance Verified: {mala_resonance}")

def test_fractal_fracture():
    """
    Proves that a single missing bit in a 1000-bit mantra causes failure.
    (Precision of the Name)
    """
    n = 1000
    perfect = MantraBit.from_n(n)
    
    # Introduce a tiny flaw (The "Ping" of Offense)
    # 5th bit flip
    flawed_val = perfect.value ^ 16 
    flawed = MantraBit(flawed_val)
    
    assert not flawed.is_purnam
    # Resonance check: intersection count / target count
    assert flawed.check_resonance(n) < 1.0

def test_genesis_boot_fractal():
    """
    Can we boot a 'High Frequency' GenesisByte?
    """
    high_freq_genesis = GenesisByte(
        signature="sovereign:maha_vishnu",
        resonance=MantraBit.from_n(64), # 64-bit Reality
        dimension=64,
        timestamp=1234.5,
        parampara_hash="0x25" # 37 (0x25) -> Valid
    )
    
    # Should pass validation with n=64
    assert high_freq_genesis.validate()

def test_genesis_boot_scalar_mismatch():
    """
    Verification fails if dimension expectation is not met.
    """
    mixed_genesis = GenesisByte(
        signature="sovereign:confusion",
        resonance=MantraBit.from_n(16), # Only 16-bit resonance provided
        dimension=32, # But 32-bit required
        parampara_hash="0x25"
    )
    
    # Should fail because 16-bit resonance is not Purnam for 32-bit dimension
    with pytest.raises(SystemError, match="Fractal Fracture"):
        mixed_genesis.validate()

def test_compatibility_constants():
    """
    Verify standard 16-bit constants still work.
    """
    h1 = MantraBit.HARE_1
    assert h1.value == 1
    
    full = MantraBit.full_resonance()
    assert full.is_purnam
    assert full.check_resonance(16) == 1.0
