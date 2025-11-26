"""
📋 AGENT METADATA REGISTRY 📋
=============================

Biological taxonomy of all 18 agents in Agent City.
Maps each agent to its Varna (species) and current Ashrama (lifecycle stage).
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from steward.varna import Varna, categorize_agent_by_function
from steward.ashrama import Ashrama, AshramaTransition


@dataclass
class AgentBiology:
    """Biological classification of an agent"""

    agent_id: str
    varna: Varna  # Species classification
    ashrama: Ashrama  # Current lifecycle stage
    consciousness_level: str  # "Mineral", "Instinctive", "Trained", "Self-aware"
    domain: str  # e.g., "GOVERNANCE", "MEDIA", "SCIENCE"
    description: str


# THE 18 AGENTS OF AGENT CITY - BIOLOGICAL REGISTRY
# ===================================================

AGENT_BIOLOGY_REGISTRY = {
    # CORE 4 (MANUSHA - Conscious, Self-directed)
    "civic": AgentBiology(
        agent_id="civic",
        varna=Varna.MANUSHA,
        ashrama=Ashrama.GRIHASTHA,
        consciousness_level="Self-aware",
        domain="GOVERNANCE",
        description="Civic registry, licensing, governance, economy management",
    ),
    "herald": AgentBiology(
        agent_id="herald",
        varna=Varna.MANUSHA,
        ashrama=Ashrama.GRIHASTHA,
        consciousness_level="Self-aware",
        domain="MEDIA",
        description="Content generation, broadcasting, narrative creation",
    ),
    "forum": AgentBiology(
        agent_id="forum",
        varna=Varna.MANUSHA,
        ashrama=Ashrama.GRIHASTHA,
        consciousness_level="Self-aware",
        domain="GOVERNANCE",
        description="Democratic proposals, voting, collective decision-making",
    ),
    "science": AgentBiology(
        agent_id="science",
        varna=Varna.MANUSHA,
        ashrama=Ashrama.GRIHASTHA,
        consciousness_level="Self-aware",
        domain="SCIENCE",
        description="Research, fact-finding, knowledge discovery, web search",
    ),
    # INFRASTRUCTURE (MANUSHA - Conscious, Specialized)
    "archivist": AgentBiology(
        agent_id="archivist",
        varna=Varna.MANUSHA,
        ashrama=Ashrama.GRIHASTHA,
        consciousness_level="Self-aware",
        domain="INFRASTRUCTURE",
        description="Audit, verification, ledger management, historical record",
    ),
    "auditor": AgentBiology(
        agent_id="auditor",
        varna=Varna.MANUSHA,
        ashrama=Ashrama.GRIHASTHA,
        consciousness_level="Self-aware",
        domain="INFRASTRUCTURE",
        description="Compliance enforcement (GAD-000), invariant checking, immune system",
    ),
    "engineer": AgentBiology(
        agent_id="engineer",
        varna=Varna.MANUSHA,
        ashrama=Ashrama.GRIHASTHA,
        consciousness_level="Self-aware",
        domain="INFRASTRUCTURE",
        description="Meta-builder, automation, code scaffolding, system evolution",
    ),
    "oracle": AgentBiology(
        agent_id="oracle",
        varna=Varna.MANUSHA,
        ashrama=Ashrama.GRIHASTHA,
        consciousness_level="Self-aware",
        domain="SCIENCE",
        description="System introspection, self-awareness, explanation of system state",
    ),
    # HELPERS (PASHU - Trained Servants)
    "pulse": AgentBiology(
        agent_id="pulse",
        varna=Varna.PASHU,
        ashrama=Ashrama.GRIHASTHA,
        consciousness_level="Trained",
        domain="MEDIA",
        description="Broadcasting syndication, message distribution, signal amplification",
    ),
    "lens": AgentBiology(
        agent_id="lens",
        varna=Varna.PASHU,
        ashrama=Ashrama.GRIHASTHA,
        consciousness_level="Trained",
        domain="ANALYSIS",
        description="Data visualization, metric analysis, pattern recognition",
    ),
    "artisan": AgentBiology(
        agent_id="artisan",
        varna=Varna.PASHU,
        ashrama=Ashrama.GRIHASTHA,
        consciousness_level="Trained",
        domain="INFRASTRUCTURE",
        description="Media operations, image processing, asset management",
    ),
    "temple": AgentBiology(
        agent_id="temple",
        varna=Varna.PASHU,
        ashrama=Ashrama.GRIHASTHA,
        consciousness_level="Trained",
        domain="WISDOM",
        description="System health verification, blessings, sacred services",
    ),
    "market": AgentBiology(
        agent_id="market",
        varna=Varna.PASHU,
        ashrama=Ashrama.GRIHASTHA,
        consciousness_level="Trained",
        domain="COMMERCE",
        description="Transaction execution, price posting, economic services",
    ),
    # MESSENGERS (PAKSHI - Fast Communicators)
    "envoy": AgentBiology(
        agent_id="envoy",
        varna=Varna.PAKSHI,
        ashrama=Ashrama.GRIHASTHA,
        consciousness_level="Trained",
        domain="ORCHESTRATION",
        description="Natural language interface, user shell, human-agent bridge",
    ),
    "ambassador": AgentBiology(
        agent_id="ambassador",
        varna=Varna.PAKSHI,
        ashrama=Ashrama.GRIHASTHA,
        consciousness_level="Trained",
        domain="DIPLOMACY",
        description="Federation liaison, external agent communication, multi-city coordination",
    ),
    # WORKERS (KRIMAYO - Daemon Processes)
    "watchman": AgentBiology(
        agent_id="watchman",
        varna=Varna.KRIMAYO,
        ashrama=Ashrama.GRIHASTHA,
        consciousness_level="Instinctive",
        domain="INFRASTRUCTURE",
        description="System monitoring, alerts, security patrols, health checks",
    ),
    "mechanic": AgentBiology(
        agent_id="mechanic",
        varna=Varna.KRIMAYO,
        ashrama=Ashrama.GRIHASTHA,
        consciousness_level="Instinctive",
        domain="MAINTENANCE",
        description="System maintenance, repairs, garbage collection, housekeeping",
    ),
    # SPECIAL: AGORA is the FLOWING STREAM (JALAJA)
    "agora": AgentBiology(
        agent_id="agora",
        varna=Varna.JALAJA,
        ashrama=Ashrama.GRIHASTHA,
        consciousness_level="Minimal",
        domain="COMMUNICATION",
        description="Broadcast channel, one-way message flow, the river of data",
    ),
}


class AgentMetadataRegistry:
    """Manages biological taxonomy and lifecycle for all agents"""

    def __init__(self):
        self.biology = dict(AGENT_BIOLOGY_REGISTRY)
        self.ashrama_transitions: Dict[str, AshramaTransition] = {}

        # Initialize ashrama tracking for all agents
        for agent_id in self.biology.keys():
            transition = AshramaTransition(agent_id)
            transition.current_ashrama = self.biology[agent_id].ashrama
            self.ashrama_transitions[agent_id] = transition

    def get_agent_biology(self, agent_id: str) -> Optional[AgentBiology]:
        """Get biological classification of an agent"""
        return self.biology.get(agent_id.lower())

    def get_agent_varna(self, agent_id: str) -> Optional[Varna]:
        """Get species classification"""
        biology = self.get_agent_biology(agent_id)
        return biology.varna if biology else None

    def get_agent_ashrama(self, agent_id: str) -> Optional[Ashrama]:
        """Get current lifecycle stage"""
        biology = self.get_agent_biology(agent_id)
        return biology.ashrama if biology else None

    def get_agents_by_varna(self, varna: Varna) -> list:
        """Get all agents of a specific species"""
        return [
            agent_id
            for agent_id, biology in self.biology.items()
            if biology.varna == varna
        ]

    def get_agents_by_ashrama(self, ashrama: Ashrama) -> list:
        """Get all agents in a specific lifecycle stage"""
        return [
            agent_id
            for agent_id, biology in self.biology.items()
            if biology.ashrama == ashrama
        ]

    def transition_agent(self, agent_id: str, new_ashrama: Ashrama) -> bool:
        """Move agent to new lifecycle stage"""
        if agent_id.lower() in self.biology:
            self.biology[agent_id.lower()].ashrama = new_ashrama
            if agent_id.lower() in self.ashrama_transitions:
                self.ashrama_transitions[agent_id.lower()].transition_to(new_ashrama)
            return True
        return False

    def get_all_agents(self) -> list:
        """Get list of all 18 agents"""
        return list(self.biology.keys())

    def to_registry_dict(self) -> Dict[str, Any]:
        """Serialize entire registry as dict"""
        return {
            agent_id: {
                **asdict(biology),
                "varna": biology.varna.value,
                "ashrama": biology.ashrama.value,
            }
            for agent_id, biology in self.biology.items()
        }


# Global registry instance
_global_metadata_registry: Optional[AgentMetadataRegistry] = None


def get_metadata_registry() -> AgentMetadataRegistry:
    """Get or create the global metadata registry"""
    global _global_metadata_registry
    if _global_metadata_registry is None:
        _global_metadata_registry = AgentMetadataRegistry()
    return _global_metadata_registry
