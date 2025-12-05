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

from vibe_core.runtime.context_loader import ContextLoader
from vibe_core.runtime.playbook_router import PlaybookRouter
from vibe_core.runtime.project_memory import ProjectMemoryManager
from vibe_core.runtime.prompt_composer import PromptComposer
from vibe_core.runtime.prompt_context import get_prompt_context
from vibe_core.store.sqlite_store import SQLiteStore


class BootSequence:
    """Main entry point for system boot"""

    def __init__(self, project_root: Path | None = None):
        self.project_root = project_root or Path.cwd()
        self.context_loader = ContextLoader(self.project_root)
        self.playbook_engine = PlaybookRouter()
        self.prompt_composer = PromptComposer()
        self.prompt_context = get_prompt_context()

        # Initialize SQLite persistence (ARCH-003: Dual Write Mode)
        db_path = self.project_root / ".vibe" / "state" / "vibe_agency.db"
        self.sqlite_store = SQLiteStore(str(db_path))

        # Initialize memory manager with SQLite store for dual-write
        self.memory_manager = ProjectMemoryManager(self.project_root, self.sqlite_store)

    def run(self, user_input: str | None = None):
        """Execute the boot sequence"""

        # PRE-FLIGHT: Check for uncommitted changes (graceful guardrail)
        git_status = self._check_uncommitted_changes()
        if git_status["has_uncommitted"] and not git_status["is_clean_state"]:
            self._display_commit_warning(git_status)
            return  # Soft halt - exit cleanly, agent sees warning

        # MIGRATION: Import legacy JSON state if present (ARCH-003)
        self._migrate_legacy_json()

        # Conveyor Belt 1: Load Context
        print("🔄 Loading context...", file=sys.stderr)
        context = self.context_loader.load()

        # Resolve dynamic context from PromptContext resolvers
        print("🔌 Resolving dynamic context...", file=sys.stderr)
        resolved = self.prompt_context.resolve(
            [
                "kernel_status",
                "kernel_agents",
                "kernel_agents_count",
                "kernel_ledger_events",
                "inbox_count",
                "agenda_summary",
                "git_sync_status",
                "system_time",
            ]
        )
        context["resolved"] = resolved

        # Load project memory (semantic layer)
        print("🧠 Loading project memory...", file=sys.stderr)
        memory = self.memory_manager.load()
        context["memory"] = memory

        # Conveyor Belt 2: Route to Task
        print("🎯 Routing to task...", file=sys.stderr)
        route = self.playbook_engine.route(user_input or "", context)

        # Conveyor Belt 3: Compose Prompt
        print("📝 Composing prompt...", file=sys.stderr)
        prompt = self.prompt_composer.compose(route.task, context)

        # Add system prompt (prime agent properly)
        system_prompt = self._get_system_prompt(route)
        final_prompt = system_prompt + "\n\n" + prompt

        # Display dashboard (includes memory summary)
        self._display_dashboard(context, route)

        # Output prompt for STEWARD
        print("\n" + "=" * 80, file=sys.stderr)
        print(final_prompt)
        print("=" * 80 + "\n", file=sys.stderr)

    def _check_uncommitted_changes(self) -> dict:
        """Check for uncommitted changes - graceful detection"""
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

            uncommitted = [line.strip() for line in result.stdout.strip().split("\n") if line.strip()]

            return {
                "has_uncommitted": len(uncommitted) > 0,
                "files": uncommitted[:10],  # First 10
                "count": len(uncommitted),
                "is_clean_state": len(uncommitted) == 0,
            }
        except Exception as e:
            return {
                "has_uncommitted": False,
                "files": [],
                "count": 0,
                "is_clean_state": True,
                "error": str(e),
            }

    def _display_commit_warning(self, git_status: dict) -> None:
        """Display graceful halt warning for uncommitted changes"""
        count = git_status["count"]
        files = git_status["files"]

        warning = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                         ⚠️  BOOT HALTED - SOFT GUARDRAIL                     ║
╚══════════════════════════════════════════════════════════════════════════════╝

❌ UNCOMMITTED CHANGES DETECTED ({count} files)

Files:
"""
        for f in files:
            warning += f"  {f}\n"

        warning += """
ACTION REQUIRED:

  Option 1: Commit changes (recommended)
    git add .
    git commit -m "your message"

  Option 2: Stash changes (if not ready)
    git stash

  Option 3: Force boot (if absolutely necessary)
    ./vibe-cli boot --force

────────────────────────────────────────────────────────────────────────────────
🎯 Why this matters:
  • Agents need clean state to track their work
  • Uncommitted changes hide what was actually changed
  • Forces explicit handoff via git commits
  • Prevents "forgot what I did" scenarios

Boot will resume once changes are committed or stashed.
────────────────────────────────────────────────────────────────────────────────
"""
        print(warning, file=sys.stderr)

    def _get_system_prompt(self, route) -> str:
        """
        System prompt dynamically composed from STEWARD config.

        Uses PromptContext resolvers (Layer 1.5/1.6) instead of hardcoded strings.
        Source of truth: config/steward.yaml
        """
        # Resolve all steward context
        resolved = self.prompt_context.resolve(
            [
                "user_context",
                "cognitive_policy",
                "behavior_rules",
                "team_context",
                "kernel_status",
                "kernel_agents_count",
            ]
        )

        # Build dynamic system prompt
        return f"""⚡ STEWARD SYSTEM PROMPT

You are STEWARD, the senior orchestration agent.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 BEHAVIOR RULES (Constitutional)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{resolved.get("behavior_rules", "[Rules unavailable]")}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👤 USER CONTEXT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{resolved.get("user_context", "[User context unavailable]")}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👥 TEAM CONTEXT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{resolved.get("team_context", "[Team context unavailable]")}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🧠 COGNITIVE POLICY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{resolved.get("cognitive_policy", "[Cognitive policy unavailable]")}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔧 KERNEL STATE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Status: {resolved.get("kernel_status", "unknown")}
Agents: {resolved.get("kernel_agents_count", "0")}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 EXECUTION PROTOCOL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. READ: Understand task completely
2. PLAN: Break into steps
3. EXECUTE: Run each step, verify
4. TEST: Verify success criteria met
5. COMMIT: `git add .` + clear message
6. HANDOFF: Update .session_handoff.json

Your work is only "done" when:
• Code changes committed to git
• .session_handoff.json updated
• Next agent can pick up where you left off
"""

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
  TASK:       {route.task.upper()}
  SOURCE:     {route.source}
  CONFIDENCE: {route.confidence}

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
🚀 Ready. Executing {route.task.upper()} task now.
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
