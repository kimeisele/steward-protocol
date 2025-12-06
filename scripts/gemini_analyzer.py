import ast
import re
from collections import Counter, defaultdict
from pathlib import Path

# Configuration
ROOT_DIR = Path("vibe_core")
EXCLUDE_DIRS = {"__pycache__", "tests", "data", "archive"}


def get_all_python_files(root):
    files = []
    for path in root.rglob("*.py"):
        if not any(part in EXCLUDE_DIRS for part in path.parts):
            files.append(path)
    return files


def analyze_dead_code(files):
    print("\n## 1. DEAD CODE FOUND")
    print("| File | Line | Type | Code |")
    print("|------|------|------|------|")

    # 1. Find all defined classes and functions
    definitions = defaultdict(list)

    # 2. Build a frequency map of all words in the codebase
    word_counts = Counter()

    for file_path in files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                # Tokenize and count
                words = re.findall(r"\b\w+\b", content)
                word_counts.update(words)

                # Parse for definitions
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        definitions[node.name].append((str(file_path), node.lineno, "class"))
                    elif isinstance(node, ast.FunctionDef):
                        if not node.name.startswith("__"):  # Ignore magic methods
                            definitions[node.name].append((str(file_path), node.lineno, "function"))
        except Exception:
            continue

    # 3. Check usage
    unused_count = 0
    for name, locs in definitions.items():
        # Skip common names to avoid noise
        if len(name) < 4 or name in ["main", "run", "execute", "process", "load", "save", "update"]:
            continue

        # If the count in the codebase equals the number of definitions, it means it's never used elsewhere
        # (Assuming definitions don't contain the name multiple times, which is true for ClassDef/FunctionDef nodes)
        # However, we need to be careful. A class name appears in its definition.
        # If I define `class Foo:`, "Foo" appears once.
        # If I use `Foo()`, "Foo" appears again.
        # So if count == len(locs), it's likely unused.

        if word_counts[name] <= len(locs):
            for file_path, lineno, type_ in locs:
                print(f"| {file_path} | {lineno} | unused_{type_} | {type_} {name} |")
                unused_count += 1
                if unused_count >= 50:  # Limit output
                    return


def analyze_circular_dependencies(files):
    print("\n## 2. CIRCULAR DEPENDENCIES")

    imports = defaultdict(set)

    for file_path in files:
        module_name = str(file_path).replace("/", ".").replace(".py", "")
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                tree = ast.parse(f.read())
                for node in ast.walk(tree):
                    if isinstance(node, ast.ImportFrom):
                        if node.module:
                            target = node.module
                            if target.startswith("vibe_core"):
                                imports[module_name].add(target)
                    elif isinstance(node, ast.Import):
                        for alias in node.names:
                            if alias.name.startswith("vibe_core"):
                                imports[module_name].add(alias.name)
        except Exception:
            continue

    # Detect cycles (DFS)
    visited = set()
    path = []
    cycles = []

    def visit(node):
        if node in path:
            cycle = path[path.index(node) :] + [node]
            cycles.append(cycle)
            return
        if node in visited:
            return

        visited.add(node)
        path.append(node)
        for neighbor in imports.get(node, []):
            visit(neighbor)
        path.pop()

    for node in list(imports.keys()):
        visit(node)
        if len(cycles) >= 5:
            break

    if cycles:
        for i, cycle in enumerate(cycles):
            print(f"- Cycle {i + 1}: {' -> '.join(cycle)}")
    else:
        print("No obvious import cycles found via static analysis.")


def analyze_missing_implementations(files):
    print("\n## 3. MISSING IMPLEMENTATIONS")
    print("| File | Line | Issue |")
    print("|------|------|-------|")

    for file_path in files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
                for i, line in enumerate(lines):
                    if "pass" in line.strip() and line.strip() == "pass":
                        print(f"| {file_path} | {i + 1} | `pass` stub detected |")
                    if "TODO" in line or "FIXME" in line:
                        clean_line = line.strip().replace("|", r"\|")[:50]
                        print(f"| {file_path} | {i + 1} | {clean_line} |")
        except Exception:
            continue


def analyze_architecture_violations(files):
    print("\n## 4. ARCHITECTURE VIOLATIONS")
    print("| File | Line | Violation |")
    print("|------|------|-----------|")

    for file_path in files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
                for i, line in enumerate(lines):
                    if '"data/' in line or "'data/" in line:
                        print(f"| {file_path} | {i + 1} | Hardcoded path to data/ |")
        except Exception:
            continue


def analyze_security(files):
    print("\n## 5. SECURITY ISSUES")
    print("| Severity | File | Issue |")
    print("|----------|------|-------|")

    for file_path in files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        bases = [b.id for b in node.bases if isinstance(b, ast.Name)]
                        if "VibeAgent" in bases or "ContextAwareAgent" in bases:
                            if "OathMixin" not in bases:
                                print(f"| HIGH | {file_path} | Agent class `{node.name}` missing `OathMixin` |")
        except Exception:
            continue


def main():
    print("# GEMINI ANALYSIS REPORT\n")
    files = get_all_python_files(ROOT_DIR)

    analyze_dead_code(files)
    analyze_circular_dependencies(files)
    analyze_missing_implementations(files)
    analyze_architecture_violations(files)
    analyze_security(files)

    print("\n## 6. RECOMMENDED DELETIONS")
    print("Files safe to delete (based on 0 imports - requires external validation):")
    print("- (Manual verification required based on Dead Code section)")

    print("\n## 7. PRIORITY FIX LIST")
    print("1. [HIGH] Fix Security Issues (Missing Oaths)")
    print("2. [MED] Resolve Circular Dependencies")
    print("3. [LOW] Clean up Dead Code")


if __name__ == "__main__":
    main()
