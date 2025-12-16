"""
MANAS ORACLE API - The Wisdom Interface (OPUS-089)

This is the **clean separation of concerns** entry point for consulting MANAS.
Other system components (Heartbeat, Envoy, etc.) call this API instead of
directly coupling to the CognitiveKernel.

Philosophy:
    "System agents are fractal-matching collections of jobs"
    → MANAS is exposed via a single, clear interface
    → No spaghetti code, just Service-Oriented Architecture

Key Methods:
    - consult(context) → AnalysisResult
    - pre_analysis(task_context) → Recommendation
    - post_analysis(task_result) → Reflection

Usage:
    from vibe_core.plugins.opus_assistant.manas.api import ManasOracle

    oracle = ManasOracle()
    recommendation = oracle.consult({
        "task_title": "Deploy to production",
        "risk_level": "high",
        "changes": ["config.yaml", "main.py"]
    })

    print(f"Priority: {recommendation.priority}")
    print(f"Safety: {recommendation.safety_score}")
    print(f"Advice: {recommendation.advice}")
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from .cognitive_kernel import CognitiveKernel, IntentConfidence, ManasConfig
from .intent_generator import Intent, IntentPriority, IntentRisk
from .memory_store import MemoryStore

logger = logging.getLogger("MANAS.Oracle")


@dataclass
class AnalysisResult:
    """Result of MANAS consultation - the "wisdom" response."""

    # Core recommendation
    priority: IntentPriority
    safety_score: float  # 0.0-1.0: How safe is this action?
    confidence: float  # 0.0-1.0: How confident is MANAS in this analysis?

    # Guidance
    advice: str  # Free-form advice/warnings
    suggested_action: Optional[str] = None  # What MANAS would do
    risks: List[str] = field(default_factory=list)  # Identified risks
    precautions: List[str] = field(default_factory=list)  # Suggested safeguards

    # Traceability
    analysis_timestamp: datetime = field(default_factory=datetime.now)
    manas_reasoning: Optional[Dict[str, Any]] = None  # Debug: Why did MANAS think this?

    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "priority": self.priority.value if isinstance(self.priority, IntentPriority) else str(self.priority),
            "safety_score": round(self.safety_score, 2),
            "confidence": round(self.confidence, 2),
            "advice": self.advice,
            "suggested_action": self.suggested_action,
            "risks": self.risks,
            "precautions": self.precautions,
            "analysis_timestamp": self.analysis_timestamp.isoformat(),
            "manas_reasoning": self.manas_reasoning,
        }

    def __str__(self) -> str:
        """Human-readable format."""
        lines = [
            "🧠 MANAS Analysis:",
            f"  Priority: {self.priority.value if isinstance(self.priority, IntentPriority) else self.priority}",
            f"  Safety: {self.safety_score:.0%}",
            f"  Confidence: {self.confidence:.0%}",
            f"  Advice: {self.advice}",
        ]

        if self.risks:
            lines.append(f"  Risks: {', '.join(self.risks)}")
        if self.precautions:
            lines.append(f"  Precautions: {', '.join(self.precautions)}")

        return "\n".join(lines)


class ManasOracle:
    """
    The Manas Oracle - Wisdom Interface for System Agents.

    This is the **clean API** that allows any system component to ask MANAS
    for advice without coupling to internal implementation details.

    Design principles:
    1. **Deterministic**: Same input → same output (no randomness)
    2. **Traceable**: All advice includes reasoning
    3. **Bounded**: Consults are fast (< 100ms)
    4. **Stateful**: Learns from history via MemoryStore
    """

    def __init__(self, config: Optional[ManasConfig] = None):
        """
        Initialize the Oracle with CognitiveKernel.

        Args:
            config: Optional ManasConfig. If None, uses defaults.
        """
        self.config = config or ManasConfig()
        # Use workspace if available, otherwise current directory

        workspace = Path.cwd()
        self.kernel = CognitiveKernel(workspace=workspace, config=self.config)
        logger.info("🧠 ManasOracle initialized")

    # =========================================================================
    # PRIMARY API: consult(context) → AnalysisResult
    # =========================================================================

    def consult(self, context: Dict[str, Any]) -> AnalysisResult:
        """
        Core method: Ask MANAS for wisdom on a decision.

        This is the main entry point for all consultations.

        Args:
            context: Dict with task/decision context. Common keys:
                - task_title: str - What is being done?
                - task_type: str - Type of task (deploy, refactor, test, etc.)
                - risk_level: str - Perceived risk (low, medium, high, critical)
                - changes: List[str] - Files/components affected
                - is_automated: bool - Is this an automated action?
                - user_approval: bool - Has a human approved it?

        Returns:
            AnalysisResult with recommendation

        Example:
            context = {
                "task_title": "Deploy to production",
                "task_type": "deploy",
                "risk_level": "high",
                "changes": ["main.py", "config.yaml"],
                "is_automated": False,
                "user_approval": True
            }
            result = oracle.consult(context)
            print(f"Safety: {result.safety_score:.0%}")
        """
        try:
            # Extract context
            task_title = context.get("task_title", "unknown task")
            task_type = context.get("task_type", "general")
            risk_level_str = context.get("risk_level", "medium").lower()
            changes = context.get("changes", [])
            is_automated = context.get("is_automated", False)
            user_approval = context.get("user_approval", False)

            # Map risk_level string to safety_score
            risk_to_safety = {
                "low": 0.95,
                "medium": 0.70,
                "high": 0.40,
                "critical": 0.10,
            }
            base_safety_score = risk_to_safety.get(risk_level_str, 0.50)

            # Boost safety if user approved
            if user_approval:
                base_safety_score = min(0.95, base_safety_score + 0.15)

            # Penalty if automated AND high risk AND no approval
            if is_automated and risk_level_str in ("high", "critical") and not user_approval:
                base_safety_score = max(0.10, base_safety_score - 0.20)

            # Determine priority from risk level
            priority_map = {
                "critical": IntentPriority.CRITICAL,
                "high": IntentPriority.HIGH,
                "medium": IntentPriority.MEDIUM,
                "low": IntentPriority.LOW,
            }
            priority = priority_map.get(risk_level_str, IntentPriority.MEDIUM)

            # Generate risks/precautions based on context
            risks = self._identify_risks(context)
            precautions = self._suggest_precautions(context, risks)

            # Query memory for historical patterns
            success_rate = self.kernel._memory.get_success_rate(task_type)
            confidence = 0.5 + (success_rate * 0.5)  # Confidence based on history

            # Build advice
            advice = self._generate_advice(
                task_title=task_title,
                task_type=task_type,
                safety_score=base_safety_score,
                changes_count=len(changes),
                user_approval=user_approval,
                success_rate=success_rate,
            )

            # Suggest action
            suggested_action = self._suggest_action(
                task_type=task_type,
                safety_score=base_safety_score,
                user_approval=user_approval,
            )

            result = AnalysisResult(
                priority=priority,
                safety_score=base_safety_score,
                confidence=confidence,
                advice=advice,
                suggested_action=suggested_action,
                risks=risks,
                precautions=precautions,
                manas_reasoning={
                    "risk_level": risk_level_str,
                    "changes_count": len(changes),
                    "user_approval": user_approval,
                    "is_automated": is_automated,
                    "success_rate": round(success_rate, 2),
                    "base_safety_score": round(base_safety_score, 2),
                },
            )

            logger.info(f"🧠 MANAS.consult() → {result.priority.value} | Safety: {result.safety_score:.0%}")
            return result

        except Exception as e:
            logger.error(f"❌ MANAS.consult() failed: {e}", exc_info=True)
            # Fallback to safe response
            return AnalysisResult(
                priority=IntentPriority.LOW,
                safety_score=0.5,
                confidence=0.3,
                advice=f"⚠️ Oracle consultation failed: {str(e)}. Assuming neutral stance.",
                risks=["System error during analysis"],
                precautions=["Proceed with caution", "Manual review recommended"],
            )

    # =========================================================================
    # SECONDARY APIS: pre_analysis, post_analysis
    # =========================================================================

    def pre_analysis(self, task_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Pre-execution hook: Should this task run at all?

        Called BEFORE UnifiedRouter executes a task.
        Returns a gate decision: can the task proceed?

        Args:
            task_context: Dict with task metadata

        Returns:
            Dict with keys:
            - proceed: bool - Should the task run?
            - reason: str - Why or why not?
            - recommendation: AnalysisResult - Full analysis

        Example:
            gate = oracle.pre_analysis({"task_id": "123", "priority": "high"})
            if gate["proceed"]:
                unified_router.execute(task)
        """
        recommendation = self.consult(task_context)

        # Decision logic
        proceed = recommendation.safety_score >= 0.40  # Threshold

        return {
            "proceed": proceed,
            "reason": recommendation.advice,
            "safety_score": recommendation.safety_score,
            "recommendation": recommendation,
        }

    def post_analysis(self, task_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Post-execution hook: Learn from what happened.

        Called AFTER task execution. MANAS updates its memory.

        Args:
            task_result: Dict with execution result
                - task_type: str
                - success: bool
                - duration_ms: float
                - error: Optional[str]

        Returns:
            Dict with learning summary
        """
        try:
            task_type = task_result.get("task_type", "unknown")
            success = task_result.get("success", False)
            error = task_result.get("error", None)
            duration_ms = task_result.get("duration_ms", 0)

            # Record to memory using the correct API
            outcome = "success" if success else "failed"
            feedback = f"Error: {error}" if error else None

            self.kernel._memory.record_intent_outcome(
                intent_type=task_type,
                description="Task execution via MANAS Oracle",
                outcome=outcome,
                feedback=feedback,
                execution_time_ms=int(duration_ms),
            )

            logger.info(f"🧠 MANAS.post_analysis() recorded {task_type} → {'✅ success' if success else '❌ failed'}")

            return {
                "recorded": True,
                "task_type": task_type,
                "success": success,
            }

        except Exception as e:
            logger.error(f"❌ MANAS.post_analysis() failed: {e}")
            return {"recorded": False, "error": str(e)}

    # =========================================================================
    # HELPER METHODS
    # =========================================================================

    def _identify_risks(self, context: Dict[str, Any]) -> List[str]:
        """Identify risks in a context."""
        risks = []

        risk_level = context.get("risk_level", "medium").lower()
        if risk_level == "critical":
            risks.append("Critical risk level - requires human approval")
        elif risk_level == "high":
            risks.append("High risk - potential for major impact")

        changes = context.get("changes", [])
        if len(changes) > 10:
            risks.append(f"Large changeset ({len(changes)} files) - scope creep risk")

        if context.get("is_automated") and not context.get("user_approval"):
            risks.append("Automated action without human approval")

        if "production" in context.get("task_title", "").lower():
            risks.append("Production environment - zero-error tolerance")

        return risks

    def _suggest_precautions(self, context: Dict[str, Any], risks: List[str]) -> List[str]:
        """Suggest precautions based on context and risks."""
        precautions = []

        if any("production" in r.lower() for r in risks):
            precautions.append("Create backup before deployment")
            precautions.append("Test in staging first")
            precautions.append("Have rollback plan ready")

        if any("large changeset" in r.lower() for r in risks):
            precautions.append("Break into smaller changes")
            precautions.append("Review each change carefully")

        if any("approval" in r.lower() for r in risks):
            precautions.append("Get explicit human sign-off")
            precautions.append("Document rationale for change")

        return precautions

    def _generate_advice(
        self,
        task_title: str,
        task_type: str,
        safety_score: float,
        changes_count: int,
        user_approval: bool,
        success_rate: float,
    ) -> str:
        """Generate human-readable advice."""
        if safety_score >= 0.90:
            base = "✅ This looks safe. Proceed with confidence."
        elif safety_score >= 0.70:
            base = "⚠️  Moderate caution advised."
        elif safety_score >= 0.40:
            base = "🔴 High caution - consider human review."
        else:
            base = "🛑 Not recommended in current state."

        # Add success rate insight
        if success_rate > 0.8:
            base += f" (Similar tasks succeeded {success_rate:.0%} of the time)"
        elif success_rate < 0.3:
            base += f" (⚠️ Similar tasks failed {1 - success_rate:.0%} of the time)"

        # Add approval status
        if not user_approval:
            base += " Waiting for human approval."

        return base

    def _suggest_action(self, task_type: str, safety_score: float, user_approval: bool) -> str:
        """Suggest the next action."""
        if safety_score >= 0.90 and user_approval:
            return "EXECUTE_NOW"
        elif safety_score >= 0.70 and user_approval:
            return "EXECUTE_WITH_MONITORING"
        elif safety_score >= 0.40:
            return "REQUEST_APPROVAL"
        else:
            return "BLOCK_AND_REVIEW"


__all__ = ["ManasOracle", "AnalysisResult"]
