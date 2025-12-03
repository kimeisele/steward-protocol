"""Playbook Router - Conveyor Belt #2: Route to task

Routes user intent + context → task playbook
Uses LEAN logic (simple if/else, no ML for MVP)

PHASE 3 WIRING: Integrated with MilkOceanRouter for Brahma Protocol gatekeeping
"""

import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

logger = logging.getLogger(__name__)


@dataclass
class PlaybookRoute:
    """Route information for a matched playbook"""

    task: str
    description: str
    confidence: str  # 'explicit', 'context', 'suggested'
    source: str  # What triggered this route


class PlaybookRouter:
    """Routes user intent + context → task playbook

    PHASE 3 INTEGRATION: Checks routes with MilkOceanRouter (Brahma Protocol gatekeeping)
    """

    def __init__(self, registry_path: Path | None = None, milk_ocean_router=None):
        self.registry_path = registry_path or Path(__file__).parent.parent / "playbook" / "_registry.yaml"
        self.registry = self._load_registry()  # Keep original registry loading
        self.matrix_rules = self._load_matrix()  # Add matrix rules initialization
        logger.info(
            f"📚 PlaybookRouter initialized with {len(self.registry.get('routes', []))} registry routes and {len(self.matrix_rules)} matrix rules"
        )
        # Optional integration with MilkOceanRouter (Brahma Protocol)
        self.milk_ocean_router = milk_ocean_router
        self._milk_ocean_available = milk_ocean_router is not None

    def _load_registry(self) -> dict[str, Any]:
        """Load playbook registry"""
        try:
            with open(self.registry_path) as f:
                return yaml.safe_load(f)
        except Exception:
            # Fallback minimal registry
            return {"routes": [], "config": {"fallback_strategy": "suggest_options"}}

    def route(self, user_input: str, context: dict) -> PlaybookRoute:
        """Main routing logic: Tier 1 → Tier 2 → Tier 3

        PHASE 3: Routes through MilkOceanRouter (Brahma Protocol gatekeeping) if available
        """

        # TIER 1: Explicit user intent (keyword matching)
        if explicit_match := self._match_keywords(user_input):
            return self._check_with_milk_ocean(explicit_match, user_input)

        # TIER 2: Context inference (simple rules)
        if context_match := self._infer_from_context(context):
            return self._check_with_milk_ocean(context_match, user_input)

        # TIER 3: Suggest options (inspiration mode)
        return self._check_with_milk_ocean(self._suggest_options(context), user_input)

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

    def _check_with_milk_ocean(self, route: PlaybookRoute, user_input: str) -> PlaybookRoute:
        """
        PHASE 3 INTEGRATION: Check route with MilkOceanRouter (Brahma Protocol gatekeeping)

        If MilkOcean is available, validate the route through Brahma's 4-tier security gates.
        Blocked requests are rejected; normal/high priority requests proceed.
        """
        if not self._milk_ocean_available:
            # MilkOcean not available - return route as-is
            return route

        try:
            # Send route description through MilkOcean gates
            prayer = f"Route to {route.task}: {route.description}"
            gate_result = self.milk_ocean_router.process_prayer(
                user_input=prayer, agent_id="PLAYBOOK_ROUTER", critical=False
            )

            # Check if request was blocked
            if gate_result.get("status") == "blocked":
                logger.warning(f"🚫 Route blocked by MilkOcean: {gate_result.get('reason')}")
                # Return route but annotate with warning
                route.source += " [GATED BY BRAHMA: LOW PRIORITY QUEUE]"
                return route

            # Log successful gate passage
            logger.info(f"✅ Route '{route.task}' passed MilkOcean gates: {gate_result.get('status')}")

            return route

        except Exception as e:
            # MilkOcean error - fallback to route as-is with warning logged
            logger.warning(f"⚠️ MilkOcean integration error (graceful fallback): {e}")
            return route

    def _load_matrix(self) -> List[Dict[str, Any]]:
        """
        Load routing rules from MATRIX.md (The Modular Synth Patch Bay).
        """
        matrix_path = Path("MATRIX.md")

        if not matrix_path.exists():
            logger.warning("⚠️  MATRIX.md not found in root. Using hardcoded routes.")
            return []

        try:
            content = matrix_path.read_text()
            return self._parse_matrix_content(content)
        except Exception as e:
            logger.error(f"❌ Failed to parse MATRIX.md: {e}")
            return []

    def _parse_matrix_content(self, content: str) -> List[Dict[str, Any]]:
        """Parse the content of MATRIX.md to extract routing rules (Stateless MVP)."""
        rules = []
        for line in content.splitlines():
            line = line.strip()
            # Only process table rows
            if not line.startswith("|"):
                continue

            # Skip headers and separators
            if "Intent Pattern" in line or "---" in line:
                continue

            # Parse row
            try:
                parts = [p.strip() for p in line.split("|") if p.strip()]
                if len(parts) >= 2:
                    pattern = parts[0].strip("`")
                    circuit = parts[1].strip("`")
                    priority = parts[2] if len(parts) > 2 else "NORMAL"
                    status = parts[3] if len(parts) > 3 else "ACTIVE"

                    if "ACTIVE" in status or "🟢" in status:
                        rules.append({"pattern": pattern, "circuit": circuit, "priority": priority})
                        logger.info(f"Added rule: {pattern} -> {circuit}")
            except Exception:
                continue

        return rules

    def _parse_matrix_row(self, line: str) -> Optional[Dict[str, Any]]:
        """Parse a single markdown table row into a rule dict."""
        try:
            # Split by pipe and strip whitespace
            parts = [p.strip() for p in line.split("|") if p.strip()]

            # Need at least Pattern and Circuit
            if len(parts) < 2:
                return None

            pattern = parts[0].strip("`")
            circuit = parts[1].strip("`")
            priority = parts[2] if len(parts) > 2 else "NORMAL"
            status = parts[3] if len(parts) > 3 else "ACTIVE"

            # Only include active rules
            if "ACTIVE" in status or "🟢" in status:
                return {"pattern": pattern, "circuit": circuit, "priority": priority}
            return None
        except Exception:
            return None

    def _route_to_task(self, route_name: str) -> str:
        """
        Map a route name (intent) to a specific task ID (Playbook).

        Priority:
        1. MATRIX.md Rules (Dynamic)
        2. Hardcoded System Routes (Fallback)
        """
        # 1. Check Matrix Rules
        for rule in self.matrix_rules:
            # Check if route_name matches the pattern (regex)
            # We use re.search to match the pattern within the route_name (which is usually the user input or a classified intent)
            # Actually, route_name passed here is usually the *classified intent* from MilkOcean (e.g. "agent_birth").
            # But MATRIX.md patterns are regexes on the *input* or *intent*.
            # If route_name is "agent_birth", and pattern is "(create|spawn).*agent", it might not match directly if route_name is normalized.
            # However, MilkOcean returns a "route_name" which is often the tool name or a keyword.
            # Let's assume route_name IS the intent string for now.

            # If the pattern matches the route_name (which might be the raw input if MilkOcean failed, or the intent)
            try:
                if re.search(rule["pattern"], route_name, re.IGNORECASE):
                    logger.info(f"🎛️  Matrix Route Match: '{route_name}' -> {rule['circuit']}")
                    return rule["circuit"]
            except re.error:
                logger.warning(f"Invalid regex in MATRIX.md: {rule['pattern']}")
                continue

        # 2. Hardcoded Fallbacks (Legacy/System)
        if route_name == "analyze_architecture":
            return "ARCHITECTURE_ANALYSIS"

        if route_name == "debug_fix":
            return "DEBUG_FIX_V2"

        if route_name == "governance_vote":
            return "GOVERNANCE_VOTE_V2"

        if route_name == "research_synthesis":
            return "RESEARCH_SYNTH_V2"

        # Domain routes also use analyze for now
        domain_routes = ["restaurant_app", "healthcare_app", "ecommerce_app"]
        if route_name in domain_routes:
            return "plan"  # Domain apps typically start with planning

        # GAD-5500: Agent Birth Circuit (Fallback if not in Matrix)
        if route_name in ["agent_birth", "spawn_agent"]:
            return "AGENT_BIRTH_V1"

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
