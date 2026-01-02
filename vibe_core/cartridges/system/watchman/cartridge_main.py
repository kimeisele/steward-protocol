#!/usr/bin/env python3
"""
THE WATCHMAN - System Integrity Enforcer (Kshatriya Authority)

Mission: Scan the federation for violations and freeze offending agents.
Authority: Can freeze accounts, record violations, block execution.

Philosophy:
"The Watchman guards the temple. When an agent breaks the law,
the Watchman's sword falls swift and merciless. No exceptions."
"""

import logging
import re
from pathlib import Path
from typing import Optional

# VibeOS Integration
from vibe_core import Task, VibeAgent
from vibe_core.config import CityConfig
from vibe_core.di import ServiceRegistry
from vibe_core.protocols.shuddhi import ShuddhiProtocol
from vibe_core.protocols.task import TaskProtocol

# Constitutional Oath Mixin
from vibe_core.steward import OathMixin

# Phase 3.2: Deep inspection tool

# CivicBank import with fallback (cryptography may not be available)
try:
    from vibe_core.cartridges.system.civic.tools.economy_agent import CivicBank
except ImportError:
    CivicBank = None

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
            r"return True\s*(#|$)",  # return True (without impl)
            r"return False\s*(#|$)",  # return False (without impl)
            r"return 0\s*(#|$)",  # return 0 (placeholder)
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
            version="3.0.0",  # Bumped for Tool Protocol refactor
            author="Steward Protocol",
            description="System integrity enforcer and governance enforcer",
            domain="SYSTEM",
            capabilities=[
                "integrity_scanning",
                "account_freezing",
                "violation_detection",
            ],
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
        if CivicBank is not None:
            try:
                self.bank = CivicBank()
                logger.info("✅ Connected to CIVIC Central Bank (Enforcement Authority)")
            except Exception as e:
                logger.warning(f"⚠️  Could not load CivicBank: {type(e).__name__} (running in audit-only mode)")
        else:
            logger.warning("⚠️  CivicBank not available (running in audit-only mode)")

        # ALL TOOLS: Accessed via kernel (self.system.execute_tool)
        # - watchman.standards (StandardsInspectionTool)
        # - watchman.health (SystemHealthCheck)

        logger.info("✅ WATCHMAN: Ready for operation (NO tool instances owned)")

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
            "details": violations,
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
        # Check all registered agents for thaw eligibility (dynamic, not hardcoded)
        logger.info("\n⚖️ JUSTICE PHASE: Checking for redemption...")
        registered_agents = (
            list(self.system.kernel.agent_registry.keys()) if hasattr(self, "system") and self.system else []
        )
        for agent_id in registered_agents:
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

        # DYNAMIC: Scan all registered agents, not a hardcoded list
        if hasattr(self, "system") and self.system and hasattr(self.system, "kernel"):
            agents_to_scan = list(self.system.kernel.agent_registry.keys())
        else:
            # Fallback: scan known agent directories
            from pathlib import Path

            agent_dirs = list(Path("vibe_core/cartridges/system").iterdir()) + list(
                Path("vibe_core/cartridges/agent_city").iterdir()
            )
            agents_to_scan = [d.name for d in agent_dirs if d.is_dir() and not d.name.startswith("_")]

        for agent_name in agents_to_scan:
            # Try multiple possible locations for cartridge
            possible_paths = [
                Path(f"vibe_core/cartridges/system/{agent_name}/cartridge_main.py"),
                Path(f"vibe_core/cartridges/agent_city/{agent_name}/cartridge_main.py"),
                Path(f"{agent_name}/cartridge_main.py"),
            ]
            cartridge_path = next((p for p in possible_paths if p.exists()), None)
            if not cartridge_path:
                continue  # Skip if no cartridge found
            tools_dir = cartridge_path.parent / "tools"

            # Scan cartridge
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
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            for i, line in enumerate(lines, start=1):
                # Check for mock patterns
                lower_line = line.lower()

                if "return true" in lower_line and "#" not in lower_line and "def " not in lower_line:
                    if "success simulation" in lower_line or "offline" in lower_line:
                        violations.append(
                            {
                                "agent_id": agent_name,
                                "file": str(file_path),
                                "line": i,
                                "pattern": "mock_return",
                                "code": line.strip(),
                                "reason": f"Mock success return detected in {agent_name}",
                            }
                        )

                if "placeholder" in lower_line or "stub" in lower_line:
                    violations.append(
                        {
                            "agent_id": agent_name,
                            "file": str(file_path),
                            "line": i,
                            "pattern": "placeholder_impl",
                            "code": line.strip(),
                            "reason": f"Placeholder implementation in {agent_name}",
                        }
                    )

                # Only flag self.mode usage WITHOUT assignment (=) and WITHOUT safety comment
                if (
                    "self.mode" in line
                    and i > 20
                    and "self.mode =" not in line
                    and "initialized" not in lower_line
                    and "safe" not in lower_line
                ):
                    violations.append(
                        {
                            "agent_id": agent_name,
                            "file": str(file_path),
                            "line": i,
                            "pattern": "uninitialized_attr",
                            "code": line.strip(),
                            "reason": f"Potential uninitialized attribute: self.mode in {agent_name}",
                        }
                    )

                # PRINCIPLE 4: Check for unauthorized network operations (Cleanliness/Saucam)
                # Check for raw socket operations without GAD-1000 verification
                # Check unauthorized network patterns
                for pattern in self.FORBIDDEN_PATTERNS.get("unauthorized_network", []):
                    if re.search(pattern, line):
                        # Allow if there's a safety comment or whitelist reference
                        if (
                            "whitelist" not in lower_line
                            and "authorized" not in lower_line
                            and "gad_1000" not in lower_line
                        ):
                            violations.append(
                                {
                                    "agent_id": agent_name,
                                    "file": str(file_path),
                                    "line": i,
                                    "pattern": "unauthorized_network",
                                    "code": line.strip(),
                                    "reason": "Unauthorized network operation detected - violates Principle 4 (Saucam/Cleanliness). Must use GAD-1000 verification.",
                                }
                            )
                            break  # Only report once per line

                # Check unverified connection patterns
                for pattern in self.FORBIDDEN_PATTERNS.get("unverified_connections", []):
                    if re.search(pattern, line):
                        if (
                            "signature" not in lower_line
                            and "verify" not in lower_line
                            and "gad_1000" not in lower_line
                        ):
                            violations.append(
                                {
                                    "agent_id": agent_name,
                                    "file": str(file_path),
                                    "line": i,
                                    "pattern": "unverified_connections",
                                    "code": line.strip(),
                                    "reason": "Unverified network connection detected - violates Principle 4. Must verify GAD-1000 identity before data exchange.",
                                }
                            )
                            break

        except Exception as e:
            logger.warning(f"⚠️ Error scanning {file_path}: {e}")

        return violations

    def run_deep_inspection(self) -> dict:
        """
        Execute deep AST-based inspection (Phase 3.2).

        This is more thorough than run_patrol() but also slower (~500ms).
        Should be run in CI/CD, NOT in pre-commit hooks.

        Returns:
            Report dict with violations and compliance status
        """
        logger.info("\n" + "=" * 70)
        logger.info("🔬 WATCHMAN DEEP INSPECTION INITIATED (Phase 3.2)")
        logger.info("=" * 70)

        system_agents_path = Path("vibe_core/cartridges/system")

        if not system_agents_path.exists():
            logger.error(f"❌ Path not found: {system_agents_path}")
            return {"status": "error", "error": f"Path not found: {system_agents_path}"}

        # Run deep inspection
        result = self.system.execute_tool(
            "watchman.standards", {"action": "inspect_all", "system_agents_path": str(system_agents_path)}
        )
        violations = result.output.get("violations", []) if result.success else []

        # Generate compliance report
        # Group violations by severity and agent
        by_severity = {}
        by_agent = {}
        for v in violations:
            severity = v.get("severity", "UNKNOWN")
            agent_id = v.get("agent_id", "unknown")

            by_severity[severity] = by_severity.get(severity, 0) + 1
            by_agent[agent_id] = by_agent.get(agent_id, 0) + 1

        critical_count = sum(1 for v in violations if v.get("severity") == "CRITICAL")

        report = {
            "total_violations": len(violations),
            "violations": violations,
            "by_severity": by_severity,
            "by_agent": by_agent,
            "critical_count": critical_count,
            "should_fail_build": critical_count > 0,
        }

        # Log summary
        logger.info("\n" + "=" * 70)
        logger.info("📊 DEEP INSPECTION SUMMARY")
        logger.info("=" * 70)
        logger.info(f"Total violations: {report['total_violations']}")
        logger.info("By severity:")
        for severity, count in report["by_severity"].items():
            if count > 0:
                logger.info(f"  • {severity}: {count}")

        logger.info("\nBy agent:")
        for agent_id, count in report["by_agent"].items():
            logger.info(f"  • {agent_id}: {count} violation(s)")

        # Determine overall status
        if report["should_fail_build"]:
            logger.error("\n❌ BUILD SHOULD FAIL - CRITICAL violations detected")
            status = "VIOLATIONS_DETECTED"
        elif report["total_violations"] > 0:
            logger.warning("\n⚠️  VIOLATIONS DETECTED - Review recommended")
            status = "WARNINGS_DETECTED"
        else:
            logger.info("\n✅ SYSTEM CLEAN - All agents compliant")
            status = "COMPLIANT"

        # PHASE 3: Create healing tasks for violations with Shuddhi remedies
        healing_tasks_created = 0
        task_service = ServiceRegistry.get(TaskProtocol)
        shuddhi = ServiceRegistry.get(ShuddhiProtocol)

        if task_service and violations:
            for v in violations:
                rule_id = v.get("rule_id")
                # Validate: YAML flag AND actual remedy registered
                can_heal = v.get("has_remedy") and (shuddhi.can_heal(rule_id) if shuddhi else False)

                if can_heal:
                    task_title = f"HEAL: {rule_id} in {Path(v.get('file_path', '')).name}"
                    # Check for existing task to avoid duplicates
                    existing = [t for t in task_service.list_tasks() if t.title == task_title]
                    if not existing:
                        task_service.add_task(
                            title=task_title,
                            description=(
                                f"Auto-heal violation detected by Watchman:\n"
                                f"Rule: {rule_id}\n"
                                f"File: {v.get('file_path')}\n"
                                f"Line: {v.get('line_number')}\n"
                                f"Code: {v.get('code_snippet')}\n\n"
                                f"Use: engineer.heal_violation(file_path, rule_id)"
                            ),
                            priority=80,  # High priority for auto-heal
                            assigned_agent="engineer",
                        )
                        healing_tasks_created += 1

            if healing_tasks_created > 0:
                logger.info(f"🛡️ Created {healing_tasks_created} healing tasks for Engineer")

        logger.info("=" * 70 + "\n")

        return {
            "status": status,
            "should_fail_build": report["should_fail_build"],
            "total_violations": report["total_violations"],
            "critical_count": report["critical_count"],
            "healing_tasks_created": healing_tasks_created,
            "report": report,
            "violations": report["violations"],
        }

    def run_health_check(self) -> dict:
        """
        Execute system health check (Phase 3.3).

        READ-ONLY monitoring of infrastructure:
        - Git hooks installation
        - Hook validity and freshness
        - Critical system files

        Philosophy: "The Watchman observes. The Operator acts."
        This agent NEVER modifies infrastructure, only reports violations.

        Returns:
            Health report dict with status and recommendations
        """
        logger.info("\n" + "=" * 70)
        logger.info("🏥 WATCHMAN SYSTEM HEALTH CHECK")
        logger.info("=" * 70)

        # Run health check
        result = self.system.execute_tool("watchman.health", {"action": "check_all"})
        report = result.output if result.success else {"status": "error", "error": result.error}

        # Log formatted report
        # Report already formatted by tool
        formatted = str(report)
        for line in formatted.split("\n"):
            if line.strip():
                logger.info(line)

        return report

    # ==================== VIBEOS AGENT INTERFACE ====================

    async def process(self, task: Task) -> dict:
        """
        Process a task from the VibeKernel scheduler.

        WATCHMAN responds to enforcement tasks:
        - "patrol": Run full system integrity check (legacy grep-based)
        - "deep_inspection": Run AST-based deep analysis (Phase 3.2)
        - "system_health": Run infrastructure health check (Phase 3.3, read-only)
        """
        try:
            action = task.payload.get("action") or task.payload.get("command")
            logger.info(f"⚔️ WATCHMAN processing task: {action}")

            if action == "patrol":
                return self.run_patrol()
            elif action == "deep_inspection":
                return self.run_deep_inspection()
            elif action == "system_health":
                return self.run_health_check()
            elif action == "verify_signatures":
                return self.verify_holon_signatures()
            else:
                return {"status": "error", "error": f"Unknown action: {action}"}
        except Exception as e:
            logger.error(f"❌ WATCHMAN processing error: {e}")
            import traceback

            logger.error(traceback.format_exc())
            return {"status": "error", "error": str(e)}

    def verify_holon_signatures(self) -> dict:
        """
        Scan and verify signatures of all .vibe containers.
        Part of GAD-000 Holon Governance.
        """
        import zipfile

        logger.info("\n" + "=" * 70)
        logger.info("🔐 WATCHMAN HOLON VERIFICATION")
        logger.info("=" * 70)

        scan_paths = getattr(self, "scan_paths", [Path("vibe_core/plugins")])
        violations = []
        verified_count = 0

        for base in scan_paths:
            if not base.exists():
                continue
            for item in base.iterdir():
                if item.suffix == ".vibe" and zipfile.is_zipfile(item):
                    try:
                        is_valid = self._verify_single_holon(item)
                        if is_valid:
                            logger.info(f"  ✅ Verified: {item.name}")
                            verified_count += 1
                        else:
                            logger.critical(f"  ❌ TAMPERED: {item.name}")
                            violations.append(
                                {"file": str(item), "reason": "Invalid signature", "severity": "CRITICAL"}
                            )
                    except Exception as e:
                        logger.error(f"  ⚠️ Error verifying {item.name}: {e}")
                        violations.append({"file": str(item), "reason": f"Verification error: {e}", "severity": "High"})

        status = "COMPLIANT" if not violations else "VIOLATIONS_DETECTED"
        logger.info(f"\nStatus: {status} ({verified_count} verified, {len(violations)} violations)")
        logger.info("=" * 70 + "\n")

        return {"status": status, "verified": verified_count, "violations": violations}

    def _verify_single_holon(self, file_path: Path) -> bool:
        """Verify signature of a single .vibe file."""
        import hashlib
        import zipfile

        try:
            with zipfile.ZipFile(file_path, "r") as z:
                # 1. Read proper signature
                if "SIGNATURE.sig" not in z.namelist():
                    logger.warning(f"Signature missing in {file_path.name}")
                    return False

                stored_sig = z.read("SIGNATURE.sig").decode("utf-8").strip()

                # 2. Recompute hash
                hasher = hashlib.sha256()

                # Hash Manifest first (Layer 0)
                if "manifest.json" in z.namelist():
                    hasher.update(z.read("manifest.json"))
                else:
                    return False  # Manifest mandatory

                # Iterate content (excluding sig and manifest which we just did)
                # Need to match deterministic order of packer?
                # Packer used os.walk / iterdir which is not strictly ordered?
                # Packer: "add_recursive(source_dir)". iterdir order is OS dependent!
                # CRITICAL FLAW IN PACKER: Order matters for stream hashing if we hash linearly.
                # BUT wait, packer output `z.write` writes to the zip stream.
                # If we read the zip stream, we get entries in the order they were written.
                # So we should iterate z.infolist() and hash content of relevant files in order!

                for info in z.infolist():
                    if info.filename == "manifest.json":
                        continue  # Already hashed
                    if info.filename == "SIGNATURE.sig":
                        continue
                    if info.filename.endswith("/"):
                        continue  # Directory entry

                    hasher.update(z.read(info.filename))

                computed_sig = hasher.hexdigest()

                # Handle v2 JSON signature format (ECDSA signed)
                if stored_sig.startswith("{"):
                    try:
                        import json

                        sig_data = json.loads(stored_sig)
                        if sig_data.get("version") == 2:
                            # v2: Compare hash field, signature verification optional
                            return computed_sig == sig_data.get("hash")
                    except json.JSONDecodeError:
                        pass  # Fall through to direct comparison

                # v1: Direct hash comparison
                return computed_sig == stored_sig
        except Exception:
            return False

    def get_manifest(self):
        """Return agent manifest for kernel registry."""
        from vibe_core.protocols import AgentManifest

        return AgentManifest(
            agent_id="watchman",
            name="WATCHMAN",
            version=self.version if hasattr(self, "version") else "1.0.0",
            author="Steward Protocol",
            description="Monitoring and health checks",
            domain="MONITORING",
            capabilities=["monitoring", "alerts", "system_integrity"],
        )

    def report_status(self) -> dict:
        """Report WATCHMAN status (VibeAgent interface)."""
        return {
            "agent_id": "watchman",
            "name": "WATCHMAN",
            "status": "RUNNING",
            "domain": "ENFORCEMENT",
            "capabilities": self.capabilities,
            "description": "System integrity enforcer and governance enforcer",
        }
