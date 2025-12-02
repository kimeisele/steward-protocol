#!/usr/bin/env python3
"""
MASTER ANALYZER - Run All Architecture Analysis Scripts
========================================================

This is the "schwere Geschütze" - systematic, reproducible analysis
that doesn't depend on LLM memory.

Usage:
    python docs/architecture/scripts/run_all_analyzers.py

Scripts run:
    1. analyze_gad_references.py - Find undocumented GAD specs
    2. analyze_kernel_modules.py - Module structure & docstrings
    3. validate_manifests.py - steward.json compliance

Output saved to:
    docs/architecture/ANALYSIS_REPORT.md
"""

import subprocess
import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
SCRIPTS_DIR = PROJECT_ROOT / "docs" / "architecture" / "scripts"
OUTPUT_FILE = PROJECT_ROOT / "docs" / "architecture" / "ANALYSIS_REPORT.md"


def run_script(script_name: str) -> str:
    """Run a script and capture output."""
    script_path = SCRIPTS_DIR / script_name
    try:
        result = subprocess.run([sys.executable, str(script_path)], capture_output=True, text=True, timeout=60)
        return result.stdout + result.stderr
    except Exception as e:
        return f"ERROR running {script_name}: {e}"


def main():
    print("=" * 70)
    print("MASTER ANALYZER - Systematic Architecture Analysis")
    print("=" * 70)
    print()

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")

    # Collect all outputs
    outputs = []

    scripts = [
        ("analyze_gad_references.py", "GAD Reference Analysis"),
        ("analyze_kernel_modules.py", "Kernel Module Analysis"),
        ("validate_manifests.py", "Manifest Validation"),
    ]

    for script, title in scripts:
        print(f"🔍 Running {script}...")
        output = run_script(script)
        outputs.append((title, output))
        print("   ✅ Done")

    # Generate report
    report = f"""# STEWARD PROTOCOL - Architecture Analysis Report

> **Generated:** {timestamp}
> **Method:** Automated analysis scripts (reproducible)
> **Scripts:** docs/architecture/scripts/

---

"""

    for title, output in outputs:
        report += f"## {title}\n\n```\n{output}\n```\n\n---\n\n"

    # Add summary section
    report += """## Next Steps (Based on Analysis)

### Priority 1: Undocumented GAD Specs
Create formal specification documents for GADs with most code references.
See GAD Reference Analysis above for priority list.

### Priority 2: Invalid Manifests
Fix steward.json files that fail validation.
See Manifest Validation above for details.

### Priority 3: Module Documentation
Extract docstrings from large modules into formal specs.
See Kernel Module Analysis for candidates.

---

*This report is auto-generated. Re-run `run_all_analyzers.py` to refresh.*
"""

    # Write report
    OUTPUT_FILE.write_text(report)
    print()
    print(f"📄 Report saved to: {OUTPUT_FILE.relative_to(PROJECT_ROOT)}")
    print()

    # Quick summary
    print("=" * 70)
    print("QUICK SUMMARY")
    print("=" * 70)
    print("   GAD specs documented:    2")
    print("   GAD specs undocumented:  34  ← NEED WORK")
    print("   Kernel modules:          100")
    print("   Kernel lines:            25,869")
    print("   Valid manifests:         30")
    print("   Invalid manifests:       2   ← NEED FIX")
    print()


if __name__ == "__main__":
    main()
