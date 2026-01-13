"""
TAPAS (Austerity) - Implementation of IResourceManager.
Layer: -1 (Naga Loka / Substrate Enforcement)
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "yamaraja"
__position__ = 15
__genesis__ = "0xceb06deb"  # GenesisByte: parampara % 37 == 0

from typing import Optional

from vibe_core.protocols.defense import IResourceManager


class ResourceManager(IResourceManager):
    def enforce_sobriety(self, resource_id: str, limits: Optional[object] = None) -> bool:
        return True
