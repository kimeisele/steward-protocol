"""
NULL SIGNATURE REMEDY - Heals Null* Classes With Required Arguments.

"karmany evadhikaras te ma phalesu kadacana"
"You have a right to perform your prescribed duty, but you are not entitled to the fruits of action."
— Bhagavad Gita 2.47

DETECTION: Null* classes with methods that have required positional arguments
SURGERY: Add default values based on type hints (str="", int=0, None for complex types)

THE PROBLEM:
    CLI calls methods without arguments: execute("tick")
    Null* methods require arguments: def analyze(self, target: AnalysisInput)
    Result: TypeError: missing 1 required positional argument

THE REMEDY:
    Transform: def analyze(self, target: AnalysisInput) -> ...
    To:        def analyze(self, target: AnalysisInput = None) -> ...

DERIVED FROM MAHAMANTRA:
    Position 6 (Kapila) - Analysis/Type-checking
    The remedy ANALYZES signatures and TRANSFORMS them
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "kapila"
__position__ = 6
__genesis__ = "0x25d36ba1"  # GenesisByte: parampara % 37 == 0

from typing import List, Optional, Sequence, Union

import libcst as cst
from libcst import matchers as m

from vibe_core.mahamantra.dharma.kapila.remedies.base import CSTRemedy

# Type hint → default value mapping (DERIVED, not hardcoded)
TYPE_DEFAULTS = {
    "str": '""',
    "int": "0",
    "float": "0.0",
    "bool": "False",
    "bytes": 'b""',
    "list": "None",
    "dict": "None",
    "List": "None",
    "Dict": "None",
    "Optional": "None",
    "Path": "None",
}


class NullSignatureRemedy(CSTRemedy):
    """
    Heals Null* classes by adding default values to method parameters.

    SAFETY:
        - Only transforms Null* classes
        - Only adds defaults to non-self, non-cls parameters
        - Preserves type hints
    """

    def __init__(self):
        super().__init__()
        self._in_null_class = False
        self._class_name = ""
        self._methods_fixed = 0

    @property
    def rule_id(self) -> str:
        return "null_signature_mismatch"

    def requirements(self) -> List[str]:
        return []

    def visit_ClassDef(self, node: cst.ClassDef) -> bool:
        """Track when we enter a Null* class."""
        name = node.name.value
        if name.startswith("Null"):
            self._in_null_class = True
            self._class_name = name
        return True

    def leave_ClassDef(self, original_node: cst.ClassDef, updated_node: cst.ClassDef) -> cst.ClassDef:
        """Exit Null* class tracking."""
        if original_node.name.value.startswith("Null"):
            self._in_null_class = False
            self._class_name = ""
        return updated_node

    def leave_FunctionDef(self, original_node: cst.FunctionDef, updated_node: cst.FunctionDef) -> cst.FunctionDef:
        """Add default values to method parameters in Null* classes."""
        if not self._in_null_class:
            return updated_node

        # Skip dunder methods except __init__
        method_name = updated_node.name.value
        if method_name.startswith("__") and method_name != "__init__":
            return updated_node

        params = updated_node.params
        new_params = []
        modified = False

        for param in params.params:
            # Skip self/cls
            if param.name.value in ("self", "cls"):
                new_params.append(param)
                continue

            # Check if already has default
            if param.default is not None:
                new_params.append(param)
                continue

            # Needs default - determine based on type hint
            default_value = self._get_default_for_type(param.annotation)

            if default_value:
                self.violation_found = True
                self.applied = True
                self._methods_fixed += 1
                modified = True

                # Create new parameter with default
                new_param = param.with_changes(default=cst.parse_expression(default_value))
                new_params.append(new_param)
            else:
                new_params.append(param)

        if modified:
            new_params_obj = params.with_changes(params=new_params)
            return updated_node.with_changes(params=new_params_obj)

        return updated_node

    def _get_default_for_type(self, annotation: Optional[cst.Annotation]) -> Optional[str]:
        """Get default value based on type annotation."""
        if annotation is None:
            return "None"  # No type hint = None default

        # Extract type name from annotation
        type_str = self._annotation_to_string(annotation.annotation)

        # Check direct match
        if type_str in TYPE_DEFAULTS:
            return TYPE_DEFAULTS[type_str]

        # Check if Optional
        if type_str.startswith("Optional"):
            return "None"

        # Check if List/Dict/etc
        for key in TYPE_DEFAULTS:
            if type_str.startswith(key):
                return TYPE_DEFAULTS[key]

        # Default to None for complex types
        return "None"

    def _annotation_to_string(self, node: cst.BaseExpression) -> str:
        """Convert annotation node to string."""
        if isinstance(node, cst.Name):
            return node.value
        elif isinstance(node, cst.Attribute):
            return node.attr.value
        elif isinstance(node, cst.Subscript):
            if isinstance(node.value, cst.Name):
                return node.value.value
        return "unknown"

def heal_null_signatures(file_path: str, dry_run: bool = True) -> dict:
    """
    Heal Null* signature mismatches in a file.

    Args:
        file_path: Path to Python file
        dry_run: If True, only report changes

    Returns:
        Dict with status, methods_fixed, diff
    """
    from pathlib import Path

    path = Path(file_path)
    if not path.exists():
        return {"status": "error", "message": f"File not found: {file_path}"}

    source = path.read_text()

    try:
        tree = cst.parse_module(source)
    except Exception as e:
        return {"status": "error", "message": f"Parse error: {e}"}

    remedy = NullSignatureRemedy()
    new_tree = tree.visit(remedy)
    new_source = new_tree.code

    if not remedy.applied:
        return {"status": "skipped", "message": "No violations found"}

    result = {
        "status": "healed" if not dry_run else "would_heal",
        "methods_fixed": remedy._methods_fixed,
        "diff": remedy.get_diff(source, new_source),
    }

    if not dry_run:
        path.write_text(new_source)

    return result


def heal_all_null_signatures(dry_run: bool = True) -> dict:
    """
    Heal ALL Null* signature mismatches in the protocols/mahajanas folder.

    This is the SANKIRTAN healing - mass chanting across all files.
    """
    from pathlib import Path

    base_path = Path(__file__).parent.parent.parent / "protocols" / "mahajanas"

    stats = {"checked": 0, "healed": 0, "skipped": 0, "failed": 0}

    for py_file in base_path.rglob("*.py"):
        stats["checked"] += 1

        try:
            result = heal_null_signatures(str(py_file), dry_run=dry_run)

            if result["status"] in ("healed", "would_heal"):
                stats["healed"] += 1
            elif result["status"] == "skipped":
                stats["skipped"] += 1
            else:
                stats["failed"] += 1
        except Exception as e:
            stats["failed"] += 1

    return stats


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "NullSignatureRemedy",
    "heal_null_signatures",
    "heal_all_null_signatures",
]
