#!/usr/bin/env python3
"""
OUROBOROS: Tech Debt -> Training Fuel Converter

This script is the BRIDGE between static tech debt reports and the
self-healing Ouroboros loop. It uses VEDA-4 compliant discovery to find
violation sources and parsers.

"Die Schuld ist nicht zu tilgen, sie ist zu verdauen."
(The debt is not to be paid off, it is to be digested.)

Usage:
    python scripts/ci/ingest_report.py              # Auto-discover sources
    python scripts/ci/ingest_report.py --status     # Show discovery status
    python scripts/ci/ingest_report.py --list       # List discovered sources

Architecture:
    ViolationSourceLoader -> Discovers files (REPORT.md, TESTS.md, etc.)
    ViolationParserLoader -> Discovers parsers for each file type
    ViolationIngester     -> Feeds violations into Knowledge Graph

The Ouroboros loop then:
1. Manas Mirror Room reads these violations
2. Generates training curriculum from patterns
3. System learns to prevent recurrence
"""

import argparse
import sys
from pathlib import Path

# VEDA-4 Loaders
from vibe_core.ouroboros import (
    ViolationIngester,
    ViolationSourceLoader,
    get_parser_loader,
    get_source_loader,
)

# Boot Prakriti (registers KG in ServiceRegistry)
from vibe_core.state.prakriti import Prakriti


def show_status():
    """Show loader status (GAD-000: Observability)."""
    print("\n[OUROBOROS] Discovery Status")
    print("=" * 60)

    # Parser status
    parser_loader = get_parser_loader()
    parser_status = parser_loader.status()

    print("\n[Parsers]")
    print(f"  Loaded: {parser_status['loaded']}")
    for name, info in parser_status["parsers"].items():
        print(f"    - {name}: {info['class']}")
        print(f"      Patterns: {info['patterns']}")

    # Source status
    print("\n[Scan Paths]")
    source_loader = get_source_loader(project_root=Path(__file__).parent.parent.parent)
    source_status = source_loader.status()

    for path in source_status["scan_paths"]:
        exists = Path(path).exists()
        status = "OK" if exists else "MISSING"
        print(f"    [{status}] {path}")

    # Discovered sources
    print(f"\n[Discovered Sources] ({source_status['discovered']} total)")
    for source_info in source_status["sources"]:
        print(f"    - {source_info['name']} (parser: {source_info['parser']})")
        print(f"      Path: {source_info['path']}")

    print("\n" + "=" * 60)


def list_sources():
    """List all discovered sources (GAD-000: Discoverability)."""
    project_root = Path(__file__).parent.parent.parent
    source_loader = get_source_loader(project_root=project_root)
    sources = source_loader.discover_sources()

    print(f"\n[OUROBOROS] Discovered {len(sources)} violation source files:\n")

    for source in sources:
        try:
            rel_path = source.path.relative_to(project_root)
        except ValueError:
            rel_path = source.path
        print(f"  {rel_path}")
        print(f"    Parser: {source.parser_name}")
        print(f"    Patterns: {source.patterns_matched}")
        print()


def ingest_all():
    """Ingest all discovered violation sources."""
    print("[OUROBOROS] Ingesting Tech Debt as Training Fuel...")
    print("=" * 60)

    project_root = Path(__file__).parent.parent.parent

    # Boot Prakriti (registers KG in ServiceRegistry)
    prakriti = Prakriti()

    # Get loaders
    parser_loader = get_parser_loader()
    source_loader = get_source_loader(project_root=project_root)

    # Discover sources
    sources = source_loader.discover_sources()
    print(f"\n[DISCOVERY] Found {len(sources)} violation sources")

    for source in sources:
        try:
            rel_path = source.path.relative_to(project_root)
        except ValueError:
            rel_path = source.path
        print(f"  - {rel_path} (parser: {source.parser_name})")

    # Create ingester
    ingester = ViolationIngester()

    # Parse and ingest each source
    total_violations = 0
    for source in sources:
        parser = parser_loader.get_parser(source.parser_name)
        if parser is None:
            print(f"\n[WARNING] No parser found for {source.name}")
            continue

        print(f"\n[PARSING] {source.name}...")
        try:
            violations = parser.parse(source.path)
            print(f"  Found {len(violations)} violations")

            if violations:
                count = ingester.ingest(violations)
                total_violations += count
                print(f"  Ingested {count} violations")

        except Exception as e:
            print(f"  [ERROR] Failed to parse: {e}")

    # Summary
    print("\n" + "=" * 60)
    print(f"[SUMMARY] Ingested {total_violations} total violations")
    print("[NEXT] Mirror.analyze_violations() to see patterns")
    print("[NEXT] Mirror.generate_violation_curriculum() for training")

    return 0


def main():
    parser = argparse.ArgumentParser(
        description="OUROBOROS: Ingest tech debt as training fuel",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
GAD-000 Compliance:
  - Discoverability: --list shows all discoverable sources
  - Observability: --status shows loader state
  - Composability: Parsers and sources are pluggable
        """,
    )
    parser.add_argument("--status", "-s", action="store_true", help="Show discovery status")
    parser.add_argument("--list", "-l", action="store_true", help="List discovered sources")
    parser.add_argument(
        "--add-path",
        "-a",
        type=Path,
        action="append",
        help="Add custom scan path",
    )

    args = parser.parse_args()

    if args.status:
        show_status()
        return 0

    if args.list:
        list_sources()
        return 0

    return ingest_all()


if __name__ == "__main__":
    sys.exit(main())
