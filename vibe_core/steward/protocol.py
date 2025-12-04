"""
Agent Protocol - Duck-typed interface for agents.

Mirrors the ConfigSectionProtocol pattern from phoenix/section_loader.py.
Any class with these attributes/methods is a valid agent.

FRACTAL PATTERN:
    phoenix/section_loader.py → ConfigSectionProtocol
    steward/protocol.py       → AgentProtocol
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Protocol, runtime_checkable


@dataclass
class AgentManifest:
    """
    What an agent IS - identity, capabilities, governance.

    This is the data structure loaded from manifest.json (formerly steward.json).
    It describes the agent's identity and what it can do.

    Unified Schema (v2.0):
    - agent_id: Unique identifier (e.g., "discoverer", "chronicle")
    - name: Human-readable name (e.g., "The Discoverer")
    - version: Semantic version (e.g., "1.0.0")
    - domain: Functional domain (e.g., "GOVERNANCE", "MEDIA", "RESEARCH")
    - description: What the agent does
    - capabilities: List of capability names
    - constitution_hash: Hash of Constitution this agent is bound to
    - compliance_level: Governance compliance level (0-3)
    """

    agent_id: str
    name: str
    version: str = "1.0.0"
    domain: str = "GENERAL"
    description: str = ""
    capabilities: List[str] = field(default_factory=list)
    constitution_hash: Optional[str] = None
    compliance_level: int = 2
    issuer: str = "passport_office"

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary (for JSON/YAML export)."""
        return {
            "agent": {
                "id": self.agent_id,
                "name": self.name,
                "version": self.version,
                "domain": self.domain,
                "description": self.description,
            },
            "capabilities": [{"name": cap} for cap in self.capabilities],
            "governance": {
                "constitution_hash": self.constitution_hash,
                "compliance_level": self.compliance_level,
                "issuer": self.issuer,
            },
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any], agent_id_fallback: Optional[str] = None) -> "AgentManifest":
        """
        Create AgentManifest from dictionary (loaded from JSON/YAML).

        Supports multiple schemas for backwards compatibility:
        - v2.0: agent.id (new standard)
        - v1.0: identity.agent_id (current majority)
        - legacy: agent_id at root level
        """
        # Try v2.0 schema: agent.id
        agent_data = data.get("agent", {})
        agent_id = agent_data.get("id")

        # Fallback to v1.0 schema: identity.agent_id
        if not agent_id:
            identity = data.get("identity", {})
            agent_id = identity.get("agent_id")

        # Fallback to legacy: root-level agent_id
        if not agent_id:
            agent_id = data.get("agent_id")

        # Final fallback: use provided fallback (usually directory name)
        if not agent_id:
            agent_id = agent_id_fallback or "unknown"

        # Extract name (try multiple locations)
        name = agent_data.get("name") or data.get("identity", {}).get("name") or data.get("name") or agent_id.upper()

        # Extract version
        version = agent_data.get("version") or data.get("specs", {}).get("version") or data.get("version") or "1.0.0"

        # Extract domain
        domain = agent_data.get("domain") or data.get("specs", {}).get("domain") or data.get("domain") or "GENERAL"

        # Extract description
        description = (
            agent_data.get("description") or data.get("specs", {}).get("description") or data.get("description") or ""
        )

        # Extract capabilities (handle both formats)
        capabilities_data = data.get("capabilities", {})
        if isinstance(capabilities_data, dict):
            # Standard format: {"operations": [{"name": "..."}, ...]}
            operations = capabilities_data.get("operations", [])
            capabilities = [op.get("name", "") for op in operations if isinstance(op, dict)]
        elif isinstance(capabilities_data, list):
            # Legacy format: ["cap1", "cap2", ...]
            capabilities = [cap if isinstance(cap, str) else cap.get("name", "") for cap in capabilities_data]
        else:
            capabilities = []

        # Extract governance
        governance = data.get("governance", {})
        constitution_hash = governance.get("constitution_hash")
        compliance_level = governance.get("compliance_level", 2)
        issuer = governance.get("issuer", "passport_office")

        return cls(
            agent_id=agent_id,
            name=name,
            version=version,
            domain=domain,
            description=description,
            capabilities=capabilities,
            constitution_hash=constitution_hash,
            compliance_level=compliance_level,
            issuer=issuer,
        )


@runtime_checkable
class AgentProtocol(Protocol):
    """
    Duck-typed protocol for agents.

    Any class with these attributes/methods is a valid agent.
    This avoids circular import issues and enables flexible implementations.

    FRACTAL PATTERN:
        ConfigSectionProtocol → section_id, from_dict(), to_dict()
        AgentProtocol         → agent_id, process(), get_manifest()
    """

    agent_id: str
    name: str
    capabilities: List[str]

    def process(self, task: Any) -> Dict[str, Any]:
        """Process a task from the kernel scheduler."""
        ...

    def get_manifest(self) -> AgentManifest:
        """Return this agent's manifest (identity + capabilities)."""
        ...


def is_valid_agent(obj: Any) -> bool:
    """
    Check if an object implements the AgentProtocol.

    Args:
        obj: Object to check

    Returns:
        True if object is a valid agent
    """
    # Check required attributes
    if not hasattr(obj, "agent_id") or not isinstance(obj.agent_id, str):
        return False
    if not hasattr(obj, "name"):
        return False

    # Check required methods
    if not hasattr(obj, "process") or not callable(getattr(obj, "process")):
        return False

    return True
