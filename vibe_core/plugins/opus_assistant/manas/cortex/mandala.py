"""
OPUS-051: MANDALA (The Fractal Configuration) - Self-Weaving Config Engine.

Sanskrit: Mandala = Circle, Sacred Diagram, Cosmic Map.

This module transforms static configuration into a living, fractal structure.
Instead of the Kernel dictating what Agents can do, Agents declare their own
capabilities, and the Kernel weaves them into a unified runtime truth.

Architecture:
    ┌─────────────────────────────────────────────────────────────────┐
    │                    MANDALA (The Cosmic Map)                      │
    │                                                                   │
    │   cartridges/          Each Cartridge              ConfigWeaver  │
    │       ↓                declares itself:            weaves into:   │
    │   ┌─────────┐                                    ┌─────────────┐ │
    │   │ dharma/ │──► steward.json ──────────────────►│             │ │
    │   │ analyst │──► cartridge.yaml ────────────────►│   RUNTIME   │ │
    │   │ scribe/ │──► tools/*.json ──────────────────►│   MANDALA   │ │
    │   │ envoy/  │──► capabilities.yaml ─────────────►│   (Graph)   │ │
    │   └─────────┘                                    └─────────────┘ │
    │                                                                   │
    │   The Mandala is not drawn. It EMERGES.                          │
    └─────────────────────────────────────────────────────────────────┘

Principles:
1. INVERSION OF CONTROL: Agents tell the Kernel, not vice versa.
2. FRACTAL CONSISTENCY: Tool config must respect Cartridge config.
3. RUNTIME TRUTH: The Mandala is built at boot, not hardcoded.
4. SELF-DOCUMENTATION: The Mandala IS the documentation.

"The whole contains the part, and the part contains the whole."
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prahlada"
__position__ = 9
__genesis__ = "0xb761bfc9"  # GenesisByte: parampara % 37 == 0

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

logger = logging.getLogger("MANAS.Cortex.Mandala")


# =============================================================================
# SECTION 1: DATA MODELS (The Sacred Geometry)
# =============================================================================


@dataclass
class CapabilitySpec:
    """
    Specification for a single capability.

    A capability is an atomic unit of what an agent CAN do.
    """

    name: str
    description: str = ""
    cost: int = 0  # Karma cost to invoke
    rate_limit: Optional[str] = None  # e.g., "10/minute"
    permissions_required: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    enabled: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "cost": self.cost,
            "rate_limit": self.rate_limit,
            "permissions_required": self.permissions_required,
            "dependencies": self.dependencies,
            "enabled": self.enabled,
        }

    @classmethod
    def from_dict(cls, name: str, data: Dict[str, Any]) -> "CapabilitySpec":
        """Create from dict (supports both simple and complex formats)."""
        if isinstance(data, dict):
            return cls(
                name=name,
                description=data.get("description", ""),
                cost=data.get("cost", 0),
                rate_limit=data.get("rate_limit"),
                permissions_required=data.get("permissions_required", []),
                dependencies=data.get("dependencies", []),
                enabled=data.get("enabled", True),
            )
        else:
            # Simple format: just a name
            return cls(name=name)


@dataclass
class ToolManifest:
    """
    Manifest for a tool within a cartridge.

    Tools are the atomic actions that capabilities enable.
    """

    tool_id: str
    name: str
    description: str = ""
    capabilities_required: List[str] = field(default_factory=list)
    rate_limit: Optional[str] = None
    permissions_required: List[str] = field(default_factory=list)
    enabled: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tool_id": self.tool_id,
            "name": self.name,
            "description": self.description,
            "capabilities_required": self.capabilities_required,
            "rate_limit": self.rate_limit,
            "permissions_required": self.permissions_required,
            "enabled": self.enabled,
        }


@dataclass
class GovernanceSpec:
    """
    Governance rules for a cartridge.

    Defines constitutional constraints and compliance requirements.
    """

    level: str = "standard"  # minimal, standard, strict, sacred
    oath_required: bool = False
    constitution_bound: bool = False
    karma_tracking: bool = True
    audit_level: str = "normal"  # none, normal, detailed, paranoid

    def to_dict(self) -> Dict[str, Any]:
        return {
            "level": self.level,
            "oath_required": self.oath_required,
            "constitution_bound": self.constitution_bound,
            "karma_tracking": self.karma_tracking,
            "audit_level": self.audit_level,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GovernanceSpec":
        return cls(
            level=data.get("level", "standard"),
            oath_required=data.get("oath_required", False),
            constitution_bound=data.get("constitution_bound", False),
            karma_tracking=data.get("karma_tracking", True),
            audit_level=data.get("audit_level", "normal"),
        )


@dataclass
class RateLimitSpec:
    """Rate limiting specification."""

    requests_per_minute: int = 60
    requests_per_hour: int = 3600
    burst_limit: int = 10

    def to_dict(self) -> Dict[str, Any]:
        return {
            "requests_per_minute": self.requests_per_minute,
            "requests_per_hour": self.requests_per_hour,
            "burst_limit": self.burst_limit,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RateLimitSpec":
        return cls(
            requests_per_minute=data.get("requests_per_minute", 60),
            requests_per_hour=data.get("requests_per_hour", 3600),
            burst_limit=data.get("burst_limit", 10),
        )


@dataclass
class FractalManifest:
    """
    The complete manifest for a cartridge.

    This is the "gene" of an agent - everything it needs to exist.
    Loaded from steward.json + cartridge.yaml (merged).
    """

    # Identity
    agent_id: str
    name: str
    version: str = "1.0.0"
    type: str = "cartridge"

    # Classification
    domain: str = "GENERAL"  # GOVERNANCE, RESEARCH, MEDIA, SYSTEM, etc.
    zone: str = "standard"  # governance, standard, experimental
    tier: str = "agent"  # system, agent, tool

    # Capabilities (the fractal children)
    capabilities: Dict[str, CapabilitySpec] = field(default_factory=dict)
    permissions: List[str] = field(default_factory=list)
    tools: List[str] = field(default_factory=list)

    # Governance
    governance: Optional[GovernanceSpec] = None
    rate_limits: Optional[RateLimitSpec] = None

    # Dependencies
    dependencies: List[str] = field(default_factory=list)
    requires_agents: List[str] = field(default_factory=list)

    # Source
    source_path: Optional[Path] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "version": self.version,
            "type": self.type,
            "domain": self.domain,
            "zone": self.zone,
            "tier": self.tier,
            "capabilities": {k: v.to_dict() for k, v in self.capabilities.items()},
            "permissions": self.permissions,
            "tools": self.tools,
            "governance": self.governance.to_dict() if self.governance else None,
            "rate_limits": self.rate_limits.to_dict() if self.rate_limits else None,
            "dependencies": self.dependencies,
            "requires_agents": self.requires_agents,
        }

    def get_all_capabilities(self) -> Set[str]:
        """Get set of all capability names."""
        return set(self.capabilities.keys())

    def has_capability(self, name: str) -> bool:
        """Check if this manifest declares a capability."""
        return name in self.capabilities

    def get_capability(self, name: str) -> Optional[CapabilitySpec]:
        """Get capability spec by name."""
        return self.capabilities.get(name)


# =============================================================================
# SECTION 2: MANIFEST LOADER (The Archaeologist)
# =============================================================================


class ManifestLoader:
    """
    Loads and merges cartridge manifests from filesystem.

    Discovers:
    1. steward.json (identity, permissions, governance)
    2. cartridge.yaml (capabilities, tools, config)
    3. tools/*.json (tool-level manifests)

    Merges them into a unified FractalManifest.
    """

    def __init__(self, workspace: Optional[Path] = None):
        """Initialize manifest loader."""
        self._workspace = workspace or Path.cwd()

    def load_cartridge_manifest(self, cartridge_path: Path) -> Optional[FractalManifest]:
        """
        Load a complete manifest from a cartridge directory.

        Args:
            cartridge_path: Path to cartridge directory

        Returns:
            FractalManifest or None if invalid
        """
        if not cartridge_path.is_dir():
            logger.warning(f"Cartridge path is not a directory: {cartridge_path}")
            return None

        # Load steward.json (primary identity)
        steward_json = cartridge_path / "steward.json"
        json_data = self._load_json(steward_json)

        # Load cartridge.yaml (config/capabilities)
        cartridge_yaml = cartridge_path / "cartridge.yaml"
        yaml_data = self._load_yaml(cartridge_yaml)

        # Merge data
        merged = self._merge_manifests(json_data, yaml_data)

        if not merged:
            # No manifest found at all - infer from directory name
            agent_id = cartridge_path.name
            logger.debug(f"No manifest found for {agent_id}, creating minimal manifest")
            return FractalManifest(
                agent_id=agent_id,
                name=agent_id.upper(),
                source_path=cartridge_path,
            )

        # Build FractalManifest
        return self._build_manifest(merged, cartridge_path)

    def _load_json(self, path: Path) -> Dict[str, Any]:
        """Load JSON file."""
        if not path.exists():
            return {}
        try:
            with open(path) as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load JSON from {path}: {e}")
            return {}

    def _load_yaml(self, path: Path) -> Dict[str, Any]:
        """Load YAML file."""
        if not path.exists():
            return {}
        try:
            import yaml

            with open(path) as f:
                return yaml.safe_load(f) or {}
        except ImportError:
            logger.warning("PyYAML not installed, skipping YAML loading")
            return {}
        except Exception as e:
            logger.warning(f"Failed to load YAML from {path}: {e}")
            return {}

    def _merge_manifests(self, json_data: Dict[str, Any], yaml_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge JSON and YAML manifests.

        Priority: yaml_data overrides json_data (more specific wins).
        """
        if not json_data and not yaml_data:
            return {}

        # Start with JSON as base
        merged = dict(json_data)

        # Overlay YAML (more specific)
        for key, value in yaml_data.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                # Deep merge dicts
                merged[key] = {**merged[key], **value}
            else:
                merged[key] = value

        return merged

    def _build_manifest(self, data: Dict[str, Any], source_path: Path) -> FractalManifest:
        """Build FractalManifest from merged data."""
        # Extract capabilities
        capabilities: Dict[str, CapabilitySpec] = {}
        caps_data = data.get("capabilities", {})

        if isinstance(caps_data, dict):
            for name, spec in caps_data.items():
                capabilities[name] = CapabilitySpec.from_dict(name, spec)
        elif isinstance(caps_data, list):
            # List format: ["git_analysis", "code_analysis"] or [{"name": "cap1"}, ...]
            for item in caps_data:
                if isinstance(item, str):
                    capabilities[item] = CapabilitySpec(name=item)
                elif isinstance(item, dict):
                    # Dict format in list: {"name": "cap1", ...} or just capability names
                    name = item.get("name", str(item))
                    capabilities[name] = CapabilitySpec.from_dict(name, item)

        # Extract governance
        governance = None
        gov_data = data.get("governance")
        if gov_data:
            governance = GovernanceSpec.from_dict(gov_data)

        # Extract rate limits
        rate_limits = None
        rl_data = data.get("rate_limits")
        if rl_data:
            rate_limits = RateLimitSpec.from_dict(rl_data)

        # Extract tools (can be list of strings or list of dicts)
        tools = []
        tools_data = data.get("tools", [])
        for tool in tools_data:
            if isinstance(tool, str):
                tools.append(tool)
            elif isinstance(tool, dict):
                tools.append(tool.get("name", tool.get("tool_id", "")))

        return FractalManifest(
            agent_id=data.get("agent_id", source_path.name),
            name=data.get("name", source_path.name.upper()),
            version=data.get("version", "1.0.0"),
            type=data.get("type", "cartridge"),
            domain=data.get("domain", "GENERAL"),
            zone=data.get("zone", "standard"),
            tier=data.get("tier", "agent"),
            capabilities=capabilities,
            permissions=data.get("permissions", []),
            tools=tools,
            governance=governance,
            rate_limits=rate_limits,
            dependencies=data.get("dependencies", []),
            requires_agents=data.get("requires_agents", []),
            source_path=source_path,
        )


# =============================================================================
# SECTION 3: CAPABILITY TREE (The Hierarchy)
# =============================================================================


@dataclass
class CapabilityNode:
    """A node in the capability tree."""

    name: str
    source_agent: str
    spec: CapabilitySpec
    children: List["CapabilityNode"] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "source_agent": self.source_agent,
            "spec": self.spec.to_dict(),
            "children": [c.to_dict() for c in self.children],
        }


class CapabilityTree:
    """
    Hierarchical tree of all capabilities in the system.

    Allows:
    - Finding which agent provides a capability
    - Checking if a capability is available
    - Validating capability dependencies
    """

    def __init__(self):
        """Initialize empty capability tree."""
        self._nodes: Dict[str, CapabilityNode] = {}
        self._agent_capabilities: Dict[str, Set[str]] = {}

    def add_agent(self, manifest: FractalManifest) -> None:
        """
        Add an agent's capabilities to the tree.

        Args:
            manifest: The agent's fractal manifest
        """
        agent_id = manifest.agent_id
        self._agent_capabilities[agent_id] = set()

        for name, spec in manifest.capabilities.items():
            node = CapabilityNode(name=name, source_agent=agent_id, spec=spec)
            self._nodes[name] = node
            self._agent_capabilities[agent_id].add(name)

        logger.debug(f"Added {len(manifest.capabilities)} capabilities from {agent_id}")

    def has_capability(self, name: str) -> bool:
        """Check if a capability exists in the tree."""
        return name in self._nodes

    def get_capability(self, name: str) -> Optional[CapabilityNode]:
        """Get capability node by name."""
        return self._nodes.get(name)

    def get_provider(self, capability: str) -> Optional[str]:
        """Get the agent_id that provides a capability."""
        node = self._nodes.get(capability)
        return node.source_agent if node else None

    def get_agent_capabilities(self, agent_id: str) -> Set[str]:
        """Get all capabilities provided by an agent."""
        return self._agent_capabilities.get(agent_id, set())

    def validate_dependencies(self) -> List[str]:
        """
        Validate that all capability dependencies are satisfied.

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        for name, node in self._nodes.items():
            for dep in node.spec.dependencies:
                if dep not in self._nodes:
                    errors.append(f"Capability '{name}' depends on '{dep}' which is not provided")

        return errors

    def to_dict(self) -> Dict[str, Any]:
        """Export tree as dictionary."""
        return {
            "nodes": {k: v.to_dict() for k, v in self._nodes.items()},
            "agent_capabilities": {k: list(v) for k, v in self._agent_capabilities.items()},
        }


# =============================================================================
# SECTION 4: CONFIG WEAVER (The Cosmic Loom)
# =============================================================================


class ConfigWeaver:
    """
    The Cosmic Loom that weaves individual agent configs into a unified Mandala.

    At boot:
    1. Discovers all cartridges
    2. Loads their manifests
    3. Builds the capability tree
    4. Validates the whole structure
    5. Produces the Runtime Mandala

    "The Mandala is not drawn. It EMERGES."
    """

    def __init__(self, workspace: Optional[Path] = None):
        """Initialize the config weaver."""
        self._workspace = workspace or Path.cwd()
        self._loader = ManifestLoader(workspace=self._workspace)

        # The woven results
        self._manifests: Dict[str, FractalManifest] = {}
        self._capability_tree: CapabilityTree = CapabilityTree()
        self._is_woven: bool = False

    @property
    def is_woven(self) -> bool:
        """Check if the Mandala has been woven."""
        return self._is_woven

    @property
    def manifests(self) -> Dict[str, FractalManifest]:
        """Get all loaded manifests."""
        return self._manifests

    @property
    def capability_tree(self) -> CapabilityTree:
        """Get the capability tree."""
        return self._capability_tree

    def weave(self) -> "ConfigWeaver":
        """
        Weave the Mandala from discovered cartridges.

        This is the main entry point - call during kernel boot.

        Returns:
            self for chaining
        """
        logger.info("🕸️ MANDALA: Beginning to weave the cosmic configuration...")

        # Discover cartridges
        cartridge_dirs = self._discover_cartridges()
        logger.info(f"🕸️ MANDALA: Discovered {len(cartridge_dirs)} cartridge directories")

        # Load manifests
        for cartridge_dir in cartridge_dirs:
            manifest = self._loader.load_cartridge_manifest(cartridge_dir)
            if manifest:
                self._manifests[manifest.agent_id] = manifest
                self._capability_tree.add_agent(manifest)

        # Validate
        errors = self._validate()
        if errors:
            for error in errors:
                logger.warning(f"🕸️ MANDALA validation warning: {error}")

        self._is_woven = True
        logger.info(
            f"🕸️ MANDALA: Weaving complete. "
            f"{len(self._manifests)} agents, "
            f"{len(self._capability_tree._nodes)} capabilities"
        )

        return self

    def _discover_cartridges(self) -> List[Path]:
        """Discover all cartridge directories."""
        cartridges: List[Path] = []

        # Primary locations
        locations = [
            self._workspace / "vibe_core" / "cartridges" / "agent_city",
            self._workspace / "vibe_core" / "cartridges" / "system",
        ]

        for location in locations:
            if not location.exists():
                continue

            for item in location.iterdir():
                if item.is_dir() and not item.name.startswith("_"):
                    # Check if it looks like a cartridge
                    if self._is_cartridge(item):
                        cartridges.append(item)

        return cartridges

    def _is_cartridge(self, path: Path) -> bool:
        """Check if a directory is a valid cartridge."""
        # Must have at least one of these
        indicators = [
            path / "steward.json",
            path / "cartridge.yaml",
            path / "cartridge_main.py",
            path / "__init__.py",
        ]
        return any(ind.exists() for ind in indicators)

    def _validate(self) -> List[str]:
        """Validate the woven Mandala."""
        errors = []

        # Validate capability dependencies
        errors.extend(self._capability_tree.validate_dependencies())

        # Validate agent dependencies
        for agent_id, manifest in self._manifests.items():
            for required_agent in manifest.requires_agents:
                if required_agent not in self._manifests:
                    errors.append(f"Agent '{agent_id}' requires '{required_agent}' which is not loaded")

        return errors

    def get_manifest(self, agent_id: str) -> Optional[FractalManifest]:
        """Get manifest for a specific agent."""
        return self._manifests.get(agent_id)

    def get_agents_by_domain(self, domain: str) -> List[FractalManifest]:
        """Get all agents in a domain."""
        return [m for m in self._manifests.values() if m.domain == domain]

    def get_agents_with_capability(self, capability: str) -> List[FractalManifest]:
        """Get all agents that provide a capability."""
        return [m for m in self._manifests.values() if m.has_capability(capability)]

    def to_dict(self) -> Dict[str, Any]:
        """Export the woven Mandala as a dictionary."""
        return {
            "is_woven": self._is_woven,
            "agent_count": len(self._manifests),
            "capability_count": len(self._capability_tree._nodes),
            "manifests": {k: v.to_dict() for k, v in self._manifests.items()},
            "capability_tree": self._capability_tree.to_dict(),
        }

    def summary(self) -> str:
        """Generate human-readable summary of the Mandala."""
        if not self._is_woven:
            return "🕸️ MANDALA: Not yet woven. Call weave() first."

        lines = [
            "🕸️ **MANDALA: The Cosmic Configuration**",
            "",
            f"**Agents:** {len(self._manifests)}",
            f"**Capabilities:** {len(self._capability_tree._nodes)}",
            "",
            "**Agents by Domain:**",
        ]

        # Group by domain
        domains: Dict[str, List[str]] = {}
        for manifest in self._manifests.values():
            domain = manifest.domain
            if domain not in domains:
                domains[domain] = []
            domains[domain].append(manifest.agent_id)

        for domain, agents in sorted(domains.items()):
            lines.append(f"  {domain}: {', '.join(sorted(agents))}")

        lines.append("")
        lines.append("**Capability Overview:**")

        # Top capabilities by agent count
        cap_counts: Dict[str, int] = {}
        for manifest in self._manifests.values():
            for cap in manifest.capabilities:
                cap_counts[cap] = cap_counts.get(cap, 0) + 1

        top_caps = sorted(cap_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        for cap, count in top_caps:
            provider = self._capability_tree.get_provider(cap)
            lines.append(f"  • {cap} (from {provider})")

        return "\n".join(lines)


# =============================================================================
# SECTION 5: JNANA INTEGRATION (Chat Bridge)
# =============================================================================


def get_mandala_for_chat(workspace: Optional[Path] = None) -> str:
    """
    Get Mandala summary for chat interface.

    Usage in JnanaHandler:
        if "mandala" in message or "config" in message:
            return get_mandala_for_chat()
    """
    weaver = ConfigWeaver(workspace=workspace)
    weaver.weave()
    return weaver.summary()


def query_capability(capability: str, workspace: Optional[Path] = None) -> str:
    """
    Query who provides a capability.

    Usage:
        query_capability("git_analysis")
        -> "Capability 'git_analysis' is provided by agent 'analyst'"
    """
    weaver = ConfigWeaver(workspace=workspace)
    weaver.weave()

    provider = weaver.capability_tree.get_provider(capability)
    if provider:
        manifest = weaver.get_manifest(provider)
        spec = manifest.get_capability(capability) if manifest else None

        if spec:
            return (
                f"🕸️ Capability '{capability}' is provided by **{provider}**\n\n"
                f"- Description: {spec.description or 'N/A'}\n"
                f"- Cost: {spec.cost} karma\n"
                f"- Rate Limit: {spec.rate_limit or 'unlimited'}\n"
                f"- Enabled: {spec.enabled}"
            )
        return f"🕸️ Capability '{capability}' is provided by **{provider}**"
    else:
        return f"❌ Capability '{capability}' is not provided by any agent"
