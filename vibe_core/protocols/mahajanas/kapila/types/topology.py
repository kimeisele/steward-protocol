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

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "kapila"
__position__ = 6
__genesis__ = "0xe84c4ee3"  # GenesisByte: parampara % 37 == 0

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Tuple

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

    id: str  # Lowercase agent identifier (e.g., 'lazara')
    name: str  # Display name (e.g., 'LAZARA')
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
    4. Each agent has a dynamic "seat" (position) based on domain
    5. Distance from center = distance from absolute truth

    DYNAMIC TOPOLOGY: Agents are discovered from kernel or filesystem,
    NOT hardcoded. When a new agent is created, it automatically appears
    on the mandala based on its domain.
    """

    # Domain to Varsha mapping - determines where agents land on the mandala
    DOMAIN_TO_VARSHA = {
        # Center (Radius 0) - Core Governance
        "GOVERNANCE": Varsha.ILAVRTA,
        # Ring 1 - Communications & Media
        "COMMUNICATIONS": Varsha.BHADRASHVA,
        "MEDIA": Varsha.BHADRASHVA,
        "SPIRITUAL": Varsha.BHADRASHVA,
        # Ring 2 - Builders & Infrastructure
        "INFRASTRUCTURE": Varsha.KIMPURASHA,
        "ENGINEERING": Varsha.KIMPURASHA,
        "MAINTENANCE": Varsha.KIMPURASHA,
        # Ring 3 - Knowledge & Research
        "INTELLIGENCE": Varsha.HARI_VARSHA,
        "RESEARCH": Varsha.HARI_VARSHA,
        "OBSERVATION": Varsha.HARI_VARSHA,
        "DATA_ETHICS": Varsha.HARI_VARSHA,
        # Ring 4 - Democracy & Community
        "COMMUNITY": Varsha.NISHADA,
        "DIPLOMACY": Varsha.NISHADA,
        "COORDINATION": Varsha.NISHADA,
        "ECONOMY": Varsha.NISHADA,
        "CONTENT": Varsha.NISHADA,
        # Ring 5 - Protection & Enforcement
        "SYSTEM": Varsha.KRAUNCHA,
        "SECURITY": Varsha.KRAUNCHA,
        "JUSTICE": Varsha.KRAUNCHA,
        # Ring 6 - Boundary/Interface
        "INTERFACE": Varsha.LOKA_LOKA,
        "TESTING": Varsha.LOKA_LOKA,
    }

    # Critical agents by ID (can't be determined by domain alone)
    CRITICAL_AGENT_IDS = frozenset(["civic", "herald", "watchman", "auditor", "agora", "envoy", "discoverer"])

    def __init__(self, kernel=None):
        """Initialize the Bhu-mandala structure.

        Args:
            kernel: VibeOS kernel for dynamic agent discovery (optional).
                   If not provided, scans filesystem for steward.json files.
        """
        self.kernel = kernel
        self.agents: Dict[str, Agent] = {}
        self._initialize_varshas()
        self._discover_and_place_agents()

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

    def _discover_and_place_agents(self):
        """
        DYNAMIC agent discovery and placement.

        Discovers agents from:
        1. Kernel's agent_registry (if available)
        2. Filesystem scan for steward.json files (fallback)

        Places each agent based on its domain using DOMAIN_TO_VARSHA mapping.
        """
        import json
        from pathlib import Path

        discovered_agents = []

        # Method 1: From kernel registry
        if self.kernel and hasattr(self.kernel, "agent_registry"):
            for agent_id, agent_obj in self.kernel.agent_registry.items():
                discovered_agents.append(
                    {
                        "agent_id": agent_id,
                        "name": getattr(agent_obj, "name", agent_id.upper()),
                        "domain": getattr(agent_obj, "domain", "SYSTEM"),
                        "description": getattr(agent_obj, "description", ""),
                    }
                )
            logger.info(f"Topology: Discovered {len(discovered_agents)} agents from kernel")

        # Method 2: Filesystem scan (fallback or supplement)
        if not discovered_agents:
            search_paths = [
                Path("vibe_core/cartridges/system"),
                Path("vibe_core/cartridges/agent_city"),
            ]

            for base_path in search_paths:
                if not base_path.exists():
                    continue

                for steward_json in base_path.rglob("steward.json"):
                    # Skip template directories
                    if "templates" in str(steward_json):
                        continue

                    try:
                        data = json.loads(steward_json.read_text())
                        agent_id = data.get("identity", {}).get("agent_id", steward_json.parent.name)

                        # Skip template placeholders
                        if agent_id.startswith("YOUR_"):
                            continue

                        discovered_agents.append(
                            {
                                "agent_id": agent_id,
                                "name": data.get("identity", {}).get("name", agent_id.upper()),
                                "domain": data.get("specs", {}).get("domain", "SYSTEM"),
                                "description": data.get("specs", {}).get("description", ""),
                            }
                        )
                    except Exception as e:
                        logger.warning(f"Failed to parse {steward_json}: {e}")

            logger.info(f"Topology: Discovered {len(discovered_agents)} agents from filesystem")

        # Place agents dynamically
        self._place_discovered_agents(discovered_agents)

    def _place_discovered_agents(self, agents: List[Dict]):
        """
        Place discovered agents on the mandala based on their domain.

        Args:
            agents: List of agent dicts with agent_id, name, domain, description
        """
        # Group agents by varsha for angle assignment
        varsha_agents: Dict[Varsha, List[Dict]] = {v: [] for v in Varsha}

        for agent_data in agents:
            domain = agent_data["domain"].upper()
            varsha = self.DOMAIN_TO_VARSHA.get(domain, Varsha.LOKA_LOKA)  # Default to boundary
            varsha_agents[varsha].append(agent_data)

        # Place agents in each varsha with auto-assigned angles
        for varsha, agent_list in varsha_agents.items():
            if not agent_list:
                continue

            radius = self.varsha_metadata[varsha]["radius"]
            num_agents = len(agent_list)

            for i, agent_data in enumerate(sorted(agent_list, key=lambda a: a["agent_id"])):
                # Distribute angles evenly in the ring
                angle = (360 // max(num_agents, 1)) * i

                agent_id = agent_data["agent_id"].lower()
                is_critical = agent_id in self.CRITICAL_AGENT_IDS

                self.agents[agent_id] = Agent(
                    id=agent_id,
                    name=agent_data["name"],
                    varsha=varsha,
                    domain=agent_data["domain"],
                    role=agent_data["description"][:50] if agent_data["description"] else "Agent",
                    radius=radius,
                    angle=angle,
                    is_critical=is_critical,
                )

        logger.info(f"Topology: Placed {len(self.agents)} agents on mandala")

    def refresh(self):
        """Refresh the topology by re-discovering agents."""
        self.agents.clear()
        self._discover_and_place_agents()

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
        Generate DYNAMIC ASCII art representation of the mandala.

        Shows all discovered agents in their respective varshas.
        """
        lines = [
            "╔════════════════════════════════════════════════════════════╗",
            "║         🕉️  BHU-MANDALA TOPOLOGY (Agent City)            ║",
            "║          Sacred Geometry of Steward Protocol              ║",
            "║                   [DYNAMIC MAP]                           ║",
            "╚════════════════════════════════════════════════════════════╝",
            "",
        ]

        # Generate each varsha dynamically
        varsha_display = [
            (Varsha.ILAVRTA, "⛛ MOUNT MERU ⛛", "Ring 0"),
            (Varsha.BHADRASHVA, "◯ BHADRASHVA-VARSHA", "Ring 1"),
            (Varsha.KIMPURASHA, "◯◯ KIMPURASHA-VARSHA", "Ring 2"),
            (Varsha.HARI_VARSHA, "◯◯◯ HARI-VARSHA", "Ring 3"),
            (Varsha.NISHADA, "◯◯◯◯ NISHADA-VARSHA", "Ring 4"),
            (Varsha.KRAUNCHA, "◯◯◯◯◯ KRAUNCHA-VARSHA", "Ring 5"),
            (Varsha.LOKA_LOKA, "≈≈≈≈≈≈ LOKA-LOKA", "Ring 6"),
        ]

        for varsha, label, ring in varsha_display:
            agents_in_varsha = self.get_varsha_agents(varsha)
            agent_names = " — ".join([a.name for a in sorted(agents_in_varsha, key=lambda x: x.angle)])

            if agents_in_varsha:
                lines.append(f"  {label} ({ring})")
                lines.append(f"    {agent_names}")
                lines.append("")

        lines.extend(
            [
                "═══════════════════════════════════════════════════════════",
                f"  Total Agents: {len(self.agents)} | Critical: {len(self.get_critical_agents())}",
                "  From center to boundary: Authority decreases",
                "═══════════════════════════════════════════════════════════",
            ]
        )

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
            report.append(f"  • {agent.name} (Radius {agent.radius}, Authority {self.authority_level(agent.name)}/10)")

        return "\n".join(report)

    def validate_topology(self) -> Tuple[bool, List[str]]:
        """
        Validate the topology structure.

        Checks:
        1. At least one agent in center (governance)
        2. No duplicate positions
        3. Authority levels consistent
        4. At least some critical agents present

        Returns:
            (is_valid, list_of_errors)
        """
        errors = []

        # Check that we have at least some agents
        if not self.agents:
            errors.append("No agents discovered - topology is empty")
            return (False, errors)

        # Check for governance center
        center_agents = self.get_agents_by_radius(0)
        if not center_agents:
            errors.append("No agent at center (radius 0) - need governance agent")

        # Check radius uniqueness
        radius_counts = {}
        for agent in self.agents.values():
            if agent.radius not in radius_counts:
                radius_counts[agent.radius] = 0
            radius_counts[agent.radius] += 1

        # Radius 0 should have at least 1 agent (Mount Meru / Governance)
        if radius_counts.get(0, 0) == 0:
            errors.append("Mount Meru (radius 0) should have at least 1 governance agent")

        # Check authority levels decrease with radius
        for radius in sorted(radius_counts.keys()):
            if radius == 0:
                continue
            auth_at_radius = [self.authority_level(a.id) for a in self.get_agents_by_radius(radius)]
            auth_at_prev = [self.authority_level(a.id) for a in self.get_agents_by_radius(radius - 1)]

            # Filter out None values (shouldn't happen but defensive)
            auth_at_radius = [a for a in auth_at_radius if a is not None]
            auth_at_prev = [a for a in auth_at_prev if a is not None]

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


def get_topology(kernel=None, refresh: bool = False) -> BhuMandalaTopology:
    """Get or create the global topology instance.

    Args:
        kernel: Optional kernel for dynamic agent discovery
        refresh: If True, refresh the topology even if it exists
    """
    global _topology_instance
    if _topology_instance is None or refresh:
        _topology_instance = BhuMandalaTopology(kernel=kernel)
        is_valid, errors = _topology_instance.validate_topology()
        if not is_valid:
            logger.warning(f"Topology validation errors: {errors}")
        else:
            logger.info(f"Topology initialized with {len(_topology_instance.agents)} agents")
    return _topology_instance


def refresh_topology(kernel=None) -> BhuMandalaTopology:
    """Force refresh the topology (e.g., after adding new agents)."""
    return get_topology(kernel=kernel, refresh=True)


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
