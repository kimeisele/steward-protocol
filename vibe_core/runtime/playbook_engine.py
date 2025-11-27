"""Playbook Engine - Conveyor Belt #2: Route to task

Routes user intent + context → task playbook
Uses LEAN logic (simple if/else, no ML for MVP)
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass
class PlaybookRoute:
    """Route information for a matched playbook"""

    task: str
    description: str
    confidence: str  # 'explicit', 'context', 'suggested'
    source: str  # What triggered this route


class PlaybookEngine:
    """Routes user intent + context → task playbook"""

    def __init__(self, registry_path: Path | None = None):
        self.registry_path = (
            registry_path or Path(__file__).parent.parent / "playbook" / "_registry.yaml"
        )
        self.registry = self._load_registry()

    def _load_registry(self) -> dict[str, Any]:
        """Load playbook registry"""
        try:
            with open(self.registry_path) as f:
                return yaml.safe_load(f)
        except Exception:
            # Fallback minimal registry
            return {"routes": [], "config": {"fallback_strategy": "suggest_options"}}

    def route(self, user_input: str, context: dict) -> PlaybookRoute:
        """Main routing logic: Tier 1 → Tier 2 → Tier 3"""

        # TIER 1: Explicit user intent (keyword matching)
        if explicit_match := self._match_keywords(user_input):
            return explicit_match

        # TIER 2: Context inference (simple rules)
        if context_match := self._infer_from_context(context):
            return context_match

        # TIER 3: Suggest options (inspiration mode)
        return self._suggest_options(context)

    def _match_keywords(self, user_input: str) -> PlaybookRoute | None:
        """Match against registry intent patterns (Tier 1)"""
        user_lower = user_input.lower().strip()

        # Don't match if input is empty
        if not user_lower:
            return None

        for route in self.registry.get("routes", []):
            patterns = route.get("intent_patterns", [])
            for pattern in patterns:
                # Simple substring match (no embeddings for MVP)
                if pattern.lower() in user_lower or user_lower in pattern.lower():
                    # Map route names to task names
                    task = self._route_to_task(route["name"])
                    return PlaybookRoute(
                        task=task,
                        description=route.get("description", ""),
                        confidence="explicit",
                        source=f"matched: '{pattern}'",
                    )

        return None

    def _infer_from_context(self, context: dict) -> PlaybookRoute | None:
        """Infer task from context signals (Tier 2 - LEAN rules!)"""

        # Rule 1: Tests failing → debug
        if context.get("tests", {}).get("failing_count", 0) > 0:
            return PlaybookRoute(
                task="debug",
                description="Fix failing tests",
                confidence="context",
                source=f"{context['tests']['failing_count']} tests failing",
            )

        # Rule 2: Uncommitted changes + no failures → test
        git_uncommitted = context.get("git", {}).get("uncommitted", 0)
        tests_failing = context.get("tests", {}).get("failing_count", 0)
        if git_uncommitted > 0 and tests_failing == 0:
            return PlaybookRoute(
                task="test",
                description="Run test suite on uncommitted changes",
                confidence="context",
                source=f"{git_uncommitted} uncommitted files",
            )

        # Rule 3: Backlog item present → implement
        backlog_item = context.get("session", {}).get("backlog_item", "")
        if backlog_item:
            return PlaybookRoute(
                task="implement",
                description=f"Implement: {backlog_item}",
                confidence="context",
                source="backlog item present",
            )

        # Rule 4: Phase is PLANNING → plan
        phase = context.get("session", {}).get("phase", "")
        if phase == "PLANNING":
            return PlaybookRoute(
                task="plan",
                description="Project in planning phase",
                confidence="context",
                source="phase=PLANNING",
            )

        return None

    def _suggest_options(self, context: dict) -> PlaybookRoute:
        """Suggest relevant tasks based on context (Tier 3)"""
        suggestions = []

        # Analyze context to build suggestions
        phase = context.get("session", {}).get("phase", "PLANNING")
        git_uncommitted = context.get("git", {}).get("uncommitted", 0)

        if phase == "PLANNING":
            suggestions.append("plan - Design architecture")

        if phase == "CODING":
            suggestions.append("implement - Code new feature")
            suggestions.append("test - Run test suite")

        if git_uncommitted > 0:
            suggestions.append("test - Verify uncommitted changes")

        suggestions.append("analyze - Explore codebase")
        suggestions.append("document - Update documentation")

        # Return first suggestion with note about alternatives
        return PlaybookRoute(
            task="analyze",  # Safe default
            description="Suggested: " + " | ".join(suggestions[:3]),
            confidence="suggested",
            source="no explicit intent or strong context signal",
        )

    def _route_to_task(self, route_name: str) -> str:
        """Map route name to task playbook name"""
        # Core routes map to analyze (as they need custom handling)
        core_routes = ["bootstrap", "session_resume", "status_check"]
        if route_name in core_routes:
            return "analyze"  # For MVP, use analyze as fallback

        # Domain routes also use analyze for now
        domain_routes = ["restaurant_app", "healthcare_app", "ecommerce_app"]
        if route_name in domain_routes:
            return "plan"  # Domain apps typically start with planning

        # Default
        return "analyze"

    def list_available_routes(self) -> list[dict[str, str]]:
        """List all available routes from registry"""
        routes = []
        for route in self.registry.get("routes", []):
            routes.append(
                {
                    "name": route["name"],
                    "description": route.get("description", ""),
                    "examples": route.get("intent_patterns", [])[:3],
                }
            )
        return routes
