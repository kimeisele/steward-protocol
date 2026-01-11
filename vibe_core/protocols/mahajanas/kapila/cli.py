"""
KAPILA CLI - GAD-000 Compliant
==============================

Position 6 in Mahamantra - Analysis/Inference/Samkhya

GAD-000 COMPLIANCE:
- Discoverability: get_capabilities() returns machine-readable specs
- Observability: get_state() returns structured state
- Parseability: CLIResult with error codes, not prose
- Composability: CLIOutput can be chained
- Idempotency: All operations are safe to retry
- Recoverability: check_health() for self-healing
- 37th (Identity): CLIContext with signature

NO print() statements. STRUCTURED output only.
"""

from __future__ import annotations

from typing import List

from vibe_core.mahamantra import (
    # Protocol
    CLIExecutable,
    CLIExecutableBase,
    # Types
    CLICapability,
    CLIContext,
    CLIErrorCode,
    CLIHealth,
    CLIOutput,
    CLIParameter,
    CLIResult,
    CLIState,
    # Mahamantra access
    mahamantra,
)


# =============================================================================
# KAPILA CLI - Implements CLIExecutable
# =============================================================================

class KapilaCLI(CLIExecutableBase):
    """
    Kapila CLI - GAD-000 Compliant.

    Domain: Analysis / Inference / Samkhya (Position 6)

    Commands:
    - analyze: Analyze a target
    - samkhya: 24 Prakriti elements
    - entropy: Protocol entropy analysis
    - gc: Garbage collection
    - inspect: State inspection
    - debug: Debug info
    """

    # =========================================================================
    # DISCOVERABILITY (GAD-000)
    # =========================================================================

    @classmethod
    def get_capabilities(cls) -> List[CLICapability]:
        """Return machine-readable capability descriptions."""
        return [
            CLICapability(
                name="analyze",
                purpose="Analyze a target for issues",
                parameters=[
                    CLIParameter(
                        name="target",
                        param_type="string",
                        required=False,
                        default="system",
                        description="Target to analyze",
                    ),
                ],
                returns_success="Analysis result with conclusion and confidence",
                returns_failure="Error code with context",
                examples=["analyze", "analyze myservice"],
                mahajana_position=6,
                keywords=["analyze", "inspect", "check"],
                idempotent=True,
            ),
            CLICapability(
                name="samkhya",
                purpose="List or analyze the 24 Prakriti elements",
                parameters=[
                    CLIParameter(
                        name="element",
                        param_type="string",
                        required=False,
                        description="Element name to analyze",
                    ),
                    CLIParameter(
                        name="--list",
                        param_type="boolean",
                        required=False,
                        default=True,
                        description="List all elements",
                    ),
                ],
                returns_success="Element list or analysis",
                returns_failure="Error code with context",
                examples=["samkhya", "samkhya --list", "samkhya MANAS"],
                mahajana_position=6,
                keywords=["samkhya", "prakriti", "elements"],
                idempotent=True,
            ),
            CLICapability(
                name="entropy",
                purpose="Analyze protocol entropy and drift",
                parameters=[],
                returns_success="Entropy report with violations",
                returns_failure="Error code with context",
                examples=["entropy"],
                mahajana_position=6,
                keywords=["entropy", "drift", "health"],
                idempotent=True,
            ),
            CLICapability(
                name="gc",
                purpose="Run garbage collection",
                parameters=[],
                returns_success="GC report with cleanup stats",
                returns_failure="Error code with context",
                examples=["gc"],
                mahajana_position=6,
                keywords=["gc", "garbage", "cleanup"],
                idempotent=True,
            ),
            CLICapability(
                name="inspect",
                purpose="Inspect Kapila state",
                parameters=[],
                returns_success="State inspection result",
                returns_failure="Error code with context",
                examples=["inspect"],
                mahajana_position=6,
                keywords=["inspect", "profile", "state"],
                idempotent=True,
            ),
        ]

    # =========================================================================
    # EXECUTION (GAD-000)
    # =========================================================================

    def _execute_impl(self, context: CLIContext) -> CLIResult:
        """
        Execute CLI command.

        Routes to appropriate handler based on command.
        NO print() - structured output only.
        """
        cmd = context.command.lower()

        # Route to handler
        if "samkhya" in cmd or "prakriti" in cmd:
            return self._handle_samkhya(context)
        elif "entropy" in cmd:
            return self._handle_entropy(context)
        elif "analyze" in cmd:
            return self._handle_analyze(context)
        elif "gc" in cmd:
            return self._handle_gc(context)
        elif "inspect" in cmd or "profile" in cmd:
            return self._handle_inspect(context)
        elif "debug" in cmd:
            return self._handle_debug(context)
        else:
            return self._handle_status(context)

    # =========================================================================
    # HANDLERS (Structured Output Only)
    # =========================================================================

    def _handle_analyze(self, context: CLIContext) -> CLIResult:
        """Handle analyze command."""
        from vibe_core.protocols.mahajanas.kapila import NullKapila

        target = context.args[0] if context.args else "system"
        kapila = NullKapila()

        analysis = kapila.analyze(target)

        output = CLIOutput()
        output.add("target", target)
        output.add("success", analysis.get("success", False))
        output.add("conclusion", analysis.get("conclusion", "No conclusion"))
        output.add("confidence", analysis.get("confidence", 0.0))

        return CLIResult.ok(output)

    def _handle_samkhya(self, context: CLIContext) -> CLIResult:
        """Handle samkhya command."""
        from vibe_core.protocols.mahajanas.kapila import (
            enumerate_all_elements,
            analyze_prakriti_element,
        )

        output = CLIOutput()

        if "--list" in context.args or not context.args:
            # List all elements
            elements = enumerate_all_elements()
            output.add("total_elements", len(elements))
            output.columns = ["number", "name", "category", "layer", "guardian"]

            for elem in elements:
                output.add_row(
                    str(elem.get("number", "")),
                    elem.get("name", ""),
                    elem.get("category", ""),
                    elem.get("layer", ""),
                    elem.get("guardian", ""),
                )

            return CLIResult.ok(output)

        # Analyze specific element
        element_name = context.args[0]
        try:
            result = analyze_prakriti_element(element_name)
            output.add("element", result.get("element", element_name))
            output.add("category", result.get("category", "unknown"))
            output.add("layer", result.get("layer", "unknown"))
            output.add("guardian", result.get("guardian", "unknown"))
            output.add("opcode", result.get("opcode", "unknown"))
            return CLIResult.ok(output)
        except Exception as e:
            return CLIResult.fail(
                CLIErrorCode.INVALID_ARGUMENT,
                f"Unknown element: {element_name}",
                element=element_name,
            )

    def _handle_entropy(self, context: CLIContext) -> CLIResult:
        """Handle entropy command."""
        from vibe_core.protocols.mahajanas.kapila import analyze_protocol_entropy

        try:
            report = analyze_protocol_entropy()

            output = CLIOutput()
            output.add("total_protocols", report.get("total_protocols", 0))
            output.add("entropy_score", report.get("entropy_score", 0.0))
            output.add("health", report.get("health", "unknown"))

            violations = report.get("violations", [])
            output.add("violation_count", len(violations))

            if violations:
                for i, v in enumerate(violations[:10]):
                    output.add(f"violation_{i}", str(v))

            return CLIResult.ok(output)
        except Exception as e:
            return CLIResult.fail(
                CLIErrorCode.INTERNAL_ERROR,
                f"Entropy analysis failed: {e}",
            )

    def _handle_gc(self, context: CLIContext) -> CLIResult:
        """Handle gc command."""
        # In real implementation, this would call actual GC
        output = CLIOutput()
        output.add("status", "complete")
        output.add("orphaned_protocols", 0)
        output.add("dangling_state", 0)
        output.add("stale_cache", 0)
        output.add("bytes_freed", 0)

        return CLIResult.ok(output)

    def _handle_inspect(self, context: CLIContext) -> CLIResult:
        """Handle inspect command."""
        from vibe_core.protocols.mahajanas.kapila import NullKapila

        kapila = NullKapila()
        state = kapila.get_state()

        output = CLIOutput()
        output.add("analyses_performed", state.get("analyses_performed", 0))
        output.add("optimizations_performed", state.get("optimizations_performed", 0))
        output.add("total_improvement", state.get("total_improvement", 0.0))
        output.add("health", state.get("health", "unknown"))

        return CLIResult.ok(output)

    def _handle_debug(self, context: CLIContext) -> CLIResult:
        """Handle debug command."""
        pos = mahamantra[6]

        output = CLIOutput()
        output.add("position", pos.index)
        output.add("guardian", str(pos.guardian))
        output.add("opcode", str(pos.opcode))
        output.add("quarter", pos.quarter)
        output.add("is_head", pos.is_head)

        return CLIResult.ok(output)

    def _handle_status(self, context: CLIContext) -> CLIResult:
        """Handle status command."""
        output = CLIOutput()
        output.add("position", 6)
        output.add("guardian", "kapila")
        output.add("domain", "Analysis / Inference / Samkhya")
        output.add("opcode", "GARBAGE_COLLECT")
        output.add("quarter", "DHARMA")

        # List capabilities
        caps = self.get_capabilities()
        output.add("capabilities", len(caps))
        for cap in caps:
            output.add(f"cmd_{cap.name}", cap.purpose)

        return CLIResult.ok(output)


# =============================================================================
# SINGLETON & CONVENIENCE
# =============================================================================

_cli_instance: KapilaCLI | None = None


def get_cli() -> KapilaCLI:
    """Get the Kapila CLI singleton."""
    global _cli_instance
    if _cli_instance is None:
        _cli_instance = KapilaCLI()
    return _cli_instance


def execute(command: str, args: List[str]) -> int:
    """
    Execute a Kapila CLI command.

    This is the entry point for cli_bridge.route().

    Args:
        command: Command name
        args: Command arguments

    Returns:
        Exit code (0 = success)
    """
    cli = get_cli()
    context = CLIContext(command=command, args=args)
    result = cli.execute(context)
    return result.exit_code


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "KapilaCLI",
    "get_cli",
    "execute",
]
