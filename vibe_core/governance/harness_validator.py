"""
OPUS-162: HARNESS Validator

Syntactic validation of @HARNESS tags in OPUS documents.
Checks that expected patterns exist in target files.

Usage:
    python -m vibe_core.governance.harness_validator docs/architecture/OPUS/160-*.md
"""

import argparse
import json
import logging
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

logger = logging.getLogger("HARNESS.VALIDATOR")


@dataclass
class HarnessCheck:
    """Result of a single HARNESS check."""

    pattern: str
    target_file: str
    passed: bool
    is_regex: bool = False
    error: Optional[str] = None


@dataclass
class HarnessResult:
    """Result of validating a single document."""

    document: Path
    checks: List[HarnessCheck]
    passed: bool

    @property
    def failed_checks(self) -> List[HarnessCheck]:
        return [c for c in self.checks if not c.passed]


def extract_harness_tags(content: str) -> List[Dict[str, Any]]:
    """
    Extract @HARNESS YAML blocks from markdown content.

    Format:
    <!-- @HARNESS
    files:
      - path: some/file.py
        required: true
    wiring:
      - pattern: "from module import Class"
        in: some/file.py
    -->
    """
    harness_blocks = []

    # Match <!-- @HARNESS ... --> blocks
    pattern = r"<!--\s*@HARNESS\s*(.*?)-->"
    matches = re.findall(pattern, content, re.DOTALL)

    for match in matches:
        try:
            parsed = yaml.safe_load(match)
            if parsed:
                harness_blocks.append(parsed)
        except yaml.YAMLError as e:
            logger.warning(f"Failed to parse HARNESS YAML: {e}")

    return harness_blocks


def validate_harness(document: Path, workspace: Optional[Path] = None) -> HarnessResult:
    """
    Validate @HARNESS tags in a document.

    Args:
        document: Path to the OPUS document
        workspace: Workspace root (defaults to cwd)

    Returns:
        HarnessResult with all checks
    """
    workspace = workspace or Path.cwd()
    checks: List[HarnessCheck] = []

    if not document.exists():
        return HarnessResult(
            document=document,
            checks=[
                HarnessCheck(
                    pattern="document_exists",
                    target_file=str(document),
                    passed=False,
                    error="Document does not exist",
                )
            ],
            passed=False,
        )

    content = document.read_text()
    harness_blocks = extract_harness_tags(content)

    if not harness_blocks:
        # No HARNESS tags - that's fine, not all docs have them
        return HarnessResult(document=document, checks=[], passed=True)

    for block in harness_blocks:
        # Check files
        files = block.get("files", [])
        for file_spec in files:
            file_path = workspace / file_spec.get("path", "")
            required = file_spec.get("required", True)

            exists = file_path.exists()
            passed = exists or not required

            checks.append(
                HarnessCheck(
                    pattern=f"file:{file_spec.get('path')}",
                    target_file=str(file_path),
                    passed=passed,
                    error=None if passed else f"Required file missing: {file_path}",
                )
            )

        # Check wiring patterns
        wiring = block.get("wiring", [])
        for wire_spec in wiring:
            pattern = wire_spec.get("pattern", "")
            target = wire_spec.get("in", "")
            is_regex = wire_spec.get("regex", False)

            target_path = workspace / target

            if not target_path.exists():
                checks.append(
                    HarnessCheck(
                        pattern=pattern,
                        target_file=target,
                        passed=False,
                        is_regex=is_regex,
                        error=f"Target file missing: {target}",
                    )
                )
                continue

            # Check if pattern exists in file
            file_content = target_path.read_text()

            if is_regex:
                found = bool(re.search(pattern, file_content))
            else:
                found = pattern in file_content

            checks.append(
                HarnessCheck(
                    pattern=pattern,
                    target_file=target,
                    passed=found,
                    is_regex=is_regex,
                    error=None if found else f"Pattern not found in {target}",
                )
            )

    all_passed = all(c.passed for c in checks)
    return HarnessResult(document=document, checks=checks, passed=all_passed)


def validate_documents(documents: List[Path], workspace: Optional[Path] = None) -> List[HarnessResult]:
    """Validate multiple documents."""
    return [validate_harness(doc, workspace) for doc in documents]


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Validate @HARNESS tags in OPUS documents",
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
        output = []
        for result in results:
            output.append(
                {
                    "document": str(result.document),
                    "passed": result.passed,
                    "checks": [
                        {
                            "pattern": c.pattern,
                            "target": c.target_file,
                            "passed": c.passed,
                            "error": c.error,
                        }
                        for c in result.checks
                    ],
                }
            )
        print(json.dumps(output, indent=2))
    else:
        all_passed = True
        for result in results:
            if not result.passed:
                all_passed = False
                print(f"❌ {result.document}")
                for check in result.failed_checks:
                    print(f"   • {check.error}")
            elif result.checks:
                print(f"✅ {result.document} ({len(result.checks)} checks)")

        if not all_passed:
            sys.exit(1)


if __name__ == "__main__":
    main()
