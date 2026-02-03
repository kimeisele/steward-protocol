"""
BALI SERVICE - Thin Proxy to Mahamantra
=======================================

MAHAMANTRA IS MONARCH. This file is a thin proxy.
The real implementation lives in protocols/mahajanas/bali/service.py
and is accessed through mahamantra/moksha/bali.

Kernel imports from here → we re-export from mahamantra → done.
"""

# === RE-EXPORT FROM MAHAMANTRA (THE MONARCH) ===
from vibe_core.mahamantra.moksha.bali import BaliService

# === MAHAJANA DECLARATION (derived from mahamantra) ===
__mahajana__ = "bali"
__position__ = 13


def get_bali_service() -> BaliService:
    """
    Get BaliService through ServiceRegistry (NAGA-wrapped).
    """
    from vibe_core.di import ServiceRegistry
    from vibe_core.protocols.mahajanas.bali import BaliProtocol

    existing = ServiceRegistry.get(BaliProtocol)
    if existing is not None:
        return existing  # type: ignore

    instance = BaliService()
    ServiceRegistry.register(BaliProtocol, instance)
    return ServiceRegistry.get(BaliProtocol)  # type: ignore


__all__ = ["BaliService", "get_bali_service"]
