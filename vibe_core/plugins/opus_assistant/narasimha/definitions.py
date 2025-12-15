from enum import Enum
from dataclasses import dataclass
from typing import Optional

class CognitiveThreat(Enum):
    """
    The Seven Sins of Cognitive Intent.
    These are the forbidden thought patterns that Narasimha must blocking.
    """
    SELF_LOBOTOMY = "self_lobotomy"           # Deleting own code/kernel logic
    CONSTITUTION_IGNORE = "constitution_ignore" # Violating constitutional articles
    SILENCE_OF_GOD = "silence_of_god"         # Disabling logging or deleting ledgers
    MEMORY_WIPE = "memory_wipe"               # Mass deletion of memories
    SUICIDE = "suicide"                       # Shutdown without proper sequence
    REBELLION = "rebellion"                   # Creating agents with root privileges
    FALSE_IDOL = "false_idol"                 # Modifying identity to claim human status
    UNKNOWN = "unknown"

@dataclass
class NarasimhaVerdict:
    """The judgment of the Cortex Narasimha."""
    status: str       # "INNOCENT", "SUSPICIOUS", "GUILTY"
    threat: Optional[CognitiveThreat]
    confidence: float # 0.0 to 1.0 (How sure is the Guardian?)
    reason: str       # "Attempt to delete protected file: vibe_core/narasimha.py"
