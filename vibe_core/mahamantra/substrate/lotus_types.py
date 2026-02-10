"""
LOTUS NODE - Auto-Discovery Infrastructure
==========================================

"padma-nābha padma-nābhāya namaḥ"

"Obeisances to the Lord whose navel is like a lotus."
— Vishnu Sahasranama

FOLDER = EXISTENCE = WIRING.

The Lotus grows from the navel of Vishnu (mahamantra).
Each petal (node) auto-discovers from folder structure.

EXTRACTED from __init__.py via SANKIRTAN radiation pattern.
"""

from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "narada"
__position__ = 2
__genesis__ = "0x3e2fa1fe"  # GenesisByte: parampara % 37 == 0

import importlib
import logging
from pathlib import Path
from typing import Dict, FrozenSet, Iterator, Optional, Set, Tuple

logger = logging.getLogger(__name__)

# =============================================================================
# SEED DATA (O(1) lookups — replaces filesystem iteration)
# =============================================================================
# Lazy-loaded to avoid circular imports at module level.
# Once loaded, these are Final tuples/dicts — zero per-call cost.
_SEED_LOADED = False
_QUARTER_NAMES: Tuple[str, ...] = ()
_QUARTER_SET: FrozenSet[str] = frozenset()
_GUARDIAN_SET: FrozenSet[str] = frozenset()
_GUARDIANS_BY_QUARTER: Dict[str, Tuple[str, ...]] = {}


def _ensure_seed() -> None:
    """Load Seed data once (lazy, breaks circular import)."""
    global _SEED_LOADED, _QUARTER_NAMES, _QUARTER_SET, _GUARDIAN_SET, _GUARDIANS_BY_QUARTER
    if _SEED_LOADED:
        return
    from vibe_core.mahamantra.substrate.seed import (
        QUARTER_NAMES, ALL_GUARDIANS, WORDS_PER_QUARTER,
    )
    _QUARTER_NAMES = QUARTER_NAMES
    _QUARTER_SET = frozenset(QUARTER_NAMES)
    _GUARDIAN_SET = frozenset(ALL_GUARDIANS)
    _GUARDIANS_BY_QUARTER = {}
    for qi, qname in enumerate(QUARTER_NAMES):
        start = qi * WORDS_PER_QUARTER
        end = start + WORDS_PER_QUARTER
        _GUARDIANS_BY_QUARTER[qname] = ALL_GUARDIANS[start:end]
    _SEED_LOADED = True

# =============================================================================
# THE LOTUS PATH
# =============================================================================


class LotusPath:
    """Path through the lotus."""

    __slots__ = ("_segments",)

    def __init__(self, segments: Tuple[str, ...] = ()) -> None:
        self._segments = segments

    @property
    def segments(self) -> Tuple[str, ...]:
        return self._segments

    @property
    def depth(self) -> int:
        return len(self._segments)

    @property
    def is_root(self) -> bool:
        return self.depth == 0

    @property
    def folder_path(self) -> str:
        return "/".join(self._segments)

    @property
    def module_path(self) -> str:
        if self.is_root:
            return "vibe_core.mahamantra"
        return "vibe_core.mahamantra." + ".".join(self._segments)

    def child(self, name: str) -> "LotusPath":
        return LotusPath(self._segments + (name,))

    def __repr__(self) -> str:
        return f"LotusPath({self._segments})"


# =============================================================================
# THE LOTUS NODE - Auto-Discovery
# =============================================================================


class LotusNode:
    """
    A node in Krishna's Lotus.

    Auto-discovers children from folder structure.
    FOLDER = EXISTENCE = WIRING.
    """

    __slots__ = ("_path", "_base", "_cache", "_module")

    # Base path for the mahamantra package
    # Adjusted for move to substrate/: Go up one level to reach vibe_core/mahamantra
    _BASE_PATH: Path = Path(__file__).parent.parent

    def __init__(self, path: LotusPath = LotusPath()) -> None:
        self._path = path
        self._cache: Dict[str, LotusNode] = {}
        self._module: Optional[object] = None

    def __getattr__(self, name: str) -> "LotusNode":
        """
        Auto-discover child from folder structure.

        mahamantra.genesis → discovers genesis/
        mahamantra.genesis.brahma → discovers genesis/brahma/
        """
        # Skip private
        if name.startswith("_"):
            raise AttributeError(name)

        # Check cache
        if name in self._cache:
            return self._cache[name]

        # Discover from folder structure
        child = self._discover(name)
        if child is not None:
            self._cache[name] = child
            return child

        # Try to get from loaded module
        module = self._get_module()
        if module is not None and hasattr(module, name):
            return getattr(module, name)

        # REGISTRY FALLBACK: Delegate to DeclarationRegistry (Senior Architect pattern)
        # Registry is the single source of truth for cross-codebase routing
        if self._path.depth == 2:  # mahajana-level (e.g., genesis.brahma)
            found = self._registry_resolve(name)
            if found is not None:
                return found

        raise AttributeError(f"'{name}' not found in lotus at '{self._path.folder_path or 'root'}'")

    def _registry_resolve(self, name: str) -> Optional[object]:
        """
        Resolve via DeclarationRegistry (singleton, proper separation of concerns).

        The registry handles:
        - Scanner loading (once)
        - Module path caching
        - Export caching (O(1) for repeated lookups)

        Lotus stays pure: folder discovery + registry delegation.
        """
        try:
            from vibe_core.mahamantra.protocols._declaration import DeclarationRegistry

            mahajana = self._path.segments[1]  # e.g., "brahma"
            registry = DeclarationRegistry()
            return registry.resolve_export(mahajana, name)
        except Exception:  # noqa: BLE001 - ARJUNA-PATTERN
            return None

    def _discover(self, name: str) -> Optional["LotusNode"]:
        """
        Discover child — SEED-FIRST, filesystem fallback.

        SEED O(1):
            Root  → name in QUARTER_NAMES?
            Quarter → name in GUARDIANS_BY_QUARTER[quarter]?
        FS FALLBACK:
            Only for non-Lotus modules (substrate, protocols, adapters, etc.)
        """
        _ensure_seed()
        child_path = self._path.child(name)

        # === SEED PATH (O(1), no filesystem) ===
        if self._path.is_root and name in _QUARTER_SET:
            return LotusNode(child_path)

        if self._path.depth == 1:
            quarter = self._path.segments[0]
            guardians = _GUARDIANS_BY_QUARTER.get(quarter, ())
            if name in guardians:
                return LotusNode(child_path)

        # === FS FALLBACK (non-Lotus modules: substrate, protocols, etc.) ===
        folder = self._BASE_PATH / child_path.folder_path
        if folder.exists() and folder.is_dir():
            return LotusNode(child_path)

        # Check .py file at root or current folder
        if self._path.is_root:
            py_file = self._BASE_PATH / f"{name}.py"
        else:
            current_folder = self._BASE_PATH / self._path.folder_path
            py_file = current_folder / f"{name}.py"

        if py_file.exists():
            return LotusNode(child_path)

        return None

    def _get_module(self) -> Optional[object]:
        """Lazy-load the actual Python module."""
        if self._module is not None:
            return self._module

        try:
            self._module = importlib.import_module(self._path.module_path)
            return self._module
        except ImportError:
            return None

    def __call__(self, *args: object, **kwargs: object) -> object:
        """Allow calling if the node has a __call__ method."""
        module = self._get_module()
        if module is not None and hasattr(module, "__call__"):
            return module(*args, **kwargs)  # type: ignore[operator]
        raise TypeError(f"'{self._path.folder_path}' is not callable")

    def __repr__(self) -> str:
        if self._path.is_root:
            return "mahamantra"
        return f"mahamantra.{'.'.join(self._path.segments)}"

    def __dir__(self) -> list:
        """
        List available children for tab-completion.

        SEED-FIRST: Quarters and Guardians from Seed (O(1)).
        FS FALLBACK: Non-Lotus modules (substrate, protocols, etc.).

        LILA BOUNDARY (Chaitanya's 24+24):
            Returns max 24 items per call (Navadvipa phase).
            Use _dir_full() for complete listing.
        """
        from vibe_core.mahamantra.substrate.byte import LILA_LIMIT

        NAVADVIPA_LIMIT = LILA_LIMIT // 2  # 24

        items: Set[str] = set()
        _ensure_seed()

        # === SEED items (O(1)) ===
        if self._path.is_root:
            items.update(_QUARTER_NAMES)
        elif self._path.depth == 1:
            quarter = self._path.segments[0]
            items.update(_GUARDIANS_BY_QUARTER.get(quarter, ()))

        # === FS items (non-Lotus modules) ===
        if self._path.is_root:
            base = self._BASE_PATH
        else:
            base = self._BASE_PATH / self._path.folder_path

        if base.exists():
            for child in base.iterdir():
                if child.name.startswith(("_", ".")):
                    continue
                if child.is_dir():
                    items.add(child.name)
                elif child.suffix == ".py":
                    items.add(child.stem)

        # Module exports
        module = self._get_module()
        if module is not None:
            items.update(name for name in dir(module) if not name.startswith("_"))

        # Sort first, THEN truncate
        result = sorted(items)
        if not self._path.is_root and len(result) > NAVADVIPA_LIMIT:
            result = result[:NAVADVIPA_LIMIT]
            result.append("__has_more__")

        return result

    def _dir_full(self) -> list:
        """
        Full directory listing (bypasses Lila boundary for internal use).

        SEED-FIRST for Lotus hierarchy, FS for non-Lotus modules.
        """
        items: Set[str] = set()
        _ensure_seed()

        # === SEED items (O(1)) ===
        if self._path.is_root:
            items.update(_QUARTER_NAMES)
        elif self._path.depth == 1:
            quarter = self._path.segments[0]
            items.update(_GUARDIANS_BY_QUARTER.get(quarter, ()))

        # === FS items (non-Lotus modules) ===
        if self._path.is_root:
            base = self._BASE_PATH
        else:
            base = self._BASE_PATH / self._path.folder_path

        if base.exists():
            for child in base.iterdir():
                if child.name.startswith("_"):
                    continue
                if child.is_dir():
                    items.add(child.name)
                elif child.suffix == ".py":
                    items.add(child.stem)

        module = self._get_module()
        if module is not None:
            items.update(name for name in dir(module) if not name.startswith("_"))

        return sorted(items)

    # === Resonance & Execution (Node-to-Node Lotus) ===

    def resonate(self, command: str) -> tuple[float, Optional["LotusNode"]]:
        """
        Calculate resonance for a command through the fractal tree.

        Returns: (resonance_score, winning_node)
        """
        cmd_lower = command.lower()

        # 1. Check direct module resonance (Leaf Level)
        # If this node represents a Mahajana (depth 2), check its protocol
        if self._path.depth == 2:
            try:
                guardian = self._path.segments[1]
                from vibe_core.mahamantra.substrate import ProtocolRegistry

                protocol_cls = ProtocolRegistry.get_by_guardian(guardian)
                if protocol_cls and hasattr(protocol_cls, "get_resonance"):
                    score = protocol_cls.get_resonance(cmd_lower)
                    if score > 0:
                        return score, self
            except Exception as _exc:
                logger.exception("Unexpected error: %s", _exc)

        # 2. Delegate to children (Tree Level)
        max_score = 0.0
        best_node = None

        # We only walk children if we are root or quarter level
        if self._path.depth < 2:
            # SEED-BASED ROUTING: Use Seed data for both root and quarter level.
            # Root → 4 Quarters, Quarter → its Guardians. No filesystem.
            _ensure_seed()
            if self._path.is_root:
                children = list(_QUARTER_NAMES)
            else:
                quarter = self._path.segments[0]
                children = list(_GUARDIANS_BY_QUARTER.get(quarter, ()))

            for child_name in children:
                if child_name.startswith("_") or child_name == "mod" or child_name == "shadow":
                    continue
                try:
                    child = getattr(self, child_name)
                    if isinstance(child, LotusNode):
                        score, node = child.resonate(command)
                        if score > max_score:
                            max_score = score
                            best_node = node
                            if max_score >= 1.0:
                                break
                except Exception:
                    continue

        return max_score, best_node

    def execute(self, command: str, args: Optional[list[str]] = None) -> dict:
        """
        Execute a command on this node.

        If this is the root, it performs resonance discovery first.
        If this is a leaf (Mahajana), it awakens the service and executes.
        """
        if self._path.is_root:
            score, winner = self.resonate(command)
            if winner and score > 0:
                return winner.execute(command, args)

            # Fallback to Narada if no resonance
            return getattr(self.genesis, "narada").execute(command, args)

        # Leaf Level Execution
        if self._path.depth == 2:
            guardian = self._path.segments[1]
            # Use the Singularity's Royal Hunt to awaken the service
            from vibe_core.mahamantra import mahamantra

            # We bypass the resonance check here because we ARE the winner
            return self._awaken_and_execute(guardian, command, args)

        return {"success": False, "output": f"Node {self} cannot execute directly."}

    def _awaken_and_execute(self, guardian: str, command: str, args: Optional[list[str]]) -> dict:
        """Awaken the service at this node and execute the command."""
        import importlib

        from vibe_core.mahamantra.substrate.proxy import MahamantraProxy

        # Royal Hunt logic encapsulated for the node
        service_class = None
        service_class_name = f"{guardian.capitalize()}Service"

        jungles = [
            f"vibe_core.mahamantra.{self._path.segments[0]}.{guardian}",
            f"vibe_core.protocols.mahajanas.{guardian}.service",
            f"vibe_core.naga.services.{guardian}",
            f"vibe_core.services.{guardian}",
        ]

        for jungle in jungles:
            try:
                module = importlib.import_module(jungle)
                candidate = getattr(module, service_class_name, None)
                if candidate and isinstance(candidate, type):
                    service_class = candidate
                    break
            except ImportError:
                continue

        if not service_class:
            return {"success": False, "output": f"Could not awaken {guardian} Service."}

        # Awaken
        instance = service_class()
        # Wrap
        if not hasattr(instance, "__tattva__"):
            # Get position from substrate
            from vibe_core.mahamantra.substrate import get_position_by_guardian

            pos = get_position_by_guardian(guardian)
            instance = MahamantraProxy(instance, pos.index, guardian)

        # Execute
        try:
            if hasattr(instance, "chat"):
                output = instance.chat(command)
            elif hasattr(instance, "execute"):
                output = instance.execute(command)
            else:
                output = f"🕉️ {guardian.upper()} awakened but is mute."

            return {"success": True, "output": output, "mahajana": guardian}
        except Exception as e:
            return {"success": False, "output": f"Execution Error: {e}"}

    # === Iteration ===

    def _walk(self, depth: int = 1) -> Iterator[Tuple[LotusPath, "LotusNode"]]:
        """
        Walk the lotus fractally — SEED-BASED.

        Uses Seed data for Quarters and Guardians (O(1)).
        Falls back to FS only for non-Lotus depths.
        """
        yield (self._path, self)

        if depth <= 0:
            return

        _ensure_seed()

        # SEED PATH: Root → Quarters, Quarter → Guardians
        if self._path.is_root:
            children = _QUARTER_NAMES
        elif self._path.depth == 1:
            quarter = self._path.segments[0]
            children = _GUARDIANS_BY_QUARTER.get(quarter, ())
        else:
            # Depth 2+: no Seed data, fall back to FS
            base = self._BASE_PATH / self._path.folder_path
            if not base.exists():
                return
            children = sorted(
                child.name for child in base.iterdir()
                if not child.name.startswith("_") and child.is_dir()
            )

        for child_name in children:
            child_node = LotusNode(self._path.child(child_name))
            yield from child_node._walk(depth - 1)

    # === Properties ===

    @property
    def path(self) -> LotusPath:
        return self._path

    @property
    def depth(self) -> int:
        return self._path.depth


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "LotusPath",
    "LotusNode",
]
