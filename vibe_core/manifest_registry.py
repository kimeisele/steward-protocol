"""
InMemoryManifestRegistry - Agent Manifest Registry Implementation

Extracted from kernel_impl.py to reduce kernel size.
"""

import logging
from typing import Dict, List, Optional

from .protocols import AgentManifest, ManifestRegistry

logger = logging.getLogger("MANIFEST_REGISTRY")


class InMemoryManifestRegistry(ManifestRegistry):
    """Agent Manifest Registry - Identity declarations"""

    def __init__(self):
        self.manifests: Dict[str, AgentManifest] = {}

    def register(self, manifest: AgentManifest) -> None:
        """Register an agent manifest"""
        self.manifests[manifest.agent_id] = manifest
        logger.info(f"Manifest registered: {manifest.agent_id} ({manifest.name})")

    def lookup(self, agent_id: str) -> Optional[AgentManifest]:
        """Look up manifest by agent_id"""
        return self.manifests.get(agent_id)

    def find_by_capability(self, capability: str) -> List[AgentManifest]:
        """Find agents with a specific capability"""
        return [m for m in self.manifests.values() if capability in m.capabilities]

    def list_all(self) -> List[AgentManifest]:
        """List all registered manifests"""
        return list(self.manifests.values())
