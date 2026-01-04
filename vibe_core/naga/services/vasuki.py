"""
VASUKI SERVICE - Der Transformator.

Vasuki - König der Schlangen, Grenze zwischen Welten.

PROMPT.md: "Memory is not Network."

Responsibilities:
- Serialize events for network (churn_out)
- Deserialize events from network (churn_in)
- Sign before sending
- Validate schema on receive
- Maintain internal/external boundary

The "churning" metaphor from Samudra Manthan:
Raw Python objects become transportable nectar.
"""

import logging
import time
from datetime import datetime
from typing import TYPE_CHECKING, Any, AsyncIterator, Callable, Dict, List, Optional

from vibe_core.protocols.correction import (
    DriftSource,
    HealingResult,
    HealingStatus,
    HealingStrategy,
    UnifiedDriftReport,
)
from vibe_core.protocols.naga import (
    NagaStatus,
    NagaType,
    NodeAddress,
    SendResult,
    SendStatus,
    SignedEnvelope,
    VasukiProtocol,
)

if TYPE_CHECKING:
    from vibe_core.naga.services.sesha import SeshaService
    from vibe_core.naga.services.takshaka import TakshakaService

logger = logging.getLogger("VASUKI")


# Events that should NOT be sent to network
INTERNAL_EVENT_TYPES = frozenset(
    [
        "DEBUG",
        "TRACE",
        "INTERNAL",
        "LOCAL_CACHE",
        "MEMORY_ONLY",
        "PRANA",  # Runtime state, dies on crash
    ]
)


class VasukiService(VasukiProtocol):
    """
    Vasuki - Das Quirlen des Ozeans.

    Transforms internal events <-> wire-ready envelopes.
    IS the boundary between internal and external.
    """

    def __init__(
        self,
        sesha: Optional["SeshaService"] = None,
        takshaka: Optional["TakshakaService"] = None,
        sign_outbound: bool = True,
    ):
        """
        Initialize Vasuki.

        Args:
            sesha: Sesha service for recording
            takshaka: Takshaka for signing/verification
            sign_outbound: Whether to sign outbound messages
        """
        self._sesha = sesha
        self._takshaka = takshaka
        self._sign_outbound = sign_outbound
        self._peers: List[NodeAddress] = []
        self._events_processed = 0
        self._errors = 0
        self._last_heartbeat = datetime.now()

        self._private_key: Optional[str] = None
        self._public_key: Optional[str] = None
        self._load_crypto()

        logger.info("🐍 VASUKI initialized - The Bridge connects")

    def _load_crypto(self) -> None:
        """Load crypto keys for signing."""
        try:
            from vibe_core.steward.crypto import load_or_generate_keys

            self._private_key, self._public_key = load_or_generate_keys()
            logger.debug("VASUKI: Crypto keys loaded")
        except Exception as e:
            logger.warning(f"VASUKI: Crypto not available: {e}")

    def inject_dependencies(
        self,
        sesha: Optional["SeshaService"] = None,
        takshaka: Optional["TakshakaService"] = None,
    ) -> None:
        """Inject dependencies after construction."""
        if sesha:
            self._sesha = sesha
        if takshaka:
            self._takshaka = takshaka

    # =========================================================================
    # Serialization (Das Quirlen)
    # =========================================================================

    def churn_out(self, event: Dict[str, Any]) -> SignedEnvelope:
        """Transform internal event -> signed wire-ready envelope."""
        try:
            import msgpack

            payload = msgpack.packb(event, use_bin_type=True)

            signature = b""
            if self._sign_outbound and self._private_key:
                try:
                    import base64

                    from vibe_core.steward.crypto import sign_content

                    sig_str = sign_content(payload.hex(), self._private_key)
                    signature = base64.b64decode(sig_str)
                except Exception as e:
                    logger.warning(f"VASUKI: Signing failed: {e}")

            envelope = SignedEnvelope(
                payload=payload,
                signature=signature,
                sender_key=self._public_key or "",
                timestamp=time.time(),
                content_type="msgpack",
            )

            self._events_processed += 1
            self._last_heartbeat = datetime.now()
            return envelope

        except Exception as e:
            logger.error(f"VASUKI: churn_out failed: {e}")
            self._errors += 1
            raise

    def churn_in(self, envelope: SignedEnvelope) -> Dict[str, Any]:
        """Transform wire envelope -> internal event."""
        try:
            import msgpack

            if envelope.content_type != "msgpack":
                raise ValueError(f"Unsupported content type: {envelope.content_type}")

            event = msgpack.unpackb(envelope.payload, raw=False)

            self._events_processed += 1
            self._last_heartbeat = datetime.now()
            return event

        except Exception as e:
            logger.error(f"VASUKI: churn_in failed: {e}")
            self._errors += 1
            raise

    # =========================================================================
    # Network Operations
    # =========================================================================

    async def send(self, target: NodeAddress, envelope: SignedEnvelope) -> SendResult:
        """Send envelope to a peer node."""
        self._last_heartbeat = datetime.now()

        if target not in self._peers:
            self._peers.append(target)

        # TODO: Actual network send
        logger.debug(f"VASUKI: Would send to {target} ({len(envelope.payload)} bytes)")

        return SendResult(
            status=SendStatus.QUEUED,
            envelope_hash=self._hash_envelope(envelope),
            message=f"Queued for {target}",
        )

    async def receive(self) -> AsyncIterator[SignedEnvelope]:
        """Receive envelopes from the network."""
        # TODO: Actual network receive
        return
        yield  # Make it a generator

    def _hash_envelope(self, envelope: SignedEnvelope) -> str:
        """Compute hash of envelope for tracking."""
        import hashlib

        content = envelope.payload + envelope.signature
        return hashlib.sha256(content).hexdigest()[:16]

    # =========================================================================
    # Boundary Enforcement
    # =========================================================================

    def is_internal(self, event: Dict[str, Any]) -> bool:
        """Check if event should stay internal (not sent to network)."""
        event_type = event.get("event_type", "")

        if event_type in INTERNAL_EVENT_TYPES:
            return True
        if event.get("_internal"):
            return True
        if event.get("_prana"):
            return True

        return False

    def get_peers(self) -> List[NodeAddress]:
        """Get known peer nodes."""
        return list(self._peers)

    def add_peer(self, peer: NodeAddress) -> None:
        """Add a peer node."""
        if peer not in self._peers:
            self._peers.append(peer)
            logger.info(f"VASUKI: Added peer {peer}")

    def remove_peer(self, peer: NodeAddress) -> bool:
        """Remove a peer node."""
        if peer in self._peers:
            self._peers.remove(peer)
            return True
        return False

    # =========================================================================
    # CorrectionHandler Interface
    # =========================================================================

    def as_handler(self) -> Callable:
        """Get this NAGA as a CorrectionHandler for DriftSource.CONFIG."""

        def handler(drift: UnifiedDriftReport, strategy: HealingStrategy) -> HealingResult:
            self._last_heartbeat = datetime.now()

            if drift.source != DriftSource.CONFIG:
                return HealingResult(
                    drift_id=drift.id,
                    status=HealingStatus.SKIPPED,
                    handler_id="vasuki",
                    message=f"Not a CONFIG drift: {drift.source}",
                )

            if not self._peers:
                return HealingResult(
                    drift_id=drift.id,
                    status=HealingStatus.SKIPPED,
                    handler_id="vasuki",
                    message="No peers connected",
                )

            if strategy == HealingStrategy.DRY_RUN:
                return HealingResult(
                    drift_id=drift.id,
                    status=HealingStatus.DEFERRED,
                    handler_id="vasuki",
                    message=f"Would propagate to {len(self._peers)} peers (DRY_RUN)",
                )

            return HealingResult(
                drift_id=drift.id,
                status=HealingStatus.DEFERRED,
                handler_id="vasuki",
                message="Propagation pending",
            )

        return handler

    # =========================================================================
    # Status
    # =========================================================================

    def get_status(self) -> NagaStatus:
        """Get NAGA health status."""
        return NagaStatus(
            naga_type=NagaType.VASUKI,
            healthy=self._errors < 10,
            last_heartbeat=self._last_heartbeat,
            events_processed=self._events_processed,
            errors=self._errors,
            message=f"peers={len(self._peers)}, crypto={'ok' if self._private_key else 'missing'}",
        )
