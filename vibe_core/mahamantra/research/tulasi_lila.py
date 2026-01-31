"""
TULASI LILA - The Living Process Research
=========================================

"vrindayai tulasi-devyai priyayai kesavasya ca
krsna-bhakti-prade devi satyavatyai namo namah"

This module models the LIVING PROCESS of Tulasi Care and Offering.
It moves beyond the mathematical "Grace Factor" (8) to the actual LILA.
"""

# === MAHAJANA DECLARATION ===
__mahajana__ = "shuka"
__position__ = 14
__genesis__ = "0xABC12345"

from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Optional, Tuple
import datetime

# Import research dependencies
from vibe_core.mahamantra.research.bhoga_prasadam import transform, KSETRAJNA, PRASADAM
from vibe_core.mahamantra.protocols._seed import (
    HARE_COUNT, 
    KRISHNA_COUNT,
    MAHA_QUANTUM,
    PANCHA,
    TRINITY
)

# =============================================================================
# CONSTANTS: THE ECOSYSTEM
# =============================================================================

class Element(Enum):
    PRITHVI = "Earth/Substrate"  # Soil
    JALA = "Water"               # Watering
    AGNI = "Fire/Light"          # Surya/Lamps
    VAYU = "Air"                 # Fresh Air
    AKASH = "Ether/Sound"        # Mantras/Kirtan

class OfferingState(Enum):
    BHOGA = "Raw/Un-offered"
    OFFERED_TO_GURU = "In Transit (Guru)"
    OFFERED_TO_PANCHA_TATTVA = "In Transit (Pancha Tattva)"
    ACCEPTED_BY_KRISHNA = "Accepted (Maha-Prasadam)"
    REJECTED = "Rejected (No Devotion/Forbidden Items)"

# =============================================================================
# PART 1: THE LIVING TULASI (Care Protocol)
# =============================================================================

@dataclass
class TulasiHealth:
    soil_moisture: float  # 0.0 to 1.0
    light_level: float    # 0.0 to 1.0 (Surya)
    devotion_received: int # Count of Pranam Mantras
    leaves_available: int

class TulasiDevi:
    """The Living Entity. Not just a simplified 'factor 8'."""
    
    def __init__(self, name: str = "Tulasi"):
        self.name = name
        self.health = TulasiHealth(soil_moisture=0.5, light_level=1.0, devotion_received=0, leaves_available=108)
        self.last_watered = datetime.datetime.now()
        
    def offer_pranam(self, mantra: str):
        """
        Offer respect to Tulasi Devi.
        'vrindayai tulasi-devyai...'
        """
        if "vrindayai" in mantra.lower() and "tulas" in mantra.lower():
            self.health.devotion_received += 1
            print(f"[{self.name}] Pranam accepted. Bhakti level: {self.health.devotion_received}")
        else:
            print(f"[{self.name}] Incomplete mantra. Please recite proper pranam.")

    def water(self, amount: float):
        """Watering service (Jala)."""
        if self.health.soil_moisture > 0.8:
            print(f"[{self.name}] Too much water! Root rot risk.")
        else:
            self.health.soil_moisture += amount
            self.last_watered = datetime.datetime.now()
            print(f"[{self.name}] Watered. Moisture: {self.health.soil_moisture:.2f}")

    def pick_leaf(self, is_dwadasi: bool, recitation: str) -> Optional['TulasiLeaf']:
        """
        Pick a leaf for offering.
        RESTRICTIONS:
        - Never on Dwadasi (Day 12)
        - Must recite 'tulasi-cayana-mantra' (forgiveness)
        """
        if is_dwadasi:
            print(f"[{self.name}] ABORT: Today is Dwadasi! Catching her leaves is forbidden.")
            return None
            
        if "cayana" not in recitation.lower() and "forgive" not in recitation.lower():
             print(f"[{self.name}] ABORT: Must ask for permission/forgiveness when picking.")
             return None
             
        if self.health.leaves_available > 0:
            self.health.leaves_available -= 1
            return TulasiLeaf(origin=self.name, picked_with_mantra=True)
        
        return None

@dataclass
class TulasiLeaf:
    origin: str
    picked_with_mantra: bool
    potency: int = HARE_COUNT * MAHA_QUANTUM  # 8 * 137 = 1096 (The standard potency)

# =============================================================================
# PART 2: THE OFFERING PIPELINE (Parampara)
# =============================================================================

@dataclass
class BhogaItem:
    name: str # e.g. "Fruit", "Water"
    is_vegetarian: bool
    quality: int # 24 (Kshetra)

@dataclass
class Prasadam:
    original_item: str
    transcendental_value: int # The '1096' value
    mercy_factor: int

class OfferingPipeline:
    """The path from Bhoga to Prasadam via Parampara."""
    
    @staticmethod
    def offer(item: BhogaItem, tulasi: Optional[TulasiLeaf], devotion_score: int) -> Prasadam:
        """
        The Complete Offering Process.
        Ref: BG 9.26 (patram puspam phalam toyam)
        """
        print(f"\n--- OFFERING: {item.name} ---")
        
        # 1. VALIDATION (KRISHNA'S RULES)
        if not item.is_vegetarian:
            print("REJECTED: Krishna does not accept meat/fish/eggs.")
            return Prasadam(item.name, 0, 0)
            
        if tulasi is None:
            print("WARNING: No Tulasi leaf! Offering is incomplete but accepted via chanting if sincere.")
            # We proceed but with lower potency
            tulasi_factor = 1
        else:
            print(f"VALID: Tulasi Leaf present ('{tulasi.origin}').")
            tulasi_factor = HARE_COUNT  # 8
            
        # 2. GURU (Srila Prabhupada)
        # Guru adds his mercy (Observer + 1)
        guru_mercy = KSETRAJNA # 1
        print("STEP 1: Offered to Guru (Parampara).")
        
        # 3. PANCHA TATTVA
        # They are very merciful. They amplify the devotion.
        # Amplification = Devotion Score * Pancha(5)
        pancha_mercy = devotion_score * PANCHA
        print(f"STEP 2: Offered to Pancha Tattva. (Amplification: {pancha_mercy})")
        
        # 4. KRISHNA (The Enjoyer)
        # He accepts if: Vegetarian AND (Tulasi OR High Devotion)
        # Formula: (Bhoga(24) + Guru(1)) * Tulasi(8) * Devotion
        
        # Base Transformation (from bhoga_prasadam.py)
        # 24 -> 25
        base_prasadam_val, _ = transform(item.quality)
        
        # The Final Value Calculation
        # This matches our 1096 discovery:
        # If perfect: 137 (seed) * 8 (tulasi) = 1096
        
        final_value = (base_prasadam_val + pancha_mercy) * tulasi_factor
        
        print(f"STEP 3: Krishna accepts! Value: {final_value}")
        
        return Prasadam(
            original_item=item.name,
            transcendental_value=final_value,
            mercy_factor=guru_mercy + pancha_mercy
        )

# =============================================================================
# MAIN (LILA SIMULATION)
# =============================================================================

def run_simulation():
    print("=== TULASI LILA SIMULATION ===\n")
    
    # 1. Setup Tulasi
    tulasi = TulasiDevi("Vrindavan-Tulasi")
    tulasi.offer_pranam("om vrindayai tulasi-devyai namah")
    tulasi.water(0.1)
    
    # 2. Pick Leaf (Correctly)
    leaf = tulasi.pick_leaf(is_dwadasi=False, recitation="om tulasi-cayana... forgive me")
    
    if leaf:
        print(f"Picked Leaf: {leaf}")
        
    # 3. Prepare Bhoga
    fruit = BhogaItem("Mango", is_vegetarian=True, quality=24)
    meat = BhogaItem("Steak", is_vegetarian=False, quality=24)
    
    # 4. Perform Offering
    print("\n--- ATTEMPT 1: The Proper Offering ---")
    prasadam_1 = OfferingPipeline.offer(item=fruit, tulasi=leaf, devotion_score=10)
    print(f"Result: {prasadam_1}")
    
    print("\n--- ATTEMPT 2: The Forbidden Offering ---")
    prasadam_2 = OfferingPipeline.offer(item=meat, tulasi=leaf, devotion_score=0)
    print(f"Result: {prasadam_2}")
    
    print("\n--- ATTEMPT 3: The Forgetful Offering (No Tulasi) ---")
    prasadam_3 = OfferingPipeline.offer(item=fruit, tulasi=None, devotion_score=5)
    print(f"Result: {prasadam_3}")

if __name__ == "__main__":
    run_simulation()
