"""
YAMARAJA ADAPTER - Bridge to Holographic Reality
=================================================

"We don't destroy, we bridge."

This adapter connects:
- NEW: MahajanaProtocol (the discovered interface)
- OLD: governance/yamaraja.py (the existing implementation)

The existing YamarajaGate is NOT touched.
It continues to work as before.
This adapter just makes it accessible via the Mahajana interface.

GAD-000: Composable (wraps existing), Recoverable (explicit errors)
"""

from typing import Any, List, Optional

from vibe_core.protocols.universal.mantra import MantraOpCode
from vibe_core.protocols.universal.types import SovereignContext
from vibe_core.protocols.mahajanas.router import Mahajana
from vibe_core.protocols.mahajanas.protocol import (
    MahajanaProtocol,
    MahajanaResult,
    MahajanaVerdict,
    BaseMahajana,
)


class YamarajaAdapter(BaseMahajana):
    """
    Adapter that bridges governance/yamaraja.py to MahajanaProtocol.

    Yamaraja owns: ASSERT_TRUTH (Bit 5)
    Yamaraja's principle: JUDGMENT

    The existing YamarajaGate has:
    - judge_action(context, command, payload) -> Judgment
    - YamarajaPhysics.measure_kriya() for performance

    This adapter translates between the old and new interfaces.
    """

    def __init__(self) -> None:
        super().__init__(Mahajana.YAMARAJA)
        self._gate: Optional[Any] = None  # Lazy loaded

    def _get_gate(self) -> Any:
        """Lazy load the existing YamarajaGate."""
        if self._gate is None:
            from vibe_core.protocols.governance.yamaraja import YamarajaGate
            self._gate = YamarajaGate()
        return self._gate

    def handle(
        self,
        opcode: MantraOpCode,
        context: Any,
        payload: Any
    ) -> MahajanaResult:
        """
        Handle ASSERT_TRUTH by delegating to existing YamarajaGate.

        Translation:
        - MahajanaProtocol.handle() → YamarajaGate.judge_action()
        - Judgment.verdict → MahajanaVerdict
        """
        if opcode != MantraOpCode.ASSERT_TRUTH:
            return self._reject(
                opcode,
                f"Yamaraja only handles ASSERT_TRUTH, not {opcode.name}"
            )

        # Ensure we have a valid context
        if not isinstance(context, SovereignContext):
            return self._reject(
                opcode,
                "Yamaraja requires SovereignContext (no ghost in the machine)"
            )

        # Extract command from payload or use default
        command = "assert"
        if isinstance(payload, dict) and "command" in payload:
            command = payload["command"]
        elif isinstance(payload, str):
            command = payload

        # Delegate to existing implementation
        try:
            gate = self._get_gate()
            judgment = gate.judge_action(context, command, payload)

            # Translate Verdict → MahajanaVerdict
            from vibe_core.protocols.governance.yamaraja import Verdict as OldVerdict

            if judgment.verdict == OldVerdict.ALLOW:
                return self._accept(
                    opcode,
                    {"judgment": judgment, "karma_cost": judgment.karma_cost},
                    judgment.reason
                )
            elif judgment.verdict == OldVerdict.DENY:
                return self._reject(opcode, judgment.reason)
            elif judgment.verdict == OldVerdict.ATONE:
                # ATONE = needs purification first, delegate to Kumaras
                return MahajanaResult(
                    verdict=MahajanaVerdict.TRANSFORM,
                    mahajana=Mahajana.YAMARAJA,
                    opcode=opcode,
                    payload={"requires": "prayascitta", "original": payload},
                    reason=judgment.reason,
                    delegate_to=Mahajana.KUMARAS  # Purity/Reset
                )
            elif judgment.verdict == OldVerdict.ELEVATED:
                # ELEVATED = Grace, beyond normal judgment
                return self._accept(
                    opcode,
                    {"judgment": judgment, "grace": True},
                    f"GRACE: {judgment.reason}"
                )
            else:
                return self._reject(opcode, f"Unknown verdict: {judgment.verdict}")

        except Exception as e:
            # GAD-000: Recoverable - explicit error
            return self._reject(opcode, f"Yamaraja error: {str(e)}")


# =============================================================================
# FACTORY FUNCTION
# =============================================================================

def get_yamaraja() -> YamarajaAdapter:
    """Get a Yamaraja adapter instance."""
    return YamarajaAdapter()


__all__ = ["YamarajaAdapter", "get_yamaraja"]
