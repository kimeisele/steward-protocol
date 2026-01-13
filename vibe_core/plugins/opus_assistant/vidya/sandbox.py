"""
VIDYA Sandbox - Ephemeral Test Runner.

OPUS-033: The Pramana Sandbox

"If the generated code contains os.system('rm -rf /') and we test it
in the kernel, the system is dead." - Senior Partner Warning

The Sandbox provides ISOLATED test execution:
- Tests run in a separate subprocess (NOT in kernel)
- Timeout protection (prevents infinite loops)
- Output capture (stdout/stderr)
- Exit code validation
- Cleanup after execution

This is the "Ordeal" phase of VIDYA - code must prove itself
in the sandbox before it can enter the kingdom.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prahlada"
__position__ = 9
__genesis__ = "0xae73178f"  # GenesisByte: parampara % 37 == 0

import asyncio
import logging
import os
import shutil
import tempfile
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger("VIDYA.Sandbox")


@dataclass
class SandboxResult:
    """Result from sandbox execution."""

    success: bool
    exit_code: int
    stdout: str = ""
    stderr: str = ""
    duration_ms: int = 0
    timed_out: bool = False
    error: Optional[str] = None
    test_results: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "exit_code": self.exit_code,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "duration_ms": self.duration_ms,
            "timed_out": self.timed_out,
            "error": self.error,
            "test_results": self.test_results,
        }


class Sandbox:
    """
    Ephemeral sandbox for safe code execution.

    The Sandbox creates a temporary directory, writes code to it,
    executes tests, and cleans up afterward.

    Security measures:
    - Runs in subprocess (isolated from kernel)
    - Timeout protection
    - No network access by default (TODO: implement)
    - Temporary directory (auto-cleanup)
    """

    DEFAULT_TIMEOUT_SECONDS = 30
    MAX_TIMEOUT_SECONDS = 120

    def __init__(
        self,
        timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
        workspace: Optional[Path] = None,
    ):
        """
        Initialize sandbox.

        Args:
            timeout_seconds: Maximum execution time
            workspace: Optional workspace root (for pytest config)
        """
        self._timeout = min(timeout_seconds, self.MAX_TIMEOUT_SECONDS)
        self._workspace = workspace or Path.cwd()
        self._sandbox_dir: Optional[Path] = None

    async def run_test(
        self,
        code: Dict[str, str],
        test_code: str,
        test_filename: str = "test_generated.py",
    ) -> SandboxResult:
        """
        Run a test against generated code in the sandbox.

        This is the main interface for the Pramana phase.

        Args:
            code: Dict of filename -> content (the generated capability)
            test_code: The test code to run
            test_filename: Name for the test file

        Returns:
            SandboxResult with pass/fail status
        """
        start_time = datetime.utcnow()

        try:
            # Create sandbox directory
            self._sandbox_dir = Path(tempfile.mkdtemp(prefix="vidya_sandbox_"))
            logger.debug(f"🏖️ Sandbox created: {self._sandbox_dir}")

            # Write generated code
            for filename, content in code.items():
                file_path = self._sandbox_dir / filename
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(content)

            # Write test file
            test_path = self._sandbox_dir / test_filename
            test_path.write_text(test_code)

            # Write __init__.py for imports
            init_path = self._sandbox_dir / "__init__.py"
            if not init_path.exists():
                init_path.write_text("")

            # Run pytest
            result = await self._run_pytest(test_path)

            # Calculate duration
            duration = datetime.utcnow() - start_time
            result.duration_ms = int(duration.total_seconds() * 1000)

            return result

        except Exception as e:
            logger.error(f"Sandbox execution failed: {e}")
            return SandboxResult(
                success=False,
                exit_code=-1,
                error=str(e),
            )
        finally:
            # Cleanup
            self._cleanup()

    async def _run_pytest(self, test_path: Path) -> SandboxResult:
        """
        Run pytest on the test file.

        Uses subprocess for isolation.
        """
        cmd = [
            "python",
            "-m",
            "pytest",
            str(test_path),
            "-v",
            "--tb=short",
            "-x",  # Stop on first failure
            "--no-header",
        ]

        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(self._sandbox_dir),
                env=self._get_sandbox_env(),
            )

            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=self._timeout,
                )
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                return SandboxResult(
                    success=False,
                    exit_code=-1,
                    timed_out=True,
                    error=f"Test timed out after {self._timeout}s",
                )

            stdout_str = stdout.decode() if stdout else ""
            stderr_str = stderr.decode() if stderr else ""

            # Parse test results
            test_results = self._parse_pytest_output(stdout_str)

            success = process.returncode == 0

            return SandboxResult(
                success=success,
                exit_code=process.returncode,
                stdout=stdout_str,
                stderr=stderr_str,
                test_results=test_results,
            )

        except FileNotFoundError:
            return SandboxResult(
                success=False,
                exit_code=-1,
                error="pytest not found - install with: pip install pytest",
            )
        except Exception as e:
            return SandboxResult(
                success=False,
                exit_code=-1,
                error=str(e),
            )

    def _get_sandbox_env(self) -> Dict[str, str]:
        """
        Get environment variables for sandbox execution.

        Inherits from parent but can restrict certain vars.
        """
        env = os.environ.copy()

        # Add sandbox directory to PYTHONPATH
        pythonpath = env.get("PYTHONPATH", "")
        if pythonpath:
            env["PYTHONPATH"] = f"{self._sandbox_dir}:{pythonpath}"
        else:
            env["PYTHONPATH"] = str(self._sandbox_dir)

        # Remove potentially dangerous vars
        dangerous_vars = [
            "AWS_ACCESS_KEY_ID",
            "AWS_SECRET_ACCESS_KEY",
            "DATABASE_URL",
            "REDIS_URL",
        ]
        for var in dangerous_vars:
            env.pop(var, None)

        return env

    def _parse_pytest_output(self, output: str) -> Dict[str, Any]:
        """Parse pytest output for structured results."""
        results = {
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "errors": [],
        }

        # Count pass/fail
        for line in output.split("\n"):
            if " passed" in line:
                try:
                    # Pattern: "1 passed"
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if part == "passed" and i > 0:
                            results["passed"] = int(parts[i - 1])
                        elif part == "failed" and i > 0:
                            results["failed"] = int(parts[i - 1])
                        elif part == "skipped" and i > 0:
                            results["skipped"] = int(parts[i - 1])
                except (ValueError, IndexError):
                    pass

            # Collect error lines
            if "FAILED" in line or "ERROR" in line:
                results["errors"].append(line.strip())

        return results

    async def run_syntax_check(self, code: str) -> SandboxResult:
        """
        Quick syntax check by compiling code.

        This doesn't require a full sandbox - just compiles in subprocess.
        """
        try:
            # Create temp file
            with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
                f.write(code)
                temp_path = f.name

            try:
                cmd = ["python", "-m", "py_compile", temp_path]
                process = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )

                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=10,
                )

                return SandboxResult(
                    success=process.returncode == 0,
                    exit_code=process.returncode,
                    stdout=stdout.decode() if stdout else "",
                    stderr=stderr.decode() if stderr else "",
                )
            finally:
                os.unlink(temp_path)

        except Exception as e:
            return SandboxResult(
                success=False,
                exit_code=-1,
                error=str(e),
            )

    async def run_script(
        self,
        script: str,
        timeout_seconds: Optional[int] = None,
    ) -> SandboxResult:
        """
        Run a Python script in the sandbox.

        Use this for simple script execution (not pytest).

        Args:
            script: Python code to execute
            timeout_seconds: Override timeout

        Returns:
            SandboxResult with output
        """
        timeout = timeout_seconds or self._timeout
        start_time = datetime.utcnow()

        try:
            # Create sandbox directory
            self._sandbox_dir = Path(tempfile.mkdtemp(prefix="vidya_sandbox_"))

            # Write script
            script_path = self._sandbox_dir / "script.py"
            script_path.write_text(script)

            # Run script
            cmd = ["python", str(script_path)]
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(self._sandbox_dir),
                env=self._get_sandbox_env(),
            )

            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout,
                )
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                return SandboxResult(
                    success=False,
                    exit_code=-1,
                    timed_out=True,
                    error=f"Script timed out after {timeout}s",
                )

            duration = datetime.utcnow() - start_time

            return SandboxResult(
                success=process.returncode == 0,
                exit_code=process.returncode,
                stdout=stdout.decode() if stdout else "",
                stderr=stderr.decode() if stderr else "",
                duration_ms=int(duration.total_seconds() * 1000),
            )

        except Exception as e:
            return SandboxResult(
                success=False,
                exit_code=-1,
                error=str(e),
            )
        finally:
            self._cleanup()

    def _cleanup(self) -> None:
        """Clean up sandbox directory."""
        if self._sandbox_dir and self._sandbox_dir.exists():
            try:
                shutil.rmtree(self._sandbox_dir)
                logger.debug(f"🧹 Sandbox cleaned up: {self._sandbox_dir}")
            except Exception as e:
                logger.warning(f"Could not cleanup sandbox: {e}")
            finally:
                self._sandbox_dir = None


# Convenience function
async def run_in_sandbox(
    code: Dict[str, str],
    test_code: str,
    timeout_seconds: int = 30,
) -> SandboxResult:
    """
    Convenience function to run code + test in sandbox.

    Args:
        code: Dict of filename -> content
        test_code: Test code to run
        timeout_seconds: Timeout

    Returns:
        SandboxResult
    """
    sandbox = Sandbox(timeout_seconds=timeout_seconds)
    return await sandbox.run_test(code, test_code)
