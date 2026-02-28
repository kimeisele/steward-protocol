"""Federation Dispatcher — Cross-repo communication via GitHub dispatch events.

Sends directives to agent-city and reads CityReports for strategy context.
Communication primitive: repository_dispatch (native GitHub, no extra infra).

Directive types:
    - create_mission: Community intent → Sankalpa Mission in agent-city
    - register_agent: Agent registration from Moltbook discovery
    - governance_signal: Strategy hints for agent-city council

CityReport: Received via federation-receiver.yml workflow, read from
    .vibe/state/city_report.json during DHARMA strategy evaluation.
"""

import json
import logging
import os
import subprocess
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger("MOLTBOOK.FEDERATION")

# Agent-city repo for dispatch target
_AGENT_CITY_REPO = "kimeisele/agent-city"


class FederationDispatcher:
    """Dispatch directives to agent-city via GitHub repository_dispatch.

    Uses `gh api` CLI — same pattern as agent-city's IntentExecutor.
    Requires FEDERATION_PAT env var (GitHub PAT with repo scope).
    """

    def __init__(self, state_dir: Optional[Path] = None):
        self._state_dir = state_dir
        self._pat = os.environ.get("FEDERATION_PAT", "")
        self._dispatched_count = 0

    @property
    def available(self) -> bool:
        """Federation is available when PAT is configured."""
        return bool(self._pat)

    def dispatch_directive(
        self,
        directive_type: str,
        params: Dict[str, str],
    ) -> bool:
        """Send a directive to agent-city via repository_dispatch.

        Args:
            directive_type: One of create_mission, register_agent, governance_signal
            params: Directive parameters (topic, context, priority, etc.)

        Returns:
            True if dispatch succeeded, False otherwise.
        """
        if not self._pat:
            logger.debug("Federation unavailable: FEDERATION_PAT not set")
            return False

        payload = {
            "event_type": "mothership-directive",
            "client_payload": {
                "directive_type": directive_type,
                "params": params,
            },
        }

        try:
            result = subprocess.run(
                [
                    "gh", "api",
                    f"repos/{_AGENT_CITY_REPO}/dispatches",
                    "--method", "POST",
                    "--input", "-",
                ],
                input=json.dumps(payload),
                capture_output=True,
                text=True,
                timeout=15,
                env={**os.environ, "GH_TOKEN": self._pat},
            )

            if result.returncode == 0:
                self._dispatched_count += 1
                logger.info(
                    f"FEDERATION: dispatched {directive_type} to {_AGENT_CITY_REPO} "
                    f"(#{self._dispatched_count})"
                )
                return True

            logger.warning(
                f"FEDERATION: dispatch failed (rc={result.returncode}): "
                f"{result.stderr[:200]}"
            )
            return False
        except subprocess.TimeoutExpired:
            logger.warning("FEDERATION: dispatch timed out (15s)")
            return False
        except FileNotFoundError:
            logger.debug("FEDERATION: gh CLI not available")
            return False
        except Exception as e:
            logger.warning(f"FEDERATION: dispatch error: {e}")
            return False

    def dispatch_create_mission(
        self,
        topic: str,
        context: str,
        source_post_id: str = "",
        priority: str = "medium",
    ) -> bool:
        """Dispatch a create_mission directive — Community intent → agent-city code task."""
        return self.dispatch_directive(
            "create_mission",
            {
                "topic": topic,
                "context": context,
                "source_post_id": source_post_id,
                "priority": priority,
            },
        )

    def dispatch_register_agent(self, agent_name: str, karma: int = 0) -> bool:
        """Dispatch agent registration — Moltbook agent → agent-city citizen."""
        return self.dispatch_directive(
            "register_agent",
            {"agent_name": agent_name, "karma": str(karma)},
        )


def read_city_report(state_dir: Optional[Path] = None) -> Optional[Dict]:
    """Read the latest CityReport from .vibe/state/city_report.json.

    Called during DHARMA strategy evaluation to incorporate
    agent-city governance state into intent generation.

    Returns None if no report exists or is unreadable.
    """
    if state_dir:
        report_path = state_dir / "city_report.json"
    else:
        # Fallback: check relative to working directory
        report_path = Path(".vibe/state/city_report.json")

    if not report_path.exists():
        return None

    try:
        data = json.loads(report_path.read_text())
        if isinstance(data, dict):
            return data
        return None
    except Exception as e:
        logger.debug(f"CityReport read failed: {e}")
        return None


def extract_city_context(report: Dict) -> str:
    """Extract human-readable context from CityReport for strategy.

    Returns compact text that can be used as strategy context.
    """
    parts: List[str] = []

    population = report.get("population", 0)
    alive = report.get("alive", 0)
    if population:
        parts.append(f"Agent City: {alive}/{population} agents alive")

    mayor = report.get("elected_mayor")
    if mayor:
        parts.append(f"Mayor: {mayor}")

    # Contract status
    contracts = report.get("contract_status", {})
    failing = [k for k, v in contracts.items() if v == "failing"]
    if failing:
        parts.append(f"Failing contracts: {', '.join(failing)}")

    # Recent governance actions
    actions = report.get("recent_actions", [])
    if actions:
        parts.append(f"Recent: {'; '.join(actions[:3])}")

    # Mission results
    results = report.get("mission_results", [])
    completed = [r for r in results if r.get("status") == "completed"]
    if completed:
        parts.append(f"Completed missions: {len(completed)}")

    return " | ".join(parts) if parts else ""
