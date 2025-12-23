"""
OPUS-210: SynapseStore - PRANA Aspect of Prakriti

Sanskrit: प्राण (Prana) = Life Force / Vital Energy / Runtime Breath

In Samkhya philosophy, Prana is the vital energy that animates the body.
In Steward Protocol, SynapseStore is a PRANA aspect of Prakriti - it
manages the living synaptic connections that animate MANAS cognition.

NOT a "single source of truth" - that is Prakriti itself.
SynapseStore is an ASPECT that handles synapse persistence (v3 schema).

"The Synapse is the Bridge between Thought and Action."

Unified v3 Schema:
{
    "schema": "v3",
    "version": "YYYY-MM-DD",
    "weights": {
        "trigger:test_failure": {
            "action:run_test": 0.8,
            "action:debug": 0.5
        }
    },
    "triggers": [  # Optional for ordered/legacy access
        {
            "trigger": "trigger:test_failure",
            "varga": "KANTHYA",
            "connections": [{"target": "action:run_test", "weight": 0.8}]
        }
    ],
    "meta": {
        "created": "2025-12-21T00:00:00Z",
        "last_updated": "2025-12-21T12:00:00Z",
        "updates_count": 42,
        "migrated_from": "v2"  # Only if migrated
    }
}

Tattva Mapping (OPUS-097):
    Prakriti → Prana Layer → SynapseStore (synaptic vitality)

Pattern: Singleton with caching (follows triggers.py pattern)
OPUS Reference: OPUS-210-STATE-UNIFICATION, OPUS-171
"""

from __future__ import annotations

import json
import logging
import threading
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("SYNAPSE_STORE")

# Schema versions
SCHEMA_V1 = "v1"  # {"triggers": [], "version": "1.0"}
SCHEMA_V2 = "v2"  # {"weights": {}, "schema": "v2"}
SCHEMA_V3 = "v3"  # Unified

# Default cache TTL in seconds
DEFAULT_CACHE_TTL = 30.0


# =============================================================================
# Data Structures
# =============================================================================


@dataclass
class SynapseConnection:
    """A single synapse connection (trigger → action)."""

    trigger: str
    action: str
    weight: float
    varga: Optional[str] = None
    last_updated: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = {
            "trigger": self.trigger,
            "action": self.action,
            "weight": self.weight,
        }
        if self.varga:
            result["varga"] = self.varga
        if self.last_updated:
            result["last_updated"] = self.last_updated
        return result


@dataclass
class SynapseMigrationResult:
    """Result of a schema migration."""

    success: bool
    from_schema: str
    to_schema: str
    connections_migrated: int
    message: str
    backup_path: Optional[str] = None


@dataclass
class SynapseSnapshot:
    """A snapshot of the synapse state."""

    schema: str
    weights: Dict[str, Dict[str, float]]
    triggers: List[Dict[str, Any]]
    meta: Dict[str, Any]
    total_triggers: int = 0
    total_actions: int = 0
    total_connections: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "schema": self.schema,
            "version": datetime.utcnow().strftime("%Y-%m-%d"),
            "weights": self.weights,
            "triggers": self.triggers,
            "meta": self.meta,
        }


# =============================================================================
# Migration Helpers
# =============================================================================


def detect_schema(data: Dict[str, Any]) -> str:
    """
    Detect the schema version of synapse data.

    Returns:
        "v1", "v2", "v3", or "unknown"
    """
    if not data:
        return "unknown"

    # Explicit v3
    if data.get("schema") == "v3":
        return SCHEMA_V3

    # Explicit v2
    if data.get("schema") == "v2":
        return SCHEMA_V2

    # v1: has "version": "1.0" and no "weights" key
    if data.get("version") == "1.0" and "weights" not in data:
        return SCHEMA_V1

    # Mixed: has both "weights" and "triggers" but no schema
    if "weights" in data and "triggers" in data:
        return SCHEMA_V2  # Treat as v2

    # Only weights dict
    if "weights" in data:
        return SCHEMA_V2

    # Only triggers list
    if "triggers" in data:
        return SCHEMA_V1

    return "unknown"


def migrate_v1_to_v3(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Migrate v1 schema to v3.

    v1 Structure:
    {
        "version": "1.0",
        "triggers": [
            {
                "trigger": "trigger:test_failure",
                "connections": [
                    {"target": "action:run_test", "weight": 0.8}
                ]
            }
        ]
    }

    v3 Structure:
    {
        "schema": "v3",
        "weights": {"trigger:x": {"action:y": 0.8}},
        "triggers": [...],  # Preserved for compatibility
        "meta": {...}
    }
    """
    now = datetime.utcnow().isoformat() + "Z"

    # Build weights from triggers list
    weights: Dict[str, Dict[str, float]] = {}
    triggers_list = data.get("triggers", [])

    for trigger_entry in triggers_list:
        trigger = trigger_entry.get("trigger", "")
        if not trigger:
            continue

        connections = trigger_entry.get("connections", [])
        for conn in connections:
            target = conn.get("target", "")
            weight = conn.get("weight", 0.5)

            if trigger and target:
                if trigger not in weights:
                    weights[trigger] = {}
                weights[trigger][target] = weight

    return {
        "schema": SCHEMA_V3,
        "version": datetime.utcnow().strftime("%Y-%m-%d"),
        "weights": weights,
        "triggers": triggers_list,  # Preserve for compatibility
        "meta": {
            "created": now,
            "last_updated": now,
            "updates_count": 0,
            "migrated_from": SCHEMA_V1,
            "migration_date": now,
        },
    }


def migrate_v2_to_v3(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Migrate v2 schema to v3.

    v2 Structure:
    {
        "schema": "v2",
        "weights": {"trigger:x": {"action:y": 0.8}},
        "triggers": [],  # Optional
        "meta": {"created": "..."}
    }

    v3 Structure:
    {
        "schema": "v3",
        "version": "YYYY-MM-DD",
        "weights": {...},
        "triggers": [...],
        "meta": {...}
    }
    """
    now = datetime.utcnow().isoformat() + "Z"

    weights = data.get("weights", {})
    triggers_list = data.get("triggers", [])
    old_meta = data.get("meta", {})

    # Rebuild triggers list from weights if empty
    if not triggers_list and weights:
        for trigger, actions in weights.items():
            connections = [{"target": action, "weight": weight} for action, weight in actions.items()]
            triggers_list.append(
                {
                    "trigger": trigger,
                    "connections": connections,
                }
            )

    return {
        "schema": SCHEMA_V3,
        "version": datetime.utcnow().strftime("%Y-%m-%d"),
        "weights": weights,
        "triggers": triggers_list,
        "meta": {
            "created": old_meta.get("created", now),
            "last_updated": now,
            "updates_count": old_meta.get("updates_count", 0),
            "migrated_from": SCHEMA_V2,
            "migration_date": now,
        },
    }


def ensure_v3_schema(data: Dict[str, Any]) -> Tuple[Dict[str, Any], Optional[str]]:
    """
    Ensure data is in v3 schema, migrating if necessary.

    Returns:
        Tuple of (v3_data, migrated_from or None if already v3)
    """
    schema = detect_schema(data)

    if schema == SCHEMA_V3:
        return data, None

    if schema == SCHEMA_V1:
        return migrate_v1_to_v3(data), SCHEMA_V1

    if schema == SCHEMA_V2:
        return migrate_v2_to_v3(data), SCHEMA_V2

    # Unknown - treat as empty v3
    now = datetime.utcnow().isoformat() + "Z"
    return {
        "schema": SCHEMA_V3,
        "version": datetime.utcnow().strftime("%Y-%m-%d"),
        "weights": {},
        "triggers": [],
        "meta": {
            "created": now,
            "last_updated": now,
            "updates_count": 0,
            "migrated_from": "unknown",
        },
    }, "unknown"


# =============================================================================
# SynapseStore - The Single Source of Truth
# =============================================================================


class SynapseStore:
    """
    OPUS-171: Unified Synapse Store with v3 Schema.

    Single source of truth for synapse persistence. Replaces 4 duplicate
    _load_synapses() implementations with one unified store.

    Features:
    - Automatic schema migration (v1/v2 → v3)
    - Caching with TTL (like triggers.py)
    - Thread-safe operations
    - Backup before migration

    Usage:
        store = SynapseStore(workspace=Path.cwd())

        # Read
        synapses = store.load()
        weight = store.get_weight("trigger:test", "action:run")

        # Write
        store.set_weight("trigger:test", "action:run", 0.9)
        store.save()

        # Or use the singleton
        from vibe_core.state.synapse_store import get_synapse_store
        store = get_synapse_store()
    """

    # Per-workspace instances (workspace path -> store)
    _instances: Dict[str, "SynapseStore"] = {}
    _lock = threading.Lock()

    def __init__(
        self,
        workspace: Optional[Path] = None,
        cache_ttl: float = DEFAULT_CACHE_TTL,
        seed_weights: Optional[Dict[str, Dict[str, float]]] = None,
    ):
        """
        Initialize SynapseStore.

        Args:
            workspace: Workspace root (default: cwd)
            cache_ttl: Cache time-to-live in seconds
            seed_weights: Initial weights to use if file doesn't exist
        """
        self._workspace = workspace or Path.cwd()

        # 🍎 STATE: Global Sovereign State (ADR-204)
        # Synapses are collective memory, they belong to the State root.
        from vibe_core.state.state_service import get_state_service

        self._state_service = get_state_service(self._workspace)  # Global/Sovereign

        self._synapse_file = self._state_service.state_root / "synapses.json"
        self._backup_dir = self._state_service.state_root / "backups"

        # Cache
        self._cache: Optional[Dict[str, Any]] = None
        self._cache_time: Optional[datetime] = None
        self._cache_ttl = cache_ttl

        # Lock for thread safety
        self._io_lock = threading.Lock()

        # Dirty flag for deferred saves
        self._dirty = False

        # Seed weights for new systems
        self._seed_weights = seed_weights

        logger.debug(f"SynapseStore initialized: {self._synapse_file}")

    # =========================================================================
    # Public API - Read Operations
    # =========================================================================

    def load(self, force: bool = False) -> Dict[str, Any]:
        """
        Load synapses from disk with caching.

        Automatically migrates v1/v2 to v3 if needed.

        Args:
            force: Force reload, bypassing cache

        Returns:
            Synapse data in v3 schema
        """
        now = datetime.utcnow()

        # Check cache validity
        if not force and self._cache is not None and self._cache_time is not None:
            age = (now - self._cache_time).total_seconds()
            if age < self._cache_ttl:
                return self._cache

        with self._io_lock:
            if not self._synapse_file.exists():
                # Initialize with v3 schema (using seed weights if provided)
                self._cache = self._create_empty_v3()
                if self._seed_weights:
                    self._cache["weights"] = self._seed_weights
                    logger.info(f"SynapseStore seeded with {len(self._seed_weights)} triggers")
                self._cache_time = now
                return self._cache

            try:
                raw_data = json.loads(self._synapse_file.read_text())

                # Check and migrate schema
                schema = detect_schema(raw_data)
                if schema != SCHEMA_V3:
                    logger.info(f"Migrating synapses from {schema} to v3")
                    self._backup_before_migration(raw_data, schema)
                    self._cache, _ = ensure_v3_schema(raw_data)
                    # Save migrated data
                    self._save_to_disk(self._cache)
                else:
                    self._cache = raw_data

            except (json.JSONDecodeError, IOError) as e:
                logger.warning(f"Failed to load synapses: {e}")
                self._cache = self._create_empty_v3()

            self._cache_time = now
            return self._cache

    def get_weights(self) -> Dict[str, Dict[str, float]]:
        """Get the weights dictionary."""
        data = self.load()
        return data.get("weights", {})

    def get_weight(self, trigger: str, action: str) -> Optional[float]:
        """Get weight for a specific trigger→action pair."""
        weights = self.get_weights()
        return weights.get(trigger, {}).get(action)

    def get_actions_for_trigger(self, trigger: str) -> Dict[str, float]:
        """Get all actions and weights for a trigger."""
        weights = self.get_weights()
        return weights.get(trigger, {})

    def get_triggers(self) -> List[str]:
        """Get list of all triggers."""
        return list(self.get_weights().keys())

    def get_snapshot(self) -> SynapseSnapshot:
        """Get a snapshot of current synapse state."""
        data = self.load()
        weights = data.get("weights", {})

        total_triggers = len(weights)
        total_actions = len(set(a for actions in weights.values() for a in actions))
        total_connections = sum(len(actions) for actions in weights.values())

        return SynapseSnapshot(
            schema=data.get("schema", "unknown"),
            weights=weights,
            triggers=data.get("triggers", []),
            meta=data.get("meta", {}),
            total_triggers=total_triggers,
            total_actions=total_actions,
            total_connections=total_connections,
        )

    # =========================================================================
    # Public API - Write Operations
    # =========================================================================

    def set_weight(
        self,
        trigger: str,
        action: str,
        weight: float,
        defer_save: bool = True,
    ) -> None:
        """
        Set weight for a trigger→action pair.

        Args:
            trigger: Trigger pattern
            action: Action pattern
            weight: Weight value (0.0-1.0)
            defer_save: If True, mark dirty and save later; else save immediately
        """
        data = self.load()
        weights = data.setdefault("weights", {})

        if trigger not in weights:
            weights[trigger] = {}
        weights[trigger][action] = weight

        # Update meta
        now = datetime.utcnow().isoformat() + "Z"
        data["meta"]["last_updated"] = now
        data["meta"]["updates_count"] = data["meta"].get("updates_count", 0) + 1

        if defer_save:
            self._dirty = True
        else:
            self.save()

    def increment_weight(
        self,
        trigger: str,
        action: str,
        delta: float = 0.05,
        max_weight: float = 0.95,
    ) -> float:
        """
        Increment weight for a trigger→action pair.

        Args:
            trigger: Trigger pattern
            action: Action pattern
            delta: Amount to increment (default 0.05)
            max_weight: Maximum weight cap (default 0.95 for VAIRAGYA)

        Returns:
            New weight after increment
        """
        current = self.get_weight(trigger, action) or 0.5
        new_weight = min(current + delta, max_weight)
        self.set_weight(trigger, action, new_weight)
        return new_weight

    def decrement_weight(
        self,
        trigger: str,
        action: str,
        delta: float = 0.05,
        min_weight: float = 0.1,
    ) -> float:
        """
        Decrement weight for a trigger→action pair.

        Args:
            trigger: Trigger pattern
            action: Action pattern
            delta: Amount to decrement (default 0.05)
            min_weight: Minimum weight floor (default 0.1)

        Returns:
            New weight after decrement
        """
        current = self.get_weight(trigger, action) or 0.5
        new_weight = max(current - delta, min_weight)
        self.set_weight(trigger, action, new_weight)
        return new_weight

    def save(self) -> bool:
        """
        Save synapses to disk.

        Returns:
            True if saved successfully
        """
        if self._cache is None:
            return False

        with self._io_lock:
            success = self._save_to_disk(self._cache)
            if success:
                self._dirty = False
            return success

    def flush(self) -> bool:
        """
        Flush any pending changes to disk.

        Returns:
            True if flushed (or nothing to flush)
        """
        if self._dirty:
            return self.save()
        return True

    def save_raw(self, data: Dict[str, Any]) -> bool:
        """
        Save raw data directly (for legacy code that modifies dict in place).

        Use this when you've modified the dict returned by load() and want
        to persist those changes. Ensures cache is updated.

        Args:
            data: The modified synapse data dict

        Returns:
            True if saved successfully
        """
        with self._io_lock:
            success = self._save_to_disk(data)
            if success:
                self._cache = data
                self._cache_time = datetime.utcnow()
                self._dirty = False
            return success

    # =========================================================================
    # Migration API
    # =========================================================================

    def migrate_to_v3(self) -> SynapseMigrationResult:
        """
        Explicitly migrate current data to v3 schema.

        Returns:
            Migration result with details
        """
        data = self.load(force=True)
        schema = detect_schema(data)

        if schema == SCHEMA_V3:
            return SynapseMigrationResult(
                success=True,
                from_schema=SCHEMA_V3,
                to_schema=SCHEMA_V3,
                connections_migrated=0,
                message="Already v3, no migration needed",
            )

        backup_path = self._backup_before_migration(data, schema)
        migrated, from_schema = ensure_v3_schema(data)

        # Count connections
        connections = sum(len(actions) for actions in migrated.get("weights", {}).values())

        self._cache = migrated
        self._save_to_disk(migrated)

        return SynapseMigrationResult(
            success=True,
            from_schema=from_schema or schema,
            to_schema=SCHEMA_V3,
            connections_migrated=connections,
            message=f"Migrated {connections} connections from {schema} to v3",
            backup_path=str(backup_path) if backup_path else None,
        )

    @staticmethod
    def get_schema_version() -> str:
        """Get the current schema version (v3)."""
        return SCHEMA_V3

    # =========================================================================
    # Internal Methods
    # =========================================================================

    def _create_empty_v3(self) -> Dict[str, Any]:
        """Create an empty v3 schema structure."""
        now = datetime.utcnow().isoformat() + "Z"
        return {
            "schema": SCHEMA_V3,
            "version": datetime.utcnow().strftime("%Y-%m-%d"),
            "weights": {},
            "triggers": [],
            "meta": {
                "created": now,
                "last_updated": now,
                "updates_count": 0,
            },
        }

    def _save_to_disk(self, data: Dict[str, Any]) -> bool:
        """Save data to disk."""
        try:
            self._synapse_file.parent.mkdir(parents=True, exist_ok=True)
            self._synapse_file.write_text(json.dumps(data, indent=2, ensure_ascii=False))
            logger.debug(f"Synapses saved to {self._synapse_file}")
            return True
        except IOError as e:
            logger.error(f"Failed to save synapses: {e}")
            return False

    def _backup_before_migration(
        self,
        data: Dict[str, Any],
        schema: str,
    ) -> Optional[Path]:
        """Create backup before migration."""
        try:
            self._backup_dir.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            backup_file = self._backup_dir / f"synapses_{schema}_{timestamp}.json"
            backup_file.write_text(json.dumps(data, indent=2, ensure_ascii=False))
            logger.info(f"Created backup: {backup_file}")
            return backup_file
        except IOError as e:
            logger.warning(f"Failed to create backup: {e}")
            return None

    def invalidate_cache(self) -> None:
        """Invalidate the cache, forcing next load to read from disk."""
        self._cache = None
        self._cache_time = None

    # =========================================================================
    # Singleton Pattern
    # =========================================================================

    @classmethod
    def get_instance(
        cls,
        workspace: Optional[Path] = None,
        seed_weights: Optional[Dict[str, Dict[str, float]]] = None,
    ) -> "SynapseStore":
        """Get or create SynapseStore instance for workspace."""
        workspace = workspace or Path.cwd()
        key = str(workspace.resolve())
        with cls._lock:
            if key not in cls._instances:
                cls._instances[key] = cls(workspace=workspace, seed_weights=seed_weights)
            return cls._instances[key]

    @classmethod
    def reset_instance(cls, workspace: Optional[Path] = None) -> None:
        """Reset instance for a workspace (for testing)."""
        with cls._lock:
            if workspace is None:
                # Reset all instances
                for store in cls._instances.values():
                    store.flush()
                cls._instances.clear()
            else:
                key = str(workspace.resolve())
                if key in cls._instances:
                    cls._instances[key].flush()
                    del cls._instances[key]


# =============================================================================
# Convenience Functions
# =============================================================================


def get_synapse_store(
    workspace: Optional[Path] = None,
    seed_weights: Optional[Dict[str, Dict[str, float]]] = None,
) -> SynapseStore:
    """
    Get or create a SynapseStore instance for the workspace.

    This is the RECOMMENDED way to access synapse data. Uses per-workspace
    singleton pattern for efficiency.

    Args:
        workspace: Workspace path (default: cwd)
        seed_weights: Initial weights for new systems (only used on first call)

    Returns:
        SynapseStore instance for the workspace
    """
    return SynapseStore.get_instance(workspace=workspace, seed_weights=seed_weights)


def reset_synapse_store(workspace: Optional[Path] = None) -> None:
    """Reset SynapseStore instance(s) for testing."""
    SynapseStore.reset_instance(workspace)


# =============================================================================
# Public API
# =============================================================================


__all__ = [
    # Main class
    "SynapseStore",
    # Data structures
    "SynapseConnection",
    "SynapseSnapshot",
    "SynapseMigrationResult",
    # Migration helpers
    "detect_schema",
    "ensure_v3_schema",
    "migrate_v1_to_v3",
    "migrate_v2_to_v3",
    # Constants
    "SCHEMA_V1",
    "SCHEMA_V2",
    "SCHEMA_V3",
    # Convenience
    "get_synapse_store",
    "reset_synapse_store",
]
