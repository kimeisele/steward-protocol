"""
ANANTA SHESHA - The System-Level Substrate Bridge.

"Der unendliche Schlangenkönig, auf dem Vishnu ruht."

Ananta (Zeit/Events) + Shesha (Raum/State) = Das Substrat der Realität.

This module is the BRIDGE that connects:
- Prakriti (State Substrate) ↔ Weaver (Orchestrator)
- System Ouroboros (Violations) ↔ NAGA Ouroboros (Loop Detection)

Architectural Position:
    Layer -2: Prakriti (State)
    Layer -1: AnantaShesha (THIS - Bridge)
    Layer  0: Ouroboros (System + NAGA)
    Layer  1: Services

Design Principles (PROMPT.md):
- Protocol statt konkrete Klassen (IGeneHost)
- Keine versteckten Zustände (Three Bodies)
- Selbstheilung über Absturz (Arjuna-Pattern)

Usage:
    from vibe_core.ouroboros.ananta_shesha import get_system_anchor

    # NAGA binds to system
    anchor = get_system_anchor()
    anchor.register_gene("naga_ouroboros", naga_ouroboros_instance)

    # System emits to NAGA
    anchor.emit_event("violation.detected", {"file": "x.py"})
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

# Protocol imports (Layer -1 - no circular deps)
from vibe_core.protocols.substrate import (
    GeneActivationState,
    GeneManifest,
    GeneStatus,
    IGene,
    IGeneHost,
    SubstrateHealth,
    SubstrateStatus,
)

logger = logging.getLogger("ANANTA_SHESHA")


# =============================================================================
# EVENT TYPES (Typed, not strings)
# =============================================================================


@dataclass
class SystemEvent:
    """Typed event for system-level communication."""

    event_type: str
    source: str  # "prakriti", "weaver", "ouroboros", "naga"
    data: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)


# =============================================================================
# ANANTA SHESHA - The System Substrate
# =============================================================================


class AnantaShesha(IGeneHost):
    """
    System-Level Implementation of IGeneHost.

    This is the "Staat" (federal) level substrate.
    NAGA Ouroboros is the "Bundesland" (state) level.

    Responsibilities:
    1. GENE REGISTRY: NAGAs register here to receive system events
    2. EVENT ROUTING: Bidirectional flow between layers
    3. HEALTH AGGREGATION: Combines health from all bound genes
    4. HEARTBEAT: System-level pulse (Ananta = Time)
    """

    def __init__(self) -> None:
        """Initialize the system substrate."""
        self._genes: Dict[str, IGene] = {}
        self._gene_statuses: Dict[str, GeneStatus] = {}
        self._capability_providers: Dict[str, str] = {}  # cap -> gene_name
        self._event_listeners: Dict[str, List[str]] = {}  # event_type -> gene_names
        self._event_handlers: Dict[str, List[Callable[[SystemEvent], None]]] = {}

        self._start_time = datetime.now()
        self._last_heartbeat = datetime.now()
        self._event_count = 0

        logger.info("ANANTA_SHESHA: System substrate initialized")

    # =========================================================================
    # IGeneHost Implementation
    # =========================================================================

    def get_gene(self, name: str) -> Optional[IGene]:
        """Get a registered gene by name."""
        return self._genes.get(name)

    def has_gene(self, name: str) -> bool:
        """Check if a gene is registered."""
        return name in self._genes

    def get_capability(self, capability: str) -> Optional[Any]:
        """Get capability from any gene that provides it."""
        provider_name = self._capability_providers.get(capability)
        if provider_name:
            return self._genes.get(provider_name)
        return None

    def emit_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """
        Emit event to all listeners.

        This is the SHANKHA (conch) - broadcasting to all.
        """
        self._event_count += 1
        self._last_heartbeat = datetime.now()

        event = SystemEvent(
            event_type=event_type,
            source="ananta_shesha",
            data=data,
        )

        # Notify gene listeners
        listener_names = self._event_listeners.get(event_type, [])
        for name in listener_names:
            gene = self._genes.get(name)
            if gene and hasattr(gene, "on_event"):
                try:
                    gene.on_event(event_type, data)  # type: ignore
                except Exception as e:
                    logger.warning(f"ANANTA_SHESHA: Gene {name} failed on {event_type}: {e}")

        # Notify direct handlers
        handlers = self._event_handlers.get(event_type, [])
        for handler in handlers:
            try:
                handler(event)
            except Exception as e:
                logger.warning(f"ANANTA_SHESHA: Handler failed on {event_type}: {e}")

        logger.debug(f"ANANTA_SHESHA: Emitted {event_type} to {len(listener_names)} genes")

    # =========================================================================
    # Gene Management
    # =========================================================================

    def register_gene(self, gene: IGene) -> bool:
        """Register a gene with the system substrate."""
        name = gene.manifest.name
        if name in self._genes:
            logger.warning(f"ANANTA_SHESHA: Gene {name} already registered")
            return False

        self._genes[name] = gene
        self._gene_statuses[name] = GeneStatus(
            manifest=gene.manifest,
            state=GeneActivationState.DORMANT,
        )

        # Register capabilities
        for cap in gene.manifest.capabilities:
            if cap not in self._capability_providers:
                self._capability_providers[cap] = name

        logger.info(f"ANANTA_SHESHA: Registered gene {name}")
        return True

    def register_gene_simple(self, name: str, gene: Any) -> None:
        """
        Simple registration for non-IGene objects.

        For backward compatibility with existing code.
        """
        self._genes[name] = gene  # type: ignore
        logger.info(f"ANANTA_SHESHA: Registered (simple) {name}")

    def subscribe(self, event_type: str, gene_name: str) -> None:
        """Subscribe a gene to an event type."""
        if event_type not in self._event_listeners:
            self._event_listeners[event_type] = []
        if gene_name not in self._event_listeners[event_type]:
            self._event_listeners[event_type].append(gene_name)

    def add_handler(self, event_type: str, handler: Callable[[SystemEvent], None]) -> None:
        """Add a direct event handler (for non-gene components)."""
        if event_type not in self._event_handlers:
            self._event_handlers[event_type] = []
        self._event_handlers[event_type].append(handler)

    # =========================================================================
    # Health & Status (Ananta = Time, Shesha = Space)
    # =========================================================================

    def heartbeat(self) -> Dict[str, Any]:
        """
        System heartbeat - the pulse of Ananta (Time).

        Returns current system status for health checks.
        """
        self._last_heartbeat = datetime.now()
        uptime = (self._last_heartbeat - self._start_time).total_seconds()

        return {
            "uptime_seconds": uptime,
            "genes_registered": len(self._genes),
            "capabilities_available": len(self._capability_providers),
            "events_processed": self._event_count,
            "last_heartbeat": self._last_heartbeat.isoformat(),
            "health": self._calculate_health().value,
        }

    def _calculate_health(self) -> SubstrateHealth:
        """Calculate overall system health from gene statuses."""
        if not self._genes:
            return SubstrateHealth.PRISTINE

        failed = sum(1 for s in self._gene_statuses.values() if s.error is not None)
        total = len(self._genes)

        if failed > total / 2:
            return SubstrateHealth.CRITICAL
        elif failed > 0:
            return SubstrateHealth.DEGRADED
        else:
            return SubstrateHealth.HEALTHY

    def get_status(self) -> SubstrateStatus:
        """Get full substrate status."""
        genes_active = sum(
            1 for g in self._genes.values()
            if hasattr(g, "state") and g.state == GeneActivationState.ACTIVE
        )
        genes_dormant = len(self._genes) - genes_active
        genes_failed = sum(1 for s in self._gene_statuses.values() if s.error is not None)

        return SubstrateStatus(
            health=self._calculate_health(),
            genes_total=len(self._genes),
            genes_active=genes_active,
            genes_dormant=genes_dormant,
            genes_failed=genes_failed,
            uptime_seconds=(datetime.now() - self._start_time).total_seconds(),
            last_heartbeat=self._last_heartbeat,
            message=f"events={self._event_count}, caps={len(self._capability_providers)}",
        )

    # =========================================================================
    # Bridge Methods (Connect layers)
    # =========================================================================

    def notify_violation(self, violation_data: Dict[str, Any]) -> None:
        """
        Called by System Ouroboros when violation detected.

        Routes to NAGA for potential healing.
        """
        self.emit_event("violation.detected", violation_data)

    def notify_loop_detected(self, loop_data: Dict[str, Any]) -> None:
        """
        Called by NAGA Ouroboros when correction loop detected.

        Escalates to system level for intervention.
        """
        self.emit_event("naga.loop_detected", loop_data)
        logger.warning(f"ANANTA_SHESHA: Loop detected - {loop_data}")

    def notify_commit(self, commit_data: Dict[str, Any]) -> None:
        """
        Called by Prakriti when commit occurs.

        Routes to interested parties (NAGA CommitWatcher, etc).
        """
        self.emit_event("prakriti.commit", commit_data)

    def request_healing(self, target: str, reason: str) -> None:
        """
        Request healing from NAGA Federation.

        Routes DOWN to NAGA services.
        """
        self.emit_event("healing.requested", {
            "target": target,
            "reason": reason,
            "source": "ananta_shesha",
        })


# =============================================================================
# SINGLETON (Global System Anchor)
# =============================================================================

_SYSTEM_INSTANCE: Optional[AnantaShesha] = None


def get_system_anchor() -> AnantaShesha:
    """
    Get the global system substrate instance.

    This is THE anchor point that NAGA binds to.
    Singleton pattern ensures one truth.
    """
    global _SYSTEM_INSTANCE
    if _SYSTEM_INSTANCE is None:
        _SYSTEM_INSTANCE = AnantaShesha()
    return _SYSTEM_INSTANCE


def reset_system_anchor() -> None:
    """Reset for testing. Use with caution."""
    global _SYSTEM_INSTANCE
    _SYSTEM_INSTANCE = None


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "AnantaShesha",
    "SystemEvent",
    "get_system_anchor",
    "reset_system_anchor",
]
