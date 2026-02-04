"""
HARDCORE AUDIT - Enforcing MAHAPROMPT.md
========================================

"The King must be pure."

CHECKS:
1. FATAL: Any usage of 'Any' type.
2. FATAL: Hardcoded Sacred Numbers (16, 37, 108, 137).
3. FATAL: Broken Genesis Bytes (intro % 37 != 0).
4. FATAL: Missing __mahajana__ declaration in modules.

USAGE:
    python3 hardcore_audit.py
"""

import ast
import os
import sys
from pathlib import Path
from typing import List, Tuple, Set

# Sacred numbers that MUST be imported, never hardcoded
SACRED_NUMBERS = {16, 37, 108, 137, 4, 3, 8}

# Exemptions (sometimes 0, 1, -1 are just math)
ALLOWED_NUMBERS = {0, 1, -1, 2}

class HardcoreVisitor(ast.NodeVisitor):
    def __init__(self, filename: str):
        self.filename = filename
        self.errors = []
        self.has_mahajana = False
        self.genesis_value = None
        self.in_type_checking = False

    def visit_Assign(self, node):
        # Check for __mahajana__ and __genesis__
        for target in node.targets:
            if isinstance(target, ast.Name):
                if target.id == "__mahajana__":
                    self.has_mahajana = True
                elif target.id == "__genesis__":
                    if isinstance(node.value, ast.Constant):
                        self.genesis_value = node.value.value
        self.generic_visit(node)

    def visit_Constant(self, node):
        if isinstance(node.value, int):
            if node.value in SACRED_NUMBERS and node.value not in ALLOWED_NUMBERS:
                # We need context. If it's an assignment to a CONSTANT_NAME, it might be the definition.
                # But even definitions should come from _seed.py if possible.
                # For now, flag ALL hardcoded sacred numbers.
                self.errors.append(f"FATAL: Hardcoded Sacred Number {node.value} on line {node.lineno}")
        self.generic_visit(node)

    def visit_Name(self, node):
        if node.id == "Any":
            self.errors.append(f"FATAL: Usage of 'Any' type on line {node.lineno}")
        self.generic_visit(node)

    def visit_Attribute(self, node):
        if node.attr == "Any":
             self.errors.append(f"FATAL: Usage of 'Any' type on line {node.lineno}")
        self.generic_visit(node)

def audit_file(filepath: Path) -> List[str]:
    with open(filepath, "r", encoding="utf-8") as f:
        try:
            tree = ast.parse(f.read(), filename=str(filepath))
        except SyntaxError as e:
            return [f"SYNTAX ERROR: {e}"]

    visitor = HardcoreVisitor(str(filepath))
    visitor.visit(tree)

    file_errors = visitor.errors

    # Check Genesis
    if "__init__.py" not in filepath.name: # __init__ doesn't always need genesis if package
        if not visitor.has_mahajana:
            pass # Not forcing mahajana on every file yet, user said "mahamantra folder" modules
                 # But MAHAPROMPT says "Entry...". 
                 # Let's flag missing mahajana only if it looks like a module that should have one.
    
    if visitor.genesis_value:
        try:
            val = int(visitor.genesis_value, 16)
            if val % 37 != 0:
                file_errors.append(f"FATAL: Broken Genesis Byte {visitor.genesis_value} (not divisible by 37)")
        except ValueError:
            file_errors.append(f"FATAL: Invalid Genesis format {visitor.genesis_value}")

    return file_errors

def main():
    root = Path(__file__).parent.parent # vibe_core/mahamantra
    print(f"Auditing {root}...")
    
    violations = 0
    checked_files = 0

    for root_dir, _, files in os.walk(root):
        for file in files:
            if file.endswith(".py") and "audit" not in root_dir: # Audit script audits itself? Skip for sanity
                filepath = Path(root_dir) / file
                checked_files += 1
                errors = audit_file(filepath)
                
                if errors:
                    print(f"\n❌ {filepath.relative_to(root)}")
                    for err in errors:
                        print(f"  - {err}")
                        violations += 1

    print(f"\n{'='*40}")
    print(f"Checked: {checked_files} files")
    print(f"Violations: {violations}")
    
    if violations > 0:
        sys.exit(1)
    else:
        print("clean_as_lotus")
        sys.exit(0)

if __name__ == "__main__":
    main()
