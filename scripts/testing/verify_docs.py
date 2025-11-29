#!/usr/bin/env python3
"""
Living Documentation Verification System.

This script implements the "TRUTH" pillar of the Recursive Bootstrap:
- Parses all *.md documentation files
- Extracts Python code blocks
- Executes them in a controlled sandbox
- Fails if any code execution fails
- Result: Documentation IS the Test Suite

Philosophy: "If the docs say the code works, the CI must prove it."

Usage:
    python scripts/verify_docs.py                    # Verify all docs
    python scripts/verify_docs.py --dir docs/        # Verify specific directory
    python scripts/verify_docs.py --file docs/api.md # Verify single file
    python scripts/verify_docs.py --verbose           # Show detailed output
"""

import os
import sys
import re
import logging
from pathlib import Path
from typing import List, Tuple, Dict, Any, Optional
from dataclasses import dataclass
import traceback

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
)
logger = logging.getLogger("VERIFY_DOCS")


@dataclass
class CodeBlock:
    """A Python code block extracted from documentation."""

    file_path: Path
    line_number: int
    code: str
    language: str  # e.g., "python", "python3"

    def __repr__(self) -> str:
        return f"{self.file_path}:{self.line_number} ({len(self.code)} chars)"


@dataclass
class ExecutionResult:
    """Result of executing a code block."""

    code_block: CodeBlock
    success: bool
    error: Optional[str] = None
    output: Optional[str] = None


class DocsParser:
    """Parse markdown files and extract Python code blocks."""

    # Regex to match code blocks (supports ```python, ```py, ```python3)
    CODE_BLOCK_PATTERN = re.compile(
        r"^```(python|py|python3)\n(.*?)\n```",
        re.MULTILINE | re.DOTALL,
    )

    @staticmethod
    def extract_code_blocks(file_path: Path) -> List[CodeBlock]:
        """
        Extract all Python code blocks from a markdown file.

        Args:
            file_path: Path to markdown file

        Returns:
            List of CodeBlock objects
        """
        if not file_path.exists():
            logger.error(f"❌ File not found: {file_path}")
            return []

        try:
            content = file_path.read_text()
            blocks = []

            # Find all code blocks and track line numbers
            line_number = 1
            for match in DocsParser.CODE_BLOCK_PATTERN.finditer(content):
                # Count newlines before this match to get line number
                line_number += content[: match.start()].count("\n")

                blocks.append(
                    CodeBlock(
                        file_path=file_path,
                        line_number=line_number,
                        code=match.group(2),
                        language=match.group(1),
                    )
                )

            return blocks

        except Exception as e:
            logger.error(f"❌ Failed to parse {file_path}: {e}")
            return []


class CodeExecutor:
    """Execute code blocks in a sandboxed environment."""

    @staticmethod
    def execute(code_block: CodeBlock) -> ExecutionResult:
        """
        Execute a code block.

        Args:
            code_block: CodeBlock to execute

        Returns:
            ExecutionResult with success status
        """
        try:
            # Create a restricted namespace for execution
            # Include common imports but restrict dangerous operations
            namespace = {
                "__builtins__": {
                    # Safe builtins
                    "print": print,
                    "len": len,
                    "range": range,
                    "dict": dict,
                    "list": list,
                    "str": str,
                    "int": int,
                    "float": float,
                    "bool": bool,
                    "set": set,
                    "tuple": tuple,
                    "isinstance": isinstance,
                    "type": type,
                    "abs": abs,
                    "all": all,
                    "any": any,
                    "max": max,
                    "min": min,
                    "sorted": sorted,
                    "sum": sum,
                    "zip": zip,
                    # Restricted builtins (can be used but should be careful)
                    "open": open,
                    "exec": exec,
                    "eval": eval,
                },
                "__name__": "__doc_test__",
                "__file__": str(code_block.file_path),
            }

            # Add common imports
            import json
            import sys as sys_module

            namespace["json"] = json
            namespace["sys"] = sys_module

            # Execute the code
            exec(code_block.code, namespace)

            return ExecutionResult(
                code_block=code_block,
                success=True,
            )

        except Exception as e:
            error_msg = f"{type(e).__name__}: {str(e)}"
            tb = traceback.format_exc()

            return ExecutionResult(
                code_block=code_block,
                success=False,
                error=error_msg,
                output=tb,
            )


class DocsVerifier:
    """Main verifier that orchestrates documentation testing."""

    def __init__(self, verbose: bool = False):
        """
        Initialize the verifier.

        Args:
            verbose: Enable verbose output
        """
        self.verbose = verbose
        self.results: List[ExecutionResult] = []

    def verify_file(self, file_path: Path) -> int:
        """
        Verify all code blocks in a markdown file.

        Args:
            file_path: Path to markdown file

        Returns:
            Number of failures
        """
        logger.info(f"📄 Verifying: {file_path}")

        blocks = DocsParser.extract_code_blocks(file_path)
        if not blocks:
            logger.info(f"   ℹ️  No Python code blocks found")
            return 0

        logger.info(f"   Found {len(blocks)} code block(s)")

        failures = 0
        for idx, block in enumerate(blocks, 1):
            result = CodeExecutor.execute(block)
            self.results.append(result)

            if result.success:
                logger.info(f"   ✅ Block {idx} (line {block.line_number}): OK")
            else:
                logger.error(f"   ❌ Block {idx} (line {block.line_number}): FAILED")
                logger.error(f"      Error: {result.error}")
                if self.verbose and result.output:
                    logger.error(f"      Traceback:\n{result.output}")
                failures += 1

        return failures

    def verify_directory(self, directory: Path) -> int:
        """
        Verify all markdown files in a directory.

        Args:
            directory: Path to directory

        Returns:
            Total number of failures
        """
        if not directory.exists():
            logger.error(f"❌ Directory not found: {directory}")
            return 1

        logger.info(f"📁 Verifying directory: {directory}")

        markdown_files = list(directory.glob("**/*.md"))
        if not markdown_files:
            logger.warning(f"⚠️  No markdown files found in {directory}")
            return 0

        logger.info(f"   Found {len(markdown_files)} markdown file(s)\n")

        total_failures = 0
        for md_file in sorted(markdown_files):
            failures = self.verify_file(md_file)
            total_failures += failures
            logger.info("")

        return total_failures

    def get_summary(self) -> Dict[str, Any]:
        """
        Get verification summary statistics.

        Returns:
            Dict with summary statistics
        """
        total = len(self.results)
        passed = sum(1 for r in self.results if r.success)
        failed = total - passed

        return {
            "total_blocks": total,
            "passed": passed,
            "failed": failed,
            "success_rate": (passed / total * 100) if total > 0 else 0,
        }

    def print_summary(self):
        """Print verification summary."""
        summary = self.get_summary()

        logger.info("=" * 70)
        logger.info("📋 LIVING DOCUMENTATION VERIFICATION SUMMARY")
        logger.info("=" * 70)
        logger.info(f"Total code blocks:  {summary['total_blocks']}")
        logger.info(f"Passed:             {summary['passed']} ✅")
        logger.info(f"Failed:             {summary['failed']} ❌")
        logger.info(f"Success rate:       {summary['success_rate']:.1f}%")
        logger.info("=" * 70)

        if summary["failed"] > 0:
            logger.error("\n🔴 VERIFICATION FAILED")
            logger.error("Documentation contains code that does not execute correctly.")
            return False
        else:
            logger.info("\n🟢 VERIFICATION PASSED")
            logger.info("All documentation code executes successfully.")
            logger.info("Documentation IS the Test Suite. ✨")
            return True


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Living Documentation Verification System",
    )
    parser.add_argument(
        "--dir",
        type=Path,
        default=Path("docs"),
        help="Directory to verify (default: docs/)",
    )
    parser.add_argument(
        "--file",
        type=Path,
        help="Single file to verify (overrides --dir)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show detailed output including tracebacks",
    )

    args = parser.parse_args()

    logger.info("🏛️  STEWARD Living Documentation Verification System")
    logger.info("=" * 70)
    logger.info('Philosophy: "If the docs say it works, CI proves it."')
    logger.info("=" * 70 + "\n")

    verifier = DocsVerifier(verbose=args.verbose)

    # Verify file or directory
    if args.file:
        failures = verifier.verify_file(args.file)
    else:
        failures = verifier.verify_directory(args.dir)

    # Print summary
    verifier.print_summary()

    # Exit with appropriate code
    sys.exit(0 if failures == 0 else 1)


if __name__ == "__main__":
    main()
