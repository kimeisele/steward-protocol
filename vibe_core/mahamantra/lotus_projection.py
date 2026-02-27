"""
LOTUS PROJECTION - Boot-Time Auto-Wiring
=========================================

"yathā padmānuraktaṁ hi toyaṁ bhāti suśobhanam"

"Like water beautified by lotus attachment."
— Padma Purana

THE MISSING PIECE:
    Discovery (LotusNode) + Wiring (auto_wire) = Projection

FOLDER = EXISTENCE = WIRED = GRAVITY.

This module bridges:
    1. LotusNode._walk() → discovers all mahajanas from folder structure
    2. module.__position__ → gets holographic address (0-15)
    3. _instantiate_guardian() → creates live instance
    4. auto_wire(kernel, instance) → injects kernel reference
    5. PositionRegistry → stores by position for gravity routing

USAGE:
    # In kernel_impl.py bootstrap():
    from vibe_core.mahamantra.lotus_projection import project_lotus

    self._positions = project_lotus(self)

    # Now gravity routing works:
    self._positions[5]  # → KumarasService instance (position 5)
    self._positions.by_guardian("kapila")  # → KapilaService instance
"""

from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "narada"  # Messenger who connects everything
__position__ = 2
__genesis__ = "0x3e2fa1fe"

import importlib
import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Dict, Iterator, Optional, Tuple

if TYPE_CHECKING:
    from vibe_core.kernel_impl import RealVibeKernel


logger = logging.getLogger("LOTUS_PROJECTION")


# =============================================================================
# POSITION REGISTRY - The Gravity Router
# =============================================================================


@dataclass
class PositionRegistry:
    """
    Registry of live instances indexed by position (0-15).

    GRAVITY ROUTING:
        registry[position] → instance
        registry.by_guardian(name) → instance
        registry.all_active() → list of (position, guardian, instance)

    This is the BRIDGE between:
        - LotusNode (discovery by folder)
        - Kernel (needs wired instances)
    """

    _instances: Dict[int, object] = field(default_factory=dict)
    _guardians: Dict[str, int] = field(default_factory=dict)  # name → position

    def __getitem__(self, position: int) -> object:
        """Get instance by position (gravity lookup)."""
        if position not in self._instances:
            raise KeyError(f"Position {position} not projected")
        return self._instances[position]

    def __contains__(self, position: int) -> bool:
        return position in self._instances

    def __len__(self) -> int:
        return len(self._instances)

    def __iter__(self) -> Iterator[int]:
        return iter(sorted(self._instances.keys()))

    def get(self, position: int, default: object = None) -> object:
        """Safe get by position."""
        return self._instances.get(position, default)

    def by_guardian(self, name: str) -> Optional[object]:
        """Get instance by guardian name."""
        position = self._guardians.get(name.lower())
        if position is None:
            return None
        return self._instances.get(position)

    def register(self, position: int, guardian: str, instance: object) -> None:
        """Register an instance at position."""
        self._instances[position] = instance
        self._guardians[guardian.lower()] = position
        logger.debug(f"🪷 Projected {guardian} at position {position}")

    def all_active(self) -> list[Tuple[int, str, object]]:
        """Return all active projections as (position, guardian, instance)."""
        result = []
        for guardian, position in self._guardians.items():
            instance = self._instances.get(position)
            if instance is not None:
                result.append((position, guardian, instance))
        return sorted(result, key=lambda x: x[0])

    def summary(self) -> str:
        """Human-readable summary."""
        lines = ["Position Registry:"]
        for pos, guardian, inst in self.all_active():
            cls_name = inst.__class__.__name__
            lines.append(f"  [{pos:2d}] {guardian:12s} → {cls_name}")
        return "\n".join(lines)


# =============================================================================
# GUARDIAN INSTANTIATION - Service Factory
# =============================================================================


def _instantiate_guardian(guardian: str, quarter: str) -> Optional[object]:
    """
    Instantiate a guardian service.

    Searches known locations (jungles) for the service class.
    Returns None if not found or instantiation fails.

    JUNGLES (search order):
        1. vibe_core.mahamantra.{quarter}.{guardian}
        2. vibe_core.protocols.mahajanas.{guardian}.service
        3. vibe_core.services.{guardian}

    Note: We intentionally skip vibe_core.naga (50k LOC bloat).
    """
    service_class_name = f"{guardian.capitalize()}Service"

    jungles = [
        f"vibe_core.mahamantra.{quarter}.{guardian}",
        f"vibe_core.protocols.mahajanas.{guardian}.service",
        f"vibe_core.services.{guardian}",
    ]

    for jungle in jungles:
        try:
            module = importlib.import_module(jungle)
            candidate = getattr(module, service_class_name, None)
            if candidate is not None and isinstance(candidate, type):
                # Found the class, instantiate it
                try:
                    return candidate()
                except Exception as e:
                    logger.warning(f"🪷 Failed to instantiate {service_class_name}: {e}")
                    return None
        except ImportError:
            continue

    # No service class found - that's OK, not all guardians have services
    return None


def _get_module_metadata(module: object) -> Tuple[Optional[int], Optional[str]]:
    """
    Extract __position__ and __mahajana__ from a module.

    Returns (position, mahajana) or (None, None) if not declared.
    """
    position = getattr(module, "__position__", None)
    mahajana = getattr(module, "__mahajana__", None)
    return position, mahajana


# =============================================================================
# LOTUS PROJECTION - The Main Function
# =============================================================================


def project_lotus(kernel: "RealVibeKernel") -> PositionRegistry:
    """
    Project the Lotus at boot time.

    FOLDER = EXISTENCE = WIRED = GRAVITY.

    SEED-BASED: Iterates ALL_GUARDIANS directly (O(1) lookup).
    No LotusNode, no filesystem, no _walk().
    Module loading via importlib (cached by Python).

    Called from kernel.bootstrap() - ONE LINE integration:
        self._positions = project_lotus(self)

    Args:
        kernel: The RealVibeKernel to wire instances to

    Returns:
        PositionRegistry with all discovered+instantiated+wired guardians
    """
    from vibe_core.mahamantra.substrate.seed import (
        ALL_GUARDIANS,
        QUARTER_NAMES,
        WORDS_PER_QUARTER,
    )
    from vibe_core.vajra.auto_wire import auto_wire

    registry = PositionRegistry()
    projected_count = 0
    wired_count = 0

    for position, guardian in enumerate(ALL_GUARDIANS):
        quarter_name = QUARTER_NAMES[position // WORDS_PER_QUARTER]

        # Try to load the module for metadata verification
        module_path = f"vibe_core.mahamantra.{quarter_name}.{guardian}"
        try:
            module = importlib.import_module(module_path)
        except ImportError:
            logger.debug(f"🪷 No module for {guardian} at {module_path}")
            continue

        declared_position, declared_mahajana = _get_module_metadata(module)

        # Use declared position if available, otherwise use Seed position
        effective_position = declared_position if declared_position is not None else position

        # Check if already projected (avoid duplicates)
        if effective_position in registry:
            continue

        # Use declared mahajana name if available, otherwise use Seed name
        effective_guardian = declared_mahajana or guardian

        # Instantiate the service
        instance = _instantiate_guardian(effective_guardian, quarter_name)

        if instance is None:
            # No service, but we can still register the module itself
            # This allows position-based access to the module's exports
            registry.register(effective_position, effective_guardian, module)
            projected_count += 1
            continue

        # Wire to kernel
        if auto_wire(kernel, instance):
            wired_count += 1

        # Register in position registry
        registry.register(effective_position, effective_guardian, instance)
        projected_count += 1

    logger.info(f"🪷 LOTUS PROJECTION complete: {projected_count} projected, {wired_count} wired to kernel")

    return registry


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================


def project_minimal(kernel: "RealVibeKernel") -> PositionRegistry:
    """
    Minimal projection - only HEAD guardians (one per quarter).

    For fast boot when full lotus not needed.
    HEAD positions derived from SSOT: HEAD_POSITIONS = (0, 4, 8, 12).
    """
    from vibe_core.mahamantra.protocols._seed import HEAD_POSITIONS
    from vibe_core.mahamantra.substrate.seed import (
        ALL_GUARDIANS,
        get_quarter_name,
    )
    from vibe_core.vajra.auto_wire import auto_wire

    registry = PositionRegistry()

    for position in HEAD_POSITIONS:
        guardian = ALL_GUARDIANS[position]
        quarter = get_quarter_name(position)
        instance = _instantiate_guardian(guardian, quarter)
        if instance is not None:
            auto_wire(kernel, instance)
            registry.register(position, guardian, instance)

    return registry


def verify_projection(registry: PositionRegistry) -> Dict[str, Any]:
    """
    Verify the projection is complete and healthy.

    Returns verification report.
    """
    from vibe_core.mahamantra.substrate.seed import ALL_GUARDIANS

    expected_guardians = set(g.lower() for g in ALL_GUARDIANS)
    projected_guardians = set(registry._guardians.keys())

    missing = expected_guardians - projected_guardians
    extra = projected_guardians - expected_guardians

    return {
        "total_projected": len(registry),
        "expected": len(expected_guardians),
        "missing": sorted(missing),
        "extra": sorted(extra),
        "coverage": len(projected_guardians & expected_guardians) / len(expected_guardians),
        "is_complete": len(missing) == 0,
    }


# =============================================================================
# SINGLETON ACCESS
# =============================================================================

_positions_singleton: Optional[PositionRegistry] = None


def get_positions() -> PositionRegistry:
    """
    Get the singleton PositionRegistry.

    USAGE:
        from vibe_core.mahamantra import positions

        positions[0]  # → VyasaService
        positions.by_guardian("kapila")  # → KapilaService

    First access triggers projection (lazy).
    Subsequent accesses return cached registry.

    Note: Uses a NullKernel since no kernel wiring needed for discovery.
    """
    global _positions_singleton

    if _positions_singleton is None:
        # NullKernel - we only need discovery, not wiring
        class NullKernel:
            pass

        _positions_singleton = project_lotus(NullKernel())

    return _positions_singleton


def reset_positions() -> None:
    """Reset the singleton (for testing)."""
    global _positions_singleton
    _positions_singleton = None


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "PositionRegistry",
    "project_lotus",
    "project_minimal",
    "verify_projection",
    "get_positions",
    "reset_positions",
]
