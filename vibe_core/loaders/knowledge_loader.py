"""
Knowledge Loader - Unified Loader implementation for Knowledge Graph.

INHERITS FROM UnifiedLoader.

Fractal Pattern:
    Items: Knowledge Files (YAML)
    Type: "knowledge"
    Scan Path: knowledge/
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "vyasa"
__position__ = 4
__genesis__ = "0x2097d262"  # GenesisByte: parampara % 37 == 0

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

from vibe_core.loaders import ItemMeta, LoaderRegistry, UnifiedLoader

logger = logging.getLogger("KNOWLEDGE.LOADER")


@dataclass
class KnowledgeMeta(ItemMeta):
    """Metadata for a knowledge file."""

    domain: str = "core"
    node_count: int = 0
    edge_count: int = 0
    raw_data: Optional[Dict[str, Any]] = None


class KnowledgeLoader(UnifiedLoader):
    """
    Unified Loader for Knowledge Graph.

    Scans knowledge/ directory for YAML files and loads them.
    Unlike plugins/agents which are directories, knowledge items are FILES.
    """

    # === UNIFIED LOADER CONFIG ===
    item_type = "knowledge"
    scan_paths = [Path("knowledge")]
    entry_suffix = ".yaml"  # Not used for file-based loading but required by base

    # === CLASS STATE ===
    _cache: Optional[Dict[str, KnowledgeMeta]] = None

    @classmethod
    def discover_and_load(
        cls,
        scan_paths: Optional[List[Path]] = None,
        config: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Custom discovery for file-based knowledge.

        Overrides UnifiedLoader.discover_and_load because knowledge
        is distributed across many YAML files, not structured as
        one-directory-per-item.
        """
        paths = scan_paths or cls.scan_paths
        items: Dict[str, Any] = {}
        metadata: Dict[str, KnowledgeMeta] = {}

        for base_path in paths:
            if not base_path.exists():
                logger.debug(f"[knowledge] Scan path does not exist: {base_path}")
                continue

            logger.info(f"[knowledge] Scanning {base_path}...")

            # recursive scan
            for yaml_file in base_path.glob("**/*.yaml"):
                if yaml_file.name.startswith("_"):
                    continue

                try:
                    meta = cls._load_knowledge_file(yaml_file)
                    if meta:
                        # For knowledge, the "item" is the raw data dict
                        items[meta.item_id] = meta.raw_data
                        metadata[meta.item_id] = meta
                        logger.debug(f"  Loaded: {meta.item_id} ({meta.node_count} nodes)")
                except Exception as e:
                    logger.warning(f"  ❌ Failed: {yaml_file.name}: {e}")

        logger.info(f"[knowledge] Loaded {len(items)} knowledge files")
        return items, metadata

    @classmethod
    def _load_knowledge_file(cls, yaml_file: Path) -> Optional[KnowledgeMeta]:
        """Load a single knowledge YAML file."""
        try:
            with open(yaml_file, "r") as f:
                content = yaml.safe_load(f)

            if not content:
                return None

            # Determine ID and Domain
            # If in knowledge/domains/X/file.yaml -> domain=X
            # If in knowledge/core/file.yaml -> domain=core
            domain = "core"
            parts = yaml_file.parts
            if "domains" in parts:
                idx = parts.index("domains")
                if idx + 1 < len(parts):
                    domain = parts[idx + 1]
            elif "core" in parts:
                domain = "core"

            item_id = f"{domain}.{yaml_file.stem}"

            # Count stats
            node_count = len(content.get("nodes", []) or content.get("agents", []) or [])
            edge_count = len(content.get("edges", []) or [])

            return KnowledgeMeta(
                item_id=item_id,
                item_type="knowledge",
                manifest={},  # content is the manifest
                manifest_path=yaml_file,
                entry_path=None,
                entry_class=None,
                loaded_successfully=True,
                domain=domain,
                node_count=node_count,
                edge_count=edge_count,
                raw_data=content,
            )

        except Exception as e:
            logger.error(f"Error loading knowledge file {yaml_file}: {e}")
            return None


# Register with LoaderRegistry
LoaderRegistry.register("knowledge", KnowledgeLoader)
