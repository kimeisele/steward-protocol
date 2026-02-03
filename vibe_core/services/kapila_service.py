"""
KAPILA SERVICE - Thin Proxy to Mahamantra
=========================================

MAHAMANTRA IS MONARCH. This file is a thin proxy.
The real implementation lives in protocols/mahajanas/kapila/service.py
and is accessed through mahamantra/dharma/kapila.

Kernel imports from here → we re-export from mahamantra → done.
"""

# === RE-EXPORT FROM MAHAMANTRA (THE MONARCH) ===
from vibe_core.mahamantra.dharma.kapila import KapilaService

# === MAHAJANA DECLARATION (derived from mahamantra) ===
__mahajana__ = "kapila"
__position__ = 6


def get_kapila_service() -> KapilaService:
    """
    Get KapilaService through ServiceRegistry (NAGA-wrapped).

    This factory ensures singleton pattern and NAGA governance.
    """
    from vibe_core.di import ServiceRegistry
    from vibe_core.protocols.mahajanas.kapila import KapilaProtocol

    existing = ServiceRegistry.get(KapilaProtocol)
    if existing is not None:
        return existing  # type: ignore

    instance = KapilaService()
    ServiceRegistry.register(KapilaProtocol, instance)
    return ServiceRegistry.get(KapilaProtocol)  # type: ignore


__all__ = ["KapilaService", "get_kapila_service"]
