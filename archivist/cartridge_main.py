#!/usr/bin/env python3
"""
ARCHIVIST Cartridge - The History Keeper

Updated for Safe Evolution Loop (GAD-5500):
- Implements VibeAgent protocol (sync process)
- seal_history: Commit verified code to git
- Only commits if audit_result.passed == true

This is the Hand that writes to Git. The Auditor is the Conscience.
"""

import os
import shutil
import subprocess
import logging
from typing import Dict, Any

from vibe_core.agent_protocol import VibeAgent, AgentManifest
from vibe_core.scheduling.task import Task

# Constitutional Oath
try:
    from steward.oath_mixin import OathMixin
except ImportError:
    OathMixin = None

logger = logging.getLogger("ARCHIVIST_CARTRIDGE")


class ArchivistCartridge(VibeAgent, OathMixin if OathMixin else object):
    """
    ARCHIVIST - The History Keeper Agent.

    Seals verified code into the repository history via git commit.
    Acts as the "Chronicle" role in the Safe Evolution Loop.

    CRITICAL: Only commits if audit_result.passed == true
    """

    def __init__(self):
        """Initialize ARCHIVIST as a VibeAgent."""
        super().__init__(
            agent_id="archivist",
            name="ARCHIVIST",
            version="2.0.0",
            author="Steward Protocol",
            description="History keeper: seals verified code into git history",
            domain="INFRASTRUCTURE",
            capabilities=["seal_history", "ledger"]
        )
        logger.info("📜 ARCHIVIST is online (History Keeper Ready)")

        # Initialize Constitutional Oath
        if OathMixin:
            self.oath_mixin_init(self.agent_id)
            self.oath_sworn = True
            logger.info("✅ ARCHIVIST has sworn the Constitutional Oath")

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
            dependencies=[]
        )

    def process(self, task: Task) -> Dict[str, Any]:
        """
        Sync dispatch based on payload 'action' or 'method'.

        Supported actions:
        - seal_history: Commit verified code
        """
        action = task.payload.get("action") or task.payload.get("method")
        logger.info(f"📜 ARCHIVIST processing: {action}")

        if action == "seal_history":
            return self.seal_history(task)
        else:
            return {"status": "ignored", "reason": f"Unknown action: {action}"}

    def seal_history(self, task: Task) -> Dict[str, Any]:
        """
        Seal code into git history (Commit).

        GATEKEEPER: Only commits if audit_result.passed == true

        Payload:
        - source_path: Path to file in sandbox
        - dest_path: Target path in repo (relative)
        - audit_result: Dict with 'passed' field (REQUIRED)
        - message: Commit message (optional)

        Returns:
        - status: "sealed" | "rejected" | "error"
        - commit: Commit hash (if sealed)
        """
        source_path = task.payload.get("source_path")
        dest_rel_path = task.payload.get("dest_path")
        audit_result = task.payload.get("audit_result", {})
        message = task.payload.get("message", "Update via Steward Protocol")

        logger.info(f"📜 Sealing history: {dest_rel_path}")

        # ===== GATEKEEPER CHECK =====
        if not audit_result.get("passed"):
            reason = audit_result.get("reason", "Unknown reason")
            logger.critical(f"⛔ GATEKEEPER VIOLATION: Audit failed. {reason}")
            return {
                "status": "rejected",
                "reason": f"Audit failed. History cannot be sealed. {reason}"
            }

        if not source_path or not os.path.exists(source_path):
            logger.error(f"❌ Source file not found: {source_path}")
            return {"status": "error", "reason": "Source file vanished."}

        # ===== MOVE TO PRODUCTION =====
        logger.info(f"📜 Moving from sandbox to production...")
        real_dest_path = os.path.abspath(dest_rel_path)

        # Security: Prevent path traversal
        try:
            cwd = os.getcwd()
            real_dest_path_normalized = os.path.normpath(os.path.abspath(real_dest_path))
            cwd_normalized = os.path.normpath(cwd)

            if not real_dest_path_normalized.startswith(cwd_normalized):
                logger.error(f"⛔ Path traversal detected: {real_dest_path}")
                return {"status": "error", "reason": "Path traversal detected."}
        except Exception as e:
            logger.error(f"❌ Path validation error: {e}")
            return {"status": "error", "reason": f"Path validation failed: {str(e)}"}

        # Create destination directory
        os.makedirs(os.path.dirname(real_dest_path), exist_ok=True)

        # Copy file from sandbox to production
        try:
            shutil.copy2(source_path, real_dest_path)
            logger.info(f"✅ File copied: {real_dest_path}")
        except Exception as e:
            logger.error(f"❌ File copy failed: {e}")
            return {"status": "error", "reason": f"File copy failed: {str(e)}"}

        # ===== GIT COMMIT =====
        logger.info(f"📜 Creating git commit...")
        try:
            # Stage the file
            subprocess.run(
                ["git", "add", dest_rel_path],
                check=True,
                cwd=cwd
            )
            logger.info(f"✅ File staged: {dest_rel_path}")

            # Commit with message
            # Optional: Add -S flag for signing if key available
            commit_msg = f"feat: {message}"
            try:
                # Try to sign (may fail if no signing key configured)
                subprocess.run(
                    ["git", "commit", "-S", "-m", commit_msg],
                    check=True,
                    cwd=cwd
                )
                signed = True
            except subprocess.CalledProcessError:
                # Fall back to unsigned commit
                logger.warning("⚠️  Signing failed, creating unsigned commit")
                subprocess.run(
                    ["git", "commit", "-m", commit_msg],
                    check=True,
                    cwd=cwd
                )
                signed = False

            logger.info(f"✅ Commit created")

            # Get commit hash
            rev = subprocess.check_output(
                ["git", "rev-parse", "HEAD"],
                cwd=cwd
            ).decode().strip()

            logger.info(f"✅ SEALED: Commit {rev[:7]}")

            return {
                "status": "sealed",
                "commit": rev,
                "commit_short": rev[:7],
                "file": dest_rel_path,
                "signed": signed,
                "message": commit_msg
            }

        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Git command failed: {e}")
            return {
                "status": "git_error",
                "details": str(e)
            }
        except Exception as e:
            logger.error(f"❌ Commit error: {e}")
            return {
                "status": "error",
                "reason": str(e)
            }

    def report_status(self) -> Dict[str, Any]:
        """Report ARCHIVIST status (VibeAgent interface)."""
        return {
            "agent_id": "archivist",
            "name": self.name,
            "status": "RUNNING",
            "domain": self.domain,
            "capabilities": self.capabilities,
            "description": self.description
        }
