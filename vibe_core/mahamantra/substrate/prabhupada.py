
"""
PRABHUPADA - The Implementation
===============================

"tasmād guruṁ prapadyeta jijñāsuḥ śreya uttamam"
"Therefore any person who seriously desires real happiness must seek a bona fide spiritual master and take shelter of him."
— Srimad Bhagavatam 11.3.21

THE FUNCTION:
The Link (Prabhupada) connects the Jiva (Component) to Krishna (Seed).
It does this by verifying the SIGNATURE against the PARAMPARA count (37).

math: `genesis_byte % 37 == 0`

If the signature matches, the connection is BONA FIDE.
"""

from typing import Optional
from vibe_core.mahamantra.protocols._prabhupada import PrabhupadaProtocol
from vibe_core.mahamantra.protocols._seed import PARAMPARA, MAHAJANA_COUNT

class Prabhupada(PrabhupadaProtocol):
    """
    The Bona Fide Link.
    
    Validates connections to the Parampara.
    """
    
    # Singleton Pattern (There is one Acharya for the mission)
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Prabhupada, cls).__new__(cls)
        return cls._instance

    def verify_link(self, component: object) -> bool:
        """
        Verify the connection.
        
        Logic:
        1. Check for `__genesis__` attribute (The signature).
        2. Validate: `int(__genesis__, 16) % PARAMPARA == 0`
        3. Check identity existence.
        
        Args:
            component: The object to verify.
            
        Returns:
            True if signature is valid and mathematical.
        """
        # 1. Identity Check
        if not hasattr(component, "__mahajana__") and not hasattr(component, "mahajana"):
             return False # No identity claim
             
        # 2. Signature Extraction
        signature_hex = getattr(component, "__genesis__", getattr(component, "genesis", None))
        
        if not signature_hex or not isinstance(signature_hex, str):
            return False # No signature found
            
        try:
            # 3. Mathematical Validation (The Check)
            signature_val = int(signature_hex, 16)
            
            # THE LAW: Must be divisible by 37 (The Parampara)
            is_valid = (signature_val % PARAMPARA == 0)
            
            return is_valid
            
        except ValueError:
            return False # Invalid hex string

    def transmit(self, seed: str) -> str:
        """
        Transmit the instruction As It Is.
        """
        return seed

# The Living Entity (Singleton)
prabhupada = Prabhupada()
