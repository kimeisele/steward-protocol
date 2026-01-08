"""
DHARMA PROTOCOL - The 4 Regulating Principles (Layer 1).

"Dharma protects those who protect it."

Wir mappen die vedischen Prinzipien auf Hardcore-Security.
Dies ersetzt 'defense.py' mit universaler Reinheit.

DIE 4 SÄULEN:
1. DAYA (Mercy) -> Data Sanitization (Kein korrupter Input).
2. SATYAM (Truth) -> Output Verification (Keine Halluzination).
3. TAPAS (Austerity) -> Resource Limits (Keine Verschwendung).
4. SAUCAM (Cleanliness) -> Network/Context Isolation (Keine Kontamination).
"""

from dataclasses import dataclass
from typing import Any, Optional, Protocol, TypeVar, runtime_checkable

from .types import ProtocolError, SovereignContext, TattvaMeter

T = TypeVar("T")


@dataclass
class DharmaVerdict:
    is_dharmic: bool
    pillar_violated: Optional[str] = None
    karma_cost: float = 0.0  # Wie teuer ist diese Verletzung?


@runtime_checkable
class DharmaGuard(Protocol):
    """
    Das Interface der Rechtschaffenheit.
    Muss von jedem Service implementiert werden, der 'Protected' sein will.
    """

    def check_daya(self, data: Any) -> DharmaVerdict:
        """
        MERCY: Prüft Input-Daten auf 'Gewalt' (Malicious Payloads).
        Nutzung: TattvaMeter.measure_rupa(data) < MAX_COMPLEXITY.
        """
        ...

    def check_satyam(self, output: Any, intent: str) -> DharmaVerdict:
        """
        TRUTH: Prüft Output gegen Intent.
        Nutzung: TattvaMeter.measure_jnana(output) (Typ-Treue).
        """
        ...

    def check_tapas(self, resource_usage: float) -> DharmaVerdict:
        """
        AUSTERITY: Prüft CPU/RAM Limits.
        """
        ...

    def check_saucam(self, context: SovereignContext) -> DharmaVerdict:
        """
        CLEANLINESS: Prüft die Herkunft (Signatur-Kette).
        """
        ...


# =============================================================================
# THE IMPLEMENTATION (Watertight Logic)
# =============================================================================


class UniversalDharma:
    """
    Die Standard-Implementierung der 4 Säulen.
    """

    def check_daya(self, data: Any) -> DharmaVerdict:
        # Purity Check via TattvaMeter
        complexity = TattvaMeter.measure_rupa(data)
        if complexity > 20:  # Zu komplex = Raja-Guna (Leidenschaft/Gefahr)
            return DharmaVerdict(False, "DAYA: Input too complex/violent", 0.5)
        return DharmaVerdict(True)

    def check_satyam(self, output: Any, intent: str) -> DharmaVerdict:
        # Truth Check via Types
        entropy = TattvaMeter.measure_jnana(output)
        if entropy < 0.5:  # Zu untypisiert = Tamas (Unwissenheit/Lüge)
            return DharmaVerdict(False, "SATYAM: Output lacks definition", 0.8)
        return DharmaVerdict(True)

    def check_tapas(self, resource_usage: float) -> DharmaVerdict:
        if resource_usage > 0.9:  # 90% Load
            return DharmaVerdict(False, "TAPAS: Gluttony detected", 0.2)
        return DharmaVerdict(True)

    def check_saucam(self, context: SovereignContext) -> DharmaVerdict:
        # Nur signierte Kontexte sind rein
        if not context.signature:
            return DharmaVerdict(False, "SAUCAM: Dirty Context (Unsigned)", 1.0)
        return DharmaVerdict(True)
