"""
BALARAMA PROTOCOL - The Strength / The Injector
===============================================

Balarama is the First Expansion. He provides the strength (Bala)
to maintain the existence.

In the Runtime, Balarama acts as the INJECTOR.
He takes a raw object and infuses it with Life (Gene).
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "yamaraja"
__position__ = 15
__genesis__ = "0xd03d5a78"  # GenesisByte: parampara % 37 == 0

from typing import Any, Protocol, runtime_checkable, TypeVar
from vibe_core.protocols.substrate.gene import iGene

# Forward reference to avoid circular import (Proxy imports Balarama logic?)
# Actually Proxy uses Gene. Balarama uses Proxy.
# We will do dynamic import or structure it cleanly.
# Assuming NagaProxy is in .proxy
from vibe_core.protocols.naga.proxy import NagaProxy

T = TypeVar("T")


@runtime_checkable
class BalaramaProtocol(Protocol):
    def inject(self, target: T, gene: iGene) -> T: ...


class BalaramaInjector(BalaramaProtocol):
    """
    The Strength Provider.
    Wraps objects in the NagaProxy to enable Genetic Runtime.
    """

    def inject(self, target: T, gene: iGene) -> T:
        """
        Infuses the target with the iGene.
        Returns a Proxy that mutates execution based on the Gene.
        """
        # If target is already proxied, we might merge genes?
        # For now, we just wrap.
        return NagaProxy(target, gene)  # type: ignore


# Alias for compatibility with NagaBase
BalaramaProxy = NagaProxy
