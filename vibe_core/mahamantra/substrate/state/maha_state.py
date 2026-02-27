"""
MAHASTATE - Sovereign State Adapter (BALARAMA PATTERN)
======================================================

"baladevera svarupa -- sankarshana
ananta, pradyumna, aniruddha, -- tanra gana"
"Balarama's forms are Sankarshana, Ananta, Pradyumna, Aniruddha" (CC Adi 5.10)

BALARAMA PATTERN: Wrap legacy, don't migrate.
MahaState wraps ALL existing state systems and makes them accessible
through ONE unified sovereign interface.

WRAPPED SYSTEMS (vibe_core/state/):
- Prakriti: 3-Layer State Engine (STHULA/PRANA/PURUSHA)
- StateService: Single Point for Writes
- StateSyncHolon: Plugin State Discovery + Git Sync
- StateSyncWeaver: Meta-Orchestration
- CognitiveWeaver: State <-> Knowledge Bridge
- GunaClassifier: Guna Diagnosis (SATTVA/RAJAS/TAMAS)

SOVEREIGN LAYER:
- pierce(): Override config values
- persist(): Own state persistence
- garuda_flight(): Naga control

PHILOSOPHY:
"alte struktur in neue struktur" - Old systems run THROUGH MahaState.
The legacy becomes manageable. The sovereign layer ADDS, never REPLACES.

WATERTIGHT: No Any types.
"""

from __future__ import annotations

from vibe_core.mahamantra.protocols._seed import HALVES, KSETRAJNA, PANCHA, TRINITY, WORDS

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "brahma"
__position__ = KSETRAJNA
__genesis__ = "0xa117b53a"  # GenesisByte: parampara % 37 == 0

import hashlib
import json
import logging
import shutil
import threading
import time
from collections import OrderedDict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import (
    TYPE_CHECKING,
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

from vibe_core.mahamantra.protocols._seed import (
    HIDDEN_RESERVE,
    KISHORA_NUMERATOR,
    MALA,
    NADI_RESONANCE,
    PARAMPARA,
)

if TYPE_CHECKING:
    from vibe_core.state.cognitive_weaver import CognitiveWeaver
    from vibe_core.state.guna_classifier import GunaClassifier, StateGuna
    from vibe_core.state.prakriti import Prakriti
    from vibe_core.state.state_service import StateService
    from vibe_core.state.sync_holon import StateSyncHolon
    from vibe_core.state.weaver import StateSyncWeaver

logger = logging.getLogger(__name__)

# =============================================================================
# WATERTIGHT TYPE DEFINITIONS (No Any!)
# =============================================================================

StateValue = Union[str, int, float, bool, None]
SourceType = Literal["sovereign", "config", "computed", "boot", "naga", "prakriti"]

# =============================================================================
# SOVEREIGN CONSTANTS (From Seed - Thresholds for pierce decisions)
# =============================================================================

# Max concurrent state entries before warning
MAX_STATE_ENTRIES: Final[int] = NADI_RESONANCE  # 72

# Reserve capacity for kernel operations
KERNEL_RESERVE: Final[int] = HIDDEN_RESERVE  # 16

# Full cycle threshold (commit after this many changes)
MALA_THRESHOLD: Final[int] = MALA  # 108

# Age threshold for Krishna's eternal youth (max staleness in minutes)
KISHORA_MAX_STALE: Final[int] = KISHORA_NUMERATOR  # 79

# =============================================================================
# STATE LOCATIONS
# =============================================================================

STATE_DIR: Final[Path] = Path(".vibe/state/mahamantra")
STATE_FILE: Final[str] = "maha_state.json"
MAX_BACKUPS: Final[int] = PANCHA


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
            computed = hashlib.sha256(content.encode()).hexdigest()[:WORDS]
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
        expected = hashlib.sha256(content.encode()).hexdigest()[:WORDS]
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

    def __enter__(self) -> None:
        pass

    def __exit__(self, exc_type: object, exc_val: object, exc_tb: object) -> None:
        pass


# =============================================================================
# MAHASTATE - Sovereign State Adapter (BALARAMA PATTERN)
# =============================================================================


class MahaState:
    """
    Sovereign state adapter wrapping ALL existing state systems.

    BALARAMA PATTERN: Wrap legacy, don't migrate.

    WRAPPED SYSTEMS:
    - prakriti: 3-Layer State Engine
    - state_service: Single Point for Writes
    - sync_holon: Plugin State Discovery
    - weaver: Meta-Orchestration
    - cognitive_weaver: State <-> Knowledge Bridge
    - guna_classifier: Guna Diagnosis

    SOVEREIGN LAYER:
    - pierce(): Override config values
    - persist(): Own state persistence
    - garuda_flight(): Naga control
    """

    _instance: Optional["MahaState"] = None
    _initialized: bool = False
    _lock: threading.Lock = threading.Lock()

    def __init__(self, workspace: Optional[Path] = None) -> None:
        self._workspace = workspace or Path.cwd()

        # === SOVEREIGN STATE (pierce/persist) ===
        self._entries: Dict[str, StateEntry] = {}
        self._observers: List[Callable[[str, StateEntry], None]] = []
        self._state_dir: Path = STATE_DIR
        self._dirty: bool = False
        self._boot_count: int = 0
        self._started_at: float = time.time()
        self._pierce_history: OrderedDict[str, float] = OrderedDict()

        # === WRAPPED SYSTEMS (lazy loaded) ===
        self._prakriti: Optional["Prakriti"] = None
        self._state_service: Optional["StateService"] = None
        self._sync_holon: Optional["StateSyncHolon"] = None
        self._weaver: Optional["StateSyncWeaver"] = None
        self._cognitive_weaver: Optional["CognitiveWeaver"] = None
        self._guna_classifier: Optional["GunaClassifier"] = None
        self._config_ref: Optional[object] = None
        self._garuda_ref: Optional[GarudaBridge] = None

    @classmethod
    def get_instance(cls, workspace: Optional[Path] = None) -> "MahaState":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls(workspace)
                    cls._instance._load_state()
                    cls._instance._boot_count += KSETRAJNA
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
    # WRAPPED SYSTEMS (BALARAMA - Lazy Loading)
    # =========================================================================

    @property
    def prakriti(self) -> Optional["Prakriti"]:
        """The Unified State Engine (3 layers: STHULA/PRANA/PURUSHA)."""
        if self._prakriti is None:
            try:
                from vibe_core.state.prakriti import Prakriti

                self._prakriti = Prakriti(self._workspace)
                logger.debug("MahaState: Prakriti wrapped")
            except ImportError as e:
                logger.warning(f"MahaState: Prakriti not available: {e}")
        return self._prakriti

    @property
    def state_service(self) -> Optional["StateService"]:
        """Single Point for all State Writes."""
        if self._state_service is None:
            try:
                from vibe_core.state.state_service import get_state_service

                self._state_service = get_state_service(self._workspace)
                logger.debug("MahaState: StateService wrapped")
            except ImportError as e:
                logger.warning(f"MahaState: StateService not available: {e}")
        return self._state_service

    @property
    def sync_holon(self) -> Optional["StateSyncHolon"]:
        """Plugin State Discovery + Git Sync."""
        if self._sync_holon is None:
            try:
                from vibe_core.state.sync_holon import StateSyncHolon

                if self.prakriti:
                    self._sync_holon = StateSyncHolon(self.prakriti)
                    logger.debug("MahaState: StateSyncHolon wrapped")
            except ImportError as e:
                logger.warning(f"MahaState: StateSyncHolon not available: {e}")
        return self._sync_holon

    @property
    def weaver(self) -> Optional["StateSyncWeaver"]:
        """Meta-Orchestration (DISCOVER -> CLASSIFY -> DECIDE -> EXECUTE)."""
        if self._weaver is None:
            try:
                from vibe_core.state.weaver import get_state_sync_weaver

                self._weaver = get_state_sync_weaver(self.prakriti, self.sync_holon)
                logger.debug("MahaState: StateSyncWeaver wrapped")
            except ImportError as e:
                logger.warning(f"MahaState: StateSyncWeaver not available: {e}")
        return self._weaver

    @property
    def cognitive_weaver(self) -> Optional["CognitiveWeaver"]:
        """State <-> Knowledge Bridge."""
        if self._cognitive_weaver is None:
            try:
                from vibe_core.state.cognitive_weaver import get_cognitive_weaver

                self._cognitive_weaver = get_cognitive_weaver()
                logger.debug("MahaState: CognitiveWeaver wrapped")
            except ImportError as e:
                logger.warning(f"MahaState: CognitiveWeaver not available: {e}")
        return self._cognitive_weaver

    @property
    def guna_classifier(self) -> Optional["GunaClassifier"]:
        """Guna Diagnosis (SATTVA/RAJAS/TAMAS)."""
        if self._guna_classifier is None:
            try:
                from vibe_core.state.guna_classifier import GunaClassifier

                git_state = self.prakriti.git if self.prakriti else None
                self._guna_classifier = GunaClassifier(
                    workspace=self._workspace,
                    git_state=git_state,
                )
                logger.debug("MahaState: GunaClassifier wrapped")
            except ImportError as e:
                logger.warning(f"MahaState: GunaClassifier not available: {e}")
        return self._guna_classifier

    # =========================================================================
    # CONVENIENCE ACCESSORS (Prakriti Layers)
    # =========================================================================

    @property
    def git(self) -> Optional[object]:
        """GitState from Prakriti (Layer 1: STHULA)."""
        return self.prakriti.git if self.prakriti else None

    @property
    def files(self) -> Optional[object]:
        """FileState from Prakriti (Layer 1: STHULA)."""
        return self.prakriti.files if self.prakriti else None

    @property
    def ledger(self) -> Optional[object]:
        """LedgerState from Prakriti (Layer 1: STHULA)."""
        return self.prakriti.ledger if self.prakriti else None

    @property
    def kernel(self) -> Optional[object]:
        """KernelState from Prakriti (Layer 2: PRANA)."""
        return self.prakriti.kernel if self.prakriti else None

    @property
    def ephemeral(self) -> Optional[object]:
        """EphemeralState from Prakriti (Layer 2: PRANA)."""
        return self.prakriti.ephemeral if self.prakriti else None

    @property
    def personas(self) -> Optional[object]:
        """PersonaManager from Prakriti (Layer 3: PURUSHA)."""
        return self.prakriti.personas if self.prakriti else None

    # =========================================================================
    # SOVEREIGN STATE OPERATIONS (pierce/set/get)
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
        """Priority: sovereign (pierced) -> config -> default."""
        if key in self._entries:
            entry = self._entries[key]
            if entry.pierced or entry.source in ("sovereign", "seal"):
                return entry.value

        config = self._get_config()
        if config is not None:
            try:
                result = config.read(key)
                if result is not None and hasattr(result, "value"):
                    return result.value
            except Exception as _exc:
                logger.exception("Unexpected error: %s", _exc)

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
    # PIERCE (Sovereign Override)
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
    # WEAVER OPERATIONS (Delegated)
    # =========================================================================

    def weave(self) -> Optional[object]:
        """Weave state + knowledge into unified context (via CognitiveWeaver)."""
        if self.cognitive_weaver:
            return self.cognitive_weaver.weave()
        return None

    def pulse(self) -> Optional[object]:
        """Run one weave cycle (via StateSyncWeaver)."""
        if self.weaver:
            return self.weaver.pulse()
        return None

    def diagnose(self) -> Optional[Dict[str, object]]:
        """Full system diagnosis (via CognitiveWeaver)."""
        if self.cognitive_weaver:
            return self.cognitive_weaver.diagnose()
        return None

    def diagnose_guna(self, path: Path) -> Optional["StateGuna"]:
        """Diagnose Guna of a path (via GunaClassifier)."""
        if self.guna_classifier:
            return self.guna_classifier.classify(path).guna
        return None

    def heal_toward_sattva(self, path: Path) -> Optional["StateGuna"]:
        """Heal path toward Sattva (via StateSyncHolon)."""
        if self.sync_holon:
            return self.sync_holon.heal_toward_sattva(path)
        return None

    # =========================================================================
    # PERSISTENCE (Sovereign State)
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
                "version": TRINITY,
                "timestamp": datetime.now().isoformat(),
                "parampara": PARAMPARA,
                "entries": {k: v.to_dict() for k, v in self._entries.items()},
                "boot_count": self._boot_count,
                "thresholds": {
                    "max_entries": MAX_STATE_ENTRIES,
                    "kernel_reserve": KERNEL_RESERVE,
                    "mala_threshold": MALA_THRESHOLD,
                    "kishora_max_stale": KISHORA_MAX_STALE,
                },
            }

            temp_file = state_file.with_suffix(".tmp")
            temp_file.write_text(json.dumps(data, indent=HALVES))
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
            except Exception as _exc:
                logger.exception("Unexpected error: %s", _exc)
        return self._config_ref

    def _get_garuda(self) -> Optional[GarudaBridge]:
        if self._garuda_ref is None:
            try:
                from vibe_core.naga.garuda import garuda

                self._garuda_ref = garuda  # type: ignore[assignment]
            except Exception as _exc:
                logger.exception("Unexpected error: %s", _exc)
        return self._garuda_ref

    # =========================================================================
    # STATUS (Unified)
    # =========================================================================

    def get_status(self) -> Dict[str, Union[str, int, float, bool, Dict[str, bool]]]:
        """Get comprehensive status including all wrapped systems."""
        return {
            # Sovereign state
            "boot_count": self._boot_count,
            "uptime_seconds": time.time() - self._started_at,
            "entries_count": len(self._entries),
            "pierced_count": len(self.pierced_keys()),
            "dirty": self._dirty,
            "garuda_flying": self.is_garuda_flying,
            # Wrapped systems availability
            "systems": {
                "prakriti": self._prakriti is not None,
                "state_service": self._state_service is not None,
                "sync_holon": self._sync_holon is not None,
                "weaver": self._weaver is not None,
                "cognitive_weaver": self._cognitive_weaver is not None,
                "guna_classifier": self._guna_classifier is not None,
            },
            # Thresholds
            "thresholds": {
                "max_entries": MAX_STATE_ENTRIES,
                "mala_threshold": MALA_THRESHOLD,
            },
        }

    def get_wrapped_systems(self) -> Dict[str, bool]:
        """Check which systems are available for wrapping."""
        return {
            "prakriti": self.prakriti is not None,
            "state_service": self.state_service is not None,
            "sync_holon": self.sync_holon is not None,
            "weaver": self.weaver is not None,
            "cognitive_weaver": self.cognitive_weaver is not None,
            "guna_classifier": self.guna_classifier is not None,
        }

    # =========================================================================
    # BALARAMA SEALING (Body/Soul Separation - Async)
    # =========================================================================

    def seal(self, key: str, content: object) -> None:
        """
        Seal content: Compress to Seed + Set Sticky bit.

        ASYNC SERIALIZATION: This does NOT write to disk immediately.
        It marks the state dirty. The System Loop will flush it.

        Args:
            key: Path key (e.g. "viveka_decisions.json")
            content: Data to seal
        """
        try:
            # Lazy import to avoid circular dependency
            from vibe_core.mahamantra.adapters.compression import MahaCompression

            # Compress content to Seed (Soul)
            result = MahaCompression().encode_samskara(content)

            # Store Seed as the Value
            # source="seal" indicates this is a File Seal, not a Config Override
            self.set(key, result.seed, source="seal")

            # Note: set() marks _dirty=True. We do NOT call save() here.
            # This prevents IO bloat.
            logger.debug(f"MahaState SEALED: {key} -> {result.seed}")

        except Exception as e:
            logger.warning(f"Failed to seal {key}: {e}")

    def validate(self, key: str, content: object) -> str:
        """
        Validate content against sealed Seed.

        Returns:
            "MATCH" - Perfect alignment
            "DRIFT" - New content, old seed (Atomicity gap) - OK
            "TAMAS" - Corruption detected (if stricter checks enabled)
            "UNKNOWN" - No seal found
        """
        config_seed = self.get(key)
        if config_seed is None:
            return "UNKNOWN"  # Not sealed yet

        try:
            from vibe_core.mahamantra.adapters.compression import MahaCompression

            current_seed = MahaCompression().encode_samskara(content).seed

            if current_seed == config_seed:
                return "MATCH"

            # If seeds mismatch, strictly it's DRIFT (unsealed changes)
            # We don't scream "TAMAS" yet unless we track timestamps.
            return "DRIFT"

        except Exception:
            return "UNKNOWN"

    def persist(self) -> None:
        """Alias for save() (Sovereign Interface)."""
        self.save()


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================


def get_maha_state(workspace: Optional[Path] = None) -> MahaState:
    return MahaState.get_instance(workspace)


def pierce(key: str, value: StateValue) -> None:
    get_maha_state().pierce(key, value)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Types
    "StateValue",
    "SourceType",
    "StateEntry",
    "GarudaBridge",
    "GarudaFlightContext",
    # Constants (Thresholds)
    "MAX_STATE_ENTRIES",
    "KERNEL_RESERVE",
    "MALA_THRESHOLD",
    "KISHORA_MAX_STALE",
    "STATE_DIR",
    "STATE_FILE",
    # Main class
    "MahaState",
    # Convenience
    "get_maha_state",
    "pierce",
]
