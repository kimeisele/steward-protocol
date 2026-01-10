"""
DETECT COMMAND - KUMARAS' Purity Check
======================================

MAHAJANA: KUMARAS (The Four Pure Sages)
OPCODE: RESOLVE_REQ (Position 6)
PHASE: PURIFY

WHY KUMARAS?
- The four Kumaras are eternally pure (celibate sages)
- They detect impurity and deviation from dharma
- Detection is about RESOLVING what the intent is
- They distinguish between pure and impure requests

MANTRA WORD: HARE (Position 6)
"Hare reveals what is hidden"

RESOLVE_REQ = Understanding what is being requested.
Before you can act, you must DETECT the true intent.
KUMARAS detect drift, impurity, and deviation.

Usage:
    naga detect                   # Full drift detection
    naga detect --git             # Git-based drift only
    naga detect --patterns        # Pattern analysis only
    naga detect --intent <msg>    # Detect intent from message
"""

import subprocess
from pathlib import Path
from typing import List, Tuple, Optional

from vibe_core.protocols.naga.cli_command import (
    Mahajana,
    NagaCommandBase,
    NagaCommandResult,
    naga_command,
)
from vibe_core.protocols.substrate import MantraOpCode


@naga_command(
    opcode=MantraOpCode.RESOLVE_REQ,
    mahajana=Mahajana.KUMARAS,
    name="detect",
    help_text="Detect drifts and resolve intent (KUMARAS' purity - PURIFY phase)",
)
class DetectCommand(NagaCommandBase):
    """
    Detect command implementation.

    KUMARAS detect:
    - Drift from expected state (git changes)
    - Pattern deviations (panic, deferral loops)
    - Intent from natural language
    - Impure code patterns

    The Kumaras are the gatekeepers of purity.
    Nothing impure passes their detection.
    """

    def execute(self, args: List[str]) -> NagaCommandResult:
        """
        Execute detect command.

        Args:
            args: Command arguments
                --git: Git-based drift detection only
                --patterns: Pattern analysis only
                --intent <msg>: Detect intent from message

        Returns:
            NagaCommandResult with detection findings
        """
        # Parse flags
        git_only = "--git" in args
        patterns_only = "--patterns" in args
        intent_mode = "--intent" in args

        # Intent detection mode
        if intent_mode:
            intent_idx = args.index("--intent")
            if intent_idx + 1 < len(args):
                message = " ".join(args[intent_idx + 1:])
                return self._detect_intent(message)
            else:
                return self.failure(
                    "Missing message after --intent. Usage: naga detect --intent <message>",
                    exit_code=1,
                )

        # Build output
        output_parts = []
        data: List[Tuple[str, str]] = [
            ("mahajana", "kumaras"),
            ("opcode", "RESOLVE_REQ"),
            ("phase", "purify"),
            ("position", "6"),
        ]

        output_parts.append("[KUMARAS] Drift Detection")
        output_parts.append("=" * 50)

        # Git drift detection
        if not patterns_only:
            git_result = self._detect_git_drift()
            output_parts.append(git_result["output"])
            data.append(("uncommitted_count", str(git_result["count"])))

        # Pattern analysis
        if not git_only:
            pattern_result = self._detect_patterns()
            output_parts.append("")
            output_parts.append(pattern_result["output"])
            data.append(("patterns_detected", str(pattern_result["count"])))

        output_parts.append("")
        output_parts.append("=" * 50)
        output_parts.append("RESOLVE_REQ: Detection complete")

        return self.success(
            "\n".join(output_parts),
            data=tuple(data),
        )

    def _detect_git_drift(self) -> dict:
        """Detect drift via git status."""
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                cwd=Path.cwd(),
                timeout=10,
            )

            if result.stdout.strip():
                lines = result.stdout.strip().split("\n")
                output_lines = [f"  Git Drift: {len(lines)} uncommitted changes"]
                for line in lines[:8]:
                    output_lines.append(f"    {line}")
                if len(lines) > 8:
                    output_lines.append(f"    ... and {len(lines) - 8} more")
                return {"output": "\n".join(output_lines), "count": len(lines)}
            else:
                return {"output": "  Git Drift: Clean (no uncommitted changes)", "count": 0}

        except subprocess.TimeoutExpired:
            return {"output": "  Git Drift: Timeout", "count": -1}
        except Exception as e:
            return {"output": f"  Git Drift: Error - {e}", "count": -1}

    def _detect_patterns(self) -> dict:
        """Detect concerning patterns."""
        patterns_found = []

        # Check for common anti-patterns in recent activity
        # This would integrate with CommitWatcher in full implementation
        output_lines = ["  Pattern Analysis:"]

        # Simulated pattern detection
        # In real implementation, this queries the Federation's CommitWatcher
        try:
            from vibe_core.di import ServiceRegistry
            from vibe_core.protocols.naga import NagaFederationProtocol

            federation = ServiceRegistry.get(NagaFederationProtocol)
            if federation and federation.commit_watcher:
                stats = federation.commit_watcher.get_stats()

                if stats.get("panic_count", 0) >= 3:
                    patterns_found.append("PANIC_PATTERN")
                    output_lines.append("    ⚠️  PANIC PATTERN: Data loss risk detected")

                if stats.get("consecutive_deferrals", 0) >= 5:
                    patterns_found.append("DEFERRAL_LOOP")
                    output_lines.append("    ⚠️  DEFERRAL LOOP: Decision paralysis detected")

                total = stats.get("total_observed", 0)
                healed = stats.get("healed_count", 0)
                if total > 10 and healed / total > 0.5:
                    patterns_found.append("CONFLICT_DRIFT")
                    output_lines.append(f"    ⚠️  CONFLICT DRIFT: {healed/total:.1%} require healing")

        except Exception:
            pass  # Federation not available, skip

        if not patterns_found:
            output_lines.append("    ✓ No concerning patterns detected")

        return {"output": "\n".join(output_lines), "count": len(patterns_found)}

    def _detect_intent(self, message: str) -> NagaCommandResult:
        """
        Detect intent from natural language message.

        KUMARAS assist PRAHLADA in understanding intent.
        This is RESOLVE_REQ in action.
        """
        msg_lower = message.lower()

        # Intent patterns (shared with ChatCommand)
        intent_patterns = {
            "status": ["status", "health", "how is", "are you", "alive", "running"],
            "scan": ["scan", "check", "verify", "audit", "security", "vulnerab"],
            "intel": ["intel", "threat", "warning", "alert", "critical"],
            "detect": ["detect", "drift", "change", "diff", "pattern"],
            "help": ["help", "usage", "how to", "what can"],
        }

        detected_intents = []
        for intent, keywords in intent_patterns.items():
            for keyword in keywords:
                if keyword in msg_lower:
                    detected_intents.append(intent)
                    break

        if detected_intents:
            primary_intent = detected_intents[0]
            output = f"""[KUMARAS] Intent Resolution
========================================
  Message: "{message}"
  Primary Intent: {primary_intent.upper()}
  All Intents: {', '.join(detected_intents)}
========================================
RESOLVE_REQ: Intent resolved → {primary_intent}"""
        else:
            output = f"""[KUMARAS] Intent Resolution
========================================
  Message: "{message}"
  Intent: UNKNOWN (general chat)
========================================
RESOLVE_REQ: No specific command intent detected"""

        return self.success(
            output,
            data=(
                ("message", message),
                ("intent", detected_intents[0] if detected_intents else "unknown"),
                ("all_intents", ",".join(detected_intents) if detected_intents else "none"),
            ),
        )


# Export for direct import
__all__ = ["DetectCommand"]
