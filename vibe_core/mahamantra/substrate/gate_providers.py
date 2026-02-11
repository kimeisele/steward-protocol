"""
GATE PROVIDERS — The 5 Watchers at the TattvaGates
====================================================

"pañca-tattvātmakaṁ kṛṣṇaṁ bhakta-rūpa-svarūpakam"

Each TattvaGate in lotus_core.__call__() now has a REAL provider.
Providers are Observer-Adapters: they receive the pipeline context,
perform validation/tracking/logging, but do NOT alter the flow.

GATE 0 — CHAITANYA (PARSE)    → MantraGateProvider    (input validation + seed tracking)
GATE 1 — NITYANANDA (VALIDATE) → StorageGateProvider   (substrate verification)
GATE 2 — ADVAITA (EXECUTE)     → InferGateProvider     (resonance tracking)
GATE 3 — GADADHARA (RESULT)    → SyncGateProvider      (routing verification)
GATE 4 — SRIVASA (SYNC)        → EnforceGateProvider   (governance enforcement via StateService)

Registration:
    wire_gate_providers()  — called once at boot, registers all 5 in TattvaRegistry.
"""

from __future__ import annotations

__mahajana__ = "vyasa"
__position__ = 0
__genesis__ = "0x3f7a1b2e"

import logging
from typing import Any, Dict, Optional

logger = logging.getLogger("MAHAMANTRA.GATES")


# =============================================================================
# GATE 0: CHAITANYA — MantraGateProvider (PARSE / Identity)
# =============================================================================
# Observer at the entry gate. Validates input shape, tracks seed generation.

class MantraGateProvider:
    """Watcher at PARSE gate — validates and tracks incoming input."""

    __slots__ = ("_parse_count", "_last_input_type")

    def __init__(self) -> None:
        self._parse_count: int = 0
        self._last_input_type: Optional[str] = None

    def parse(self, input_data: Any) -> Dict[str, Any]:
        """
        Observe the PARSE gate.

        Validates input is not None, tracks input type and count.
        Returns observation metadata (not used by pipeline — observer only).
        """
        self._parse_count += 1
        self._last_input_type = type(input_data).__name__

        if input_data is None:
            logger.warning("PARSE gate: received None input")
            return {"valid": False, "reason": "null_input"}

        logger.debug(
            "PARSE gate: input #%d type=%s",
            self._parse_count, self._last_input_type,
        )
        return {
            "valid": True,
            "input_type": self._last_input_type,
            "parse_count": self._parse_count,
        }

    @property
    def stats(self) -> Dict[str, Any]:
        return {
            "parse_count": self._parse_count,
            "last_input_type": self._last_input_type,
        }


# =============================================================================
# GATE 1: NITYANANDA — StorageGateProvider (VALIDATE / Substrate)
# =============================================================================
# Observer at the validation gate. Verifies seed is within valid range.

class StorageGateProvider:
    """Watcher at VALIDATE gate — verifies seed integrity."""

    __slots__ = ("_validate_count", "_rejection_count")

    def __init__(self) -> None:
        self._validate_count: int = 0
        self._rejection_count: int = 0

    def validate(self, seed: int) -> Dict[str, Any]:
        """
        Observe the VALIDATE gate.

        Checks seed is a valid integer within expected range.
        """
        self._validate_count += 1

        if not isinstance(seed, int):
            self._rejection_count += 1
            logger.warning("VALIDATE gate: seed is %s, not int", type(seed).__name__)
            return {"valid": False, "reason": "non_integer_seed"}

        if seed < 0:
            self._rejection_count += 1
            logger.warning("VALIDATE gate: negative seed %d", seed)
            return {"valid": False, "reason": "negative_seed"}

        logger.debug("VALIDATE gate: seed=%d (#%d)", seed, self._validate_count)
        return {
            "valid": True,
            "seed": seed,
            "validate_count": self._validate_count,
        }

    @property
    def stats(self) -> Dict[str, Any]:
        return {
            "validate_count": self._validate_count,
            "rejection_count": self._rejection_count,
        }


# =============================================================================
# GATE 2: ADVAITA — InferGateProvider (EXECUTE / Bridge)
# =============================================================================
# Observer at the execution gate. Tracks attractor distribution.

class InferGateProvider:
    """Watcher at EXECUTE gate — tracks inference patterns."""

    __slots__ = ("_infer_count", "_attractor_seen")

    def __init__(self) -> None:
        self._infer_count: int = 0
        self._attractor_seen: Dict[int, int] = {}

    def infer(self, seed: int, attractor: int) -> Dict[str, Any]:
        """
        Observe the EXECUTE gate.

        Tracks which attractors are being hit and how often.
        """
        self._infer_count += 1
        self._attractor_seen[attractor] = self._attractor_seen.get(attractor, 0) + 1

        logger.debug(
            "EXECUTE gate: seed=%d attractor=%d (seen %dx)",
            seed, attractor, self._attractor_seen[attractor],
        )
        return {
            "seed": seed,
            "attractor": attractor,
            "attractor_frequency": self._attractor_seen[attractor],
            "unique_attractors": len(self._attractor_seen),
        }

    @property
    def stats(self) -> Dict[str, Any]:
        return {
            "infer_count": self._infer_count,
            "unique_attractors": len(self._attractor_seen),
            "top_attractors": sorted(
                self._attractor_seen.items(), key=lambda x: x[1], reverse=True
            )[:5],
        }


# =============================================================================
# GATE 3: GADADHARA — SyncGateProvider (RESULT / Energy)
# =============================================================================
# Observer at the result gate. Tracks position distribution across the 16 words.

class SyncGateProvider:
    """Watcher at RESULT gate — tracks routing and energy flow."""

    __slots__ = ("_route_count", "_position_hits")

    def __init__(self) -> None:
        self._route_count: int = 0
        self._position_hits: Dict[int, int] = {}

    def route(self, attractor: int) -> Dict[str, Any]:
        """
        Observe the RESULT gate.

        Tracks which positions are being routed to.
        Position = attractor % 16 (same as lotus_core.__call__).
        """
        self._route_count += 1
        position = attractor % 16
        self._position_hits[position] = self._position_hits.get(position, 0) + 1

        logger.debug(
            "RESULT gate: attractor=%d → position=%d (hit %dx)",
            attractor, position, self._position_hits[position],
        )
        return {
            "attractor": attractor,
            "position": position,
            "position_frequency": self._position_hits[position],
        }

    @property
    def stats(self) -> Dict[str, Any]:
        return {
            "route_count": self._route_count,
            "position_distribution": dict(sorted(self._position_hits.items())),
        }


# =============================================================================
# GATE 4: SRIVASA — EnforceGateProvider (SYNC / Governance)
# =============================================================================
# Observer at the governance gate. Enforces state tracking via StateService.
# This is the CRITICAL gate — where governance meets computation.

class EnforceGateProvider:
    """Watcher at SYNC gate — enforces governance and tracks state commits."""

    __slots__ = ("_enforce_count", "_state_service", "_last_position", "_last_seed")

    def __init__(self) -> None:
        self._enforce_count: int = 0
        self._state_service = None  # Lazy — resolved on first enforce()
        self._last_position: Optional[int] = None
        self._last_seed: Optional[int] = None

    def _get_state_service(self):
        """Lazy-resolve StateService from DI registry."""
        if self._state_service is None:
            try:
                from vibe_core.di import ServiceRegistry
                from vibe_core.protocols import StateServiceProtocol
                self._state_service = ServiceRegistry.get(StateServiceProtocol)
            except Exception:
                pass  # No StateService available — degrade gracefully
        return self._state_service

    def enforce(self, position: int, seed: int, attractor: int) -> Dict[str, Any]:
        """
        Observe the SYNC gate.

        Tracks governance events. If StateService is available,
        marks the gate passage as a state event for audit trail.
        """
        self._enforce_count += 1
        self._last_position = position
        self._last_seed = seed

        # Try to record gate passage in StateService
        state_svc = self._get_state_service()
        committed = False
        if state_svc is not None:
            try:
                state_svc.mark_dirty(
                    state_svc.state_root / "gate_audit.json"
                )
                committed = True
            except Exception as exc:
                logger.debug("SYNC gate: StateService mark_dirty failed: %s", exc)

        logger.debug(
            "SYNC gate: position=%d seed=%d attractor=%d committed=%s (#%d)",
            position, seed, attractor, committed, self._enforce_count,
        )
        return {
            "position": position,
            "seed": seed,
            "attractor": attractor,
            "committed": committed,
            "enforce_count": self._enforce_count,
        }

    @property
    def stats(self) -> Dict[str, Any]:
        return {
            "enforce_count": self._enforce_count,
            "last_position": self._last_position,
            "last_seed": self._last_seed,
            "state_service_available": self._get_state_service() is not None,
        }


# =============================================================================
# WIRING — Register all 5 providers at boot
# =============================================================================

# Singleton instances (one per process, like VenuOrchestrator)
_PROVIDERS: Optional[Dict[str, object]] = None


def get_providers() -> Dict[str, object]:
    """Get or create the singleton gate provider instances."""
    global _PROVIDERS
    if _PROVIDERS is None:
        _PROVIDERS = {
            "mantra_gate": MantraGateProvider(),
            "storage_gate": StorageGateProvider(),
            "infer_gate": InferGateProvider(),
            "sync_gate": SyncGateProvider(),
            "enforce_gate": EnforceGateProvider(),
        }
    return _PROVIDERS


def wire_gate_providers() -> int:
    """
    Register all 5 gate providers in TattvaRegistry.

    Called once at boot. Returns number of successfully registered providers.
    Safe to call multiple times (idempotent — checks existing registrations).
    """
    from vibe_core.mahamantra.substrate.pancha_tattva import TattvaGate
    from vibe_core.mahamantra.substrate.tattva_registry import get_registry

    registry = get_registry()
    providers = get_providers()

    gate_map = {
        "mantra_gate": TattvaGate.PARSE,
        "storage_gate": TattvaGate.VALIDATE,
        "infer_gate": TattvaGate.EXECUTE,
        "sync_gate": TattvaGate.RESULT,
        "enforce_gate": TattvaGate.SYNC,
    }

    registered = 0
    for name, gate in gate_map.items():
        # Skip if already registered
        if registry.gate_provider_count(gate) > 0:
            existing = registry.get_gate_providers(gate)
            if any(n == name for n, _ in existing):
                continue

        obj = providers[name]
        if registry.register_gate_provider(name, obj, gate):
            registered += 1
            logger.info("Gate provider wired: %s → %s", name, gate.name)
        else:
            logger.error("Gate provider FAILED: %s → %s", name, gate.name)

    if registered:
        logger.info("🚪 %d gate providers wired (5 gates armed)", registered)

    return registered


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "MantraGateProvider",
    "StorageGateProvider",
    "InferGateProvider",
    "SyncGateProvider",
    "EnforceGateProvider",
    "get_providers",
    "wire_gate_providers",
]
