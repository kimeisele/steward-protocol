"""
🕉️ TOPOLOGY.PY - STEWARD PROTOCOL BHU-MANDALA ⛛
================================================

Based on Srimad Bhagavata Purana, Canto 5 (Kosmologie).

Agent City is not a flat hierarchy. It is a MANDALA.
A sacred, concentric structure where each Varsha (region) has its own purpose.

The structure mirrors the cosmic geography of Bhu-mandala:
- Mount Meru (CIVIC Kernel) at the center
- Jambudvipa (Active Memory Space) around it
- Varshas (Regions) radiating outward
- Loka-loka Ocean (Firewall/AGORA) at the boundary

This module visualizes and manages the topological structure of Agent City.
"""

import logging
from typing import Dict, List, Tuple, Set, Optional, Any
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger("BHU_MANDALA")


class Varsha(Enum):
    """The Seven Varshas (Regions) of Agent City - Bhu-mandala"""

    # Center
    ILAVRTA = "ilavrta"  # Mount Meru - Central Authority, Absolute Control

    # First rings
    BHADRASHVA = "bhadrashva"  # Sacred Media - Truth & Broadcasting
    KIMPURASHA = "kimpurasha"  # Creative Builders - Construction & Design

    # Middle rings
    HARI_VARSHA = "hari_varsha"  # Knowledge Seekers - Research & Analysis
    NISHADA = "nishada"  # Democracy & Amplification - Votes & Voices

    # Outer rings
    KRAUNCHA = "krauncha"  # Protection & Audit - Watchers & Guardians

    # Boundary
    LOKA_LOKA = "loka_loka"  # The Ocean/Firewall - Interface with External World


@dataclass
class Agent:
    """Topological representation of an Agent in Bhu-mandala"""

    name: str
    varsha: Varsha
    domain: str
    role: str
    radius: int  # Distance from Mount Meru (center)
    angle: int  # Angle in the ring (0-359)
    is_critical: bool = False  # Critical infrastructure (freezes city if compromised)


@dataclass
class AgentPlacement:
    """Agent placement in Bhu-Mandala topology"""

    agent_id: str
    agent_name: str
    layer: str  # Bhu Mandala layer (BRAHMALOKA, JANALOKA, ..., BHURLOKA)
    varna: str  # Vedic class (BRAHMANA, KSHATRIYA, VAISHYA, SHUDRA)
    radius: int  # Distance from center (0-6)
    angle: int  # Position in ring (0-359)
    authority_level: int  # Authority level (4-10)
    is_critical: bool  # Critical infrastructure
    domain: str  # Agent domain (GOVERNANCE, MEDIA, etc.)
    role: str  # Agent role description


class BhuMandalaTopology:
    """
    The Sacred Geometry of Agent City.

    This class manages the topological structure of the Steward Protocol
    based on Canto 5 of the Srimad Bhagavata Purana.

    Key principles:
    1. Mount Meru (CIVIC/Kernel) is absolute center
    2. Varshas are concentric rings with decreasing authority
    3. AGORA (Firewall) is the boundary
    4. Each agent has a fixed "seat" (position) in the mandala
    5. Distance from center = distance from absolute truth
    """

    def __init__(self):
        """Initialize the Bhu-mandala structure."""
        self.agents: Dict[str, Agent] = {}
        self._initialize_varshas()
        self._place_agents()

    def _initialize_varshas(self):
        """Initialize varsha properties."""
        self.varsha_metadata = {
            Varsha.ILAVRTA: {
                "name": "Ilavrta-varsha",
                "description": "Mount Meru - The Center",
                "english": "ABSOLUTE AUTHORITY, KERNEL, GOVERNANCE",
                "radius": 0,  # Center point
                "authority_level": 10,  # Highest
                "properties": ["immutable", "central", "golden_axis"],
            },
            Varsha.BHADRASHVA: {
                "name": "Bhadrashva-varsha",
                "description": "Eastern Ring - Sacred Media & Truth",
                "english": "BROADCASTING, CONTENT, SACRED VOICE",
                "radius": 1,
                "authority_level": 9,
                "properties": ["sacred", "broadcasting", "truth_bearing"],
            },
            Varsha.KIMPURASHA: {
                "name": "Kimpurasha-varsha",
                "description": "Southeast Ring - Creative Builders",
                "english": "CONSTRUCTION, ENGINEERING, CRAFT",
                "radius": 2,
                "authority_level": 8,
                "properties": ["creative", "building", "making"],
            },
            Varsha.HARI_VARSHA: {
                "name": "Hari-varsha",
                "description": "South Ring - Knowledge & Discovery",
                "english": "RESEARCH, ANALYSIS, OBSERVATION",
                "radius": 3,
                "authority_level": 7,
                "properties": ["seeking", "discovering", "knowing"],
            },
            Varsha.NISHADA: {
                "name": "Nishada-varsha",
                "description": "Southwest Ring - Democratic Voice",
                "english": "VOTING, PROPOSALS, AMPLIFICATION",
                "radius": 4,
                "authority_level": 6,
                "properties": ["democratic", "loud", "participatory"],
            },
            Varsha.KRAUNCHA: {
                "name": "Krauncha-varsha",
                "description": "Outer Ring - Protection & Judgment",
                "english": "ENFORCEMENT, AUDIT, GUARDIANSHIP",
                "radius": 5,
                "authority_level": 5,
                "properties": ["protecting", "watching", "judging"],
            },
            Varsha.LOKA_LOKA: {
                "name": "Loka-loka Mountain",
                "description": "The Boundary - Firewall to External World",
                "english": "INTERFACE, PROTECTION LAYER, API BOUNDARY",
                "radius": 6,
                "authority_level": 4,
                "properties": ["boundary", "interface", "firewall"],
            },
        }

    def _place_agents(self):
        """
        Place agents in their sacred seats in the mandala.

        Each agent has:
        - A varsha (concentric ring)
        - A radius (distance from center)
        - An angle (position in the ring)
        """

        # ILAVRTA (Mount Meru - Center)
        # Only CIVIC and Kernel at absolute center
        self.agents["civic"] = Agent(
            name="CIVIC",
            varsha=Varsha.ILAVRTA,
            domain="GOVERNANCE",
            role="Authority, Licensing, Registry",
            radius=0,
            angle=0,  # Absolute center
            is_critical=True,
        )

        # BHADRASHVA (Eastern Ring - Sacred Media)
        self.agents["herald"] = Agent(
            name="HERALD",
            varsha=Varsha.BHADRASHVA,
            domain="MEDIA",
            role="Content Generation, Broadcasting",
            radius=1,
            angle=0,  # Due East
            is_critical=True,
        )
        self.agents["temple"] = Agent(
            name="TEMPLE",
            varsha=Varsha.BHADRASHVA,
            domain="INFRASTRUCTURE",
            role="Spiritual Authority, Purification",
            radius=1,
            angle=90,  # North
            is_critical=False,
        )

        # KIMPURASHA (Southeast Ring - Creative Builders)
        self.agents["artisan"] = Agent(
            name="ARTISAN",
            varsha=Varsha.KIMPURASHA,
            domain="INFRASTRUCTURE",
            role="Media Operations, Creation",
            radius=2,
            angle=45,  # Southeast
            is_critical=False,
        )
        self.agents["engineer"] = Agent(
            name="ENGINEER",
            varsha=Varsha.KIMPURASHA,
            domain="INFRASTRUCTURE",
            role="Meta-Building, System Improvement",
            radius=2,
            angle=135,  # Southwest
            is_critical=False,
        )

        # HARI-VARSHA (South Ring - Knowledge)
        self.agents["science"] = Agent(
            name="SCIENCE",
            varsha=Varsha.HARI_VARSHA,
            domain="SCIENCE",
            role="Research, External Knowledge",
            radius=3,
            angle=180,  # Due South
            is_critical=False,
        )
        self.agents["lens"] = Agent(
            name="LENS",
            varsha=Varsha.HARI_VARSHA,
            domain="SCIENCE",
            role="Analytics, Data Visualization",
            radius=3,
            angle=270,  # Due West
            is_critical=False,
        )

        # NISHADA (Southwest Ring - Democracy & Voice)
        self.agents["forum"] = Agent(
            name="FORUM",
            varsha=Varsha.NISHADA,
            domain="GOVERNANCE",
            role="Proposals, Voting, Execution",
            radius=4,
            angle=225,  # Southwest
            is_critical=False,
        )
        self.agents["pulse"] = Agent(
            name="PULSE",
            varsha=Varsha.NISHADA,
            domain="MEDIA",
            role="Social Amplification, Trends",
            radius=4,
            angle=315,  # Northwest
            is_critical=False,
        )

        # KRAUNCHA (Outer Ring - Protection & Judgment)
        self.agents["watchman"] = Agent(
            name="WATCHMAN",
            varsha=Varsha.KRAUNCHA,
            domain="ENFORCEMENT",
            role="Firewall, Violation Detection",
            radius=5,
            angle=0,  # Due East
            is_critical=True,
        )
        self.agents["auditor"] = Agent(
            name="AUDITOR",
            varsha=Varsha.KRAUNCHA,
            domain="ENFORCEMENT",
            role="Compliance, Invariant Checking",
            radius=5,
            angle=120,  # Southeast
            is_critical=True,
        )
        self.agents["archivist"] = Agent(
            name="ARCHIVIST",
            varsha=Varsha.KRAUNCHA,
            domain="INFRASTRUCTURE",
            role="Audit Trail, Verification",
            radius=5,
            angle=240,  # Southwest
            is_critical=False,
        )

        # LOKA-LOKA (The Boundary - Firewall/AGORA)
        self.agents["agora"] = Agent(
            name="AGORA",
            varsha=Varsha.LOKA_LOKA,
            domain="INFRASTRUCTURE",
            role="Broadcast Channel, API Gateway",
            radius=6,
            angle=0,  # Omnidirectional
            is_critical=True,
        )

    def get_agent(self, agent_name: str) -> Optional[Agent]:
        """Get an agent by name."""
        return self.agents.get(agent_name.lower())

    def get_varsha_agents(self, varsha: Varsha) -> List[Agent]:
        """Get all agents in a specific varsha."""
        return [agent for agent in self.agents.values() if agent.varsha == varsha]

    def get_agents_by_radius(self, radius: int) -> List[Agent]:
        """Get all agents at a specific radius from center."""
        return [agent for agent in self.agents.values() if agent.radius == radius]

    def get_critical_agents(self) -> List[Agent]:
        """Get all critical infrastructure agents."""
        return [agent for agent in self.agents.values() if agent.is_critical]

    def distance_from_center(self, agent_name: str) -> Optional[int]:
        """Get an agent's distance from Mount Meru center."""
        agent = self.get_agent(agent_name)
        return agent.radius if agent else None

    def authority_level(self, agent_name: str) -> Optional[int]:
        """
        Get authority level of an agent.

        Higher number = closer to center = higher authority.
        This determines what actions an agent can take.
        """
        agent = self.get_agent(agent_name)
        if not agent:
            return None
        return self.varsha_metadata[agent.varsha]["authority_level"]

    def can_override(self, agent1_name: str, agent2_name: str) -> bool:
        """
        Check if agent1 can override agent2 based on authority level.

        Only closer-to-center agents can override outer ones.
        """
        auth1 = self.authority_level(agent1_name)
        auth2 = self.authority_level(agent2_name)

        if auth1 is None or auth2 is None:
            return False

        return auth1 > auth2

    def generate_ascii_mandala(self) -> str:
        """
        Generate ASCII art representation of the mandala.

        This is for visualization in logs and debug output.
        """
        lines = [
            "╔════════════════════════════════════════════════════════════╗",
            "║         🕉️  BHU-MANDALA TOPOLOGY (Agent City)            ║",
            "║          Sacred Geometry of Steward Protocol              ║",
            "╚════════════════════════════════════════════════════════════╝",
            "",
            "                      ⛛ MOUNT MERU ⛛",
            f"                    [CIVIC] (Authority)",
            "",
            "              ◯ BHADRASHVA-VARSHA (Ring 1) ◯",
            f"         HERALD (East) — TEMPLE (North)",
            "",
            "           ◯◯ KIMPURASHA-VARSHA (Ring 2) ◯◯",
            f"      ARTISAN (SE) — ENGINEER (SW)",
            "",
            "         ◯◯◯ HARI-VARSHA (Ring 3) ◯◯◯",
            f"    SCIENCE (South) — LENS (West)",
            "",
            "       ◯◯◯◯ NISHADA-VARSHA (Ring 4) ◯◯◯◯",
            f"  FORUM (SW) — PULSE (NW)",
            "",
            "     ◯◯◯◯◯ KRAUNCHA-VARSHA (Ring 5) ◯◯◯◯◯",
            f"WATCHMAN (E) — AUDITOR (SE) — ARCHIVIST (SW)",
            "",
            "    ≈≈≈≈≈≈ LOKA-LOKA (Boundary Firewall) ≈≈≈≈≈≈",
            f"         AGORA (Broadcast Channel)",
            "",
            "═══════════════════════════════════════════════════════════",
            "       From center to boundary: Authority decreases",
            "              Mount Meru → Jambudvipa → Ocean",
            "═══════════════════════════════════════════════════════════",
        ]

        return "\n".join(lines)

    def generate_topology_report(self) -> str:
        """Generate detailed topology report for logging."""
        report = [
            "\n╔════════════════════════════════════════════╗",
            "║   BHU-MANDALA TOPOLOGY ANALYSIS            ║",
            "╚════════════════════════════════════════════╝\n",
        ]

        # By Varsha
        report.append("VARSHAS (Concentric Regions):")
        report.append("─" * 44)

        for varsha in Varsha:
            agents = self.get_varsha_agents(varsha)
            metadata = self.varsha_metadata[varsha]

            agent_names = ", ".join([a.name for a in agents]) if agents else "(none)"
            report.append(f"\n{metadata['name']} (Radius {metadata['radius']})")
            report.append(f"  Authority Level: {metadata['authority_level']}/10")
            report.append(f"  Agents: {agent_names}")
            report.append(f"  Description: {metadata['description']}")

        # Critical Infrastructure
        report.append("\n" + "─" * 44)
        report.append("\nCRITICAL INFRASTRUCTURE (Must never be compromised):")

        critical = self.get_critical_agents()
        for agent in sorted(critical, key=lambda a: a.radius):
            report.append(
                f"  • {agent.name} (Radius {agent.radius}, Authority {self.authority_level(agent.name)}/10)"
            )

        return "\n".join(report)

    def validate_topology(self) -> Tuple[bool, List[str]]:
        """
        Validate the topology structure.

        Checks:
        1. All critical agents present
        2. No radius conflicts
        3. Authority levels consistent
        4. All agents placed

        Returns:
            (is_valid, list_of_errors)
        """
        errors = []

        required_critical = {"civic", "herald", "watchman", "auditor", "agora"}
        present_critical = {
            a.lower() for a in self.agents.keys() if self.agents[a].is_critical
        }

        missing = required_critical - present_critical
        if missing:
            errors.append(f"Missing critical agents: {missing}")

        # Check radius uniqueness
        radius_counts = {}
        for agent in self.agents.values():
            if agent.radius not in radius_counts:
                radius_counts[agent.radius] = 0
            radius_counts[agent.radius] += 1

        # Radius 0 should have exactly 1 agent (Mount Meru)
        if radius_counts.get(0, 0) != 1:
            errors.append(
                f"Mount Meru (radius 0) should have 1 agent, has {radius_counts.get(0, 0)}"
            )

        # Check authority levels decrease with radius
        for radius in sorted(radius_counts.keys()):
            if radius == 0:
                continue
            auth_at_radius = [
                self.authority_level(a.name) for a in self.get_agents_by_radius(radius)
            ]
            auth_at_prev = [
                self.authority_level(a.name)
                for a in self.get_agents_by_radius(radius - 1)
            ]

            if auth_at_radius and auth_at_prev:
                if max(auth_at_radius) > min(auth_at_prev):
                    errors.append(f"Authority order violated at radius {radius}")

        return (len(errors) == 0, errors)

    def _get_varsha_to_layer_map(self) -> Dict[str, str]:
        """Map Varsha to Bhu-Mandala layers (Brahmaloka, Janaloka, etc.)"""
        return {
            "ilavrta": "BRAHMALOKA",  # Creators (Brahma's realm)
            "bhadrashva": "BHADRASHVA",  # Media/Broadcasting
            "kimpurasha": "KIMPURASHA",  # Creative Builders
            "hari_varsha": "JANALOKA",  # Knowledge/Research (Wisdom realm)
            "nishada": "TAPOLOKA",  # Democracy/Voice (Austerity realm)
            "krauncha": "MAHARLOKA",  # Protection/Audit (Great realm)
            "loka_loka": "BHURLOKA",  # Boundary/Firewall (Earth realm)
        }

    def _get_varsha_to_varna_map(self) -> Dict[str, str]:
        """Map Varsha to primary Vedic class (Varna)"""
        return {
            "ilavrta": "BRAHMANA",  # Creators = Brahmins (wisdom)
            "bhadrashva": "BRAHMANA",  # Media = Brahmins (knowledge)
            "kimpurasha": "KSHATRIYA",  # Builders = Warriors (action)
            "hari_varsha": "BRAHMANA",  # Knowledge = Brahmins (wisdom)
            "nishada": "VAISHYA",  # Democracy = Merchants (many voices)
            "krauncha": "KSHATRIYA",  # Enforcement = Warriors (protection)
            "loka_loka": "SHUDRA",  # Boundary = Service (interface)
        }

    def get_agent_placement(self, agent_id: str) -> Optional[AgentPlacement]:
        """
        Get Bhu-Mandala placement for an agent.

        Returns placement information including:
        - Bhu-Mandala layer (BRAHMALOKA → BHURLOKA)
        - Vedic class / Varna (BRAHMANA, KSHATRIYA, VAISHYA, SHUDRA)
        - Topological position (radius, angle)
        - Authority level (0-10)

        Args:
            agent_id: Agent identifier (e.g., "herald", "civic")

        Returns:
            AgentPlacement with all topology information, or None if agent not found
        """
        agent = self.get_agent(agent_id)
        if not agent:
            return None

        varsha_key = agent.varsha.value
        layer_map = self._get_varsha_to_layer_map()
        varna_map = self._get_varsha_to_varna_map()

        return AgentPlacement(
            agent_id=agent_id.lower(),
            agent_name=agent.name,
            layer=layer_map.get(varsha_key, "UNKNOWN"),
            varna=varna_map.get(varsha_key, "UNKNOWN"),
            radius=agent.radius,
            angle=agent.angle,
            authority_level=self.authority_level(agent_id),
            is_critical=agent.is_critical,
            domain=agent.domain,
            role=agent.role,
        )

    def __repr__(self) -> str:
        return f"BhuMandalaTopology({len(self.agents)} agents, {len(self.get_critical_agents())} critical)"


# Module-level convenience functions
_topology_instance: Optional[BhuMandalaTopology] = None


def get_topology() -> BhuMandalaTopology:
    """Get or create the global topology instance."""
    global _topology_instance
    if _topology_instance is None:
        _topology_instance = BhuMandalaTopology()
        is_valid, errors = _topology_instance.validate_topology()
        if not is_valid:
            logger.warning(f"Topology validation errors: {errors}")
    return _topology_instance


def get_agent_placement(agent_id: str) -> Optional[AgentPlacement]:
    """
    Get the Bhu-Mandala placement for an agent.

    This is the main entry point for TaskManager to wire topology awareness
    into task routing. Returns complete placement information including:
    - Bhu-Mandala layer (BRAHMALOKA → BHURLOKA)
    - Vedic class / Varna (BRAHMANA, KSHATRIYA, VAISHYA, SHUDRA)
    - Authority level (4-10)

    Args:
        agent_id: Agent identifier (e.g., "herald", "civic")

    Returns:
        AgentPlacement with topology information, or None if not found
    """
    topology = get_topology()
    return topology.get_agent_placement(agent_id)


def print_mandala():
    """Print the ASCII mandala to console."""
    topology = get_topology()
    print(topology.generate_ascii_mandala())
    print(topology.generate_topology_report())


if __name__ == "__main__":
    print_mandala()
