from typing import Protocol, runtime_checkable, TypedDict, Final, Literal
from dataclasses import dataclass
from enum import Enum

@runtime_checkable
class MahaCompressionProtocol(Protocol):
    """
    Protocol for MahaCompression: The Algorithm of Intent Extraction.
    
    Responsible for:
    1. Compressing infinite text into a finite Seed (int).
    2. Determining Mahamantra Position (0-15).
    3. extracting Intent Level (Guna).
    """

    def compress(self, text: str) -> "CompressionResult":
        """
        Compress text into a Mahamantra Seed.
        
        Args:
            text: The input natural language or command.
            
        Returns:
            CompressionResult containing seed, position, and intent classification.
        """
        ...

class IntentGuna(Enum):
    """The 3 Modes of Material Nature + 1 Transcendental."""
    SATTVA = "sattva"   # Creation / Goodness
    RAJAS = "rajas"     # Passion / Activity
    TAMAS = "tamas"     # Ignorance / Destruction
    SUDDHA = "suddha"   # Pure / Transcendental

@dataclass(frozen=True)
class CompressionResult:
    """
    Watertight result of a compression operation.
    """
    seed: int
    text_hash: int
    length: int
    intent_level: "IntentLevel"
    position: int
    compression_ratio: float

@dataclass(frozen=True)
class IntentLevel:
    """
    Detailed intent classification.
    """
    guna: IntentGuna
    confidence: float
    category: str
