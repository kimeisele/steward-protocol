"""
TEST AVATARS - The Dramatis Personae of the Test Suite.
=======================================================
"Testing is not a Simulation. It is a Dress Rehearsal."

These are REAL implementations of PersonProtocol. 
They have Identity (Context) and Will (Authorize).
They are used to test Prahlad (Memory) and Dwarapala (Gate).
"""

from dataclasses import dataclass, field
from typing import List, Set, Optional
from vibe_core.protocols.types import PersonProtocol, Capability, SovereignContext, TranscendentalQuality

@dataclass
class TestDevotee:
    """
    A Dharmic Actor (e.g. Vidura, Arjuna).
    Implements PersonProtocol fully.
    """
    name: str = "Vidura_The_Tester"
    tattva_level: int = TranscendentalQuality.SPIRITUAL # Level 50 (Valid)
    _capabilities: Set[Capability] = field(default_factory=set)
    _context: Optional[SovereignContext] = None

    def __post_init__(self):
        # Auto-Sign Identity if not provided
        if not self._context:
            self._context = SovereignContext(
                identity=f"did:vibe:test:{self.name.lower()}",
                tattva_level=self.tattva_level
            )

    @property
    def capabilities(self) -> Set[Capability]:
        return self._capabilities

    def add_capability(self, cap_name: str, risk: int = 1):
        """Grant a capability dynamically."""
        self._capabilities.add(Capability(name=cap_name, risk_level=risk))

    def authorize(self, action: str) -> bool:
        """
        The Will.
        A Devotee authorizes Dharmic actions.
        """
        # Simplification: Authorizes everything locally initiated
        return True

@dataclass
class TestDemon:
    """
    An Adharmic Actor (e.g. Hiranyakashipu).
    Technically has Identity, but might fail moral checks.
    Useful for testing 'Identity Crisis' if we strip PersonProtocol (but here we implement it to test rejection logic).
    Wait, Dwarapala checks isinstance(PersonProtocol).
    So if this implements it, it IS a Person.
    To test 'Not a Person', we use a different class or simple object.
    
    This class represents a 'Bad Person' (Person with Bad Intent/Low Tattva).
    """
    name: str = "Hiranyakashipu"
    tattva_level: int = TranscendentalQuality.MATERIAL # Level 10
    _capabilities: Set[Capability] = field(default_factory=set)
    
    @property
    def capabilities(self) -> Set[Capability]:
        return self._capabilities

    def authorize(self, action: str) -> bool:
        return True

class TestService:
    """
    A Service (Prakriti).
    Does NOT implement PersonProtocol.
    Used to fail Dwarapala checks.
    """
    def serve(self):
        pass
