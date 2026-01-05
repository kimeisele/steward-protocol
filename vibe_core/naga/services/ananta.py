"""
ANANTA SERVICE - The Gene Splicer + Loader Governor (12th Lord).

Ananta - The Infinite One, cosmic form of Sesha who holds all worlds.
Also: "The Infinite Remainder" - what survives when everything crashes.

From mythology: Ananta Shesha is the infinite serpent upon whom
Vishnu rests. He holds the entire universe on his thousand hoods.
When the universe is destroyed, Shesha remains - the substrate.

Responsibilities:
- Analyze services for NAGA needs (Detection Criteria)
- Propose flooding with appropriate Mixins
- Request Prahlad's approval (Check and Balance)
- Create flooded classes via DNA injection (Soft Flood)
- **NEW: Loading Governance** - Wraps VEDA-4 loaders for audit
- **NEW: Boot Audit Trail** - Records every manifest/module load

This is the OUROBOROS made explicit:
    ManifestRegistry.scan_all() -> Ananta records -> Chitragupta persists
    UnifiedLoader.discover_and_load() -> Ananta records -> Ledger audit

Integration:
- Works with Narada (discovery) → Ananta (proposal) → Prahlad (veto)
- Uses Mixin pattern, NOT Proxy pattern (preserves isinstance)
- Wraps ManifestRegistry and UnifiedLoader for governance
"""

import ast
import inspect
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Set, Type, TypeVar

if TYPE_CHECKING:
    from vibe_core.ledger import SQLiteLedger

T = TypeVar("T")

from vibe_core.naga.kulika import (
    NagaCapability,
    NagaLord,
    naga_service,
)
from vibe_core.naga.services.base import NagaBaseService, naga_governed
from vibe_core.protocols.naga import (
    AnantaProtocol,
    FloodProposal,
    NagaStatus,
    NagaType,
    ServiceClassification,
    VetoDecision,
)

logger = logging.getLogger("ANANTA")


# =============================================================================
# Detection Patterns (from NAGA.md)
# =============================================================================

SERVICE_INDICATORS = {"Service", "Manager", "Handler", "Controller", "Provider"}
STATE_PATTERNS = {"save", "write", "store", "persist", "update", "delete", "create"}
AUTH_PATTERNS = {"auth", "permission", "validate", "verify", "token", "credential"}
NETWORK_PATTERNS = {"http", "request", "fetch", "send", "post", "get", "api", "url"}
RETRY_PATTERNS = {"retry", "fallback", "recover", "heal", "resilient"}
METRIC_PATTERNS = {"log", "metric", "trace", "profile", "measure", "record"}


# =============================================================================
# Loading Governance (OUROBOROS on Loaders)
# =============================================================================


@dataclass
class LoadEvent:
    """A recorded loading operation for audit trail."""

    event_id: str
    loader_type: str  # "manifest_registry", "unified_loader", etc.
    operation: str  # "scan", "discover", "load", "instantiate"
    item_type: str  # "plugin", "cartridge", "section", etc.
    item_id: Optional[str] = None
    success: bool = True
    error: Optional[str] = None
    duration_ms: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)


@naga_service(
    name="Ananta",
    lord=NagaLord.ANANTA,
    drift_source=None,  # Governance, no drift handling
    priority=85,
    capabilities=[NagaCapability.FLOOD],
    protocol_class="vibe_core.protocols.naga.AnantaProtocol",
)
class AnantaService(NagaBaseService, AnantaProtocol):
    """
    Ananta - The Gene Splicer.

    Creates flooded classes via Mixin inheritance (Soft Flood).
    NOT via Proxy wrapping (Hard Flood).

    Soft Flood preserves:
    - isinstance checks
    - pickle compatibility
    - internal state access

    OUROBOROS: Inherits NagaBaseService for self-monitoring.
    """

    def __init__(self, ledger: Optional["SQLiteLedger"] = None) -> None:
        """Initialize Ananta."""
        super().__init__(service_name="Ananta")

        self._ledger = ledger
        self._flood_history: List[VetoDecision] = []
        self._available_mixins: Dict[str, Type] = {}
        self._last_heartbeat = datetime.now()

        # Loading Governance (OUROBOROS on Loaders)
        self._load_events: List[LoadEvent] = []
        self._load_by_loader: Dict[str, List[LoadEvent]] = {}
        self._load_by_item: Dict[str, List[LoadEvent]] = {}
        self._total_loads = 0
        self._failed_loads = 0
        self._total_duration_ms = 0.0
        self._max_events = 10000  # LRU limit

        # Wrapper state
        self._original_scan_all: Optional[Callable] = None
        self._wrapped = False

        # Register available Mixins (will be expanded)
        self._register_mixins()

        logger.info("ANANTA initialized - Gene Splicer + Loader Governor ready")

    def _register_mixins(self) -> None:
        """Register available NAGA Mixins."""
        # TODO: Import actual Mixin classes when created
        # For now, we track names only
        self._mixin_names = {
            "sesha": "SeshaMixin",
            "vasuki": "VasukiMixin",
            "takshaka": "TakshakaMixin",
            "kaliya": "KaliyaMixin",
            "karkotaka": "KarkotakaMixin",
            "kulika": "KulikaMixin",
            "padma": "PadmaMixin",
            "shankha": "ShankhaMixin",
            "narada": "NaradaMixin",
            "chitragupta": "ChitraguptaMixin",
            "prahlad": "PrahladMixin",
        }

    # =========================================================================
    # Service Analysis
    # =========================================================================

    @naga_governed(operation="analyze_service")
    def analyze_service(self, service_class: Type) -> FloodProposal:
        """Analyze a service and propose which NAGAs it needs."""
        self._last_heartbeat = datetime.now()

        name = service_class.__name__
        try:
            path = inspect.getfile(service_class)
        except (OSError, TypeError):
            path = ""

        # Check if already flooded
        if hasattr(service_class, "_naga_manifest"):
            return FloodProposal(
                service_name=name,
                service_path=path,
                classification=ServiceClassification.FLOODED,
                proposed_nagas=[],
                proposed_mixins=[],
                reason="Already has @naga_service decorator",
                overhead_estimate="none",
                risk_level="none",
            )

        # Analyze class structure
        is_service_like = self._is_service_like(service_class)
        needed_nagas = self._detect_needed_nagas(service_class)

        if not is_service_like and not needed_nagas:
            return FloodProposal(
                service_name=name,
                service_path=path,
                classification=ServiceClassification.CIVILIAN,
                proposed_nagas=[],
                proposed_mixins=[],
                reason="Pure utility class - no NAGA integration needed",
                overhead_estimate="high",
                risk_level="low",
            )

        # It's a REBEL - needs flooding
        proposed_mixins = [self._mixin_names[n] for n in needed_nagas if n in self._mixin_names]

        return FloodProposal(
            service_name=name,
            service_path=path,
            classification=ServiceClassification.REBEL,
            proposed_nagas=needed_nagas,
            proposed_mixins=proposed_mixins,
            reason=f"Service-like class needs NAGA integration: {', '.join(needed_nagas)}",
            overhead_estimate=self._estimate_overhead(len(needed_nagas)),
            risk_level=self._estimate_risk(needed_nagas),
        )

    def _is_service_like(self, cls: Type) -> bool:
        """Check if class is service-like based on naming."""
        name = cls.__name__
        return any(indicator in name for indicator in SERVICE_INDICATORS)

    def _detect_needed_nagas(self, cls: Type) -> List[str]:
        """Detect which NAGAs a class needs based on its code."""
        needed: Set[str] = set()

        # Get source code if available
        try:
            source = inspect.getsource(cls)
            source_lower = source.lower()
        except (OSError, TypeError):
            source_lower = ""

        # Check method names and signatures
        for method_name in dir(cls):
            if method_name.startswith("_"):
                continue

            method_lower = method_name.lower()

            # State mutation → Sesha
            if any(p in method_lower for p in STATE_PATTERNS):
                needed.add("sesha")

            # Auth/Security → Takshaka
            if any(p in method_lower for p in AUTH_PATTERNS):
                needed.add("takshaka")

            # Network calls → Vasuki
            if any(p in method_lower for p in NETWORK_PATTERNS):
                needed.add("vasuki")

            # Retry/Resilience → Prahlad/Kaliya
            if any(p in method_lower for p in RETRY_PATTERNS):
                needed.add("prahlad")
                needed.add("kaliya")

            # Metrics/Logging → Chitragupta
            if any(p in method_lower for p in METRIC_PATTERNS):
                needed.add("chitragupta")

        # Check source code for patterns
        if source_lower:
            if "open(" in source_lower or "write(" in source_lower:
                needed.add("sesha")
            if "request" in source_lower or "http" in source_lower:
                needed.add("vasuki")
            if "password" in source_lower or "secret" in source_lower:
                needed.add("karkotaka")

        # If it's service-like, at minimum add observation
        if self._is_service_like(cls) and not needed:
            needed.add("narada")
            needed.add("chitragupta")

        return sorted(needed)

    def _estimate_overhead(self, naga_count: int) -> str:
        """Estimate overhead based on NAGA count."""
        if naga_count == 0:
            return "none"
        if naga_count <= 2:
            return "low"
        if naga_count <= 4:
            return "medium"
        return "high"

    def _estimate_risk(self, nagas: List[str]) -> str:
        """Estimate risk based on NAGAs involved."""
        high_risk = {"takshaka", "karkotaka", "vasuki"}
        if any(n in high_risk for n in nagas):
            return "medium"
        return "low"

    # =========================================================================
    # Prahlad's Veto (Check and Balance)
    # =========================================================================

    @naga_governed(operation="request_approval")
    def request_approval(self, proposal: FloodProposal) -> VetoDecision:
        """Request Prahlad's approval for a flood proposal."""
        self._last_heartbeat = datetime.now()

        # Already flooded → SKIP
        if proposal.classification == ServiceClassification.FLOODED:
            decision = VetoDecision(
                proposal=proposal,
                approved=False,
                reason="SKIP: Already FLOODED - no action needed",
            )
            self._flood_history.append(decision)
            return decision

        # Civilian → VETO
        if proposal.classification == ServiceClassification.CIVILIAN:
            decision = VetoDecision(
                proposal=proposal,
                approved=False,
                reason="VETO: CIVILIAN class - overhead not justified",
            )
            self._flood_history.append(decision)
            return decision

        # Rebel → APPROVE (with possible modifications)
        override_nagas = None

        # Prahlad may reduce NAGAs if overhead is too high
        if proposal.overhead_estimate == "high" and len(proposal.proposed_nagas) > 4:
            # Keep only essential NAGAs
            essential = {"sesha", "takshaka", "chitragupta"}
            override_nagas = [n for n in proposal.proposed_nagas if n in essential]

        decision = VetoDecision(
            proposal=proposal,
            approved=True,
            reason=f"APPROVED: REBEL service needs flooding with {len(proposal.proposed_nagas)} NAGAs",
            override_nagas=override_nagas,
        )
        self._flood_history.append(decision)
        return decision

    # =========================================================================
    # Soft Flood (DNA Injection)
    # =========================================================================

    @naga_governed(operation="create_flooded_class")
    def create_flooded_class(
        self,
        original_class: Type,
        decision: VetoDecision,
    ) -> Type:
        """Create a new class with NAGA genes injected (Soft Flood)."""
        self._last_heartbeat = datetime.now()

        if not decision.approved:
            raise ValueError(f"Cannot flood: decision not approved - {decision.reason}")

        # Get the NAGAs to use (may be overridden by Prahlad)
        nagas = decision.override_nagas or decision.proposal.proposed_nagas

        # Get Mixin classes
        mixins = []
        for naga in nagas:
            mixin = self.get_mixin_for_naga(naga)
            if mixin:
                mixins.append(mixin)

        if not mixins:
            # No mixins available, create a marker class
            mixins = [_NagaFloodedMarker]

        # Create new class with Mixin inheritance (DNA injection)
        flooded_name = f"Flooded{original_class.__name__}"
        bases = tuple(mixins) + (original_class,)

        flooded_class = type(
            flooded_name,
            bases,
            {
                "_naga_flooded": True,
                "_naga_genes": nagas,
                "__module__": original_class.__module__,
            },
        )

        logger.info(f"ANANTA: Created {flooded_name} with genes {nagas}")
        return flooded_class

    def get_mixin_for_naga(self, naga_name: str) -> Optional[Type]:
        """Get the Mixin class for a NAGA."""
        # Return actual Mixin if registered
        if naga_name in self._available_mixins:
            return self._available_mixins[naga_name]

        # For now, return a generic marker mixin
        return _create_marker_mixin(naga_name)

    def register_mixin(self, naga_name: str, mixin_class: Type) -> None:
        """Register a Mixin class for a NAGA."""
        self._available_mixins[naga_name] = mixin_class
        logger.debug(f"ANANTA: Registered {mixin_class.__name__} for {naga_name}")

    def list_available_mixins(self) -> List[str]:
        """List all available NAGA Mixins."""
        return list(self._mixin_names.values())

    def get_flood_history(self) -> List[VetoDecision]:
        """Get history of all flood decisions."""
        return list(self._flood_history)

    # =========================================================================
    # Loading Governance (OUROBOROS on Loaders)
    # =========================================================================

    def inject_ledger(self, ledger: "SQLiteLedger") -> None:
        """Inject ledger after construction."""
        self._ledger = ledger

    @naga_governed(operation="record_load")
    def record_load(
        self,
        loader_type: str,
        operation: str,
        item_type: str,
        item_id: Optional[str] = None,
        success: bool = True,
        error: Optional[str] = None,
        duration_ms: float = 0.0,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Record a loading operation.

        This is the core governance function - every load goes through here.

        Returns:
            Event ID for the recorded event
        """
        self._last_heartbeat = datetime.now()
        self._total_loads += 1
        if not success:
            self._failed_loads += 1
        self._total_duration_ms += duration_ms

        event_id = f"load_{self._total_loads}_{int(time.time() * 1000) % 10000}"

        event = LoadEvent(
            event_id=event_id,
            loader_type=loader_type,
            operation=operation,
            item_type=item_type,
            item_id=item_id,
            success=success,
            error=error,
            duration_ms=duration_ms,
            metadata=metadata or {},
        )

        # Store in memory
        self._load_events.append(event)
        if loader_type not in self._load_by_loader:
            self._load_by_loader[loader_type] = []
        self._load_by_loader[loader_type].append(event)
        if item_id:
            if item_id not in self._load_by_item:
                self._load_by_item[item_id] = []
            self._load_by_item[item_id].append(event)

        # LRU eviction
        while len(self._load_events) > self._max_events:
            oldest = self._load_events.pop(0)
            if oldest.loader_type in self._load_by_loader:
                try:
                    self._load_by_loader[oldest.loader_type].remove(oldest)
                except ValueError:
                    pass
            if oldest.item_id and oldest.item_id in self._load_by_item:
                try:
                    self._load_by_item[oldest.item_id].remove(oldest)
                except ValueError:
                    pass

        # Persist to ledger
        if self._ledger:
            try:
                self._ledger.record_event(
                    event_type="ANANTA_LOAD",
                    agent_id="ANANTA",
                    details={
                        "loader_type": loader_type,
                        "operation": operation,
                        "item_type": item_type,
                        "item_id": item_id,
                        "success": success,
                        "error": error,
                        "duration_ms": duration_ms,
                    },
                    result="OK" if success else "FAILED",
                )
            except Exception as e:
                logger.warning(f"ANANTA: Failed to persist load event: {e}")

        log_level = logging.DEBUG if success else logging.WARNING
        logger.log(
            log_level,
            f"ANANTA: {operation} {item_type}"
            + (f":{item_id}" if item_id else "")
            + (f" FAILED: {error}" if error else f" ({duration_ms:.1f}ms)"),
        )

        return event_id

    def wrap_manifest_registry(self) -> None:
        """
        Wrap ManifestRegistry.scan_all for governance.

        Makes manifest scanning auditable via NAGA.
        """
        if self._wrapped:
            return

        try:
            from vibe_core.loaders.manifest_registry import ManifestRegistry

            # Store reference to self for closure
            ananta = self
            original_scan = ManifestRegistry.scan_all

            @classmethod
            def governed_scan_all(cls, force: bool = False) -> int:
                start_time = time.time()

                try:
                    result = original_scan.__func__(cls, force)
                    duration_ms = (time.time() - start_time) * 1000

                    ananta.record_load(
                        loader_type="manifest_registry",
                        operation="scan_all",
                        item_type="all",
                        success=True,
                        duration_ms=duration_ms,
                        metadata={"manifests_found": result, "forced": force},
                    )

                    return result

                except Exception as e:
                    duration_ms = (time.time() - start_time) * 1000

                    ananta.record_load(
                        loader_type="manifest_registry",
                        operation="scan_all",
                        item_type="all",
                        success=False,
                        error=str(e),
                        duration_ms=duration_ms,
                    )

                    raise

            ManifestRegistry.scan_all = governed_scan_all
            self._original_scan_all = original_scan
            self._wrapped = True

            logger.info("ANANTA: ManifestRegistry wrapped for governance")

        except ImportError:
            logger.warning("ANANTA: ManifestRegistry not available")

    def unwrap(self) -> None:
        """Restore original loader functions (for testing)."""
        if not self._wrapped:
            return

        try:
            from vibe_core.loaders.manifest_registry import ManifestRegistry

            if self._original_scan_all:
                ManifestRegistry.scan_all = self._original_scan_all
                self._original_scan_all = None

            self._wrapped = False
            logger.info("ANANTA: Loaders unwrapped")

        except ImportError:
            pass

    def get_load_events(
        self,
        loader_type: Optional[str] = None,
        item_id: Optional[str] = None,
        success_only: bool = False,
        limit: int = 100,
    ) -> List[LoadEvent]:
        """Get recorded load events with optional filters."""
        self._last_heartbeat = datetime.now()

        events = self._load_events
        if loader_type:
            events = self._load_by_loader.get(loader_type, [])
        elif item_id:
            events = self._load_by_item.get(item_id, [])

        if success_only:
            events = [e for e in events if e.success]

        return events[-limit:]

    def get_failed_loads(self, limit: int = 50) -> List[LoadEvent]:
        """Get failed load events for debugging."""
        return [e for e in self._load_events if not e.success][-limit:]

    def get_load_stats(self) -> Dict[str, Any]:
        """Get loading statistics."""
        return {
            "total_loads": self._total_loads,
            "failed_loads": self._failed_loads,
            "success_rate": (self._total_loads - self._failed_loads) / max(self._total_loads, 1),
            "total_duration_ms": self._total_duration_ms,
            "avg_duration_ms": self._total_duration_ms / max(self._total_loads, 1),
            "events_in_memory": len(self._load_events),
            "loaders_tracked": list(self._load_by_loader.keys()),
            "wrapped": self._wrapped,
        }

    def get_boot_audit(self) -> Dict[str, Any]:
        """
        Get complete boot audit trail.

        This is the OUROBOROS output - what exactly was loaded and when.
        """
        return {
            "stats": self.get_load_stats(),
            "by_loader": {lt: len(events) for lt, events in self._load_by_loader.items()},
            "failures": [
                {
                    "event_id": e.event_id,
                    "loader": e.loader_type,
                    "item": f"{e.item_type}:{e.item_id}",
                    "error": e.error,
                }
                for e in self.get_failed_loads()
            ],
            "timeline": [
                {
                    "event_id": e.event_id,
                    "operation": f"{e.loader_type}.{e.operation}",
                    "item": f"{e.item_type}:{e.item_id}" if e.item_id else e.item_type,
                    "success": e.success,
                    "duration_ms": e.duration_ms,
                }
                for e in self._load_events[-20:]
            ],
        }

    # =========================================================================
    # Status
    # =========================================================================

    def get_status(self) -> NagaStatus:
        """Get NAGA health status."""
        return NagaStatus(
            naga_type=NagaType.SESHA,  # Ananta IS Shesha (the Infinite)
            healthy=self._failed_loads < 10,
            last_heartbeat=self._last_heartbeat,
            events_processed=len(self._flood_history) + self._total_loads,
            errors=self._failed_loads,
            message=f"floods={len(self._flood_history)}, loads={self._total_loads}, wrapped={self._wrapped}",
        )


# =============================================================================
# Marker Mixins (Placeholder until real Mixins are created)
# =============================================================================


class _NagaFloodedMarker:
    """Marker class indicating NAGA flooding."""

    _naga_flooded = True


def _create_marker_mixin(naga_name: str) -> Type:
    """Create a marker Mixin for a NAGA."""
    mixin_name = f"{naga_name.capitalize()}Mixin"
    return type(
        mixin_name,
        (_NagaFloodedMarker,),
        {
            "_naga_type": naga_name,
            "__module__": __name__,
        },
    )
