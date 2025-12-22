"""
Audit Handler - Architecture audit and wiring inspection.

OPUS-171 Phase 5: Extracted from IntentRouter.

Handles:
- audit_architecture, architecture_audit, check_drift (DHARMA)
- audit_wiring, find_blind_spots (WiringMap)
- plan_strategy, review_todos (SANKALPA)
"""

import logging
from typing import TYPE_CHECKING, Any, Dict

from .base import AgentType, BaseHandler, register_handler

if TYPE_CHECKING:
    from vibe_core.plugins.opus_assistant.manas.intent_generator import Intent

logger = logging.getLogger("MANAS.Handler.Audit")


@register_handler
class DharmaHandler(BaseHandler):
    """
    Handle architecture audit intents.

    Routes to DHARMA for compliance checking.
    """

    name = "dharma"
    intent_types = [
        "audit_architecture",
        "architecture_audit",
        "check_drift",
    ]
    agent_type = AgentType.AUDIT
    priority = 15

    def handle(self, intent: "Intent") -> Dict[str, Any]:
        """Route to DHARMA for architecture audit."""
        from vibe_core.plugins.opus_assistant.manas.cortex.dharma import DharmaAuditor

        logger.info(f"⚖️ DHARMA handling: {intent.title}")

        try:
            auditor = DharmaAuditor(workspace=self._workspace)
            report = auditor.audit()

            return {
                "success": True,
                "handler": self.name,
                "violations_found": len(report.violations),
                "drift_detected": report.total_violations > 0,
                "compliance_score": report.compliance_score,
                "message": (
                    f"DHARMA audit complete: {len(report.violations)} violations, "
                    f"{report.compliance_score:.1f}% compliant"
                ),
            }
        except Exception as e:
            return {"success": False, "handler": self.name, "error": str(e)}


@register_handler
class WiringHandler(BaseHandler):
    """
    Handle wiring audit and blind spot detection.

    OPUS-066: Routes to WiringMap.
    """

    name = "wiring"
    intent_types = [
        "audit_wiring",
        "find_blind_spots",
    ]
    agent_type = AgentType.AUDIT
    priority = 12

    def handle(self, intent: "Intent") -> Dict[str, Any]:
        """Route to WiringMap for blind spot detection."""
        from vibe_core.plugins.opus_assistant.manas.cortex.wiring_map import WiringMap

        logger.info(f"🔌 WiringMap handling: {intent.title}")

        try:
            wmap = WiringMap(workspace=self._workspace)
            report = wmap.audit()

            return {
                "success": True,
                "handler": self.name,
                "total_nodes": report.total_nodes,
                "connected": report.connected_nodes,
                "disconnected": report.disconnected_nodes,
                "health_score": f"{report.health_score:.1f}%",
                "blind_spots": report.blind_spots[:10],
                "message": (f"Wiring audit: {report.health_score:.1f}% healthy, {len(report.blind_spots)} blind spots"),
            }
        except Exception as e:
            return {"success": False, "handler": self.name, "error": str(e)}


@register_handler
class SankalpaHandler(BaseHandler):
    """
    Handle strategy planning intents.

    OPUS-089: Routes to SANKALPA.
    """

    name = "sankalpa"
    intent_types = [
        "plan_strategy",
        "review_todos",
    ]
    agent_type = AgentType.STRATEGY
    priority = 10

    def handle(self, intent: "Intent") -> Dict[str, Any]:
        """Route to SANKALPA for strategy planning."""
        from vibe_core.plugins.opus_assistant.manas.cortex.sankalpa import SankalpaOrchestrator

        logger.info(f"🎯 SANKALPA handling: {intent.title}")

        try:
            orchestrator = SankalpaOrchestrator(workspace=self._workspace)

            return {
                "success": True,
                "handler": self.name,
                "action": "strategy_acknowledged",
                "message": f"SANKALPA acknowledged: {intent.title}",
            }
        except Exception as e:
            return {"success": False, "handler": self.name, "error": str(e)}
