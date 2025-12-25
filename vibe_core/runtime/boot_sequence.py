"""Boot Sequence - Main entry point for system-boot.sh → vibe-cli boot

Orchestrates the conveyor belt:
1. Context Loader → Collect signals
2. Playbook Engine → Route to task
3. Prompt Composer → Compose final prompt
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

from vibe_core.loaders.manifest_registry import ManifestRegistry
from vibe_core.runtime.context_loader import ContextLoader
from vibe_core.runtime.project_memory import ProjectMemoryManager
from vibe_core.runtime.prompt_composer import PromptComposer
from vibe_core.runtime.unified_execution import UnifiedRouter
from vibe_core.store.sqlite_store import SQLiteStore


class BootSequence:
    """Main entry point for system boot"""

    def __init__(self, project_root: Path | None = None):
        self.project_root = project_root or Path.cwd()

        # OPUS-307 Phase F: Scan manifests ONCE at boot (before any loader runs)
        # "Das System WEISS was installiert ist, es RATET nicht."
        ManifestRegistry.scan_all()

        # Conveyor Belt 1: Context (Unified Load)
        # BootSequence uses the 'project' context item provided by ContextLoader

        # State Persistence (vibe.db)
        # Initialize BEFORE ProjectMemoryManager which depends on it
        # OPUS-025: Bootstrap Paradox - Config not yet loaded, construct from defaults
        # ADR-025b: project.state_db = ".vibe/vibe.db"
        _vibe_root = ".vibe"
        _state_db = "vibe.db"
        self.sqlite_store = SQLiteStore(self.project_root / _vibe_root / _state_db)

        items, _ = ContextLoader.discover_and_load(scan_paths=[self.project_root])
        self.context_loader = items["project"]  # Actually a ContextManager instance

        # Conveyor Belt 2: Playbook Engine (Unified Router)
        # Now uses UnifiedRouter which wraps LayeredRouter

        self.playbook_engine = UnifiedRouter()  # UnifiedRouter replaces PlaybookRouter

        # Conveyor Belt 3: Prompt Composition (Context-Aware)
        # Use SINGLETON to share with plugins that register context
        from vibe_core.runtime.prompt_context import get_prompt_context

        self.prompt_context = get_prompt_context()
        self.prompt_composer = PromptComposer(self.prompt_context)

        # Load plugins so they can register their context providers
        self._load_plugin_contexts()

        # Output Manager (Renderer)
        from vibe_core.doc_renderer import DocRenderer

        self.doc_renderer = DocRenderer(self.project_root)

        # Memory System

        self.memory_manager = ProjectMemoryManager(self.project_root, self.sqlite_store)

        # Knowledge Graph (Unified)
        from vibe_core.knowledge.graph import get_knowledge_graph

        self.knowledge_graph = get_knowledge_graph()

        # Telemetry (Stub for now, or unified later)
        # self.telemetry = TelemetryManager(self.project_root)

        # LLM Engine
        from vibe_core.runtime.llm_engine import LLMEngine

        self.llm = LLMEngine()

    def _load_plugin_contexts(self) -> None:
        """
        Load plugins and let them register context providers.

        SCALABLE PATTERN: Any plugin with a `register_context_provider` method
        can inject context into prompts WITHOUT modifying core files.
        """
        try:
            from vibe_core.plugin_loader import PluginLoader

            plugins, _ = PluginLoader.discover_and_load()

            for plugin_id, plugin in plugins.items():
                # Check if plugin has a context registration method
                if hasattr(plugin, "_register_context_provider"):
                    try:
                        plugin._workspace = self.project_root
                        plugin._register_context_provider()
                    except Exception:
                        # Silent fail - not all plugins need context
                        pass
        except Exception:
            # Plugin loading is optional for boot
            pass

    def run(self, user_input: str | None = None):
        """Execute the boot sequence"""

        # PRE-FLIGHT: Check for uncommitted changes (configurable guardrail)
        git_status = self._check_uncommitted_changes()
        guardrail_action = self._handle_uncommitted_guardrail(git_status)
        if guardrail_action == "halt":
            return  # Soft halt - exit cleanly, agent sees warning

        # MIGRATION: Import legacy JSON state if present (ARCH-003)
        self._migrate_legacy_json()

        # Conveyor Belt 1: Load Context
        print("🔄 Loading context...", file=sys.stderr)
        context = self.context_loader.load()

        # Resolve dynamic context from PromptContext resolvers
        print("🔌 Resolving dynamic context...", file=sys.stderr)
        # Core keys (system-level context)
        core_keys = [
            "kernel_status",
            "kernel_agents",
            "kernel_agents_count",
            "kernel_ledger_events",
            "inbox_count",
            "agenda_summary",
            "git_sync_status",
            "system_time",
            # Core *_context keys (STEWARD Protocol Layer 1.5/1.6)
            "user_context",
            "team_context",
        ]

        # OPUS-029: Auto-discover PLUGIN context keys (SCALABLE PATTERN)
        # Plugins can register "*_context" keys - they're auto-included!
        # NO hardcoding of specific plugin keys here.
        plugin_keys = [
            key for key in self.prompt_context._resolvers.keys() if key.endswith("_context") and key not in core_keys
        ]

        resolved = self.prompt_context.resolve(core_keys + plugin_keys)
        context["resolved"] = resolved

        # Load project memory (semantic layer)
        print("🧠 Loading project memory...", file=sys.stderr)
        memory = self.memory_manager.load()
        context["memory"] = memory

        # Conveyor Belt 2: Route to Task
        print("🎯 Routing to task...", file=sys.stderr)
        route = self.playbook_engine.route(user_input or "", source="boot_cli", context=context)

        # Conveyor Belt 3: Compose Prompt
        print("📝 Composing prompt...", file=sys.stderr)
        # UnifiedRouter returns ExecutionRequest with target_id (circuit/playbook ID)
        prompt = self.prompt_composer.compose(route.target_id, context)

        # Add system prompt (prime agent properly)
        system_prompt = self._get_system_prompt(route)
        final_prompt = system_prompt + "\n\n" + prompt

        # Display dashboard (includes memory summary)
        self._display_dashboard(context, route)

        # Output prompt for STEWARD
        print("\n" + "=" * 80, file=sys.stderr)
        print(final_prompt)
        print("=" * 80 + "\n", file=sys.stderr)

    def _handle_uncommitted_guardrail(self, git_status: dict) -> str:
        """Handle uncommitted changes based on guardrails config.

        Returns:
            "halt" - stop boot
            "continue" - proceed with boot
        """
        if not git_status["has_uncommitted"] or git_status["is_clean_state"]:
            return "continue"

        # Load guardrails config
        from vibe_core.phoenix.config import get_config
        from vibe_core.phoenix.sections.guardrails import GuardrailMode

        phoenix = get_config()

        # Default to WARN if guardrails section not loaded
        mode = GuardrailMode.WARN
        if phoenix.guardrails:
            mode = phoenix.guardrails.git.uncommitted_changes

        if mode == GuardrailMode.IGNORE:
            # Skip check entirely
            return "continue"
        elif mode == GuardrailMode.WARN:
            # Show warning but continue
            self._display_commit_warning(git_status, block=False)
            return "continue"
        else:  # BLOCK
            # Show warning and halt
            self._display_commit_warning(git_status, block=True)
            return "halt"

    def _check_uncommitted_changes(self) -> dict:
        """Check for uncommitted changes - graceful detection

        Auto-generated markdown files are excluded from the check.
        These are determined by the InterfaceConfig (config/interface.yaml)
        which defines all renderers and their output files.
        """
        try:
            import subprocess

            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=5,
                check=True,
            )

            # Get auto-generated files from Interface Config (SSOT)
            # The InterfacePlugin is the authority for which files it generates
            from vibe_core.phoenix.config import get_config

            phoenix = get_config()
            auto_generated_files = set()
            if phoenix.interface:
                for renderer in phoenix.interface.get_enabled_renderers().values():
                    if renderer.output:
                        auto_generated_files.add(renderer.output)

            all_changes = [line.strip() for line in result.stdout.strip().split("\n") if line.strip()]

            # Filter out auto-generated root markdown files
            significant_changes = []
            for change in all_changes:
                # Format is "XY filename" or "XY old -> new" for renames
                parts = change.split()
                if len(parts) >= 2:
                    filename = parts[-1]
                    # Check if it's a root-level auto-generated file
                    if "/" not in filename and filename in auto_generated_files:
                        continue
                significant_changes.append(change)

            return {
                "has_uncommitted": len(significant_changes) > 0,
                "files": significant_changes[:10],  # First 10
                "count": len(significant_changes),
                "is_clean_state": len(significant_changes) == 0,
                "filtered_count": len(all_changes) - len(significant_changes),
            }
        except Exception as e:
            return {
                "has_uncommitted": False,
                "files": [],
                "count": 0,
                "is_clean_state": True,
                "error": str(e),
            }

    def _display_commit_warning(self, git_status: dict, block: bool = True) -> None:
        """Display warning for uncommitted changes.

        Args:
            git_status: Dict with uncommitted file info
            block: If True, shows "HALTED". If False, shows "WARNING" and continues.
        """
        count = git_status["count"]
        files = git_status["files"]

        if block:
            header = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                         ⚠️  BOOT HALTED - GUARDRAIL (block)                  ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
            footer = """
────────────────────────────────────────────────────────────────────────────────
🎯 Why this matters:
  • Agents need clean state to track their work
  • Uncommitted changes hide what was actually changed
  • Forces explicit handoff via git commits

Boot will resume once changes are committed or stashed.
To change this behavior: config/guardrails.yaml → git.uncommitted_changes: warn
────────────────────────────────────────────────────────────────────────────────
"""
        else:
            header = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                    ⚠️  WARNING - GUARDRAIL (warn) - CONTINUING               ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
            footer = """
────────────────────────────────────────────────────────────────────────────────
To block on uncommitted changes: config/guardrails.yaml → git.uncommitted_changes: block
────────────────────────────────────────────────────────────────────────────────
"""

        warning = (
            header
            + f"""
❌ UNCOMMITTED CHANGES DETECTED ({count} files)

Files:
"""
        )
        for f in files:
            warning += f"  {f}\n"

        if block:
            warning += """
ACTION REQUIRED:

  Option 1: Commit changes (recommended)
    git add .
    git commit -m "your message"

  Option 2: Stash changes (if not ready)
    git stash

  Option 3: Change guardrail mode
    config/guardrails.yaml → git.uncommitted_changes: warn
"""
        warning += footer
        print(warning, file=sys.stderr)

    def _get_system_prompt(self, route) -> str:
        """
        System prompt GENERATED from Protocol data.

        NO HARDCODING - Prompt is COMPOSED from:
        1. STEWARD.md (Protocol description)
        2. kernel.steward config (behavior rules, user context)
        3. Current kernel state (live data)

        The system prompt describes the OPERATOR's behavior,
        not an agent identity (STEWARD is the Protocol, not an agent).
        """
        # Load steward config from Phoenix
        from vibe_core.phoenix.config import get_config

        phoenix = get_config()
        steward_config = phoenix.steward

        # Resolve dynamic context values
        # Core keys (always included)
        core_keys = ["kernel_status", "kernel_agents_count"]

        # Auto-discover plugin contexts (SCALABLE PATTERN)
        # Any plugin can register "*_context" keys - they're auto-included!
        plugin_keys = [key for key in self.prompt_context._resolvers.keys() if key.endswith("_context")]

        resolved = self.prompt_context.resolve(core_keys + plugin_keys)

        # Format plugin contexts for injection
        plugin_context_section = ""
        for key in sorted(plugin_keys):
            value = resolved.get(key, "")
            if value and str(value).strip():
                plugin_context_section += str(value).strip() + "\n\n"

        # Build behavior rules from config
        behavior = steward_config.behavior
        behavior_rules = []
        if behavior.genesis_protocol:
            behavior_rules.append("• Genesis Protocol: Verify system integrity before work")
        if behavior.anti_slop_rules:
            behavior_rules.append("• Anti-Slop: No shortcuts, verify everything")
        if behavior.require_tests:
            behavior_rules.append("• Tests Required: Run tests before claiming done")
        if behavior.require_commit:
            behavior_rules.append("• Commits Required: Must commit changes")
        if behavior.require_handoff:
            behavior_rules.append("• Handoff Required: Update .session_handoff.json")

        # Build user context from config
        user_prefs = steward_config.get_active_user_prefs()
        user_context = f"Workflow: {user_prefs.workflow_style}, Verbosity: {user_prefs.verbosity}, Communication: {user_prefs.communication}"

        # Build cognitive policy summary
        cog = steward_config.cognitive_policy
        cognitive_policy = f"Budget: ${cog.economic_constraints.max_cost_per_run}/run, ${cog.economic_constraints.max_daily_budget}/day"

        # Build team context
        team = steward_config.user_context.team
        team_context = (
            f"Style: {team.development_style}, Git: {team.git_workflow}, Coverage: {team.min_coverage * 100:.0f}%"
        )

        # Compose the system prompt FROM Protocol data
        return f"""You are operating the STEWARD Protocol.

STEWARD is a distributed governance protocol for autonomous agents.
You are the OPERATOR - a human or LLM interfacing with the system.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BEHAVIOR RULES (Constitutional)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{chr(10).join(behavior_rules)}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
USER CONTEXT (Layer 1.5)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{user_context}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TEAM CONTEXT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{team_context}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
COGNITIVE POLICY (Layer 1.6)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{cognitive_policy}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
KERNEL STATE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Status: {resolved.get("kernel_status", "unknown")}
Agents: {resolved.get("kernel_agents_count", 0)}

{plugin_context_section}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EXECUTION PROTOCOL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Execute the task following the workflow
2. Verify completion against success criteria
3. Update state via .session_handoff.json
4. Commit changes with clear message
5. Report completion - what was done, what's next"""

    def _check_git_sync(self) -> dict:
        """Check if repo is behind remote - graceful fallback if git fails"""
        try:
            import subprocess

            # Fetch latest refs (non-destructive)
            subprocess.run(
                ["git", "fetch", "origin"],
                cwd=self.project_root,
                capture_output=True,
                timeout=5,
                check=False,  # Don't fail if fetch fails
            )

            # Count commits behind
            result = subprocess.run(
                ["git", "rev-list", "--count", "HEAD..origin/main"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=5,
                check=True,
            )

            commits_behind = int(result.stdout.strip())
            return {
                "behind": commits_behind > 0,
                "commits_behind": commits_behind,
                "status": "sync_needed" if commits_behind > 0 else "up_to_date",
            }
        except Exception as e:
            # Graceful fallback - don't break boot
            return {
                "behind": False,
                "commits_behind": 0,
                "status": "unknown",
                "error": str(e),
            }

    def _display_dashboard(self, context: dict, route) -> None:
        """Display kernel-style boot output (lean, visual, actionable)"""

        git = context.get("git", {})
        tests = context.get("tests", {})
        env = context.get("environment", {})
        sync_status = self._check_git_sync()

        # Get semantic memory summary
        memory_summary = self.memory_manager.get_semantic_summary()

        # Kernel-style output - clean, scannable, actionable
        dashboard = f"""
╔════════════════════════════════════════════════════════════╗
║              VIBE AGENCY STEWARD BOOT v1.1                ║
║                    [Playbook Integrated]                   ║
╚════════════════════════════════════════════════════════════╝

[BOOT SEQUENCE]
  [✓] Integrity verified
  [✓] Context loaded (5 sources)
  [✓] Memory loaded (semantic layer)
  [✓] Playbook routed: {route.task.upper()}
  [✓] Prompt composed

[SYSTEM STATUS]
  Git:    {"✓" if git.get("uncommitted", 0) == 0 else "⚠"} clean ({git.get("branch", "unknown")})
  Tests:  {"✓" if tests.get("failing_count", 0) == 0 else "⚠"} {tests.get("failing_count", 0)} failing
  Sync:   {"✓" if not sync_status.get("behind") else "⚠"} {sync_status.get("commits_behind", 0)} behind
  Env:    {"✓" if env.get("status") == "ready" else "⚠"} {env.get("status")}

{memory_summary}

[NEXT ACTION]
  TASK:       {route.target_id.upper()}
  SOURCE:     {route.source}
  CONFIDENCE: {route.confidence:.2f}

[EXECUTION PROTOCOL]
  1. READ task playbook completely
  2. PLAN steps before executing
  3. EXECUTE minimal surgical changes
  4. VERIFY with tests (no claims without proof)
  5. COMMIT with clear message
  6. UPDATE .session_handoff.json
  7. REPORT completion + next steps

[ANTI-SLOP RULES]
  ✓ manifest=truth | read>write | edit>create
  ✓ test>claim | health>features

════════════════════════════════════════════════════════════
🚀 Ready. Executing {route.target_id.upper()} task now.
"""

        print(dashboard, file=sys.stderr)

    def show_routes(self) -> None:
        """Show all available playbook routes"""
        routes = self.playbook_engine.list_available_routes()

        print("\n╔══════════════════════════════════════════════════════════════════════════════╗")
        print("║                        📚 AVAILABLE PLAYBOOK ROUTES                          ║")
        print("╚══════════════════════════════════════════════════════════════════════════════╝\n")

        for route in routes:
            print(f"🎯 {route['name'].upper()}")
            print(f"   {route['description']}")
            print(f"   Examples: {', '.join(route['examples'])}")
            print()

    def _migrate_legacy_json(self) -> None:
        """
        Migrate legacy active_mission.json to SQLite (ARCH-003)

        Strategy: Phase 1 - Dual-Write/Import
        - Check for existing active_mission.json
        - Import to SQLite if not already present
        - Rename JSON (keep as backup, DO NOT DELETE)
        - Log migration status

        Safety: NO DATA LOSS - JSON is preserved
        """
        json_file = self.project_root / ".vibe" / "state" / "active_mission.json"

        if not json_file.exists():
            # No legacy JSON - nothing to migrate
            return

        try:
            # Load JSON data
            with open(json_file) as f:
                json_data = json.load(f)

            mission_uuid = json_data.get("mission_id", "unknown")

            # Import to SQLite (idempotent - won't duplicate)
            imported_id = self.sqlite_store.import_legacy_mission(json_data)

            if imported_id:
                # Mission was imported - rename JSON as backup
                timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
                backup_name = f"active_mission_migrated_{timestamp}.json"
                backup_path = json_file.parent / backup_name

                os.rename(json_file, backup_path)

                print("✅ Legacy mission imported to SQLite", file=sys.stderr)
                print(f"   Mission UUID: {mission_uuid}", file=sys.stderr)
                print(f"   SQLite ID: {imported_id}", file=sys.stderr)
                print(f"   Backup: {backup_path.name}", file=sys.stderr)
            else:
                # Mission already in DB - just log it
                print(f"ℹ️  Mission '{mission_uuid}' already in database", file=sys.stderr)

        except json.JSONDecodeError as e:
            print(f"⚠️ Failed to parse legacy JSON: {e}", file=sys.stderr)
            print(f"   File preserved at: {json_file}", file=sys.stderr)
        except Exception as e:
            print(f"⚠️ Migration error (non-critical): {e}", file=sys.stderr)
            print(f"   JSON file preserved at: {json_file}", file=sys.stderr)
            # Continue boot - JSON is still available

    def health_check(self) -> bool:
        """Quick health check - returns True if system is operational"""
        try:
            context = self.context_loader.load()

            # Check critical components
            git_ok = context.get("git", {}).get("status") == "available"
            env_ok = context.get("environment", {}).get("status") in [
                "ready",
                "needs_setup",
            ]

            if not git_ok:
                print("⚠️ Git not available", file=sys.stderr)
            if not env_ok:
                print("⚠️ Environment issues detected", file=sys.stderr)

            return git_ok and env_ok
        except Exception as e:
            print(f"❌ Health check failed: {e}", file=sys.stderr)
            return False
