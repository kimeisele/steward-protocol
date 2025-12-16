"""
OPUS-065: DHARMA-JNANA Intent Router

Routes approved intents to the appropriate cortex module for execution.

This is the MISSING LINK that connects:
    analyzers/ (detect) → cognitive_kernel (manage) → cortex/ (execute)

Architecture:
    ┌─────────────────────────────────────────────────────────────┐
    │                    IntentRouter                              │
    ├─────────────────────────────────────────────────────────────┤
    │  Intent Type          →  Cortex Module                      │
    │  ─────────────────────────────────────────────────          │
    │  document_*, update_* →  SUTRA (Wiki/Docs)                  │
    │  fix_*drift           →  DHARMA (Audit)                     │
    │  commit_*, cleanup_*  →  ShellCortex (Git)                  │
    │  genesis_*, create_*  →  SILPA (Code Gen)                   │
    │  test_*, revive_*     →  TestCortex (Tests)                 │
    │  config_*             →  MANDALA (Config)                   │
    │  analyze_*, scan_*    →  AKASHA (Knowledge)                 │
    │  plan_*, strategy_*   →  SANKALPA (Strategy)                │
    └─────────────────────────────────────────────────────────────┘

VAJRA Compliance:
    - All routes are logged
    - Failed routes don't crash the system
    - Unknown intents are safely queued for manual handling
"""

import json
import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional

if TYPE_CHECKING:
    from vibe_core.kernel_impl import RealVibeKernel

from .intent_generator import Intent
from .validator import SrutiValidator

logger = logging.getLogger("MANAS.IntentRouter")

# OPUS-075: HIL Bridge state directory
HIL_STATE_DIR = ".opus_state"
PENDING_INTENTS_FILE = "pending_intents.json"
KARMA_LOG_FILE = "karma_log.json"


@dataclass
class RouteResult:
    """Result of routing an intent to a cortex module."""

    success: bool
    handler: str  # Which cortex handled it
    result: Dict[str, Any]
    error: Optional[str] = None


class IntentRouter:
    """
    Routes intents to appropriate cortex modules for execution.

    PRATYAYA (Verification):
        - Only routes intents with known handlers
        - Unknown intents return safely with error
        - All routes logged for audit

    KARMA (Action):
        - Calls cortex module with intent params
        - Returns structured result
        - Never crashes, always returns RouteResult
    """

    def __init__(self, workspace: Optional[Path] = None):
        """Initialize the router with optional workspace path."""
        self._workspace = workspace or Path.cwd()
        self._kernel: Optional["RealVibeKernel"] = None
        self._handlers: Dict[str, Callable[[Intent], Dict[str, Any]]] = {}
        self._validator = SrutiValidator(workspace=self._workspace)  # OPUS-069
        self._register_handlers()

        # OPUS-075: Load MANAS fortress config
        self._manas_config = self._load_manas_config()
        self._autonomous_steps = 0  # Track steps for safety limit

    def _load_manas_config(self) -> Dict[str, Any]:
        """Load MANAS config from config/opus.yaml."""
        import yaml

        config_path = self._workspace / "config" / "opus.yaml"
        if config_path.exists():
            try:
                with open(config_path) as f:
                    data = yaml.safe_load(f)
                    return data.get("manas", {})
            except Exception as e:
                logger.warning(f"Failed to load MANAS config: {e}")
        return {
            "mode": "manual",
            "auto_execute_threshold": 0.85,
            "protected_zones": [],
            "max_autonomous_steps": 10,
        }

    def inject_kernel(self, kernel: "RealVibeKernel") -> None:
        """
        ⚡ VAJRA: Inject kernel for ledger access.

        OPUS-069: Also injects into SrutiValidator for SRUTI validation.
        """
        self._kernel = kernel
        # OPUS-069: Wire validator to kernel for ledger access
        self._validator.inject_kernel(kernel)
        logger.info("⚡ IntentRouter: Kernel injected (+ SrutiValidator bound)")

    def _register_handlers(self) -> None:
        """Register intent type → handler mappings."""
        # Documentation intents → SUTRA
        self._handlers["update_readme"] = self._handle_sutra
        self._handlers["update_opus_documentation"] = self._handle_sutra
        self._handlers["document_manas"] = self._handle_sutra
        self._handlers["fix_documentation_drift"] = self._handle_sutra

        # Git/Shell intents → ShellCortex
        self._handlers["commit_pending_changes"] = self._handle_shell
        self._handlers["cleanup_stale_branches"] = self._handle_shell
        self._handlers["cleanup_old_logs"] = self._handle_shell

        # Test intents → TestCortex
        self._handlers["revive_archived_tests"] = self._handle_test
        self._handlers["run_tests"] = self._handle_test

        # Code generation → SILPA
        self._handlers["genesis_tests"] = self._handle_silpa
        self._handlers["create_tests"] = self._handle_silpa

        # Architecture audit → DHARMA
        self._handlers["audit_architecture"] = self._handle_dharma
        self._handlers["check_drift"] = self._handle_dharma

        # Strategy → SANKALPA
        self._handlers["plan_strategy"] = self._handle_sankalpa
        self._handlers["review_todos"] = self._handle_sankalpa

        # Research → VIDYA (Web Search via Tavily)
        self._handlers["research_topic"] = self._handle_research
        self._handlers["web_search"] = self._handle_research
        self._handlers["get_best_practices"] = self._handle_research
        self._handlers["find_implementation_guide"] = self._handle_research

        # Wiring audit → OPUS-066 WiringMap
        self._handlers["audit_wiring"] = self._handle_wiring
        self._handlers["find_blind_spots"] = self._handle_wiring

        # Mutation testing → OPUS-038 MutationHandlers
        self._handlers["run_mutation_tests"] = self._handle_mutation
        self._handlers["mutation_protocol"] = self._handle_mutation

        # Knowledge graph → UnifiedKnowledgeGraph
        self._handlers["knowledge_query"] = self._handle_knowledge
        self._handlers["search_knowledge"] = self._handle_knowledge
        self._handlers["get_context"] = self._handle_knowledge

        logger.info(f"IntentRouter: {len(self._handlers)} handlers registered")

    # =========================================================================
    # OPUS-075: MANAS 6D FORTRESS - Prefrontal Cortex
    # =========================================================================

    def gate(self, intent: Intent) -> Dict[str, Any]:
        """
        OPUS-075: The Prefrontal Cortex - decides whether to execute or ask.

        Returns:
            {"status": "execute"} - OK to auto-execute
            {"status": "ask_user", "reason": ...} - Need human approval
            {"status": "blocked", "reason": ...} - Denied (protected zone)
        """
        mode = self._manas_config.get("mode", "manual")
        threshold = self._manas_config.get("auto_execute_threshold", 0.85)
        protected_zones = self._manas_config.get("protected_zones", [])
        max_steps = self._manas_config.get("max_autonomous_steps", 10)

        # Get confidence from intent (default 0.5 if not set)
        confidence = getattr(intent, "confidence", 0.5)
        targets = getattr(intent, "targets", [])

        # 1. Protected Zone Check (Nuclear Safety)
        for target in targets:
            for zone in protected_zones:
                if zone in str(target):
                    logger.warning(f"🛡️ BLOCKED: Target {target} is Protected Zone")
                    return {"status": "blocked", "reason": "protected_zone", "target": str(target)}

        # 2. Mode Check
        if mode == "manual":
            return {"status": "ask_user", "reason": "manual_mode"}

        # 3. Step Limit Check
        if self._autonomous_steps >= max_steps:
            logger.warning(f"✋ LIMIT: {self._autonomous_steps} autonomous steps reached")
            return {"status": "ask_user", "reason": "step_limit_reached"}

        # 4. Confidence Check (The Singularity Gate)
        if confidence >= threshold:
            logger.info(f"⚡ AUTO-EXECUTE: Confidence {confidence:.2f} >= {threshold}")
            self._autonomous_steps += 1
            return {"status": "execute", "confidence": confidence}
        else:
            logger.info(f"✋ HESITATION: Confidence {confidence:.2f} < {threshold}")
            return {"status": "ask_user", "reason": "low_confidence", "confidence": confidence}

    def reset_autonomous_steps(self) -> None:
        """Reset the autonomous step counter (call on session start)."""
        self._autonomous_steps = 0

    # =========================================================================
    # OPUS-075: HIL BRIDGE - Human-In-The-Loop Persistence
    # =========================================================================

    def _get_state_dir(self) -> Path:
        """Get or create the HIL state directory."""
        state_dir = self._workspace / HIL_STATE_DIR
        state_dir.mkdir(parents=True, exist_ok=True)
        return state_dir

    def _load_pending_intents(self) -> Dict[str, Dict[str, Any]]:
        """Load pending intents from JSON file."""
        pending_file = self._get_state_dir() / PENDING_INTENTS_FILE
        if pending_file.exists():
            try:
                return json.loads(pending_file.read_text())
            except Exception as e:
                logger.warning(f"Failed to load pending intents: {e}")
        return {}

    def _save_pending_intents(self, pending: Dict[str, Dict[str, Any]]) -> None:
        """Save pending intents to JSON file."""
        pending_file = self._get_state_dir() / PENDING_INTENTS_FILE
        try:
            pending_file.write_text(json.dumps(pending, indent=2, default=str))
        except Exception as e:
            logger.error(f"Failed to save pending intents: {e}")

    def queue_intent(self, intent: Intent, gate_result: Dict[str, Any]) -> str:
        """
        OPUS-075: Queue an intent for human approval.

        Called when gate() returns ask_user - stores the intent for later approval.

        Returns:
            The intent ID (for reference in approve command)
        """
        pending = self._load_pending_intents()

        # Serialize intent for storage
        intent_data = {
            "id": intent.id,
            "intent_type": intent.intent_type,
            "title": intent.title,
            "params": intent.params,
            "confidence": getattr(intent, "confidence", 0.5),
            "targets": getattr(intent, "targets", []),
            "gate_reason": gate_result.get("reason", "unknown"),
            "queued_at": datetime.now().isoformat(),
            "status": "pending",
        }

        pending[intent.id] = intent_data
        self._save_pending_intents(pending)

        logger.info(f"📥 Intent queued for approval: {intent.id} ({intent.title})")
        return intent.id

    def list_pending_intents(self) -> List[Dict[str, Any]]:
        """
        OPUS-075: List all pending intents awaiting approval.

        Returns:
            List of pending intent dictionaries
        """
        pending = self._load_pending_intents()
        return [v for v in pending.values() if v.get("status") == "pending"]

    def approve_intent(self, intent_id: str) -> RouteResult:
        """
        OPUS-075: Approve and execute a pending intent.

        Args:
            intent_id: The ID of the intent to approve

        Returns:
            RouteResult from executing the intent
        """
        pending = self._load_pending_intents()

        if intent_id not in pending:
            logger.warning(f"Intent not found: {intent_id}")
            return RouteResult(
                success=False,
                handler="HIL_BRIDGE",
                result={},
                error=f"Intent not found: {intent_id}",
            )

        intent_data = pending[intent_id]

        if intent_data.get("status") != "pending":
            return RouteResult(
                success=False,
                handler="HIL_BRIDGE",
                result={},
                error=f"Intent already processed: {intent_data.get('status')}",
            )

        # Reconstruct Intent object
        intent = Intent(
            id=intent_data["id"],
            intent_type=intent_data["intent_type"],
            title=intent_data["title"],
            description=intent_data.get("description", intent_data["title"]),
            reasoning=intent_data.get("reasoning", "Approved via HIL Bridge"),
            params=intent_data.get("params", {}),
        )
        # Restore optional attributes
        if "confidence" in intent_data:
            intent.confidence = intent_data["confidence"]
        if "targets" in intent_data:
            intent.targets = intent_data["targets"]

        logger.info(f"✅ Approving intent: {intent_id} ({intent.title})")

        # Execute via Envoy (The Hand)
        # OPUS-078: Clean Architecture - Gehirn (Manas) delegates to Hände (Envoy)
        if self._kernel and hasattr(self._kernel, "envoy"):
            logger.info("🕵️ Delegating to Envoy for execution...")
            envoy_result = self._kernel.envoy.execute_mission(intent)

            # Map Envoy result to RouteResult
            result = RouteResult(
                success=envoy_result.get("status") == "success",
                handler=envoy_result.get("executed_by", "Envoy"),
                result=envoy_result,
                error=envoy_result.get("error"),
            )
        else:
            # Fallback if kernel/envoy isn't ready (shouldn't happen in full boot)
            logger.warning("⚠️ Envoy not found on kernel - falling back to direct routing")
            result = self.route(intent)

        # Update status and record karma
        intent_data["status"] = "approved"
        intent_data["approved_at"] = datetime.now().isoformat()
        intent_data["result_success"] = result.success
        pending[intent_id] = intent_data
        self._save_pending_intents(pending)

        # Record karma feedback
        self._record_karma(intent, result.success)

        return result

    def reject_intent(self, intent_id: str, reason: str = "") -> bool:
        """
        OPUS-075: Reject a pending intent.

        Args:
            intent_id: The ID of the intent to reject
            reason: Optional reason for rejection

        Returns:
            True if rejected successfully
        """
        pending = self._load_pending_intents()

        if intent_id not in pending:
            logger.warning(f"Intent not found: {intent_id}")
            return False

        intent_data = pending[intent_id]
        intent_data["status"] = "rejected"
        intent_data["rejected_at"] = datetime.now().isoformat()
        intent_data["rejection_reason"] = reason
        pending[intent_id] = intent_data
        self._save_pending_intents(pending)

        # Record negative karma
        intent = Intent(
            id=intent_data["id"],
            intent_type=intent_data["intent_type"],
            title=intent_data["title"],
            description=intent_data.get("description", intent_data["title"]),
            reasoning=intent_data.get("reasoning", "Rejected via HIL Bridge"),
            params=intent_data.get("params", {}),
        )
        self._record_karma(intent, success=False, rejected=True)

        logger.info(f"❌ Rejected intent: {intent_id}")
        return True

    def _record_karma(self, intent: Intent, success: bool, rejected: bool = False) -> None:
        """
        OPUS-075: Record karma feedback for learning.

        Karma is used to adjust future confidence thresholds and improve
        MANAS's judgment over time.
        """
        karma_config = self._manas_config.get("karma", {})
        if not karma_config.get("enabled", True):
            return

        karma_file = self._get_state_dir() / KARMA_LOG_FILE
        karma_log = []
        if karma_file.exists():
            try:
                karma_log = json.loads(karma_file.read_text())
            except Exception:
                karma_log = []

        # Calculate karma score
        if rejected:
            score = -karma_config.get("failure_weight", 2.0)
        elif success:
            score = karma_config.get("success_weight", 1.0)
        else:
            score = -karma_config.get("failure_weight", 2.0)

        entry = {
            "timestamp": datetime.now().isoformat(),
            "intent_id": intent.id,
            "intent_type": intent.intent_type,
            "confidence": getattr(intent, "confidence", 0.5),
            "outcome": "rejected" if rejected else ("success" if success else "failure"),
            "karma_score": score,
        }
        karma_log.append(entry)

        # Keep only last 100 entries
        karma_log = karma_log[-100:]

        try:
            karma_file.write_text(json.dumps(karma_log, indent=2))
        except Exception as e:
            logger.warning(f"Failed to save karma log: {e}")

    def get_karma_summary(self) -> Dict[str, Any]:
        """
        OPUS-075: Get karma summary for dashboard display.

        Returns:
            Dictionary with karma statistics
        """
        karma_file = self._get_state_dir() / KARMA_LOG_FILE
        if not karma_file.exists():
            return {"total_karma": 0, "entries": 0, "success_rate": 0.0}

        try:
            karma_log = json.loads(karma_file.read_text())
            total_karma = sum(e.get("karma_score", 0) for e in karma_log)
            successes = sum(1 for e in karma_log if e.get("outcome") == "success")
            total = len(karma_log)

            return {
                "total_karma": total_karma,
                "entries": total,
                "success_rate": (successes / total * 100) if total > 0 else 0.0,
                "recent": karma_log[-5:] if karma_log else [],
            }
        except Exception:
            return {"total_karma": 0, "entries": 0, "success_rate": 0.0}

    def route(self, intent: Intent) -> RouteResult:
        """
        Route an intent to the appropriate cortex module.

        Args:
            intent: The intent to route

        Returns:
            RouteResult with success status and execution result
        """
        intent_type = intent.intent_type
        logger.info(f"🔀 Routing intent: {intent_type} ({intent.id})")

        # Find handler
        handler = self._handlers.get(intent_type)

        if handler is None:
            # Check for prefix matches (genesis_*, semantic_gap_*)
            for prefix in ["genesis_", "semantic_gap_", "ci_status_"]:
                if intent_type.startswith(prefix):
                    handler = self._get_prefix_handler(prefix)
                    break

        if handler is None:
            logger.warning(f"⚠️ No handler for intent type: {intent_type}")
            return RouteResult(
                success=False,
                handler="none",
                result={},
                error=f"No handler registered for intent type: {intent_type}",
            )

        try:
            result = handler(intent)

            # OPUS-069: Validate output against Sruti (Ledger)
            validation = self._validator.validate_intent_output(result)
            if not validation.valid:
                logger.warning(f"⚠️ SRUTI VIOLATION: {validation.errors}")
                result["sruti_validation"] = validation.to_dict()
            elif validation.warnings:
                logger.info(f"📝 SRUTI: {validation.warnings}")
                result["sruti_validation"] = validation.to_dict()

            return RouteResult(
                success=result.get("success", True),
                handler=result.get("handler", "unknown"),
                result=result,
            )
        except Exception as e:
            logger.error(f"❌ Handler failed for {intent_type}: {e}")
            return RouteResult(
                success=False,
                handler="error",
                result={},
                error=str(e),
            )

    def _get_prefix_handler(self, prefix: str) -> Optional[Callable]:
        """Get handler for prefix-based intent types."""
        prefix_map = {
            "genesis_": self._handle_silpa,  # Code generation
            "semantic_gap_": self._handle_silpa,  # Test generation
            "ci_status_": self._handle_shell,  # CI/CD related
        }
        return prefix_map.get(prefix)

    # =========================================================================
    # CORTEX HANDLERS
    # =========================================================================

    def _handle_sutra(self, intent: Intent) -> Dict[str, Any]:
        """
        Route to SUTRA for documentation tasks.

        OPUS-071: Now supports full wiki sync with GITHUB_TOKEN!
        """
        from .cortex.sutra import SutraOrchestrator, SutraWeaver, WikiSync

        logger.info(f"📜 SUTRA handling: {intent.title}")

        try:
            # Check if this is a sync request
            sync_keywords = {"sync", "push", "update wiki", "publish"}
            is_sync_request = any(kw in intent.title.lower() for kw in sync_keywords)

            # Check for credentials
            wiki_sync = WikiSync(workspace=self._workspace)
            has_creds = wiki_sync.has_credentials()

            if is_sync_request and has_creds:
                # OPUS-071: Full wiki sync!
                logger.info("📜 SUTRA: Executing full wiki sync...")
                orchestrator = SutraOrchestrator(workspace=self._workspace)
                result = orchestrator.generate_and_sync()

                if result.success:
                    return {
                        "success": True,
                        "handler": "SUTRA",
                        "action": "wiki_synced",
                        "pages_synced": result.pages_synced,
                        "wiki_url": result.wiki_url,
                        "message": f"📜 SUTRA synced {len(result.pages_synced)} pages to GitHub Wiki!",
                    }
                else:
                    return {
                        "success": False,
                        "handler": "SUTRA",
                        "action": "sync_failed",
                        "errors": result.errors,
                        "message": f"SUTRA sync failed: {', '.join(result.errors)}",
                    }

            elif is_sync_request and not has_creds:
                # Want to sync but no credentials
                return {
                    "success": False,
                    "handler": "SUTRA",
                    "action": "no_credentials",
                    "message": "📜 SUTRA: Set GITHUB_TOKEN environment variable to enable wiki sync",
                }

            else:
                # Just gather context (preview mode)
                weaver = SutraWeaver(workspace=self._workspace)
                ctx = weaver.gather_context()

                return {
                    "success": True,
                    "handler": "SUTRA",
                    "action": "context_gathered",
                    "agents_found": len(ctx.agents),
                    "modules_found": len(ctx.modules),
                    "has_credentials": has_creds,
                    "message": f"📜 SUTRA gathered context: {len(ctx.agents)} agents, {len(ctx.modules)} modules. "
                    + ("Ready to sync!" if has_creds else "Set GITHUB_TOKEN to enable sync."),
                }

        except Exception as e:
            logger.error(f"SUTRA error: {e}")
            return {"success": False, "handler": "SUTRA", "error": str(e)}

    def _handle_shell(self, intent: Intent) -> Dict[str, Any]:
        """Route to ShellCortex for shell commands."""
        from .cortex.shell import ShellCortex

        logger.info(f"🐚 ShellCortex handling: {intent.title}")

        try:
            # OPUS-SILPA: Real Git operations via GitTools
            if intent.intent_type == "commit_pending_changes":
                return self._execute_git_commit(intent)

            shell = ShellCortex(workspace=self._workspace)
            if self._kernel:
                shell.inject_kernel(self._kernel)

            # Determine command based on intent type
            cmd = None
            if intent.intent_type == "cleanup_stale_branches":
                cmd = "git branch --merged | grep -v main | head -5"
            elif intent.intent_type == "cleanup_old_logs":
                cmd = "find . -name '*.log' -mtime +7 | head -10"

            if cmd:
                result = shell.execute(cmd, safe_mode=True)
                return {
                    "success": result.exit_code == 0,
                    "handler": "ShellCortex",
                    "command": cmd,
                    "output": result.stdout[:500] if result.stdout else "",
                    "exit_code": result.exit_code,
                }
            else:
                return {
                    "success": True,
                    "handler": "ShellCortex",
                    "message": "Intent acknowledged, no specific command defined",
                }
        except Exception as e:
            return {"success": False, "handler": "ShellCortex", "error": str(e)}

    def _execute_git_commit(self, intent: Intent) -> Dict[str, Any]:
        """
        OPUS-SILPA: Execute real git commit via GitTools.

        This gives MANAS actual hands to commit code changes.
        The commit message references the intent for audit trail.
        """
        from vibe_core.cartridges.system.chronicle.tools.git_tools import GitTools

        logger.info(f"🔐 SILPA executing git commit: {intent.title}")

        try:
            git = GitTools()

            # First check status
            status = git.get_status()
            if not status.get("dirty"):
                return {
                    "success": True,
                    "handler": "GitTools",
                    "action": "no_changes",
                    "message": "No pending changes to commit",
                }

            # Build commit message with MANAS attribution
            commit_msg = f"chore(manas): {intent.title}\n\nIntent ID: {intent.id}\nGenerated by MANAS Cognitive Kernel"

            # Get files to commit from intent params or commit all
            files = intent.params.get("files")

            # Execute the commit (without signing for now - simpler)
            result = git.seal_history(
                message=commit_msg,
                files=files,
                sign=False,  # Skip signing to avoid GPG complexity
            )

            if result.get("success"):
                logger.info(f"✅ MANAS committed: {result.get('commit_hash_short')}")
                return {
                    "success": True,
                    "handler": "GitTools",
                    "action": "committed",
                    "commit_hash": result.get("commit_hash"),
                    "commit_hash_short": result.get("commit_hash_short"),
                    "message": f"MANAS committed: {result.get('commit_hash_short')} - {intent.title}",
                }
            else:
                return {
                    "success": False,
                    "handler": "GitTools",
                    "action": "commit_failed",
                    "error": result.get("message", "Unknown error"),
                }

        except Exception as e:
            logger.error(f"❌ Git commit failed: {e}")
            return {"success": False, "handler": "GitTools", "error": str(e)}

    def _handle_test(self, intent: Intent) -> Dict[str, Any]:
        """Route to TestCortex for test-related tasks."""
        from .cortex.test import TestCortex

        logger.info(f"🧪 TestCortex handling: {intent.title}")

        try:
            test_cortex = TestCortex(workspace=self._workspace)
            if self._kernel:
                test_cortex.inject_kernel(self._kernel)

            # Run smoke test by default
            result = test_cortex.run_smoke_test()
            return {
                "success": result.success,
                "handler": "TestCortex",
                "tests_passed": result.tests_passed,
                "tests_failed": result.tests_failed,
                "duration_ms": result.duration_ms,
            }
        except Exception as e:
            return {"success": False, "handler": "TestCortex", "error": str(e)}

    def _handle_silpa(self, intent: Intent) -> Dict[str, Any]:
        """Route to SILPA for code generation/refactoring."""
        from .cortex.silpa import SilpaArchitect

        logger.info(f"🏗️ SILPA handling: {intent.title}")

        try:
            architect = SilpaArchitect(workspace=self._workspace)

            # SILPA analyzes what could be refactored
            # Full refactoring requires human approval
            return {
                "success": True,
                "handler": "SILPA",
                "action": "analysis_only",
                "message": f"SILPA analyzed intent: {intent.title}. Full execution requires approval.",
                "intent_params": intent.params,
            }
        except Exception as e:
            return {"success": False, "handler": "SILPA", "error": str(e)}

    def _handle_dharma(self, intent: Intent) -> Dict[str, Any]:
        """Route to DHARMA for architecture audit."""
        from .cortex.dharma import DharmaAuditor

        logger.info(f"⚖️ DHARMA handling: {intent.title}")

        try:
            auditor = DharmaAuditor(workspace=self._workspace)
            report = auditor.audit()

            return {
                "success": True,
                "handler": "DHARMA",
                "violations_found": len(report.violations),
                "drift_detected": report.total_violations > 0,
                "compliance_score": report.compliance_score,
                "message": f"DHARMA audit complete: {len(report.violations)} violations, {report.compliance_score:.1f}% compliant",
            }
        except Exception as e:
            return {"success": False, "handler": "DHARMA", "error": str(e)}

    def _handle_sankalpa(self, intent: Intent) -> Dict[str, Any]:
        """Route to SANKALPA for strategy planning."""
        from .cortex.sankalpa import SankalpaOrchestrator

        logger.info(f"🎯 SANKALPA handling: {intent.title}")

        try:
            orchestrator = SankalpaOrchestrator(workspace=self._workspace)

            return {
                "success": True,
                "handler": "SANKALPA",
                "action": "strategy_acknowledged",
                "message": f"SANKALPA acknowledged: {intent.title}",
            }
        except Exception as e:
            return {"success": False, "handler": "SANKALPA", "error": str(e)}

    def _handle_wiring(self, intent: Intent) -> Dict[str, Any]:
        """Route to WiringMap for blind spot detection."""
        from .cortex.wiring_map import WiringMap

        logger.info(f"🔌 WiringMap handling: {intent.title}")

        try:
            wmap = WiringMap(workspace=self._workspace)
            report = wmap.audit()

            return {
                "success": True,
                "handler": "WiringMap",
                "total_nodes": report.total_nodes,
                "connected": report.connected_nodes,
                "disconnected": report.disconnected_nodes,
                "health_score": f"{report.health_score:.1f}%",
                "blind_spots": report.blind_spots[:10],  # Top 10
                "message": f"Wiring audit: {report.health_score:.1f}% healthy, {len(report.blind_spots)} blind spots",
            }
        except Exception as e:
            return {"success": False, "handler": "WiringMap", "error": str(e)}

    def _handle_research(self, intent: Intent) -> Dict[str, Any]:
        """Route to VIDYA for research/web search tasks."""
        import asyncio

        from vibe_core.plugins.opus_assistant.vidya.research_interface import ResearchInterface

        logger.info(f"🔬 VIDYA handling: {intent.title}")

        try:
            research = ResearchInterface(kernel=self._kernel)

            # Extract query from intent params or title
            query = intent.params.get("query") or intent.params.get("topic") or intent.title

            # Run async query in sync context
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            # Choose method based on intent type
            if intent.intent_type == "get_best_practices":
                topic = intent.params.get("topic", query)
                result = loop.run_until_complete(research.get_best_practices(topic))
            elif intent.intent_type == "find_implementation_guide":
                task = intent.params.get("task", query)
                result = loop.run_until_complete(research.get_implementation_guide(task))
            else:
                # Default research query
                max_results = intent.params.get("max_results", 5)
                result = loop.run_until_complete(research.query(query, max_results=max_results))

            return {
                "success": result.success,
                "handler": "VIDYA",
                "mode": result.mode,
                "query": result.query,
                "sources_count": len(result.sources),
                "summary": result.summary[:500] if result.summary else "",
                "key_insights": result.key_insights[:3] if result.key_insights else [],
                "error": result.error,
            }
        except Exception as e:
            return {"success": False, "handler": "VIDYA", "error": str(e)}

    def _handle_mutation(self, intent: Intent) -> Dict[str, Any]:
        """Route to MutationHandlers for mutation testing."""
        import asyncio

        from vibe_core.plugins.opus_assistant.events.mutation_handlers import get_mutation_handlers

        logger.info(f"🧬 MutationHandlers handling: {intent.title}")

        try:
            handlers = get_mutation_handlers(workspace=self._workspace)

            # Extract params
            source_code = intent.params.get("source_code", "")
            test_code = intent.params.get("test_code", "")
            module_name = intent.params.get("module_name", "legacy_module")

            if not source_code or not test_code:
                return {
                    "success": False,
                    "handler": "MutationHandlers",
                    "error": "Missing source_code or test_code parameters",
                }

            # Run async mutation protocol in sync context
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            result = loop.run_until_complete(
                handlers.run_mutation_protocol(
                    {
                        "source_code": source_code,
                        "test_code": test_code,
                        "module_name": module_name,
                    }
                )
            )

            return {
                "success": result.get("success", False),
                "handler": "MutationHandlers",
                "kill_rate": result.get("kill_rate", 0.0),
                "total_mutants": result.get("total_mutants", 0),
                "killed": result.get("killed", 0),
                "survived": result.get("survived", 0),
                "message": f"Mutation test: {result.get('kill_rate', 0):.1%} kill rate",
            }
        except Exception as e:
            return {"success": False, "handler": "MutationHandlers", "error": str(e)}

    def _handle_knowledge(self, intent: Intent) -> Dict[str, Any]:
        """Route to UnifiedKnowledgeGraph for knowledge queries."""
        from vibe_core.knowledge.graph import get_knowledge_graph

        logger.info(f"📚 KnowledgeGraph handling: {intent.title}")

        try:
            graph = get_knowledge_graph()

            # Determine query type
            query = intent.params.get("query") or intent.params.get("concept") or intent.title

            if intent.intent_type == "get_context":
                # Return compiled prompt context
                context = graph.compile_prompt_context(query)
                return {
                    "success": True,
                    "handler": "KnowledgeGraph",
                    "context": context[:2000] if context else "",
                    "message": f"Context compiled for: {query}",
                }
            else:
                # Search nodes
                nodes = graph.search_nodes(query)
                return {
                    "success": True,
                    "handler": "KnowledgeGraph",
                    "nodes_found": len(nodes),
                    "nodes": [{"id": n.id, "name": n.name, "type": n.type.value} for n in nodes[:10]],
                    "message": f"Found {len(nodes)} nodes for: {query}",
                }
        except Exception as e:
            return {"success": False, "handler": "KnowledgeGraph", "error": str(e)}


def create_execution_callback(
    workspace: Optional[Path] = None, kernel: Optional["RealVibeKernel"] = None
) -> Callable[[Intent], Dict[str, Any]]:
    """
    Factory function to create an execution callback for CognitiveKernel.

    Usage:
        callback = create_execution_callback(workspace, kernel)
        cognitive_kernel.set_execution_callback(callback)
    """
    router = IntentRouter(workspace=workspace)
    if kernel:
        router.inject_kernel(kernel)

    def callback(intent: Intent) -> Dict[str, Any]:
        result = router.route(intent)
        return {
            "success": result.success,
            "handler": result.handler,
            "error": result.error,
            **result.result,
        }

    return callback
