"""
BHISHMA SERVICE - Thin Proxy to Mahamantra
==========================================

MAHAMANTRA IS MONARCH. This file is a thin proxy.
The real implementation lives in protocols/mahajanas/bhishma/service.py
and is accessed through mahamantra/karma/bhishma.

Kernel imports from here → we re-export from mahamantra → done.
"""

# === RE-EXPORT FROM MAHAMANTRA (THE MONARCH) ===
from vibe_core.mahamantra.karma.bhishma import BhishmaService

# === MAHAJANA DECLARATION (derived from mahamantra) ===
__mahajana__ = "bhishma"
__position__ = 11


def get_bhishma_service(ledger=None) -> BhishmaService:
    """
    Get BhishmaService through ServiceRegistry (NAGA-wrapped).

    Args:
        ledger: The ledger instance (required for first instantiation)
    """
    from vibe_core.di import ServiceRegistry
    from vibe_core.protocols.mahajanas.bhishma import BhishmaProtocol

    existing = ServiceRegistry.get(BhishmaProtocol)
    if existing is not None:
        return existing  # type: ignore

    if ledger is None:
        raise ValueError("BhishmaService requires a ledger for first instantiation")

    instance = BhishmaService(ledger)
    ServiceRegistry.register(BhishmaProtocol, instance)
    return ServiceRegistry.get(BhishmaProtocol)  # type: ignore


__all__ = ["BhishmaService", "get_bhishma_service"]
