"""
TESTS.md Parser - Extracts test coverage gaps.

Parses TESTS.md format for modules lacking test coverage.
These become training scenarios for "write more tests" patterns.
"""

import re
from pathlib import Path
from typing import List

from vibe_core.ouroboros.ingestion import ViolationRecord, ViolationSource
from vibe_core.ouroboros.parsers.base import BaseViolationParser


class TestsMdParser(BaseViolationParser):
    """
    Parser for TESTS.md and test coverage reports.

    Extracts:
        - Modules with zero tests
        - Modules with low test ratios
        - Test coverage gaps
    """

    name = "tests_md"
    patterns = ["**/TESTS*.md", "**/*coverage*.md", "**/test_report*.md"]

    def can_parse(self, path: Path) -> bool:
        """Check if file is a test coverage report."""
        if not path.exists():
            return False
        if path.suffix.lower() != ".md":
            return False

        # Check for test-related keywords in filename
        name_upper = path.name.upper()
        return any(keyword in name_upper for keyword in ["TEST", "COVERAGE", "SPEC", "DIAMOND"])

    def parse(self, path: Path) -> List[ViolationRecord]:
        """Parse test coverage gaps from TESTS.md format."""
        violations = []

        if not path.exists():
            return violations

        content = path.read_text()

        # Pattern 1: Untested modules (0 tests)
        violations.extend(self._parse_untested_modules(content))

        # Pattern 2: Low coverage ratios
        violations.extend(self._parse_low_coverage(content))

        return violations

    def _parse_untested_modules(self, content: str) -> List[ViolationRecord]:
        """
        Parse modules with zero tests.

        Format:
            | doc_renderer.py | 743 | 0 | HOCH |
        """
        violations = []

        # Match: | module.py | lines | 0 | severity |
        untested_pattern = r"\|\s+([a-z_]+\.py)\s+\|\s+(\d+)\s+\|\s+0\s+\|\s+[^|]+\|"
        matches = re.findall(untested_pattern, content)

        for module_name, lines_str in matches:
            lines = int(lines_str)
            severity = "HIGH" if lines > 500 else "MEDIUM"

            violations.append(
                ViolationRecord(
                    source=ViolationSource.CI_TEST,
                    rule_id="TESTS:UNTESTED_MODULE",
                    file_path=f"vibe_core/{module_name}",
                    line=None,
                    message=f"{module_name} has {lines} lines with 0 tests",
                    severity=severity,
                    has_remedy=True,  # Can write tests
                    context={
                        "module": module_name,
                        "lines": lines,
                        "source": "TESTS.md",
                        "parser": self.name,
                    },
                )
            )

        return violations

    def _parse_low_coverage(self, content: str) -> List[ViolationRecord]:
        """
        Parse modules with low test coverage ratios.

        Format:
            | ModuleName | 500 | 3 | 0.6% |
        """
        violations = []

        # Match: | Module | lines | tests | ratio% |
        low_ratio_pattern = r"\|\s+([A-Za-z_]+)\s+\|\s+(\d+)\s+\|\s+(\d+)\s+\|\s+([\d.]+%)\s+\|"
        matches = re.findall(low_ratio_pattern, content)

        for module, lines_str, tests_str, ratio in matches:
            lines = int(lines_str)
            tests = int(tests_str)
            ratio_float = float(ratio.replace("%", ""))

            # Only report if has some tests but very low coverage
            if ratio_float < 1.0 and tests > 0:
                violations.append(
                    ViolationRecord(
                        source=ViolationSource.CI_TEST,
                        rule_id="TESTS:LOW_COVERAGE",
                        file_path=f"vibe_core/{module.lower()}/",
                        line=None,
                        message=f"{module}: {tests} tests for {lines} lines ({ratio} coverage)",
                        severity="MEDIUM",
                        has_remedy=True,  # Can write more tests
                        context={
                            "module": module,
                            "lines": lines,
                            "tests": tests,
                            "ratio": ratio_float,
                            "source": "TESTS.md",
                            "parser": self.name,
                        },
                    )
                )

        return violations
