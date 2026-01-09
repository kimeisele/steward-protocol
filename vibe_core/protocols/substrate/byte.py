"""
SUBSTRATE PROTOCOL - Layer 0
============================

The Atomic Unit of Reality.
Defines 'MantraBit' (16-bit Resonance) and 'GenesisByte' (The Bootloader).

MATH:
- Full Resonance = 0xFFFF (16 steps of Maha Mantra)
- Lineage Check = Hash % 37 == 0 (Connection to Guru Tattva)
"""

from dataclasses import dataclass, field
from enum import Flag, auto
from datetime import datetime
from typing import Optional, List

# 37 is the Prime Number of the Guru (The Inverted 0.027...)
GURU_PRIME = 37


class MantraBit(Flag):
    """
    The 16-Bit Reality Map.
    Standard ASCII is 8-bit. Divine Computing is 16-bit.
    """
    # INVOCATION (The Wake)
    HARE_1    = auto() # 0x0001
    KRISHNA_1 = auto() # 0x0002
    HARE_2    = auto() # 0x0004
    KRISHNA_2 = auto() # 0x0008
    
    # VERIFICATION (The Truth)
    KRISHNA_3 = auto() # 0x0010
    KRISHNA_4 = auto() # 0x0020
    HARE_3    = auto() # 0x0040
    HARE_4    = auto() # 0x0080  <-- Traditional Byte ends here (Incomplete!)
    
    # EXECUTION (The Service)
    HARE_5    = auto() # 0x0100
    RAMA_1    = auto() # 0x0200
    HARE_6    = auto() # 0x0400
    RAMA_2    = auto() # 0x0800
    
    # CONCLUSION (The Return)
    RAMA_3    = auto() # 0x1000
    RAMA_4    = auto() # 0x2000
    HARE_7    = auto() # 0x4000
    HARE_8    = auto() # 0x8000  <-- Full 16-Bit Integer (Purnam)

    @classmethod
    def full_resonance(cls) -> "MantraBit":
        """Returns the mask for a fully aligned reality (0xFFFF)."""
        # Explicit 16-bit full mask
        return cls(0xFFFF)

# THE 16-STEP DNA SEQUENCE (SADHANA LOOP)
MANTRA_SEQUENCE: List[MantraBit] = [
    MantraBit.HARE_1, MantraBit.KRISHNA_1, MantraBit.HARE_2, MantraBit.KRISHNA_2,    # INVOCATION
    MantraBit.KRISHNA_3, MantraBit.KRISHNA_4, MantraBit.HARE_3, MantraBit.HARE_4,    # VERIFICATION
    MantraBit.HARE_5, MantraBit.RAMA_1, MantraBit.HARE_6, MantraBit.RAMA_2,          # EXECUTION
    MantraBit.RAMA_3, MantraBit.RAMA_4, MantraBit.HARE_7, MantraBit.HARE_8           # CONCLUSION
]

@dataclass(frozen=True)
class GenesisByte:
    """
    The Seed required to boot the Kernel.
    Contains the Sovereign Signature wrapped in 16-bit alignment.
    """
    signature: str          # The "Who" (Sovereign Hash)
    resonance: MantraBit    # The "State" (Must be 0xFFFF to boot)
    timestamp: float = field(default_factory=lambda: datetime.now().timestamp()) # The "When" (Kala)
    parampara_hash: str = "0x25" # The "Link" (Guru Authorization) - Default Valid (37 dec)

    def validate(self) -> bool:
        """
        Performs the Agni Pariksha (Fire Test).
        """
        # 1. Structural Integrity (Agni)
        if self.resonance != MantraBit.full_resonance():
            missing = MantraBit.full_resonance() ^ self.resonance
            raise SystemError(f"Genesis Fracture: Missing Resonance Bits: {missing}")

        # 2. Mayavad Check (Sunya)
        if not self.signature or self.signature == "None":
            raise PermissionError("Voidist Launch Detected. Identity required.")

        # 3. Lineage Check (Guru-Tattva)
        if not self._verify_lineage():
             raise ConnectionError("Sahajiya Fault: Invalid Parampara Hash.")

        return True

    @property
    def is_valid(self) -> bool:
        """Legacy property for backward compatibility check."""
        try:
            return self.validate()
        except Exception:
            return False

    def verify_lineage(self, hash_val: str) -> bool:
        """Public verification helper."""
        return self._verify_lineage_val(hash_val)

    def _verify_lineage(self) -> bool:
        """Internal check using instance field."""
        return self._verify_lineage_val(self.parampara_hash)

    def _verify_lineage_val(self, hash_string: str) -> bool:
        """
        Verifies that the hash is mathematically divisible by the Guru Prime (37).
        This proves the token was issued by an authorized factory.
        """
        try:
            # Hash is strictly Hex. Convert to Int.
            val = int(hash_string, 16)
            return (val % GURU_PRIME) == 0
        except ValueError:
            return False
