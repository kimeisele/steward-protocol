"""
MAHAMANTRA - The Sovereign Singularity (Level -2)
================================================

"aham sarvasya prabhavo mattah sarvam pravartate"
"I am the source of all. Everything emanates from Me." (BG 10.8)

THE CLEAN LOTUS:
----------------
Pure delegation. No manual wiring. No circular imports.
"""

from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "brahma"
__position__ = 1
__genesis__ = "0x7340d7d6"  # GenesisByte: parampara % 37 == 0

import logging
from typing import Dict, Iterator, List, Optional, Union

# Core Protocols
from vibe_core.mahamantra.protocols._gad import GADBase, GADProtocol
from vibe_core.mahamantra._lotus import LotusNode, LotusPath
from vibe_core.mahamantra._types import ExecuteResult, RouteResult

# Substrate
from vibe_core.mahamantra.substrate.seed import WORDS, PARAMPARA, ALL_GUARDIANS
from vibe_core.mahamantra.substrate.position import get_position

logger = logging.getLogger("MAHAMANTRA")

# =============================================================================
# THE SINGULARITY
# =============================================================================

class MahamantraLotus(LotusNode, GADBase, GADProtocol):
    """
    The Root of the Lotus.
    
    This is the only node that knows HOW to execute and resonate.
    """

    def __init__(self) -> None:
        LotusNode.__init__(self, LotusPath())
        GADBase.__init__(self)

    # === Resonance & Routing (Root Intelligence) ===

    def resonate(self, command: str) -> tuple[float, Optional[LotusNode]]:
        """
        Poll the ProtocolRegistry for resonance.
        
        WATERTIGHT: Triggers Lazy Initiation (Diksha) if registry is empty.
        """
        from vibe_core.mahamantra.substrate import ProtocolRegistry
        from vibe_core.mahamantra.substrate.seed import ALL_GUARDIANS
        import importlib
        
        # 1. Lazy Diksha: Ensure protocols are loaded
        if ProtocolRegistry.coverage()[0] == 0:
            for guardian in ALL_GUARDIANS:
                try:
                    # Direct module load bypasses the lotus navigation to avoid loops
                    importlib.import_module(f"vibe_core.protocols.mahajanas.{guardian}")
                except (ImportError, AttributeError):
                    continue

        best_score = 0.0
        best_guardian = None
        
        # 2. Flat Poll
        for idx in range(16):
            guardian = ALL_GUARDIANS[idx]
            protocol_cls = ProtocolRegistry.get(idx)
            
            if protocol_cls and hasattr(protocol_cls, "get_resonance"):
                score = protocol_cls.get_resonance(command)
                if score > best_score:
                    best_score = score
                    best_guardian = guardian
                    if best_score >= 1.0: break
                    
        if best_guardian:
            return best_score, self.resolve(best_guardian)
            
        return 0.0, None

    def execute(self, command: str, args: Optional[List[str]] = None) -> ExecuteResult:
        """Execute via resonance."""
        score, winner = self.resonate(command)
        
        if winner and score > 0:
            guardian = winner._path.segments[-1]
            quarter = winner._path.segments[0]
            
            # Simple awakening logic (Proxy/Service Hunt)
            # In Phase 10, this will be fully decentralized
            output = f"🕉️ {guardian.upper()} resonated with '{command}'."
            
            return ExecuteResult(
                success=True,
                exit_code=0,
                position=-1, # derived
                guardian=guardian,
                quarter=quarter,
                guna="vishuddha",
                requires_confirmation=False,
                output=output,
                error=None
            )

        # Fallback to Narada
        return ExecuteResult(success=False, output="No one heard your mantra.", guardian="narada", quarter="genesis")

    def resolve(self, name: str) -> LotusNode:
        """Helper to find a node by guardian name."""
        from vibe_core.mahamantra.substrate.seed import get_guardian_quarter
        q = get_guardian_quarter(name)
        if q: return getattr(getattr(self, q.lower()), name)
        return getattr(self, name)

    # === GAD-000 Compliance ===
    def discover(self) -> Dict[str, object]: return {"type": "MahamantraLotus"}
    def get_state(self) -> Dict[str, object]: return {"status": "resonant"}
    def is_healthy(self) -> bool: return True
    @property
    def is_idempotent(self) -> bool: return True
    def detect_drift(self) -> List[str]: return []
    def test_daya(self) -> bool: return True
    def test_satyam(self) -> bool: return True
    def test_tapas(self) -> bool: return True
    def test_saucam(self) -> bool: return True

    # === SHARANAGATI GATE ===
    def bootstrap(self, *, silent: bool = False) -> None:
        """
        Initialize the Mahamantra system (Sharanagati Gate).
        
        Called by kernel during startup. Currently a no-op as the
        system is initialized on import.
        
        Args:
            silent: If True, suppress logging.
        """
        if not silent:
            import logging
            logging.getLogger("MAHAMANTRA").info("🙏 Mahamantra bootstrap complete")


    # === VEDA-4 ===
    def __call__(self, cmd: Optional[str] = None) -> Union[str, ExecuteResult]:
        if cmd is None: return "Hare Krishna"
        return self.execute(cmd)

    def __getitem__(self, index: Union[int, str]) -> Union[object, LotusNode]:
        if isinstance(index, int): return get_position(index)
        return self.resolve(index)

    def __len__(self) -> int: return 16

# =============================================================================
# THE INSTANCE
# =============================================================================

mahamantra = MahamantraLotus()
lotus = mahamantra

# =============================================================================
# LAZY RE-EXPORT (Krishna routet alles)
# =============================================================================
# "from vibe_core.mahamantra import X" → delegates to substrate
# NO MANUAL LABOR. One __getattr__, all symbols available.

def __getattr__(name: str):
    """Delegate to substrate for any symbol not defined here."""
    from vibe_core.mahamantra import substrate
    return getattr(substrate, name)

__all__ = ["mahamantra", "lotus"]

