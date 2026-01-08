"""
YAMARAJA PROTOCOL - The Lord of Justice (Governance Gate).

"Identity Crisis Ends Here."

Yamaraja ist der Gatekeeper. Er entscheidet, wer exekutieren darf.
Er ersetzt 'GovernanceGate' mit einer Tattva-basierten Logik.

GRACE-PLUS ROUTE:
Wenn das Urteil 'DENY' ist, prüft Yamaraja auf 'Ajamila-Klausel':
Hat der User den Heiligen Namen (Mantra) gerufen? Wenn ja -> Access Granted (mit Karma-Kosten).
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any

from .dharma import DharmaVerdict, UniversalDharma
from .prabhupada import PRABHUPADA
from .types import SovereignContext, TranscendentalQuality


class Verdict(str, Enum):
    ALLOW = "allow"  # Vaikuntha (Freier Durchgang)
    DENY = "deny"  # Naraka (Blockiert)
    ATONE = "atone"  # Prayascitta (Erlaubt, aber mit Buße/Log)
    ELEVATED = "elevated"  # Grace (Spezialzugriff durch Krishna)


@dataclass
class Judgment:
    verdict: Verdict
    reason: str
    karma_cost: float


class YamarajaGate:
    """
    Die Implementation des Governance Gate.
    """

    def __init__(self):
        self.dharma = UniversalDharma()
        # Dangerous Operations (Die Sünden)
        self.ugra_karma = {"delete", "destroy", "kill", "wipe", "narasimha"}

    def judge_action(self, context: SovereignContext, command: str, payload: Any) -> Judgment:
        """
        Das Jüngste Gericht für jeden Command call.
        """
        # 1. SAUCAM CHECK (Identity)
        cleanliness = self.dharma.check_saucam(context)
        if not cleanliness.is_dharmic:
            return Judgment(Verdict.DENY, cleanliness.pillar_violated or "Dirty", 1.0)

        # 2. UGRA KARMA CHECK (Dangerous Ops)
        is_dangerous = any(sin in command.lower() for sin in self.ugra_karma)

        # 3. TATTVA CHECK (Permission Level)
        # Wir nutzen die 64 Qualitäten aus types.py
        # Krishna-Tattva (61-64) darf alles.
        # Jiva-Tattva (1-50) darf kein Ugra-Karma ohne Erlaubnis.

        user_level = context.tattva_level

        if is_dangerous:
            # Nur Vishnu/Krishna Tattva oder Admin darf zerstören
            if user_level < TranscendentalQuality.INCONCEIVABLE_POTENCY:  # < 56
                # GRACE-PLUS ROUTE (Ajamila Protocol)
                # Wir prüfen, ob Prabhupada (Vani) eine Ausnahme erlaubt.
                instruction = PRABHUPADA.consult_book_bhagavat(command)

                if instruction.id == "BG_18.66":  # Surrender command
                    return Judgment(Verdict.ELEVATED, "Surrender Accepted via Grace", 0.0)

                return Judgment(Verdict.DENY, "Jiva cannot perform Ugra Karma", 0.5)

        # 4. DAYA CHECK (Input Safety)
        mercy = self.dharma.check_daya(payload)
        if not mercy.is_dharmic:
            # Wir erlauben es vielleicht im 'ATONE' Mode (Logging)
            return Judgment(Verdict.ATONE, f"Risky Input: {mercy.pillar_violated}", mercy.karma_cost)

        return Judgment(Verdict.ALLOW, "Dharmic Action", 0.0)
