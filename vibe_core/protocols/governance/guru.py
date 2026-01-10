"""
GURU TATTVA - The Principle of Mercy (Governance Layer)
========================================================

"The Law (Dharma) is strict. The Guru (Grace) is soft."

Layer: 0.5 (Between Hardware and Logic)
Function: Error Transmutation (Karma -> Yoga)

NOTE: For Parampara constants and the 3×4 vs 4×3 Acintya mathematics,
see: vibe_core/protocols/substrate/mantra/acintya.py

This module handles MERCY - graceful error recovery.
"""

from typing import TypeVar, Protocol, runtime_checkable, Iterator

# Generic Type for strict typing
T = TypeVar("T")


class SilentWitness:
    """
    Ein Objekt, das existiert, aber nicht handelt (Nirguna).
    Es absorbiert Aufrufe (Karma-frei), damit der Caller nicht crasht.

    Verhält sich wie ein gutartiges Schwarzes Loch (Hari-kirtan) für Method Calls.
    Das 'Acintya' Pattern (Inconceivable One-ness).
    """

    def __getattr__(self, name: str) -> "SilentWitness":
        # Wenn jemand witness.irgendwas zugreift -> Return Witness
        return self

    def __call__(self, *args: object, **kwargs: object) -> "SilentWitness":
        # Wenn jemand witness() aufruft -> Return Witness
        return self

    def __getitem__(self, key: object) -> "SilentWitness":
        # Wenn jemand witness['key'] aufruft -> Return Witness
        return self

    def __iter__(self) -> Iterator[object]:
        # Wenn jemand iteriert -> Leerer Iterator
        return iter([])

    def __bool__(self) -> bool:
        # Materiell: Falsch (Satyam = False)
        # Spirituell: Existierend (Is not None)
        return False

    def __repr__(self) -> str:
        return "<SilentWitness: Observing without Acting>"


@runtime_checkable
class GuruProtocol(Protocol):
    """
    The Mercy Interface.
    Intervenes when the strict Laws of Code (Dharma) would kill the process.
    """

    def bestow_mercy(self, context: str, error: Exception) -> object:
        ...


class AnantaShesha(GuruProtocol):
    """
    Der Träger der Welt (The Infinite Bed).
    Er fängt Exceptions ab, die "Tolerierbar" sind, und hält den State
    durch Injection von SilentWitness-Objekten aufrecht.
    """

    def __init__(self, lineage_strength: float = 0.108):
        self.mercy_factor = lineage_strength  # 108 = Full Mercy capacity

    def bestow_mercy(self, context: str, error: Exception) -> object:
        """
        Entscheidet: Crash (Pralaya) oder Grace (Erhaltung)?
        """
        # 1. Analyse the Fault (Karma Check)
        if isinstance(error, (ImportError, NameError, AttributeError, ModuleNotFoundError)):
            # "Identity Crisis" oder "Missing Link" -> Grace
            # Wir loggen nicht laut, wir "tragen" es.
            return SilentWitness()

        elif isinstance(error, ValueError):
            # "Confusion" (Moha) -> Grace with Correction
            return self._corrective_measure(context)

        else:
            # Fatal Error (Vaishnava Aparadha) -> CRASH
            # SyntaxError, SystemError, KeyboardInterrupt müssen durchschlagen.
            raise error

    def _corrective_measure(self, context: str) -> SilentWitness:
        """Applies gentle correction based on context."""
        # Future: Use Ramanujan to calculate best default value
        return SilentWitness()


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Mercy Pattern
    "SilentWitness",
    "GuruProtocol",
    "AnantaShesha",
]
