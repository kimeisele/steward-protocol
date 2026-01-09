"""
YAMARAJA PROTOCOL - The Lord of Justice (Governance Gate).

"Identity Crisis Ends Here."

Refactored for Hardness:
- Strict Type Hints
- Integration of GuruProtocol for Resilience
- No 'Any' in core logic
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional, Set

# Absolute Imports required for Hardness
from vibe_core.protocols.governance.guru import AnantaShesha
from vibe_core.protocols.types import SovereignContext, TranscendentalQuality
# Assuming Dharma is available (Mock/Protocol needed if not provided)
from vibe_core.protocols.dharma import UniversalDharma, DharmaVerdict 

class Verdict(str, Enum):
    ALLOW = "allow"      # Vaikuntha (Freier Durchgang)
    DENY = "deny"        # Naraka (Blockiert)
    ATONE = "atone"      # Prayascitta (Erlaubt, aber mit Buße/Log)
    ELEVATED = "elevated"# Grace (Spezialzugriff durch Krishna)


@dataclass(frozen=True)
class Judgment:
    verdict: Verdict
    reason: str
    karma_cost: float


class YamarajaGate:
    """
    Die Implementation des Governance Gate.
    Härtet die Zugriffskontrolle durch Ugra-Karma Checks.
    """

    def __init__(self):
        self.dharma = UniversalDharma()
        self.shesha = AnantaShesha() # The Mercy Layer
        # Dangerous Operations (Die Sünden) - Hardcoded Set
        self.ugra_karma: Set[str] = {"delete", "destroy", "kill", "wipe", "narasimha"}

    def judge_action(self, context: SovereignContext, command: str, payload: Any) -> Judgment:
        """
        Das Jüngste Gericht für jeden Command call.
        """
        try:
            return self._execute_judgment(context, command, payload)
        except Exception as e:
            # Wenn Yamaraja selbst stolpert (interner Fehler),
            # fängt Ananta Shesha ihn auf. Aber Yamaraja darf nicht 'Silent' sein.
            # Ein ausgefallener Richter bedeutet: Access Denied (Sicherheit).
            self.shesha.bestow_mercy("yamaraja_critical_fail", e)
            return Judgment(Verdict.DENY, "System Turmoil (Yamaraja Unavailable)", 1.0)

    def _execute_judgment(self, context: SovereignContext, command: str, payload: Any) -> Judgment:
        # 1. SAUCAM CHECK (Cleanliness)
        try:
            cleanliness = self.dharma.check_saucam(context)
        except Exception as e:
            # Fallback if Dharma service is down
            self.shesha.bestow_mercy("dharma_down", e)
            cleanliness = DharmaVerdict(is_dharmic=False, pillar_violated="Unknown")

        is_dirty = not cleanliness.is_dharmic

        # 2. UGRA KARMA CHECK (Dangerous Ops)
        # Lowercase normalization for strict string matching
        cmd_norm = command.lower()
        is_dangerous = any(sin in cmd_norm for sin in self.ugra_karma)

        # 3. TATTVA CHECK (Permission Level)
        # Accessing typed attribute
        user_level = context.tattva_level

        if is_dangerous:
            # Nur Vishnu/Krishna Tattva oder Admin darf zerstören
            # INCONCEIVABLE_POTENCY = 56 (Strict Check)
            if user_level < TranscendentalQuality.INCONCEIVABLE_POTENCY:
                
                # GRACE-PLUS ROUTE (Ajamila Protocol)
                try:
                    from vibe_core.prabhupada import PRABHUPADA
                    instruction = PRABHUPADA.consult_book_bhagavat(command)
                    
                    if instruction.id == "BG_18.66":  # Surrender command
                        return Judgment(Verdict.ELEVATED, "Surrender Accepted via Grace", 0.0)
                except ImportError as e:
                    # Prabhupada Modul fehlt -> Kein Grace möglich
                    self.shesha.bestow_mercy("prabhupada_missing", e)

                return Judgment(Verdict.DENY, "Jiva cannot perform Ugra Karma", 0.5)

        # 4. SAFE ACTION HANDLING
        if is_dirty:
            # Safe but Dirty = ATONE
            msg = cleanliness.pillar_violated or "Dirty Context"
            return Judgment(Verdict.ATONE, msg, 0.1)

        # 5. DAYA CHECK (Input Safety)
        try:
            mercy = self.dharma.check_daya(payload)
            if not mercy.is_dharmic:
                return Judgment(Verdict.ATONE, f"Risky Input: {mercy.pillar_violated}", mercy.karma_cost)
        except AttributeError:
             # Payload mismatch -> Fail safe
             return Judgment(Verdict.DENY, "Malformed Payload", 0.0)

        return Judgment(Verdict.ALLOW, "Dharmic Action", 0.0)
