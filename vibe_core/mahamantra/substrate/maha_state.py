"""
MAHASTATE - Sovereign State Layer
=================================

"om purnam adah purnam idam" - That is complete, this is complete.

MahaState sits ABOVE PhoenixConfig and can PIERCE (override) config values.
MINIMAL implementation - no redundant validation (Kumaras handles that).

HIERARCHY:
    MahaState (sovereign) → pierces → PhoenixConfig (legacy)
    Nagas ← Garuda controls

WHAT IT DOES:
- pierce(): Override config values with sovereign state
- persist(): Save/load state to disk
- garuda_flight(): Suppress Nagas during sensitive operations

WHAT IT DOES NOT DO:
- Validation (Kumaras handles that at Position 5)
- Position checking (SSOT is constant - checking it is meaningless)
- Redundant observation (the Mahamantra algorithm IS the computation)

WATERTIGHT: No Any types.
"""

from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "brahma"
__position__ = 1
__genesis__ = "0xa117b53a"  # GenesisByte: parampara % 37 == 0

import hashlib
import json
import logging
import shutil
import threading
import time
from collections import OrderedDict
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import (
    Callable,
    Dict,
    Final,
    FrozenSet,
    List,
    Literal,
    Optional,
    Protocol,
    Union,
    runtime_checkable,
)

from vibe_core.mahamantra.protocols._seed import PARAMPARA

logger = logging.getLogger(__name__)

# =============================================================================
# WATERTIGHT TYPE DEFINITIONS (No Any!)
# =============================================================================

StateValue = Union[str, int, float, bool, None]
SourceType = Literal["sovereign", "config", "computed", "boot", "naga"]

# =============================================================================
# STATE LOCATIONS
# =============================================================================

STATE_DIR: Final[Path] = Path(".vibe/state/mahamantra")
STATE_FILE: Final[str] = "maha_state.json"
MAX_BACKUPS: Final[int] = 5

# =============================================================================
# THRESHOLD CONSTANTS (SSOT-derived)
# =============================================================================
# These control state management limits, derived from mahamantra constants

MAX_STATE_ENTRIES: Final[int] = 72   # NADI_RESONANCE - max sovereign overrides
KERNEL_RESERVE: Final[int] = 16      # HIDDEN_RESERVE - reserved for kernel state
MALA_THRESHOLD: Final[int] = 108     # MALA - cleanup cycle threshold
KISHORA_MAX_STALE: Final[int] = 79   # KISHORA_NUMERATOR - max stale entry age


# =============================================================================
# STATE ENTRY
# =============================================================================


@dataclass(frozen=True)
class StateEntry:
    """A single state entry with provenance."""

    key: str
    value: StateValue
    source: SourceType
    timestamp: str
    pierced: bool = False
    hash: str = ""

    def __post_init__(self) -> None:
        if not self.hash:
            content = f"{self.key}:{self.value}:{self.source}:{self.timestamp}"
            computed = hashlib.sha256(content.encode()).hexdigest()[:16]
            object.__setattr__(self, "hash", computed)

    def to_dict(self) -> Dict[str, StateValue]:
        return {
            "key": self.key,
            "value": self.value,
            "source": self.source,
            "timestamp": self.timestamp,
            "pierced": self.pierced,
            "hash": self.hash,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, StateValue]) -> "StateEntry":
        return cls(
            key=str(data.get("key", "")),
            value=data.get("value"),
            source=str(data.get("source", "sovereign")),  # type: ignore[arg-type]
            timestamp=str(data.get("timestamp", "")),
            pierced=bool(data.get("pierced", False)),
            hash=str(data.get("hash", "")),
        )

    def verify_integrity(self) -> bool:
        content = f"{self.key}:{self.value}:{self.source}:{self.timestamp}"
        expected = hashlib.sha256(content.encode()).hexdigest()[:16]
        return self.hash == expected


# =============================================================================
# GARUDA BRIDGE (Naga Control)
# =============================================================================


@runtime_checkable
class GarudaBridge(Protocol):
    @property
    def is_flying(self) -> bool: ...
    def fly(self) -> "GarudaFlightContext": ...


class GarudaFlightContext(Protocol):
    def __enter__(self) -> None: ...
    def __exit__(self, exc_type: object, exc_val: object, exc_tb: object) -> None: ...


class _NullFlightContext:
    """No-op when Garuda not available."""
    def __enter__(self) -> None: pass
    def __exit__(self, exc_type: object, exc_val: object, exc_tb: object) -> None: pass


# =============================================================================
# MAHASTATE - Minimal Sovereign State
# =============================================================================


class MahaState:
    """
    Sovereign state layer above PhoenixConfig.

    MINIMAL: Only pierce, persist, garuda. No redundant validation.
    """

    _instance: Optional["MahaState"] = None
    _initialized: bool = False
    _lock: threading.Lock = threading.Lock()

    def __init__(self) -> None:
        self._entries: Dict[str, StateEntry] = {}
        self._observers: List[Callable[[str, StateEntry], None]] = []
        self._config_ref: Optional[object] = None
        self._garuda_ref: Optional[GarudaBridge] = None
        self._state_dir: Path = STATE_DIR
        self._dirty: bool = False
        self._boot_count: int = 0
        self._started_at: float = time.time()
        self._pierce_history: OrderedDict[str, float] = OrderedDict()

    @classmethod
    def get_instance(cls) -> "MahaState":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
                    cls._instance._load_state()
                    cls._instance._boot_count += 1
                    cls._initialized = True
        return cls._instance

    @classmethod
    def reset_instance(cls) -> None:
        with cls._lock:
            if cls._instance is not None:
                cls._instance.save()
            cls._instance = None
            cls._initialized = False

    # =========================================================================
    # STATE OPERATIONS
    # =========================================================================

    def set(
        self,
        key: str,
        value: StateValue,
        pierce: bool = False,
        source: SourceType = "sovereign",
    ) -> None:
        entry = StateEntry(
            key=key,
            value=value,
            source=source,
            timestamp=datetime.now().isoformat(),
            pierced=pierce,
        )

        with self._lock:
            self._entries[key] = entry
            self._dirty = True

        for observer in self._observers:
            try:
                observer(key, entry)
            except Exception as e:
                logger.warning(f"State observer failed for {key}: {e}")

    def get(self, key: str, default: StateValue = None) -> StateValue:
        """Priority: sovereign (pierced) → config → default."""
        if key in self._entries:
            entry = self._entries[key]
            if entry.pierced or entry.source == "sovereign":
                return entry.value

        config = self._get_config()
        if config is not None:
            try:
                result = config.read(key)
                if result is not None and hasattr(result, "value"):
                    return result.value
            except Exception:
                pass

        return default

    def has(self, key: str) -> bool:
        return key in self._entries

    def keys(self) -> FrozenSet[str]:
        return frozenset(self._entries.keys())

    def get_entry(self, key: str) -> Optional[StateEntry]:
        return self._entries.get(key)

    def delete(self, key: str) -> bool:
        with self._lock:
            if key in self._entries:
                del self._entries[key]
                self._dirty = True
                return True
        return False

    # =========================================================================
    # PIERCE (Override Config)
    # =========================================================================

    def pierce(self, key: str, value: StateValue) -> None:
        """Sovereign override - this value WINS over config."""
        now = time.time()
        dedup_key = f"{key}:{value}"
        if dedup_key in self._pierce_history:
            if now - self._pierce_history[dedup_key] < 1.0:
                return
        self._pierce_history[dedup_key] = now
        self._trim_history()

        self.set(key, value, pierce=True, source="sovereign")
        logger.info(f"MahaState PIERCED: {key} = {value}")

    def unpierce(self, key: str) -> bool:
        entry = self._entries.get(key)
        if entry is not None and entry.pierced:
            return self.delete(key)
        return False

    def pierced_keys(self) -> List[str]:
        return [k for k, v in self._entries.items() if v.pierced]

    def _trim_history(self) -> None:
        while len(self._pierce_history) > 1000:
            self._pierce_history.popitem(last=False)

    # =========================================================================
    # OBSERVERS
    # =========================================================================

    def observe(self, callback: Callable[[str, StateEntry], None]) -> None:
        self._observers.append(callback)

    def unobserve(self, callback: Callable[[str, StateEntry], None]) -> None:
        if callback in self._observers:
            self._observers.remove(callback)

    # =========================================================================
    # GARUDA (Naga Control)
    # =========================================================================

    def garuda_flight(self) -> GarudaFlightContext:
        """Suppress Nagas during sensitive operations."""
        garuda = self._get_garuda()
        if garuda is None:
            return _NullFlightContext()
        return garuda.fly()

    @property
    def is_garuda_flying(self) -> bool:
        garuda = self._get_garuda()
        return garuda.is_flying if garuda else False

    # =========================================================================
    # PERSISTENCE
    # =========================================================================

    def save(self) -> bool:
        if not self._dirty:
            return True

        try:
            self._state_dir.mkdir(parents=True, exist_ok=True)
            state_file = self._state_dir / STATE_FILE

            if state_file.exists():
                self._rotate_backups(state_file)

            data = {
                "version": 2,
                "timestamp": datetime.now().isoformat(),
                "parampara": PARAMPARA,
                "entries": {k: v.to_dict() for k, v in self._entries.items()},
                "boot_count": self._boot_count,
            }

            temp_file = state_file.with_suffix(".tmp")
            temp_file.write_text(json.dumps(data, indent=2))
            temp_file.replace(state_file)

            self._dirty = False
            logger.debug(f"MahaState saved: {len(self._entries)} entries")
            return True

        except Exception as e:
            logger.error(f"Failed to save MahaState: {e}")
            return False

    def _rotate_backups(self, state_file: Path) -> None:
        backup_dir = self._state_dir / "maha_state_backup"
        backup_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        shutil.copy2(state_file, backup_dir / f"{ts}_{STATE_FILE}")
        backups = sorted(backup_dir.glob(f"*_{STATE_FILE}"))
        while len(backups) > MAX_BACKUPS:
            backups.pop(0).unlink()

    def _load_state(self) -> None:
        state_file = self._state_dir / STATE_FILE
        if not state_file.exists():
            return

        try:
            data = json.loads(state_file.read_text())
            if not isinstance(data, dict):
                return

            entries = data.get("entries", {})
            for key, entry_data in entries.items():
                if isinstance(entry_data, dict):
                    self._entries[key] = StateEntry.from_dict(entry_data)

            self._boot_count = data.get("boot_count", 0)
            logger.debug(f"MahaState loaded: {len(self._entries)} entries")

        except Exception as e:
            logger.warning(f"Failed to load MahaState: {e}")

    # =========================================================================
    # LAZY REFS (Avoid Circular Imports)
    # =========================================================================

    def _get_config(self) -> Optional[object]:
        if self._config_ref is None:
            try:
                from vibe_core.mahamantra.substrate.config import get_config
                self._config_ref = get_config()
            except Exception:
                pass
        return self._config_ref

    def _get_garuda(self) -> Optional[GarudaBridge]:
        if self._garuda_ref is None:
            try:
                from vibe_core.naga.garuda import garuda
                self._garuda_ref = garuda  # type: ignore[assignment]
            except Exception:
                pass
        return self._garuda_ref

    # =========================================================================
    # STATUS
    # =========================================================================

    def get_status(self) -> Dict[str, Union[str, int, float, bool]]:
        return {
            "boot_count": self._boot_count,
            "uptime_seconds": time.time() - self._started_at,
            "entries_count": len(self._entries),
            "pierced_count": len(self.pierced_keys()),
            "dirty": self._dirty,
            "garuda_flying": self.is_garuda_flying,
        }


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================


def get_maha_state() -> MahaState:
    return MahaState.get_instance()


def pierce(key: str, value: StateValue) -> None:
    get_maha_state().pierce(key, value)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "StateValue",
    "SourceType",
    "StateEntry",
    "GarudaBridge",
    "GarudaFlightContext",
    "MahaState",
    "get_maha_state",
    "pierce",
]
