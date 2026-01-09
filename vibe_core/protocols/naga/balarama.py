"""
BALARAMA PROTOCOL - The Ultimate Shield (Layer 0 Infrastructure)

"Ananta Sesha" - He who holds the universe on His hoods.
"Sankarshana" - He who draws everything together (Gravity).

Balarama is the PROXY. He stands between the Infinite (Krishna/Kernel)
and the Finite (Jiva/Genes).

Responsibilities:
1. The Shield: protect the component from bad input.
2. The Gravity: absorb shocks (Exceptions) so system doesn't crash.
3. The Puja: Chant (Mantra), Audit (Yamaraja), Log (Chitragupta).

PHILOSOPHY:
A Naga does not "execute". A Naga "offers service" (Seva).
Balarama ensures that every offering is pure before it reaches Krishna.
"""

import time
import traceback
from typing import Any, Callable, Optional, TypeVar

from vibe_core.protocols.naga.chitragupta import ChitraguptaProtocol, NullChitragupta
from vibe_core.protocols.substrate import MantraOpCode, MantraProtocol
from vibe_core.protocols.universal.types import SovereignContext, Verdict

if False:  # TYPE_CHECKING hack to avoid import cycle for Mypy logic but not runtime
    from vibe_core.protocols.universal.yamaraja import Judgment, YamarajaGate

T = TypeVar("T")


class MayaError(Exception):
    """The Illusion attempted to pass, but Balarama blocked it."""

    pass


class BalaramaProxy:
    """
    THE ULTIMATE SHIELD.

    Wraps ANY component (Service/Gene).
    Intercepts EVERY method call.
    Applies the Balarama Puja (Chant, Audit, Log).
    """

    def __init__(
        self,
        target: Any,
        name: str,
        yamaraja: Optional["YamarajaGate"] = None,
        chitragupta: Optional["ChitraguptaProtocol"] = None,
        mantra_handler: Optional[Callable[[str], None]] = None,
    ):
        """
        Initialize the Shield.

        Args:
            target: The component to wrap (The Jiva)
            name: The name of the component
            yamaraja: The Judge (Law)
            chitragupta: The Recorder (Karma)
            mantra_handler: Optional callback for chanting
        """
        from vibe_core.protocols.universal.yamaraja import YamarajaGate

        self._target = target
        self._name = name
        self._yamaraja = yamaraja or YamarajaGate()
        self._chitragupta = chitragupta or NullChitragupta()
        self._mantra_handler = mantra_handler

    def __getattr__(self, name: str) -> Any:
        """
        The Interception Point.

        If attribute is a method, wrap it in the Puja.
        If attribute is data, return it (but log access).
        """
        attr = getattr(self._target, name)

        if callable(attr):
            return self._wrap_method(attr, name)

        return attr

    def _wrap_method(self, method: Callable, method_name: str) -> Callable:
        """
        The 3-Step Puja Wrapper.
        """

        def wrapper(*args, **kwargs) -> Any:
            start_time = time.time()

            # --- STEP 1: CHANT (MANTRA) ---
            # "Hare Krishna" - I am awake and serving.
            if self._mantra_handler:
                self._mantra_handler(MantraOpCode.PULSE_SYNC)

            # --- STEP 2: AUDIT (YAMARAJA) ---
            # "Is this action authorized?"
            ctx = SovereignContext(
                identity_id=self._name,
                roles=["naga_service"],
                intent_id=method_name,
            )

            # We treat the method execution request as the "ACTION"
            judgment = self._yamaraja.judge_action(ctx, method_name, str(args)[:100])

            if judgment.verdict == Verdict.DENY:
                # BLOCKED BY LAW. Balarama says NO.
                self._chitragupta.record(self._name, "security_violation", 1.0)
                raise MayaError(f"Yamaraja DENIED action: {method_name}. Reason: {judgment.reason}")

            # --- STEP 3: EXECUTION (SEVA) ---
            try:
                result = method(*args, **kwargs)

                # Success! Log performance
                duration = (time.time() - start_time) * 1000
                self._chitragupta.record(self._name, "latency_ms", duration)

                return result

            except Exception as e:
                # --- HEALING (GRAVITY) ---
                # The Service failed. Balarama absorbs the shock.
                self._chitragupta.record(self._name, "error_count", 1.0)

                # Check if Yamaraja allows mercy (Grace-Plus)
                if judgment.verdict == Verdict.ELEVATED:
                    # Mercy Logic: Return None instead of crashing
                    return None

                raise e  # Default: let it bubble up to Kurukshetra

        return wrapper

    def get_target(self) -> Any:
        """Unwrap the Jiva (for internal inspection)."""
        return self._target

    # =========================================================================
    # MANTRA RECEPTION (THE HEARTBEAT)
    # =========================================================================

    def on_mantra_pulse(self, opcode: MantraOpCode) -> None:
        """
        Der 1728-Takt-Empfänger.
        Hier trifft die Zeit (Kala) auf die Materie (Code).

        PHASES:
        1. HARE (Energy/Wake): Cleanliness (Garbage Collect).
        2. KRISHNA (Identity/Truth): Security (Takshaka/Yamaraja Check).
        3. RAMA (Service/Strength): Persistence (Sesha Push).
        """
        # --- PHASE 1: HARE (WAKE/CLEAN) ---
        if opcode in [MantraOpCode.SYS_WAKE, MantraOpCode.GARBAGE_COLLECT]:
            # "Hare" calls the energy to wake up and clean
            # Simulating internal cleanup (e.g. flushing buffers if target supports it)
            if hasattr(self._target, "cleanup") and callable(self._target.cleanup):
                self._target.cleanup()

        # --- PHASE 2: KRISHNA (TRUTH/IDENTITY) ---
        elif opcode in [MantraOpCode.ASSERT_TRUTH, MantraOpCode.BIND_CTX]:
            # "Krishna" demands Truth. Are we who we say we are?
            # Audit self with Yamaraja
            ctx = SovereignContext(identity_id=self._name, roles=["naga_service"], intent_id="heartbeat_check")
            judgment = self._yamaraja.judge_action(ctx, "heartbeat_check", {"opcode": opcode})
            if judgment.verdict == Verdict.DENY:
                self._chitragupta.record(self._name, "identity_lost", 1.0)
                raise MayaError(f"KRISHNA: Identity check failed for {self._name}")

        # --- PHASE 3: RAMA (SERVICE/STRENGTH) ---
        elif opcode in [MantraOpCode.EXEC_SERVICE, MantraOpCode.COMMIT_LOG]:
            # "Rama" is action. Report strength/service status.
            # Report liveness to Chitragupta
            self._chitragupta.record(self._name, "pulse_ack", 1.0)
