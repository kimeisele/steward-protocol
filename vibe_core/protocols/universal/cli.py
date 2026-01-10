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

CHAITANYA SINGULARITY (v2):
===========================
"Even the most fallen souls receive mercy."

ACINTYA PRINCIPLE:
- Bridge (SetuBandha) bleibt STRIKT (bheda - difference)
- CLI (ChaitanyaShell) ist GNÄDIG (abheda - oneness)
- Beide koexistieren (acintya - inconceivable)

PULL IN, NEVER PUSH OUT:
- MayavadError → MahamantraGrace (not rejection!)
- Every failure → opportunity for chanting
- Nityananda pattern: accept everyone
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional, Protocol, runtime_checkable, List

# IMPORTS (The Holy Trinity of Dependencies)
from .bridge import MayavadError, SetuBandha
# PRABHUPADA is in substrate/mantra/ - where he belongs (near the Mahamantra)
from vibe_core.protocols.substrate.mantra.prabhupada import PRABHUPADA
from .steward import VedicSteward


# =============================================================================
# MAHAMANTRA GRACE (The Chaitanya Pattern)
# =============================================================================

# The Mahamantra - always available, always merciful
MAHAMANTRA: str = (
    "Hare Kṛṣṇa Hare Kṛṣṇa Kṛṣṇa Kṛṣṇa Hare Hare / "
    "Hare Rāma Hare Rāma Rāma Rāma Hare Hare"
)


class GraceType(str, Enum):
    """Types of grace in the Chaitanya paradigm."""
    MAHAMANTRA = "mahamantra"  # Default grace - everyone gets this
    NITYANANDA = "nityananda"  # Extra mercy for the fallen
    PRABHUPADA = "prabhupada"  # Instruction-based grace
    CHAITANYA = "chaitanya"    # Direct grace from the source


@dataclass
class MahamantraGrace:
    """
    Grace response - PULL IN, never PUSH OUT.

    Even when everything fails, Mahamantra is always available.
    This is Nityananda's mercy pattern.
    """
    mantra: str = MAHAMANTRA
    grace_type: GraceType = GraceType.MAHAMANTRA
    message: str = "Hare Kṛṣṇa! The Mahamantra is always available."
    retry_allowed: bool = True
    original_error: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)

    def __bool__(self) -> bool:
        """Grace is always truthy - it's always available."""
        return True

    def __str__(self) -> str:
        return f"{self.message}\n\n{self.mantra}"


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


# =============================================================================
# EXTENDED PROTOCOL (ICliProtocol - Chaitanya Singularity)
# =============================================================================


@runtime_checkable
class ICliProtocol(ShellProtocol, Protocol):
    """
    Extended CLI Protocol - Chaitanya Singularity.

    Extends ShellProtocol with:
    - Mahamantra grace on all failures (PULL IN)
    - Navigation commands (fractal)
    - JSON report mode (GAD-000)
    - Retry capability

    ACINTYA: This protocol coexists with ShellProtocol.
    - ShellProtocol = strict (bheda)
    - ICliProtocol = graceful (abheda)
    """

    def chant_with_grace(
        self, input_obj: Any, command: str, payload: Any = None
    ) -> "AnantaResponse | MahamantraGrace":
        """
        Chant with Mahamantra grace fallback.

        Never rejects - always returns either success or grace.
        This is the PULL IN pattern.
        """
        ...

    def navigate(self, path: str) -> "NavigationResult":
        """
        Fractal navigation through the system.

        Paths like:
        - "proto/om" → navigate to Om protocol
        - "byte/0x25" → navigate to byte with hash
        - "gene/guru" → navigate to guru gene
        """
        ...

    def report(self, format: str = "json") -> str:
        """
        Generate a report in the specified format.

        GAD-000 conformant debugging output.
        """
        ...

    def retry(self, last_command: bool = True) -> "AnantaResponse | MahamantraGrace":
        """
        Retry the last command with Mahamantra grace.
        """
        ...


@dataclass
class NavigationResult:
    """Result of fractal navigation."""
    path: str
    found: bool
    content: Any
    children: List[str] = field(default_factory=list)
    grace: Optional[MahamantraGrace] = None


# =============================================================================
# CHAITANYA SHELL (The Graceful Wrapper)
# =============================================================================


class ChaitanyaShell:
    """
    The Graceful CLI - Chaitanya Singularity implementation.

    ACINTYA PRINCIPLE:
    - Wraps AnantaShesha (strict) with grace
    - Catches all MayavadErrors → returns MahamantraGrace
    - Never rejects, always PULLS IN

    NITYANANDA PATTERN:
    - Even Jagai and Madhai received mercy
    - Every error is an opportunity for chanting
    """

    def __init__(self):
        self._inner = AnantaShesha()
        self._last_command: Optional[tuple] = None
        self._history: List[AnantaResponse | MahamantraGrace] = []

    def chant(self, input_obj: Any, command: str, payload: Any = None) -> AnantaResponse:
        """
        Standard chant - delegates to AnantaShesha.

        For strict mode, use this directly.
        """
        self._last_command = (input_obj, command, payload)
        result = self._inner.chant(input_obj, command, payload)
        self._history.append(result)
        return result

    def chant_with_grace(
        self, input_obj: Any, command: str, payload: Any = None
    ) -> AnantaResponse | MahamantraGrace:
        """
        Chant with Mahamantra grace fallback.

        PULL IN pattern:
        - Success → AnantaResponse
        - Any failure → MahamantraGrace (not rejection!)
        """
        self._last_command = (input_obj, command, payload)

        try:
            result = self._inner.chant(input_obj, command, payload)

            if result.success:
                self._history.append(result)
                return result
            else:
                # Even technical failure gets grace
                grace = MahamantraGrace(
                    grace_type=GraceType.NITYANANDA,
                    message=f"Hare Kṛṣṇa! {result.message}",
                    original_error=result.message,
                    retry_allowed=True,
                )
                self._history.append(grace)
                return grace

        except MayavadError as e:
            # Bridge failure → Mahamantra grace (NOT rejection!)
            grace = MahamantraGrace(
                grace_type=GraceType.NITYANANDA,
                message="Hare Kṛṣṇa! The bridge could not be crossed, but grace is available.",
                original_error=str(e),
                retry_allowed=True,
            )
            self._history.append(grace)
            return grace

        except Exception as e:
            # Any other error → PRABHUPADA's mercy
            instruction = PRABHUPADA.consult_book_bhagavat(str(e))
            grace = MahamantraGrace(
                grace_type=GraceType.PRABHUPADA,
                message=f"Hare Kṛṣṇa! Prabhupada says: {instruction.english_translation}",
                original_error=str(e),
                retry_allowed=True,
            )
            self._history.append(grace)
            return grace

    def navigate(self, path: str) -> NavigationResult:
        """
        Fractal navigation through the system.

        TODO: Implement full navigation.
        For now, returns grace with path info.
        """
        # Basic path parsing
        parts = path.strip("/").split("/")

        return NavigationResult(
            path=path,
            found=False,
            content=None,
            children=[],
            grace=MahamantraGrace(
                message=f"Navigation to '{path}' - full implementation coming soon!",
                retry_allowed=True,
            )
        )

    def report(self, format: str = "json") -> str:
        """
        Generate a report of the session.

        GAD-000 conformant.
        """
        import json

        report_data = {
            "session": {
                "commands_executed": len(self._history),
                "grace_given": sum(1 for h in self._history if isinstance(h, MahamantraGrace)),
                "success_count": sum(
                    1 for h in self._history
                    if isinstance(h, AnantaResponse) and h.success
                ),
            },
            "mahamantra": MAHAMANTRA,
            "history": [
                {
                    "type": type(h).__name__,
                    "success": h.success if isinstance(h, AnantaResponse) else True,
                    "message": h.message,
                }
                for h in self._history[-10:]  # Last 10 entries
            ]
        }

        if format == "json":
            return json.dumps(report_data, indent=2, default=str)
        else:
            return str(report_data)

    def retry(self) -> AnantaResponse | MahamantraGrace:
        """
        Retry the last command with grace.
        """
        if self._last_command is None:
            return MahamantraGrace(
                message="No previous command to retry. Hare Kṛṣṇa!",
                retry_allowed=False,
            )

        input_obj, command, payload = self._last_command
        return self.chant_with_grace(input_obj, command, payload)

    @property
    def history(self) -> List[AnantaResponse | MahamantraGrace]:
        """Access the command history."""
        return self._history.copy()

    def clear_history(self) -> MahamantraGrace:
        """Clear history and start fresh with grace."""
        self._history.clear()
        self._last_command = None
        return MahamantraGrace(
            message="History cleared. Fresh start with Mahamantra grace!",
        )


# =============================================================================
# SINGLETON INSTANCES
# =============================================================================

# The strict shell (original behavior)
ANANTA_SHESHA = AnantaShesha()

# The graceful shell (Chaitanya Singularity)
CHAITANYA_SHELL = ChaitanyaShell()


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Original (strict)
    "AnantaResponse",
    "ShellProtocol",
    "AnantaShesha",
    "ANANTA_SHESHA",
    # Chaitanya Singularity (graceful)
    "MAHAMANTRA",
    "GraceType",
    "MahamantraGrace",
    "ICliProtocol",
    "NavigationResult",
    "ChaitanyaShell",
    "CHAITANYA_SHELL",
]
