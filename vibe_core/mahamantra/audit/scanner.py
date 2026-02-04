"""
NITYANANDA - Module Scanner (File/Module Discovery)
====================================================

"nityananda-rupa haya gaura-avatar"
"Lord Nityananda is the form of Gauranga's avatar."
-- Chaitanya Charitamrita

The FOUNDATION of the Audit Agency. Scans all files, extracts:
- __mahajana__ declarations
- __position__ values
- __genesis__ bytes
- Import relationships
- Class/Function definitions
- Module structure

Imports production patterns from NaradaScanner.
"""

from __future__ import annotations

import ast
import hashlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

# === MAHAJANA DECLARATION ===
__mahajana__ = "nityananda"
__position__ = 1
__genesis__ = "0x00000001"


@dataclass
class ModuleInfo:
    """Complete information about a Python module."""
    path: Path
    relative_path: str
    
    # Declarations
    mahajana: Optional[str] = None
    position: Optional[int] = None
    genesis: Optional[str] = None
    
    # Structure
    imports: List[str] = field(default_factory=list)
    from_imports: List[tuple] = field(default_factory=list)  # (module, names)
    classes: List[str] = field(default_factory=list)
    functions: List[str] = field(default_factory=list)
    
    # Metrics
    loc: int = 0
    hash: str = ""
    
    # Errors during parsing
    parse_error: Optional[str] = None


class ModuleScanner:
    """
    Scans the codebase for Python modules and extracts structured information.
    
    Usage:
        scanner = ModuleScanner(project_root)
        modules = scanner.scan_all()
        mahajana_files = scanner.by_mahajana("vyasa")
    """
    
    def __init__(self, root: Path):
        self.root = root
        self._modules: Dict[str, ModuleInfo] = {}
        self._scanned = False
    
    def scan_all(self, include_patterns: List[str] = None) -> Dict[str, ModuleInfo]:
        """Scan all Python files in the project."""
        if include_patterns is None:
            include_patterns = ["vibe_core/**/*.py"]
        
        for pattern in include_patterns:
            for py_file in self.root.glob(pattern):
                if "__pycache__" in str(py_file):
                    continue
                self._scan_file(py_file)
        
        self._scanned = True
        return self._modules
    
    def _scan_file(self, file_path: Path) -> ModuleInfo:
        """Scan a single Python file."""
        relative = str(file_path.relative_to(self.root))
        
        info = ModuleInfo(
            path=file_path,
            relative_path=relative,
        )
        
        try:
            content = file_path.read_text(encoding="utf-8")
            info.loc = len(content.splitlines())
            info.hash = hashlib.sha256(content.encode()).hexdigest()[:16]
            
            tree = ast.parse(content)
            self._extract_from_ast(tree, info)
            
        except SyntaxError as e:
            info.parse_error = f"SyntaxError: {e}"
        except Exception as e:
            info.parse_error = f"{type(e).__name__}: {e}"
        
        self._modules[relative] = info
        return info
    
    def _extract_from_ast(self, tree: ast.AST, info: ModuleInfo) -> None:
        """Extract information from AST."""
        for node in ast.walk(tree):
            # Module-level assignments (declarations)
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        self._extract_declaration(target.name, node.value, info)
            
            # Imports
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    info.imports.append(alias.name)
            
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    names = [alias.name for alias in node.names]
                    info.from_imports.append((node.module, names))

        # Classes and functions (top-level only - not nested)
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.ClassDef):
                info.classes.append(node.name)

            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if not node.name.startswith("_") or node.name.startswith("__"):
                    info.functions.append(node.name)
    
    def _extract_declaration(self, name: str, value: ast.AST, info: ModuleInfo) -> None:
        """Extract __mahajana__, __position__, __genesis__ declarations."""
        # Handle both ast.Constant (Python 3.8+) and ast.Str/ast.Num (older)
        def get_value(node):
            if isinstance(node, ast.Constant):
                return node.value
            elif isinstance(node, ast.Str):  # Python < 3.8
                return node.s
            elif isinstance(node, ast.Num):  # Python < 3.8
                return node.n
            return None

        val = get_value(value)
        if name == "__mahajana__" and val is not None:
            info.mahajana = val
        elif name == "__position__" and val is not None:
            info.position = val
        elif name == "__genesis__" and val is not None:
            info.genesis = val
    
    def by_mahajana(self, mahajana: str) -> List[ModuleInfo]:
        """Get all modules declared for a specific mahajana."""
        if not self._scanned:
            self.scan_all()
        return [m for m in self._modules.values() if m.mahajana == mahajana]
    
    def by_position(self, position: int) -> List[ModuleInfo]:
        """Get all modules at a specific position."""
        if not self._scanned:
            self.scan_all()
        return [m for m in self._modules.values() if m.position == position]
    
    def summary(self) -> Dict[str, Any]:
        """Get a token-efficient summary of the scan."""
        if not self._scanned:
            self.scan_all()
        
        mahajana_count: Dict[str, int] = {}
        position_count: Dict[int, int] = {}
        total_loc = 0
        errors = []
        
        for m in self._modules.values():
            total_loc += m.loc
            if m.mahajana:
                mahajana_count[m.mahajana] = mahajana_count.get(m.mahajana, 0) + 1
            if m.position is not None:
                position_count[m.position] = position_count.get(m.position, 0) + 1
            if m.parse_error:
                errors.append((m.relative_path, m.parse_error))
        
        return {
            "total_files": len(self._modules),
            "total_loc": total_loc,
            "mahajana_distribution": mahajana_count,
            "position_distribution": position_count,
            "parse_errors": len(errors),
            "errors": errors[:10],  # First 10 errors only
        }

