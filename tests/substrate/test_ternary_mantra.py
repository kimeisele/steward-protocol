import pytest
from vibe_core.protocols.substrate.byte import MantraByte, MantraTrit, HolyName, GenesisByte

def test_ternary_structure():
    """Confirms the Atomic Trit Structure."""
    h = MantraTrit(HolyName.HARE)
    k = MantraTrit(HolyName.KRISHNA)
    r = MantraTrit(HolyName.RAMA)

    assert h.value == 0
    assert k.value == 1
    assert r.value == 2
    assert repr(h) == "HARE(1.00)"
    # str() now returns IAST encoding
    assert str(h) == "hare"
    assert str(k) == "kṛṣṇa"
    assert str(r) == "rāma"

def test_mantra_byte_sequence():
    """Confirms MantraByte acts as a sequence of trits."""
    # "HARE KRISHNA"
    mb = MantraByte.from_string("HARE KRISHNA")
    assert len(mb) == 2
    assert mb.sequence[0].value == HolyName.HARE
    assert mb.sequence[1].value == HolyName.KRISHNA
    
    # Standard 16
    std = MantraByte.standard_16()
    assert len(std) == 16
    assert std.sequence[0].value == HolyName.HARE
    assert std.sequence[-1].value == HolyName.HARE # Ends with HARE

def test_fractal_coherence():
    """Verifies the Coherence Math."""
    # Perfect Coherence
    std = MantraByte.standard_16()
    assert std.coherence == pytest.approx(1.0, 0.01)
    
    # Partial Coherence (First half only)
    half = MantraByte.from_string("HARE KRISHNA HARE KRISHNA KRISHNA KRISHNA HARE HARE") # 8 words
    # It matches the first 8 words of standard, so ratio should be 1.0 (since it compares index % 16)
    # Wait, my logic: matches / len(sequence). 
    # If sequence is 8, and all 8 match standard[0..7], then ratio is 1.0?
    assert half.coherence == pytest.approx(1.0, 0.01)
    
    # Chaos (Rama everywhere)
    chaos = MantraByte.from_string("RAMA " * 16)
    # Standard has 4 Ramas. 
    # Chaos has 16 Ramas.
    # Matches will be 4 (indices 9, 11, 12, 13).
    # Ratio = 4/16 = 0.25.
    # Coherence = 1 - e^(-5 * 0.25) = 1 - e^-1.25 = 1 - 0.286 = 0.714
    assert chaos.coherence < 0.8 # Should fail verification check

def test_genesis_byte_ternary():
    """Confirms GenesisByte now accepts MantraByte."""
    g = GenesisByte(
        signature="sovereign:test",
        resonance=MantraByte.standard_16(),
        dimension=16
    )
    assert g.validate()

def test_fractal_facture_ternary():
    """Confirms Fractal Fracture detection."""
    # Dimension Mismatch
    g = GenesisByte(
        signature="sovereign:fail",
        resonance=MantraByte.from_string("HARE"), # 1 word
        dimension=16 # Expecting 16
    )
    
    with pytest.raises(SystemError, match="Fractal Fracture"):
        g.validate()

    # Dissonance Check
    g_chaos = GenesisByte(
        signature="sovereign:chaos",
        resonance=MantraByte.from_string("RAMA " * 16),
        dimension=16
    )
    with pytest.raises(SystemError, match="Dissonance Detected"):
        g_chaos.validate()
