#!/usr/bin/env python3
"""
AUDITOR Cartridge - The Quality Gate

Updated for Safe Evolution Loop (GAD-5500):
- Implements VibeAgent protocol (sync process)
- verify_changes: Auditor before Commit gate
- Checks: AST Syntax + Flake8 Linting

This is the Conscience that guards the Commit Gate.
"""

import os
import ast
import subprocess
import logging
from typing import Dict, Any, Optional

from vibe_core.protocols import VibeAgent, AgentManifest
from vibe_core.config import CityConfig
from vibe_core.scheduling.task import Task

# Constitutional Oath

# Constitutional Oath Mixin
from steward.oath_mixin import OathMixin

# Phase 3.4: Constitutional Verdict Tool
from .tools.constitutional_verdict import ConstitutionalVerdictTool

logger = logging.getLogger("AUDITOR_CARTRIDGE")


class AuditorCartridge(VibeAgent, OathMixin):
    """
    AUDITOR - The Quality Gate Agent.

    Verifies code before it commits. Two-layer check:
    1. AST Syntax (hard failure - code must parse)
    2. Flake8 Linting (soft failure - style/quality)
    """

    def __init__(self, config: Optional[CityConfig] = None):
        """Initialize AUDITOR as a VibeAgent."""
        # BLOCKER #0: Accept Phoenix Config
        self.config = config or CityConfig()

        super().__init__(
            agent_id="auditor",
            name="AUDITOR",
            version="2.0.0",
            author="Steward Protocol",
            description="Quality gate: verifies code syntax and linting before commit",
            domain="SECURITY",
            capabilities=["verify_changes", "auditing", "constitutional_verdict"],
        )
        logger.info("🔍 AUDITOR is online (Quality Gate Ready)")

        # Initialize Constitutional Oath
        if OathMixin:
            self.oath_mixin_init(self.agent_id)
            self.oath_sworn = True
            logger.info("✅ AUDITOR has sworn the Constitutional Oath")

        # Phase 3.4: Initialize Constitutional Verdict Tool
        self.verdict_tool = ConstitutionalVerdictTool()
        logger.info("⚖️  Constitutional Verdict Tool initialized (Layer 3 - Supreme Authority)")

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

    def process(self, task: Task) -> Dict[str, Any]:
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
            return {"passed": False, "reason": "SYNTAX ERROR", "details": f"Line {e.lineno}: {e.msg}"}
        except Exception as e:
            logger.error(f"❌ AST Parse Failed: {e}")
            return {"passed": False, "reason": "AST Parse Failed", "details": str(e)}

        # ===== CHECK 2: SOFT - Flake8 Linting =====
        try:
            result = subprocess.run(["flake8", target_path, "--isolated"], capture_output=True, text=True, timeout=30)

            if result.returncode != 0:
                output = result.stdout.strip() or result.stderr.strip()
                logger.error(f"❌ LINTING FAILED:\n{output}")
                return {"passed": False, "reason": "LINTING FAILED (flake8)", "details": output}

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
        return {"passed": True, "stamp": "AUDITED_CLEAN", "checker": "flake8", "file": target_path}

    def render_constitutional_verdict(self, task: Task) -> Dict[str, Any]:
        """
        Render constitutional verdict (Phase 3.4 - Layer 3).

        This is the final authority on code quality - constitutional judgment
        that verifies adherence to THE AGENT CONSTITUTION.

        Payload:
        - system_agents_path: Path to steward/system_agents (optional)

        Returns:
        - verdict: CONSTITUTIONAL | GOVERNANCE_VIOLATIONS | WARNINGS | UNCONSTITUTIONAL
        - should_fail_build: bool
        - violations: List of constitutional violations
        """
        from pathlib import Path

        # Get system agents path
        system_agents_path = task.payload.get("system_agents_path")
        if not system_agents_path:
            system_agents_path = Path("steward/system_agents")
        else:
            system_agents_path = Path(system_agents_path)

        if not system_agents_path.exists():
            logger.error(f"❌ Path not found: {system_agents_path}")
            return {"verdict": "ERROR", "should_fail_build": True, "error": f"Path not found: {system_agents_path}"}

        # Render constitutional verdict
        verdict = self.verdict_tool.render_verdict(system_agents_path)

        return verdict

    def report_status(self) -> Dict[str, Any]:
        """Report AUDITOR status (VibeAgent interface)."""
        return {
            "agent_id": "auditor",
            "name": self.name,
            "status": "RUNNING",
            "domain": self.domain,
            "capabilities": self.capabilities,
            "description": self.description,
        }
