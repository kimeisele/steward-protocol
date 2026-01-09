import pytest
from decimal import Decimal
from vibe_core.protocols.universal.guna import GunaProtocol, GunaProfile, GunaType, ZERO, ONE
from vibe_core.protocols.universal.mantra import MantraProtocol
from vibe_core.protocols.science.entropy import KaliYugaEngine

class MaterialObject(GunaProtocol):
    def get_guna_profile(self) -> GunaProfile:
        # A standard material object: Mix of 3 modes
        # 20% Sattva, 50% Rajas, 30% Tamas
        return GunaProfile(
            sattva=Decimal("0.2"), 
            rajas=Decimal("0.5"), 
            tamas=Decimal("0.3"), 
            visuddha=ZERO
        )

class VoidObject(GunaProtocol):
    def get_guna_profile(self) -> GunaProfile:
        # The Mayavad Illusion (Nothingness)
        return GunaProfile(ZERO, ZERO, ZERO, ZERO)

# MantraProtocol is already Visuddha (imported)

    def test_visuddha_healing():
        """
        Proves that Mantra (Visuddha) causes Negentropy (Growth).
        """
        engine = KaliYugaEngine()
        mantra_obj = ConcreteMantra() # Use concrete implementation 
    # We need an instance that implements it. 
    # Ah, MantraProtocol in mantra.py IS a Protocol class, but we can mock or instantiate a concrete one?
    # No, 'class MantraProtocol(GunaProtocol)' in mantra.py is a Protocol definition?
    # Let's check mantra.py content. 
    # Result: It's defined as a Protocol but has concrete methods?
    # No, usually Protocol methods are empty... but wait, I implemented get_guna_profile in it!
    # A Protocol with concrete method implementation is a 'Mixin' or 'Concrete Protocol'? 
    # In Python, Protocols can provide default implementations but usually don't?
    # For test, I'll create a concrete class inheriting MantraProtocol if needed.
    # But wait, I added get_guna_profile implementation TO MantraProtocol class directly.
    # Python Protocols can have code. But you can't instantiate a Protocol directly if it has abstract methods.
    # Checks: chant, surrender, etc are ...
    pass

class ConcreteMantra(MantraProtocol):
    def chant(self, frequency_hz=432.0) -> float: return 1.0
    def surrender(self, context) -> None: pass
    def get_alignment_score(self) -> float: return 1.0
    def receive_mantra(self, mantra) -> None: pass
    # It inherits get_guna_profile from MantraProtocol
    
def test_physics_engine():
    engine = KaliYugaEngine()
    
    # 1. TEST MANTRA (Visuddha) -> GROWTH
    mantra_obj = ConcreteMantra()
    result = engine.apply_decay(mantra_obj)
    # 1.08 Growth
    assert result > Decimal("1.0"), f"Mantra should grow! Got {result}"
    assert result == Decimal("1.08"), "Visuddha constant mismatch."
    
    # 2. TEST VOID -> COLLAPSE
    void_obj = VoidObject()
    result = engine.apply_decay(void_obj)
    assert result == ZERO, "Void should collapse to Zero."
    
    # 3. TEST MATTER -> DECAY
    # Calculation: (.3*.1 + .5*.5 + .2*.9) * 0.9
    # (.03 + .25 + .18) * 0.9
    # (.46) * 0.9 = 0.414
    mat_obj = MaterialObject()
    result = engine.apply_decay(mat_obj)
    assert result < ONE, "Matter should decay."
    assert result > ZERO, "Matter should exist."
    print(f"\nMaterial Decay Factor: {result}")
