"""
OPUS-307 Phase F: Manifest-Driven Discovery

THE END OF ITERDIR CRAWLING.

This registry scans for manifests ONCE at boot and caches them.
All loaders query this registry instead of scanning the filesystem.

"Das System WEISS was installiert ist, es RATET nicht."

VEDA-4 Pattern:
    SHABDA   → Boot: Scan for manifest.json files (ONE TIME)
    ARTHA    → Validate and parse manifests
    PRATYAYA → Build indexed registry
    KARMA    → Loaders query registry (NO iterdir!)

Usage:
    # At boot (once):
    ManifestRegistry.scan_all()

    # In loaders (many times, no iterdir):
    manifests = ManifestRegistry.get_by_type("plugin")
    manifest = ManifestRegistry.get("opus_assistant")
"""

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

logger = logging.getLogger("MANIFEST.REGISTRY")


@dataclass
class ManifestEntry:
    """
    A discovered manifest entry.

    Immutable after creation - the registry is a snapshot.
    """

    id: str
    type: str  # "plugin", "cartridge", "section", "circuit"
    path: Path  # Path to manifest.json
    manifest: Dict[str, Any]
    enabled: bool = True
    priority: int = 100

    @property
    def entry_point(self) -> Optional[Path]:
        """Get the entry point file path."""
        ep = self.manifest.get("entry_point")
        if ep:
            return self.path.parent / ep
        return None

    @property
    def parent_dir(self) -> Path:
        """Get the parent directory of the manifest."""
        return self.path.parent


class ManifestRegistry:
    """
    Central registry for all manifests in the system.

    PHILOSOPHY:
    - Scans ONCE at boot
    - All queries are O(1) dictionary lookups
    - No iterdir() after initialization

    THE ANTI-PATTERN WE'RE KILLING:
        for item in base_path.iterdir():  # TAMAS - blind scanning
            ...

    THE NEW PATTERN:
        for manifest in ManifestRegistry.get_by_type("plugin"):  # SATTVA - knowing
            ...
    """

    # Scan paths for each type
    SCAN_PATHS: Dict[str, List[Path]] = {
        "plugin": [Path("vibe_core/plugins")],
        "cartridge": [
            Path("vibe_core/cartridges/system"),
            Path("vibe_core/cartridges/agent_city"),
        ],
        "section": [Path("vibe_core/phoenix/sections")],
        "circuit": [
            Path("vibe_core/playbook/circuits"),
            Path("knowledge/genesis/circuits"),
            Path("knowledge/circuits"),
        ],
        # Knowledge packs (cognitive packs, genesis, etc.)
        "cognitive_pack": [Path("knowledge")],
    }

    # Manifest filenames to look for (in order of priority)
    MANIFEST_FILENAMES = ["manifest.json", "manifest.yaml", "cartridge.yaml"]

    # The registry (populated by scan_all)
    _entries: Dict[str, ManifestEntry] = {}
    _by_type: Dict[str, List[ManifestEntry]] = {}
    _scanned: bool = False

    @classmethod
    def scan_all(cls, force: bool = False) -> int:
        """
        Scan all known paths for manifests.

        This is the ONLY place where iterdir() is allowed.
        It runs ONCE at boot.

        Args:
            force: Re-scan even if already scanned

        Returns:
            Number of manifests discovered
        """
        if cls._scanned and not force:
            return len(cls._entries)

        cls._entries.clear()
        cls._by_type.clear()

        total = 0

        for item_type, paths in cls.SCAN_PATHS.items():
            cls._by_type[item_type] = []

            for base_path in paths:
                if not base_path.exists():
                    continue

                count = cls._scan_directory(base_path, item_type)
                total += count

        cls._scanned = True
        logger.info(f"[MANIFEST.REGISTRY] Scanned {total} manifests (Types: {list(cls._by_type.keys())})")

        return total

    @classmethod
    def _scan_directory(cls, base_path: Path, item_type: str) -> int:
        """
        Scan a directory for manifests.

        This is the ONLY iterdir() in the system.
        """
        count = 0

        # THE LAST ITERDIR - after this, we're done scanning
        for item in base_path.iterdir():
            if not item.is_dir():
                continue
            if item.name.startswith((".", "_")):
                continue

            # Look for manifest
            manifest_path = None
            for filename in cls.MANIFEST_FILENAMES:
                candidate = item / filename
                if candidate.exists():
                    manifest_path = candidate
                    break

            if not manifest_path:
                continue

            # Parse manifest
            try:
                manifest = cls._load_manifest(manifest_path)
            except Exception as e:
                logger.warning(f"Failed to parse {manifest_path}: {e}")
                continue

            # Create entry
            entry_id = manifest.get("id", item.name)
            entry = ManifestEntry(
                id=entry_id,
                type=manifest.get("type", item_type),
                path=manifest_path,
                manifest=manifest,
                enabled=manifest.get("enabled", True),
                priority=manifest.get("priority", 100),
            )

            cls._entries[entry_id] = entry
            cls._by_type[item_type].append(entry)
            count += 1

        return count

    @classmethod
    def _load_manifest(cls, path: Path) -> Dict[str, Any]:
        """
        Load manifest from file.

        Handles special cases:
        - cartridge.yaml: Has nested 'meta:' section containing id, name, etc.
        """
        if path.suffix == ".json":
            with open(path) as f:
                return json.load(f)
        elif path.suffix == ".yaml":
            import yaml

            with open(path) as f:
                data = yaml.safe_load(f)

            # Handle cartridge.yaml format: unwrap 'meta' section
            if path.name == "cartridge.yaml" and "meta" in data:
                # Merge meta into top level but preserve original structure
                meta = data.get("meta", {})
                return {
                    "id": meta.get("id", path.parent.name),
                    "name": meta.get("name"),
                    "version": meta.get("version"),
                    "type": "cartridge",
                    "description": meta.get("description"),
                    "enabled": data.get("enabled", True),
                    "priority": data.get("priority", 100),
                    "_raw": data,  # Keep original for reference
                }

            return data
        else:
            raise ValueError(f"Unknown manifest format: {path.suffix}")

    # =========================================================================
    # PUBLIC API - O(1) lookups, NO iterdir
    # =========================================================================

    @classmethod
    def get(cls, entry_id: str) -> Optional[ManifestEntry]:
        """Get manifest by ID."""
        cls._ensure_scanned()
        return cls._entries.get(entry_id)

    @classmethod
    def get_by_type(cls, item_type: str) -> List[ManifestEntry]:
        """Get all manifests of a specific type."""
        cls._ensure_scanned()
        return cls._by_type.get(item_type, [])

    @classmethod
    def get_enabled(cls, item_type: str) -> List[ManifestEntry]:
        """Get all enabled manifests of a specific type."""
        return [e for e in cls.get_by_type(item_type) if e.enabled]

    @classmethod
    def get_sorted_by_priority(cls, item_type: str) -> List[ManifestEntry]:
        """Get manifests sorted by priority (lowest first)."""
        return sorted(cls.get_enabled(item_type), key=lambda e: e.priority)

    @classmethod
    def all(cls) -> List[ManifestEntry]:
        """Get all manifests."""
        cls._ensure_scanned()
        return list(cls._entries.values())

    @classmethod
    def all_ids(cls) -> List[str]:
        """Get all manifest IDs."""
        cls._ensure_scanned()
        return list(cls._entries.keys())

    @classmethod
    def has(cls, entry_id: str) -> bool:
        """Check if manifest exists."""
        cls._ensure_scanned()
        return entry_id in cls._entries

    @classmethod
    def types(cls) -> List[str]:
        """Get all registered types."""
        cls._ensure_scanned()
        return list(cls._by_type.keys())

    @classmethod
    def count(cls, item_type: Optional[str] = None) -> int:
        """Count manifests."""
        cls._ensure_scanned()
        if item_type:
            return len(cls._by_type.get(item_type, []))
        return len(cls._entries)

    @classmethod
    def _ensure_scanned(cls) -> None:
        """Ensure registry has been scanned."""
        if not cls._scanned:
            cls.scan_all()

    @classmethod
    def clear(cls) -> None:
        """Clear the registry (for testing)."""
        cls._entries.clear()
        cls._by_type.clear()
        cls._scanned = False

    # =========================================================================
    # INTROSPECTION
    # =========================================================================

    @classmethod
    def status(cls) -> Dict[str, Any]:
        """Get registry status for debugging."""
        cls._ensure_scanned()
        return {
            "scanned": cls._scanned,
            "total": len(cls._entries),
            "by_type": {t: len(entries) for t, entries in cls._by_type.items()},
            "scan_paths": {t: [str(p) for p in paths] for t, paths in cls.SCAN_PATHS.items()},
        }
