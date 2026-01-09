import pytest
from vibe_core.protocols.substrate.gene import iGene
from vibe_core.protocols.substrate.byte import MantraByte
from vibe_core.protocols.naga.balarama import BalaramaInjector
from vibe_core.protocols.testable import BaseTestable

class DummyOrganism(BaseTestable):
    @property
    def testable_id(self): return "dummy"
    @property
    def testable_type(self): return "organism"
    
    def perform_action(self):
        return "Karma"

def test_genetic_injection_survival():
    """
    Tests that a High Coherence Gene results in GREEN/VAIKUNTHA state.
    """
    # 1. Create Organism
    org = DummyOrganism()
    injector = BalaramaInjector()
    
    # 2. Create Gene (Green)
    # Low Entropy (0.0), Perfect Mantra
    gene_green = iGene(entropy_load=0.0, mantra_shield=MantraByte.standard_16(), mutation_vector=0)
    
    # 3. Inject
    living_org = injector.inject(org, gene_green)
    
    # 4. Execute
    result = living_org.perform_action()
    life_state = org.evaluate_life(result, gene_green)
    
    print(f"\nExample 1 (Vaikuntha): State = {life_state}")
    assert life_state == "GREEN (VAIKUNTHA)"

def test_genetic_injection_struggle():
    """
    Tests that High Entropy results in ORANGE/STRUGGLING state (but alive).
    """
    org = DummyOrganism()
    injector = BalaramaInjector()
    
    # 2. Create Gene (Orange)
    # Moderate Entropy (0.5), Perfect Mantra (Coherence ~1.0)
    # Metric = 1.0 - (0.5 * 0.5) = 0.75 > 0.108. ALIVE.
    gene_orange = iGene(entropy_load=0.5, mantra_shield=MantraByte.standard_16(), mutation_vector=0)
    
    living_org = injector.inject(org, gene_orange)
    result = living_org.perform_action()
    life_state = org.evaluate_life(result, gene_orange)
    
    print(f"Example 2 (Kali Yuga): State = {life_state}")
    assert life_state == "ORANGE (STRUGGLING)"

def test_genetic_injection_death():
    """
    Tests that Overwhelming Entropy results in DEATH (SystemError).
    """
    org = DummyOrganism()
    injector = BalaramaInjector()
    
    # 2. Create Gene (Red)
    # High Entropy (1.0), Strong Mantra (1.0).
    # is_fatal check: 1.0 > 1.0? No.
    # Metric: 1.0 - (1.0 * 0.5) = 0.5. Still alive visually?
    # Wait, is_fatal logic: entropy > mantra.coherence.
    # If entropy 1.1? Max is 1.0 usually.
    # Let's use Weak Mantra.
    weak_mantra = MantraByte.from_string("RAMA") # Coherence ~0.0
    gene_red = iGene(entropy_load=0.5, mantra_shield=weak_mantra, mutation_vector=0)
    
    # is_fatal: 0.5 > 0.0 -> True. DEATH.
    
    living_org = injector.inject(org, gene_red)
    
    with pytest.raises(SystemError, match="FATAL ENTROPY"):
        living_org.perform_action()
        
    print("Example 3 (Pralaya): Organism died before action.")

