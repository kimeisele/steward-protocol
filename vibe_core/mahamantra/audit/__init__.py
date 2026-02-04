"""
MAHA AUDIT AGENCY - Deep System Intelligence via RESONANCE
===========================================================

"yasya deve parā bhaktir yathā deve tathā gurau"
-- Svetasvatara Upanishad 6.23

NOT if/else binary analysis!
Uses EXISTING PRODUCTION COMPONENTS for real semantic understanding.

INTEGRATION WITH EXISTING SYSTEMS:
==================================
- project_introspection.py  → scan_codebase(), find_gaps(), verify_parampara()
- CodeScanner               → UnifiedKnowledgeGraph, imports/calls tracking
- StandardsInspectionTool   → AST rule-based analysis
- MahaCompression           → Text → Seed → Position (RESONANCE!)
- PhoneticBridge            → Varga/Sthana analysis

USAGE:
======
    from vibe_core.mahamantra.audit import AuditAgency

    agency = AuditAgency()

    # Use EXISTING production introspection
    files, metrics = agency.scan()

    # Resonance-based semantic analysis
    resonance = agency.analyze_resonance("some text or code")

    # Full system understanding
    report = agency.deep_audit()
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "vyasa"  # Position 0 - The Compiler/Historian
__position__ = 0
__genesis__ = "0x00000000"


@dataclass
class ResonanceResult:
    """Result of resonance-based analysis."""
    seed: int
    position: int
    mahajana: str
    varga_dominant: str
    sthana_dominant: str
    guna: str
    shakti: float


class AuditAgency:
    """
    Deep System Intelligence via RESONANCE.

    Wraps EXISTING production components - no reinventing!
    """

    def __init__(self, root_path: str | None = None):
        if root_path is None:
            self._root = Path(__file__).parent.parent.parent.parent
        else:
            self._root = Path(root_path)

        # Lazy-loaded production components
        self._introspection = None
        self._code_scanner = None
        self._compression = None
        self._phonetic_bridge = None

    # =========================================================================
    # INTROSPECTION (uses research/project_introspection.py)
    # =========================================================================

    def scan(self) -> Tuple[List[Any], Any]:
        """
        Scan codebase using EXISTING project_introspection.
        Returns (files, metrics) with mahajana info.
        """
        from vibe_core.mahamantra.research.project_introspection import scan_codebase
        return scan_codebase(self._root)

    def find_gaps(self) -> Dict[str, Any]:
        """Find disconnected components via EXISTING introspection."""
        from vibe_core.mahamantra.research.project_introspection import find_gaps
        return find_gaps(self._root)

    def verify_parampara(self) -> Dict[str, Any]:
        """Verify lineage connections via EXISTING introspection."""
        from vibe_core.mahamantra.research.project_introspection import verify_parampara
        files, _ = self.scan()
        return verify_parampara(files)

    def measure_scale(self) -> Dict[str, int]:
        """Measure codebase scale via EXISTING introspection."""
        from vibe_core.mahamantra.research.project_introspection import measure_scale
        return measure_scale(self._root)

    # =========================================================================
    # KNOWLEDGE GRAPH (uses vibe_core/knowledge/code_scanner.py)
    # =========================================================================

    def build_knowledge_graph(self) -> Dict[str, Any]:
        """
        Build full knowledge graph with imports/calls/inheritance.
        Uses EXISTING CodeScanner + UnifiedKnowledgeGraph.
        """
        from vibe_core.knowledge.code_scanner import CodeScanner
        from vibe_core.knowledge.graph import UnifiedKnowledgeGraph

        graph = UnifiedKnowledgeGraph()
        scanner = CodeScanner(graph)
        stats = scanner.scan_directory(self._root / "vibe_core")

        return {
            "stats": stats,
            "nodes": len(graph.nodes),
            "edges": sum(len(e) for e in graph.edges.values()),
        }

    # =========================================================================
    # RESONANCE ANALYSIS (uses MahaCompression + PhoneticBridge)
    # =========================================================================

    def analyze_resonance(self, text: str) -> ResonanceResult:
        """
        Analyze text via RESONANCE - not binary if/else!

        Uses MahaCompression for intent + PhoneticBridge for phonetics.
        """
        from vibe_core.mahamantra.adapters.compression import MahaCompression
        from vibe_core.mahamantra.substrate.phonetic_bridge import UniversalPhoneticBridge
        from vibe_core.mahamantra.substrate.position import get_position

        # Compress to get seed/position/intent
        compressor = MahaCompression()
        result = compressor.compress(text)

        # Phonetic analysis
        bridge = UniversalPhoneticBridge()
        tensor = bridge.analyze(text)

        # Map position to mahajana using proper function
        position = result.position
        mantra_pos = get_position(position)
        mahajana = mantra_pos.guardian.value  # Guardian enum -> string value

        # Get guna from intent_level
        guna = result.intent_level.guna.value if hasattr(result.intent_level.guna, 'value') else str(result.intent_level.guna)

        return ResonanceResult(
            seed=result.seed,
            position=position,
            mahajana=mahajana,
            varga_dominant=tensor.dominant_varga.name,
            sthana_dominant=tensor.dominant_sthana.name,
            guna=guna,
            shakti=tensor.shakti,
        )

    # =========================================================================
    # WATCHMAN (uses StandardsInspectionTool)
    # =========================================================================

    def inspect_standards(self, path: str = "vibe_core") -> List[Dict]:
        """
        Run AST-based standards inspection via EXISTING Watchman.
        """
        from vibe_core.cartridges.system.watchman.tools.standards_inspection import (
            StandardsInspectionTool,
        )

        tool = StandardsInspectionTool()
        result = tool.execute({"action": "inspect_all", "path": path})

        if result.success:
            return result.output.get("violations", [])
        return []

    # =========================================================================
    # DEEP AUDIT (combines all)
    # =========================================================================

    def deep_audit(self) -> Dict[str, Any]:
        """
        Full deep audit combining all production components.
        """
        scale = self.measure_scale()
        parampara = self.verify_parampara()

        return {
            "scale": scale,
            "parampara": parampara,
            "summary": {
                "total_files": scale["total_files"],
                "total_loc": scale["total_lines"],
                "mahajana_coverage": scale["files_with_mahajana"],
                "parampara_valid": scale["valid_parampara"],
                "parampara_broken": scale["broken_lineage"],
            }
        }


__all__ = [
    "AuditAgency",
    "ResonanceResult",
]

