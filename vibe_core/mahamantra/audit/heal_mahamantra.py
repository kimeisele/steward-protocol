"""
HEAL MAHAMANTRA - The Compliance Surgeon
========================================

"The surgeon cuts to heal."

This script uses LibCST to:
1. Replace Magic Numbers with SSOT Constants.
2. Remove 'Any' types (Actionable: Replace with 'object' or 'None').
3. Inject necessary imports from `protocols._seed`.

TARGET: vibe_core/mahamantra/substrate
"""

import libcst as cst
from libcst import matchers as m
from pathlib import Path
import sys

# MAPPING: Value -> Constant Name
CONSTANTS_MAP = {
    16: "WORDS",
    3: "TRINITY",
    4: "QUARTERS",
    8: "HARE_COUNT",
    2: "HALVES",
    5: "PANCHA",
    10: "TEN",
    7: "SEVEN",
    37: "PARAMPARA",
    108: "MALA",
    18: "GITA_CHAPTERS",
    64: "QUALITIES",
    137: "MAHA_QUANTUM",
    24: "KSHETRA",
    1: "KSETRAJNA",
    9: "NAVA",
    6: "SHARANAGATI",
    12: "MAHAJANA_COUNT",
    48: "LILA",
    136: "POSITION_SUM_TOTAL",
    70: "POSITION_SUM_HARE",
    17: "POSITION_SUM_KRISHNA",
    49: "POSITION_SUM_RAMA",
}

# IGNORE THESE (keep as numbers)
IGNORE_VALUES = {0, -1}


class HealingTransformer(cst.CSTTransformer):
    def __init__(self):
        self.needed_imports = set()
        self.modified = False
        self.in_import = False  # State tracking

    def visit_Import(self, node: cst.Import) -> None:
        self.in_import = True

    def leave_Import(self, original_node: cst.Import, updated_node: cst.Import) -> cst.Import:
        self.in_import = False
        return updated_node

    def visit_ImportFrom(self, node: cst.ImportFrom) -> None:
        self.in_import = True

    def leave_ImportFrom(self, original_node: cst.ImportFrom, updated_node: cst.ImportFrom) -> cst.ImportFrom:
        self.in_import = False
        return updated_node

    def leave_Integer(self, original_node: cst.Integer, updated_node: cst.Integer) -> cst.BaseExpression:
        try:
            # Use ast.literal_eval for safe parsing of 0x, 0b, etc.
            import ast

            val = ast.literal_eval(original_node.value)
            if val in CONSTANTS_MAP and val not in IGNORE_VALUES:
                name = CONSTANTS_MAP[val]
                self.needed_imports.add(name)
                self.modified = True
                return cst.Name(value=name)
        except (ValueError, SyntaxError):
            pass
        return updated_node

    def leave_Name(self, original_node: cst.Name, updated_node: cst.Name) -> cst.Name:
        # Replace Any with object, BUT skip imports
        if self.in_import:
            return updated_node

        if original_node.value == "Any":
            self.modified = True
            return updated_node.with_changes(value="object")

        return updated_node

    def leave_Attribute(self, original_node: cst.Attribute, updated_node: cst.Attribute) -> cst.BaseExpression:
        # Handle typing.Any -> object
        # structure: Attribute(value=Name(typing), attr=Name(Any))
        # leave_Name matches inner nodes first.
        # If we replaced Any->object in leave_Name, we get typing.object which is valid-ish but ugly.
        # Ideally we want just 'object'.

        # If leave_Name already ran, updated_node.attr might be 'object'.
        if m.matches(updated_node, m.Attribute(value=m.Name("typing"), attr=m.Name("object"))):
            self.modified = True
            return cst.Name(value="object")

        if m.matches(updated_node, m.Attribute(value=m.Name("typing"), attr=m.Name("Any"))):
            self.modified = True
            return cst.Name(value="object")

        return updated_node


class ImportInjector(cst.CSTTransformer):
    def __init__(self, needed_imports: set):
        self.needed_imports = sorted(list(needed_imports))
        self.injected = False

    def leave_Module(self, original_node: cst.Module, updated_node: cst.Module) -> cst.Module:
        if not self.needed_imports:
            return updated_node

        # Check if import already exists (simplistic check)
        # Better: Add to the first ImportFrom found, or top of file.

        # Construct the import statement
        # from vibe_core.mahamantra.protocols._seed import (A, B, C)

        names = [cst.ImportAlias(name=cst.Name(n)) for n in self.needed_imports]
        import_stmt = cst.ImportFrom(
            module=cst.parse_expression("vibe_core.mahamantra.protocols._seed"),
            names=names,
            lpar=cst.LeftParen(),
            rpar=cst.RightParen(),
        )

        # Insert at top (after docstring)
        new_body = list(updated_node.body)

        # Find insertion point (after docstring, before other imports ideally)
        # For now, just prepend to body, LibCST handles spacing somewhat
        new_body.insert(1, cst.SimpleStatementLine(body=[import_stmt]))  # Index 1 assuming docstring is 0

        return updated_node.with_changes(body=new_body)


def heal_file(path: Path):
    if "_seed" in path.name or "seed/" in str(path):
        print(f"Skipping SEED file: {path}")
        return

    print(f"Healing {path}...")
    source = path.read_text()

    try:
        wrapper = cst.MetadataWrapper(cst.parse_module(source))
        transformer = HealingTransformer()
        new_wrapper = wrapper.visit(transformer)

        if transformer.modified:
            # Need to inject imports?
            if transformer.needed_imports:
                injector = ImportInjector(transformer.needed_imports)
                new_module = new_wrapper.visit(injector)
                path.write_text(new_module.code)
            else:
                path.write_text(new_wrapper.code)
            print("  -> HEALED")
        else:
            print("  -> CLEAN")

    except Exception as e:
        print(f"  -> ERROR: {e}")


def main():
    root = Path("vibe_core/mahamantra/substrate")
    for path in root.rglob("*.py"):
        heal_file(path)

    # Also target Kernel
    root = Path("vibe_core/mahamantra/kernel")
    for path in root.rglob("*.py"):
        heal_file(path)

    # Also target Protocols
    root = Path("vibe_core/mahamantra/protocols")
    for path in root.rglob("*.py"):
        heal_file(path)


if __name__ == "__main__":
    main()
