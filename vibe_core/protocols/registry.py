"""
Manifest Registry Protocol - Interface Definition

BLOCKER #2: Layer 1 Protocol (no implementations)
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from .agent import AgentManifest


class ManifestRegistry(ABC):
    """Agent manifest registry interface"""

    @abstractmethod
    def register(self, manifest: AgentManifest) -> None:
        """Register an agent manifest"""
        pass

    @abstractmethod
    def lookup(self, agent_id: str) -> Optional[AgentManifest]:
        """Look up manifest by agent_id"""
        pass

    @abstractmethod
    def find_by_capability(self, capability: str) -> List[AgentManifest]:
        """Find agents with a specific capability"""
        pass

    @abstractmethod
    def list_all(self) -> List[AgentManifest]:
        """List all registered manifests"""
        pass
