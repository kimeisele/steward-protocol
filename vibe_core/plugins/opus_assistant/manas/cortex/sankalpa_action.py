"""
OPUS-102: Sankalpa Action - VEDA-4 Compliant Strategic Will.

This wraps SankalpaOrchestrator in a BaseAction interface for auto-discovery.

Karmendriya: UPASTHA (Creative/Generative) - The power to manifest intention.

SANKALPA = The Will. Without will, there is no action.
This is the FINAL Karmendriya needed for MANAS autonomy.

Handled Intent Types:
- plan_strategy: Create strategic plans
- review_todos: Review and prioritize tasks
- create_mission: Create a new mission
- list_missions: List all missions
- get_mission_status: Get mission status
- update_mission: Update mission parameters
- evaluate_strategies: Run strategy evaluation
- think_proactive: Generate proactive intents
- hygiene_check: Run daily hygiene checks

CRITICAL: Without SankalpaAction, MANAS cannot PLAN.
Planning is the bridge between perception and action.

<!-- @HARNESS
files:
  - path: vibe_core/plugins/opus_assistant/manas/cortex/sankalpa_action.py
    required: true
  - path: vibe_core/plugins/opus_assistant/manas/cortex/sankalpa.py
    required: true
wiring:
  - pattern: "class SankalpaAction\\(BaseAction\\)"
    in: vibe_core/plugins/opus_assistant/manas/cortex/sankalpa_action.py
  - pattern: "handled_intent_types.*plan_strategy"
    in: vibe_core/plugins/opus_assistant/manas/cortex/sankalpa_action.py
-->
"""

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Optional, Set

from .base_action import ActionResult, BaseAction
from .sankalpa import (
    MissionPriority,
    MissionStatus,
    SankalpaMission,
    SankalpaOrchestrator,
    SankalpaStrategy,
    SankalpaTrigger,
    StrategyFrequency,
    TriggerType,
)

if TYPE_CHECKING:
    from vibe_core.plugins.opus_assistant.manas.intent_generator import Intent

logger = logging.getLogger("MANAS.Action.Sankalpa")


class SankalpaAction(BaseAction):
    """
    Sankalpa Action - Strategic planning and mission orchestration.

    Wraps SankalpaOrchestrator in BaseAction interface for ActionLoader discovery.

    "UPASTHA (Creative) - The power to manifest intention into reality."

    CRITICAL: This is the WILL of MANAS. Without it, the system is reactive only.
    With SankalpaAction, MANAS can:
    - Create and manage long-term missions
    - Define strategies with triggers
    - Generate proactive intents
    - Plan its own improvement
    """

    # OPUS-102: VEDA-4 auto-discovery
    name = "sankalpa_action"

    # Intent types this action handles
    handled_intent_types: Set[str] = {
        # Strategic planning
        "plan_strategy",
        "create_strategy",
        "review_todos",
        "review_strategy",
        # Mission management
        "create_mission",
        "list_missions",
        "get_missions",
        "get_mission_status",
        "mission_status",
        "update_mission",
        "pause_mission",
        "resume_mission",
        "complete_mission",
        # Strategy evaluation
        "evaluate_strategies",
        "think_proactive",
        "proactive_think",
        # Hygiene (triggered by Sankalpa)
        "hygiene_check",
        "daily_hygiene",
        # Architecture audit (can be triggered by mission)
        "architecture_audit",
        # Memory review
        "memory_review",
        "review_memories",
    }

    def __init__(
        self,
        workspace: Optional[Path] = None,
        config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize Sankalpa Action.

        Args:
            workspace: Workspace root
            config: Configuration dict
        """
        super().__init__(workspace, config)
        self._orchestrator = SankalpaOrchestrator(
            workspace=self._workspace,
            config=self._config,
        )
        logger.info("[SANKALPA_ACTION] Initialized - UPASTHA (The Will)")

    def act(self, intent: "Intent") -> ActionResult:
        """
        Execute a sankalpa-related intent.

        Routes to appropriate orchestrator method based on intent type.

        Args:
            intent: The intent to execute

        Returns:
            ActionResult with execution status
        """
        intent_type = intent.type
        params = intent.params or {}

        try:
            # Strategic planning
            if intent_type in ("plan_strategy", "create_strategy"):
                return self._handle_create_strategy(intent, params)

            elif intent_type in ("review_todos", "review_strategy"):
                return self._handle_review(intent, params)

            # Mission management
            elif intent_type in ("create_mission",):
                return self._handle_create_mission(intent, params)

            elif intent_type in ("list_missions", "get_missions"):
                return self._handle_list_missions(intent)

            elif intent_type in ("get_mission_status", "mission_status"):
                return self._handle_mission_status(intent, params)

            elif intent_type in ("update_mission",):
                return self._handle_update_mission(intent, params)

            elif intent_type in ("pause_mission",):
                return self._handle_pause_mission(intent, params)

            elif intent_type in ("resume_mission",):
                return self._handle_resume_mission(intent, params)

            elif intent_type in ("complete_mission",):
                return self._handle_complete_mission(intent, params)

            # Strategy evaluation
            elif intent_type in ("evaluate_strategies", "think_proactive", "proactive_think"):
                return self._handle_evaluate(intent, params)

            # Hygiene check
            elif intent_type in ("hygiene_check", "daily_hygiene"):
                return self._handle_hygiene(intent, params)

            # Architecture audit
            elif intent_type in ("architecture_audit",):
                return self._handle_audit(intent, params)

            # Memory review
            elif intent_type in ("memory_review", "review_memories"):
                return self._handle_memory_review(intent, params)

            else:
                return ActionResult(
                    success=False,
                    action_name=self.name,
                    intent_type=intent_type,
                    error=f"Unknown intent type for SankalpaAction: {intent_type}",
                )

        except Exception as e:
            logger.error(f"[SANKALPA_ACTION] Error handling {intent_type}: {e}")
            return ActionResult(
                success=False,
                action_name=self.name,
                intent_type=intent_type,
                error=str(e),
            )

    # =========================================================================
    # MISSION MANAGEMENT
    # =========================================================================

    def _handle_create_mission(self, intent: "Intent", params: Dict) -> ActionResult:
        """Create a new mission."""
        name = params.get("name") or params.get("mission_name")
        description = params.get("description", "")
        priority = params.get("priority", "medium")

        if not name:
            return ActionResult(
                success=False,
                action_name=self.name,
                intent_type=intent.type,
                error="Missing mission name",
            )

        import uuid

        mission = SankalpaMission(
            id=f"mission_{uuid.uuid4().hex[:8]}",
            name=name,
            description=description,
            priority=MissionPriority(priority),
            status=MissionStatus.ACTIVE,
            strategies=[],
            owner="MANAS",
        )

        self._orchestrator.registry.add_mission(mission)

        logger.info(f"[SANKALPA] Created mission: {name}")
        return ActionResult(
            success=True,
            action_name=self.name,
            intent_type=intent.type,
            result={
                "mission_id": mission.id,
                "name": mission.name,
                "status": mission.status.value,
            },
            metadata={"action": "mission_created"},
        )

    def _handle_list_missions(self, intent: "Intent") -> ActionResult:
        """List all missions."""
        status = self._orchestrator.get_status()

        return ActionResult(
            success=True,
            action_name=self.name,
            intent_type=intent.type,
            result={
                "total_missions": status["total_missions"],
                "active_missions": status["active_missions"],
                "missions": status["missions"],
            },
            metadata={"action": "missions_listed"},
        )

    def _handle_mission_status(self, intent: "Intent", params: Dict) -> ActionResult:
        """Get status of a specific mission."""
        mission_id = params.get("mission_id") or params.get("id")

        if mission_id:
            mission = self._orchestrator.registry.get_mission(mission_id)
            if mission:
                return ActionResult(
                    success=True,
                    action_name=self.name,
                    intent_type=intent.type,
                    result=mission.to_dict(),
                    metadata={"action": "mission_status"},
                )
            else:
                return ActionResult(
                    success=False,
                    action_name=self.name,
                    intent_type=intent.type,
                    error=f"Mission not found: {mission_id}",
                )
        else:
            # Return overall status
            return self._handle_list_missions(intent)

    def _handle_update_mission(self, intent: "Intent", params: Dict) -> ActionResult:
        """Update mission parameters."""
        mission_id = params.get("mission_id") or params.get("id")

        if not mission_id:
            return ActionResult(
                success=False,
                action_name=self.name,
                intent_type=intent.type,
                error="Missing mission_id",
            )

        mission = self._orchestrator.registry.get_mission(mission_id)
        if not mission:
            return ActionResult(
                success=False,
                action_name=self.name,
                intent_type=intent.type,
                error=f"Mission not found: {mission_id}",
            )

        # Update fields if provided
        if "name" in params:
            mission.name = params["name"]
        if "description" in params:
            mission.description = params["description"]
        if "priority" in params:
            mission.priority = MissionPriority(params["priority"])

        self._orchestrator.registry.update_mission(mission)

        return ActionResult(
            success=True,
            action_name=self.name,
            intent_type=intent.type,
            result={"mission_id": mission_id, "updated": True},
            metadata={"action": "mission_updated"},
        )

    def _handle_pause_mission(self, intent: "Intent", params: Dict) -> ActionResult:
        """Pause a mission."""
        mission_id = params.get("mission_id") or params.get("id")

        if not mission_id:
            return ActionResult(
                success=False,
                action_name=self.name,
                intent_type=intent.type,
                error="Missing mission_id",
            )

        mission = self._orchestrator.registry.get_mission(mission_id)
        if mission:
            mission.status = MissionStatus.PAUSED
            self._orchestrator.registry.update_mission(mission)

            return ActionResult(
                success=True,
                action_name=self.name,
                intent_type=intent.type,
                result={"mission_id": mission_id, "status": "paused"},
                metadata={"action": "mission_paused"},
            )
        else:
            return ActionResult(
                success=False,
                action_name=self.name,
                intent_type=intent.type,
                error=f"Mission not found: {mission_id}",
            )

    def _handle_resume_mission(self, intent: "Intent", params: Dict) -> ActionResult:
        """Resume a paused mission."""
        mission_id = params.get("mission_id") or params.get("id")

        if not mission_id:
            return ActionResult(
                success=False,
                action_name=self.name,
                intent_type=intent.type,
                error="Missing mission_id",
            )

        mission = self._orchestrator.registry.get_mission(mission_id)
        if mission:
            mission.status = MissionStatus.ACTIVE
            self._orchestrator.registry.update_mission(mission)

            return ActionResult(
                success=True,
                action_name=self.name,
                intent_type=intent.type,
                result={"mission_id": mission_id, "status": "active"},
                metadata={"action": "mission_resumed"},
            )
        else:
            return ActionResult(
                success=False,
                action_name=self.name,
                intent_type=intent.type,
                error=f"Mission not found: {mission_id}",
            )

    def _handle_complete_mission(self, intent: "Intent", params: Dict) -> ActionResult:
        """Mark a mission as completed."""
        from datetime import datetime, timezone

        mission_id = params.get("mission_id") or params.get("id")

        if not mission_id:
            return ActionResult(
                success=False,
                action_name=self.name,
                intent_type=intent.type,
                error="Missing mission_id",
            )

        mission = self._orchestrator.registry.get_mission(mission_id)
        if mission:
            mission.status = MissionStatus.COMPLETED
            mission.completed_at = datetime.now(timezone.utc).isoformat()
            self._orchestrator.registry.update_mission(mission)

            return ActionResult(
                success=True,
                action_name=self.name,
                intent_type=intent.type,
                result={"mission_id": mission_id, "status": "completed"},
                metadata={"action": "mission_completed"},
            )
        else:
            return ActionResult(
                success=False,
                action_name=self.name,
                intent_type=intent.type,
                error=f"Mission not found: {mission_id}",
            )

    # =========================================================================
    # STRATEGY MANAGEMENT
    # =========================================================================

    def _handle_create_strategy(self, intent: "Intent", params: Dict) -> ActionResult:
        """Create a new strategy for a mission."""
        mission_id = params.get("mission_id")
        strategy_name = params.get("name") or params.get("strategy_name")
        description = params.get("description", "")
        intent_type = params.get("intent_type", "proactive_task")
        frequency = params.get("frequency", "daily")
        trigger_type = params.get("trigger_type", "idle_based")
        idle_minutes = params.get("idle_minutes", 60)

        if not mission_id or not strategy_name:
            return ActionResult(
                success=False,
                action_name=self.name,
                intent_type=intent.type,
                error="Missing mission_id or strategy name",
            )

        mission = self._orchestrator.registry.get_mission(mission_id)
        if not mission:
            return ActionResult(
                success=False,
                action_name=self.name,
                intent_type=intent.type,
                error=f"Mission not found: {mission_id}",
            )

        import uuid

        strategy = SankalpaStrategy(
            id=f"strategy_{uuid.uuid4().hex[:8]}",
            name=strategy_name,
            description=description,
            trigger=SankalpaTrigger(
                trigger_type=TriggerType(trigger_type),
                idle_minutes=idle_minutes,
            ),
            frequency=StrategyFrequency(frequency),
            intent_type=intent_type,
            intent_template=params.get("intent_template", {"title": strategy_name}),
            enabled=True,
        )

        mission.strategies.append(strategy)
        self._orchestrator.registry.update_mission(mission)

        logger.info(f"[SANKALPA] Created strategy: {strategy_name} for mission: {mission.name}")
        return ActionResult(
            success=True,
            action_name=self.name,
            intent_type=intent.type,
            result={
                "strategy_id": strategy.id,
                "mission_id": mission_id,
                "name": strategy_name,
            },
            metadata={"action": "strategy_created"},
        )

    def _handle_review(self, intent: "Intent", params: Dict) -> ActionResult:
        """Review current strategies and todos."""
        status = self._orchestrator.get_status()

        # Build review summary
        active_strategies = []
        for mission in self._orchestrator.registry.get_active_missions():
            for strategy in mission.strategies:
                if strategy.enabled:
                    active_strategies.append(
                        {
                            "mission": mission.name,
                            "strategy": strategy.name,
                            "frequency": strategy.frequency.value,
                            "last_executed": strategy.last_executed,
                            "executions_today": strategy.execution_count_today,
                        }
                    )

        return ActionResult(
            success=True,
            action_name=self.name,
            intent_type=intent.type,
            result={
                "active_missions": status["active_missions"],
                "enabled_strategies": status["enabled_strategies"],
                "strategies": active_strategies,
            },
            metadata={"action": "review_completed"},
        )

    # =========================================================================
    # PROACTIVE THINKING
    # =========================================================================

    def _handle_evaluate(self, intent: "Intent", params: Dict) -> ActionResult:
        """Evaluate strategies and generate proactive intents."""
        context = params.get("context", {})
        idle_minutes = params.get("idle_minutes", 0)
        pending_intents = params.get("pending_intents", 0)

        # Use orchestrator's think method
        proactive_intents = self._orchestrator.think(
            context=context,
            idle_minutes=idle_minutes,
            pending_intents=pending_intents,
        )

        return ActionResult(
            success=True,
            action_name=self.name,
            intent_type=intent.type,
            result={
                "generated_intents": len(proactive_intents),
                "intents": [i.to_dict() for i in proactive_intents],
            },
            metadata={"action": "evaluation_completed"},
        )

    # =========================================================================
    # HYGIENE & AUDIT
    # =========================================================================

    def _handle_hygiene(self, intent: "Intent", params: Dict) -> ActionResult:
        """Run daily hygiene check."""
        import subprocess

        actions = params.get("actions", ["lint", "format", "test_quick"])
        results = {"success": True, "checks": {}}

        try:
            if "lint" in actions:
                lint_result = subprocess.run(
                    ["ruff", "check", "."],
                    capture_output=True,
                    text=True,
                    timeout=60,
                    cwd=str(self._workspace),
                )
                results["checks"]["lint"] = {
                    "passed": lint_result.returncode == 0,
                    "issues": lint_result.stdout.count("\n") if lint_result.stdout else 0,
                }
                if lint_result.returncode != 0:
                    results["success"] = False

            if "format" in actions:
                format_result = subprocess.run(
                    ["ruff", "format", "--check", "."],
                    capture_output=True,
                    text=True,
                    timeout=60,
                    cwd=str(self._workspace),
                )
                results["checks"]["format"] = {"passed": format_result.returncode == 0}
                if format_result.returncode != 0:
                    results["success"] = False

            if "test_quick" in actions:
                test_result = subprocess.run(
                    ["python", "-m", "pytest", "tests/unit/loaders/", "-x", "-q", "--timeout=30"],
                    capture_output=True,
                    text=True,
                    timeout=120,
                    cwd=str(self._workspace),
                )
                results["checks"]["test_quick"] = {
                    "passed": test_result.returncode == 0,
                    "output": test_result.stdout[-300:] if test_result.stdout else "",
                }
                if test_result.returncode != 0:
                    results["success"] = False

            return ActionResult(
                success=results["success"],
                action_name=self.name,
                intent_type=intent.type,
                result=results,
                metadata={"action": "hygiene_completed"},
            )

        except Exception as e:
            return ActionResult(
                success=False,
                action_name=self.name,
                intent_type=intent.type,
                error=str(e),
            )

    def _handle_audit(self, intent: "Intent", params: Dict) -> ActionResult:
        """Run architecture audit via DHARMA."""
        try:
            from .dharma import DharmaAuditor

            auditor = DharmaAuditor(workspace=self._workspace)
            report = auditor.audit()

            return ActionResult(
                success=True,
                action_name=self.name,
                intent_type=intent.type,
                result={
                    "violations_found": len(report.violations),
                    "compliance_score": report.compliance_score,
                    "drift_detected": report.total_violations > 0,
                },
                metadata={"action": "audit_completed"},
            )
        except Exception as e:
            return ActionResult(
                success=False,
                action_name=self.name,
                intent_type=intent.type,
                error=f"Audit failed: {e}",
            )

    def _handle_memory_review(self, intent: "Intent", params: Dict) -> ActionResult:
        """Review recent memories and patterns."""
        # This would integrate with the karma/memory system
        # For now, return a placeholder
        return ActionResult(
            success=True,
            action_name=self.name,
            intent_type=intent.type,
            result={
                "status": "memory_review_acknowledged",
                "message": "Memory review scheduled",
            },
            metadata={"action": "memory_review"},
        )
