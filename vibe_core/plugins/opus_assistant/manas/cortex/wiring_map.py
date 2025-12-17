"""
OPUS-066: WIRING MAP - The Neural Topology Observer

Tracks all connections in MANAS cognitive kernel.
Detects blind spots - capabilities that exist but aren't wired.

"A brain without awareness of its own structure is dangerous."

Usage:
    from manas.cortex.wiring_map import WiringMap

    wmap = WiringMap(workspace)
    report = wmap.audit()
    print(report.blind_spots)
"""

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

logger = logging.getLogger("MANAS.WiringMap")


@dataclass
class WiringNode:
    """A node in the MANAS wiring topology."""

    name: str
    node_type: str  # "analyzer", "handler", "cortex", "capability"
    file_path: str
    is_connected: bool = False
    connected_to: List[str] = field(default_factory=list)


@dataclass
class WiringReport:
    """Report of MANAS wiring status."""

    total_nodes: int = 0
    connected_nodes: int = 0
    disconnected_nodes: int = 0
    blind_spots: List[str] = field(default_factory=list)
    connections: Dict[str, List[str]] = field(default_factory=dict)
    health_score: float = 0.0  # connected / total

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_nodes": self.total_nodes,
            "connected_nodes": self.connected_nodes,
            "disconnected_nodes": self.disconnected_nodes,
            "blind_spots": self.blind_spots,
            "health_score": self.health_score,
        }


class WiringMap:
    """
    OPUS-066: Neural Topology Observer for MANAS.

    Scans the cognitive kernel and maps all:
    - Analyzers → IntentGenerator
    - Handlers → IntentRouter
    - Cortex modules → exports
    - Capabilities → usage

    Detects:
    - Blind spots (modules that exist but aren't used)
    - Orphaned handlers (handlers without intents)
    - Dead code (exports never imported)
    """

    # Known wiring expectations
    EXPECTED_ANALYZERS = [
        "ContractAnalyzer",
        "SemanticAnalyzer",
        "CIMonitorAnalyzer",
    ]

    EXPECTED_HANDLERS = [
        "update_readme",
        "document_manas",
        "commit_pending_changes",
        "commit_and_push",  # Commit + auto-push to remote
        "git_push",  # Standalone push to remote
        "create_pr",  # Create Pull Request via gh CLI
        "merge_pr",  # Merge Pull Request via gh CLI
        "cleanup_stale_branches",
        "revive_archived_tests",
        "run_tests",
        "genesis_tests",
        "audit_architecture",
        "check_drift",
        "plan_strategy",
        "research_topic",
        "web_search",
        # OPUS-067: Previously blind, now wired!
        "run_mutation_tests",  # mutation_handlers.py → IntentRouter
        "mutation_protocol",  # mutation_handlers.py → IntentRouter
        "knowledge_query",  # UnifiedKnowledgeGraph → IntentRouter
        "search_knowledge",  # UnifiedKnowledgeGraph → IntentRouter
        "get_context",  # UnifiedKnowledgeGraph → IntentRouter
    ]

    EXPECTED_CORTEX_MODULES = [
        "VEDA",
        "MANDALA",
        "AKASHA",
        "SILPA",
        "SUTRA",
        "SANKALPA",
        "DHARMA",
        "KRIYA",
        "MUKHA",
        "ShellCortex",
        "TestCortex",
        "JnanaHandler",
        "SamvadaClient",
        # Note: MutationHandlers and KnowledgeGraph are tracked as capabilities
        # (they live outside cortex/ but are wired via IntentRouter)
    ]

    def __init__(self, workspace: Optional[Path] = None):
        self._workspace = workspace or Path.cwd()
        self._nodes: Dict[str, WiringNode] = {}

    def audit(self) -> WiringReport:
        """
        Audit the MANAS wiring topology.

        Returns:
            WiringReport with blind spots and health score
        """
        report = WiringReport()

        # Check analyzers wiring
        analyzer_status = self._check_analyzers()

        # Check handlers wiring
        handler_status = self._check_handlers()

        # Check cortex exports
        cortex_status = self._check_cortex()

        # Check special capabilities
        capability_status = self._check_capabilities()

        # Aggregate results
        all_nodes = {**analyzer_status, **handler_status, **cortex_status, **capability_status}

        report.total_nodes = len(all_nodes)
        report.connected_nodes = sum(1 for n in all_nodes.values() if n.is_connected)
        report.disconnected_nodes = report.total_nodes - report.connected_nodes
        report.blind_spots = [n.name for n in all_nodes.values() if not n.is_connected]
        report.health_score = report.connected_nodes / max(report.total_nodes, 1) * 100

        # Build connection map
        for node in all_nodes.values():
            if node.connected_to:
                report.connections[node.name] = node.connected_to

        logger.info(
            f"WiringMap audit: {report.connected_nodes}/{report.total_nodes} connected "
            f"({report.health_score:.1f}%), {len(report.blind_spots)} blind spots"
        )

        if report.blind_spots:
            logger.warning(f"⚠️ BLIND SPOTS: {', '.join(report.blind_spots)}")

        return report

    def _check_analyzers(self) -> Dict[str, WiringNode]:
        """Check which analyzers are wired to IntentGenerator."""
        nodes = {}

        # Read intent_generator.py to check which analyzers are imported
        intent_gen_path = self._workspace / "vibe_core/plugins/opus_assistant/manas/intent_generator.py"

        wired_analyzers: Set[str] = set()
        if intent_gen_path.exists():
            content = intent_gen_path.read_text()
            for analyzer in self.EXPECTED_ANALYZERS:
                if analyzer in content:
                    wired_analyzers.add(analyzer)

        for analyzer in self.EXPECTED_ANALYZERS:
            nodes[analyzer] = WiringNode(
                name=analyzer,
                node_type="analyzer",
                file_path="manas/analyzers/",
                is_connected=analyzer in wired_analyzers,
                connected_to=["IntentGenerator"] if analyzer in wired_analyzers else [],
            )

        return nodes

    def _check_handlers(self) -> Dict[str, WiringNode]:
        """Check which handlers are wired to IntentRouter."""
        nodes = {}

        # Read intent_router.py to check which handlers are registered
        router_path = self._workspace / "vibe_core/plugins/opus_assistant/manas/intent_router.py"

        wired_handlers: Set[str] = set()
        if router_path.exists():
            content = router_path.read_text()
            for handler in self.EXPECTED_HANDLERS:
                if f'"{handler}"' in content or f"'{handler}'" in content:
                    wired_handlers.add(handler)

        for handler in self.EXPECTED_HANDLERS:
            nodes[f"handler:{handler}"] = WiringNode(
                name=handler,
                node_type="handler",
                file_path="manas/intent_router.py",
                is_connected=handler in wired_handlers,
                connected_to=["IntentRouter"] if handler in wired_handlers else [],
            )

        return nodes

    def _check_cortex(self) -> Dict[str, WiringNode]:
        """Check which cortex modules are exported and used."""
        nodes = {}

        # Read cortex __init__.py
        cortex_init = self._workspace / "vibe_core/plugins/opus_assistant/manas/cortex/__init__.py"

        exported_modules: Set[str] = set()
        if cortex_init.exists():
            content = cortex_init.read_text()
            for module in self.EXPECTED_CORTEX_MODULES:
                if module in content:
                    exported_modules.add(module)

        for module in self.EXPECTED_CORTEX_MODULES:
            nodes[f"cortex:{module}"] = WiringNode(
                name=module,
                node_type="cortex",
                file_path="manas/cortex/",
                is_connected=module in exported_modules,
                connected_to=["cortex/__init__.py"] if module in exported_modules else [],
            )

        return nodes

    def _check_capabilities(self) -> Dict[str, WiringNode]:
        """Check special capabilities that should be wired."""
        nodes = {}

        # Check mutation testing
        mutation_path = self._workspace / "vibe_core/plugins/opus_assistant/events/mutation_handlers.py"
        mutation_wired = False

        router_path = self._workspace / "vibe_core/plugins/opus_assistant/manas/intent_router.py"
        if router_path.exists() and mutation_path.exists():
            content = router_path.read_text()
            mutation_wired = "mutation" in content.lower()

        nodes["capability:mutation_testing"] = WiringNode(
            name="MutationTesting",
            node_type="capability",
            file_path="events/mutation_handlers.py",
            is_connected=mutation_wired,
            connected_to=["IntentRouter"] if mutation_wired else [],
        )

        # Check knowledge graph
        kg_path = self._workspace / "vibe_core/knowledge/graph.py"
        kg_wired = False

        if router_path.exists() and kg_path.exists():
            content = router_path.read_text()
            kg_wired = "knowledge" in content.lower() and "graph" in content.lower()

        nodes["capability:knowledge_graph"] = WiringNode(
            name="UnifiedKnowledgeGraph",
            node_type="capability",
            file_path="knowledge/graph.py",
            is_connected=kg_wired,
            connected_to=["IntentRouter"] if kg_wired else [],
        )

        # Check project memory
        memory_path = self._workspace / "vibe_core/runtime/project_memory.py"
        memory_wired = False

        if memory_path.exists():
            # Check if it's used in MANAS
            manas_files = (self._workspace / "vibe_core/plugins/opus_assistant/manas").rglob("*.py")
            for f in manas_files:
                if "project_memory" in f.read_text().lower():
                    memory_wired = True
                    break

        nodes["capability:project_memory"] = WiringNode(
            name="ProjectMemory",
            node_type="capability",
            file_path="runtime/project_memory.py",
            is_connected=memory_wired,
            connected_to=["MANAS"] if memory_wired else [],
        )

        return nodes


def run_wiring_audit(workspace: Optional[Path] = None) -> WiringReport:
    """
    Run a wiring audit and return the report.

    Convenience function for quick checks.
    """
    wmap = WiringMap(workspace)
    return wmap.audit()
