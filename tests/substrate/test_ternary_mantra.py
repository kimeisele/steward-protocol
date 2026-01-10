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


# =============================================================================
# FRACTAL INTEGRATION TESTS
# =============================================================================

class TestMantraTritFractal:
    """Test MantraTrit integration with mantra/ fractal structure."""

    def test_trit_has_pada(self):
        """MantraTrit exposes full Pada object."""
        h = MantraTrit(HolyName.HARE)
        assert h.pada is not None
        assert h.pada.iast == "hare"
        assert h.pada.devanagari == "हरे"

    def test_trit_has_aksaras(self):
        """MantraTrit exposes aksaras."""
        h = MantraTrit(HolyName.HARE)
        assert len(h.aksaras) == 2
        assert h.aksaras[0].iast == "ha"
        assert h.aksaras[1].iast == "re"

    def test_trit_has_meaning(self):
        """MantraTrit exposes philosophical meaning."""
        h = MantraTrit(HolyName.HARE)
        k = MantraTrit(HolyName.KRISHNA)
        r = MantraTrit(HolyName.RAMA)
        assert "Energy" in h.meaning
        assert "Attractive" in k.meaning
        assert "Pleasure" in r.meaning

    def test_void_has_no_fractal(self):
        """VOID has empty aksaras and meaning."""
        v = MantraTrit(HolyName.VOID)
        assert v.aksaras == ()
        assert v.meaning == ""


class TestMantraByteFractal:
    """Test MantraByte integration with mantra/ fractal structure."""

    def test_to_padas_returns_16(self):
        """Standard 16 decomposes to 16 Padas."""
        mb = MantraByte.standard_16()
        padas = mb.to_padas()
        assert len(padas) == 16

    def test_to_aksaras_returns_32(self):
        """Standard 16 decomposes to 32 Aksaras (2 per word)."""
        mb = MantraByte.standard_16()
        aksaras = mb.to_aksaras()
        assert len(aksaras) == 32

    def test_iter_at_level_pada(self):
        """Iterate at PADA level."""
        from vibe_core.protocols.substrate.mantra.routing import FractalLevel
        mb = MantraByte.standard_16()
        padas = list(mb.iter_at_level(FractalLevel.PADA))
        assert len(padas) == 16
        assert padas[0].iast == "hare"
        assert padas[1].iast == "kṛṣṇa"

    def test_iter_at_level_aksara(self):
        """Iterate at AKSARA level."""
        from vibe_core.protocols.substrate.mantra.routing import FractalLevel
        mb = MantraByte.standard_16()
        aksaras = list(mb.iter_at_level(FractalLevel.AKSARA))
        assert len(aksaras) == 32
        assert aksaras[0].iast == "ha"
        assert aksaras[1].iast == "re"
        assert aksaras[2].iast == "kṛ"
        assert aksaras[3].iast == "ṣṇa"

    def test_get_quarter(self):
        """Get quarter for positions."""
        mb = MantraByte.standard_16()
        assert mb.get_quarter(0) == 0
        assert mb.get_quarter(3) == 0
        assert mb.get_quarter(4) == 1
        assert mb.get_quarter(8) == 2
        assert mb.get_quarter(12) == 3

    def test_get_padas_in_quarter(self):
        """Get padas in each quarter."""
        mb = MantraByte.standard_16()
        # Quarter 0: Hare Krishna Hare Krishna
        q0 = mb.get_padas_in_quarter(0)
        assert len(q0) == 4
        assert [p.iast for p in q0] == ["hare", "kṛṣṇa", "hare", "kṛṣṇa"]
        # Quarter 2: Hare Rama Hare Rama
        q2 = mb.get_padas_in_quarter(2)
        assert [p.iast for p in q2] == ["hare", "rāma", "hare", "rāma"]

    def test_get_fractal_path(self):
        """Get fractal path for a position."""
        from vibe_core.protocols.substrate.mantra.routing import FractalLevel
        mb = MantraByte.standard_16()
        path = mb.get_fractal_path(1)  # Second word (Krishna)
        assert len(path) == 3
        assert path[0].level == FractalLevel.VAKYA
        assert path[1].level == FractalLevel.PADA
        assert path[1].index == 1
        assert path[2].level == FractalLevel.AKSARA
