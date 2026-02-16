"""
TATTVA REGISTRY — The Border Control
=====================================

"yo māṁ paśyati sarvatra sarvaṁ ca mayi paśyati"
"He who sees Me everywhere, and sees everything in Me..."
— Bhagavad Gita 6.30

33 classes declare __tattva__. Until now, nobody read the content.
This registry collects, indexes, and exposes all Tattva declarations
so the kernel can introspect ANY component by its 5-fold truth.

ARCHITECTURE:
- Register: component declares __tattva__ → registry stores it
- Query: kernel asks "who has STORAGE capability?" → registry answers
- Introspect: any component can read any other component's truth

This is the CONSUMER that was missing.
Passport without border control → border control installed.
"""

from __future__ import annotations

__mahajana__ = "bhishma"
__position__ = 11
__genesis__ = "0x030295b1"

import logging
import threading
import warnings
from typing import Dict, Iterator, List, Optional, Tuple

from vibe_core.mahamantra.protocols._pancha import TattvaDict
from vibe_core.mahamantra.substrate.pancha_tattva import TattvaGate

logger = logging.getLogger("TATTVA_REGISTRY")


class TattvaRegistry:
    """
    Collects and indexes __tattva__ declarations.

    Thread-safe singleton. Components register on load,
    kernel queries at runtime.

    Usage:
        >>> registry = get_registry()
        >>> registry.register("venu_orchestrator", orchestrator)
        >>> registry.query("nityananda", "Clock")
        [("venu_service", {...})]
    """

    _instance: Optional["TattvaRegistry"] = None
    _lock = threading.Lock()

    def __init__(self) -> None:
        self._entries: Dict[str, TattvaDict] = {}
        self._objects: Dict[str, object] = {}
        self._gate_providers: Dict[TattvaGate, List[Tuple[str, object]]] = {}
        self._violations: List[Tuple[str, str]] = []  # (name, reason)

    @classmethod
    def instance(cls) -> "TattvaRegistry":
        """Get or create the singleton registry."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    @classmethod
    def reset(cls) -> None:
        """Reset the singleton (for testing only)."""
        with cls._lock:
            cls._instance = None

    # =========================================================================
    # REGISTER — Components declare their truth
    # =========================================================================

    def register(self, name: str, obj: object) -> bool:
        """
        DEPRECATED: Self-declared __tattva__ (5 strings) is Ahankara.
        Use register_gate_provider() with Capability Protocols instead.
        """
        warnings.warn(
            f"TattvaRegistry.register('{name}'): __tattva__ registration is deprecated. "
            "Use register_gate_provider() with Capability Protocols.",
            DeprecationWarning,
            stacklevel=2,
        )
        tattva = getattr(obj, "__tattva__", None)
        if tattva is None:
            return False

        if not isinstance(tattva, dict):
            return False

        self._entries[name] = tattva
        self._objects[name] = obj
        return True

    def unregister(self, name: str) -> bool:
        """Remove a component from the registry."""
        if name in self._entries:
            del self._entries[name]
            del self._objects[name]
            return True
        return False

    # =========================================================================
    # QUERY — Kernel reads the passports
    # =========================================================================

    def get(self, name: str) -> Optional[TattvaDict]:
        """Get a specific component's tattva by name."""
        return self._entries.get(name)

    def get_object(self, name: str) -> Optional[object]:
        """Get the registered object by name."""
        return self._objects.get(name)

    def query(self, key: str, pattern: str) -> List[Tuple[str, TattvaDict]]:
        """DEPRECATED: String-matching on self-declared __tattva__ is not real capability discovery."""
        warnings.warn(
            "TattvaRegistry.query() is deprecated. Use get_gate_providers() for capability-based lookup.",
            DeprecationWarning,
            stacklevel=2,
        )
        pattern_lower = pattern.lower()
        results = []
        for name, tattva in self._entries.items():
            value = tattva.get(key, "")
            if pattern_lower in value.lower():
                results.append((name, tattva))
        return results

    def by_capability(self, capability: str) -> List[Tuple[str, TattvaDict]]:
        """DEPRECATED: String-matching on self-declared __tattva__ is not real capability discovery."""
        warnings.warn(
            "TattvaRegistry.by_capability() is deprecated. Use get_gate_providers() for real capability checks.",
            DeprecationWarning,
            stacklevel=2,
        )
        cap_lower = capability.lower()
        results = []
        for name, tattva in self._entries.items():
            for value in tattva.values():
                if cap_lower in str(value).lower():
                    results.append((name, tattva))
                    break
        return results

    # =========================================================================
    # GATE PROVIDERS — Components claim responsibility for gates
    # =========================================================================

    def register_gate_provider(self, name: str, obj: object, gate: TattvaGate) -> bool:
        """
        Register an object as a provider for a specific TattvaGate.

        The object MUST satisfy the capability protocol for that gate.
        Non-compliant objects are rejected and logged as violations.

        Args:
            name: Provider identifier
            obj: The provider object
            gate: Which gate this provider serves

        Returns:
            True if accepted, False if capability check failed
        """
        from vibe_core.mahamantra.protocols._capabilities import check_capability, get_capability_for_gate

        if not check_capability(obj, gate):
            cap = get_capability_for_gate(gate)
            reason = f"{name} lacks {cap.__name__} for gate {gate.name}"
            self._violations.append((name, reason))
            logger.warning("Gate provider REJECTED: %s", reason)
            return False

        if gate not in self._gate_providers:
            self._gate_providers[gate] = []
        self._gate_providers[gate].append((name, obj))
        logger.debug("Gate provider registered: %s → %s", name, gate.name)
        return True

    def get_gate_providers(self, gate: TattvaGate) -> List[Tuple[str, object]]:
        """Get all registered providers for a gate."""
        return list(self._gate_providers.get(gate, []))

    def gate_provider_count(self, gate: Optional[TattvaGate] = None) -> int:
        """Count providers. If gate is None, count all."""
        if gate is not None:
            return len(self._gate_providers.get(gate, []))
        return sum(len(v) for v in self._gate_providers.values())

    @property
    def violations(self) -> List[Tuple[str, str]]:
        """All capability violations (rejected registrations)."""
        return list(self._violations)

    # =========================================================================
    # INTROSPECTION — The system describes itself
    # =========================================================================

    @property
    def count(self) -> int:
        """Number of registered components."""
        return len(self._entries)

    @property
    def names(self) -> Tuple[str, ...]:
        """All registered component names."""
        return tuple(self._entries.keys())

    def __iter__(self) -> Iterator[Tuple[str, TattvaDict]]:
        """Iterate over all (name, tattva) pairs."""
        yield from self._entries.items()

    def __contains__(self, name: str) -> bool:
        return name in self._entries

    def __len__(self) -> int:
        return len(self._entries)

    def __repr__(self) -> str:
        return f"TattvaRegistry({self.count} components)"

    @property
    def __tattva__(self) -> TattvaDict:
        """The registry describes itself."""
        providers = self.gate_provider_count()
        viols = len(self._violations)
        return {
            "chaitanya": f"TattvaRegistry — Border Control ({self.count} passports, {providers} gate providers)",
            "nityananda": "Dict[str, TattvaDict] + Dict[str, object] + Dict[TattvaGate, providers] (in-memory, thread-safe)",
            "advaita": "register(name, obj) → register_gate_provider(name, obj, gate) → query(key, pattern)",
            "gadadhara": f"Registered: {', '.join(self.names[:5])}{'...' if self.count > 5 else ''}, violations: {viols}",
            "srivasa": "Singleton via get_registry(), reset() for testing. Capability-checked gate providers.",
        }


def get_registry() -> TattvaRegistry:
    """Get the global TattvaRegistry singleton."""
    return TattvaRegistry.instance()
