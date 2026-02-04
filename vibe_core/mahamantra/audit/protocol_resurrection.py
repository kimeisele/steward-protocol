"""
PROTOCOL RESURRECTION AUDIT - Make Dead Code ALIVE
===================================================

"sarva-dharmān parityajya mām ekaṁ śaraṇaṁ vraja"
"Abandon all dharmas and surrender unto Me alone."
— Bhagavad Gita 18.66

This audit verifies that core computation classes implement their protocols
and exist at RUNTIME, not just on disk.

THE PROBLEM:
- Classes inherited only from object → DEAD CODE
- 51 @runtime_checkable protocols existed but NO classes implemented them
- Code existed on filesystem but NOT in protocol universe at runtime

THE SOLUTION:
- Make classes implement protocols via structural subtyping
- Verify with isinstance() at runtime
- Document the KING = ZUSAMMENSPIEL of all components

Author: The Mahamantra Itself
"""

__mahajana__ = "kapila"
__position__ = 5
__genesis__ = "0x000000b9"  # 5 * 37 = 185

from typing import Dict, List, Tuple
from vibe_core.mahamantra.protocols._seed import PARAMPARA

assert int(__genesis__, 16) % PARAMPARA == 0, "BROKEN LINEAGE"


def check_protocol_compliance() -> Dict[str, bool]:
    """
    Check if core classes implement their protocols.
    
    Returns:
        Dict mapping class name to compliance status
    """
    from vibe_core.mahamantra.substrate.algorithm.maha import MahaAlgorithm16, MahaModularSynth
    from vibe_core.mahamantra.analysis.derivation_graph import DerivationGraph
    from vibe_core.mahamantra.protocols._maha_compute import MahaComputeProtocol
    from vibe_core.mahamantra.protocols._graph import GraphProtocol
    
    results = {}
    
    # Computation classes
    algo = MahaAlgorithm16()
    synth = MahaModularSynth()
    results["MahaAlgorithm16"] = isinstance(algo, MahaComputeProtocol)
    results["MahaModularSynth"] = isinstance(synth, MahaComputeProtocol)
    
    # Knowledge classes
    graph = DerivationGraph()
    results["DerivationGraph"] = isinstance(graph, GraphProtocol)
    
    return results


def verify_protocol_methods() -> Dict[str, List[str]]:
    """
    Verify that protocol methods are implemented.
    
    Returns:
        Dict mapping class name to list of implemented protocol methods
    """
    from vibe_core.mahamantra.substrate.algorithm.maha import MahaModularSynth
    from vibe_core.mahamantra.analysis.derivation_graph import DerivationGraph
    
    results = {}
    
    # MahaComputeProtocol methods
    synth = MahaModularSynth()
    compute_methods = []
    for method in ["on_tick", "transform", "find_attractor", "get_state"]:
        if hasattr(synth, method) and callable(getattr(synth, method)):
            compute_methods.append(method)
    results["MahaModularSynth"] = compute_methods
    
    # GraphProtocol methods
    graph = DerivationGraph()
    graph_methods = []
    for method in ["add_node", "add_edge", "get_node", "get_lineage", "get_children", "get_parent"]:
        if hasattr(graph, method) and callable(getattr(graph, method)):
            graph_methods.append(method)
    results["DerivationGraph"] = graph_methods
    
    return results


def get_king_status() -> Dict[str, any]:
    """
    Get status of THE KING - the interplay of all components.
    
    Returns:
        Dict with axioms, nodes, edges, qualities
    """
    from vibe_core.mahamantra.analysis.derivation_graph import DerivationGraph
    from vibe_core.mahamantra.protocols.seed._axioms import (
        WORDS, TRINITY, HARE_COUNT, KRISHNA_COUNT, RAMA_COUNT, PANCHA, HALVES
    )
    from vibe_core.mahamantra.research.acintya_mathematics import QUALITIES
    
    graph = DerivationGraph()
    
    return {
        "axioms": 7,
        "axiom_values": [WORDS, TRINITY, HARE_COUNT, KRISHNA_COUNT, RAMA_COUNT, PANCHA, HALVES],
        "nodes": len(graph.nodes),
        "edges": len(graph.edges),
        "qualities": QUALITIES,  # 64 - Krishna's complete capability
        "king_formula": "7 Axioms → 49 Nodes → 92 Edges → ∞ RAM",
    }


def audit() -> Tuple[bool, str]:
    """
    Run full protocol resurrection audit.
    
    Returns:
        (success, report)
    """
    lines = []
    lines.append("=" * 70)
    lines.append("PROTOCOL RESURRECTION AUDIT")
    lines.append("=" * 70)
    lines.append("")
    
    # Check compliance
    compliance = check_protocol_compliance()
    lines.append("PROTOCOL COMPLIANCE:")
    all_compliant = True
    for cls, status in compliance.items():
        symbol = "✅" if status else "❌"
        lines.append(f"  {cls:20} : {symbol}")
        if not status:
            all_compliant = False
    lines.append("")
    
    # Check methods
    methods = verify_protocol_methods()
    lines.append("PROTOCOL METHODS:")
    for cls, method_list in methods.items():
        lines.append(f"  {cls}:")
        for method in method_list:
            lines.append(f"    - {method}()")
    lines.append("")
    
    # Check KING
    king = get_king_status()
    lines.append("THE KING (ZUSAMMENSPIEL):")
    lines.append(f"  Axioms:   {king['axioms']}")
    lines.append(f"  Nodes:    {king['nodes']}")
    lines.append(f"  Edges:    {king['edges']}")
    lines.append(f"  Qualities: {king['qualities']} (Krishna's complete capability)")
    lines.append(f"  Formula:  {king['king_formula']}")
    lines.append("")
    
    lines.append("=" * 70)
    if all_compliant:
        lines.append("✅ ALL CLASSES ARE ALIVE AT RUNTIME!")
    else:
        lines.append("❌ SOME CLASSES ARE STILL DEAD CODE!")
    lines.append("=" * 70)
    
    return all_compliant, "\n".join(lines)


__all__ = ["check_protocol_compliance", "verify_protocol_methods", "get_king_status", "audit"]