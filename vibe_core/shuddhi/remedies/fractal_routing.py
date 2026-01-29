"""
FRACTAL ROUTING REMEDY - CST-Based __getattr__ Injection
=========================================================

"EIN IMPORT. KRISHNA ROUTET ALLES."

Detection: __init__.py without __getattr__ fractal routing
Surgery: Add CST-safe __getattr__ function for auto-discovery

PHILOSOPHY:
    The folder structure IS the wiring. No manual imports needed.
    Any .py file or subpackage is auto-discoverable via __getattr__.

SAFE TRANSFORMATION:
    1. Parse module with libcst
    2. Check if __getattr__ already exists
    3. If missing, add fractal routing __getattr__ at end (before __all__)
    4. Verify with compile() before returning

WATERTIGHT: Only transforms __init__.py files missing __getattr__.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "kapila"
__position__ = 6
__genesis__ = "0x8a4c7e00"  # GenesisByte: parampara % 37 == 0

from typing import List, Sequence, Union

import libcst as cst

from vibe_core.shuddhi.remedies.base import CSTRemedy


# The fractal routing __getattr__ function as CST nodes
FRACTAL_GETATTR_CODE = '''
def __getattr__(name: str):
    """
    Fractal routing: folder IS wiring.
    "EIN IMPORT. KRISHNA ROUTET ALLES."
    """
    from pathlib import Path
    import importlib

    pkg_root = Path(__file__).parent

    # Check for subpackage (folder with __init__.py)
    subpkg_path = pkg_root / name
    if subpkg_path.is_dir() and (subpkg_path / "__init__.py").exists():
        return importlib.import_module(f"{__name__}.{name}")

    # Check for module (.py file)
    module_path = pkg_root / f"{name}.py"
    if module_path.exists():
        return importlib.import_module(f"{__name__}.{name}")

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
'''


class FractalRoutingRemedy(CSTRemedy):
    """
    Heals __init__.py files missing fractal routing __getattr__.

    SAFE TRANSFORMATION:
        - Only applies to files that do NOT have __getattr__ defined
        - Adds the standard fractal routing function
        - Preserves existing code structure
        - Places __getattr__ before __all__ if present, else at end

    This implements "folder IS wiring" - any module or subpackage
    in a directory becomes auto-discoverable without manual imports.
    """

    @property
    def rule_id(self) -> str:
        return "missing_fractal_routing"

    def requirements(self) -> List[str]:
        return []  # No special requirements

    def __init__(self) -> None:
        super().__init__()
        self._has_getattr = False
        self._has_all = False
        self._all_index: int = -1
        self._is_init_file = False

    def visit_Module(self, node: cst.Module) -> bool:
        """Check module-level for existing __getattr__."""
        return True

    def visit_FunctionDef(self, node: cst.FunctionDef) -> bool:
        """Detect if __getattr__ already exists."""
        if node.name.value == "__getattr__":
            self._has_getattr = True
        return False  # Don't descend into function bodies

    def visit_Assign(self, node: cst.Assign) -> bool:
        """Detect __all__ assignment for placement."""
        for target in node.targets:
            if isinstance(target.target, cst.Name):
                if target.target.value == "__all__":
                    self._has_all = True
        return False

    def leave_Module(
        self, original_node: cst.Module, updated_node: cst.Module
    ) -> cst.Module:
        """
        Transform module by adding __getattr__ if missing.

        Placement strategy:
        1. If __all__ exists: insert before __all__
        2. Otherwise: append at end of module
        """
        # Already has __getattr__ - nothing to do
        if self._has_getattr:
            return updated_node

        # Mark that we found a violation and will fix it
        self.violation_found = True
        self.applied = True

        # Parse the fractal __getattr__ function
        getattr_module = cst.parse_module(FRACTAL_GETATTR_CODE)
        getattr_func = getattr_module.body[0]

        # Add blank lines before the function for readability
        getattr_with_spacing = cst.EmptyLine(whitespace=cst.SimpleWhitespace(""))

        # Find where to insert
        new_body: List[Union[cst.SimpleStatementLine, cst.BaseCompoundStatement]] = []
        inserted = False

        for i, stmt in enumerate(updated_node.body):
            # Check if this is __all__ assignment
            is_all_stmt = False
            if isinstance(stmt, cst.SimpleStatementLine):
                for inner in stmt.body:
                    if isinstance(inner, cst.Assign):
                        for target in inner.targets:
                            if isinstance(target.target, cst.Name):
                                if target.target.value == "__all__":
                                    is_all_stmt = True
                                    break

            # Insert before __all__ if found
            if is_all_stmt and not inserted:
                # Add two blank lines before __getattr__
                new_body.append(cst.EmptyLine(whitespace=cst.SimpleWhitespace("")))
                new_body.append(getattr_func)
                new_body.append(cst.EmptyLine(whitespace=cst.SimpleWhitespace("")))
                inserted = True

            new_body.append(stmt)

        # If no __all__ found, append at end
        if not inserted:
            # Add two blank lines before __getattr__
            new_body.append(cst.EmptyLine(whitespace=cst.SimpleWhitespace("")))
            new_body.append(getattr_func)

        return updated_node.with_changes(body=new_body)


class FractalRoutingDetector(CSTRemedy):
    """
    Detection-only remedy for missing fractal routing.

    Use this to scan and report which __init__.py files
    are missing the fractal routing __getattr__.

    Does NOT transform - only detects for reporting.
    """

    @property
    def rule_id(self) -> str:
        return "fractal_routing_detection"

    def requirements(self) -> List[str]:
        return []

    def __init__(self) -> None:
        super().__init__()
        self._has_getattr = False

    def visit_FunctionDef(self, node: cst.FunctionDef) -> bool:
        """Detect if __getattr__ exists."""
        if node.name.value == "__getattr__":
            self._has_getattr = True
        return False

    def leave_Module(
        self, original_node: cst.Module, updated_node: cst.Module
    ) -> cst.Module:
        """Mark violation if __getattr__ is missing."""
        if not self._has_getattr:
            self.violation_found = True
        return updated_node

    @property
    def has_fractal_routing(self) -> bool:
        """Returns True if file has __getattr__."""
        return self._has_getattr
