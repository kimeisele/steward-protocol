import ast
import json
import sys


def extract_docstrings(filepath):
    """
    Extracts module, class, and function docstrings from a Python file.
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            try:
                content = f.read()
                tree = ast.parse(content, filename=filepath)
            except Exception:
                # Ignore files that can't be parsed
                return None
    except FileNotFoundError:
        return None

    docstrings = {"file_path": filepath, "docstrings": []}

    # Module docstring
    module_docstring = ast.get_docstring(tree)
    if module_docstring:
        docstrings["docstrings"].append(
            {"type": "module", "name": filepath, "lineno": 1, "docstring": module_docstring}
        )

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            docstring = ast.get_docstring(node)
            if docstring:
                docstrings["docstrings"].append(
                    {"type": node.__class__.__name__, "name": node.name, "lineno": node.lineno, "docstring": docstring}
                )

    if not docstrings["docstrings"]:
        return None

    return docstrings


if __name__ == "__main__":
    all_docstrings = []

    files = []
    if len(sys.argv) > 1:
        files = sys.argv[1:]
    else:
        for line in sys.stdin:
            files.append(line.strip())

    for filepath in files:
        data = extract_docstrings(filepath)
        if data:
            all_docstrings.append(data)

    print(json.dumps(all_docstrings, indent=2))
