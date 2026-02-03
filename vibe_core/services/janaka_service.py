"""
JANAKA SERVICE - Thin Proxy to Mahamantra
=========================================

MAHAMANTRA IS MONARCH. This file is a thin proxy.
The real implementation lives in protocols/mahajanas/janaka/service.py
and is accessed through mahamantra/karma/janaka.

Kernel imports from here → we re-export from mahamantra → done.
"""

# === RE-EXPORT FROM MAHAMANTRA (THE MONARCH) ===
from vibe_core.mahamantra.karma.janaka import JanakaService

# === MAHAJANA DECLARATION (derived from mahamantra) ===
__mahajana__ = "janaka"
__position__ = 10


def get_janaka_service() -> JanakaService:
    """
    Get JanakaService through ServiceRegistry (NAGA-wrapped).
    """
    from vibe_core.di import ServiceRegistry
    from vibe_core.protocols.mahajanas.janaka import JanakaProtocol

    existing = ServiceRegistry.get(JanakaProtocol)
    if existing is not None:
        return existing  # type: ignore

    instance = JanakaService()
    ServiceRegistry.register(JanakaProtocol, instance)
    return ServiceRegistry.get(JanakaProtocol)  # type: ignore


__all__ = ["JanakaService", "get_janaka_service"]
