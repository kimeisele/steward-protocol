# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "shambhu"
__position__ = 3
__genesis__ = "0xac6f074d"  # GenesisByte: parampara % 37 == 0

from dataclasses import dataclass
from enum import IntEnum, Enum
from typing import Protocol, TypeVar, Set, runtime_checkable

class TranscendentalQuality(IntEnum):
    UNCONSCIOUS = 0
    EXISTENCE = 1
    TRUTHFULNESS = 8
    MATERIAL = 10
    SPIRITUAL = 50
    INCONCEIVABLE_POTENCY = 56 # Acintya

@dataclass
class SovereignContext:
    identity: str
    tattva_level: TranscendentalQuality

# --- NEW ONTOLOGY (USER REFACTOR) ---

# GENERIC TYPE VARS (No More Any)
T_Sacred = TypeVar("T_Sacred") # Data protected by Prahlad
T_Result = TypeVar("T_Result")

@dataclass(frozen=True)
class Capability:
    """
    A 'Verb' that a Person is allowed to execute.
    """
    name: str
    risk_level: int # 1=Safe, 10=Ugra (Dangerous)

@runtime_checkable
class PersonProtocol(Protocol):
    """
    A 'Person' (Purusha) who has Will and Capabilities.
    Services are NOT Persons.
    """
    @property
    def name(self) -> str: ...
    
    @property
    def capabilities(self) -> Set[Capability]: ...
    
    def authorize(self, action: str) -> bool: ...

@runtime_checkable
class ServiceProtocol(Protocol):
    """
    A 'Service' (Prakriti). It functions but has no Will.
    It CANNOT hold Capabilities.
    """
    def serve(self) -> None: ...
