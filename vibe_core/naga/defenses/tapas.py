"""
TAPAS (Austerity) - Implementation of IResourceManager.
Layer: -1 (Naga Loka / Substrate Enforcement)
"""

from typing import Optional

from vibe_core.protocols.defense import IResourceManager


class ResourceManager(IResourceManager):
    def enforce_sobriety(self, resource_id: str, limits: Optional[object] = None) -> bool:
        return True
