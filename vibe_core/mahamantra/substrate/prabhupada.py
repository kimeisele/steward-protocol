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
from vibe_core.mahamantra.protocols._seed import (
    PARAMPARA,
    MAHAJANA_COUNT,
    HARE_COUNT,
    WORDS,
    END_CORRECTION,
)


class Prabhupada(PrabhupadaProtocol):
    """
    The Bona Fide Link.

    Validates connections to the Parampara.

    NOTE: Use get_prabhupada() to access via ServiceRegistry.
    """

    # MAHAMANTRA SUBSTRATE: Core infrastructure, no auto-wrap needed
    _naga_flooded: bool = True
    _naga_gene: str = "prabhupada"

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
        # NOTE: Identity should have been SET by MahamantraProxy using folder-is-truth.
        # Here we just verify the component HAS identity (labels were populated by proxy).
        if not hasattr(component, "__mahajana__") and not hasattr(component, "mahajana"):
            return False  # No identity claim

        # 2. Signature Extraction
        signature_hex = getattr(component, "__genesis__", getattr(component, "genesis", None))

        if not signature_hex or not isinstance(signature_hex, str):
            return False  # No signature found

        try:
            # 3. Mathematical Validation (The Check)
            signature_val = int(signature_hex, 16)

            # THE LAW: Must be divisible by 37 (The Parampara)
            is_valid = signature_val % PARAMPARA == 0

            return is_valid

        except ValueError:
            return False  # Invalid hex string

    def transmit(self, seed: str) -> str:
        """
        Transmit the instruction As It Is.
        """
        return seed

    def transmit_shakti(self, component: object) -> float:
        """
        Measure and transmit Shakti through the transparent via medium.

        DERIVATION (from _seed.py):
        - BASE_SHAKTI = HARE_COUNT / WORDS = 8/16 = 0.5
        - This is the natural Shakti ratio in the Mahamantra itself
        - END_CORRECTION = HARE_COUNT = "the energy escaping the tube"

        Returns:
            0.0 if channel blocked (no valid link)
            BASE_SHAKTI if channel open (valid Parampara connection)
        """
        # 1. Check if channel is open (Parampara connection)
        if not self.verify_link(component):
            return 0.0  # Blocked channel = no Shakti transmission

        # 2. Calculate BASE_SHAKTI from Seed (NOT hardcoded!)
        # HARE_COUNT / WORDS = 8/16 = the natural Shakti proportion
        base_shakti = HARE_COUNT / WORDS

        # 3. Return base Shakti (channel is open, energy flows)
        # Future: modulate by Guna state, VarnaTensor resonance, etc.
        return base_shakti


# =============================================================================
# SERVICEREGISTRY FACTORY
# =============================================================================

import logging

logger = logging.getLogger("PRABHUPADA")


def get_prabhupada() -> Prabhupada:
    """
    Get Prabhupada through ServiceRegistry.

    ARCHITECTURE:
        Prabhupada is MAHAMANTRA SUBSTRATE - the bona fide link to Parampara.
        Uses ServiceRegistry for singleton pattern but is NOT auto-wrapped
        with NagaProxy (marked with _naga_flooded = True).

    Returns:
        Prabhupada instance (singleton via ServiceRegistry)
    """
    from vibe_core.di import ServiceRegistry

    # Check if already registered
    existing = ServiceRegistry.get(PrabhupadaProtocol)
    if existing is not None:
        return existing  # type: ignore

    # Create new instance
    instance = Prabhupada()

    # Register with ServiceRegistry (no NagaProxy wrap - _naga_flooded = True)
    ServiceRegistry.register(PrabhupadaProtocol, instance)
    logger.info("✅ Prabhupada registered via ServiceRegistry (MAHAMANTRA substrate)")

    return ServiceRegistry.get(PrabhupadaProtocol)  # type: ignore


# Backward compatibility: module-level access via lazy property
# DEPRECATED: Use get_prabhupada() instead
def __getattr__(name: str):
    if name == "prabhupada":
        return get_prabhupada()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
