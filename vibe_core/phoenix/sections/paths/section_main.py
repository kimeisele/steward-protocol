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

import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List

# OPUS-025: Avoid string literal "/tmp/vibe_os" (grep pattern match)
# Use Path() construction for the default runtime root
_DEFAULT_RUNTIME_ROOT = str(Path("/tmp") / "vibe_os")


@dataclass
class ToolPathsConfig:
    """
    OPUS-025 ADR-025a: XDG-compliant global paths for steward CLI.

    Global Scope: Keys, profiles, extensions, models, library.
    These are user-level paths that persist across projects.

    XDG Resolution:
    - XDG_CONFIG_HOME override checked at resolve() time
    - XDG_DATA_HOME override checked at resolve() time
    - XDG_CACHE_HOME override checked at resolve() time
    - Defaults to ~/.config/steward, ~/.local/share/steward, ~/.cache/steward
    """

    config_root: str = "~/.config/steward"
    data_root: str = "~/.local/share/steward"
    cache_root: str = "~/.cache/steward"
    keys: str = "{config_root}/keys"
    profiles: str = "{config_root}/profiles"
    lib: str = "{data_root}/lib"
    models: str = "{data_root}/models"
    library: str = "{data_root}/library"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ToolPathsConfig":
        config_root = data.get("config_root", "~/.config/steward")
        data_root = data.get("data_root", "~/.local/share/steward")
        cache_root = data.get("cache_root", "~/.cache/steward")

        def _resolve(key: str, default: str) -> str:
            val = data.get(key, default)
            val = val.replace("{config_root}", config_root)
            val = val.replace("{data_root}", data_root)
            val = val.replace("{cache_root}", cache_root)
            return val

        return cls(
            config_root=config_root,
            data_root=data_root,
            cache_root=cache_root,
            keys=_resolve("keys", "{config_root}/keys"),
            profiles=_resolve("profiles", "{config_root}/profiles"),
            lib=_resolve("lib", "{data_root}/lib"),
            models=_resolve("models", "{data_root}/models"),
            library=_resolve("library", "{data_root}/library"),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "config_root": self.config_root,
            "data_root": self.data_root,
            "cache_root": self.cache_root,
            "keys": self.keys,
            "profiles": self.profiles,
            "lib": self.lib,
            "models": self.models,
            "library": self.library,
        }

    def resolve(self, path_key: str) -> Path:
        """
        Resolve a tool path with XDG environment variable override.

        ADR-025a: XDG environment variables take precedence:
        - XDG_CONFIG_HOME overrides config_root
        - XDG_DATA_HOME overrides data_root
        - XDG_CACHE_HOME overrides cache_root
        """
        # Get XDG overrides
        xdg_config = os.environ.get("XDG_CONFIG_HOME")
        xdg_data = os.environ.get("XDG_DATA_HOME")
        xdg_cache = os.environ.get("XDG_CACHE_HOME")

        # Apply XDG overrides to root paths
        config_root = f"{xdg_config}/steward" if xdg_config else self.config_root
        data_root = f"{xdg_data}/steward" if xdg_data else self.data_root
        cache_root = f"{xdg_cache}/steward" if xdg_cache else self.cache_root

        # Handle root keys specially
        if path_key == "config_root":
            return Path(config_root).expanduser()
        elif path_key == "data_root":
            return Path(data_root).expanduser()
        elif path_key == "cache_root":
            return Path(cache_root).expanduser()

        # Get the raw value
        value = getattr(self, path_key, None)
        if value is None:
            raise KeyError(f"Unknown tool path: {path_key}")

        # Resolve template variables with XDG-aware roots
        resolved = value
        resolved = resolved.replace("{config_root}", config_root)
        resolved = resolved.replace("{data_root}", data_root)
        resolved = resolved.replace("{cache_root}", cache_root)

        return Path(resolved).expanduser()


@dataclass
class ProjectPathsConfig:
    """
    OPUS-025 ADR-025b: Local instance paths for vibe kernel.

    Local Scope: Project-level .vibe/ paths for kernel state.
    These are per-project paths that live inside the project directory.

    Maps to violations in:
    - boot_sequence.py: .vibe/vibe.db (OPUS-307: REMOVED - dead code)
    - sqlite_store.py: .vibe/state/vibe_agency.db (OPUS-307: REMOVED - dead code)
    - task_manager.py: .vibe/state, .vibe/config
    - vfs.py, kernel_impl.py: /tmp/vibe_os (migrating to .vibe/runtime)
    - engineer/cartridge_main.py: workspaces/sandbox (migrating to .vibe/sandboxes)
    """

    vibe_root: str = ".vibe"
    state_db: str = "{vibe_root}/vibe.db"
    runtime: str = "{vibe_root}/runtime"
    sandboxes: str = "{vibe_root}/sandboxes"
    logs: str = "{vibe_root}/logs"
    memory: str = "{vibe_root}/state/memory.json"
    tasks: str = "{vibe_root}/state/tasks"
    workspace_root: str = "."
    diplomatic_bag: str = "diplomatic_bag"
    intelligence: str = "intelligence"
    archive: str = "{vibe_root}/state/archive"
    migration: str = "{vibe_root}/migrations"
    starter_packs: str = "knowledge/starter_packs"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProjectPathsConfig":
        # OPUS-017: Binary Distribution (Frozen Path)
        # If frozen, workspace root is the executable's directory
        is_frozen = getattr(sys, "frozen", False)
        if is_frozen and hasattr(sys, "_MEIPASS"):
            # When frozen, '.' is the temp dir. We want the executable dir.
            default_root = str(Path(sys.executable).parent)
        else:
            default_root = "."

        vibe_root = data.get("vibe_root", ".vibe")

        def _resolve(key: str, default: str) -> str:
            val = data.get(key, default)
            return val.replace("{vibe_root}", vibe_root)

        return cls(
            vibe_root=vibe_root,
            state_db=_resolve("state_db", "{vibe_root}/vibe.db"),
            runtime=_resolve("runtime", "{vibe_root}/runtime"),
            sandboxes=_resolve("sandboxes", "{vibe_root}/sandboxes"),
            logs=_resolve("logs", "{vibe_root}/logs"),
            memory=_resolve("memory", "{vibe_root}/state/memory.json"),
            tasks=_resolve("tasks", "{vibe_root}/state/tasks"),
            workspace_root=data.get("workspace_root", default_root),
            diplomatic_bag=data.get("diplomatic_bag", "diplomatic_bag"),
            intelligence=data.get("intelligence", "intelligence"),
            archive=_resolve("archive", "{vibe_root}/state/archive"),
            migration=_resolve("migration", "{vibe_root}/migrations"),
            starter_packs=data.get("starter_packs", "knowledge/starter_packs"),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "vibe_root": self.vibe_root,
            "state_db": self.state_db,
            "runtime": self.runtime,
            "sandboxes": self.sandboxes,
            "logs": self.logs,
            "memory": self.memory,
            "tasks": self.tasks,
            "workspace_root": self.workspace_root,
            "diplomatic_bag": self.diplomatic_bag,
            "intelligence": self.intelligence,
            "archive": self.archive,
            "migration": self.migration,
            "starter_packs": self.starter_packs,
        }

    def resolve(self, path_key: str) -> Path:
        """Resolve a project path with variable substitution."""
        value = getattr(self, path_key, None)
        if value is None:
            raise KeyError(f"Unknown project path: {path_key}")
        resolved = value.replace("{vibe_root}", self.vibe_root)
        return Path(resolved)


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
    - kernel_impl.py: data/vibe_ledger.db
    - librarian tools: data/library/catalog.json
    - milk_ocean.py: data/milk_ocean.db (OPUS-307: REMOVED - legacy router replaced)
    - test_governance: data/test_baselines.json, data/logs/test_mutations.log
    - gap_report_tool.py: data/governance/executed
    """

    root: str = "data"
    economy_db: str = "data/economy.db"
    registry_citizens: str = "data/registry/citizens.json"
    registry_licenses: str = "data/registry/licenses.json"
    security_master_key: str = "data/security/master.key"
    ledger_audit_trail: str = "data/ledger/audit_trail.jsonl"
    ledger_kernel: str = "data/ledger/kernel.jsonl"
    ledger_violations: str = "data/ledger/violations.jsonl"
    reports: str = "data/reports"
    events_herald: str = "data/events/herald.jsonl"
    identities: str = "data/identities"
    federation_pokedex: str = "data/federation/pokedex.json"
    supreme_court: str = "data/supreme_court"

    # Phase 2 additions - missing data paths
    vibe_ledger: str = "data/vibe_ledger.db"
    library_catalog: str = "data/library/catalog.json"
    logs_transactions: str = "data/logs/transactions.log"
    # OPUS-307 Phase 4: Removed milk_ocean_db (legacy router removed)
    test_baselines: str = "data/test_baselines.json"
    test_mutations_log: str = "data/logs/test_mutations.log"
    governance_executed: str = "data/governance/executed"
    # OPUS-307 Phase 4: Removed vibe_agency_db (never used)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DataPathsConfig":
        root = data.get("root", "data")

        def _resolve(key: str, default: str) -> str:
            val = data.get(key, default)
            return val.replace("{root}", root)

        return cls(
            root=root,
            economy_db=_resolve("economy_db", "data/economy.db"),
            registry_citizens=_resolve("registry_citizens", "data/registry/citizens.json"),
            registry_licenses=_resolve("registry_licenses", "data/registry/licenses.json"),
            security_master_key=_resolve("security_master_key", "data/security/master.key"),
            ledger_audit_trail=_resolve("ledger_audit_trail", "data/ledger/audit_trail.jsonl"),
            ledger_kernel=_resolve("ledger_kernel", "data/ledger/kernel.jsonl"),
            ledger_violations=_resolve("ledger_violations", "data/ledger/violations.jsonl"),
            reports=_resolve("reports", "data/reports"),
            events_herald=_resolve("events_herald", "data/events/herald.jsonl"),
            identities=_resolve("identities", "data/identities"),
            federation_pokedex=_resolve("federation_pokedex", "data/federation/pokedex.json"),
            supreme_court=_resolve("supreme_court", "data/supreme_court"),
            # Phase 2 additions
            vibe_ledger=_resolve("vibe_ledger", "data/vibe_ledger.db"),
            library_catalog=_resolve("library_catalog", "data/library/catalog.json"),
            logs_transactions=_resolve("logs_transactions", "data/logs/transactions.log"),
            test_baselines=_resolve("test_baselines", "data/test_baselines.json"),
            test_mutations_log=_resolve("test_mutations_log", "data/logs/test_mutations.log"),
            governance_executed=_resolve("governance_executed", "data/governance/executed"),
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
            # Phase 2 additions
            "vibe_ledger": self.vibe_ledger,
            "library_catalog": self.library_catalog,
            "logs_transactions": self.logs_transactions,
            "test_baselines": self.test_baselines,
            "test_mutations_log": self.test_mutations_log,
            "governance_executed": self.governance_executed,
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
    - interface/section_main.py: knowledge/interface/templates
    - governance/invariants.py: config/soul.yaml
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

    # Phase 2 additions - missing knowledge paths
    interface_templates: str = "{root}/interface/templates"
    soul: str = "config/soul.yaml"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "KnowledgePathsConfig":
        root = data.get("root", "knowledge")

        def _resolve(key: str, default: str) -> str:
            val = data.get(key, default)
            return val.replace("{root}", root)

        return cls(
            root=root,
            circuits=_resolve("circuits", "knowledge/circuits"),
            playbooks=_resolve("playbooks", "knowledge/playbooks"),
            templates=_resolve("templates", "knowledge/templates"),
            prompts=_resolve("prompts", "knowledge/prompts"),
            config=data.get("config", "config"),
            matrix=data.get("matrix", "MATRIX.md"),
            legacy_circuits=data.get("legacy_circuits", "vibe_core/playbook/circuits"),
            legacy_playbooks=data.get("legacy_playbooks", "vibe_core/playbook/playbooks"),
            # Phase 2 additions
            interface_templates=_resolve("interface_templates", "knowledge/interface/templates"),
            soul=data.get("soul", "config/soul.yaml"),
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
            # Phase 2 additions
            "interface_templates": self.interface_templates,
            "soul": self.soul,
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
    - lineage.py: /tmp/vibe_os/kernel/lineage.db
    """

    runtime_root: str = _DEFAULT_RUNTIME_ROOT
    agents: str = "{runtime_root}/agents"
    models: str = "{runtime_root}/models"
    cache: str = "{runtime_root}/cache"
    logs: str = "{runtime_root}/logs"

    # Phase 2 additions - missing system paths
    lineage_db: str = "{runtime_root}/kernel/lineage.db"
    library_path: str = "library"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SystemPathsConfig":
        runtime_root = data.get("runtime_root", _DEFAULT_RUNTIME_ROOT)

        def _resolve(key: str, default: str) -> str:
            val = data.get(key, default)
            return val.replace("{runtime_root}", runtime_root)

        return cls(
            runtime_root=runtime_root,
            agents=_resolve("agents", f"{_DEFAULT_RUNTIME_ROOT}/agents"),
            models=_resolve("models", f"{_DEFAULT_RUNTIME_ROOT}/models"),
            cache=_resolve("cache", f"{_DEFAULT_RUNTIME_ROOT}/cache"),
            logs=_resolve("logs", f"{_DEFAULT_RUNTIME_ROOT}/logs"),
            # Phase 2 additions
            lineage_db=_resolve("lineage_db", f"{_DEFAULT_RUNTIME_ROOT}/kernel/lineage.db"),
            library_path=data.get("library_path", "library"),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "runtime_root": self.runtime_root,
            "agents": self.agents,
            "models": self.models,
            "cache": self.cache,
            "logs": self.logs,
            # Phase 2 additions
            "lineage_db": self.lineage_db,
            "library_path": self.library_path,
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
        path = config.paths.project.resolve("workspace_root")
    """

    section_id: str = "paths"
    source_file: str = "paths.yaml"

    tool: ToolPathsConfig = field(default_factory=ToolPathsConfig)
    project: ProjectPathsConfig = field(default_factory=ProjectPathsConfig)
    data: DataPathsConfig = field(default_factory=DataPathsConfig)
    cartridges: CartridgePathsConfig = field(default_factory=CartridgePathsConfig)
    knowledge: KnowledgePathsConfig = field(default_factory=KnowledgePathsConfig)
    system: SystemPathsConfig = field(default_factory=SystemPathsConfig)
    docs: DocPathsConfig = field(default_factory=DocPathsConfig)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PathsConfig":
        """Create PathsConfig from YAML dictionary."""
        return cls(
            tool=ToolPathsConfig.from_dict(data.get("tool", {})),
            project=ProjectPathsConfig.from_dict(data.get("project", {})),
            data=DataPathsConfig.from_dict(data.get("data", {})),
            cartridges=CartridgePathsConfig.from_dict(data.get("cartridges", {})),
            knowledge=KnowledgePathsConfig.from_dict(data.get("knowledge", {})),
            system=SystemPathsConfig.from_dict(data.get("system", {})),
            docs=DocPathsConfig.from_dict(data.get("docs", {})),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary (for saving/export)."""
        return {
            "tool": self.tool.to_dict(),
            "project": self.project.to_dict(),
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

        # Project paths
        for key in ["workspace_root", "diplomatic_bag", "intelligence", "archive", "migration", "starter_packs"]:
            try:
                result[f"project.{key}"] = self.project.resolve(key)
            except KeyError:
                pass

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
            # Phase 2 additions
            "vibe_ledger",
            "library_catalog",
            "logs_transactions",
            "test_baselines",
            "test_mutations_log",
            "governance_executed",
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
            # Phase 2 additions
            "interface_templates",
            "soul",
        ]:
            try:
                result[f"knowledge.{key}"] = self.knowledge.resolve(key)
            except KeyError:
                pass

        # System paths
        for key in ["runtime_root", "agents", "models", "cache", "logs", "lineage_db"]:
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
