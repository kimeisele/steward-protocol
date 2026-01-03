"""
OPUS-212: LCOM4 Analyzer - The God Class Detector.

LCOM4 (Lack of Cohesion of Methods, version 4) measures structural cohesion
using graph theory. Unlike LCOM1-3, it accounts for both data usage AND
method invocations, producing an integer value that directly corresponds
to the number of architectural splits required.

Interpretation:
- LCOM4 = 1: Ideal. The class is a single cohesive unit.
- LCOM4 > 1: God Class. Should be split into LCOM4 separate classes.
- LCOM4 = 0: Degenerate case (no methods).

The connected components returned by the analysis provide the exact
refactoring roadmap: each component becomes a new class.
"""

import ast
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, FrozenSet, List, Optional, Set

try:
    import networkx as nx

    HAS_NETWORKX = True
except ImportError:
    HAS_NETWORKX = False


@dataclass
class LCOM4Result:
    """Result of LCOM4 analysis for a single class."""

    class_name: str
    score: int
    components: List[FrozenSet[str]]
    methods: Set[str]
    is_god_class: bool
    line: int
    col: int

    @property
    def refactoring_suggestion(self) -> Optional[str]:
        """Generate refactoring suggestion if score > 1."""
        if self.score <= 1:
            return None

        suggestions = []
        for i, component in enumerate(self.components, 1):
            methods_str = ", ".join(sorted(component))
            suggestions.append(f"  Class {i}: {{{methods_str}}}")

        return f"Split {self.class_name} into {self.score} classes:\n" + "\n".join(suggestions)


class LCOM4GraphBuilder(ast.NodeVisitor):
    """
    AST Visitor that extracts the Method-Attribute and Method-Method
    dependency graph for LCOM4 calculation.

    Excludes __init__ to prevent artificial cohesion (constructors
    typically initialize all attributes, masking poor cohesion).
    """

    def __init__(self):
        self.methods: Set[str] = set()
        self.method_accesses: Dict[str, Set[str]] = defaultdict(set)
        self.method_calls: Dict[str, Set[str]] = defaultdict(set)
        self.current_method: Optional[str] = None
        self.class_attrs: Set[str] = set()

    def visit_FunctionDef(self, node: ast.FunctionDef):
        """Visit method definitions."""
        # Skip __init__ and magic methods to prevent artificial cohesion
        if node.name.startswith("__"):
            return

        self.current_method = node.name
        self.methods.add(node.name)
        self.generic_visit(node)
        self.current_method = None

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        """Visit async method definitions."""
        if node.name.startswith("__"):
            return

        self.current_method = node.name
        self.methods.add(node.name)
        self.generic_visit(node)
        self.current_method = None

    def visit_Attribute(self, node: ast.Attribute):
        """Detect 'self.variable' usage."""
        if isinstance(node.value, ast.Name) and node.value.id == "self":
            if self.current_method:
                # Record attribute access (might be field or method)
                self.method_accesses[self.current_method].add(node.attr)
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call):
        """Detect 'self.method()' calls."""
        if isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name) and node.func.value.id == "self":
                if self.current_method:
                    self.method_calls[self.current_method].add(node.func.attr)
        self.generic_visit(node)


def calculate_lcom4(source_code: str) -> Dict[str, LCOM4Result]:
    """
    Calculate LCOM4 metric for all classes in the source code.

    Args:
        source_code: Python source code to analyze

    Returns:
        Dict mapping class names to LCOM4Result objects
    """
    if not HAS_NETWORKX:
        raise ImportError("NetworkX is required for LCOM4 analysis. Install with: pip install networkx")

    tree = ast.parse(source_code)
    results = {}

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            result = _analyze_class(node)
            if result:
                results[node.name] = result

    return results


def _analyze_class(class_node: ast.ClassDef) -> Optional[LCOM4Result]:
    """Analyze a single class for LCOM4."""
    builder = LCOM4GraphBuilder()
    builder.visit(class_node)

    if not builder.methods:
        return LCOM4Result(
            class_name=class_node.name,
            score=0,
            components=[],
            methods=set(),
            is_god_class=False,
            line=class_node.lineno,
            col=class_node.col_offset,
        )

    # Build the graph
    G = nx.Graph()
    G.add_nodes_from(builder.methods)

    # Add edges based on shared attributes
    attr_map: Dict[str, List[str]] = defaultdict(list)
    for method, attrs in builder.method_accesses.items():
        for attr in attrs:
            # Only consider attributes, not methods
            if attr not in builder.methods:
                attr_map[attr].append(method)

    for attr, methods in attr_map.items():
        # Connect every pair of methods sharing this attribute
        for i in range(len(methods)):
            for j in range(i + 1, len(methods)):
                G.add_edge(methods[i], methods[j])

    # Add edges based on method calls
    for caller, callees in builder.method_calls.items():
        for callee in callees:
            if callee in builder.methods:
                G.add_edge(caller, callee)

    # Compute connected components
    components = [frozenset(c) for c in nx.connected_components(G)]
    score = len(components)

    return LCOM4Result(
        class_name=class_node.name,
        score=score,
        components=components,
        methods=builder.methods,
        is_god_class=score > 1,
        line=class_node.lineno,
        col=class_node.col_offset,
    )


def analyze_file(file_path: Path) -> Dict[str, LCOM4Result]:
    """
    Analyze a Python file for God Classes using LCOM4.

    Args:
        file_path: Path to Python file

    Returns:
        Dict mapping class names to LCOM4Result objects
    """
    source_code = file_path.read_text()
    return calculate_lcom4(source_code)


def find_god_classes(source_code: str, threshold: int = 1) -> List[LCOM4Result]:
    """
    Find all God Classes (classes with LCOM4 > threshold).

    Args:
        source_code: Python source code
        threshold: LCOM4 score above which a class is considered a God Class

    Returns:
        List of LCOM4Result for God Classes
    """
    results = calculate_lcom4(source_code)
    return [r for r in results.values() if r.score > threshold]
