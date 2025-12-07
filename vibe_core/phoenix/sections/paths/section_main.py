"""
Paths Configuration - All system paths from a single source of truth.

VEDA-4 Pattern:
    SHABDA: Auto-discovered from vibe_core/phoenix/sections/paths/
    ARTHA: Parsed from config/paths.yaml
    PRATYAYA: Validated (paths must be valid, no hardcoded defaults)
    KARMA: Instantiated as PathsConfig dataclass

This section eliminates all 105 hardcoded Path() violations found in the audit.
Each path category maps to actual code usage:
    - data: data/economy.db, data/registry/, data/ledger/, etc.
    - cartridges: vibe_core/cartridges/system, vibe_core/cartridges/agent_city
    - knowledge: knowledge/circuits, knowledge/playbooks, knowledge/templates, knowledge/prompts
    - system: /tmp/vibe_os/agents, /tmp/vibe_os/models
    - docs: OPERATIONS.md, SETTINGS.md, ENVOY.md
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List


@dataclass
class DataPathsConfig:
    """
    Data paths for runtime state and persistence.

    Maps to violations in:
    - registry_agent.py: data/registry/citizens.json
    - vault_tool.py: data/security/master.key
    - economy.py, bank_tool.py, ledger_tool.py: data/economy.db
    - license_tool.py: data/registry/licenses.json
    - ledger_visualizer.py: data/ledger/audit_trail.jsonl
    - watchdog_tool.py: data/ledger/kernel.jsonl, violations.jsonl
    - agency_director.py: data/reports
    - memory.py: data/events/herald.jsonl
    - identity_tool.py: data/identities
    - scout_tool_legacy.py: data/federation/pokedex.json
    - supreme_court tools: data/supreme_court
    """

    root: str = "data"
    economy_db: str = "{root}/economy.db"
    registry_citizens: str = "{root}/registry/citizens.json"
    registry_licenses: str = "{root}/registry/licenses.json"
    security_master_key: str = "{root}/security/master.key"
    ledger_audit_trail: str = "{root}/ledger/audit_trail.jsonl"
    ledger_kernel: str = "{root}/ledger/kernel.jsonl"
    ledger_violations: str = "{root}/ledger/violations.jsonl"
    reports: str = "{root}/reports"
    events_herald: str = "{root}/events/herald.jsonl"
    identities: str = "{root}/identities"
    federation_pokedex: str = "{root}/federation/pokedex.json"
    supreme_court: str = "{root}/supreme_court"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DataPathsConfig":
        return cls(
            root=data.get("root", "data"),
            economy_db=data.get("economy_db", "{root}/economy.db"),
            registry_citizens=data.get("registry_citizens", "{root}/registry/citizens.json"),
            registry_licenses=data.get("registry_licenses", "{root}/registry/licenses.json"),
            security_master_key=data.get("security_master_key", "{root}/security/master.key"),
            ledger_audit_trail=data.get("ledger_audit_trail", "{root}/ledger/audit_trail.jsonl"),
            ledger_kernel=data.get("ledger_kernel", "{root}/ledger/kernel.jsonl"),
            ledger_violations=data.get("ledger_violations", "{root}/ledger/violations.jsonl"),
            reports=data.get("reports", "{root}/reports"),
            events_herald=data.get("events_herald", "{root}/events/herald.jsonl"),
            identities=data.get("identities", "{root}/identities"),
            federation_pokedex=data.get("federation_pokedex", "{root}/federation/pokedex.json"),
            supreme_court=data.get("supreme_court", "{root}/supreme_court"),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "root": self.root,
            "economy_db": self.economy_db,
            "registry_citizens": self.registry_citizens,
            "registry_licenses": self.registry_licenses,
            "security_master_key": self.security_master_key,
            "ledger_audit_trail": self.ledger_audit_trail,
            "ledger_kernel": self.ledger_kernel,
            "ledger_violations": self.ledger_violations,
            "reports": self.reports,
            "events_herald": self.events_herald,
            "identities": self.identities,
            "federation_pokedex": self.federation_pokedex,
            "supreme_court": self.supreme_court,
        }

    def resolve(self, path_key: str) -> Path:
        """Resolve a path with variable substitution."""
        value = getattr(self, path_key, None)
        if value is None:
            raise KeyError(f"Unknown data path: {path_key}")
        resolved = value.replace("{root}", self.root)
        return Path(resolved)


@dataclass
class CartridgePathsConfig:
    """
    Cartridge directory paths.

    Maps to violations in:
    - watchman/cartridge_main.py: vibe_core/cartridges/system, agent_city
    - registry_agent.py: vibe_core/cartridges/system
    - auditor/cartridge_main.py: vibe_core/cartridges/system
    - loaders/schema.py: plugins, cartridges/system, agent_city, phoenix/sections
    - steward/loader.py: cartridges/system, agent_city
    - topology.py: cartridges/system, agent_city
    """

    system: str = "vibe_core/cartridges/system"
    agent_city: str = "vibe_core/cartridges/agent_city"
    plugins: str = "vibe_core/plugins"
    phoenix_sections: str = "vibe_core/phoenix/sections"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CartridgePathsConfig":
        return cls(
            system=data.get("system", "vibe_core/cartridges/system"),
            agent_city=data.get("agent_city", "vibe_core/cartridges/agent_city"),
            plugins=data.get("plugins", "vibe_core/plugins"),
            phoenix_sections=data.get("phoenix_sections", "vibe_core/phoenix/sections"),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "system": self.system,
            "agent_city": self.agent_city,
            "plugins": self.plugins,
            "phoenix_sections": self.phoenix_sections,
        }

    def resolve(self, path_key: str) -> Path:
        """Resolve a cartridge path."""
        value = getattr(self, path_key, None)
        if value is None:
            raise KeyError(f"Unknown cartridge path: {path_key}")
        return Path(value)


@dataclass
class KnowledgePathsConfig:
    """
    Knowledge directory paths.

    Maps to violations in:
    - circuit_loader.py: knowledge/circuits, vibe_core/playbook/circuits (LEGACY)
    - playbook_loader.py: knowledge/playbooks, vibe_core/playbook/playbooks (LEGACY)
    - phoenix/config.py: vibe_core/playbook/circuits, MATRIX.md, config
    - section_loader.py: vibe_core/phoenix/sections, config
    """

    root: str = "knowledge"
    circuits: str = "{root}/circuits"
    playbooks: str = "{root}/playbooks"
    templates: str = "{root}/templates"
    prompts: str = "{root}/prompts"
    config: str = "config"
    matrix: str = "MATRIX.md"

    # Legacy paths (for deprecation warnings)
    legacy_circuits: str = "vibe_core/playbook/circuits"
    legacy_playbooks: str = "vibe_core/playbook/playbooks"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "KnowledgePathsConfig":
        return cls(
            root=data.get("root", "knowledge"),
            circuits=data.get("circuits", "{root}/circuits"),
            playbooks=data.get("playbooks", "{root}/playbooks"),
            templates=data.get("templates", "{root}/templates"),
            prompts=data.get("prompts", "{root}/prompts"),
            config=data.get("config", "config"),
            matrix=data.get("matrix", "MATRIX.md"),
            legacy_circuits=data.get("legacy_circuits", "vibe_core/playbook/circuits"),
            legacy_playbooks=data.get("legacy_playbooks", "vibe_core/playbook/playbooks"),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "root": self.root,
            "circuits": self.circuits,
            "playbooks": self.playbooks,
            "templates": self.templates,
            "prompts": self.prompts,
            "config": self.config,
            "matrix": self.matrix,
            "legacy_circuits": self.legacy_circuits,
            "legacy_playbooks": self.legacy_playbooks,
        }

    def resolve(self, path_key: str) -> Path:
        """Resolve a knowledge path with variable substitution."""
        value = getattr(self, path_key, None)
        if value is None:
            raise KeyError(f"Unknown knowledge path: {path_key}")
        resolved = value.replace("{root}", self.root)
        return Path(resolved)


@dataclass
class SystemPathsConfig:
    """
    System paths for runtime directories.

    Maps to violations in:
    - cli.py: /tmp/vibe_os/...
    - local_llama_provider.py: /tmp/vibe_os/models
    - kernel_spawn.py: /tmp/vibe_os/agents
    - vfs.py: /tmp/vibe_os/agents
    """

    runtime_root: str = "/tmp/vibe_os"
    agents: str = "{runtime_root}/agents"
    models: str = "{runtime_root}/models"
    cache: str = "{runtime_root}/cache"
    logs: str = "{runtime_root}/logs"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SystemPathsConfig":
        return cls(
            runtime_root=data.get("runtime_root", "/tmp/vibe_os"),
            agents=data.get("agents", "{runtime_root}/agents"),
            models=data.get("models", "{runtime_root}/models"),
            cache=data.get("cache", "{runtime_root}/cache"),
            logs=data.get("logs", "{runtime_root}/logs"),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "runtime_root": self.runtime_root,
            "agents": self.agents,
            "models": self.models,
            "cache": self.cache,
            "logs": self.logs,
        }

    def resolve(self, path_key: str) -> Path:
        """Resolve a system path with variable substitution."""
        value = getattr(self, path_key, None)
        if value is None:
            raise KeyError(f"Unknown system path: {path_key}")
        resolved = value.replace("{runtime_root}", self.runtime_root)
        return Path(resolved)


@dataclass
class DocPathsConfig:
    """
    Documentation/Markdown paths.

    Maps to (acceptable) violations in:
    - doc_renderer.py: OPERATIONS.md, SETTINGS.md, ENVOY.md
    - envoy_sync.py: ENVOY.md
    - settings_sync.py: SETTINGS.md
    """

    operations: str = "OPERATIONS.md"
    settings: str = "SETTINGS.md"
    envoy: str = "ENVOY.md"
    readme: str = "README.md"
    index: str = "INDEX.md"
    agents: str = "AGENTS.md"
    help: str = "HELP.md"
    tasks: str = "TASKS.md"
    opus: str = "OPUS.md"
    citymap: str = "CITYMAP.md"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DocPathsConfig":
        return cls(
            operations=data.get("operations", "OPERATIONS.md"),
            settings=data.get("settings", "SETTINGS.md"),
            envoy=data.get("envoy", "ENVOY.md"),
            readme=data.get("readme", "README.md"),
            index=data.get("index", "INDEX.md"),
            agents=data.get("agents", "AGENTS.md"),
            help=data.get("help", "HELP.md"),
            tasks=data.get("tasks", "TASKS.md"),
            opus=data.get("opus", "OPUS.md"),
            citymap=data.get("citymap", "CITYMAP.md"),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "operations": self.operations,
            "settings": self.settings,
            "envoy": self.envoy,
            "readme": self.readme,
            "index": self.index,
            "agents": self.agents,
            "help": self.help,
            "tasks": self.tasks,
            "opus": self.opus,
            "citymap": self.citymap,
        }

    def resolve(self, path_key: str) -> Path:
        """Resolve a doc path."""
        value = getattr(self, path_key, None)
        if value is None:
            raise KeyError(f"Unknown doc path: {path_key}")
        return Path(value)


@dataclass
class PathsConfig:
    """
    Master Paths Configuration.

    Auto-discovered by SectionLoader -> loads from config/paths.yaml

    VEDA-4 Pattern:
    - section_id: "paths" (SHABDA - unique identifier)
    - source_file: "paths.yaml" (ARTHA - where to load from)
    - from_dict/to_dict (PRATYAYA - parse/serialize)
    - validate() (KARMA - enforce invariants)

    Usage in code:
        # Before (BAD - hardcoded):
        path = Path("data/economy.db")

        # After (GOOD - injected):
        path = config.paths.data.resolve("economy_db")
    """

    section_id: str = "paths"
    source_file: str = "paths.yaml"

    data: DataPathsConfig = field(default_factory=DataPathsConfig)
    cartridges: CartridgePathsConfig = field(default_factory=CartridgePathsConfig)
    knowledge: KnowledgePathsConfig = field(default_factory=KnowledgePathsConfig)
    system: SystemPathsConfig = field(default_factory=SystemPathsConfig)
    docs: DocPathsConfig = field(default_factory=DocPathsConfig)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PathsConfig":
        """Create PathsConfig from YAML dictionary."""
        return cls(
            data=DataPathsConfig.from_dict(data.get("data", {})),
            cartridges=CartridgePathsConfig.from_dict(data.get("cartridges", {})),
            knowledge=KnowledgePathsConfig.from_dict(data.get("knowledge", {})),
            system=SystemPathsConfig.from_dict(data.get("system", {})),
            docs=DocPathsConfig.from_dict(data.get("docs", {})),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary (for saving/export)."""
        return {
            "data": self.data.to_dict(),
            "cartridges": self.cartridges.to_dict(),
            "knowledge": self.knowledge.to_dict(),
            "system": self.system.to_dict(),
            "docs": self.docs.to_dict(),
        }

    def validate(self) -> List[str]:
        """
        Validate configuration.

        Returns:
            List of error messages (empty = valid)
        """
        errors = []

        # Validate data root exists or is creatable
        data_root = Path(self.data.root)
        if not data_root.exists() and not data_root.parent.exists():
            errors.append(f"data.root parent does not exist: {data_root.parent}")

        # Validate cartridge paths exist
        for path_type in ["system", "agent_city", "plugins"]:
            cart_path = self.cartridges.resolve(path_type)
            if not cart_path.exists():
                errors.append(f"cartridges.{path_type} does not exist: {cart_path}")

        # Validate knowledge root
        knowledge_root = Path(self.knowledge.root)
        if not knowledge_root.exists():
            errors.append(f"knowledge.root does not exist: {knowledge_root}")

        return errors

    def resolve_all(self) -> Dict[str, Path]:
        """
        Resolve all paths for debugging/inspection.

        Returns:
            Dict mapping path names to resolved Path objects
        """
        result = {}

        # Data paths
        for key in [
            "root",
            "economy_db",
            "registry_citizens",
            "registry_licenses",
            "security_master_key",
            "ledger_audit_trail",
            "ledger_kernel",
            "ledger_violations",
            "reports",
            "events_herald",
            "identities",
            "federation_pokedex",
            "supreme_court",
        ]:
            try:
                result[f"data.{key}"] = self.data.resolve(key)
            except KeyError:
                pass

        # Cartridge paths
        for key in ["system", "agent_city", "plugins", "phoenix_sections"]:
            try:
                result[f"cartridges.{key}"] = self.cartridges.resolve(key)
            except KeyError:
                pass

        # Knowledge paths
        for key in [
            "root",
            "circuits",
            "playbooks",
            "templates",
            "prompts",
            "config",
            "matrix",
            "legacy_circuits",
            "legacy_playbooks",
        ]:
            try:
                result[f"knowledge.{key}"] = self.knowledge.resolve(key)
            except KeyError:
                pass

        # System paths
        for key in ["runtime_root", "agents", "models", "cache", "logs"]:
            try:
                result[f"system.{key}"] = self.system.resolve(key)
            except KeyError:
                pass

        # Doc paths
        for key in ["operations", "settings", "envoy", "readme", "index", "agents", "help", "tasks", "opus", "citymap"]:
            try:
                result[f"docs.{key}"] = self.docs.resolve(key)
            except KeyError:
                pass

        return result
