"""
Code Scanner - The Weaver's Eye

OPUS-110: Graph-based Gap Detection

Scans Python source code and populates the UnifiedKnowledgeGraph with:
- MODULE nodes (files)
- CLASS nodes (class definitions)
- FUNCTION nodes (function definitions)
- INTERFACE nodes (ABC classes)

Creates edges:
- DEFINES (module -> class/function)
- INHERITS (class -> parent)
- DUPLICATES (class -> class with same name + bases)

This enables graph-based queries like:
    graph.get_nodes_by_type(NodeType.CLASS)
        .filter(lambda n: graph.has_edge(n.id, RelationType.DUPLICATES))
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
            f"{stats['duplicates_found']} duplicates"
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
