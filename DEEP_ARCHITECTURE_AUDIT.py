#!/usr/bin/env python3
"""
DEEP ARCHITECTURE AUDIT - Finding the REAL Problems
====================================================

This audit goes DEEPER than surface-level pattern matching.
It analyzes the ACTUAL architecture and finds SSOT violations.
"""

import os
import re
import ast
import json
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set, Tuple

# SSOT Constants from _axioms.py
SSOT_AXIOMS = {
    "WORDS": 16,
    "TRINITY": 3,
    "HARE_COUNT": 8,
    "KRISHNA_COUNT": 4,
    "RAMA_COUNT": 4,
    "PANCHA": 5,
    "HALVES": 2,
}

# Known derived constants (should be computed, not hardcoded)
DERIVED_CONSTANTS = {
    "MAHA_QUANTUM": 137,  # Should be derived
    "PARAMPARA": 37,  # Should be derived
    "QUARTERS": 4,  # = WORDS // QUARTERS
    "HALF_SIZE": 8,  # = WORDS // HALVES
}


def find_hardcoded_magic_numbers(file_path: str) -> List[Dict]:
    """Find hardcoded magic numbers that should be SSOT constants."""
    findings = []
    magic_numbers = {16, 137, 37, 4, 8, 3, 5, 2}  # SSOT values

    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        # Skip if it's the SSOT file itself
        if "_axioms.py" in file_path or "_seed.py" in file_path:
            return []

        for i, line in enumerate(content.split("\n"), 1):
            # Skip comments and strings
            if line.strip().startswith("#"):
                continue

            # Find numeric literals
            for match in re.finditer(r"\b(\d+)\b", line):
                num = int(match.group(1))
                if num in magic_numbers:
                    # Check if it's already using a constant
                    if not any(const in line for const in SSOT_AXIOMS.keys()):
                        if not any(const in line for const in DERIVED_CONSTANTS.keys()):
                            findings.append(
                                {
                                    "file": file_path,
                                    "line": i,
                                    "number": num,
                                    "code": line.strip()[:80],
                                    "should_be": [
                                        k for k, v in {**SSOT_AXIOMS, **DERIVED_CONSTANTS}.items() if v == num
                                    ],
                                }
                            )
    except Exception as e:
        pass

    return findings


def find_duplicate_definitions(root_dir: str) -> Dict[str, List[str]]:
    """Find constants defined in multiple places (SSOT violations)."""
    definitions = defaultdict(list)

    for root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if d != "__pycache__" and not d.startswith(".")]

        for file in files:
            if not file.endswith(".py"):
                continue
            if "test" in file.lower():
                continue

            file_path = os.path.join(root, file)
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                # Find constant definitions
                for match in re.finditer(r"^([A-Z][A-Z_0-9]+)\s*[:=]", content, re.MULTILINE):
                    const_name = match.group(1)
                    definitions[const_name].append(file_path)
            except:
                pass

    # Filter to only duplicates
    return {k: v for k, v in definitions.items() if len(v) > 1}


def find_import_chaos(root_dir: str) -> Dict[str, int]:
    """Find files with excessive imports (complexity indicator)."""
    import_counts = {}

    for root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if d != "__pycache__" and not d.startswith(".")]

        for file in files:
            if not file.endswith(".py"):
                continue

            file_path = os.path.join(root, file)
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                imports = len(re.findall(r"^(?:from|import)\s+", content, re.MULTILINE))
                if imports > 20:  # Threshold for "too many imports"
                    import_counts[file_path] = imports
            except:
                pass

    return dict(sorted(import_counts.items(), key=lambda x: -x[1])[:20])


def find_circular_import_risk(root_dir: str) -> List[Tuple[str, str]]:
    """Find potential circular import patterns."""
    # Map file -> what it imports
    imports_map = {}

    for root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if d != "__pycache__" and not d.startswith(".")]

        for file in files:
            if not file.endswith(".py"):
                continue

            file_path = os.path.join(root, file)
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                imports = set()
                for match in re.finditer(r"from\s+([\w.]+)\s+import", content):
                    imports.add(match.group(1))
                imports_map[file_path] = imports
            except:
                pass

    # Find cycles (simplified - just direct mutual imports)
    cycles = []
    checked = set()
    for file_a, imports_a in imports_map.items():
        for file_b, imports_b in imports_map.items():
            if file_a >= file_b:
                continue
            pair = (file_a, file_b)
            if pair in checked:
                continue
            checked.add(pair)

            # Check if they import each other's modules
            module_a = file_a.replace("/", ".").replace(".py", "")
            module_b = file_b.replace("/", ".").replace(".py", "")

            if any(module_b in imp for imp in imports_a) and any(module_a in imp for imp in imports_b):
                cycles.append((file_a, file_b))

    return cycles[:20]  # Top 20


def analyze_file_complexity(root_dir: str) -> List[Dict]:
    """Find overly complex files (lines, functions, classes)."""
    complex_files = []

    for root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if d != "__pycache__" and not d.startswith(".")]

        for file in files:
            if not file.endswith(".py"):
                continue
            if "test" in file.lower():
                continue

            file_path = os.path.join(root, file)
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    lines = content.split("\n")

                line_count = len(lines)
                func_count = len(re.findall(r"^\s*def\s+", content, re.MULTILINE))
                class_count = len(re.findall(r"^\s*class\s+", content, re.MULTILINE))

                # Flag if too complex
                if line_count > 500 or func_count > 30 or class_count > 5:
                    complex_files.append(
                        {
                            "file": file_path,
                            "lines": line_count,
                            "functions": func_count,
                            "classes": class_count,
                            "complexity_score": line_count + func_count * 10 + class_count * 50,
                        }
                    )
            except:
                pass

    return sorted(complex_files, key=lambda x: -x["complexity_score"])[:30]


def main():
    print("=" * 80)
    print("DEEP ARCHITECTURE AUDIT - Finding the REAL Problems")
    print("=" * 80)
    print()

    root_dir = "vibe_core/mahamantra"

    # 1. Find hardcoded magic numbers
    print("🔍 SCANNING FOR HARDCODED MAGIC NUMBERS...")
    all_magic = []
    for root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for file in files:
            if file.endswith(".py") and "test" not in file.lower():
                findings = find_hardcoded_magic_numbers(os.path.join(root, file))
                all_magic.extend(findings)

    print(f"   Found {len(all_magic)} potential SSOT violations")
    print()

    # 2. Find duplicate definitions
    print("🔍 SCANNING FOR DUPLICATE CONSTANT DEFINITIONS...")
    duplicates = find_duplicate_definitions(root_dir)
    print(f"   Found {len(duplicates)} constants defined in multiple places")
    for const, files in list(duplicates.items())[:10]:
        print(f"      {const}: {len(files)} definitions")
    print()

    # 3. Find import chaos
    print("🔍 SCANNING FOR IMPORT CHAOS (>20 imports)...")
    import_chaos = find_import_chaos(root_dir)
    print(f"   Found {len(import_chaos)} files with excessive imports")
    for file, count in list(import_chaos.items())[:5]:
        print(f"      {file}: {count} imports")
    print()

    # 4. Find complex files
    print("🔍 SCANNING FOR OVERLY COMPLEX FILES...")
    complex_files = analyze_file_complexity(root_dir)
    print(f"   Found {len(complex_files)} overly complex files")
    for cf in complex_files[:10]:
        print(f"      {cf['file']}: {cf['lines']} lines, {cf['functions']} funcs, {cf['classes']} classes")
    print()

    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total SSOT violations (magic numbers): {len(all_magic)}")
    print(f"Total duplicate constant definitions: {len(duplicates)}")
    print(f"Total files with import chaos: {len(import_chaos)}")
    print(f"Total overly complex files: {len(complex_files)}")
    print()

    # Save detailed report
    report = {
        "magic_numbers": all_magic[:100],  # Top 100
        "duplicates": {k: v for k, v in list(duplicates.items())[:50]},
        "import_chaos": import_chaos,
        "complex_files": complex_files,
    }

    with open("DEEP_AUDIT_REPORT.json", "w") as f:
        json.dump(report, f, indent=2)

    print("✓ Detailed report saved to DEEP_AUDIT_REPORT.json")


if __name__ == "__main__":
    main()
