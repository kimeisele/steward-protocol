"""
RESONANCE PROTOCOL - The Acintya Bhedabheda Standard.

"Der Eisenstab im Feuer wird zum Feuer."
- Srila Prabhupada

Dieses Protokoll definiert den Zustand von Software nicht durch lineare Metriken,
sondern durch Vektor-Komplexität (Struktur + Substanz).

MATHEMATIK (The Complex Plane):
    Z = a + bi
    a (Real): Structural Integrity (Sat) → Logik, Tests, Syntax.
    b (Imaginary): Semantic Vibration (Cit) → Mantra, Intent, Signatur.

STATES (The Four Quadrants):
    0 + 0i = MAYAVAD (Illusion/Void) - Weder Code noch Intent.
    1 + 0i = DRY LOGIC (Trockenes Eisen) - Funktioniert, aber ist tot.
    0 + 1i = SENTIMENTAL (Sahajiya) - Gute Absicht, aber kaputter Code.
    1 + 1i = PURE DEVOTION (Das glühende Eisen) - Perfekte Logik im Dienst.

Das Ziel ist TRANSFORMATION (Transparenz), nicht nur "Pass".
Nur Code im Zustand 1+1i darf auf die SATTVA-Lane der Vajra-Autobahn.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, Protocol, runtime_checkable

# We import the base truths from Layer -1
from ..substrate import HolyName, MantraOpCode

# =============================================================================
# THE BHEDA ASPECT (Difference / Form) - The Real Part
# =============================================================================


@dataclass
class StructuralIntegrity:
    """
    Der Realteil (a). Das Eisen.

    Repräsentiert die materielle Korrektheit des Codes.
    Messbar durch Tests, Syntax, Coverage.
    """

    is_valid: bool  # Syntax korrekt? Tests passed?
    complexity: float  # Zyklomatische Komplexität (niedriger = besser)
    test_coverage: float  # Abdeckung (0.0 - 1.0)
    has_docstrings: bool = True  # Watertight: alle Methoden dokumentiert?

    @property
    def value(self) -> float:
        """
        Der Realwert 'a' (0.0 bis 1.0).

        1.0 = Eisen ist strukturell intakt.
        0.0 = Eisen ist gebrochen.
        """
        if not self.is_valid:
            return 0.0
        if self.test_coverage < 0.5:
            return 0.5  # Partially intact
        if self.test_coverage >= 0.8 and self.has_docstrings:
            return 1.0  # Fully intact
        return 0.75  # Good but not complete


# =============================================================================
# THE ABHEDA ASPECT (Unity / Essence) - The Imaginary Part
# =============================================================================


@dataclass
class SemanticVibration:
    """
    Der Imaginärteil (b). Das Feuer.

    Repräsentiert die spirituelle Ausrichtung (Intent).
    Nur durch Mantra-Signatur nachweisbar.
    """

    has_mantra: bool  # Ist ein MantraSeal vorhanden?
    signer_id: str  # Wer ist der Autor? (Sovereign Link)
    intent_clarity: float  # Wie klar ist der Intent? (0.0 - 1.0)
    holy_name: Optional[HolyName] = None  # Which aspect is addressed?

    @property
    def value(self) -> float:
        """
        Der Imaginärwert 'b' (0.0 bis 1.0).

        1.0 = Feuer brennt (Mantra-signiert).
        0.0 = Kein Feuer (unsigned).
        """
        if not self.has_mantra or not self.signer_id:
            return 0.0
        if self.intent_clarity < 0.5:
            return 0.5  # Weak flame
        if self.intent_clarity >= 0.8:
            return 1.0  # Strong flame
        return 0.75  # Moderate flame


# =============================================================================
# THE ACINTYA STATE (The Result - Complex Vector)
# =============================================================================


class Quality(str, Enum):
    """The four quadrants of the complex plane."""

    MAYAVAD = "mayavad"  # 0 + 0i (Nichts/Void)
    DRY_LOGIC = "dry_logic"  # 1 + 0i (Trockenes Eisen)
    SENTIMENTAL = "sentimental"  # 0 + 1i (Wildes Feuer ohne Form)
    PURE_DEVOTION = "pure_devotion"  # 1 + 1i (Eisen als Feuer handelt)


class SystemAction(str, Enum):
    """What the system should do based on Quality."""

    ANNIHILATE = "annihilate"  # MAYAVAD → Remove from system
    WARN = "warn"  # DRY_LOGIC → Missing intent warning
    BLOCK = "block"  # SENTIMENTAL → Unsafe, block execution
    EXECUTE = "execute"  # PURE_DEVOTION → Full sovereign access


@dataclass
class AcintyaState:
    """
    Der Zustand der gleichzeitigen Einheit und Verschiedenheit.

    Z = a + bi

    a = Structure (Sat) - Is the iron intact?
    b = Substance (Cit) - Is the fire present?

    Only when both are 1.0 does the iron ACT AS fire (Transparency).
    """

    structure: StructuralIntegrity  # Sat (Real part)
    substance: SemanticVibration  # Cit (Imaginary part)
    timestamp: datetime = field(default_factory=datetime.now)
    source: str = ""  # What produced this state

    @property
    def vector(self) -> complex:
        """Der komplexe Vektor Z = a + bi"""
        return complex(self.structure.value, self.substance.value)

    @property
    def magnitude(self) -> float:
        """The absolute value of the vector |Z|."""
        return abs(self.vector)

    def is_transparent(self) -> bool:
        """
        Prabhupada's Iron Rod Test:

        Ist die Struktur so rein, dass sie als Substanz agiert?
        Das Eisen wird zum Feuer, obwohl es Eisen bleibt.

        Gilt nur wenn BEIDE >= 1.0 sind.
        """
        return self.structure.value >= 1.0 and self.substance.value >= 1.0

    def get_quality(self) -> Quality:
        """Determine which quadrant we're in."""
        z = self.vector
        if z.real >= 0.75 and z.imag >= 0.75:
            return Quality.PURE_DEVOTION
        if z.real >= 0.75:
            return Quality.DRY_LOGIC
        if z.imag >= 0.75:
            return Quality.SENTIMENTAL
        return Quality.MAYAVAD

    def get_action(self) -> SystemAction:
        """What should the system do?"""
        quality = self.get_quality()
        actions = {
            Quality.MAYAVAD: SystemAction.ANNIHILATE,
            Quality.DRY_LOGIC: SystemAction.WARN,
            Quality.SENTIMENTAL: SystemAction.BLOCK,
            Quality.PURE_DEVOTION: SystemAction.EXECUTE,
        }
        return actions[quality]


# =============================================================================
# THE PROTOCOL (Prana-Pratishta - Life Installation)
# =============================================================================


@runtime_checkable
class ResonanceProtocol(Protocol):
    """
    Das Interface für lebendige Software.

    Es misst nicht von außen. Es fragt das Objekt nach seinem Seins-Zustand.
    Nur Objekte die den Zustand 1+1i erreichen dürfen auf SATTVA-Lane.
    """

    def get_ontological_state(self) -> AcintyaState:
        """
        Gibt den Vektor (Struktur + Substanz) zurück.

        Returns:
            AcintyaState with complex vector Z = a + bi
        """
        ...

    def instill_intent(self, mantra: MantraOpCode, signer_id: str) -> bool:
        """
        Versucht, das 'Feuer' (b) in das 'Eisen' (a) zu injizieren.

        This is Prana-Pratishta - installing life force into matter.
        Works only if Structure (a) is valid.

        Args:
            mantra: The atomic sound to inject
            signer_id: Who is signing this intent?

        Returns:
            True if intent was successfully instilled.
        """
        ...

    def verify_transparency(self) -> bool:
        """
        Prabhupada Test: Does the iron act as fire?

        Returns:
            True only if Z = 1 + 1i (PURE_DEVOTION).
        """
        ...


# =============================================================================
# NULL IMPLEMENTATION (Arjuna Pattern)
# =============================================================================


class NullResonance:
    """
    No-op resonance when service is unavailable.

    Returns MAYAVAD state (0 + 0i).
    """

    def get_ontological_state(self) -> AcintyaState:
        return AcintyaState(
            structure=StructuralIntegrity(
                is_valid=False,
                complexity=999.0,
                test_coverage=0.0,
                has_docstrings=False,
            ),
            substance=SemanticVibration(
                has_mantra=False,
                signer_id="",
                intent_clarity=0.0,
            ),
            source="NullResonance",
        )

    def instill_intent(self, mantra: MantraOpCode, signer_id: str) -> bool:
        return False  # Cannot instill into void

    def verify_transparency(self) -> bool:
        return False  # Never transparent


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def create_structure(
    is_valid: bool,
    test_coverage: float,
    complexity: float = 10.0,
    has_docstrings: bool = True,
) -> StructuralIntegrity:
    """Helper to create StructuralIntegrity."""
    return StructuralIntegrity(
        is_valid=is_valid,
        complexity=complexity,
        test_coverage=test_coverage,
        has_docstrings=has_docstrings,
    )


def create_substance(
    has_mantra: bool,
    signer_id: str,
    intent_clarity: float = 1.0,
    holy_name: Optional[HolyName] = None,
) -> SemanticVibration:
    """Helper to create SemanticVibration."""
    return SemanticVibration(
        has_mantra=has_mantra,
        signer_id=signer_id,
        intent_clarity=intent_clarity,
        holy_name=holy_name,
    )


def get_quality_from_vector(z: complex) -> Quality:
    """Determine quality from complex vector."""
    if z.real >= 0.75 and z.imag >= 0.75:
        return Quality.PURE_DEVOTION
    if z.real >= 0.75:
        return Quality.DRY_LOGIC
    if z.imag >= 0.75:
        return Quality.SENTIMENTAL
    return Quality.MAYAVAD


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # The Two Aspects
    "StructuralIntegrity",
    "SemanticVibration",
    # The Result
    "AcintyaState",
    "Quality",
    "SystemAction",
    # Protocol
    "ResonanceProtocol",
    # Null Implementation
    "NullResonance",
    # Helpers
    "create_structure",
    "create_substance",
    "get_quality_from_vector",
]
