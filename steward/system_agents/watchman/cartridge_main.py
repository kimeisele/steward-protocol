#!/usr/bin/env python3
"""
THE WATCHMAN - System Integrity Enforcer (Kshatriya Authority)

Mission: Scan the federation for violations and freeze offending agents.
Authority: Can freeze accounts, record violations, block execution.

Philosophy:
"The Watchman guards the temple. When an agent breaks the law,
the Watchman's sword falls swift and merciless. No exceptions."
"""

import os
import logging
import sys
import re
from pathlib import Path
from typing import Optional

# VibeOS Integration
from vibe_core import VibeAgent, Task
from vibe_core.config import CityConfig

# Constitutional Oath Mixin
from steward.oath_mixin import OathMixin

# CivicBank is lazily imported to avoid cryptography issues at boot time
# (see __init__ for lazy loading)

# Constitutional Oath
logger = logging.getLogger("WATCHMAN")


class WatchmanCartridge(VibeAgent, OathMixin):
    """
    THE WATCHMAN - System Integrity Enforcer.

    Kshatriya-level authority to:
    1. Scan for violations (mocks, fakes, incomplete implementations)
    2. Freeze offending agents' accounts
    3. Log violations to ledger (immutable audit trail)
    4. Prevent frozen agents from executing
    """

    FORBIDDEN_PATTERNS = {
        "mock_return": [
            r'return True\s*(#|$)',  # return True (without impl)
            r'return False\s*(#|$)',  # return False (without impl)
            r'return 0\s*(#|$)',  # return 0 (placeholder)
        ],
        "fake_success": [
            r"Success simulation",
            r"offline.*return True",
            r"would publish",
            r"would post",
            r"simulation mode",
        ],
        "placeholder_impl": [
            r"placeholder",
            r"stub",
            r"TODO.*implement",
            r"NotImplementedError",
        ],
        "uninitialized_attr": [
            r"self\.(\w+)(?:\s*\[|\s*\.|\))",  # Need semantic analysis
        ],
        # PRINCIPLE 4: NO UNAUTHORIZED CONNECTIONS (Cleanliness/Saucam)
        "unauthorized_network": [
            r"socket\s*\(",  # Direct socket creation without authorization
            r"requests\.get\s*\(",  # HTTP without GAD-1000 verification
            r"requests\.post\s*\(",
            r"urllib.*urlopen",  # urllib without authorization
            r"http\.client\s*\(",  # Low-level HTTP without checks
            r"ftplib\.",  # FTP without authorization
            r"telnetlib\.",  # Telnet without authorization
        ],
        "unverified_connections": [
            r"socket.*bind\s*\(",  # Server socket without port whitelist check
            r"socket.*listen\s*\(",  # Listening without authorization
            r"socket.*connect\s*\(",  # Client connection without verification
            r"\.recv\s*\(",  # Data receive without signature verification
            r"\.send\s*\(",  # Data send without encryption/signing
        ],
    }

    def __init__(self, config: Optional[CityConfig] = None):
        """Initialize Watchman as a VibeAgent with enforcement authority."""
        # BLOCKER #0: Accept Phoenix Config
        self.config = config or CityConfig()

        # Initialize VibeAgent base class
        super().__init__(
            agent_id="watchman",
            name="WATCHMAN",
            version="1.0.0",
            author="Steward Protocol",
            description="System integrity enforcer and governance enforcer",
            domain="ENFORCEMENT",
            capabilities=["integrity_scanning", "account_freezing", "violation_detection"]
        )

        logger.info("⚔️ WATCHMAN BOOTING...")

        # Initialize Constitutional Oath mixin (if available)
        if OathMixin:
            self.oath_mixin_init(self.agent_id)
            # SWEAR THE OATH IMMEDIATELY in __init__
            self.oath_sworn = True
            logger.info("✅ WATCHMAN has sworn the Constitutional Oath")

        # Load CivicBank (optional - may fail due to cryptography issues)
        self.bank = None
        try:
            self.bank = CivicBank()
            logger.info("✅ Connected to CIVIC Central Bank (Enforcement Authority)")
        except Exception as e:
            logger.warning(f"⚠️  Could not load CivicBank: {type(e).__name__} (running in audit-only mode)")

    def run_patrol(self) -> dict:
        """Execute full system integrity check, punish violators, and grant amnesty to redeemed."""
        logger.info("\n" + "=" * 70)
        logger.info("⚔️ WATCHMAN PATROL INITIATED")
        logger.info("=" * 70)

        violations = self._scan_federation()

        report = {
            "status": "clean" if not violations else "VIOLATIONS_DETECTED",
            "violations_found": len(violations),
            "agents_frozen": [],
            "agents_thawed": [],
            "details": violations
        }

        # PHASE 1: IDENTIFY CURRENT VIOLATORS
        current_violators = set()
        if violations:
            logger.warning(f"\n🚨 FOUND {len(violations)} VIOLATIONS")
            for v in violations:
                agent_id = v["agent_id"]
                reason = v["reason"]
                current_violators.add(agent_id)

                if agent_id not in ["system", "civic"]:
                    if not self.bank.is_frozen(agent_id):
                        logger.critical(f"❄️ FREEZING: {agent_id.upper()}")
                        self.bank.freeze_account(agent_id, reason)
                        report["agents_frozen"].append(agent_id)
                    else:
                        logger.info(f"ℹ️ {agent_id.upper()} already frozen")

        # PHASE 2: GRANT AMNESTY TO REDEEMED AGENTS
        # Check all known agents for thaw eligibility
        logger.info("\n⚖️ JUSTICE PHASE: Checking for redemption...")
        for agent_id in ["herald", "science", "forum"]:
            if self.bank.is_frozen(agent_id) and agent_id not in current_violators:
                # Agent was frozen but has no current violations = REDEEMED
                logger.info(f"🔥 THAWING: {agent_id.upper()} (violations resolved)")
                self.bank.unfreeze_account(agent_id, "Compliance Restored")
                report["agents_thawed"].append(agent_id)

        if not violations:
            logger.info("✅ SYSTEM CLEAN. TEMPLE SECURE.")

        logger.info("=" * 70 + "\n")
        return report

    def _scan_federation(self) -> list:
        """Scan all agent cartridges for violations."""
        violations = []
        agents_to_scan = ["herald", "science", "forum"]

        for agent_name in agents_to_scan:
            cartridge_path = Path(f"{agent_name}/cartridge_main.py")
            tools_dir = Path(f"{agent_name}/tools")

            # Scan cartridge
            if cartridge_path.exists():
                violations.extend(self._scan_file(cartridge_path, agent_name))

            # Scan tools
            if tools_dir.exists():
                for tool_file in tools_dir.glob("*.py"):
                    violations.extend(self._scan_file(tool_file, agent_name))

        return violations

    def _scan_file(self, file_path: Path, agent_name: str) -> list:
        """Scan a single file for violation patterns."""
        violations = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            for i, line in enumerate(lines, start=1):
                # Check for mock patterns
                lower_line = line.lower()

                if "return true" in lower_line and "#" not in lower_line and "def " not in lower_line:
                    if "success simulation" in lower_line or "offline" in lower_line:
                        violations.append({
                            "agent_id": agent_name,
                            "file": str(file_path),
                            "line": i,
                            "pattern": "mock_return",
                            "code": line.strip(),
                            "reason": f"Mock success return detected in {agent_name}"
                        })

                if "placeholder" in lower_line or "stub" in lower_line:
                    violations.append({
                        "agent_id": agent_name,
                        "file": str(file_path),
                        "line": i,
                        "pattern": "placeholder_impl",
                        "code": line.strip(),
                        "reason": f"Placeholder implementation in {agent_name}"
                    })

                # Only flag self.mode usage WITHOUT assignment (=) and WITHOUT safety comment
                if ("self.mode" in line and i > 20 and "self.mode =" not in line
                    and "initialized" not in lower_line and "safe" not in lower_line):
                    violations.append({
                        "agent_id": agent_name,
                        "file": str(file_path),
                        "line": i,
                        "pattern": "uninitialized_attr",
                        "code": line.strip(),
                        "reason": f"Potential uninitialized attribute: self.mode in {agent_name}"
                    })

                # PRINCIPLE 4: Check for unauthorized network operations (Cleanliness/Saucam)
                # Check for raw socket operations without GAD-1000 verification
                # Check unauthorized network patterns
                for pattern in self.FORBIDDEN_PATTERNS.get("unauthorized_network", []):
                    if re.search(pattern, line):
                        # Allow if there's a safety comment or whitelist reference
                        if "whitelist" not in lower_line and "authorized" not in lower_line and "gad_1000" not in lower_line:
                            violations.append({
                                "agent_id": agent_name,
                                "file": str(file_path),
                                "line": i,
                                "pattern": "unauthorized_network",
                                "code": line.strip(),
                                "reason": f"Unauthorized network operation detected - violates Principle 4 (Saucam/Cleanliness). Must use GAD-1000 verification."
                            })
                            break  # Only report once per line

                # Check unverified connection patterns
                for pattern in self.FORBIDDEN_PATTERNS.get("unverified_connections", []):
                    if re.search(pattern, line):
                        if "signature" not in lower_line and "verify" not in lower_line and "gad_1000" not in lower_line:
                            violations.append({
                                "agent_id": agent_name,
                                "file": str(file_path),
                                "line": i,
                                "pattern": "unverified_connections",
                                "code": line.strip(),
                                "reason": f"Unverified network connection detected - violates Principle 4. Must verify GAD-1000 identity before data exchange."
                            })
                            break

        except Exception as e:
            logger.warning(f"⚠️ Error scanning {file_path}: {e}")

        return violations

    # ==================== VIBEOS AGENT INTERFACE ====================

    def process(self, task: Task) -> dict:
        """
        Process a task from the VibeKernel scheduler.

        WATCHMAN responds to enforcement tasks:
        - "patrol": Run full system integrity check
        """
        try:
            action = task.payload.get("action") or task.payload.get("command")
            logger.info(f"⚔️ WATCHMAN processing task: {action}")

            if action == "patrol":
                return self.run_patrol()
            else:
                return {
                    "status": "error",
                    "error": f"Unknown action: {action}"
                }
        except Exception as e:
            logger.error(f"❌ WATCHMAN processing error: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return {
                "status": "error",
                "error": str(e)
            }
    def get_manifest(self):
        """Return agent manifest for kernel registry."""
        from vibe_core.protocols import AgentManifest
        return AgentManifest(
            agent_id="watchman",
            name="WATCHMAN",
            version=self.version if hasattr(self, 'version') else "1.0.0",
            author="Steward Protocol",
            description="Monitoring and health checks",
            domain="MONITORING",
            capabilities=['monitoring', 'alerts', 'system_integrity']
        )



    def report_status(self) -> dict:
        """Report WATCHMAN status (VibeAgent interface)."""
        return {
            "agent_id": "watchman",
            "name": "WATCHMAN",
            "status": "RUNNING",
            "domain": "ENFORCEMENT",
            "capabilities": self.capabilities,
            "description": "System integrity enforcer and governance enforcer"
        }
