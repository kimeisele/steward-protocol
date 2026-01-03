#!/usr/bin/env python3
"""
OUROBOROS: Tech Debt → Training Fuel Converter

This script is the BRIDGE between static tech debt reports and the
self-healing Ouroboros loop. It parses REPORT.md and TESTS.md,
extracts violations, and feeds them into the Knowledge Graph.

"Die Schuld ist nicht zu tilgen, sie ist zu verdauen."
(The debt is not to be paid off, it is to be digested.)

Usage:
    python scripts/ci/ingest_report.py

The Ouroboros loop then:
1. Manas Mirror Room reads these violations
2. Generates training curriculum from patterns
3. System learns to prevent recurrence
"""

import json
import re
import sys
from pathlib import Path
from typing import List, Tuple

from vibe_core.di import ServiceRegistry
from vibe_core.knowledge.graph import UnifiedKnowledgeGraph
from vibe_core.ouroboros.ingestion import ViolationIngester, ViolationRecord, ViolationSource

# Boot Prakriti to get ServiceRegistry wired up
from vibe_core.state.prakriti import Prakriti


def parse_report_md(report_path: Path) -> List[ViolationRecord]:
    """
    Parse REPORT.md and extract violations.

    Patterns detected:
    - A-P0-*, B-P0-*, etc. (Priority 0 issues)
    - PROMPT.md violations
    - AI-Slop patterns
    """
    violations = []

    if not report_path.exists():
        print(f"REPORT.md not found at {report_path}")
        return violations

    content = report_path.read_text()

    # Pattern 1: Section headers with priority (e.g., "### A-P0: KRITISCH")
    priority_sections = re.findall(r"###\s+([A-Z]-P[0-3]):\s+(\w+)[^\n]*\n(.+?)(?=###|\Z)", content, re.DOTALL)

    for section_id, severity, section_content in priority_sections:
        # Extract individual findings (e.g., "#### A-P0-1: VFS Sandbox Escape")
        findings = re.findall(
            r"####\s+(" + section_id.replace("-", r"-") + r"-\d+):\s+([^\n]+)\n\*\*Datei:\*\*\s+`([^`]+)`",
            section_content,
        )

        for finding_id, title, file_path in findings:
            # Map severity
            severity_map = {"P0": "CRITICAL", "P1": "HIGH", "P2": "MEDIUM", "P3": "LOW"}
            priority = section_id.split("-")[1]

            violations.append(
                ViolationRecord(
                    source=ViolationSource.WATCHMAN,
                    rule_id=f"REPORT:{finding_id}",
                    file_path=file_path.split(":")[0] if ":" in file_path else file_path,
                    line=int(file_path.split(":")[1].split("-")[0]) if ":" in file_path else None,
                    message=title,
                    severity=severity_map.get(priority, "MEDIUM"),
                    has_remedy=not section_id.startswith("A"),  # A = VISNU protected, can't fix
                    context={"section": section_id, "source": "REPORT.md"},
                )
            )

    # Pattern 2: PROMPT.md violations from the summary table
    prompt_violations = re.findall(r"\|\s+\*\*([^*]+)\*\*\s+\|\s+(\d+)\s+\|\s+([^|]+)\s+\|", content)

    for metric, count, violation_desc in prompt_violations:
        if int(count) > 0:
            violations.append(
                ViolationRecord(
                    source=ViolationSource.WATCHMAN,
                    rule_id=f"PROMPT:{metric.replace(' ', '_')}",
                    file_path="vibe_core/",  # Codebase-wide
                    line=None,
                    message=f"{count} instances: {violation_desc.strip()}",
                    severity="HIGH" if "KRITISCH" in violation_desc or int(count) > 100 else "MEDIUM",
                    has_remedy=True,
                    context={"metric": metric, "count": int(count), "source": "REPORT.md"},
                )
            )

    return violations


def parse_tests_md(tests_path: Path) -> List[ViolationRecord]:
    """
    Parse TESTS.md and extract test coverage gaps.

    These become training scenarios for "write more tests" patterns.
    """
    violations = []

    if not tests_path.exists():
        print(f"TESTS.md not found at {tests_path}")
        return violations

    content = tests_path.read_text()

    # Pattern: Modules without tests from the table
    # | doc_renderer.py | 743 | 0 | ⚠️ HOCH |
    untested_modules = re.findall(r"\|\s+([a-z_]+\.py)\s+\|\s+(\d+)\s+\|\s+0\s+\|\s+[^|]+\|", content)

    for module_name, lines in untested_modules:
        violations.append(
            ViolationRecord(
                source=ViolationSource.CI_TEST,
                rule_id="TESTS:UNTESTED_MODULE",
                file_path=f"vibe_core/{module_name}",
                line=None,
                message=f"{module_name} has {lines} lines with 0 tests",
                severity="HIGH" if int(lines) > 500 else "MEDIUM",
                has_remedy=True,
                context={"module": module_name, "lines": int(lines), "source": "TESTS.md"},
            )
        )

    # Pattern: Low test ratios
    low_ratio_modules = re.findall(r"\|\s+([A-Za-z_]+)\s+\|\s+(\d+)\s+\|\s+(\d+)\s+\|\s+([\d.]+%)\s+\|", content)

    for module, lines, tests, ratio in low_ratio_modules:
        ratio_float = float(ratio.replace("%", ""))
        if ratio_float < 1.0 and int(tests) > 0:
            violations.append(
                ViolationRecord(
                    source=ViolationSource.CI_TEST,
                    rule_id="TESTS:LOW_COVERAGE",
                    file_path=f"vibe_core/{module.lower()}/",
                    line=None,
                    message=f"{module}: {tests} tests for {lines} lines ({ratio} coverage)",
                    severity="MEDIUM",
                    has_remedy=True,
                    context={"module": module, "ratio": ratio_float, "source": "TESTS.md"},
                )
            )

    return violations


def discover_violation_sources(project_root: Path) -> List[Path]:
    """
    Auto-discover violation source files.

    Looks for:
    - REPORT.md, TESTS.md (standard names)
    - *_AUDIT.md, *_REPORT.md (pattern match)
    - Files in .prakriti/violations/ (if exists)

    Returns paths sorted by modification time (newest first).
    """
    sources = []

    # Standard files
    for name in ["REPORT.md", "TESTS.md", "REAL_TECH_DEBT_AUDIT.md"]:
        path = project_root / name
        if path.exists():
            sources.append(path)

    # Pattern match in docs/
    docs_dir = project_root / "docs"
    if docs_dir.exists():
        for pattern in ["*AUDIT*.md", "*REPORT*.md"]:
            sources.extend(docs_dir.glob(f"**/{pattern}"))

    # Deduplicate and sort by mtime
    seen = set()
    unique = []
    for p in sources:
        if p not in seen:
            seen.add(p)
            unique.append(p)

    return sorted(unique, key=lambda p: p.stat().st_mtime, reverse=True)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="OUROBOROS: Ingest tech debt as training fuel")
    parser.add_argument("--report", "-r", type=Path, help="Path to REPORT.md (auto-discovered if not specified)")
    parser.add_argument("--tests", "-t", type=Path, help="Path to TESTS.md (auto-discovered if not specified)")
    parser.add_argument("--discover", "-d", action="store_true", help="Auto-discover all violation sources")
    args = parser.parse_args()

    print("🐍 OUROBOROS: Ingesting Tech Debt as Training Fuel...")
    print("=" * 60)

    # Paths - either from args or auto-discover
    project_root = Path(__file__).parent.parent.parent

    if args.discover:
        sources = discover_violation_sources(project_root)
        print(f"\n🔍 Auto-discovered {len(sources)} violation sources:")
        for s in sources:
            print(f"   - {s.relative_to(project_root)}")
        report_path = next((s for s in sources if "REPORT" in s.name.upper()), None)
        tests_path = next((s for s in sources if "TEST" in s.name.upper()), None)
    else:
        report_path = args.report or project_root / "REPORT.md"
        tests_path = args.tests or project_root / "TESTS.md"

    # Boot Prakriti (registers KG in ServiceRegistry)
    prakriti = Prakriti()

    # Get or create Knowledge Graph
    kg = ServiceRegistry.get(UnifiedKnowledgeGraph)
    if kg is None:
        kg = UnifiedKnowledgeGraph()
        ServiceRegistry.register(UnifiedKnowledgeGraph, kg)

    # Create ingester
    ingester = ViolationIngester(kg)

    # Parse and ingest REPORT.md
    print(f"\n📄 Parsing {report_path.name}...")
    report_violations = parse_report_md(report_path)
    print(f"   Found {len(report_violations)} violations")

    # Parse and ingest TESTS.md
    print(f"\n📄 Parsing {tests_path.name}...")
    test_violations = parse_tests_md(tests_path)
    print(f"   Found {len(test_violations)} test gaps")

    # Combine and ingest
    all_violations = report_violations + test_violations

    print(f"\n📥 Ingesting {len(all_violations)} total violations...")
    count = ingester.ingest(all_violations)
    print(f"   Ingested {count} violations into Knowledge Graph")

    # Save to disk (persist knowledge graph state)
    try:
        from vibe_core.state.synapse_store import get_synapse_store

        # KG persists automatically on add_violation, but we can explicitly save synapses
        pass  # Knowledge Graph uses in-memory storage by default
    except Exception:
        pass  # Non-critical

    # Summary by rule_id
    print("\n📊 Violations by Rule ID:")
    by_rule = {}
    for v in all_violations:
        by_rule.setdefault(v.rule_id, []).append(v)

    for rule_id, vs in sorted(by_rule.items(), key=lambda x: -len(x[1]))[:10]:
        print(f"   {rule_id}: {len(vs)}")

    print("\n" + "=" * 60)
    print("✅ Tech Debt ingested. The Ouroboros loop can now digest it.")
    print("   Run: Mirror.analyze_violations() to see patterns")
    print("   Run: Mirror.generate_violation_curriculum() for training")

    return 0


if __name__ == "__main__":
    sys.exit(main())
