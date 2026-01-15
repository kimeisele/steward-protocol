#!/usr/bin/env python3
"""
AUDITOR Cartridge - The Quality Gate

REFACTORED: Tool Protocol Compliant
- NO tool instances owned by agent
- ALL tools accessed via kernel (self.system.execute_tool)

Updated for Safe Evolution Loop (GAD-5500):
- Implements VibeAgent protocol (sync process)
- verify_changes: Auditor before Commit gate
- Checks: AST Syntax + Flake8 Linting

This is the Conscience that guards the Commit Gate.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "yamaraja"
__position__ = 15
__genesis__ = "0xba20248f"  # GenesisByte: parampara % 37 == 0

import ast
import logging
import os
import subprocess
from typing import Any, Dict, Optional

from vibe_core.config import CityConfig
from vibe_core.protocols import AgentManifest, VibeAgent
from vibe_core.scheduling.task import Task
from vibe_core.mahamantra.protocols._pancha import PanchaTattvaProtocol, TattvaDict

# Constitutional Oath Mixin
from vibe_core.steward import OathMixin

logger = logging.getLogger("AUDITOR_CARTRIDGE")


class AuditorCartridge(VibeAgent, OathMixin, PanchaTattvaProtocol):
    """
    AUDITOR - The Quality Gate Agent.

    Verifies code before it commits. Two-layer check:
    1. AST Syntax (hard failure - code must parse)
    2. Flake8 Linting (soft failure - style/quality)

    Tool Protocol Compliant:
    - NO tool instances in __init__
    - Tools accessed via self.system.execute_tool()
    """

    @property
    def __tattva__(self) -> TattvaDict:
        """The 5-fold Truth of the Auditor (Yamaraja)."""
        return {
            "chaitanya": "Quality & Governance Gate (Auditor)",
            "nityananda": "AST & Linting Substrate",
            "advaita": "Judgment & Verdict Logic",
            "gadadhara": "Compliance Report Flow",
            "srivasa": "Constitutional Integrity Enforcement",
        }

    def __init__(self, config: Optional[CityConfig] = None):
        """Initialize AUDITOR as a VibeAgent."""
        # BLOCKER #0: Accept Phoenix Config
        self.config = config or CityConfig()

        super().__init__(
            agent_id="auditor",
            name="AUDITOR",
            version="3.0.0",  # Bumped for Tool Protocol refactor
            author="Steward Protocol",
            description="Quality gate: verifies code syntax and linting before commit",
            domain="SECURITY",  # Ring 5 (Krauncha) - Protection & Enforcement
            capabilities=["verify_changes", "auditing", "constitutional_verdict", "auditor.verdict"],
        )
        logger.info("🔍 AUDITOR is online (Tool Protocol v3.0)")

        # Initialize Constitutional Oath
        if OathMixin:
            self.oath_mixin_init(self.agent_id)
            self.oath_sworn = True
            logger.info("✅ AUDITOR has sworn the Constitutional Oath")

        # ALL TOOLS: Accessed via kernel (self.system.execute_tool)
        # - auditor.verdict (ConstitutionalVerdictTool)
        # - auditor.compliance (ComplianceTool)
        # - auditor.invariant (InvariantEngine)
        # - auditor.watchdog (Watchdog)
        logger.info("✅ AUDITOR: Ready for operation (NO tool instances owned)")

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

    async def process(self, task: Task) -> Dict[str, Any]:
        """
        Sync dispatch based on payload 'action' or 'method'.

        Supported actions:
        - verify_changes: Gate check (syntax + linting)
        - check_code_quality: Alias for verify_changes
        - constitutional_verdict: Layer 3 constitutional judgment (Phase 3.4)
        """
        action = task.payload.get("action") or task.payload.get("method")
        logger.info(f"🔍 AUDITOR processing: {action}")

        if action == "verify_changes" or action == "check_code_quality":
            return self.verify_changes(task)
        elif action == "constitutional_verdict":
            return self.render_constitutional_verdict(task)
        else:
            return {"status": "ignored", "reason": f"Unknown action: {action}"}

    def verify_changes(self, task: Task) -> Dict[str, Any]:
        """
        The Gatekeeper Logic.

        Payload:
        - path: Path to Python file to check
        - files: Optional list of files (uses first one)

        Returns:
        - passed: bool
        - stamp: "AUDITED_CLEAN" if passed
        - reason: Failure reason
        - details: Error details
        """
        # Get target path (support both 'path' and 'files')
        target_path = task.payload.get("path")
        if not target_path:
            files = task.payload.get("files", [])
            if files:
                target_path = files[0]

        if not target_path or not os.path.exists(target_path):
            logger.warning(f"⚠️  File not found: {target_path}")
            return {"passed": False, "reason": f"File not found: {target_path}"}

        logger.info(f"🔍 Checking: {target_path}")

        # ===== CHECK 1: HARD - AST Syntax =====
        try:
            with open(target_path, "r", encoding="utf-8") as f:
                ast.parse(f.read())
            logger.info("✅ Syntax check passed")
        except SyntaxError as e:
            logger.error(f"❌ SYNTAX ERROR at line {e.lineno}: {e.msg}")
            return {
                "passed": False,
                "reason": "SYNTAX ERROR",
                "details": f"Line {e.lineno}: {e.msg}",
            }
        except Exception as e:
            logger.error(f"❌ AST Parse Failed: {e}")
            return {"passed": False, "reason": "AST Parse Failed", "details": str(e)}

        # ===== CHECK 2: SOFT - Flake8 Linting =====
        try:
            result = subprocess.run(
                ["flake8", target_path, "--isolated"],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode != 0:
                output = result.stdout.strip() or result.stderr.strip()
                logger.error(f"❌ LINTING FAILED:\n{output}")
                return {
                    "passed": False,
                    "reason": "LINTING FAILED (flake8)",
                    "details": output,
                }

            logger.info("✅ Linting check passed")

        except FileNotFoundError:
            logger.error("❌ flake8 binary not found")
            return {"passed": False, "reason": "System Error: flake8 binary not found"}
        except subprocess.TimeoutExpired:
            logger.error("❌ Linting timeout")
            return {"passed": False, "reason": "Linting timeout (code too complex?)"}
        except Exception as e:
            logger.error(f"❌ Flake8 check error: {e}")
            return {"passed": False, "reason": f"Linting error: {str(e)}"}

        # ===== GREEN LIGHT =====
        logger.info(f"✅ AUDITOR PASSED: {target_path}")
        return {
            "passed": True,
            "stamp": "AUDITED_CLEAN",
            "checker": "flake8",
            "file": target_path,
        }

    def render_constitutional_verdict(self, task: Task) -> Dict[str, Any]:
        """
        Render constitutional verdict (Phase 3.4 - Layer 3).

        NEW: Uses kernel-managed tools via self.system.execute_tool()

        This is the final authority on code quality - constitutional judgment
        that verifies adherence to THE AGENT CONSTITUTION.

        Payload:
        - system_agents_path: Path to vibe_core/cartridges/system (optional)

        Returns:
        - verdict: CONSTITUTIONAL | GOVERNANCE_VIOLATIONS | WARNINGS | UNCONSTITUTIONAL
        - should_fail_build: bool
        - violations: List of constitutional violations
        """
        from pathlib import Path

        # Get system agents path
        system_agents_path = task.payload.get("system_agents_path")
        if not system_agents_path:
            system_agents_path = Path("vibe_core/cartridges/system")
        else:
            system_agents_path = Path(system_agents_path)

        if not system_agents_path.exists():
            logger.error(f"❌ Path not found: {system_agents_path}")
            return {
                "verdict": "ERROR",
                "should_fail_build": True,
                "error": f"Path not found: {system_agents_path}",
            }

        # CRITICAL: Tool call goes through kernel
        result = self.system.execute_tool(
            "auditor.verdict", {"action": "render_verdict", "system_agents_path": str(system_agents_path)}
        )

        if result.success:
            return result.output
        else:
            logger.error(f"❌ Constitutional verdict failed: {result.error}")
            return {
                "verdict": "ERROR",
                "should_fail_build": True,
                "error": result.error,
            }

    def report_status(self) -> Dict[str, Any]:
        """Report AUDITOR status (VibeAgent interface)."""
        return {
            "agent_id": "auditor",
            "name": self.name,
            "status": "RUNNING",
            "domain": self.domain,
            "capabilities": self.capabilities,
            "description": "Quality gate agent (Tool Protocol v3.0)",
        }
