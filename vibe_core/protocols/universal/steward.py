"""
STEWARD PROTOCOL - The Representative (Layer 1).

"Der Steward ist der Fahrer des Wagens."

Er verbindet Identity (Layer 0) mit Action (Layer 2).
Er ruft Yamaraja an, bevor er handelt.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "vyasa"
__position__ = 4
__genesis__ = "0x75ecc23f"  # GenesisByte: parampara % 37 == 0

from dataclasses import dataclass
from typing import Any, Protocol, runtime_checkable

from .types import SovereignContext, TranscendentalQuality
# ONE Yamaraja - all aspects in mahajanas/yamaraja (acintya)
# Defer import to break cycle with universal/__init__ -> cli -> steward -> mahajanas
# from vibe_core.protocols.mahajanas.yamaraja import Verdict, YamarajaGate

# V2 SYSTEM REFERENCE
# The V2 Steward System (System Lifecycle & Identity) is defined in _steward.py
from vibe_core.mahamantra.protocols._steward import StewardSystem, get_steward

@runtime_checkable
class StewardProtocol(Protocol):
    """
    [LEGACY] Interface für den Agenten-Kern (Command Execution).
    
    NOTE: This is the 'Command Executor' capability, not the System Protocol.
    For System Identity & Lifecycle, see vibe_core.mahamantra.protocols._steward.
    """

    def execute_command(self, command: str, payload: Any) -> Any: ...


class VedicSteward:
    """
    Die Referenz-Implementierung.
    """

    def __init__(self, context: SovereignContext):
        # ONE Yamaraja - all aspects in mahajanas/yamaraja (acintya)
        from vibe_core.protocols.mahajanas.yamaraja import YamarajaGate
        self.context = context
        self.gate = YamarajaGate()  # Dependency Injection wäre besser, aber wir machen es explizit.

    def execute_command(self, command: str, payload: Any) -> Any:
        # ONE Yamaraja - all aspects in mahajanas/yamaraja (acintya)
        from vibe_core.protocols.mahajanas.yamaraja import Verdict
        # 1. Ask Yamaraja
        judgment = self.gate.judge_action(self.context, command, payload)

        # 2. Handle Verdict
        if judgment.verdict == Verdict.DENY:
            raise PermissionError(f"Yamaraja says NO: {judgment.reason}")

        if judgment.verdict == Verdict.ATONE:
            self._log_penance(judgment)
            # Proceed with caution

        if judgment.verdict == Verdict.ELEVATED:
            self._chant_mantra()
            # Proceed with Grace

        # 3. Execute (Simulation)
        return f"Executed {command} with {judgment.verdict}"

    def _log_penance(self, judgment):
        print(f"WARNING: Bad Karma accumulated: {judgment.karma_cost}")

    def _chant_mantra(self):
        print("Hare Krishna... Grace Granted.")
