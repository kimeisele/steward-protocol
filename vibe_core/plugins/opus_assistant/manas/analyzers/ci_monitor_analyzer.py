"""
OPUS-041: VAK (The Voice) - CI Monitor Analyzer.

This analyzer uses ShellCortex to check system status and
generate intents when CI issues are detected.

"The system must be able to observe itself."
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

from ..cortex.shell import ShellCortex, ShellResult
from ..intent_generator import Intent, IntentPriority, IntentRisk
from .base import AnalyzerConfig, BaseAnalyzer

logger = logging.getLogger("MANAS.Analyzer.CIMonitor")


class CIMonitorAnalyzer(BaseAnalyzer):
    """
    Analyzer that monitors CI/system status via ShellCortex.

    This analyzer:
    1. Runs 'status' command to check system health
    2. Runs 'capabilities' to ensure system is functional
    3. Generates intents when issues are detected

    All commands are SAFE (read-only) and execute automatically.
    """

    def __init__(
        self,
        workspace: Optional[Path] = None,
        config: Optional[AnalyzerConfig] = None,
    ):
        """
        Initialize CI Monitor Analyzer.

        Args:
            workspace: Workspace root path
            config: Optional configuration
        """
        super().__init__(workspace, config)
        self._cortex = ShellCortex(workspace=self._workspace)
        self._last_status_check: Optional[datetime] = None
        self._last_status_result: Optional[ShellResult] = None

    @property
    def name(self) -> str:
        """Unique name for this analyzer."""
        return "ci_monitor"

    def analyze(self, context: Dict[str, Any]) -> List[Intent]:
        """
        Analyze CI/system status and generate intents.

        Args:
            context: Current system context

        Returns:
            List of intents for any issues detected
        """
        if not self.is_enabled:
            return []

        intents = []

        # Check system status
        status_intent = self._check_system_status(context)
        if status_intent:
            intents.append(status_intent)

        # Check capabilities
        cap_intent = self._check_capabilities(context)
        if cap_intent:
            intents.append(cap_intent)

        # Respect max_intents_per_run
        if len(intents) > self._config.max_intents_per_run:
            intents = intents[: self._config.max_intents_per_run]

        return intents

    def _check_system_status(self, context: Dict[str, Any]) -> Optional[Intent]:
        """
        Check system status via ShellCortex.

        Returns an intent if status check fails or shows issues.
        """
        logger.debug("Checking system status...")

        result = self._cortex.execute_safe(["status"])
        self._last_status_result = result
        self._last_status_check = datetime.utcnow()

        # If command was blocked, something is wrong with our classification
        if result.blocked:
            logger.error(f"Status command was blocked: {result.error}")
            return None

        # Check exit code
        if result.exit_code != 0:
            # Status check failed - generate an intent
            return Intent(
                id=f"ci_status_{uuid4().hex[:8]}",
                intent_type="ci_status_failure",
                title="System Status Check Failed",
                description=f"The 'status' command returned exit code {result.exit_code}. "
                f"Stderr: {result.stderr[:200] if result.stderr else 'none'}",
                reasoning="MANAS detected that the system status check failed. "
                "This could indicate kernel issues or configuration problems.",
                priority=IntentPriority.HIGH,
                risk=IntentRisk.SAFE,  # Just observing, not changing
                auto_executable=False,  # Human should investigate
                params={
                    "exit_code": result.exit_code,
                    "stdout": result.stdout[:500] if result.stdout else "",
                    "stderr": result.stderr[:500] if result.stderr else "",
                },
                # WEAVING: Link to kernel/CI docs
                related_docs=["024-KERNEL-PROTECTION-AUDIT.md"],
            )

        # Parse status output for issues
        return self._parse_status_for_issues(result)

    def _parse_status_for_issues(self, result: ShellResult) -> Optional[Intent]:
        """
        Parse status output for known issues.

        Returns an intent if issues are detected.
        """
        stdout = result.stdout.lower()

        # Check for known issue patterns
        if "error" in stdout or "failed" in stdout:
            return Intent(
                id=f"ci_status_error_{uuid4().hex[:8]}",
                intent_type="ci_status_error_detected",
                title="System Status Shows Errors",
                description="The system status output contains error indicators.",
                reasoning="MANAS detected error keywords in status output. This may require human investigation.",
                priority=IntentPriority.MEDIUM,
                risk=IntentRisk.SAFE,
                auto_executable=False,
                params={
                    "status_output": result.stdout[:1000],
                },
                related_docs=["024-KERNEL-PROTECTION-AUDIT.md"],
            )

        return None

    def _check_capabilities(self, context: Dict[str, Any]) -> Optional[Intent]:
        """
        Check system capabilities via ShellCortex.

        Returns an intent if capabilities check fails.
        """
        logger.debug("Checking system capabilities...")

        result = self._cortex.execute_safe(["capabilities"])

        if result.blocked:
            logger.error(f"Capabilities command was blocked: {result.error}")
            return None

        if result.exit_code != 0:
            return Intent(
                id=f"ci_caps_{uuid4().hex[:8]}",
                intent_type="ci_capabilities_failure",
                title="Capabilities Check Failed",
                description=f"The 'capabilities' command returned exit code {result.exit_code}.",
                reasoning="MANAS could not retrieve system capabilities. This may indicate a broken installation.",
                priority=IntentPriority.HIGH,
                risk=IntentRisk.SAFE,
                auto_executable=False,
                params={
                    "exit_code": result.exit_code,
                    "error": result.stderr[:500] if result.stderr else "",
                },
                related_docs=["024-KERNEL-PROTECTION-AUDIT.md"],
            )

        # Try to parse capabilities JSON
        try:
            caps = json.loads(result.stdout)

            # Check for missing critical capabilities
            if "system_commands" not in caps:
                return Intent(
                    id=f"ci_caps_incomplete_{uuid4().hex[:8]}",
                    intent_type="ci_capabilities_incomplete",
                    title="Incomplete System Capabilities",
                    description="System capabilities response is missing 'system_commands'.",
                    reasoning="MANAS detected incomplete capabilities. The system may be partially configured.",
                    priority=IntentPriority.MEDIUM,
                    risk=IntentRisk.SAFE,
                    auto_executable=False,
                    params={
                        "capabilities": caps,
                    },
                    related_docs=["024-KERNEL-PROTECTION-AUDIT.md"],
                )

        except json.JSONDecodeError:
            # Capabilities output is not valid JSON
            return Intent(
                id=f"ci_caps_invalid_{uuid4().hex[:8]}",
                intent_type="ci_capabilities_invalid_json",
                title="Invalid Capabilities Response",
                description="The 'capabilities' command returned invalid JSON.",
                reasoning="MANAS could not parse capabilities as JSON. This may indicate a bug or corruption.",
                priority=IntentPriority.MEDIUM,
                risk=IntentRisk.SAFE,
                auto_executable=False,
                params={
                    "raw_output": result.stdout[:500],
                },
                related_docs=["024-KERNEL-PROTECTION-AUDIT.md"],
            )

        return None

    def get_last_status(self) -> Optional[ShellResult]:
        """Get the result of the last status check."""
        return self._last_status_result

    def get_last_check_time(self) -> Optional[datetime]:
        """Get the time of the last status check."""
        return self._last_status_check
