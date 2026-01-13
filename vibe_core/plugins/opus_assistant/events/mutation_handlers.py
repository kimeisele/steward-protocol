"""
MUTATION PROTOCOL HANDLERS - Operation Sanctuary
=================================================
OPUS-038: Mutation Testing for Legacy Code

"A test that cannot detect errors is not a test. It is a lie."

This module implements mutation testing to validate tests for legacy code:
1. GREEN Gate: Test passes with original code
2. MUTATE: Inject controlled bugs (AST-based)
3. RED Gate: Test must FAIL against mutants

The Three Deadly Pitfalls (mitigated):
1. Infinite Loop Death → Strict timeout (5s per mutant)
2. Import Cache Death → Fresh temp directory + PYTHONPATH isolation
3. Noise Death → Only Tier 1 (Comparison) + Tier 3 (Return) mutations

Philosophy:
    Diamond Protocol: RED → GREEN (for new code)
    Mutation Protocol: GREEN → MUTATE → RED (for legacy code)
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prahlada"
__position__ = 9
__genesis__ = "0x8f9250a0"  # GenesisByte: parampara % 37 == 0

import ast
import asyncio
import logging
import shutil
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("MUTATION.Handlers")


# =============================================================================
# MUTATION ENGINE - AST-Based Code Sabotage
# =============================================================================


@dataclass
class Mutation:
    """Represents a single mutation applied to code."""

    operator: str  # e.g., "GT_TO_LT", "RET_TO_NONE"
    original: str  # Original code snippet
    mutated: str  # Mutated code snippet
    line_number: int
    description: str


@dataclass
class MutationResult:
    """Result of running a test against a mutant."""

    mutation: Mutation
    killed: bool  # True if test FAILED (good!)
    survived: bool  # True if test PASSED (bad - weak test!)
    timeout: bool  # True if test timed out (treated as killed)
    exit_code: int
    stdout: str = ""
    stderr: str = ""


@dataclass
class MutationReport:
    """Final report from mutation testing."""

    total_mutants: int
    killed: int
    survived: int
    timeout: int
    kill_rate: float  # killed / total
    results: List[MutationResult] = field(default_factory=list)
    success: bool = False  # True if kill_rate >= threshold

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for circuit consumption."""
        return {
            "success": self.success,
            "total_mutants": self.total_mutants,
            "killed": self.killed,
            "survived": self.survived,
            "timeout": self.timeout,
            "kill_rate": self.kill_rate,
            "surviving_mutations": [
                {"operator": r.mutation.operator, "line": r.mutation.line_number, "description": r.mutation.description}
                for r in self.results
                if r.survived
            ],
        }


class ComparisonMutator(ast.NodeTransformer):
    """
    Tier 1: Comparison Mutations (High Signal)

    Mutates comparison operators:
    - > → <
    - >= → <=
    - < → >
    - <= → >=
    - == → !=
    - != → ==
    """

    # Mapping of original operator to mutated operator
    MUTATIONS = {
        ast.Gt: (ast.Lt, "GT_TO_LT", "> to <"),
        ast.Lt: (ast.Gt, "LT_TO_GT", "< to >"),
        ast.GtE: (ast.LtE, "GTE_TO_LTE", ">= to <="),
        ast.LtE: (ast.GtE, "LTE_TO_GTE", "<= to >="),
        ast.Eq: (ast.NotEq, "EQ_TO_NE", "== to !="),
        ast.NotEq: (ast.Eq, "NE_TO_EQ", "!= to =="),
    }

    def __init__(self, target_index: int = 0):
        """
        Initialize mutator.

        Args:
            target_index: Which comparison to mutate (0 = first found)
        """
        self.target_index = target_index
        self.current_index = 0
        self.applied_mutation: Optional[Mutation] = None

    def visit_Compare(self, node: ast.Compare) -> ast.Compare:
        """Visit comparison nodes and mutate the target one."""
        for i, op in enumerate(node.ops):
            op_type = type(op)
            if op_type in self.MUTATIONS:
                if self.current_index == self.target_index:
                    # Apply mutation
                    new_op_class, op_name, description = self.MUTATIONS[op_type]
                    original_op = ast.unparse(node) if hasattr(ast, "unparse") else str(op_type.__name__)

                    node.ops[i] = new_op_class()

                    mutated_op = ast.unparse(node) if hasattr(ast, "unparse") else str(new_op_class.__name__)

                    self.applied_mutation = Mutation(
                        operator=op_name,
                        original=original_op,
                        mutated=mutated_op,
                        line_number=node.lineno,
                        description=f"Changed {description} at line {node.lineno}",
                    )
                self.current_index += 1
        return node


class ReturnMutator(ast.NodeTransformer):
    """
    Tier 3: Return Mutations (High Signal)

    Mutates return statements:
    - return x → return None
    - return True → return False
    - return False → return True
    """

    def __init__(self, target_index: int = 0):
        """
        Initialize mutator.

        Args:
            target_index: Which return to mutate (0 = first found)
        """
        self.target_index = target_index
        self.current_index = 0
        self.applied_mutation: Optional[Mutation] = None

    def visit_Return(self, node: ast.Return) -> ast.Return:
        """Visit return nodes and mutate the target one."""
        if node.value is None:
            return node

        if self.current_index == self.target_index:
            original = ast.unparse(node) if hasattr(ast, "unparse") else "return ..."

            # Determine mutation type based on return value
            if isinstance(node.value, ast.Constant):
                if node.value.value is True:
                    node.value = ast.Constant(value=False)
                    op_name = "RET_TRUE_TO_FALSE"
                    description = "return True → return False"
                elif node.value.value is False:
                    node.value = ast.Constant(value=True)
                    op_name = "RET_FALSE_TO_TRUE"
                    description = "return False → return True"
                else:
                    node.value = ast.Constant(value=None)
                    op_name = "RET_TO_NONE"
                    description = "return x → return None"
            else:
                # For complex expressions, just return None
                node.value = ast.Constant(value=None)
                op_name = "RET_TO_NONE"
                description = "return x → return None"

            mutated = ast.unparse(node) if hasattr(ast, "unparse") else "return None"

            self.applied_mutation = Mutation(
                operator=op_name,
                original=original,
                mutated=mutated,
                line_number=node.lineno,
                description=f"{description} at line {node.lineno}",
            )

        self.current_index += 1
        return node


class MutationEngine:
    """
    AST-based Mutation Engine.

    Generates mutated versions of Python source code.
    Focuses on Tier 1 (Comparisons) and Tier 3 (Returns) for high signal.
    """

    def __init__(self, max_mutants: int = 10):
        """
        Initialize mutation engine.

        Args:
            max_mutants: Maximum number of mutants to generate
        """
        self.max_mutants = max_mutants

    def count_mutation_targets(self, source_code: str) -> Dict[str, int]:
        """Count how many mutation targets exist in the code."""
        try:
            tree = ast.parse(source_code)
        except SyntaxError:
            return {"comparisons": 0, "returns": 0}

        comparisons = 0
        returns = 0

        for node in ast.walk(tree):
            if isinstance(node, ast.Compare):
                for op in node.ops:
                    if type(op) in ComparisonMutator.MUTATIONS:
                        comparisons += 1
            elif isinstance(node, ast.Return) and node.value is not None:
                returns += 1

        return {"comparisons": comparisons, "returns": returns}

    def generate_mutants(self, source_code: str) -> List[Tuple[str, Mutation]]:
        """
        Generate mutated versions of the source code.

        Args:
            source_code: Original Python source code

        Returns:
            List of (mutated_code, mutation_info) tuples
        """
        mutants: List[Tuple[str, Mutation]] = []

        try:
            ast.parse(source_code)
        except SyntaxError as e:
            logger.error(f"Cannot parse source code: {e}")
            return mutants

        # Count targets
        targets = self.count_mutation_targets(source_code)
        total_targets = targets["comparisons"] + targets["returns"]

        if total_targets == 0:
            logger.warning("No mutation targets found in source code")
            return mutants

        # Generate comparison mutations
        for i in range(targets["comparisons"]):
            if len(mutants) >= self.max_mutants:
                break
            try:
                tree_copy = ast.parse(source_code)
                mutator = ComparisonMutator(target_index=i)
                mutator.visit(tree_copy)
                ast.fix_missing_locations(tree_copy)

                if mutator.applied_mutation:
                    mutated_code = ast.unparse(tree_copy)
                    mutants.append((mutated_code, mutator.applied_mutation))
            except Exception as e:
                logger.debug(f"Failed to generate comparison mutant {i}: {e}")

        # Generate return mutations
        for i in range(targets["returns"]):
            if len(mutants) >= self.max_mutants:
                break
            try:
                tree_copy = ast.parse(source_code)
                mutator = ReturnMutator(target_index=i)
                mutator.visit(tree_copy)
                ast.fix_missing_locations(tree_copy)

                if mutator.applied_mutation:
                    mutated_code = ast.unparse(tree_copy)
                    mutants.append((mutated_code, mutator.applied_mutation))
            except Exception as e:
                logger.debug(f"Failed to generate return mutant {i}: {e}")

        logger.info(f"🧬 Generated {len(mutants)} mutants from {total_targets} targets")
        return mutants


# =============================================================================
# MUTATION HANDLERS - Sandbox Execution
# =============================================================================


class MutationHandlers:
    """
    Handlers for the Mutation Protocol.

    Executes mutation testing with proper isolation:
    - Fresh temp directory for each mutant
    - PYTHONPATH isolation
    - Strict timeout enforcement
    """

    # Strict timeout to prevent infinite loops (The Halting Problem)
    MUTANT_TIMEOUT_SECONDS = 5
    GREEN_GATE_TIMEOUT_SECONDS = 30

    # Kill rate threshold
    MIN_KILL_RATE = 0.8  # 80%

    def __init__(self, workspace: Optional[Path] = None):
        """
        Initialize mutation handlers.

        Args:
            workspace: Workspace root directory
        """
        self._workspace = workspace or Path.cwd()
        self._engine = MutationEngine(max_mutants=10)

    async def green_gate_original(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        GREEN Gate: Test must PASS against original code.

        This proves the test works with the current implementation.

        Target: opus.mutation_green_gate

        Params:
            source_code: str - The original source code
            test_code: str - The test code
            module_name: str - Name of the module being tested

        Returns:
            success: bool - True if test passed
        """
        source_code = params.get("source_code", "")
        test_code = params.get("test_code", "")
        module_name = params.get("module_name", "legacy_module")

        logger.info(f"🟢 GREEN GATE: Testing {module_name} with original code")

        result = await self._run_test_in_sandbox(
            source_code=source_code,
            test_code=test_code,
            module_name=module_name,
            timeout=self.GREEN_GATE_TIMEOUT_SECONDS,
        )

        test_passed = result["exit_code"] == 0

        if test_passed:
            logger.info("🟢✅ GREEN GATE PASSED: Test works with original code")
        else:
            logger.warning("🟢❌ GREEN GATE FAILED: Test broken with original code")

        return {
            "success": test_passed,
            "test_passed": test_passed,
            "stdout": result["stdout"],
            "stderr": result["stderr"],
            "error": None if test_passed else "Test failed against original code",
        }

    async def run_mutation_protocol(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run the full Mutation Protocol.

        Target: opus.mutation_protocol

        Params:
            source_code: str - The original source code
            test_code: str - The test code
            module_name: str - Name of the module being tested
            min_kill_rate: float - Minimum kill rate (default 0.8)

        Returns:
            MutationReport as dict
        """
        source_code = params.get("source_code", "")
        test_code = params.get("test_code", "")
        module_name = params.get("module_name", "legacy_module")
        min_kill_rate = params.get("min_kill_rate", self.MIN_KILL_RATE)

        logger.info(f"🧬 MUTATION PROTOCOL: Starting for {module_name}")

        # Phase 1: GREEN Gate (original code)
        green_result = await self.green_gate_original(
            {"source_code": source_code, "test_code": test_code, "module_name": module_name}
        )

        if not green_result["success"]:
            return MutationReport(
                total_mutants=0,
                killed=0,
                survived=0,
                timeout=0,
                kill_rate=0.0,
                success=False,
            ).to_dict()

        # Phase 2: Generate mutants
        mutants = self._engine.generate_mutants(source_code)

        if not mutants:
            logger.warning("No mutants generated - code may be too simple")
            return MutationReport(
                total_mutants=0,
                killed=0,
                survived=0,
                timeout=0,
                kill_rate=1.0,  # No mutants = perfect score (vacuously true)
                success=True,
            ).to_dict()

        # Phase 3: RED Gate (run test against each mutant)
        results: List[MutationResult] = []
        killed = 0
        survived = 0
        timeout_count = 0

        for mutated_code, mutation in mutants:
            logger.debug(f"🧬 Testing mutant: {mutation.operator} at line {mutation.line_number}")

            result = await self._run_test_in_sandbox(
                source_code=mutated_code,
                test_code=test_code,
                module_name=module_name,
                timeout=self.MUTANT_TIMEOUT_SECONDS,
            )

            is_timeout = result.get("timeout", False)
            test_failed = result["exit_code"] != 0

            # Mutant is KILLED if test FAILS (or timeout)
            is_killed = test_failed or is_timeout

            mutation_result = MutationResult(
                mutation=mutation,
                killed=is_killed and not is_timeout,
                survived=not is_killed,
                timeout=is_timeout,
                exit_code=result["exit_code"],
                stdout=result["stdout"],
                stderr=result["stderr"],
            )
            results.append(mutation_result)

            if is_timeout:
                timeout_count += 1
                logger.debug(f"  ⏰ TIMEOUT (killed): {mutation.operator}")
            elif is_killed:
                killed += 1
                logger.debug(f"  💀 KILLED: {mutation.operator}")
            else:
                survived += 1
                logger.warning(f"  🧟 SURVIVED: {mutation.operator} - {mutation.description}")

        # Phase 4: Calculate kill rate
        total = len(mutants)
        # Timeout counts as killed (the mutation caused something bad)
        effective_killed = killed + timeout_count
        kill_rate = effective_killed / total if total > 0 else 0.0

        success = kill_rate >= min_kill_rate

        report = MutationReport(
            total_mutants=total,
            killed=killed,
            survived=survived,
            timeout=timeout_count,
            kill_rate=kill_rate,
            results=results,
            success=success,
        )

        if success:
            logger.info(f"🧬✅ MUTATION PROTOCOL PASSED: Kill rate {kill_rate:.1%} >= {min_kill_rate:.1%}")
        else:
            logger.warning(
                f"🧬❌ MUTATION PROTOCOL FAILED: Kill rate {kill_rate:.1%} < {min_kill_rate:.1%}"
                f" ({survived} mutants survived)"
            )

        return report.to_dict()

    async def _run_test_in_sandbox(
        self,
        source_code: str,
        test_code: str,
        module_name: str,
        timeout: int,
    ) -> Dict[str, Any]:
        """
        Run test in isolated sandbox.

        Creates a fresh temp directory to avoid import cache issues.

        Args:
            source_code: The source code to test
            test_code: The test code
            module_name: Name for the module file
            timeout: Timeout in seconds

        Returns:
            Dict with exit_code, stdout, stderr, timeout
        """
        sandbox_dir = None
        try:
            # Create isolated sandbox directory
            sandbox_dir = Path(tempfile.mkdtemp(prefix="mutation_sandbox_"))

            # Write source code
            source_file = sandbox_dir / f"{module_name}.py"
            source_file.write_text(source_code)

            # Write test file
            test_file = sandbox_dir / f"test_{module_name}.py"
            test_file.write_text(test_code)

            # Write __init__.py for imports
            init_file = sandbox_dir / "__init__.py"
            init_file.write_text("")

            # Run pytest with isolated PYTHONPATH
            import os

            env = os.environ.copy()
            env["PYTHONPATH"] = str(sandbox_dir)

            cmd = [
                "python",
                "-m",
                "pytest",
                str(test_file),
                "-x",  # Stop on first failure
                "-v",
                "--tb=short",
                "--no-header",
            ]

            try:
                process = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=str(sandbox_dir),
                    env=env,
                )

                try:
                    stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout)
                    return {
                        "exit_code": process.returncode,
                        "stdout": stdout.decode() if stdout else "",
                        "stderr": stderr.decode() if stderr else "",
                        "timeout": False,
                    }
                except asyncio.TimeoutError:
                    process.kill()
                    await process.wait()
                    return {
                        "exit_code": -1,
                        "stdout": "",
                        "stderr": f"Test timed out after {timeout}s",
                        "timeout": True,
                    }

            except FileNotFoundError:
                return {
                    "exit_code": -1,
                    "stdout": "",
                    "stderr": "pytest not found",
                    "timeout": False,
                }

        except Exception as e:
            logger.error(f"Sandbox execution failed: {e}")
            return {
                "exit_code": -1,
                "stdout": "",
                "stderr": str(e),
                "timeout": False,
            }
        finally:
            # Always cleanup sandbox
            if sandbox_dir and sandbox_dir.exists():
                try:
                    shutil.rmtree(sandbox_dir)
                except Exception as e:
                    logger.warning(f"Could not cleanup sandbox: {e}")


# =============================================================================
# SINGLETON ACCESS
# =============================================================================

_mutation_handlers: Optional[MutationHandlers] = None


def get_mutation_handlers(workspace: Optional[Path] = None) -> MutationHandlers:
    """Get or create the singleton MutationHandlers instance."""
    global _mutation_handlers
    if _mutation_handlers is None:
        _mutation_handlers = MutationHandlers(workspace=workspace)
    return _mutation_handlers
