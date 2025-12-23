"""
OPUS-052: AKASHA (The Cosmic Ether) - Knowledge Graph Context.

Sanskrit: Akasha = Ether, Space, the fifth element that contains all.

AKASHA is the bridge between the Knowledge Graph and MANAS consciousness.
It provides context before action - answering "what does the system know?"
before asking "what should the system do?"

Architecture:
    ┌─────────────────────────────────────────────────────────────┐
    │                     AKASHA (The Ether)                      │
    │                                                             │
    │   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐      │
    │   │ AkashaPort  │──▶│ AkashaQuery │──▶│ AkashaSync  │      │
    │   │ (Bridge)    │   │ (Queries)   │   │ (Populate)  │      │
    │   └─────────────┘   └─────────────┘   └─────────────┘      │
    │          │                                    │              │
    │          ▼                                    ▼              │
    │   ┌─────────────────────────────────────────────────────┐  │
    │   │        UnifiedKnowledgeGraph (4D Structure)         │  │
    │   │  Ontology │ Topology │ Constraints │ Metrics        │  │
    │   └─────────────────────────────────────────────────────┘  │
    └─────────────────────────────────────────────────────────────┘

Integration Points:
    - VEDA Artha Phase: Inject context before intent resolution
    - JNANA Handler: Answer graph queries via chat
    - MANDALA: Populate graph from cartridge declarations

"Akasha is the space where all knowledge flows - the ether that connects."
"""

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

logger = logging.getLogger("MANAS.Cortex.Akasha")


# =============================================================================
# SECTION 1: DATA MODELS
# =============================================================================


@dataclass
class AkashaDependency:
    """A dependency relationship found in the graph."""

    source: str  # What depends
    target: str  # What it depends on
    relation: str  # Type of dependency
    depth: int = 0  # How far in the chain


@dataclass
class AkashaNode:
    """A simplified node representation for chat responses."""

    id: str
    name: str
    node_type: str
    domain: str
    description: str = ""

    def to_chat_string(self) -> str:
        """Format for chat response."""
        type_emoji = {
            "agent": "🤖",
            "feature": "✨",
            "concept": "💡",
            "rule": "📜",
            "domain": "🏛️",
        }.get(self.node_type, "📦")

        desc = f" - {self.description}" if self.description else ""
        return f"{type_emoji} **{self.name}** ({self.node_type}){desc}"


@dataclass
class AkashaQueryResult:
    """Result of a knowledge graph query."""

    query: str
    nodes: List[AkashaNode] = field(default_factory=list)
    dependencies: List[AkashaDependency] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    metrics: Dict[str, Dict[str, float]] = field(default_factory=dict)
    raw_context: str = ""
    found: bool = False

    def to_chat_response(self) -> str:
        """Format the result for chat display."""
        if not self.found:
            return f"❓ No knowledge found for: '{self.query}'"

        lines = [f"🔮 **Knowledge Query: {self.query}**", ""]

        # Nodes section
        if self.nodes:
            lines.append("**Found Entities:**")
            for node in self.nodes[:10]:  # Limit display
                lines.append(f"  {node.to_chat_string()}")
            lines.append("")

        # Dependencies section
        if self.dependencies:
            lines.append("**Dependencies:**")
            for dep in self.dependencies[:10]:
                indent = "  " * (dep.depth + 1)
                lines.append(f"{indent}↳ {dep.source} → {dep.target} ({dep.relation})")
            lines.append("")

        # Constraints section
        if self.constraints:
            lines.append("**Constraints:**")
            for constraint in self.constraints[:5]:
                lines.append(f"  ⚠️ {constraint}")
            lines.append("")

        # Metrics section
        if self.metrics:
            lines.append("**Scores:**")
            for node_id, metrics in list(self.metrics.items())[:5]:
                metrics_str = ", ".join(f"{k}={v}" for k, v in metrics.items())
                lines.append(f"  📊 {node_id}: {metrics_str}")

        return "\n".join(lines)


@dataclass
class AkashaContext:
    """
    Context package for VEDA Artha phase integration.

    This is injected into the processing pipeline to provide
    knowledge-backed context before action.
    """

    relevant_nodes: List[AkashaNode]
    dependencies_found: List[AkashaDependency]
    constraints_applicable: List[str]
    context_summary: str  # One-line summary for prompts
    raw_prompt_context: str  # Full context for LLM prompts

    def is_empty(self) -> bool:
        """Check if any context was found."""
        return not self.relevant_nodes and not self.dependencies_found


# =============================================================================
# SECTION 2: AKASHA PORT - Bridge to UnifiedKnowledgeGraph
# =============================================================================


class AkashaPort:
    """
    Bridge to the UnifiedKnowledgeGraph.

    Provides lazy initialization and workspace-aware loading.
    The "port" through which MANAS accesses universal knowledge.

    "The port is the gateway - it connects but does not contain."
    """

    def __init__(self, workspace: Optional[Path] = None):
        """
        Initialize AKASHA port.

        Args:
            workspace: Optional workspace path for knowledge loading
        """
        self._workspace = workspace
        self._graph = None
        self._loaded = False
        logger.debug("AKASHA Port initialized")

    @property
    def graph(self):
        """Lazy-load the knowledge graph."""
        if self._graph is None:
            self._initialize_graph()
        return self._graph

    def _initialize_graph(self) -> None:
        """Initialize the knowledge graph."""
        try:
            from vibe_core.knowledge.graph import UnifiedKnowledgeGraph

            self._graph = UnifiedKnowledgeGraph()

            # Try to load from workspace first, then default
            knowledge_paths = []
            if self._workspace:
                workspace_knowledge = self._workspace / "knowledge"
                if workspace_knowledge.exists():
                    knowledge_paths.append(workspace_knowledge)

            # Default knowledge path
            default_knowledge = Path(__file__).parent.parent.parent.parent.parent / "knowledge"
            if default_knowledge.exists():
                knowledge_paths.append(default_knowledge)

            # Load from first available path
            for kpath in knowledge_paths:
                try:
                    self._graph.load(kpath)
                    self._loaded = True
                    logger.info(f"AKASHA: Loaded knowledge from {kpath}")
                    break
                except Exception as e:
                    logger.debug(f"AKASHA: Could not load from {kpath}: {e}")

            # OPUS-155: CODEBASE SCANNING (P0 Fix)
            if self._loaded and self._workspace:
                try:
                    from vibe_core.knowledge.code_scanner import CodeScanner

                    scanner = CodeScanner(self._graph)

                    # Scan core and plugins
                    core_path = self._workspace / "vibe_core"
                    if core_path.exists():
                        logger.info("AKASHA: Scanning codebase for code knowledge...")
                        scanner.scan_directory(core_path)

                    # Scan for duplicates and resolve wildcard edges
                    self._graph.resolve_wildcards()
                except Exception as e:
                    logger.warning(f"AKASHA: Code scan failed: {e}")

            if not self._loaded:
                logger.warning("AKASHA: No knowledge loaded - operating in empty mode")

        except ImportError as e:
            logger.warning(f"AKASHA: Knowledge graph not available: {e}")
            self._graph = None

    def is_loaded(self) -> bool:
        """Check if knowledge is loaded."""
        return self._loaded

    def get_node_count(self) -> int:
        """Get number of nodes in graph."""
        if self.graph:
            return len(self.graph.nodes)
        return 0

    def get_edge_count(self) -> int:
        """Get number of edges in graph."""
        if self.graph:
            return sum(len(edges) for edges in self.graph.edges.values())
        return 0


# =============================================================================
# SECTION 3: AKASHA QUERY - Chat-Friendly Knowledge Queries
# =============================================================================


class AkashaQuery:
    """
    Chat-friendly knowledge query interface.

    Translates natural questions into graph operations.

    "Ask, and the ether shall answer."
    """

    def __init__(self, port: AkashaPort):
        """
        Initialize query interface.

        Args:
            port: AkashaPort instance for graph access
        """
        self._port = port

    def what_is(self, concept: str) -> AkashaQueryResult:
        """
        Answer "What is X?" queries.

        Args:
            concept: The concept to look up

        Returns:
            AkashaQueryResult with node information
        """
        logger.debug(f"AKASHA Query: what_is('{concept}')")
        result = AkashaQueryResult(query=f"What is {concept}?")

        graph = self._port.graph
        if not graph:
            return result

        # Search for matching nodes
        nodes = graph.search_nodes(concept)

        if nodes:
            result.found = True
            for node in nodes[:10]:
                result.nodes.append(
                    AkashaNode(
                        id=node.id,
                        name=node.name,
                        node_type=node.type.value,
                        domain=node.domain,
                        description=node.description,
                    )
                )

            # Get metrics for found nodes
            for node in nodes[:5]:
                metrics = graph.get_all_metrics(node.id)
                if metrics:
                    result.metrics[node.id] = {k.value: v for k, v in metrics.items()}

        return result

    def what_depends_on(self, target: str, depth: int = 2) -> AkashaQueryResult:
        """
        Answer "What depends on X?" queries (reverse dependency lookup).

        Args:
            target: The target node to find dependents of
            depth: How deep to search

        Returns:
            AkashaQueryResult with dependency information
        """
        logger.debug(f"AKASHA Query: what_depends_on('{target}', depth={depth})")
        result = AkashaQueryResult(query=f"What depends on {target}?")

        graph = self._port.graph
        if not graph:
            return result

        # First find the target node
        target_nodes = graph.search_nodes(target)
        if not target_nodes:
            return result

        result.found = True

        # For each target, find what depends on it (incoming edges)
        from vibe_core.knowledge.schema import RelationType

        for target_node in target_nodes[:3]:  # Limit target expansion
            result.nodes.append(
                AkashaNode(
                    id=target_node.id,
                    name=target_node.name,
                    node_type=target_node.type.value,
                    domain=target_node.domain,
                    description=target_node.description,
                )
            )

            # Get incoming DEPENDS_ON edges
            incoming = graph.get_incoming_edges(target_node.id, RelationType.DEPENDS_ON)

            for edge in incoming:
                result.dependencies.append(
                    AkashaDependency(
                        source=edge.source,
                        target=edge.target,
                        relation=edge.relation.value,
                        depth=0,
                    )
                )

                # Recurse for deeper dependencies if requested
                if depth > 1:
                    self._find_dependents_recursive(
                        graph, edge.source, depth - 1, result.dependencies, visited={edge.source}
                    )

        return result

    def _find_dependents_recursive(
        self,
        graph,
        node_id: str,
        depth: int,
        result_list: List[AkashaDependency],
        visited: Set[str],
        current_depth: int = 1,
    ) -> None:
        """Recursively find dependents."""
        if depth <= 0:
            return

        from vibe_core.knowledge.schema import RelationType

        incoming = graph.get_incoming_edges(node_id, RelationType.DEPENDS_ON)

        for edge in incoming:
            if edge.source not in visited:
                visited.add(edge.source)
                result_list.append(
                    AkashaDependency(
                        source=edge.source,
                        target=edge.target,
                        relation=edge.relation.value,
                        depth=current_depth,
                    )
                )
                self._find_dependents_recursive(graph, edge.source, depth - 1, result_list, visited, current_depth + 1)

    def dependencies_of(self, source: str, depth: int = 2) -> AkashaQueryResult:
        """
        Answer "What does X depend on?" queries (forward dependency lookup).

        Args:
            source: The source node to find dependencies of
            depth: How deep to search

        Returns:
            AkashaQueryResult with dependency information
        """
        logger.debug(f"AKASHA Query: dependencies_of('{source}', depth={depth})")
        result = AkashaQueryResult(query=f"What does {source} depend on?")

        graph = self._port.graph
        if not graph:
            return result

        # Find the source node
        source_nodes = graph.search_nodes(source)
        if not source_nodes:
            return result

        result.found = True

        from vibe_core.knowledge.schema import RelationType

        for source_node in source_nodes[:3]:
            result.nodes.append(
                AkashaNode(
                    id=source_node.id,
                    name=source_node.name,
                    node_type=source_node.type.value,
                    domain=source_node.domain,
                    description=source_node.description,
                )
            )

            # Traverse forward dependencies
            deps = graph.traverse(source_node.id, RelationType.DEPENDS_ON, depth)

            for dep_id, dep_node in deps.items():
                if dep_id != source_node.id:
                    # Find the edge for relation info
                    edges = graph.get_edges(source_node.id, RelationType.DEPENDS_ON)
                    for edge in edges:
                        if edge.target == dep_id:
                            result.dependencies.append(
                                AkashaDependency(
                                    source=source_node.id,
                                    target=dep_id,
                                    relation=edge.relation.value,
                                    depth=0,
                                )
                            )
                            break

        return result

    def constraints_for(self, node_id: str) -> AkashaQueryResult:
        """
        Get constraints that apply to a node.

        Args:
            node_id: The node to check constraints for

        Returns:
            AkashaQueryResult with constraint information
        """
        logger.debug(f"AKASHA Query: constraints_for('{node_id}')")
        result = AkashaQueryResult(query=f"Constraints for {node_id}")

        graph = self._port.graph
        if not graph:
            return result

        # Find the node first
        nodes = graph.search_nodes(node_id)
        if nodes:
            result.found = True
            for node in nodes[:3]:
                result.nodes.append(
                    AkashaNode(
                        id=node.id,
                        name=node.name,
                        node_type=node.type.value,
                        domain=node.domain,
                        description=node.description,
                    )
                )

                # Get constraints
                constraints = graph.get_constraints(node.id)
                for c in constraints:
                    result.constraints.append(c.message)

        return result

    def graph_summary(self) -> AkashaQueryResult:
        """
        Get a summary of the knowledge graph.

        Returns:
            AkashaQueryResult with summary information
        """
        result = AkashaQueryResult(query="Knowledge Graph Summary")

        graph = self._port.graph
        if not graph:
            return result

        result.found = True

        # Gather stats
        from vibe_core.knowledge.schema import NodeType

        for node_type in NodeType:
            nodes = graph.get_nodes_by_type(node_type)
            for node in nodes[:5]:  # Sample each type
                result.nodes.append(
                    AkashaNode(
                        id=node.id,
                        name=node.name,
                        node_type=node.type.value,
                        domain=node.domain,
                        description=node.description,
                    )
                )

        # Count stats
        node_count = len(graph.nodes)
        edge_count = sum(len(e) for e in graph.edges.values())
        constraint_count = len(graph.constraints)

        result.raw_context = f"Knowledge Graph: {node_count} nodes, {edge_count} edges, {constraint_count} constraints"

        return result


# =============================================================================
# SECTION 4: AKASHA SYNC - Populate Graph from MANDALA
# =============================================================================


class AkashaSync:
    """
    Synchronize knowledge graph with MANDALA cartridge data.

    When agents declare themselves via MANDALA, their capabilities
    flow into AKASHA for universal awareness.

    "What is declared in MANDALA, flows into AKASHA."
    """

    def __init__(self, port: AkashaPort):
        """
        Initialize sync interface.

        Args:
            port: AkashaPort instance for graph access
        """
        self._port = port

    def sync_from_mandala(self, mandala_manifest: Any) -> int:
        """
        Sync a MANDALA manifest into the knowledge graph.

        Args:
            mandala_manifest: FractalManifest from MANDALA

        Returns:
            Number of nodes added/updated
        """
        graph = self._port.graph
        if not graph:
            logger.warning("AKASHA Sync: No graph available")
            return 0

        count = 0

        try:
            from vibe_core.knowledge.schema import Edge, Node, NodeType, RelationType

            # Add agent node
            agent_id = mandala_manifest.agent_id
            agent_node = Node(
                id=agent_id,
                type=NodeType.AGENT,
                name=mandala_manifest.name,
                domain="mandala",
                description=f"MANDALA Agent v{mandala_manifest.version}",
                properties={"version": mandala_manifest.version},
            )
            graph.nodes[agent_id] = agent_node
            count += 1

            # Add capability nodes
            for cap_name, cap_spec in mandala_manifest.capabilities.items():
                cap_id = f"{agent_id}.{cap_name}"
                cap_node = Node(
                    id=cap_id,
                    type=NodeType.FEATURE,
                    name=cap_name,
                    domain="mandala",
                    description=cap_spec.description,
                    properties={
                        "cost": cap_spec.cost,
                        "rate_limit": cap_spec.rate_limit,
                        "enabled": cap_spec.enabled,
                    },
                )
                graph.nodes[cap_id] = cap_node
                count += 1

                # Add HANDLES edge from agent to capability
                edge = Edge(
                    source=agent_id,
                    target=cap_id,
                    relation=RelationType.HANDLES,
                )
                if agent_id not in graph.edges:
                    graph.edges[agent_id] = []
                graph.edges[agent_id].append(edge)

                # Add DEPENDS_ON edges for capability dependencies
                for dep in cap_spec.dependencies:
                    dep_edge = Edge(
                        source=cap_id,
                        target=dep,
                        relation=RelationType.DEPENDS_ON,
                    )
                    if cap_id not in graph.edges:
                        graph.edges[cap_id] = []
                    graph.edges[cap_id].append(dep_edge)

            logger.info(f"AKASHA Sync: Added {count} nodes from MANDALA manifest '{agent_id}'")

        except Exception as e:
            logger.error(f"AKASHA Sync failed: {e}")

        return count


# =============================================================================
# SECTION 5: VEDA INTEGRATION - Context for Artha Phase
# =============================================================================


def get_akasha_context(keywords: Set[str], workspace: Optional[Path] = None) -> AkashaContext:
    """
    Get knowledge context for VEDA Artha phase.

    This function is called during intent resolution to inject
    relevant knowledge context before action.

    Args:
        keywords: Keywords extracted by SHABDA phase
        workspace: Optional workspace path

    Returns:
        AkashaContext with relevant knowledge

    Usage in VEDA:
        # In Artha.process():
        akasha_ctx = get_akasha_context(shabda.keywords)
        # Use akasha_ctx.context_summary in hints
    """
    port = AkashaPort(workspace)
    query = AkashaQuery(port)

    relevant_nodes: List[AkashaNode] = []
    dependencies: List[AkashaDependency] = []
    constraints: List[str] = []

    # Query for each keyword
    for keyword in list(keywords)[:5]:  # Limit to top 5 keywords
        result = query.what_is(keyword)
        if result.found:
            relevant_nodes.extend(result.nodes)

        # Also check dependencies
        dep_result = query.what_depends_on(keyword, depth=1)
        if dep_result.found:
            dependencies.extend(dep_result.dependencies)

        # Check constraints
        constraint_result = query.constraints_for(keyword)
        if constraint_result.found:
            constraints.extend(constraint_result.constraints)

    # Deduplicate
    seen_nodes = set()
    unique_nodes = []
    for node in relevant_nodes:
        if node.id not in seen_nodes:
            seen_nodes.add(node.id)
            unique_nodes.append(node)

    # Generate summary
    if unique_nodes:
        context_summary = f"Found {len(unique_nodes)} related concepts: {', '.join(n.name for n in unique_nodes[:3])}"
    else:
        context_summary = "No prior knowledge found"

    # Generate raw prompt context
    raw_lines = []
    if unique_nodes:
        raw_lines.append("RELEVANT KNOWLEDGE:")
        for node in unique_nodes[:10]:
            raw_lines.append(f"  - {node.name} ({node.node_type}): {node.description}")

    if dependencies:
        raw_lines.append("\nDEPENDENCIES:")
        for dep in dependencies[:5]:
            raw_lines.append(f"  - {dep.source} depends on {dep.target}")

    if constraints:
        raw_lines.append("\nCONSTRAINTS:")
        for c in constraints[:5]:
            raw_lines.append(f"  - {c}")

    return AkashaContext(
        relevant_nodes=unique_nodes,
        dependencies_found=dependencies,
        constraints_applicable=constraints,
        context_summary=context_summary,
        raw_prompt_context="\n".join(raw_lines) if raw_lines else "",
    )


# =============================================================================
# SECTION 6: JNANA INTEGRATION - Chat Interface
# =============================================================================


def handle_akasha_query(content: str, workspace: Optional[Path] = None) -> str:
    """
    Handle a knowledge query from JNANA chat.

    Parses the query and routes to appropriate AKASHA operation.

    Args:
        content: The user's query content
        workspace: Optional workspace path

    Returns:
        Formatted response string
    """
    port = AkashaPort(workspace)
    query_engine = AkashaQuery(port)

    content_lower = content.lower()

    # Detect query type
    if any(phrase in content_lower for phrase in ["depends on", "hängt ab", "abhängig"]):
        # Extract the target
        # "What depends on X?" pattern
        import re

        match = re.search(r"depends?\s+on\s+['\"]?(\w+)['\"]?", content_lower)
        if not match:
            match = re.search(r"hängt?\s+.*?ab.*?['\"]?(\w+)['\"]?", content_lower)
        if not match:
            # Try to get last word as target
            words = content_lower.split()
            if words:
                target = words[-1].strip("?")
            else:
                target = ""
        else:
            target = match.group(1)

        if target:
            result = query_engine.what_depends_on(target)
            return result.to_chat_response()
        else:
            return "❓ Please specify what you want to check dependencies for."

    elif any(phrase in content_lower for phrase in ["what is", "was ist", "describe", "beschreibe"]):
        # "What is X?" pattern
        import re

        match = re.search(r"(?:what is|was ist|describe|beschreibe)\s+['\"]?(\w+)['\"]?", content_lower)
        if match:
            target = match.group(1)
            result = query_engine.what_is(target)
            return result.to_chat_response()
        else:
            return "❓ Please specify what you want to know about."

    elif any(phrase in content_lower for phrase in ["constraints", "einschränkungen", "rules"]):
        # Constraints query
        words = content_lower.replace("?", "").split()
        target = words[-1] if words else ""
        if target and target not in ["constraints", "einschränkungen", "rules"]:
            result = query_engine.constraints_for(target)
            return result.to_chat_response()
        else:
            return "❓ Please specify what you want to check constraints for."

    elif any(phrase in content_lower for phrase in ["summary", "zusammenfassung", "overview", "überblick"]):
        result = query_engine.graph_summary()
        return result.to_chat_response()

    else:
        # Default: search for keywords
        words = content_lower.replace("?", "").split()
        keywords = [w for w in words if len(w) > 2 and w not in {"the", "what", "how", "is", "are"}]

        if keywords:
            result = query_engine.what_is(keywords[0])
            return result.to_chat_response()
        else:
            return "❓ Please ask about a specific concept, dependency, or constraint."


def get_akasha_for_chat(workspace: Optional[Path] = None) -> str:
    """
    Get AKASHA status for chat display.

    Args:
        workspace: Optional workspace path

    Returns:
        Status string for chat
    """
    port = AkashaPort(workspace)

    if not port.is_loaded():
        return "🔮 AKASHA: Knowledge graph not loaded"

    node_count = port.get_node_count()
    edge_count = port.get_edge_count()

    return f"""🔮 **AKASHA** (Knowledge Graph)
├─ Nodes: {node_count}
├─ Edges: {edge_count}
└─ Status: {"Active" if port.is_loaded() else "Inactive"}

**Query Examples:**
- "What depends on agent_city?"
- "What is MANAS?"
- "Show constraints for kernel"
- "Knowledge summary"
"""


# =============================================================================
# SECTION 7: SINGLETON ACCESS
# =============================================================================


_akasha_port: Optional[AkashaPort] = None
_akasha_query: Optional[AkashaQuery] = None


def get_akasha_port(workspace: Optional[Path] = None) -> AkashaPort:
    """Get or create the global AKASHA port."""
    global _akasha_port
    if _akasha_port is None:
        _akasha_port = AkashaPort(workspace)
    return _akasha_port


def get_akasha_query(workspace: Optional[Path] = None) -> AkashaQuery:
    """Get or create the global AKASHA query interface."""
    global _akasha_query
    if _akasha_query is None:
        _akasha_query = AkashaQuery(get_akasha_port(workspace))
    return _akasha_query
