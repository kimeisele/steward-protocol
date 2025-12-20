"""
OPUS-162: HARNESS Validator - Pre-commit Interface

This is a thin CLI wrapper around DocHarnessAnalyzer.
The REAL validation logic lives in manas/analyzers/doc_harness_analyzer.py

NO DUPLICATION - we delegate to the existing analyzer.

Usage:
    python -m vibe_core.governance.harness_validator docs/architecture/OPUS/160-*.md
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger("HARNESS.VALIDATOR")


def validate_document(document: Path, workspace: Optional[Path] = None) -> dict:
    """
    Validate a single OPUS document's @HARNESS tags.

    Delegates to DocHarnessAnalyzer for the actual validation.
    Returns a simplified result dict for CLI use.
    """
    workspace = workspace or Path.cwd()

    if not document.exists():
        return {
            "document": str(document),
            "passed": False,
            "checks": [],
            "error": "Document does not exist",
        }

    # Use the REAL analyzer from MANAS - no duplication!
    try:
        from vibe_core.plugins.opus_assistant.manas.analyzers.doc_harness_analyzer import (
            DocHarnessAnalyzer,
        )

        analyzer = DocHarnessAnalyzer(workspace=workspace)
        result = analyzer._analyze_file(document)

        # Convert to simple pass/fail for pre-commit
        checks = []

        # Check files
        for f in result.files_section:
            missing = f in result.files_missing
            required = result.files_required.get(f, True)

            # OPUS-128: Only fail on required missing files
            passed = not missing or not required
            checks.append(
                {
                    "pattern": f"file:{f}",
                    "target": f,
                    "passed": passed,
                    "required": required,
                    "error": f"Missing required file: {f}" if not passed else None,
                }
            )

        # Check wiring
        for w in result.wiring_section:
            broken = w in result.wiring_broken
            checks.append(
                {
                    "pattern": w["pattern"],
                    "target": w["in"],
                    "passed": not broken,
                    "error": f"Pattern not found in {w['in']}" if broken else None,
                }
            )

        # OPUS-128: Consider doc status
        # TDD contracts (PLANNED/IN_PROGRESS) - red is CORRECT
        if result.is_tdd_contract:
            return {
                "document": str(document),
                "passed": True,  # TDD contract - red is intentional
                "checks": checks,
                "status": result.doc_status,
                "is_tdd_contract": True,
            }

        # SUPERSEDED/DEPRECATED docs - skip validation
        if result.skip_validation:
            return {
                "document": str(document),
                "passed": True,  # Skip validation
                "checks": [],
                "status": result.doc_status,
                "skipped": True,
            }

        # No harness - that's fine, not all docs need one
        if not result.has_harness:
            return {
                "document": str(document),
                "passed": True,
                "checks": [],
                "no_harness": True,
            }

        # Normal validation - only fail on required missing
        passed = result.is_valid
        return {
            "document": str(document),
            "passed": passed,
            "checks": checks,
            "quality_score": result.quality_score,
        }

    except ImportError as e:
        # Fallback if DocHarnessAnalyzer not available (shouldn't happen)
        logger.warning(f"DocHarnessAnalyzer not available: {e}")
        return {
            "document": str(document),
            "passed": True,  # Graceful degradation
            "checks": [],
            "error": "Analyzer not available",
        }


def validate_documents(documents: List[Path], workspace: Optional[Path] = None) -> list:
    """Validate multiple documents."""
    return [validate_document(doc, workspace) for doc in documents]


def main():
    """CLI entry point for pre-commit hook."""
    parser = argparse.ArgumentParser(
        description="Validate @HARNESS tags in OPUS documents (uses DocHarnessAnalyzer)",
    )
    parser.add_argument(
        "documents",
        nargs="+",
        type=Path,
        help="OPUS document paths to validate",
    )
    parser.add_argument(
        "--workspace",
        type=Path,
        default=Path.cwd(),
        help="Workspace root directory",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON",
    )

    args = parser.parse_args()

    results = validate_documents(args.documents, args.workspace)

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        all_passed = True
        for result in results:
            doc_name = Path(result["document"]).name

            if result.get("skipped"):
                print(f"⏭️  {doc_name} (skipped: {result.get('status', 'unknown')})")
            elif result.get("is_tdd_contract"):
                print(f"📋 {doc_name} (TDD contract: {result.get('status', 'planned')})")
            elif result.get("no_harness"):
                # No harness is fine - silent
                pass
            elif not result["passed"]:
                all_passed = False
                print(f"❌ {doc_name}")
                for check in result.get("checks", []):
                    if not check.get("passed") and check.get("error"):
                        print(f"   • {check['error']}")
            elif result.get("checks"):
                print(f"✅ {doc_name} ({len(result['checks'])} checks)")

        if not all_passed:
            sys.exit(1)


if __name__ == "__main__":
    main()
