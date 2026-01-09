"""
YAMARAJA PROTOCOL - The Lord of Justice.

Scope:
1. GovernanceGate (Permissions) - "Who are you?"
2. SecureContract (Performance) - "Are you fast enough?"

HARDENING LEVEL: GERMAN (Strict Types, No Mercy)
"""

import time
import functools
from dataclasses import dataclass
from enum import Enum
from typing import TypeVar, ParamSpec, Callable, cast, Set, Optional, Dict, Any

# Protocol Imports
# Using placeholder imports or assuming they exist/will be created if missing
# In "Universal" folder, we had imports pointing to .dharma etc.
# Ideally we reuse universal or move them. For now, assuming standard path or relative.
# But 'vibe_core.protocols.dharma' implies a package structure. 
# We'll use relative imports assuming we are in vibe_core.protocols.governance

# from vibe_core.protocols.universal.dharma import UniversalDharma, DharmaVerdict
from vibe_core.protocols.universal.types import SovereignContext, TranscendentalQuality

# --- STRICT TYPING PRIMITIVES ---
P = ParamSpec("P")
R = TypeVar("R")

class Verdict(str, Enum):
    ALLOW = "allow"      # Vaikuntha
    DENY = "deny"        # Naraka
    ATONE = "atone"      # Prayascitta
    ELEVATED = "elevated"# Grace

@dataclass(frozen=True)
class Judgment:
    verdict: Verdict
    reason: str
    karma_cost: float

# --- PART 1: THE PERFORMANCE JUDGE (The Missing Link) ---

class YamarajaPhysics:
    """
    Enforces the Laws of Thermodynamics & Singularity.
    """
    MIN_RESONANCE_THRESHOLD = 1.08  # The Golden Ratio of Growth

    @staticmethod
    def measure_kriya(name: str, baseline: float, current: float) -> Judgment:
        if baseline <= 0: 
            return Judgment(Verdict.ALLOW, "Initial Seed", 0.0)

        growth = current / baseline

        if growth >= YamarajaPhysics.MIN_RESONANCE_THRESHOLD:
            return Judgment(Verdict.ALLOW, f"EXPANSION: {growth:.2f}x", 0.0)
        else:
            return Judgment(Verdict.DENY, f"STAGNATION: {growth:.2f}x < 1.08x", 1.0)

# Backward Compatibility Alias (The User's Brain expects this name)
YamarajaProtocol = YamarajaPhysics

def secure_contract(baseline_metric: float) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """
    The Yamaraja Seal.
    Wraps a function. If it performs linearly (slowly), it is terminated.
    
    Strict Typing: Preserves the signature P -> R of the wrapped function.
    """
    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            # 1. Start Clock
            start = time.perf_counter()
            
            # 2. Execute (Type Safe)
            try:
                result = func(*args, **kwargs)
            except Exception as e:
                # Code that crashes is inherently Tamasic
                raise SystemError(f"YAMARAJA: Process {func.__qualname__} died violently: {e}")

            # 3. Stop Clock & Judge
            duration = time.perf_counter() - start
            
            # --- INTELLIGENT OPS CALCULATION ---
            # If the result object has its own 'ops_per_sec', we trust it (Self-Reporting).
            # Otherwise, we assume 1 Call = 1 Op.
            ops = 0.0
            if hasattr(result, "ops_per_sec"):
                # Trust the internal metrics (The 'Caitanya' way)
                ops = float(getattr(result, "ops_per_sec"))
            else:
                # Default observation (The 'Material' way)
                ops = (1.0 / duration) if duration > 0 else float('inf')
            
            judgment = YamarajaPhysics.measure_kriya(func.__qualname__, baseline_metric, ops)
            
            if judgment.verdict == Verdict.DENY:
                # THE DANDA (Punishment)
                raise SystemError(f"YAMARAJA VIOLATION: {judgment.reason}")
                
            return result
        return wrapper
    return decorator

# --- PART 2: THE GOVERNANCE GATE (Existing Logic) ---

class YamarajaGate:
    """
    The Governance Implementation.
    """
    def __init__(self):
        from vibe_core.protocols.universal.dharma import UniversalDharma
        self.dharma = UniversalDharma()
        # self.shesha = AnantaShesha() # Removing assuming AnantaShesha not implemented yet
        self.ugra_karma: Set[str] = {"delete", "destroy", "kill", "wipe", "narasimha"}

    def judge_action(self, context: SovereignContext, command: str, payload: Optional[Any] = None) -> Judgment:
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
                # Assuming PRABHUPADA import if needed, or simplified check
                return Judgment(Verdict.DENY, "Jiva cannot perform Ugra Karma", 0.5)

        # 4. SAFE ACTION HANDLING
        if is_dirty:
            return Judgment(Verdict.ATONE, cleanliness.pillar_violated or "Dirty", 0.1)

        # 5. DAYA CHECK (Input Safety)
        mercy = self.dharma.check_daya(payload)
        if not mercy.is_dharmic:
            return Judgment(Verdict.ATONE, f"Risky Input: {mercy.pillar_violated}", mercy.karma_cost)

        return Judgment(Verdict.ALLOW, "Dharmic Action", 0.0)
