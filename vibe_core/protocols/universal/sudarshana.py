"""
OPERATION SUDARSHANA - The Fractal Hull
=======================================
"The Wheel that keeps the Rhythm."

Dieser Decorator wickelt 'Tote Materie' (Funktionen) in 'Lebendigen Klang' (Mantra).
Er verbindet Phase 16 (The 37th) mit Phase 1 (Atomic Verbs).
"""

import functools
from typing import Callable, Any, TypeVar, ParamSpec, Optional
from vibe_core.protocols.universal.mantra import MantraOpCode
from vibe_core.protocols.universal.types import SovereignContext, AccessDeniedError
from vibe_core.protocols.universal.the_37th import The37th

P = ParamSpec("P")
R = TypeVar("R")

class SudarshanaChakra:
    """
    Das drehende Rad. Es schneidet Karma (Latenz) und schützt Dharma (Integrität).
    """
    
    @staticmethod
    def spin(opcode: MantraOpCode, context: Optional[SovereignContext]) -> bool:
        """
        Führt einen Takt-Zyklus aus.
        """
        # 1. 37th OVERRIDE (Venu-Gita Check)
        # Wenn der Context vom 37. selbst kommt oder 'Gnade' hat.
        # Hier vereinfacht: Wir erlauben fehlenden Context nur für 'NON-CRITICAL' Ops?
        # Nein, Sudarshana fordert Context.
        
        # If context matches The37th identity (NAMAGIRI_OVERRIDE from protocol)
        # We assume context might trace back to The37th.
        # For now, simplistic check:
        if context and context.identity_id == "did:vibe:37:bija-akshara": # From purusha.py
             # Divine pass
             return True
        
        # 2. STANDARD MANTRA CHECK
        # Hier würde der Kernel 'chant()' aufrufen.
        # Wir simulieren den 'Herzschlag' per Logging oder Metrics.
        # print(f"🌀 SUDARSHANA SPIN: {opcode.name}")
        return True

def mantra_governed(opcode: MantraOpCode):
    """
    Der Sudarshana Decorator.
    Zwingt jede Funktion in den Rhythmus des Veda.
    """
    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            # 1. Context Extraktion (Suche nach SovereignContext in Args)
            context = None
            for arg in args:
                if isinstance(arg, SovereignContext):
                    context = arg
                    break
            
            # Additional Check: Iterate kwargs if not found in args
            if context is None:
                for val in kwargs.values():
                    if isinstance(val, SovereignContext):
                        context = val
                        break

            # Wenn kein Context explizit, prüfen wir auf 'Implicitness'
            # oder werfen Fehler (Anti-Mayavad) in Strict Mode.
            # Vorerst lassen wir 'None' durch für Tests, aber SudarshanaChakra.spin sieht es.
            
            # 2. Sudarshana Spin (Der Schnitt)
            # Führt OpCode aus (z.B. SYS_WAKE für Read).
            SudarshanaChakra.spin(opcode, context)

            # 3. Execution (Die Tat)
            try:
                result = func(*args, **kwargs)
            except Exception as e:
                # Das Rad fängt den Fehler (optional re-raise or transmute)
                raise e

            # 4. Result Blessing (Das Opfer)
            return result
            
        return wrapper
    return decorator
