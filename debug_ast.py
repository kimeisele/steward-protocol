
import ast
from pathlib import Path

code = Path("vibe_core/cartridges/system/civic/tools/dashboard_tool.py").read_text()
tree = ast.parse(code)

for node in ast.walk(tree):
    if isinstance(node, ast.Call):
        if isinstance(node.func, ast.Name) and node.func.id == "open":
            print(f"FOUND open() at line {node.lineno}")
            for arg in node.args:
                print(f"  Arg: {ast.dump(arg)}")
            for kw in node.keywords:
                print(f"  KW: {kw.arg}={ast.dump(kw.value)}")
