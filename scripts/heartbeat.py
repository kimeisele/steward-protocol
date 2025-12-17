#!/usr/bin/env python3
"""
🫀 HEARTBEAT ENGINE - The Autonomous Task Orchestrator

This is the "ignition key" for the TaskManager Ferrari.
Runs every 15 minutes via GitHub Actions to:
1. Sync TASKS.md ↔ TaskManager (bi-directional)
2. Ingest tasks from data/inbox/*.json
3. Execute pending tasks
4. Commit progress to Git

Architecture:
- Paper UI: TASKS.md (human-friendly interface)
- State Machine: TaskManager (vibe_core)
- Persistence: SQLite (data/vibe_agency.db)
- Concurrency: FileLock (.vibe/state/.lock)
"""

import json
import logging
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import Unified Router for task execution/routing
try:
    from vibe_core.runtime.unified_execution import ExecutionRequest, MilkOceanGate, UnifiedRouter

    UNIFIED_ROUTER_AVAILABLE = True
except ImportError:
    UnifiedRouter = None
    UNIFIED_ROUTER_AVAILABLE = False

# OPUS-073: MANAS Cognitive Kernel - Proactive System Intelligence
try:
    from vibe_core.plugins.opus_assistant.manas import CognitiveKernel, ManasConfig

    MANAS_AVAILABLE = True
except ImportError:
    CognitiveKernel = None
    ManasConfig = None
    MANAS_AVAILABLE = False

# OPUS-089: MANAS Oracle API - Wisdom Interface for System Agents
try:
    from vibe_core.plugins.opus_assistant.manas.api import ManasOracle

    MANAS_ORACLE_AVAILABLE = True
except ImportError:
    ManasOracle = None
    MANAS_ORACLE_AVAILABLE = False

# OPUS-074 WIRING: SQLiteLedger for VAJRA binding in headless mode
try:
    from vibe_core.ledger import SQLiteLedger

    LEDGER_AVAILABLE = True
except ImportError:
    SQLiteLedger = None
    LEDGER_AVAILABLE = False

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S")
logger = logging.getLogger("HEARTBEAT")

# PRANA integration - config-driven behavior
# Allows changing heartbeat behavior via config/prana.yaml WITHOUT touching
# the VISNU-protected workflow files in .github/workflows/
try:
    from vibe_core.prana import (
        ensure_kernel_running,
        get_last_heartbeat,
        record_heartbeat,
    )
    from vibe_core.prana import (
        load_config as load_prana_config,
    )

    PRANA_AVAILABLE = True
except ImportError:
    PRANA_AVAILABLE = False
    load_prana_config = None

# OPUS-087 PRANA: Plugin Pulse Architecture
# Orchestrates plugin on_pulse() calls during heartbeat
try:
    from vibe_core.prana_orchestrator import PranaOrchestrator

    PRANA_ORCHESTRATOR_AVAILABLE = True
except ImportError:
    PranaOrchestrator = None
    PRANA_ORCHESTRATOR_AVAILABLE = False


class HeartbeatEngine:
    """The Autonomous Task Orchestrator."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        # NOTE: TaskManager is now provided by TaskManagerPlugin
        # No longer instantiated here - it's plugin-local with state sovereignty

        # Initialize Unified Router for intelligent task execution
        self.router = None
        if UNIFIED_ROUTER_AVAILABLE:
            try:
                # Initialize without kernel (standalone mode)
                self.router = UnifiedRouter(kernel=None)
                logger.info("🌊 Unified Router ready for task routing")
            except Exception as e:
                logger.warning(f"⚠️ Unified Router unavailable: {e}")
        else:
            logger.warning("⚠️ Unified Router not available - tasks will queue but not execute")

        # OPUS-074 WIRING: Initialize SQLiteLedger for VAJRA (headless mode)
        self.ledger = None
        if LEDGER_AVAILABLE:
            try:
                ledger_path = project_root / "data" / "vibe_ledger.db"
                ledger_path.parent.mkdir(parents=True, exist_ok=True)
                self.ledger = SQLiteLedger(str(ledger_path))
                logger.info("⚡ VAJRA: SQLiteLedger ready (headless mode)")
            except Exception as e:
                logger.warning(f"⚠️ VAJRA: Ledger unavailable: {e}")
        else:
            logger.warning("⚠️ VAJRA: SQLiteLedger not available - running in shadow mode")

        # OPUS-073: Initialize MANAS Cognitive Kernel
        self.manas = None
        if MANAS_AVAILABLE:
            try:
                config = ManasConfig(
                    thinking_interval_minutes=15,  # Match heartbeat interval
                    auto_execute_safe=True,  # Execute SAFE intents automatically
                )
                self.manas = CognitiveKernel(workspace=project_root, config=config)

                # OPUS-074 WIRING: Inject Ledger for VAJRA binding
                if self.ledger and hasattr(self.manas, "inject_ledger"):
                    self.manas.inject_ledger(self.ledger)
                    logger.info("⚡ VAJRA: Ledger bound to MANAS")

                # OPUS-SILPA: Wire execution callback - GIVE MANAS HANDS!
                # Without this, MANAS can think but cannot act.
                try:
                    from vibe_core.plugins.opus_assistant.manas.intent_router import (
                        create_execution_callback,
                    )

                    execution_callback = create_execution_callback(workspace=project_root)
                    self.manas.set_execution_callback(execution_callback)
                    logger.info("🤲 SILPA: Execution callback wired - MANAS has hands!")
                except Exception as wire_err:
                    logger.warning(f"⚠️ SILPA: Could not wire execution: {wire_err}")

                # OPUS-JNANA: Verify LLM Provider is available
                # The provider auto-detects from env vars (OPENROUTER_API_KEY, ANTHROPIC_API_KEY, etc.)
                # Individual handlers import and create providers as needed at runtime
                try:
                    from vibe_core.runtime.providers.factory import create_provider

                    llm_provider = create_provider()
                    provider_name = type(llm_provider).__name__
                    if provider_name != "NoOpProvider":
                        logger.info(f"🧠 JNANA: LLM available ({provider_name}) - deep cognition enabled")
                    else:
                        logger.warning("⚠️ JNANA: No LLM configured - running in analysis-only mode")
                except Exception as llm_err:
                    logger.warning(f"⚠️ JNANA: LLM check failed: {llm_err}")

                logger.info("🧠 MANAS Cognitive Kernel ready")
            except Exception as e:
                logger.warning(f"⚠️ MANAS unavailable: {e}")
        else:
            logger.warning("⚠️ MANAS not available - no proactive cognition")

        # OPUS-089: Initialize MANAS Oracle API - Wisdom Interface
        self.manas_oracle = None
        if MANAS_ORACLE_AVAILABLE:
            try:
                self.manas_oracle = ManasOracle(config=ManasConfig(thinking_interval_minutes=15))
                logger.info("🔮 MANAS Oracle API ready - wisdom interface active")
            except Exception as e:
                logger.warning(f"⚠️ MANAS Oracle API initialization failed: {e}")
        else:
            logger.warning("⚠️ MANAS Oracle API not available")

        # OPUS-087 PRANA: Initialize Plugin Pulse Orchestrator
        self.prana_orchestrator = None
        if PRANA_ORCHESTRATOR_AVAILABLE:
            try:
                self.prana_orchestrator = PranaOrchestrator(kernel=None)

                # Headless Mode: Dynamically load all plugins via PluginLoader
                # This ensures Prana can see and pulse all plugins without a full kernel boot
                try:
                    from pathlib import Path

                    from vibe_core.plugin_loader import PluginLoader

                    logger.info("🔌 PRANA: dynamically loading plugins for headless pulse...")
                    # Scan plugins directory relative to current working directory (root)
                    scan_paths = [
                        Path("vibe_core/plugins"),
                        Path("vibe_core/plugins/runtime_extensions"),
                    ]
                    plugins_map, _ = PluginLoader.discover_and_load(scan_paths=scan_paths)

                    count = 0
                    for plugin in plugins_map.values():
                        self.prana_orchestrator.register_plugin(plugin)
                        count += 1

                    logger.info(f"   + Registered {count} plugins for pulse (Headless)")

                except Exception as e:
                    logger.warning(f"   - Failed to load plugins: {e}")

                logger.info("🫀 PRANA Orchestrator ready for plugin pulse")
            except Exception as e:
                logger.warning(f"⚠️ PRANA Orchestrator unavailable: {e}")

    def pulse(self):
        """Execute one heartbeat cycle."""
        logger.info("💓 HEARTBEAT PULSE STARTED")

        try:
            # OPUS-087 PRANA: Plugin Pulse Cycle (runs FIRST)
            # Executes all plugin on_pulse() methods in phase order
            # SENSORS → ACTUATORS → CLEANUP
            self._run_prana_pulse()

            # Phase 1: MANAS thinks (OPUS-073)
            self._manas_think()

            # Phase 2: Chronicle seals changes in git (OPUS-091)
            self._chronicle_commit()

            logger.info("✅ HEARTBEAT PULSE COMPLETED")
        except Exception as e:
            logger.error(f"❌ HEARTBEAT FAILED: {e}", exc_info=True)
            raise

    def _run_prana_pulse(self):
        """
        OPUS-087 PRANA: Execute plugin pulse cycle.

        Runs all registered plugins' on_pulse() methods in phase order:
        1. SENSORS - Collect data (opus_assistant)
        2. COGNITION - Process data
        3. ACTUATORS - Take actions (vedic_governance)
        4. CLEANUP - Cleanup temp state

        Mutations are batched and committed atomically at the end.
        """
        if not self.prana_orchestrator:
            logger.debug("🫀 PRANA: Orchestrator not available, skipping plugin pulse")
            return

        try:
            logger.info("🫀 PRANA: Starting plugin pulse cycle...")

            result = self.prana_orchestrator.run_pulse_cycle()

            plugins_run = result.get("plugins_executed", 0)
            mutations = result.get("mutations_committed", 0)
            failures = result.get("failures", 0)

            if failures > 0:
                logger.warning(f"🫀 PRANA: {plugins_run} plugins, {mutations} mutations, {failures} failures")
            else:
                logger.info(f"🫀 PRANA: {plugins_run} plugins executed, {mutations} mutations committed")

        except Exception as e:
            # Don't fail the entire heartbeat if PRANA fails
            logger.error(f"🫀 PRANA: Plugin pulse failed: {e}")
            # Continue with legacy heartbeat phases

    def _manas_think(self):
        """OPUS-073: Invoke MANAS cognitive cycle."""
        if not self.manas:
            logger.info("🧠 MANAS not available - skipping cognitive cycle")
            return

        logger.info("🧠 MANAS: Starting cognitive cycle...")

        try:
            # Force=True because heartbeat runs on schedule (not rate-limited)
            intents = self.manas.think(force=True)

            if intents:
                logger.info(f"🧠 MANAS generated {len(intents)} intent(s):")
                for intent in intents:
                    logger.info(f"   • [{intent.risk.value}] {intent.title}")
                    if intent.auto_executable:
                        logger.info(f"     → Auto-executable: {intent.action}")
            else:
                logger.info("🧠 MANAS: No new intents generated")

        except Exception as e:
            logger.warning(f"⚠️ MANAS cognitive cycle failed: {e}")
            # Don't raise - MANAS failure shouldn't stop heartbeat

    def _chronicle_commit(self):
        """
        OPUS-091: Seal changes in git history using Chronicle Cartridge.

        Replaces the old system_chronicle Plugin with direct GitTools call.
        GPG signing is configurable via config/prana.yaml.

        RESILIENCE: Gracefully degrades GPG signing in CI environments where keys
        are not available, preventing silent commit failures.
        """
        # Check if chronicle is enabled
        prana_config = load_prana_config() if PRANA_AVAILABLE else {}
        chronicle_config = prana_config.get("chronicle", {})

        if not chronicle_config.get("enabled", True):
            logger.debug("📜 Chronicle: Disabled in config, skipping")
            return

        try:
            import os

            from vibe_core.cartridges.system.chronicle.tools.git_tools import GitTools

            logger.info("📜 Chronicle: Checking repository status...")

            tools = GitTools()
            status = tools.get_status()

            if not status.get("success"):
                logger.warning("⚠️  Chronicle: Could not get git status")
                return

            # Only commit if dirty (configurable)
            commit_only_if_dirty = chronicle_config.get("commit_only_if_dirty", True)
            if commit_only_if_dirty and not status.get("dirty"):
                logger.debug("📝 Chronicle: No changes to commit")
                return

            # Git is dirty - create commit
            files_changed = status.get("files_changed", [])
            logger.info(f"📜 Chronicle: Found {len(files_changed)} changed files. Sealing history...")

            # Get config values
            gpg_sign = chronicle_config.get("gpg_sign_commits", True)
            commit_prefix = chronicle_config.get("commit_prefix", "🫀 Heartbeat Pulse:")

            # RESILIENCE: Detect if we're in CI environment
            # If running in GitHub Actions without GPG setup, gracefully degrade
            is_ci = os.environ.get("GITHUB_ACTIONS") == "true"
            if is_ci and gpg_sign:
                # Check if GPG key is available
                gpg_available = self._check_gpg_key_available()
                if not gpg_available:
                    logger.warning(
                        "⚠️  Chronicle: GPG signing requested but no key found in CI environment. "
                        "Falling back to unsigned commits (configure GPG_SIGNING_KEY secret if needed)."
                    )
                    gpg_sign = False

            commit_result = tools.seal_history(
                message=f"{commit_prefix} System auto-save",
                files=None,  # Commit all staged (or all modified if nothing staged)
                sign=gpg_sign,  # Configurable GPG signing (with CI fallback)
            )

            if commit_result.get("success"):
                commit_hash = commit_result.get("commit_hash", "unknown")[:8]
                sign_status = "signed" if gpg_sign else "unsigned"
                logger.info(f"✅ Chronicle: History sealed ({commit_hash}, {sign_status})")
            else:
                logger.warning(f"⚠️  Chronicle: Commit failed - {commit_result.get('message', 'unknown error')}")

        except ImportError as e:
            logger.warning(f"⚠️  Chronicle: GitTools not available ({e})")
        except Exception as e:
            logger.error(f"❌ Chronicle: Unexpected error - {e}", exc_info=True)

    @staticmethod
    def _check_gpg_key_available() -> bool:
        """
        Check if GPG key is available for signing.

        Returns:
            True if GPG key exists and is usable, False otherwise
        """

        try:
            # List available GPG keys
            result = subprocess.run(
                ["gpg", "--list-secret-keys", "--quiet"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            # If there are keys, return True
            return result.returncode == 0 and bool(result.stdout.strip())
        except (subprocess.TimeoutExpired, FileNotFoundError):
            # GPG not installed or timed out
            return False
        except Exception:
            # Any other error, assume key not available
            return False


def main():
    """
    Main entry point.

    PRANA Integration:
    - Checks config/prana.yaml for settings
    - Respects min_interval_minutes to prevent duplicate runs
    - Optionally boots kernel before processing tasks
    - Records heartbeat timestamp for tracking

    This allows changing behavior WITHOUT modifying VISNU-protected workflows.
    """
    # PRANA: Config-driven behavior
    if PRANA_AVAILABLE:
        config = load_prana_config()

        # Check if heartbeat is enabled
        if not config.heartbeat.enabled:
            logger.info("💓 PRANA: Heartbeat disabled in config. Exiting.")
            return

        # Check minimum interval (prevent duplicate runs)
        last_pulse = get_last_heartbeat()
        if last_pulse:
            from datetime import datetime, timedelta

            try:
                last_dt = datetime.fromisoformat(last_pulse)
                min_interval = timedelta(minutes=config.heartbeat.min_interval_minutes)
                if datetime.utcnow() - last_dt < min_interval:
                    logger.info(
                        f"💓 PRANA: Skipping - last pulse was {last_pulse} (interval: {config.heartbeat.min_interval_minutes}min)"
                    )
                    return
            except Exception as e:
                logger.warning(f"⚠️ Could not parse last heartbeat: {e}")

        # Boot kernel if configured
        if config.heartbeat.boot_kernel_first:
            logger.info("💓 PRANA: Ensuring kernel is running...")
            ensure_kernel_running(config)

        # Record this heartbeat
        record_heartbeat()

        logger.info(f"💓 PRANA: Config loaded - max_tasks={config.heartbeat.max_tasks_per_pulse}")
    else:
        logger.warning("⚠️ PRANA not available - running with defaults")

    # Run the heartbeat
    engine = HeartbeatEngine(project_root)
    engine.pulse()


if __name__ == "__main__":
    main()
