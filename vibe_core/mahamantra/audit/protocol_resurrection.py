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
from vibe_core.mahamantra.audit.audit_registry import AuditFinding, FindingSeverity

assert int(__genesis__, 16) % PARAMPARA == 0, "BROKEN LINEAGE"


class Auditor:
    """Auditor for runtime protocol compliance."""

    def run_audit(self) -> List[AuditFinding]:
        """Execute the audit and return a list of findings."""
        findings: List[AuditFinding] = []
        all_compliant = True

        # Check compliance
        compliance = self._check_protocol_compliance()
        for cls_name, status in compliance.items():
            if not status:
                all_compliant = False
                findings.append(
                    AuditFinding(
                        source="ProtocolResurrection.compliance",
                        position=__position__,
                        mahajana=__mahajana__,
                        description=f"Class '{cls_name}' failed runtime protocol compliance check.",
                        severity=FindingSeverity.CRITICAL,
                    )
                )

        # Add a summary finding
        summary_severity = FindingSeverity.INFO if all_compliant else FindingSeverity.WARNING
        summary_desc = "All core classes are ALIVE at runtime."
        if not all_compliant:
            summary_desc = "DEAD CODE DETECTED: Some core classes do not comply with their protocols."

        findings.append(
            AuditFinding(
                source="ProtocolResurrection.summary",
                position=__position__,
                mahajana=__mahajana__,
                description=summary_desc,
                severity=summary_severity,
            )
        )

        return findings

    def _check_protocol_compliance(self) -> Dict[str, bool]:
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

    def _verify_protocol_methods(self) -> Dict[str, List[str]]:
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

    def _get_king_status(self) -> Dict[str, any]:
        """
        Get status of THE KING - the interplay of all components.

        Returns:
            Dict with axioms, nodes, edges, qualities
        """
        from vibe_core.mahamantra.analysis.derivation_graph import DerivationGraph
        from vibe_core.mahamantra.protocols.seed._axioms import (
            WORDS,
            TRINITY,
            HARE_COUNT,
            KRISHNA_COUNT,
            RAMA_COUNT,
            PANCHA,
            HALVES,
        )
        from vibe_core.mahamantra_research.acintya_mathematics import QUALITIES

        graph = DerivationGraph()

        return {
            "axioms": 7,
            "axiom_values": [WORDS, TRINITY, HARE_COUNT, KRISHNA_COUNT, RAMA_COUNT, PANCHA, HALVES],
            "nodes": len(graph.nodes),
            "edges": len(graph.edges),
            "qualities": QUALITIES,  # 64 - Krishna's complete capability
            "king_formula": "7 Axioms → 49 Nodes → 92 Edges → ∞ RAM",
        }


__all__ = ["Auditor"]
