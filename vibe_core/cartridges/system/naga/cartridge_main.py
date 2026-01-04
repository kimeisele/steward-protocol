#!/usr/bin/env python3
"""
NAGA Cartridge - The Invisible Guardian.

"Niemand darf es merken" - they infiltrate invisibly.
"Wie Wasser in jede Ritze" - organic flooding into every crack.
"Der Wächter" - they notice when things go wrong.

NAGA Federation Cartridge for Agent City:
- Provides Agent-level access to NAGA services
- Exposes detection, scanning, and audit capabilities
- Integrates with CommitWatcher and FloodManager

This is the EXECUTIVE layer between analysis and action.
BUDDHI vor MANAS - discrimination before thinking.

Tool Protocol Compliant:
- NO tool instances owned by agent
- ALL tools accessed via kernel (self.system.execute_tool)
"""

import logging
from typing import Any, Dict, Optional

from vibe_core.config import CityConfig
from vibe_core.protocols import AgentManifest, VibeAgent
from vibe_core.scheduling.task import Task
from vibe_core.steward import OathMixin

logger = logging.getLogger("NAGA_CARTRIDGE")


class NagaCartridge(VibeAgent, OathMixin):
    """
    NAGA - The Invisible Guardian Cartridge.

    Varna: Kshatriya (Protector, not Ruler)
    Karma: Nishkama (Selfless action serving Dharma)
    Ashrama: Grihastha (Active service phase)

    Capabilities:
    - status: Federation health check
    - scan: Toxicity detection (Takshaka)
    - detect: Drift and violation detection (CommitWatcher)
    - audit: Ledger audit trail (Sesha)
    - flood: EventBus observation status (FloodManager)

    Tool Protocol Compliant:
    - NO tool instances in __init__
    - Tools accessed via self.system.execute_tool()
    """

    def __init__(self, config: Optional[CityConfig] = None):
        """Initialize NAGA as a VibeAgent."""
        self.config = config or CityConfig()

        super().__init__(
            agent_id="naga",
            name="NAGA Federation",
            version="1.0.0",
            author="Steward Protocol",
            description="The Invisible Guardian - Security, Audit, Detection",
            domain="SECURITY",  # Ring 5 (Krauncha) - Protection & Enforcement
            capabilities=[
                "status",
                "scan",
                "detect",
                "audit",
                "flood",
                "naga.status",
                "naga.scan",
                "naga.detect",
            ],
        )
        logger.info("🐍 NAGA Cartridge online (Tool Protocol v1.0)")

        # Initialize Constitutional Oath
        if OathMixin:
            self.oath_mixin_init(self.agent_id)
            self.oath_sworn = True
            logger.info("✅ NAGA has sworn the Constitutional Oath")

        # Lazy-loaded federation reference
        self._federation = None

        logger.info("✅ NAGA: Ready for operation (NO tool instances owned)")

    def get_manifest(self) -> AgentManifest:
        """Return agent manifest (VibeAgent interface)."""
        return AgentManifest(
            agent_id=self.agent_id,
            name=self.name,
            version=self.version,
            author=self.author,
            description=self.description,
            domain=self.domain,
            capabilities=self.capabilities,
            dependencies=[],
        )

    @property
    def federation(self):
        """Lazy-load NagaFederation from ServiceRegistry."""
        if self._federation is None:
            try:
                from vibe_core.di import ServiceRegistry
                from vibe_core.protocols.naga import NagaFederationProtocol

                self._federation = ServiceRegistry.get(NagaFederationProtocol)
            except Exception as e:
                logger.debug(f"NagaFederation not available: {e}")
                return None
        return self._federation

    async def process(self, task: Task) -> Dict[str, Any]:
        """
        Async dispatch based on payload 'action' or 'method'.

        Supported actions:
        - status: Get federation health status
        - scan: Scan content for toxicity
        - detect: Get drift/violation detections
        - audit: Query ledger audit trail
        - flood: Get flood manager status
        """
        action = task.payload.get("action") or task.payload.get("method")
        logger.info(f"🐍 NAGA processing: {action}")

        if action == "status":
            return self._get_status()
        elif action == "scan":
            return await self._scan_toxicity(task.payload)
        elif action == "detect":
            return self._get_detections()
        elif action == "audit":
            return await self._query_audit(task.payload)
        elif action == "flood":
            return self._get_flood_status()
        else:
            return {"status": "ignored", "reason": f"Unknown action: {action}"}

    def _get_status(self) -> Dict[str, Any]:
        """Get NAGA Federation health status."""
        if not self.federation:
            return {
                "status": "unavailable",
                "reason": "NagaOrchestrator not registered",
                "healthy": False,
            }

        try:
            status = self.federation.get_status()
            return {
                "status": "healthy" if self.federation.is_ready() else "degraded",
                "federation": status,
                "healthy": self.federation.is_ready(),
            }
        except Exception as e:
            logger.error(f"Failed to get federation status: {e}")
            return {"status": "error", "error": str(e), "healthy": False}

    async def _scan_toxicity(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Scan content for toxicity using Takshaka."""
        content = payload.get("content", "")

        if not content:
            return {"error": "No content provided", "toxicity": 0.0, "blocked": False}

        if not self.federation or not self.federation.takshaka:
            return {
                "error": "Takshaka not available",
                "toxicity": 0.0,
                "blocked": False,
            }

        try:
            result = self.federation.takshaka.scan_toxicity(content)
            return {
                "toxicity": result.score,
                "blocked": result.blocked,
                "patterns": result.patterns if hasattr(result, "patterns") else [],
                "scanned_length": len(content),
            }
        except Exception as e:
            logger.error(f"Toxicity scan failed: {e}")
            return {"error": str(e), "toxicity": 0.0, "blocked": False}

    def _get_detections(self) -> Dict[str, Any]:
        """Get drift and violation detections from CommitWatcher."""
        if not self.federation:
            return {"error": "NagaOrchestrator not available", "detections": []}

        result = {"detections": [], "stats": {}}

        # CommitWatcher stats
        if self.federation.commit_watcher:
            stats = self.federation.commit_watcher.get_stats()
            result["commit_watcher"] = stats
            result["stats"]["panic_count"] = stats.get("panic_count", 0)
            result["stats"]["deferred_count"] = stats.get("deferred_count", 0)
            result["stats"]["alerts_generated"] = stats.get("alerts_generated", 0)

        # FloodManager observations
        if self.federation.flood_manager:
            flood_status = self.federation.flood_manager.get_status()
            result["flood_observations"] = flood_status.get("total_observations", 0)

        return result

    async def _query_audit(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Query ledger audit trail via Sesha."""
        if not self.federation or not self.federation.sesha:
            return {"error": "Sesha not available", "events": []}

        try:
            # Get recent events from Sesha's ledger access
            event_type = payload.get("event_type")
            limit = payload.get("limit", 10)

            # Use Sesha's ledger if available
            if hasattr(self.federation.sesha, "_ledger"):
                ledger = self.federation.sesha._ledger
                if event_type:
                    events = ledger.get_events_by_type(event_type, limit=limit)
                else:
                    events = ledger.get_recent_events(limit=limit)
                return {"events": [e.to_dict() for e in events], "count": len(events)}

            return {"events": [], "count": 0, "note": "Direct ledger access unavailable"}
        except Exception as e:
            logger.error(f"Audit query failed: {e}")
            return {"error": str(e), "events": []}

    def _get_flood_status(self) -> Dict[str, Any]:
        """Get FloodManager status."""
        if not self.federation or not self.federation.flood_manager:
            return {"error": "FloodManager not available", "active": False}

        try:
            status = self.federation.flood_manager.get_status()
            return {
                "active": status.get("active", False),
                "total_observations": status.get("total_observations", 0),
                "subscribers": status.get("subscriber_count", 0),
                "details": status,
            }
        except Exception as e:
            logger.error(f"Flood status failed: {e}")
            return {"error": str(e), "active": False}

    def report_status(self) -> Dict[str, Any]:
        """Report NAGA status (VibeAgent interface)."""
        federation_ready = self.federation.is_ready() if self.federation else False

        return {
            "agent_id": "naga",
            "name": self.name,
            "status": "RUNNING" if federation_ready else "DEGRADED",
            "domain": self.domain,
            "capabilities": self.capabilities,
            "federation_ready": federation_ready,
            "description": "The Invisible Guardian (Tool Protocol v1.0)",
        }


# Convenience function for standalone testing
def create_naga_cartridge(config: Optional[CityConfig] = None) -> NagaCartridge:
    """Factory function for creating NAGA cartridge."""
    return NagaCartridge(config)
