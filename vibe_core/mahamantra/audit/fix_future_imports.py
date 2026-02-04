"""
FIX FUTURE IMPORTS
==================

Moves 'from __future__' imports to the top of the file.
Recovering from 'heal_mahamantra.py' regression.
"""

from pathlib import Path
import re

def fix_file(path: Path):
    content = path.read_text()
    lines = content.splitlines()
    
    future_imports = []
    other_lines = []
    
    # Extract future imports
    for line in lines:
        if line.startswith("from __future__ import"):
            future_imports.append(line)
        else:
            other_lines.append(line)
            
    if not future_imports:
        return

    # Reconstruct
    # 1. Docstring (if exists)
    # 2. Future imports
    # 3. Rest
    
    new_lines = []
    docstring_end_safeguard = 0
    in_docstring = False
    
    # Simple docstring detection (first lines)
    # If first line is """ or ''', we are in docstring.
    # But files might start with comments.
    
    # SAFE STRATEGY:
    # Just put future imports after the first block of comments/docstrings.
    # OR, if unsure, put them at the VERY TOP (valid even before docstring? No, docstring must be first).
    # Docstring MUST be first statement. Future must be second.
    
    # Let's try to detect where to insert.
    # Usually index 0 or 1.
    
    # We will iterate `other_lines` and find the insertion point.
    
    # Current busted state:
    # 1. Docstring
    # 2. SEED IMPORT
    # 3. ...
    # N. Future Import
    
    # We stripped Future Import.
    # Now valid state:
    # 1. Docstring
    # 2. SEED IMPORT ...
    
    # We want:
    # 1. Docstring
    # 2. Future Import
    # 3. SEED IMPORT
    
    # So we search for the end of docstring.
    
    idx = 0
    if len(other_lines) > 0 and (other_lines[0].startswith('"""') or other_lines[0].startswith("'''")):
        # Identify end of docstring
        quote = other_lines[0][:3]
        if other_lines[0].count(quote) >= 2 and len(other_lines[0]) > 3:
             # Single line docstring
             idx = 1
        else:
            # Multi line
            idx = 1
            while idx < len(other_lines):
                if quote in other_lines[idx]:
                    idx += 1
                    break
                idx += 1
    
    # Insert future imports at idx
    final_lines = other_lines[:idx] + future_imports + other_lines[idx:]
    
    new_content = "\n".join(final_lines)
    if content.strip() != new_content.strip():
        # Only check if meaningfully changed (ignoring whitespace diffs from splitlines)
        if content != new_content + "\n" and content != new_content:
             print(f"Fixing {path}")
             path.write_text(new_content + "\n")

def main():
    root = Path("vibe_core/mahamantra/substrate")
    for path in root.rglob("*.py"):
        fix_file(path)

    root = Path("vibe_core/mahamantra/kernel")
    for path in root.rglob("*.py"):
        fix_file(path)

    # Protocols too checking
    root = Path("vibe_core/mahamantra/protocols")
    for path in root.rglob("*.py"):
         fix_file(path)

if __name__ == "__main__":
    main()
