"""
UDANA ROUTER - Agent ↔ Mahajana Communication via UDANA Nadi
=============================================================

"udāna" - The ascending breath, rising upward.

UDANA NADI is the channel for Agent ↔ Mahajana communication.
Agents "ascend" to Mahajanas for guidance, routing, and dispatch.

ARCHITECTURE:
=============

    Agent Request
        ↓
    UdanaRouter.route() ← NadiMessage from Agent
        ↓
    MahajanaRouter.route() → MahajanaRoute
        ↓
    Dispatch to Mahajana via NadiOp.DELEGATE
        ↓
    Response via NadiOp.RECEIVE
        ↓
    UdanaRouter.receive() → Back to Agent

ALL CONSTANTS DERIVED FROM SEED.PY:
- Uses NadiType.UDANA (index 3)
- Routing capacity from NADI_RESONANCE (72)
- Timeouts from PRANA_DURATION_MS (4000ms)
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "narada"
__position__ = 2
__genesis__ = "0x74232aa8"  # GenesisByte: parampara % 37 == 0

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, Final, List, Optional
from uuid import uuid4

# Import Nadi infrastructure
# GAD compliance
from vibe_core.mahamantra import GADBase, LocalNadi, MantraOpCode, NadiProtocol, NadiType
from vibe_core.mahamantra.substrate.nadi import (
    NADI_CAPACITY,
    NADI_TIMEOUT_MS,
    NadiConnection,
    NadiMessage,
    NadiOp,
    NadiPriority,
)

# Import seed constants
from vibe_core.mahamantra.substrate.seed import (
    NADI_RESONANCE,
    NAVA,
    PRANA_DURATION_MS,
    SHARANAGATI,
)

# Import MahajanaRouter for routing decisions
from vibe_core.protocols.mahajanas.router import (
    Mahajana,
    MahajanaRoute,
    MahajanaRouter,
    get_router,
)

logger = logging.getLogger("UDANA_ROUTER")


# =============================================================================
# DERIVED CONSTANTS
# =============================================================================

# Max concurrent agent routes = NADI_RESONANCE = 72
UDANA_ROUTE_CAPACITY: Final[int] = NADI_RESONANCE  # 72

# Route timeout = PRANA_DURATION_MS × SHARANAGATI = 24000ms = 24 seconds
UDANA_ROUTE_TIMEOUT_MS: Final[int] = PRANA_DURATION_MS * SHARANAGATI  # 24000ms

# Max routing attempts = NAVA = 9 (the 9 operations)
UDANA_MAX_ATTEMPTS: Final[int] = NAVA  # 9

# Verification
assert UDANA_ROUTE_CAPACITY == 72, "Route capacity = NADI_RESONANCE"
assert UDANA_ROUTE_TIMEOUT_MS == 24000, "Route timeout = 24 seconds"
assert UDANA_MAX_ATTEMPTS == 9, "Max attempts = NAVA"


# =============================================================================
# UDANA REQUEST - Agent → Mahajana
# =============================================================================


@dataclass
class UdanaRequest:
    """
    A routing request from Agent to Mahajana.

    The Agent "ascends" (udana) to seek guidance from a Mahajana.
    """

    request_id: str
    agent_id: str
    opcode: MantraOpCode  # The operation to route
    payload: Dict[str, Any]  # Request data
    timestamp: datetime = field(default_factory=datetime.now)
    attempts: int = 0  # Retry count
    resolved_mahajana: Optional[Mahajana] = None
    resolved_route: Optional[MahajanaRoute] = None

    def to_nadi_message(self, source: str, target: str) -> NadiMessage:
        """Convert to NadiMessage for transport."""
        return NadiMessage(
            source=source,
            target=target,
            nadi_type=NadiType.UDANA,
            operation=NadiOp.REQUEST,
            payload={
                "request_id": self.request_id,
                "agent_id": self.agent_id,
                "opcode": self.opcode.name,
                "opcode_value": self.opcode.value,
                "data": self.payload,
                "attempts": self.attempts,
                "resolved_mahajana": self.resolved_mahajana.value if self.resolved_mahajana else None,
            },
            priority=NadiPriority.RAJAS,
            timestamp=self.timestamp,
        )

    @classmethod
    def from_nadi_message(cls, msg: NadiMessage) -> "UdanaRequest":
        """Create UdanaRequest from NadiMessage."""
        payload = msg.payload
        opcode_name = payload.get("opcode", "SYS_WAKE")
        opcode = MantraOpCode[opcode_name]

        mahajana_name = payload.get("resolved_mahajana")
        mahajana = Mahajana(mahajana_name) if mahajana_name else None

        return cls(
            request_id=payload.get("request_id", str(uuid4())),
            agent_id=payload.get("agent_id", "unknown"),
            opcode=opcode,
            payload=payload.get("data", {}),
            timestamp=msg.timestamp,
            attempts=payload.get("attempts", 0),
            resolved_mahajana=mahajana,
        )


# =============================================================================
# UDANA RESPONSE - Mahajana → Agent
# =============================================================================


@dataclass
class UdanaResponse:
    """
    A routing response from Mahajana back to Agent.
    """

    response_id: str
    request_id: str  # Links to original request
    agent_id: str
    mahajana: Mahajana
    route: MahajanaRoute
    result: Dict[str, Any]  # Response data
    success: bool
    timestamp: datetime = field(default_factory=datetime.now)
    error: Optional[str] = None

    def to_nadi_message(self, source: str, target: str) -> NadiMessage:
        """Convert to NadiMessage for transport."""
        return NadiMessage(
            source=source,
            target=target,
            nadi_type=NadiType.UDANA,
            operation=NadiOp.RECEIVE,
            payload={
                "response_id": self.response_id,
                "request_id": self.request_id,
                "agent_id": self.agent_id,
                "mahajana": self.mahajana.value,
                "route": {
                    "opcode": self.route.opcode.name,
                    "quarter": self.route.quarter,
                    "position": self.route.position,
                },
                "result": self.result,
                "success": self.success,
                "error": self.error,
            },
            priority=NadiPriority.RAJAS,
            timestamp=self.timestamp,
        )

    @classmethod
    def from_nadi_message(cls, msg: NadiMessage, route: MahajanaRoute) -> "UdanaResponse":
        """Create UdanaResponse from NadiMessage."""
        payload = msg.payload
        return cls(
            response_id=payload.get("response_id", str(uuid4())),
            request_id=payload.get("request_id", "unknown"),
            agent_id=payload.get("agent_id", "unknown"),
            mahajana=Mahajana(payload.get("mahajana", "brahma")),
            route=route,
            result=payload.get("result", {}),
            success=payload.get("success", False),
            error=payload.get("error"),
            timestamp=msg.timestamp,
        )


# =============================================================================
# UDANA ROUTER - The Ascending Channel
# =============================================================================


class UdanaRouter(GADBase):
    """
    UDANA Nadi for Agent ↔ Mahajana communication.

    Wraps MahajanaRouter with Nadi transport.
    GAD-000 compliant.

    FLOW:
    1. Agent sends UdanaRequest with OpCode
    2. UdanaRouter routes via MahajanaRouter
    3. Request dispatched to target Mahajana
    4. Response comes back
    5. UdanaRouter sends UdanaResponse to Agent
    """

    def __init__(
        self,
        router_id: str = "udana_router",
        mahajana_router: Optional[MahajanaRouter] = None,
    ):
        super().__init__()  # Initialize GADBase

        self._router_id = router_id

        # Create UDANA Nadi for this router
        self._nadi = LocalNadi(
            endpoint_id=f"udana_{router_id}",
            nadi_type=NadiType.UDANA,
        )

        # Use provided router or get default
        self._mahajana_router = mahajana_router or get_router()

        # Pending requests
        self._pending: Dict[str, UdanaRequest] = {}

        # Completed routes
        self._completed: Dict[str, UdanaResponse] = {}

        # Connected agents
        self._agents: Dict[str, str] = {}  # agent_id → endpoint_id

        # Callbacks
        self._on_route: Optional[Callable[[UdanaRequest, MahajanaRoute], None]] = None
        self._on_response: Optional[Callable[[UdanaResponse], None]] = None

        # Stats
        self._requests_received = 0
        self._routes_computed = 0
        self._responses_sent = 0
        self._failures = 0

    # =========================================================================
    # PROPERTIES
    # =========================================================================

    @property
    def router_id(self) -> str:
        return self._router_id

    @property
    def nadi(self) -> NadiProtocol:
        """Access underlying Nadi."""
        return self._nadi

    @property
    def mahajana_router(self) -> MahajanaRouter:
        """Access Mahajana router."""
        return self._mahajana_router

    @property
    def pending_count(self) -> int:
        """Count of pending requests."""
        return len(self._pending)

    @property
    def connected_agents(self) -> int:
        """Count of connected agents."""
        return len(self._agents)

    # =========================================================================
    # GAD COMPLIANCE
    # =========================================================================

    def discover(self) -> Dict[str, object]:
        """GAD Discoverability."""
        return {
            "service": "udana_router",
            "mahajana": __mahajana__,
            "position": __position__,
            "genesis": __genesis__,
            "nadi_type": NadiType.UDANA.name,
            "capabilities": [
                "opcode_routing",
                "mahajana_dispatch",
                "agent_connection",
            ],
            "constants": {
                "route_capacity": UDANA_ROUTE_CAPACITY,
                "route_timeout_ms": UDANA_ROUTE_TIMEOUT_MS,
                "max_attempts": UDANA_MAX_ATTEMPTS,
            },
        }

    def get_state(self) -> Dict[str, object]:
        """GAD Observability."""
        return {
            "router_id": self._router_id,
            "pending_requests": self.pending_count,
            "completed_routes": len(self._completed),
            "connected_agents": self.connected_agents,
            "requests_received": self._requests_received,
            "routes_computed": self._routes_computed,
            "responses_sent": self._responses_sent,
            "failures": self._failures,
            "heartbeat": self.heartbeat.get_summary(),
        }

    def detect_drift(self) -> List[str]:
        """GAD Drift Detection."""
        issues = []

        # Check for stale requests
        now = datetime.now()
        for req_id, req in self._pending.items():
            elapsed = (now - req.timestamp).total_seconds() * 1000
            if elapsed > UDANA_ROUTE_TIMEOUT_MS:
                issues.append(f"Stale request: {req_id}")

        # Check for too many pending
        if self.pending_count > UDANA_ROUTE_CAPACITY:
            issues.append(f"Too many pending requests: {self.pending_count}")

        # Check for too many retries
        for req_id, req in self._pending.items():
            if req.attempts >= UDANA_MAX_ATTEMPTS:
                issues.append(f"Request {req_id} exceeded max attempts")

        return issues

    def test_tapas(self) -> bool:
        """GAD Tapas: Resource efficiency."""
        return self.pending_count <= UDANA_ROUTE_CAPACITY

    def test_saucam(self) -> bool:
        """GAD Saucam: Connection purity."""
        return self._nadi.nadi_type == NadiType.UDANA

    # =========================================================================
    # AGENT MANAGEMENT
    # =========================================================================

    def register_agent(self, agent_id: str, endpoint_id: str) -> bool:
        """Register an agent endpoint."""
        if len(self._agents) >= UDANA_ROUTE_CAPACITY:
            logger.warning(f"Agent capacity reached: {UDANA_ROUTE_CAPACITY}")
            return False

        self._agents[agent_id] = endpoint_id
        logger.info(f"Agent registered: {agent_id} → {endpoint_id}")
        return True

    def unregister_agent(self, agent_id: str) -> bool:
        """Unregister an agent."""
        if agent_id in self._agents:
            del self._agents[agent_id]
            logger.info(f"Agent unregistered: {agent_id}")
            return True
        return False

    def get_agent_endpoint(self, agent_id: str) -> Optional[str]:
        """Get endpoint for an agent."""
        return self._agents.get(agent_id)

    # =========================================================================
    # ROUTING CORE
    # =========================================================================

    def route_opcode(
        self, agent_id: str, opcode: MantraOpCode, payload: Optional[Dict[str, Any]] = None
    ) -> UdanaRequest:
        """
        Route an OpCode from an agent to the appropriate Mahajana.

        1. Create UdanaRequest
        2. Route via MahajanaRouter
        3. Store as pending
        4. Return routed request
        """
        # Create request
        request = UdanaRequest(
            request_id=f"req_{uuid4().hex[:8]}",
            agent_id=agent_id,
            opcode=opcode,
            payload=payload or {},
        )

        # Route through Mahajana router
        try:
            mahajana = self._mahajana_router.route(opcode)
            route = self._mahajana_router.get_route(opcode)

            request.resolved_mahajana = mahajana
            request.resolved_route = route

            self._routes_computed += 1

        except ValueError as e:
            # HEAD opcode or unknown - use fallback
            logger.warning(f"Route failed for {opcode}: {e}")
            self._failures += 1
            request.attempts += 1

        # Track
        self._pending[request.request_id] = request
        self._requests_received += 1

        # Trigger callback
        if self._on_route and request.resolved_route:
            self._on_route(request, request.resolved_route)

        logger.info(
            f"UDANA route: agent={agent_id}, opcode={opcode.name} → "
            f"mahajana={request.resolved_mahajana.value if request.resolved_mahajana else 'NONE'}"
        )

        return request

    def complete_request(
        self, request_id: str, result: Dict[str, Any], success: bool = True, error: Optional[str] = None
    ) -> Optional[UdanaResponse]:
        """
        Complete a pending request with a response.

        Called when Mahajana returns a result.
        """
        if request_id not in self._pending:
            logger.warning(f"Unknown request: {request_id}")
            return None

        request = self._pending.pop(request_id)

        if not request.resolved_mahajana or not request.resolved_route:
            logger.warning(f"Request {request_id} was never routed")
            return None

        response = UdanaResponse(
            response_id=f"res_{uuid4().hex[:8]}",
            request_id=request_id,
            agent_id=request.agent_id,
            mahajana=request.resolved_mahajana,
            route=request.resolved_route,
            result=result,
            success=success,
            error=error,
        )

        self._completed[request_id] = response
        self._responses_sent += 1

        if not success:
            self._failures += 1

        # Trigger callback
        if self._on_response:
            self._on_response(response)

        logger.info(f"UDANA response: request={request_id}, success={success}, mahajana={response.mahajana.value}")

        return response

    def retry_request(self, request_id: str) -> bool:
        """
        Retry a pending request.

        Returns False if max attempts exceeded.
        """
        if request_id not in self._pending:
            return False

        request = self._pending[request_id]

        if request.attempts >= UDANA_MAX_ATTEMPTS:
            logger.warning(f"Request {request_id} exceeded max attempts")
            return False

        request.attempts += 1
        request.timestamp = datetime.now()

        # Re-route
        try:
            mahajana = self._mahajana_router.route(request.opcode)
            route = self._mahajana_router.get_route(request.opcode)
            request.resolved_mahajana = mahajana
            request.resolved_route = route
            self._routes_computed += 1
            return True
        except ValueError:
            self._failures += 1
            return False

    def get_pending_request(self, request_id: str) -> Optional[UdanaRequest]:
        """Get a pending request by ID."""
        return self._pending.get(request_id)

    def get_response(self, request_id: str) -> Optional[UdanaResponse]:
        """Get a completed response by request ID."""
        return self._completed.get(request_id)

    # =========================================================================
    # NADI INTEGRATION
    # =========================================================================

    def dispatch_to_mahajana(self, request: UdanaRequest, mahajana_endpoint: str) -> bool:
        """
        Dispatch a request to target Mahajana via UDANA Nadi.
        """
        if not request.resolved_mahajana:
            logger.warning("Cannot dispatch unrouted request")
            return False

        nadi_msg = NadiMessage(
            source=self._nadi.endpoint_id,
            target=mahajana_endpoint,
            nadi_type=NadiType.UDANA,
            operation=NadiOp.DELEGATE,
            payload={
                "type": "udana_dispatch",
                "request": request.to_nadi_message(
                    self._nadi.endpoint_id,
                    mahajana_endpoint,
                ).payload,
            },
            priority=NadiPriority.RAJAS,
        )

        return self._nadi.send(nadi_msg)

    def receive_from_nadi(self) -> List[UdanaResponse]:
        """
        Receive pending responses from Nadi.
        """
        responses = []

        for nadi_msg in self._nadi.receive_all():
            if nadi_msg.operation == NadiOp.RECEIVE:
                payload = nadi_msg.payload
                request_id = payload.get("request_id")

                if request_id and request_id in self._pending:
                    response = self.complete_request(
                        request_id=request_id,
                        result=payload.get("result", {}),
                        success=payload.get("success", False),
                        error=payload.get("error"),
                    )
                    if response:
                        responses.append(response)

        return responses

    # =========================================================================
    # CALLBACKS
    # =========================================================================

    def set_on_route(self, callback: Callable[[UdanaRequest, MahajanaRoute], None]) -> None:
        """Set callback for routing events."""
        self._on_route = callback

    def set_on_response(self, callback: Callable[[UdanaResponse], None]) -> None:
        """Set callback for response events."""
        self._on_response = callback

    # =========================================================================
    # MAINTENANCE
    # =========================================================================

    def prune_stale_requests(self) -> int:
        """Remove stale requests (exceeded timeout)."""
        now = datetime.now()
        stale = []

        for req_id, req in self._pending.items():
            elapsed = (now - req.timestamp).total_seconds() * 1000
            if elapsed > UDANA_ROUTE_TIMEOUT_MS:
                stale.append(req_id)

        for req_id in stale:
            del self._pending[req_id]
            self._failures += 1

        if stale:
            logger.info(f"Pruned {len(stale)} stale UDANA requests")

        return len(stale)

    def prune_old_responses(self, max_age_ms: int = UDANA_ROUTE_TIMEOUT_MS * 2) -> int:
        """Remove old completed responses."""
        now = datetime.now()
        old = []

        for req_id, resp in self._completed.items():
            elapsed = (now - resp.timestamp).total_seconds() * 1000
            if elapsed > max_age_ms:
                old.append(req_id)

        for req_id in old:
            del self._completed[req_id]

        return len(old)

    def pulse(self) -> bool:
        """
        Send heartbeat and prune stale data.
        """
        self.prune_stale_requests()
        self.prune_old_responses()
        self._nadi.pulse()
        self.chant()
        return True

    # =========================================================================
    # STATS
    # =========================================================================

    def get_stats(self) -> Dict[str, Any]:
        """Get router statistics."""
        return {
            "router_id": self._router_id,
            "pending_requests": self.pending_count,
            "completed_routes": len(self._completed),
            "connected_agents": self.connected_agents,
            "requests_received": self._requests_received,
            "routes_computed": self._routes_computed,
            "responses_sent": self._responses_sent,
            "failures": self._failures,
            "nadi_stats": self._nadi.get_stats().__dict__,
        }


# =============================================================================
# FACTORY FUNCTION
# =============================================================================


def get_udana_router(router_id: str = "udana_router") -> UdanaRouter:
    """
    Get UdanaRouter through ServiceRegistry (WIRED + NAGA-wrapped).

    ARCHITECTURE:
        Raw UdanaRouter → ServiceRegistry.register() → NagaProxy wrapping

    This ensures:
    - Singleton pattern via ServiceRegistry
    - NAGA observation (Narada sees all Agent→Mahajana routing)
    - NAGA profiling (Chitragupta tracks routing latency)
    - NAGA isolation (Kaliya handles routing failures)
    """
    from vibe_core.di import ServiceRegistry

    # Use UdanaRouter type as protocol (GADBase compliant)
    existing = ServiceRegistry.get(UdanaRouter)
    if existing is not None:
        return existing

    # Create new instance
    instance = UdanaRouter(router_id)

    # Register with ServiceRegistry (applies NagaProxy wrapping!)
    ServiceRegistry.register(UdanaRouter, instance)
    logger.info("✅ UdanaRouter registered via ServiceRegistry (WIRED + NAGA-observed)")

    return ServiceRegistry.get(UdanaRouter)  # type: ignore


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Constants
    "UDANA_ROUTE_CAPACITY",
    "UDANA_ROUTE_TIMEOUT_MS",
    "UDANA_MAX_ATTEMPTS",
    # Data structures
    "UdanaRequest",
    "UdanaResponse",
    # Router
    "UdanaRouter",
    # Factory
    "get_udana_router",
]
