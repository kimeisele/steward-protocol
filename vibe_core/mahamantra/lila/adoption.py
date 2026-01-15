"""
LILA ADOPTION - The Sacred Migration
====================================

"sarva-dharman parityajya..."

This module implements the Protocol Adoption Logic for the Mahamantra.
It analyzes code, determines its true nature (OpCode), and assigns it to a Mahajana.

SOURCE OF TRUTH:
- protocols._seed (Constants)
- protocols._pancha (Structure)
- protocols._sankirtan (Injection)

LOGIC EXTRACTED FROM: vibe_core/protocols/mahajanas/adoption.py (Legacy)
"""

from typing import List, Optional, Dict, TypedDict, Set
from vibe_core.mahamantra.protocols._seed import PARAMPARA, WORDS
from vibe_core.mahamantra.substrate.opcode import MantraOpCode
from vibe_core.mahamantra.substrate.wiring import get_position_by_opcode

# Heuristic Mapping (from Legacy Knowledge)
OPCODE_KEYWORDS: Dict[str, Set[str]] = {
    "SYS_WAKE": {"wake", "init", "bootstrap", "start"},
    "LOAD_ROOT": {"load", "root", "create", "inject"},
    "ALLOC_MEM": {"alloc", "memory", "buffer"},
    "INIT_THREAD": {"bind", "context"},
    "COMPILE_AST": {"assert", "verify", "validate"},
    "BIND_SYMBOL": {"resolve", "query", "lookup"},
    "TYPE_CHECK": {"garbage", "collect", "cleanup"},
    "DHARMA_TEST": {"pulse", "sync", "event"},
    "EXEC_OP": {"fetch", "resource", "get"},
    "EXTEND_CAP": {"exec", "execute", "run"},
    "STATE_SYNC": {"dharma", "rule", "policy"},
    "LEDGER_SIGN": {"commit", "log", "record"},
    "CACHE_STATE": {"cache", "store", "memoize"},
    "OPTIMIZE": {"optimize", "tune"},
    "YIELD_CPU": {"yield", "wait", "suspend"},
    "AUDIT_SEAL": {"reset", "recover", "audit"},
}

class AnalysisResult(TypedDict):
    opcode: str
    mahajana: str
    position: int
    confidence: float
    is_mayavad: bool

def analyze_source(source_code: str) -> AnalysisResult:
    """
    Analyze source code to determine its Mahamantra Identity.
    """
    source_lower = source_code.lower()
    
    # 1. Mayavad Check
    mayavad_triggers = ["i am god", "all is one", "void"]
    is_mayavad = any(t in source_lower for t in mayavad_triggers)
    
    # 2. OpCode Detection
    scores: Dict[str, int] = {}
    for op_name, keywords in OPCODE_KEYWORDS.items():
        count = sum(source_lower.count(kw) for kw in keywords)
        if count > 0:
            scores[op_name] = count
            
    best_op = "SYS_WAKE" # Default
    if scores:
        best_op = max(scores, key=scores.get)
        
    # 3. Determine Mahajana (via substrate lookup)
    try:
        opcode_enum = MantraOpCode[best_op]
        pos = get_position_by_opcode(opcode_enum)
        mahajana = pos.guardian.value
        position = pos.index
    except (KeyError, ValueError, AttributeError):
        mahajana = "prithu"
        position = 0
        
    return {
        "opcode": best_op,
        "mahajana": mahajana,
        "position": position,
        "confidence": 0.8 if scores else 0.1,
        "is_mayavad": is_mayavad
    }

# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "analyze_source",
    "AnalysisResult",
]
