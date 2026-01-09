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
        # 1. SAUCAM CHECK (Flag only, don't return yet)
        cleanliness = self.dharma.check_saucam(context)
        is_dirty = not cleanliness.is_dharmic

        # 2. UGRA KARMA CHECK (Dangerous Ops)
        is_dangerous = any(sin in command.lower() for sin in self.ugra_karma)

        # 3. TATTVA CHECK (Permission Level)
        user_level = context.tattva_level

        if is_dangerous:
            # Nur Vishnu/Krishna Tattva oder Admin darf zerstören
            if user_level < TranscendentalQuality.INCONCEIVABLE_POTENCY:  # < 56
                # GRACE-PLUS ROUTE (Ajamila Protocol)
                instruction = PRABHUPADA.consult_book_bhagavat(command)

                if instruction.id == "BG_18.66":  # Surrender command
                    # Grace overrides Dirtiness!
                    return Judgment(Verdict.ELEVATED, "Surrender Accepted via Grace", 0.0)

                return Judgment(Verdict.DENY, "Jiva cannot perform Ugra Karma", 0.5)

        # 4. SAFE ACTION HANDLING
        if is_dirty:
            # MERCY FOR THE IGNORANT (Legacy)
            # Safe but Dirty = ATONE
            return Judgment(Verdict.ATONE, cleanliness.pillar_violated or "Dirty", 0.1)

        # 5. DAYA CHECK (Input Safety)
        mercy = self.dharma.check_daya(payload)
        if not mercy.is_dharmic:
            return Judgment(Verdict.ATONE, f"Risky Input: {mercy.pillar_violated}", mercy.karma_cost)

        return Judgment(Verdict.ALLOW, "Dharmic Action", 0.0)


# ============================================================================
# PHASE 12: THE PERFORMANCE CONTRACT (STRICT ENFORCEMENT)
# ============================================================================

import functools
import time
from typing import Callable, ParamSpec, TypeVar, cast

# STRICT TYPING: Keine 'Any' Faulheit mehr.
# P = Die Parameter der Funktion (args, kwargs)
# R = Der Rückgabetyp der Funktion
P = ParamSpec("P")
R = TypeVar("R")

class YamarajaProtocol:
    """
    The Performance Judge.
    Enforces the 'Contract of Singularity'.
    """
    MIN_RESONANCE_THRESHOLD = 1.08  # The Golden Ratio of Growth

    @staticmethod
    def evaluate(name: str, baseline: float, current: float) -> Judgment:
        """
        Judge the performance.
        """
        if baseline <= 0:
            return Judgment(Verdict.ALLOW, "Initial Seed Accepted", 0.0)

        # Calculate the expansion ratio
        growth = current / baseline

        if growth >= YamarajaProtocol.MIN_RESONANCE_THRESHOLD:
            return Judgment(
                Verdict.ALLOW, 
                f"VALID: {name} is expanding (Growth: {growth:.2f}x).",
                0.0
            )
        else:
            return Judgment(
                Verdict.DENY, 
                f"INVALID: {name} is stagnating (Growth: {growth:.2f}x < 1.08x). Terminating.",
                1.0
            )

def secure_contract(baseline_metric: float) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """
    Der Vertrag (The Seal).
    Wraps a function to ensure it adheres to Yamaraja's Contract.
    Strictly Typed using ParamSpec.
    """
    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            start = time.perf_counter()
            
            # Ausführung (Type Safe)
            result = func(*args, **kwargs)
            
            end = time.perf_counter()
            duration = end - start
            ops_per_sec = 1.0 / duration if duration > 0 else float('inf')
            
            # The Judgment
            judgment = YamarajaProtocol.evaluate(func.__qualname__, baseline_metric, ops_per_sec)
            
            if judgment.verdict == Verdict.DENY:
                # STRICT ENFORCEMENT - The 'Hardening'
                raise SystemError(f"YAMARAJA PROTOCOL VIOLATION: {judgment.reason}")
            
            return result
        return wrapper
    return decorator
