"""
Code Scanner - The Weaver's Eye

OPUS-110: Graph-based Gap Detection
OPUS-155: Akasha Nervous System (Import/Call tracking)

Scans Python source code and populates the UnifiedKnowledgeGraph with:
- MODULE nodes (files)
- CLASS nodes (class definitions)
- FUNCTION nodes (function definitions)
- INTERFACE nodes (ABC classes)

Creates edges:
- DEFINES (module -> class/function)
- INHERITS (class -> parent)
- DUPLICATES (class -> class with same name + bases)
- IMPORTS (module -> module) [OPUS-155: Nadis - the wires]
- CALLS (module -> function) [OPUS-155: Prana - the sparks]

This enables graph-based queries like:
    graph.get_nodes_by_type(NodeType.CLASS)
        .filter(lambda n: graph.has_edge(n.id, RelationType.DUPLICATES))

OPUS-155: The Nervous System
    Import edges create the "wires" (Nadis) between modules.
    Call edges track the "sparks" (Prana) of execution flow.
    This enables pre-cognitive wiring awareness in Akasha.
"""

import ast
import logging
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from .graph import UnifiedKnowledgeGraph
from .schema import Edge, Node, NodeType, RelationType

logger = logging.getLogger("CODE_SCANNER")


class CodeScanner:
    """
    Scans Python source code into the Knowledge Graph.

    The Weaver's Eye - sees code as nodes and edges.
    """

    def __init__(self, graph: UnifiedKnowledgeGraph):
        self.graph = graph
        self._class_registry: Dict[str, List[Dict]] = defaultdict(list)
        self._scanned_files: Set[str] = set()

    def scan_directory(self, directory: Path, pattern: str = "**/*.py") -> Dict:
        """
        Scan a directory and populate the graph.

        Args:
            directory: Root directory to scan
            pattern: Glob pattern for files

        Returns:
            Scan statistics
        """
        stats = {
            "files_scanned": 0,
            "modules_added": 0,
            "classes_added": 0,
            "functions_added": 0,
            "interfaces_added": 0,
            "duplicates_found": 0,
            # OPUS-155: Nervous System
            "imports_added": 0,
            "calls_added": 0,
        }

        # First pass: collect all class definitions
        for py_file in directory.rglob(pattern.replace("**/", "")):
            if "__pycache__" in str(py_file):
                continue
            if str(py_file) in self._scanned_files:
                continue

            try:
                self._scan_file(py_file, stats)
                self._scanned_files.add(str(py_file))
            except Exception as e:
                logger.debug(f"Could not scan {py_file}: {e}")

        # Second pass: detect duplicates
        stats["duplicates_found"] = self._detect_duplicates()

        logger.info(
            f"Code scan complete: {stats['files_scanned']} files, "
            f"{stats['classes_added']} classes, "
            f"{stats['duplicates_found']} duplicates, "
            f"{stats['imports_added']} imports, "
            f"{stats['calls_added']} calls"
        )

        return stats

    def _scan_file(self, filepath: Path, stats: Dict) -> None:
        """Scan a single Python file."""
        with open(filepath, "r", encoding="utf-8") as f:
            source = f.read()

        try:
            tree = ast.parse(source)
        except SyntaxError:
            return

        stats["files_scanned"] += 1

        # Create module node
        module_id = f"module:{filepath}"
        module_node = Node(
            id=module_id,
            type=NodeType.MODULE,
            name=filepath.stem,
            domain="code",
            description=f"Python module: {filepath}",
            properties={"path": str(filepath)},
        )
        self.graph.nodes[module_id] = module_node
        stats["modules_added"] += 1

        # Scan for classes and functions
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                self._process_class(node, module_id, filepath, stats)
            elif isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                # Only top-level functions (not methods)
                if hasattr(node, "col_offset") and node.col_offset == 0:
                    self._process_function(node, module_id, filepath, stats)

        # OPUS-155: Scan for imports and calls (Nervous System)
        self._scan_imports(tree, module_id, filepath, stats)
        self._scan_calls(tree, module_id, filepath, stats)

    def _process_class(self, node: ast.ClassDef, module_id: str, filepath: Path, stats: Dict) -> None:
        """Process a class definition."""
        class_id = f"class:{filepath}:{node.name}"

        # Get base classes
        bases = []
        is_abc = False
        for base in node.bases:
            if isinstance(base, ast.Name):
                bases.append(base.id)
                if base.id == "ABC":
                    is_abc = True
            elif isinstance(base, ast.Attribute):
                bases.append(base.attr)
                if base.attr == "ABC":
                    is_abc = True

        # Determine node type
        node_type = NodeType.INTERFACE if is_abc else NodeType.CLASS

        # Create class node
        class_node = Node(
            id=class_id,
            type=node_type,
            name=node.name,
            domain="code",
            description=f"{'Interface' if is_abc else 'Class'}: {node.name}",
            properties={
                "path": str(filepath),
                "line": node.lineno,
                "bases": bases,
                "is_abc": is_abc,
            },
        )
        self.graph.nodes[class_id] = class_node

        if is_abc:
            stats["interfaces_added"] += 1
        else:
            stats["classes_added"] += 1

        # Create DEFINES edge (module -> class)
        defines_edge = Edge(
            source=module_id,
            target=class_id,
            relation=RelationType.DEFINES,
        )
        if module_id not in self.graph.edges:
            self.graph.edges[module_id] = []
        self.graph.edges[module_id].append(defines_edge)

        # Create INHERITS edges
        for base in bases:
            inherits_edge = Edge(
                source=class_id,
                target=f"class:*:{base}",  # Wildcard - resolved in second pass
                relation=RelationType.INHERITS,
                properties={"base_name": base},
            )
            if class_id not in self.graph.edges:
                self.graph.edges[class_id] = []
            self.graph.edges[class_id].append(inherits_edge)

        # Register for duplicate detection
        self._class_registry[node.name].append(
            {
                "id": class_id,
                "path": str(filepath),
                "line": node.lineno,
                "bases": frozenset(bases),
                "is_abc": is_abc,
            }
        )

    def _process_function(self, node, module_id: str, filepath: Path, stats: Dict) -> None:
        """Process a top-level function definition."""
        func_id = f"function:{filepath}:{node.name}"

        func_node = Node(
            id=func_id,
            type=NodeType.FUNCTION,
            name=node.name,
            domain="code",
            description=f"Function: {node.name}",
            properties={
                "path": str(filepath),
                "line": node.lineno,
                "is_async": isinstance(node, ast.AsyncFunctionDef),
            },
        )
        self.graph.nodes[func_id] = func_node
        stats["functions_added"] += 1

        # Create DEFINES edge
        defines_edge = Edge(
            source=module_id,
            target=func_id,
            relation=RelationType.DEFINES,
        )
        if module_id not in self.graph.edges:
            self.graph.edges[module_id] = []
        self.graph.edges[module_id].append(defines_edge)

    def _detect_duplicates(self) -> int:
        """
        Detect duplicate class definitions.

        A duplicate is when:
        - Same class name
        - Same base classes
        - Different files

        Returns:
            Number of duplicate groups found
        """
        duplicates_found = 0

        for class_name, locations in self._class_registry.items():
            if len(locations) < 2:
                continue

            # Group by base classes
            by_bases: Dict[frozenset, List[Dict]] = defaultdict(list)
            for loc in locations:
                by_bases[loc["bases"]].append(loc)

            # Check for duplicates (same bases, multiple locations)
            for bases, locs in by_bases.items():
                if len(locs) > 1:
                    duplicates_found += 1

                    # Create DUPLICATES edges between all pairs
                    for i, loc1 in enumerate(locs):
                        for loc2 in locs[i + 1 :]:
                            edge = Edge(
                                source=loc1["id"],
                                target=loc2["id"],
                                relation=RelationType.DUPLICATES,
                                properties={
                                    "class_name": class_name,
                                    "severity": "critical" if loc1["is_abc"] else "high",
                                },
                            )
                            if loc1["id"] not in self.graph.edges:
                                self.graph.edges[loc1["id"]] = []
                            self.graph.edges[loc1["id"]].append(edge)

                    logger.warning(
                        f"🔴 DUPLICATE: {class_name} defined in {len(locs)} files (bases: {list(bases) or 'none'})"
                    )

        return duplicates_found

    def get_duplicates(self) -> List[Dict]:
        """
        Get all duplicate class groups.

        Returns:
            List of {class_name, locations, severity} dicts
        """
        duplicates = []

        for class_name, locations in self._class_registry.items():
            if len(locations) < 2:
                continue

            # Group by base classes
            by_bases: Dict[frozenset, List[Dict]] = defaultdict(list)
            for loc in locations:
                by_bases[loc["bases"]].append(loc)

            for bases, locs in by_bases.items():
                if len(locs) > 1:
                    duplicates.append(
                        {
                            "class_name": class_name,
                            "bases": list(bases),
                            "locations": [{"path": loc["path"], "line": loc["line"]} for loc in locs],
                            "severity": "critical" if locs[0]["is_abc"] else "high",
                            "count": len(locs),
                        }
                    )

        return sorted(duplicates, key=lambda d: (d["severity"], -d["count"]))

    def query_classes_with_duplicates(self) -> List[Node]:
        """
        Query the graph for all classes that have DUPLICATES edges.

        This is the graph-based equivalent of the regex scanner!

        Returns:
            List of class nodes that are duplicated
        """
        duplicated = []

        for node_id, node in self.graph.nodes.items():
            if node.type not in (NodeType.CLASS, NodeType.INTERFACE):
                continue

            # Check if this node has any DUPLICATES edges
            edges = self.graph.edges.get(node_id, [])
            for edge in edges:
                if edge.relation == RelationType.DUPLICATES:
                    duplicated.append(node)
                    break

        return duplicated

    # =========================================================================
    # OPUS-155: Akasha Nervous System - Import/Call Tracking
    # =========================================================================

    def _scan_imports(self, tree: ast.AST, module_id: str, filepath: Path, stats: Dict) -> None:
        """
        OPUS-155: Scan for import statements and create IMPORTS edges.

        These are the Nadis (नाडी) - the wires/channels between modules.
        Each import creates a connection in the nervous system.

        Args:
            tree: The AST of the module
            module_id: The module node ID
            filepath: Path to the source file
            stats: Statistics dict to update
        """
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                # import foo, bar
                for alias in node.names:
                    target_module = alias.name
                    self._create_import_edge(module_id, target_module, filepath, weight=1.0, stats=stats)

            elif isinstance(node, ast.ImportFrom):
                # from foo import bar, baz
                if node.module:
                    # Weight by number of names imported
                    weight = len(node.names) if node.names else 1.0
                    self._create_import_edge(module_id, node.module, filepath, weight=weight, stats=stats)

    def _create_import_edge(
        self,
        source_id: str,
        target_module: str,
        source_path: Path,
        weight: float,
        stats: Dict,
    ) -> None:
        """Create an IMPORTS edge between modules."""
        # Normalize target module to potential file path
        target_id = f"module:{target_module}"

        edge = Edge(
            source=source_id,
            target=target_id,
            relation=RelationType.IMPORTS,
            weight=weight,
            properties={
                "source_path": str(source_path),
                "target_module": target_module,
            },
        )

        if source_id not in self.graph.edges:
            self.graph.edges[source_id] = []
        self.graph.edges[source_id].append(edge)
        stats["imports_added"] += 1

    def _scan_calls(self, tree: ast.AST, module_id: str, filepath: Path, stats: Dict) -> None:
        """
        OPUS-155: Scan for function calls and create CALLS edges.

        These are the Prana (प्राण) - the sparks/energy flowing through the system.
        Tracks which functions are called and how often.

        Args:
            tree: The AST of the module
            module_id: The module node ID
            filepath: Path to the source file
            stats: Statistics dict to update
        """
        from collections import Counter

        call_counts: Counter = Counter()

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                call_target = None

                if isinstance(node.func, ast.Attribute):
                    # obj.method() style - track the method name
                    call_target = node.func.attr
                elif isinstance(node.func, ast.Name):
                    # direct_call() style
                    call_target = node.func.id

                if call_target:
                    call_counts[call_target] += 1

        # Create edges for significant call patterns (called 2+ times)
        for target, count in call_counts.items():
            if count >= 2:
                target_id = f"function:*:{target}"  # Wildcard - any module

                edge = Edge(
                    source=module_id,
                    target=target_id,
                    relation=RelationType.CALLS,
                    weight=float(count),
                    properties={
                        "source_path": str(filepath),
                        "call_target": target,
                        "call_count": count,
                    },
                )

                if module_id not in self.graph.edges:
                    self.graph.edges[module_id] = []
                self.graph.edges[module_id].append(edge)
                stats["calls_added"] += 1

    def get_import_graph(self) -> Dict[str, List[str]]:
        """
        Get a simplified import graph for visualization.

        Returns:
            Dict mapping module_id to list of imported module names
        """
        import_graph = {}

        for source_id, edges in self.graph.edges.items():
            if not source_id.startswith("module:"):
                continue

            imports = []
            for edge in edges:
                if edge.relation == RelationType.IMPORTS:
                    imports.append(edge.properties.get("target_module", edge.target))

            if imports:
                import_graph[source_id] = imports

        return import_graph

    def get_hot_modules(self, min_imports: int = 5) -> List[Tuple[str, int]]:
        """
        Find modules with many incoming imports (high coupling).

        These are the "hot" modules that many others depend on.
        High heat = potential architectural risk if changed.

        Args:
            min_imports: Minimum import count to be considered "hot"

        Returns:
            List of (module_id, import_count) tuples, sorted by count
        """
        import_counts: Dict[str, int] = defaultdict(int)

        for source_id, edges in self.graph.edges.items():
            for edge in edges:
                if edge.relation == RelationType.IMPORTS:
                    target = edge.properties.get("target_module", "")
                    import_counts[target] += 1

        hot = [(mod, count) for mod, count in import_counts.items() if count >= min_imports]
        return sorted(hot, key=lambda x: -x[1])

    # =========================================================================
    # OPUS-155: Resonance Calculation (Electrical Proximity)
    # =========================================================================

    def calculate_import_resonance(self, source_path: str, target_module: str) -> float:
        """
        Calculate the resonance between source and target based on layer distance.

        Uses OPUS-114 Varga mapping:
        - Same layer: 1.0 (perfect harmony)
        - Adjacent layers: 0.8 (natural flow)
        - 2 layers apart: 0.6 (moderate)
        - 3 layers apart: 0.4 (weak)
        - 4 layers apart: 0.2 (electrical noise)

        Args:
            source_path: Path to the source module
            target_module: Name of the target module (may not be a path)

        Returns:
            Resonance score (0.0 to 1.0)
        """
        try:
            from vibe_core.plugins.opus_assistant.manas.akshara import (
                Varga,
                map_path_to_varga,
            )

            # Get source Varga from path
            source_varga = map_path_to_varga(source_path)

            # Try to map target module to a path
            # If it's a stdlib module (logging, pathlib, etc.), default to TALAVYA
            if "." not in target_module and "/" not in target_module:
                # Likely a stdlib or third-party module
                target_varga = Varga.TALAVYA  # Neutral cognitive layer
            else:
                # Convert module path to file path
                target_path = target_module.replace(".", "/") + ".py"
                target_varga = map_path_to_varga(target_path)

            # Calculate resonance based on Varga distance
            distance = abs(source_varga.value - target_varga.value)
            resonance_map = {0: 1.0, 1: 0.8, 2: 0.6, 3: 0.4, 4: 0.2}
            return resonance_map.get(distance, 0.1)

        except ImportError:
            # If akshara not available, return neutral resonance
            return 0.5

    def get_dissonant_imports(self, threshold: float = 0.4) -> List[Dict]:
        """
        Find imports with low resonance (cross-layer violations).

        These are the "electrical noise" points in the architecture.
        High dissonance = potential architectural smell.

        Args:
            threshold: Maximum resonance to be considered dissonant

        Returns:
            List of {source, target, resonance} dicts for dissonant imports
        """
        dissonant = []

        for source_id, edges in self.graph.edges.items():
            if not source_id.startswith("module:"):
                continue

            source_path = source_id.replace("module:", "")

            for edge in edges:
                if edge.relation != RelationType.IMPORTS:
                    continue

                target_module = edge.properties.get("target_module", "")
                resonance = self.calculate_import_resonance(source_path, target_module)

                if resonance <= threshold:
                    dissonant.append(
                        {
                            "source": source_path,
                            "target": target_module,
                            "resonance": resonance,
                            "weight": edge.weight,
                            "friction": (1.0 - resonance) * edge.weight,
                        }
                    )

        # Sort by friction (highest first)
        return sorted(dissonant, key=lambda x: -x["friction"])

    def get_friction_heatmap(self) -> Dict[str, float]:
        """
        Calculate friction score for each module.

        High friction = many cross-layer imports = architectural smell.
        Low friction = clean layer boundaries = healthy design.

        Returns:
            Dict mapping module path to friction score
        """
        friction_map: Dict[str, float] = defaultdict(float)

        for source_id, edges in self.graph.edges.items():
            if not source_id.startswith("module:"):
                continue

            source_path = source_id.replace("module:", "")

            for edge in edges:
                if edge.relation != RelationType.IMPORTS:
                    continue

                target_module = edge.properties.get("target_module", "")
                resonance = self.calculate_import_resonance(source_path, target_module)

                # Friction is inverse of resonance, weighted by import weight
                friction = (1.0 - resonance) * edge.weight
                friction_map[source_path] += friction

        return dict(friction_map)

    def get_pain_points(self, threshold: float = 5.0) -> List[Tuple[str, float]]:
        """
        Find modules with high accumulated friction.

        These are the architectural pain points that need attention.

        Args:
            threshold: Minimum friction to be considered a pain point

        Returns:
            List of (module_path, friction_score) tuples
        """
        friction = self.get_friction_heatmap()
        pain = [(mod, score) for mod, score in friction.items() if score >= threshold]
        return sorted(pain, key=lambda x: -x[1])
