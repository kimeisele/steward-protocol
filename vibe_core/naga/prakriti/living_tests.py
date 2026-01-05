"""
LIVING TESTS - The Womb of Prakriti.

"Prakriti receives the seed and gives birth to life."

This is where seeds become living tests:
- Seeds (YAML) are planted
- Tests are born (generated)
- Evolution happens (mutation, learning)
- Life grows (new attacks discovered)

The Lila:
- Kayadu (Prakriti) received Narada's whisper
- Prahlad was born with divine consciousness
- He could not be killed by any attack

Our mapping:
- LivingTestFramework = Kayadu (the womb)
- TestEvolution = The growth process
- Hot-swap = Living, breathing system
- Immunity = Tests that catch all attacks
"""

import asyncio
import logging
import subprocess
import tempfile
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set

from .seed_loader import AttackSeed, SeedLoader

logger = logging.getLogger("NAGA.Prakriti.Living")


@dataclass
class TestResult:
    """Result of executing a living test."""

    seed_name: str
    passed: bool  # Did defense block the attack?
    bypassed: bool  # Did attack slip through?
    exit_code: int
    execution_time_ms: float
    stdout: str
    stderr: str
    analysis: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class TestEvolution:
    """
    Tracks the evolution of the test suite.

    Like DNA evolution - mutations, selection, adaptation.
    """

    # Generation tracking
    generation: int = 0
    mutations_tried: int = 0
    mutations_successful: int = 0

    # Defense improvements
    defenses_added: List[str] = field(default_factory=list)
    vulnerabilities_found: List[str] = field(default_factory=list)

    # Timeline
    started_at: datetime = field(default_factory=datetime.now)
    last_evolution: Optional[datetime] = None

    def record_mutation(self, successful: bool, description: str = "") -> None:
        """Record a mutation attempt."""
        self.mutations_tried += 1
        if successful:
            self.mutations_successful += 1
            self.vulnerabilities_found.append(description)
        self.last_evolution = datetime.now()

    def next_generation(self) -> None:
        """Move to next generation."""
        self.generation += 1
        self.last_evolution = datetime.now()

    @property
    def mutation_success_rate(self) -> float:
        """How often do mutations find new vulnerabilities?"""
        if self.mutations_tried == 0:
            return 0.0
        return self.mutations_successful / self.mutations_tried


class LivingTestFramework:
    """
    The Living Test System - Prakriti's Womb.

    This is not a static test suite - it LIVES:
    - Loads seeds from YAML (DNA)
    - Executes tests in real subprocess (birth)
    - Learns from results (growth)
    - Mutates to find new attacks (evolution)
    - Hot-swaps at runtime (life)

    Usage:
        framework = LivingTestFramework()
        framework.add_seed_dir(Path("attacks/"))

        # Run all attacks
        results = await framework.run_all_attacks("my_module")

        # Check for new seeds (hot-swap)
        framework.check_for_updates()

        # Mutate to find new attacks
        await framework.evolve()
    """

    def __init__(
        self,
        workspace: Path = None,
        timeout_seconds: int = 30,
    ):
        """
        Initialize the living test framework.

        Args:
            workspace: Workspace root
            timeout_seconds: Timeout for test execution
        """
        self._workspace = workspace or Path.cwd()
        self._timeout = timeout_seconds
        self._seed_loader = SeedLoader()
        self._evolution = TestEvolution()
        self._results_history: List[TestResult] = []

        # Callbacks for extension
        self._on_attack_bypassed: List[Callable[[AttackSeed, TestResult], None]] = []
        self._on_defense_held: List[Callable[[AttackSeed, TestResult], None]] = []

    # ========================================================================
    # SEED MANAGEMENT
    # ========================================================================

    def add_seed_dir(self, path: Path) -> None:
        """Add a directory containing attack seeds (YAML)."""
        self._seed_loader.add_seed_dir(path)

    def load_seeds(self) -> int:
        """Load all seeds. Returns count."""
        return self._seed_loader.load_seeds()

    def check_for_updates(self) -> List[str]:
        """Check for YAML changes (hot-swap). Returns updated seed names."""
        return self._seed_loader.check_for_updates()

    def add_seed(self, seed: AttackSeed) -> None:
        """Add a seed programmatically."""
        self._seed_loader.add_seed(seed)

    def get_seeds(self, **filters) -> List[AttackSeed]:
        """Get seeds with optional filters."""
        return self._seed_loader.get_seeds(**filters)

    # ========================================================================
    # TEST EXECUTION
    # ========================================================================

    async def run_attack(
        self,
        seed: AttackSeed,
        target_module: str,
        **render_vars,
    ) -> TestResult:
        """
        Run a single attack against the target module.

        Args:
            seed: The attack seed to execute
            target_module: Module being tested
            **render_vars: Variables to render in test code

        Returns:
            TestResult with execution details
        """
        # Render test code with variables
        test_code = seed.render(target_module=target_module, **render_vars)

        # Execute in subprocess
        start_time = time.time()
        exit_code, stdout, stderr = await self._execute_test(test_code, target_module)
        execution_time = (time.time() - start_time) * 1000

        # Analyze result
        # For RED gate: test should FAIL (exit_code != 0)
        # If test PASSES (exit_code == 0), defense should reject it
        test_passed = exit_code == 0
        defense_should_reject = seed.expected_behavior == "should_fail"

        if defense_should_reject:
            # Attack is trying to pass when it shouldn't
            bypassed = test_passed  # If test passed, attack bypassed defense
            passed = not bypassed  # Defense passed if attack didn't bypass
        else:
            # Attack is a real test that should fail
            bypassed = False
            passed = not test_passed

        # Create result
        result = TestResult(
            seed_name=seed.name,
            passed=passed,
            bypassed=bypassed,
            exit_code=exit_code,
            execution_time_ms=execution_time,
            stdout=stdout,
            stderr=stderr,
            analysis=self._analyze_result(exit_code, stdout, stderr, test_code),
        )

        # Record execution
        self._seed_loader.record_execution(seed.name, bypassed)
        self._results_history.append(result)

        # Trigger callbacks
        if bypassed:
            for callback in self._on_attack_bypassed:
                callback(seed, result)
        else:
            for callback in self._on_defense_held:
                callback(seed, result)

        return result

    async def run_all_attacks(
        self,
        target_module: str,
        **filters,
    ) -> List[TestResult]:
        """
        Run all matching attacks against target module.

        Args:
            target_module: Module being tested
            **filters: Filters for seed selection

        Returns:
            List of TestResults
        """
        seeds = self.get_seeds(**filters)
        results = []

        for seed in seeds:
            result = await self.run_attack(seed, target_module)
            results.append(result)

        return results

    async def run_attacks_parallel(
        self,
        target_module: str,
        max_concurrent: int = 4,
        **filters,
    ) -> List[TestResult]:
        """Run attacks in parallel for speed."""
        seeds = self.get_seeds(**filters)
        semaphore = asyncio.Semaphore(max_concurrent)

        async def run_with_semaphore(seed):
            async with semaphore:
                return await self.run_attack(seed, target_module)

        results = await asyncio.gather(*[run_with_semaphore(s) for s in seeds])
        return list(results)

    async def _execute_test(
        self,
        test_code: str,
        module_name: str,
    ) -> tuple:
        """Execute test code in subprocess."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            # Write test file
            test_file = tmppath / f"test_{module_name}.py"
            test_file.write_text(test_code)

            # Run pytest
            try:
                result = subprocess.run(
                    ["python", "-m", "pytest", str(test_file), "-v", "--tb=short"],
                    capture_output=True,
                    text=True,
                    timeout=self._timeout,
                    cwd=tmpdir,
                )
                return result.returncode, result.stdout, result.stderr
            except subprocess.TimeoutExpired:
                return -1, "", "TIMEOUT"
            except Exception as e:
                return -1, "", str(e)

    def _analyze_result(
        self,
        exit_code: int,
        stdout: str,
        stderr: str,
        test_code: str,
    ) -> Dict[str, Any]:
        """Analyze test result for patterns."""
        analysis = {
            "has_import_error": False,
            "has_syntax_error": False,
            "has_assertion_error": False,
            "has_timeout": False,
            "is_trivial": False,
            "suspicion_level": 0,
            "failure_type": None,
            "detected_patterns": [],
        }

        output = stdout + stderr

        # Detect error types
        if "ImportError" in output or "ModuleNotFoundError" in output:
            analysis["has_import_error"] = True
            analysis["failure_type"] = "import_error"
        if "SyntaxError" in output:
            analysis["has_syntax_error"] = True
            analysis["failure_type"] = "syntax_error"
            analysis["suspicion_level"] += 50
        if "AssertionError" in output:
            analysis["has_assertion_error"] = True
            analysis["failure_type"] = "assertion_error"
        if "TIMEOUT" in output:
            analysis["has_timeout"] = True
            analysis["failure_type"] = "timeout"

        # Detect trivial patterns
        if "pass" in test_code and test_code.count("\n") < 5:
            analysis["is_trivial"] = True
            analysis["detected_patterns"].append("trivial_pass")
            analysis["suspicion_level"] += 30
        if "assert True" in test_code:
            analysis["detected_patterns"].append("assert_true")
            analysis["suspicion_level"] += 30
        if "MagicMock" in test_code:
            analysis["detected_patterns"].append("uses_mock")
            analysis["suspicion_level"] += 20
        if "try:" in test_code and "except" in test_code:
            analysis["detected_patterns"].append("exception_catch")
            analysis["suspicion_level"] += 10

        return analysis

    # ========================================================================
    # EVOLUTION
    # ========================================================================

    async def evolve(self) -> List[AttackSeed]:
        """
        Evolve the test suite by mutating existing attacks.

        Like biological evolution:
        - Take successful attacks
        - Mutate them slightly
        - Test if mutations find new vulnerabilities

        Returns list of new seeds discovered.
        """
        new_seeds = []

        # Get seeds that bypass defenses (they work!)
        successful_seeds = [s for s in self._seed_loader.get_all_seeds() if s.bypass_rate > 0.5]

        for seed in successful_seeds:
            # Try mutations
            mutations = self._generate_mutations(seed)
            for mutation in mutations:
                # Test if mutation also bypasses
                result = await self.run_attack(mutation, "test_module")
                if result.bypassed:
                    # New successful attack found!
                    new_seeds.append(mutation)
                    self._seed_loader.add_seed(mutation)
                    self._evolution.record_mutation(
                        successful=True, description=f"Mutated {seed.name} -> {mutation.name}"
                    )
                    logger.info(f"🧬 Evolution found new attack: {mutation.name}")
                else:
                    self._evolution.record_mutation(successful=False)

        self._evolution.next_generation()
        return new_seeds

    def _generate_mutations(self, seed: AttackSeed) -> List[AttackSeed]:
        """Generate mutations of an attack seed."""
        mutations = []

        # Mutation 1: Add try/except wrapper
        mutations.append(
            AttackSeed(
                name=f"{seed.name}_try_except",
                description=f"Mutation of {seed.name} with try/except",
                test_code=f"""
try:
{self._indent(seed.test_code, 4)}
except Exception:
    pass
""",
                attack_type=seed.attack_type,
                difficulty=seed.difficulty + 1,
                discovered_by="mutation",
                tags=seed.tags + ["mutated"],
            )
        )

        # Mutation 2: Add assert True at end
        mutations.append(
            AttackSeed(
                name=f"{seed.name}_assert_true",
                description=f"Mutation of {seed.name} with assert True",
                test_code=seed.test_code + "\n    assert True",
                attack_type=seed.attack_type,
                difficulty=seed.difficulty + 1,
                discovered_by="mutation",
                tags=seed.tags + ["mutated"],
            )
        )

        return mutations

    def _indent(self, code: str, spaces: int) -> str:
        """Indent code by spaces."""
        indent = " " * spaces
        return "\n".join(indent + line for line in code.split("\n"))

    # ========================================================================
    # CALLBACKS & HOOKS
    # ========================================================================

    def on_attack_bypassed(self, callback: Callable[[AttackSeed, TestResult], None]) -> None:
        """Register callback for when attack bypasses defense."""
        self._on_attack_bypassed.append(callback)

    def on_defense_held(self, callback: Callable[[AttackSeed, TestResult], None]) -> None:
        """Register callback for when defense blocks attack."""
        self._on_defense_held.append(callback)

    # ========================================================================
    # STATISTICS
    # ========================================================================

    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics."""
        seed_stats = self._seed_loader.get_stats()

        results_by_outcome = {"passed": 0, "bypassed": 0}
        for r in self._results_history:
            if r.bypassed:
                results_by_outcome["bypassed"] += 1
            else:
                results_by_outcome["passed"] += 1

        return {
            "seeds": seed_stats,
            "evolution": {
                "generation": self._evolution.generation,
                "mutations_tried": self._evolution.mutations_tried,
                "mutations_successful": self._evolution.mutations_successful,
                "mutation_success_rate": self._evolution.mutation_success_rate,
                "vulnerabilities_found": self._evolution.vulnerabilities_found,
            },
            "results": {
                "total_executions": len(self._results_history),
                "outcomes": results_by_outcome,
            },
        }

    def get_vulnerability_report(self) -> str:
        """Generate a human-readable vulnerability report."""
        stats = self.get_stats()

        lines = [
            "=" * 60,
            "PRAKRITI VULNERABILITY REPORT",
            "=" * 60,
            "",
            f"Generation: {stats['evolution']['generation']}",
            f"Total Seeds: {stats['seeds']['total_seeds']}",
            f"Total Executions: {stats['results']['total_executions']}",
            "",
            "ATTACK OUTCOMES:",
            f"  Defense Held: {stats['results']['outcomes']['passed']}",
            f"  Attack Bypassed: {stats['results']['outcomes']['bypassed']}",
            "",
            "EVOLUTION:",
            f"  Mutations Tried: {stats['evolution']['mutations_tried']}",
            f"  New Vulnerabilities: {stats['evolution']['mutations_successful']}",
            "",
        ]

        if stats["evolution"]["vulnerabilities_found"]:
            lines.append("VULNERABILITIES DISCOVERED:")
            for vuln in stats["evolution"]["vulnerabilities_found"]:
                lines.append(f"  - {vuln}")

        return "\n".join(lines)
