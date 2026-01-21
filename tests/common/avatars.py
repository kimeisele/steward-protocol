"""
AVATARS.PY - The Test Sovereigns (Vidura & Friends)
===================================================
"Tests are not simulations. They are rituals."

This module provides REAL implementations of PersonProtocol for testing.
NO MOCKS ALLOWED. These objects have:
1. Identity (SovereignContext)
2. Will (Capabilities)
3. Tattva (Quality Level)
"""

from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime

# Adjust imports based on your exact structure
from vibe_core.protocols.types import PersonProtocol, Capability, SovereignContext, TranscendentalQuality


@dataclass
class TestDevotee:
    """
    Vidura: The Honest Tester.
    A fully realized 'Person' for test scenarios.
    Implicitly implements PersonProtocol (Duck Typing).
    """

    name: str = "Vidura_The_Tester"
    tattva_level: int = TranscendentalQuality.TRUTHFULNESS.value  # Level 8
    capabilities: List[Capability] = field(default_factory=list)

    # THE SOUL (Crypto-Identity)
    # Hardcoded 'valid' signature for tests
    _context: SovereignContext = field(
        default_factory=lambda: SovereignContext(
            identity="did:vibe:test:vidura-001", tattva_level=TranscendentalQuality.TRUTHFULNESS
        )
    )

    @property
    def sovereign_context(self) -> SovereignContext:
        """Returns the Immutable Identity."""
        return self._context

    # --- HELPER METHODS (The 'Boons') ---

    def grant_capability(self, cap_name: str):
        """Mechanically adds a capability (simulating training/initiation)."""
        self.capabilities.append(
            Capability(
                name=cap_name,
                risk_level=1,  # Default safe
            )
        )

    def revoke_all(self):
        """Resets capabilities (Tyaga)."""
        self.capabilities = []

    def authorize(self, action: str) -> bool:
        return True


@dataclass
class TestDemon:
    """
    Duryodhana: The Unauthorized Accessor.
    Used to test rejection logic.
    Implicitly implements PersonProtocol.
    """

    name: str = "Duryodhana_The_Usurper"
    capabilities: List[Capability] = field(default_factory=list)

    @property
    def sovereign_context(self) -> SovereignContext:
        # Invalid Context (Unsigned / Low Tattva)
        return SovereignContext(
            identity="did:vibe:test:asura-666",
            tattva_level=TranscendentalQuality.EXISTENCE,  # Level 1 (Too low)
        )

    def authorize(self, action: str) -> bool:
        return True


@dataclass
class TestService:
    """
    A Robot. Not a Person.
    Used to verify Dwarapala rejects non-persons.
    """

    service_id: str = "service_auto_bot_v1"
    capabilities: List[Capability] = field(default_factory=list)

    # No 'sovereign_context' property implies it is Prakriti (Matter), not Purusha.
    def serve(self):
        pass
