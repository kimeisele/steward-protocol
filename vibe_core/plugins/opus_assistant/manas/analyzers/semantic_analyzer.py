"""
Semantic Analyzer - The Genesis Impulse.

OPUS-032: Find GAPS, not ERRORS. This is the 51% analyzer.

The 50%/51% distinction:
- 50% (ContractAnalyzer): Fixes what's BROKEN (immune system)
- 51% (SemanticAnalyzer): Creates what's MISSING (genesis impulse)

This is the moment the system stops being a servant and starts being a partner.
It looks at code and asks: "What's missing that would add value?"

Examples:
- Tool without test → "I should create test_tool.py"
- Module without docstring → "I should document this"
- Similar files without abstraction → "I could refactor this"
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prahlada"
__position__ = 9
__genesis__ = "0xfedd33f9"  # GenesisByte: parampara % 37 == 0

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..intent_generator import Intent, IntentPriority, IntentRisk
from .base import AnalyzerConfig, BaseAnalyzer

logger = logging.getLogger("MANAS.SemanticAnalyzer")


class SemanticAnalyzer(BaseAnalyzer):
    """
    OPUS-032: The Genesis Impulse - 51% Analyzer.

    This analyzer doesn't look for errors. It looks for OPPORTUNITY.
    It scans the codebase for gaps that, if filled, would add value.

    Philosophy:
        "Moksha ist nicht nur Freiheit von Fehlern (Bug-Fixing),
         sondern Freiheit zu Schöpfen (Feature-Creation)."
    """

    def __init__(
        self,
        workspace: Optional[Path] = None,
        config: Optional[AnalyzerConfig] = None,
    ):
        """Initialize SemanticAnalyzer."""
        super().__init__(workspace=workspace, config=config)
        self._intent_counter = 0

    @property
    def name(self) -> str:
        """Analyzer name for logging and cooldowns."""
        return "semantic_analyzer"

    def _next_id(self) -> str:
        """Generate next intent ID."""
        self._intent_counter += 1
        return f"genesis_{self._intent_counter:04d}"

    def analyze(self, context: Dict[str, Any]) -> List[Intent]:
        """
        Analyze codebase for GAPS - opportunities for creation.

        This is NOT about fixing errors. This is about adding VALUE.

        Args:
            context: System context

        Returns:
            List of genesis intents
        """
        intents: List[Intent] = []

        # Gap 1: Code without tests
        test_gaps = self._find_test_gaps()
        intents.extend(test_gaps)

        # Gap 2: Modules without docstrings (future)
        # Gap 3: Similar code without abstraction (future)
        # Gap 4: APIs without examples (future)

        if intents:
            logger.info(f"SemanticAnalyzer: Found {len(intents)} creation opportunities")
        else:
            logger.debug("SemanticAnalyzer: No gaps found - codebase complete")

        # Respect max intents per run
        return intents[: self._config.max_intents_per_run]

    def _find_test_gaps(self) -> List[Intent]:
        """
        Find code files without corresponding test files.

        This is the core 51% analysis:
        - Scan plugins/ for .py files
        - Check if test_*.py exists
        - If not → genesis intent

        Returns:
            List of intents to create missing tests
        """
        intents: List[Intent] = []
        plugins_dir = self._workspace / "vibe_core" / "plugins"

        if not plugins_dir.exists():
            return []

        for plugin_dir in plugins_dir.iterdir():
            if not plugin_dir.is_dir():
                continue
            if plugin_dir.name.startswith("_"):
                continue

            # Look for tools/ directory (common pattern)
            tools_dir = plugin_dir / "tools"
            tests_dir = plugin_dir / "tests"

            if tools_dir.exists():
                intent = self._check_tools_coverage(plugin_dir.name, tools_dir, tests_dir)
                if intent:
                    intents.append(intent)

            # Also check core/ directory
            core_dir = plugin_dir / "core"
            if core_dir.exists():
                intent = self._check_core_coverage(plugin_dir.name, core_dir, tests_dir)
                if intent:
                    intents.append(intent)

            # Check manas/ for opus_assistant specifically
            if plugin_dir.name == "opus_assistant":
                manas_dir = plugin_dir / "manas"
                if manas_dir.exists():
                    intent = self._check_manas_coverage(manas_dir, tests_dir)
                    if intent:
                        intents.append(intent)

        return intents

    def _check_tools_coverage(self, plugin_name: str, tools_dir: Path, tests_dir: Path) -> Optional[Intent]:
        """Check if tools have test coverage."""
        untested_tools = []

        for tool_file in tools_dir.glob("*.py"):
            if tool_file.name.startswith("_"):
                continue
            if tool_file.name == "__init__.py":
                continue

            # Expected test file
            expected_test = f"test_{tool_file.name}"

            # Check multiple test locations
            test_exists = False
            if tests_dir.exists():
                if (tests_dir / expected_test).exists():
                    test_exists = True
                # Also check tests/unit/
                if (tests_dir / "unit" / expected_test).exists():
                    test_exists = True

            if not test_exists:
                untested_tools.append(tool_file.name)

        if not untested_tools:
            return None

        # Generate ONE intent for all missing tests in this plugin
        return Intent(
            id=self._next_id(),
            intent_type="semantic_gap_test",
            title=f"Create tests for {plugin_name} tools",
            description=f"Found {len(untested_tools)} tools without test coverage: {', '.join(untested_tools[:3])}{'...' if len(untested_tools) > 3 else ''}",
            reasoning="TDD Dharma: Tests protect the system. Creating tests adds value without changing functionality.",
            priority=IntentPriority.LOW,
            risk=IntentRisk.SAFE,  # Creating tests is always safe
            params={
                "plugin": plugin_name,
                "untested_files": untested_tools,
                "type": "tools",
            },
            auto_executable=True,  # Safe to auto-create tests with high karma
        )

    def _check_core_coverage(self, plugin_name: str, core_dir: Path, tests_dir: Path) -> Optional[Intent]:
        """Check if core modules have test coverage."""
        untested_core = []

        for core_file in core_dir.glob("*.py"):
            if core_file.name.startswith("_"):
                continue
            if core_file.name == "__init__.py":
                continue

            expected_test = f"test_{core_file.name}"

            test_exists = False
            if tests_dir.exists():
                if (tests_dir / expected_test).exists():
                    test_exists = True
                if (tests_dir / "unit" / expected_test).exists():
                    test_exists = True

            if not test_exists:
                untested_core.append(core_file.name)

        if not untested_core:
            return None

        return Intent(
            id=self._next_id(),
            intent_type="semantic_gap_test",
            title=f"Create tests for {plugin_name} core",
            description=f"Found {len(untested_core)} core modules without tests: {', '.join(untested_core[:3])}{'...' if len(untested_core) > 3 else ''}",
            reasoning="Core modules are critical. Test coverage ensures stability.",
            priority=IntentPriority.LOW,
            risk=IntentRisk.SAFE,
            params={
                "plugin": plugin_name,
                "untested_files": untested_core,
                "type": "core",
            },
            auto_executable=True,
        )

    def _check_manas_coverage(self, manas_dir: Path, tests_dir: Path) -> Optional[Intent]:
        """Check if MANAS modules have test coverage."""
        untested = []

        # Check main MANAS modules
        key_modules = ["cognitive_kernel.py", "intent_generator.py", "memory_store.py"]

        for module_name in key_modules:
            module_file = manas_dir / module_name
            if not module_file.exists():
                continue

            expected_test = f"test_{module_name}"

            test_exists = False
            if tests_dir.exists():
                if (tests_dir / expected_test).exists():
                    test_exists = True
                if (tests_dir / "unit" / expected_test).exists():
                    test_exists = True
                # Also check tests/manas/
                manas_tests = tests_dir / "manas"
                if manas_tests.exists() and (manas_tests / expected_test).exists():
                    test_exists = True

            if not test_exists:
                untested.append(module_name)

        # Also check analyzers/
        analyzers_dir = manas_dir / "analyzers"
        if analyzers_dir.exists():
            for analyzer_file in analyzers_dir.glob("*.py"):
                if analyzer_file.name.startswith("_"):
                    continue
                if analyzer_file.name == "__init__.py":
                    continue
                if analyzer_file.name == "base.py":
                    continue  # Base class doesn't need tests

                expected_test = f"test_{analyzer_file.name}"
                test_exists = False
                if tests_dir.exists():
                    for test_loc in [
                        tests_dir / expected_test,
                        tests_dir / "manas" / expected_test,
                        tests_dir / "analyzers" / expected_test,
                    ]:
                        if test_loc.exists():
                            test_exists = True
                            break

                if not test_exists:
                    untested.append(f"analyzers/{analyzer_file.name}")

        if not untested:
            return None

        return Intent(
            id=self._next_id(),
            intent_type="semantic_gap_test",
            title="Create tests for MANAS cognitive kernel",
            description=f"The brain of OPUS needs tests: {', '.join(untested)}",
            reasoning="MANAS is the cognitive core. Tests ensure the mind stays sharp.",
            priority=IntentPriority.MEDIUM,  # Slightly higher - brain is important
            risk=IntentRisk.SAFE,
            params={
                "plugin": "opus_assistant",
                "untested_files": untested,
                "type": "manas",
            },
            auto_executable=True,
        )
