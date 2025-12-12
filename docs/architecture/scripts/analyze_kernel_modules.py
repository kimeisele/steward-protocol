#!/usr/bin/env python3
"""
KERNEL MODULE ANALYZER
======================
Analyzes vibe_core/ structure, extracts module docstrings, maps dependencies.

Usage:
    python docs/architecture/scripts/analyze_kernel_modules.py

Output:
    - Module hierarchy with line counts
    - Docstrings that could become formal specs
    - Inter-module dependencies
    - Class/function inventory
"""

import ast
import re
from collections import defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
VIBE_CORE = PROJECT_ROOT / "vibe_core"


def count_lines(filepath: Path) -> int:
    """Count non-empty, non-comment lines."""
    try:
        content = filepath.read_text()
        lines = [ln for ln in content.split("\n") if ln.strip() and not ln.strip().startswith("#")]
        return len(lines)
    except Exception:
        return 0


def extract_module_info(filepath: Path) -> dict:
    """Extract docstring, classes, functions from a Python module."""
    info = {
        "path": str(filepath.relative_to(PROJECT_ROOT)),
        "lines": count_lines(filepath),
        "docstring": None,
        "classes": [],
        "functions": [],
        "imports": [],
        "gad_refs": [],
    }

    try:
        content = filepath.read_text()
        tree = ast.parse(content)

        # Module docstring
        if tree.body and isinstance(tree.body[0], ast.Expr) and isinstance(tree.body[0].value, ast.Constant):
            info["docstring"] = tree.body[0].value.value[:500]

        # Classes and functions
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_info = {"name": node.name, "methods": []}
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        class_info["methods"].append(item.name)
                info["classes"].append(class_info)

            elif isinstance(node, ast.FunctionDef) and node.col_offset == 0:
                info["functions"].append(node.name)

            elif isinstance(node, ast.Import):
                for alias in node.names:
                    info["imports"].append(alias.name)

            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    info["imports"].append(node.module)

        # GAD references in content
        gad_matches = re.findall(r"GAD-(\d+)", content)
        info["gad_refs"] = list(set(gad_matches))

    except Exception as e:
        info["error"] = str(e)

    return info


def analyze_directory(dirpath: Path, depth=0) -> list:
    """Recursively analyze a directory."""
    results = []

    if not dirpath.exists():
        return results

    # Get all Python files
    py_files = sorted(dirpath.glob("*.py"))
    subdirs = sorted([d for d in dirpath.iterdir() if d.is_dir() and not d.name.startswith("_")])

    for f in py_files:
        if f.name != "__init__.py":
            results.append(extract_module_info(f))

    for subdir in subdirs:
        if subdir.name != "__pycache__":
            results.extend(analyze_directory(subdir, depth + 1))

    return results


def main():
    print("=" * 70)
    print("KERNEL MODULE ANALYZER - vibe_core/ Deep Scan")
    print("=" * 70)
    print()

    modules = analyze_directory(VIBE_CORE)

    # Sort by lines (biggest first)
    modules.sort(key=lambda m: -m["lines"])

    # Summary
    total_lines = sum(m["lines"] for m in modules)
    total_classes = sum(len(m["classes"]) for m in modules)
    total_functions = sum(len(m["functions"]) for m in modules)

    print("📊 SUMMARY")
    print(f"   Total modules: {len(modules)}")
    print(f"   Total lines:   {total_lines:,}")
    print(f"   Total classes: {total_classes}")
    print(f"   Total functions: {total_functions}")
    print()

    # Top modules by size
    print("📦 TOP 15 MODULES BY SIZE:")
    print("-" * 70)
    for m in modules[:15]:
        gads = f" [GAD: {','.join(m['gad_refs'][:3])}]" if m["gad_refs"] else ""
        print(f"   {m['lines']:5} lines | {m['path']}{gads}")
    print()

    # Modules with docstrings (potential specs)
    print("📝 MODULES WITH SUBSTANTIAL DOCSTRINGS (potential specs):")
    print("-" * 70)
    for m in modules:
        if m["docstring"] and len(m["docstring"]) > 100:
            print(f"\n   📄 {m['path']} ({m['lines']} lines)")
            print(f"   GAD refs: {', '.join(m['gad_refs']) if m['gad_refs'] else 'None'}")
            # First 200 chars of docstring
            doc_preview = m["docstring"][:200].replace("\n", " ")
            print(f'   "{doc_preview}..."')
    print()

    # GAD coverage
    print("🔗 GAD REFERENCES PER MODULE:")
    print("-" * 70)
    gad_to_modules = defaultdict(list)
    for m in modules:
        for gad in m["gad_refs"]:
            gad_to_modules[gad].append(m["path"])

    for gad, paths in sorted(gad_to_modules.items(), key=lambda x: -len(x[1])):
        print(f"   GAD-{gad}: {len(paths)} modules")
        for p in paths[:3]:
            print(f"      - {p}")
        if len(paths) > 3:
            print(f"      ... and {len(paths) - 3} more")
    print()

    # Class inventory
    print("🏛️ CLASS INVENTORY (main classes):")
    print("-" * 70)
    for m in modules[:20]:
        if m["classes"]:
            print(f"\n   {m['path']}:")
            for cls in m["classes"][:5]:
                methods = ", ".join(cls["methods"][:5])
                if len(cls["methods"]) > 5:
                    methods += f", ... (+{len(cls['methods']) - 5})"
                print(f"      class {cls['name']}: [{methods}]")


if __name__ == "__main__":
    main()
