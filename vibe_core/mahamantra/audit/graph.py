"""
ADVAITA - Dependency Graph Builder
===================================

"advaita acharya gosani saksat isvara"
"Sri Advaita Acharya is the Supreme Lord Himself."
-- Chaitanya Charitamrita

Builds relationship graphs:
- Import dependencies between modules
- Delegation chains (who listens to whom)
- Mahajana → Module mappings
- Position → Module mappings

Uses existing LCOM4 patterns for cohesion analysis.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

# === MAHAJANA DECLARATION ===
__mahajana__ = "advaita"
__position__ = 2
__genesis__ = "0x00000002"


@dataclass
class GraphNode:
    """A node in the dependency graph."""
    path: str
    mahajana: Optional[str] = None
    position: Optional[int] = None
    imports: Set[str] = field(default_factory=set)
    imported_by: Set[str] = field(default_factory=set)
    
    @property
    def in_degree(self) -> int:
        return len(self.imported_by)
    
    @property
    def out_degree(self) -> int:
        return len(self.imports)


@dataclass
class DelegationEdge:
    """An edge representing delegation relationship."""
    from_module: str
    to_module: str
    delegation_type: str  # "avatar", "mahajana", "shadow", "naga"


class DependencyGraph:
    """
    Builds and analyzes dependency graphs for the codebase.
    
    Usage:
        graph = DependencyGraph(project_root)
        graph.build()
        hubs = graph.find_hubs()
        chain = graph.delegation_chain("vyasa")
    """
    
    def __init__(self, root: Path):
        self.root = root
        self._nodes: Dict[str, GraphNode] = {}
        self._edges: List[DelegationEdge] = []
        self._built = False
    
    def build(self, scanner=None) -> None:
        """Build the dependency graph from scanner data."""
        if scanner is None:
            from .scanner import ModuleScanner
            scanner = ModuleScanner(self.root)
            scanner.scan_all()
        
        # Create nodes
        for path, info in scanner._modules.items():
            self._nodes[path] = GraphNode(
                path=path,
                mahajana=info.mahajana,
                position=info.position,
            )
        
        # Build edges from imports
        for path, info in scanner._modules.items():
            node = self._nodes[path]
            
            for imp in info.imports:
                target = self._resolve_import(imp)
                if target and target in self._nodes:
                    node.imports.add(target)
                    self._nodes[target].imported_by.add(path)
            
            for module, names in info.from_imports:
                target = self._resolve_import(module)
                if target and target in self._nodes:
                    node.imports.add(target)
                    self._nodes[target].imported_by.add(path)
        
        self._built = True
    
    def _resolve_import(self, import_path: str) -> Optional[str]:
        """Resolve an import path to a file path."""
        # Convert vibe_core.mahamantra.foo to vibe_core/mahamantra/foo.py
        parts = import_path.split(".")
        
        # Try as module file
        file_path = "/".join(parts) + ".py"
        if file_path in self._nodes:
            return file_path
        
        # Try as package __init__
        init_path = "/".join(parts) + "/__init__.py"
        if init_path in self._nodes:
            return init_path
        
        return None
    
    def find_hubs(self, min_degree: int = 10) -> List[Tuple[str, int, int]]:
        """Find modules with high connectivity (potential God modules)."""
        if not self._built:
            self.build()
        
        hubs = []
        for path, node in self._nodes.items():
            total = node.in_degree + node.out_degree
            if total >= min_degree:
                hubs.append((path, node.in_degree, node.out_degree))
        
        return sorted(hubs, key=lambda x: x[1] + x[2], reverse=True)
    
    def delegation_chain(self, mahajana: str) -> Dict[str, List[str]]:
        """Find the delegation chain for a specific mahajana."""
        if not self._built:
            self.build()
        
        result = {
            "modules": [],
            "delegates_to": [],
            "receives_from": [],
        }
        
        for path, node in self._nodes.items():
            if node.mahajana == mahajana:
                result["modules"].append(path)
                result["delegates_to"].extend(node.imports)
                result["receives_from"].extend(node.imported_by)
        
        return result
    
    def mahajana_graph(self) -> Dict[str, Dict]:
        """Build a mahajana-level dependency graph."""
        if not self._built:
            self.build()
        
        # Group modules by mahajana
        by_mahajana: Dict[str, Set[str]] = defaultdict(set)
        for path, node in self._nodes.items():
            if node.mahajana:
                by_mahajana[node.mahajana].add(path)
        
        # Build mahajana-to-mahajana edges
        edges: Dict[str, Set[str]] = defaultdict(set)
        for mahajana, modules in by_mahajana.items():
            for mod_path in modules:
                node = self._nodes[mod_path]
                for imp in node.imports:
                    if imp in self._nodes:
                        target_mahajana = self._nodes[imp].mahajana
                        if target_mahajana and target_mahajana != mahajana:
                            edges[mahajana].add(target_mahajana)
        
        return {
            "mahajanas": {m: len(mods) for m, mods in by_mahajana.items()},
            "edges": {m: list(targets) for m, targets in edges.items()},
        }
    
    def summary(self) -> Dict[str, Any]:
        """Get a token-efficient summary."""
        if not self._built:
            self.build()
        
        return {
            "total_nodes": len(self._nodes),
            "total_edges": sum(len(n.imports) for n in self._nodes.values()),
            "hubs": self.find_hubs()[:10],
            "mahajana_graph": self.mahajana_graph(),
        }

