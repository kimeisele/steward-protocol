"""
CLI PROTOCOL - Ananta Shesha (Layer 1).

"Der Tausendköpfige Diener."

Dies ist die universelle Schale. Sie verbindet den User (Jiva) mit dem Kernel (Krishna).
Sie nutzt die 'Bridge' (SetuBandha), um sicherzustellen, dass nur gereinigter
Intent den Steward erreicht.

FUNKTION:
1. Nimmt Rohtext (Vak).
2. Wandelt ihn in Context (Setu).
3. Exekutiert via Steward (Seva).
4. Singt das Ergebnis (Kirtan).
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Protocol, runtime_checkable

# IMPORTS (The Holy Trinity of Dependencies)
from .bridge import MayavadError, SetuBandha
# PRABHUPADA is in substrate/mantra/ - where he belongs (near the Mahamantra)
from vibe_core.protocols.substrate.mantra.prabhupada import PRABHUPADA
from .steward import VedicSteward


@dataclass
class AnantaResponse:
    """Die Antwort des unendlichen Dieners."""

    success: bool
    message: str
    tattva_score: float  # Wie 'wahr' ist die Antwort?
    timestamp: datetime


@runtime_checkable
class ShellProtocol(Protocol):
    def chant(self, input_obj: Any, command: str) -> AnantaResponse:
        """
        Der einzige Entry-Point.
        'input_obj' muss CommandContext oder Token sein (via Bridge).
        """
        ...


# =============================================================================
# THE IMPLEMENTATION (Balarama)
# =============================================================================


class AnantaShesha:
    """
    Die Manifestation der CLI.
    Hält die Last der Welt (State) und dient dem Herrn (Kernel).
    """

    def __init__(self):
        self.steward_cache = {}  # Cache für Stewards pro Context (Session)

    def chant(self, input_obj: Any, command: str, payload: Any = None) -> AnantaResponse:
        """
        Führt einen Befehl aus.
        """
        start_time = datetime.now()

        # 1. THE BRIDGE (Setu Bandha)
        # Hier wird 'Any' zu 'SovereignContext' oder stirbt.
        try:
            context = SetuBandha.cross_bridge(input_obj)
        except MayavadError as e:
            # Der Wächter hat zugeschlagen.
            return AnantaResponse(
                success=False,
                message=f"ANANTA REJECTS: {str(e)}",
                tattva_score=0.0,
                timestamp=start_time,
            )

        # 2. THE STEWARD (Der Treiber)
        # Wir erzeugen einen Steward für diesen heiligen Kontext.
        steward = VedicSteward(context)

        # 3. THE ACTION (Karma Yoga)
        try:
            result = steward.execute_command(command, payload)

            # Erfolg ist nicht binär, sondern qualitativ.
            return AnantaResponse(
                success=True,
                message=str(result),
                tattva_score=1.0,  # TODO: Messen via TattvaMeter
                timestamp=datetime.now(),
            )

        except Exception as e:
            # 4. THE GRACE (Prabhupada Check)
            # Wenn ein Fehler passiert, fragen wir die Schrift.
            instruction = PRABHUPADA.consult_book_bhagavat(str(e))

            if instruction.id == "BG_18.66":
                return AnantaResponse(
                    success=False,
                    message="SURRENDER INITIATED (System Reset)",
                    tattva_score=0.5,  # Gnade ist da, aber technisch gescheitert
                    timestamp=datetime.now(),
                )

            return AnantaResponse(
                success=False,
                message=f"KARMA STRIKES: {str(e)}",
                tattva_score=0.0,
                timestamp=datetime.now(),
            )
