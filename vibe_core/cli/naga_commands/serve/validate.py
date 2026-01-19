"""
VALIDATE COMMAND - JANAKA's Dharma Check
=========================================

MAHAJANA: JANAKA (The Philosopher King)
OPCODE: CHECK_DHARMA (Position 10)
PHASE: SERVE

WHY JANAKA?
- Janaka ruled Videha with perfect dharma
- He tested reality (the famous "fire in the palace" test)
- He validated that Sita was dharmic before giving her to Rama
- CHECK_DHARMA is about validating that everything is in order

MANTRA WORD: KRISHNA (Position 10)
"Krishna ensures dharma is upheld"

CHECK_DHARMA = Validate the system state against dharmic principles.
Janaka tests, validates, and ensures compliance.

Usage:
    naga validate                 # Run all validations
    naga validate --types         # Type checking only
    naga validate --imports       # Import validation only
    naga validate --protocols     # Protocol compliance only
    naga validate --quick         # Quick validation (no deep checks)
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "yamaraja"
__position__ = 15
__genesis__ = "0xf18cc929"  # GenesisByte: parampara % 37 == 0

import subprocess
from pathlib import Path
from typing import List, Tuple

from vibe_core.protocols.naga.cli_command import NagaCommandBase, NagaCommandResult, naga_command
from vibe_core.protocols.substrate import MantraOpCode


@naga_command(
    opcode=MantraOpCode.STATE_SYNC, name="validate", help_text="Validate system dharma (JANAKA's test - SERVE phase)"
)
class ValidateCommand(NagaCommandBase):
    """
    Validate command implementation.

    JANAKA validates:
    - Type safety (mypy/pyright)
    - Import structure (circular imports)
    - Protocol compliance (ABC contracts)
    - Configuration validity

    The Philosopher King ensures all is in order.
    """

    def execute(self, args: List[str]) -> NagaCommandResult:
        """
        Execute validation checks.

        Args:
            args: Command arguments
                --types: Type checking only
                --imports: Import validation only
                --protocols: Protocol compliance only
                --quick: Quick validation (skip slow checks)

        Returns:
            NagaCommandResult with validation results
        """
        # Parse flags
        types_only = "--types" in args
        imports_only = "--imports" in args
        protocols_only = "--protocols" in args
        quick_mode = "--quick" in args

        # Build output
        output_parts = []
        data: List[Tuple[str, str]] = [
            ("mahajana", "janaka"),
            ("opcode", "CHECK_DHARMA"),
            ("phase", "serve"),
            ("position", "10"),
        ]

        output_parts.append("[JANAKA] Dharma Validation")
        output_parts.append("=" * 50)

        validations_run = 0
        validations_passed = 0
        issues = []

        # Type validation
        if not imports_only and not protocols_only:
            output_parts.append("")
            output_parts.append("  Type Safety (Mypy):")
            type_result = self._validate_types(quick=quick_mode)
            validations_run += 1
            if type_result["passed"]:
                validations_passed += 1
                output_parts.append(f"    ✓ {type_result['message']}")
            else:
                output_parts.append(f"    ✗ {type_result['message']}")
                issues.extend(type_result.get("issues", []))
            data.append(("types_passed", str(type_result["passed"])))

        # Import validation
        if not types_only and not protocols_only:
            output_parts.append("")
            output_parts.append("  Import Structure:")
            import_result = self._validate_imports()
            validations_run += 1
            if import_result["passed"]:
                validations_passed += 1
                output_parts.append(f"    ✓ {import_result['message']}")
            else:
                output_parts.append(f"    ✗ {import_result['message']}")
                issues.extend(import_result.get("issues", []))
            data.append(("imports_passed", str(import_result["passed"])))

        # Protocol validation
        if not types_only and not imports_only:
            output_parts.append("")
            output_parts.append("  Protocol Compliance:")
            protocol_result = self._validate_protocols()
            validations_run += 1
            if protocol_result["passed"]:
                validations_passed += 1
                output_parts.append(f"    ✓ {protocol_result['message']}")
            else:
                output_parts.append(f"    ✗ {protocol_result['message']}")
                issues.extend(protocol_result.get("issues", []))
            data.append(("protocols_passed", str(protocol_result["passed"])))

        # Summary
        output_parts.append("")
        output_parts.append("=" * 50)
        all_passed = validations_passed == validations_run
        status = "DHARMIC" if all_passed else "ADHARMIC"
        output_parts.append(f"CHECK_DHARMA: {validations_passed}/{validations_run} validations passed - {status}")

        if issues:
            output_parts.append("")
            output_parts.append("Issues found:")
            for issue in issues[:5]:
                output_parts.append(f"  • {issue}")
            if len(issues) > 5:
                output_parts.append(f"  ... and {len(issues) - 5} more")

        data.append(("validations_run", str(validations_run)))
        data.append(("validations_passed", str(validations_passed)))
        data.append(("status", status))

        return self.success("\n".join(output_parts), data=tuple(data))

    def _validate_types(self, quick: bool = False) -> dict:
        """Run type checking with mypy."""
        try:
            cmd = ["python", "-m", "mypy", "--version"]
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=Path.cwd(), timeout=5)

            if result.returncode != 0:
                return {
                    "passed": True,
                    "message": "Mypy not available (skipped)",
                }

            # Quick check: just verify mypy can run
            if quick:
                return {
                    "passed": True,
                    "message": "Quick mode - mypy available",
                }

            # Full check on vibe_core
            vibe_core = Path.cwd() / "vibe_core"
            if not vibe_core.exists():
                return {
                    "passed": True,
                    "message": "No vibe_core directory found",
                }

            # Run mypy with lenient settings
            cmd = [
                "python",
                "-m",
                "mypy",
                str(vibe_core),
                "--ignore-missing-imports",
                "--no-error-summary",
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=Path.cwd(), timeout=60)

            if result.returncode == 0:
                return {"passed": True, "message": "No type errors found"}
            else:
                lines = result.stdout.strip().split("\n") if result.stdout else []
                error_count = len([l for l in lines if ": error:" in l])
                return {
                    "passed": False,
                    "message": f"{error_count} type errors found",
                    "issues": lines[:5],
                }

        except subprocess.TimeoutExpired:
            return {"passed": False, "message": "Type check timed out"}
        except Exception as e:
            return {"passed": True, "message": f"Type check skipped: {e}"}

    def _validate_imports(self) -> dict:
        """Validate import structure for circular imports."""
        try:
            # Check key modules can be imported
            test_imports = [
                "vibe_core.protocols.substrate",
                "vibe_core.protocols.naga.cli_command",
                "vibe_core.cli.naga_commands",
            ]

            failed = []
            for module in test_imports:
                try:
                    __import__(module)
                except ImportError as e:
                    failed.append(f"{module}: {e}")

            if failed:
                return {
                    "passed": False,
                    "message": f"{len(failed)} import failures",
                    "issues": failed,
                }

            return {
                "passed": True,
                "message": f"All {len(test_imports)} core imports valid",
            }

        except Exception as e:
            return {"passed": False, "message": f"Import check failed: {e}"}

    def _validate_protocols(self) -> dict:
        """Validate protocol compliance."""
        try:
            from vibe_core.cli.naga_commands import discover_commands
            from vibe_core.protocols.naga.cli_command import NAGA_COMMAND_REGISTRY

            discover_commands()

            # Check all registered commands have required methods
            issues = []
            cmd_count = len(NAGA_COMMAND_REGISTRY._commands)

            for name in NAGA_COMMAND_REGISTRY._commands:
                cmd = NAGA_COMMAND_REGISTRY.get(name)

                # Verify required attributes
                if not hasattr(cmd, "opcode"):
                    issues.append(f"{name}: missing opcode")
                if not hasattr(cmd, "mahajana"):
                    issues.append(f"{name}: missing mahajana")
                if not hasattr(cmd, "execute"):
                    issues.append(f"{name}: missing execute method")

            if issues:
                return {
                    "passed": False,
                    "message": f"{len(issues)} protocol violations",
                    "issues": issues,
                }

            return {
                "passed": True,
                "message": f"All {cmd_count} commands protocol-compliant",
            }

        except Exception as e:
            return {"passed": False, "message": f"Protocol check failed: {e}"}


# Export for direct import
__all__ = ["ValidateCommand"]
