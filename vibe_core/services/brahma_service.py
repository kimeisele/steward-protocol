"""
BRAHMA SERVICE - Thin Proxy to Mahamantra
=========================================

MAHAMANTRA IS MONARCH. This file is a thin proxy.
The real implementation lives in protocols/mahajanas/brahma/service.py
and is accessed through mahamantra/genesis/brahma.

Kernel imports from here → we re-export from mahamantra → done.
"""

# === RE-EXPORT FROM MAHAMANTRA (THE MONARCH) ===
from vibe_core.mahamantra.genesis.brahma import BrahmaService

# === MAHAJANA DECLARATION (derived from mahamantra) ===
__mahajana__ = "brahma"
__position__ = 1


def get_brahma_service(ledger=None) -> BrahmaService:
    """
    Get BrahmaService through ServiceRegistry (NAGA-wrapped).

    Args:
        ledger: The ledger instance (required for first instantiation)
    """
    from vibe_core.di import ServiceRegistry
    from vibe_core.protocols.mahajanas.brahma import BrahmaProtocol

    existing = ServiceRegistry.get(BrahmaProtocol)
    if existing is not None:
        return existing  # type: ignore

    if ledger is None:
        raise ValueError("BrahmaService requires a ledger for first instantiation")

    instance = BrahmaService(ledger)
    ServiceRegistry.register(BrahmaProtocol, instance)
    return ServiceRegistry.get(BrahmaProtocol)  # type: ignore


__all__ = ["BrahmaService", "get_brahma_service"]
