"""
Playbook Loader - Auto-discovery for Multi-Agent Playbooks.

INHERITS FROM UnifiedLoader - The fraktal pattern!

Specifics for Playbooks:
- Loads from knowledge/playbooks/ (DATA location)
- YAML-based playbooks with stages and dependencies
- DAG-based execution (topological sort on depends_on)
- Supports loops (max_iterations)

FRAKTAL PRINCIPLE:
    Playbooks are DATA, not CODE. They describe WHAT agents do, not HOW.
    The executor (LLM, deterministic, hybrid) is pluggable.

Key differences from Circuits:
- Circuits: state_machine with states/transitions
- Playbooks: DAG with stages/depends_on/agents
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "narada"
__position__ = 2
__genesis__ = "0xc9639a28"  # GenesisByte: parampara % 37 == 0

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

from vibe_core.loaders import LoaderRegistry, UnifiedLoader

logger = logging.getLogger("PLAYBOOK.LOADER")


@dataclass
class PlaybookStage:
    """A single stage in a playbook."""

    id: str
    name: str
    agent: str  # Agent ID to execute this stage
    description: str = ""
    depends_on: List[str] = field(default_factory=list)
    task: Dict[str, Any] = field(default_factory=dict)
    output: Dict[str, Any] = field(default_factory=dict)
    timeout: str = "300s"
    loop: Optional[Dict[str, Any]] = None  # For enhancement loops


@dataclass
class PlaybookMeta:
    """
    Metadata about a discovered playbook.

    Playbooks are self-describing - ID comes from YAML content.
    """

    playbook_id: str
    playbook_type: str  # "dag", "sequence", "hybrid"
    file_path: Path
    definition: Dict[str, Any]
    description: str = ""
    version: str = "1.0.0"
    triggers: List[Dict[str, Any]] = field(default_factory=list)
    inputs: Dict[str, Any] = field(default_factory=dict)
    stages: List[PlaybookStage] = field(default_factory=list)
    quality_gates: List[Dict[str, Any]] = field(default_factory=list)
    loaded_successfully: bool = True
    error: Optional[str] = None

    def __repr__(self) -> str:
        status = "OK" if self.loaded_successfully else f"FAILED: {self.error}"
        return f"<playbook:{self.playbook_id} stages={len(self.stages)} status={status}>"


# Type aliases
PlaybookRegistry = Dict[str, Dict[str, Any]]  # playbook_id -> definition
PlaybookMetadata = Dict[str, PlaybookMeta]  # playbook_id -> metadata


class PlaybookLoader(UnifiedLoader):
    """
    Auto-discovery loader for Multi-Agent Playbooks.

    UNIVERSAL - Loads YAML playbooks without caring what agents execute them.
    The same loader works for:
    - LLM-powered agent playbooks
    - Deterministic validation playbooks
    - Human-in-the-loop workflows
    - Hybrid combinations

    Scans: knowledge/playbooks/**/*.yaml

    Usage:
        # Discover all playbooks
        playbooks, meta = PlaybookLoader.discover_and_load()

        # Get specific playbook
        test_suite = playbooks.get("comprehensive_test_suite")

        # Get playbook stages
        meta["comprehensive_test_suite"].stages
    """

    # === UNIFIED LOADER CONFIG ===
    item_type = "playbook"
    scan_paths = [
        Path("knowledge/playbooks"),  # PRIMARY: DATA location (FRAKTAL)
        Path("vibe_core/playbook/playbooks"),  # LEGACY: CODE location
    ]
    manifest_filenames = ["manifest.json"]  # Optional
    entry_suffix = ".yaml"

    # === CLASS-LEVEL CACHE ===
    _playbook_cache: Optional[PlaybookRegistry] = None
    _metadata_cache: Optional[PlaybookMetadata] = None

    # =========================================================================
    # OVERRIDE: Custom discovery for YAML playbooks (WITH CACHING)
    # =========================================================================

    @classmethod
    def discover_and_load(
        cls,
        scan_paths: Optional[List[Path]] = None,
        config: Optional[Dict[str, Any]] = None,
        force_refresh: bool = False,
    ) -> Tuple[PlaybookRegistry, PlaybookMetadata]:
        """
        Discover and load all playbooks. CACHED after first call.

        Playbooks are YAML files that are self-describing:
        - playbook_id comes from 'playbook_id' field in YAML
        - No manifest.json needed

        Args:
            scan_paths: Override default paths
            config: Optional config
            force_refresh: If True, bypass cache

        Returns:
            Tuple of (playbook_definitions, metadata)
        """
        # Return cached if available
        if not force_refresh and cls._playbook_cache is not None:
            return cls._playbook_cache, cls._metadata_cache or {}

        paths = scan_paths or cls.scan_paths
        playbooks: PlaybookRegistry = {}
        metadata: PlaybookMetadata = {}

        for base_path in paths:
            base_path = Path(base_path)
            if not base_path.exists():
                logger.debug(f"[playbook] Scan path does not exist: {base_path}")
                continue

            logger.debug(f"[playbook] Scanning {base_path}...")

            # Recursive YAML discovery
            for yaml_file in base_path.glob("**/*.yaml"):
                # Skip schema files
                if yaml_file.name.startswith("_") or yaml_file.name == "schema.yaml":
                    continue

                try:
                    meta = cls._load_playbook_file(yaml_file)
                    if meta and meta.loaded_successfully:
                        playbooks[meta.playbook_id] = meta.definition
                        metadata[meta.playbook_id] = meta
                        logger.debug(f"  Loaded: {meta.playbook_id} ({len(meta.stages)} stages)")
                except Exception as e:
                    logger.warning(f"  ❌ Failed: {yaml_file.name}: {e}")

        # Cache results
        cls._playbook_cache = playbooks
        cls._metadata_cache = metadata

        logger.info(f"[playbook] Loaded {len(playbooks)} playbooks (cached)")
        return playbooks, metadata

    @classmethod
    def clear_cache(cls) -> None:
        """Clear cached playbook data."""
        cls._playbook_cache = None
        cls._metadata_cache = None

    @classmethod
    def _load_playbook_file(cls, yaml_file: Path) -> Optional[PlaybookMeta]:
        """
        Load a single playbook YAML file.

        Self-describing: extracts playbook_id from YAML content.
        """
        try:
            with open(yaml_file, "r") as f:
                content = yaml.safe_load(f)

            if content is None:
                return None

            # Extract playbook_id
            playbook_id = (
                content.get("playbook_id") or content.get("id") or yaml_file.stem  # Fallback to filename
            )

            # Extract type
            playbook_type = content.get("type", "dag")

            # Extract metadata
            description = content.get("description", "")
            version = content.get("version", "1.0.0")
            triggers = content.get("triggers", [])
            inputs = content.get("inputs", {})
            quality_gates = content.get("quality_gates", [])

            # Parse stages
            stages = []
            for stage_def in content.get("stages", []):
                stage = PlaybookStage(
                    id=stage_def.get("id", ""),
                    name=stage_def.get("name", ""),
                    agent=stage_def.get("agent", ""),
                    description=stage_def.get("description", ""),
                    depends_on=stage_def.get("depends_on", []),
                    task=stage_def.get("task", {}),
                    output=stage_def.get("output", {}),
                    timeout=stage_def.get("timeout", "300s"),
                    loop=stage_def.get("loop"),
                )
                stages.append(stage)

            return PlaybookMeta(
                playbook_id=playbook_id,
                playbook_type=playbook_type,
                file_path=yaml_file,
                definition=content,
                description=description,
                version=version,
                triggers=triggers,
                inputs=inputs,
                stages=stages,
                quality_gates=quality_gates,
                loaded_successfully=True,
            )

        except yaml.YAMLError as e:
            return PlaybookMeta(
                playbook_id=yaml_file.stem,
                playbook_type="unknown",
                file_path=yaml_file,
                definition={},
                loaded_successfully=False,
                error=f"YAML parse error: {e}",
            )
        except Exception as e:
            return PlaybookMeta(
                playbook_id=yaml_file.stem,
                playbook_type="unknown",
                file_path=yaml_file,
                definition={},
                loaded_successfully=False,
                error=str(e),
            )

    # =========================================================================
    # UTILITY: Query playbooks
    # =========================================================================

    @classmethod
    def get_playbooks_for_trigger(
        cls,
        trigger_event: str,
        metadata: Optional[PlaybookMetadata] = None,
    ) -> List[str]:
        """
        Get playbooks that respond to a specific trigger event.

        Args:
            trigger_event: Event name (e.g., "plugin_installed", "manual")
            metadata: Pre-loaded metadata (or will discover)

        Returns:
            List of playbook_ids that handle this trigger
        """
        if metadata is None:
            _, metadata = cls.discover_and_load()

        matching = []
        for playbook_id, meta in metadata.items():
            for trigger in meta.triggers:
                if trigger.get("event") == trigger_event:
                    matching.append(playbook_id)
                    break

        return matching

    @classmethod
    def get_execution_order(cls, meta: PlaybookMeta) -> List[str]:
        """
        Get topologically sorted execution order for playbook stages.

        Args:
            meta: Playbook metadata with stages

        Returns:
            List of stage IDs in execution order
        """
        # Build dependency graph
        stages = {s.id: s for s in meta.stages}
        in_degree = {s.id: len(s.depends_on) for s in meta.stages}
        dependents = {s.id: [] for s in meta.stages}

        for stage in meta.stages:
            for dep in stage.depends_on:
                if dep in dependents:
                    dependents[dep].append(stage.id)

        # Kahn's algorithm
        queue = [sid for sid, degree in in_degree.items() if degree == 0]
        order = []

        while queue:
            sid = queue.pop(0)
            order.append(sid)

            for dependent in dependents[sid]:
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)

        # Check for cycles
        if len(order) != len(stages):
            logger.error(f"Playbook {meta.playbook_id} has circular dependencies!")
            return []

        return order


# Register with LoaderRegistry - FRAKTAL!
LoaderRegistry.register("playbook", PlaybookLoader)
