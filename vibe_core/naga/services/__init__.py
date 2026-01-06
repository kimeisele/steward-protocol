"""
NAGA Services - The Invisible Guardians (NSA - NAGA Service Agency).

HOLON UPGRADE: Lazy Loading to prevent import cycles.
Services are only loaded when accessed, not at module import.

Infrastructure Layer (Real Nagas - 8 Lords):
- Sesha (Data/Truth/Ledger)
- Vasuki (Network/Boundary)
- Takshaka (Security/Guard)
- Kaliya (Quarantine/Isolation)
- Karkotaka (Crypto/Secrets/Magic)
- Kulika (Schema/Registry/Order)
- Padma (Cache/Treasury)
- Shankha (Broadcast/Pubsub)

Governance Layer (Personnel - 4 Lords):
- Narada (Spy/Observer)
- Chitragupta (Profiler/Behavioral)
- Prahlad (Resilience/Hardening)
- Ananta (Gene Splicer/Auto-Flood)

Total: 12 Lords ACTIVE

Usage:
    # Lazy - only loads when accessed
    from vibe_core.naga.services import SeshaService

    # Or direct import (bypasses lazy loading)
    from vibe_core.naga.services.sesha import SeshaService
"""

from typing import TYPE_CHECKING, Any

# TYPE_CHECKING imports for type hints only (not runtime)
if TYPE_CHECKING:
    from vibe_core.naga.services.ananta import AnantaService as _AnantaService
    from vibe_core.naga.services.chitragupta import ChitraguptaService as _ChitraguptaService
    from vibe_core.naga.services.kaliya import KaliyaService as _KaliyaService
    from vibe_core.naga.services.karkotaka import KarkotakaService as _KarkotakaService
    from vibe_core.naga.services.kulika import KulikaService as _KulikaService
    from vibe_core.naga.services.narada import NaradaService as _NaradaService
    from vibe_core.naga.services.padma import PadmaService as _PadmaService
    from vibe_core.naga.services.prahlad import PrahladService as _PrahladService
    from vibe_core.naga.services.sesha import SeshaService as _SeshaService
    from vibe_core.naga.services.shankha import ShankhaService as _ShankhaService
    from vibe_core.naga.services.takshaka import TakshakaService as _TakshakaService
    from vibe_core.naga.services.vasuki import VasukiService as _VasukiService


# =============================================================================
# LAZY LOADING - Import only when accessed
# =============================================================================

_SERVICE_MAP = {
    # Infrastructure Layer (Real Nagas - 8)
    "SeshaService": ("vibe_core.naga.services.sesha", "SeshaService"),
    "VasukiService": ("vibe_core.naga.services.vasuki", "VasukiService"),
    "TakshakaService": ("vibe_core.naga.services.takshaka", "TakshakaService"),
    "KaliyaService": ("vibe_core.naga.services.kaliya", "KaliyaService"),
    "KarkotakaService": ("vibe_core.naga.services.karkotaka", "KarkotakaService"),
    "KulikaService": ("vibe_core.naga.services.kulika", "KulikaService"),
    "PadmaService": ("vibe_core.naga.services.padma", "PadmaService"),
    "ShankhaService": ("vibe_core.naga.services.shankha", "ShankhaService"),
    # Governance Layer (Personnel - 4)
    "NaradaService": ("vibe_core.naga.services.narada", "NaradaService"),
    "ChitraguptaService": ("vibe_core.naga.services.chitragupta", "ChitraguptaService"),
    "PrahladService": ("vibe_core.naga.services.prahlad", "PrahladService"),
    "AnantaService": ("vibe_core.naga.services.ananta", "AnantaService"),
}

_loaded_services: dict[str, Any] = {}


def __getattr__(name: str) -> Any:
    """
    Lazy load services on first access.

    HOLON PATTERN: Each service is loaded independently,
    preventing import cycles that cause deadlocks.
    """
    if name in _SERVICE_MAP:
        if name not in _loaded_services:
            module_path, class_name = _SERVICE_MAP[name]
            import importlib
            module = importlib.import_module(module_path)
            _loaded_services[name] = getattr(module, class_name)
        return _loaded_services[name]

    raise AttributeError(f"module 'vibe_core.naga.services' has no attribute '{name}'")


def __dir__() -> list[str]:
    """List available services for autocomplete."""
    return list(_SERVICE_MAP.keys())


__all__ = [
    # Infrastructure Layer (Real Nagas - 8)
    "SeshaService",
    "VasukiService",
    "TakshakaService",
    "KaliyaService",
    "KarkotakaService",
    "KulikaService",
    "PadmaService",
    "ShankhaService",
    # Governance Layer (Personnel - 4)
    "NaradaService",
    "ChitraguptaService",
    "PrahladService",
    "AnantaService",
]
