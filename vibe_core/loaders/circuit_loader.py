"""
Circuit Loader - Auto-discovery for Cognitive Circuits.

INHERITS FROM UnifiedLoader - The fraktal pattern!

Specifics for Circuits:
- Loads from knowledge/circuits/ (DATA location)
- YAML-based circuits (no manifest.json needed - circuit_id is in YAML)
- UNIVERSAL - doesn't care what's inside (LLM, deterministic, human, dog with keyboard)
- Self-describing: circuit_id comes from YAML content

FRAKTAL PRINCIPLE:
    Circuits are DATA, not CODE. They describe WHAT to do, not HOW.
    The executor (LLM, deterministic, human) is pluggable.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "brahma"
__position__ = 1
__genesis__ = "0xd26f5a5e"  # GenesisByte: parampara % 37 == 0

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

from vibe_core.loaders import LoaderRegistry, UnifiedLoader

logger = logging.getLogger("CIRCUIT.LOADER")


@dataclass
class CircuitMeta:
    """
    Metadata about a discovered circuit.

    Circuits are self-describing - ID comes from YAML content.
    """

    circuit_id: str
    circuit_type: str  # "state_machine", "dag", "sequence"
    file_path: Path
    definition: Dict[str, Any]
    description: str = ""
    version: str = "1.0.0"
    triggers: List[Dict[str, Any]] = field(default_factory=list)
    loaded_successfully: bool = True
    error: Optional[str] = None

    def __repr__(self) -> str:
        status = "OK" if self.loaded_successfully else f"FAILED: {self.error}"
        return f"<circuit:{self.circuit_id} type={self.circuit_type} status={status}>"


# Type aliases
CircuitRegistry = Dict[str, Dict[str, Any]]  # circuit_id -> definition
CircuitMetadata = Dict[str, CircuitMeta]  # circuit_id -> metadata


class CircuitLoader(UnifiedLoader):
    """
    Auto-discovery loader for Cognitive Circuits.

    UNIVERSAL - Loads YAML circuits without caring what's inside.
    The same loader works for:
    - LLM-powered circuits
    - Deterministic state machines
    - Human-in-the-loop workflows
    - Anything else

    Scans: knowledge/circuits/**/*.yaml

    Usage:
        # Discover all circuits
        circuits, meta = CircuitLoader.discover_and_load()

        # Get specific circuit
        test_validation = circuits.get("test_validation")
    """

    # === UNIFIED LOADER CONFIG ===
    item_type = "circuit"
    scan_paths = [
        Path("knowledge/circuits"),  # PRIMARY: DATA location (FRAKTAL)
        Path("vibe_core/playbook/circuits"),  # LEGACY: CODE location (backward compat)
    ]
    manifest_filenames = ["manifest.json"]  # Optional for circuits
    entry_suffix = ".yaml"  # Circuits are YAML files

    # === CLASS-LEVEL CACHE ===
    _circuit_cache: Optional[CircuitRegistry] = None
    _metadata_cache: Optional[CircuitMetadata] = None

    # =========================================================================
    # OVERRIDE: Custom discovery for YAML circuits (WITH CACHING)
    # =========================================================================

    @classmethod
    def discover_and_load(
        cls,
        scan_paths: Optional[List[Path]] = None,
        config: Optional[Dict[str, Any]] = None,
        force_refresh: bool = False,
    ) -> Tuple[CircuitRegistry, CircuitMetadata]:
        """
        Discover and load all circuits. CACHED after first call.

        Circuits are YAML files that are self-describing:
        - circuit_id comes from 'circuit_id' or 'circuit.id' in YAML
        - No manifest.json needed

        Args:
            scan_paths: Override default paths
            config: Optional config
            force_refresh: If True, bypass cache

        Returns:
            Tuple of (circuit_definitions, metadata)
        """
        # Return cached if available
        if not force_refresh and cls._circuit_cache is not None:
            return cls._circuit_cache, cls._metadata_cache or {}

        paths = scan_paths or cls.scan_paths
        circuits: CircuitRegistry = {}
        metadata: CircuitMetadata = {}

        for base_path in paths:
            base_path = Path(base_path)
            if not base_path.exists():
                logger.debug(f"[circuit] Scan path does not exist: {base_path}")
                continue

            logger.debug(f"[circuit] Scanning {base_path}...")

            # Recursive YAML discovery
            for yaml_file in base_path.glob("**/*.yaml"):
                try:
                    meta = cls._load_circuit_file(yaml_file)
                    if meta and meta.loaded_successfully:
                        circuits[meta.circuit_id] = meta.definition
                        metadata[meta.circuit_id] = meta
                        logger.debug(f"  Loaded: {meta.circuit_id}")
                except Exception as e:
                    logger.warning(f"  ❌ Failed: {yaml_file.name}: {e}")

        # Cache results
        cls._circuit_cache = circuits
        cls._metadata_cache = metadata

        logger.info(f"[circuit] Loaded {len(circuits)} circuits (cached)")
        return circuits, metadata

    @classmethod
    def clear_cache(cls) -> None:
        """Clear cached circuit data."""
        cls._circuit_cache = None
        cls._metadata_cache = None

    @classmethod
    def _load_circuit_file(cls, yaml_file: Path) -> Optional[CircuitMeta]:
        """
        Load a single circuit YAML file.

        Self-describing: extracts circuit_id from YAML content.
        """
        try:
            with open(yaml_file, "r") as f:
                content = yaml.safe_load(f)

            if content is None:
                return None

            # Extract circuit_id (multiple formats supported)
            circuit_id = (
                content.get("circuit_id")
                or content.get("id")
                or (content.get("circuit", {}) or {}).get("id")
                or yaml_file.stem  # Fallback to filename
            )

            # Extract circuit type
            circuit_type = (
                content.get("type") or (content.get("circuit", {}) or {}).get("type") or "state_machine"  # Default
            )

            # Extract metadata
            description = content.get("description") or (content.get("circuit", {}) or {}).get("description") or ""

            version = content.get("version", "1.0.0")
            triggers = content.get("triggers", [])

            # The definition is the full content (or nested 'circuit' object)
            definition = content.get("circuit", content)

            return CircuitMeta(
                circuit_id=circuit_id,
                circuit_type=circuit_type,
                file_path=yaml_file,
                definition=definition,
                description=description,
                version=version,
                triggers=triggers,
                loaded_successfully=True,
            )

        except yaml.YAMLError as e:
            return CircuitMeta(
                circuit_id=yaml_file.stem,
                circuit_type="unknown",
                file_path=yaml_file,
                definition={},
                loaded_successfully=False,
                error=f"YAML parse error: {e}",
            )
        except Exception as e:
            return CircuitMeta(
                circuit_id=yaml_file.stem,
                circuit_type="unknown",
                file_path=yaml_file,
                definition={},
                loaded_successfully=False,
                error=str(e),
            )

    # =========================================================================
    # UTILITY: Query circuits by trigger
    # =========================================================================

    @classmethod
    def get_circuits_for_trigger(
        cls,
        trigger_event: str,
        circuits: Optional[CircuitRegistry] = None,
        metadata: Optional[CircuitMetadata] = None,
    ) -> List[str]:
        """
        Get circuits that respond to a specific trigger event.

        Args:
            trigger_event: Event name (e.g., "file_created", "file_modified")
            circuits: Pre-loaded circuits (or will discover)
            metadata: Pre-loaded metadata (or will discover)

        Returns:
            List of circuit_ids that handle this trigger
        """
        if metadata is None:
            _, metadata = cls.discover_and_load()

        matching = []
        for circuit_id, meta in metadata.items():
            for trigger in meta.triggers:
                if trigger.get("event") == trigger_event:
                    matching.append(circuit_id)
                    break

        return matching

    @classmethod
    def get_circuits_by_type(
        cls,
        circuit_type: str,
        metadata: Optional[CircuitMetadata] = None,
    ) -> List[str]:
        """
        Get circuits of a specific type.

        Args:
            circuit_type: Type name (e.g., "state_machine", "dag")
            metadata: Pre-loaded metadata (or will discover)

        Returns:
            List of circuit_ids of this type
        """
        if metadata is None:
            _, metadata = cls.discover_and_load()

        return [circuit_id for circuit_id, meta in metadata.items() if meta.circuit_type == circuit_type]


# Register with LoaderRegistry - FRAKTAL!
LoaderRegistry.register("circuit", CircuitLoader)
