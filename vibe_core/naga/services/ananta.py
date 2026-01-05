"""
ANANTA SERVICE - The Gene Splicer (12th Lord).

Ananta - The Infinite One, cosmic form of Sesha who holds all worlds.

From mythology: Ananta Shesha is the infinite serpent upon whom
Vishnu rests. He holds the entire universe on his thousand hoods.

Responsibilities:
- Analyze services for NAGA needs (Detection Criteria)
- Propose flooding with appropriate Mixins
- Request Prahlad's approval (Check and Balance)
- Create flooded classes via DNA injection (Soft Flood)

Integration:
- Works with Narada (discovery) → Ananta (proposal) → Prahlad (veto)
- Uses Mixin pattern, NOT Proxy pattern (preserves isinstance)
"""

import ast
import inspect
import logging
from datetime import datetime
from typing import Dict, List, Optional, Set, Type

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

    def __init__(self) -> None:
        """Initialize Ananta."""
        super().__init__(service_name="Ananta")

        self._flood_history: List[VetoDecision] = []
        self._available_mixins: Dict[str, Type] = {}
        self._last_heartbeat = datetime.now()

        # Register available Mixins (will be expanded)
        self._register_mixins()

        logger.info("ANANTA initialized - Gene Splicer ready")

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

    def get_status(self) -> NagaStatus:
        """Get NAGA health status."""
        return NagaStatus(
            naga_type=NagaType.SESHA,  # No ANANTA in NagaType yet
            healthy=True,
            last_heartbeat=self._last_heartbeat,
            events_processed=len(self._flood_history),
            errors=0,
            message=f"decisions={len(self._flood_history)}, mixins={len(self._available_mixins)}",
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
