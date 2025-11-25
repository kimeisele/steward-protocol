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
from pathlib import Path
from civic.tools.economy import CivicBank

logger = logging.getLogger("WATCHMAN")


class WatchmanCartridge:
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
        ]
    }

    def __init__(self):
        """Initialize Watchman with enforcement authority."""
        logger.info("⚔️ WATCHMAN BOOTING...")
        self.bank = CivicBank()
        logger.info("✅ Connected to CIVIC Central Bank (Enforcement Authority)")

    def run_patrol(self) -> dict:
        """Execute full system integrity check."""
        logger.info("\n" + "=" * 70)
        logger.info("⚔️ WATCHMAN PATROL INITIATED")
        logger.info("=" * 70)

        violations = self._scan_federation()

        report = {
            "status": "clean" if not violations else "VIOLATIONS_DETECTED",
            "violations_found": len(violations),
            "agents_frozen": [],
            "details": violations
        }

        # ENFORCEMENT PHASE
        if violations:
            logger.warning(f"\n🚨 FOUND {len(violations)} VIOLATIONS")
            frozen_agents = set()

            for v in violations:
                agent_id = v["agent_id"]
                reason = v["reason"]

                if agent_id not in frozen_agents and agent_id not in ["system", "civic"]:
                    if not self.bank.is_frozen(agent_id):
                        logger.critical(f"❄️ FREEZING: {agent_id.upper()}")
                        self.bank.freeze_account(agent_id, reason)
                        frozen_agents.add(agent_id)
                        report["agents_frozen"].append(agent_id)
                    else:
                        logger.info(f"ℹ️ {agent_id.upper()} already frozen")

        else:
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

                if "self.mode" in line and i > 20:  # Skip imports
                    violations.append({
                        "agent_id": agent_name,
                        "file": str(file_path),
                        "line": i,
                        "pattern": "uninitialized_attr",
                        "code": line.strip(),
                        "reason": f"Potential uninitialized attribute: self.mode in {agent_name}"
                    })

        except Exception as e:
            logger.warning(f"⚠️ Error scanning {file_path}: {e}")

        return violations
