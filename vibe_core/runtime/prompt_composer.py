"""Prompt Composer - Conveyor Belt #3: Compose final prompt

Composes task playbook + context → enriched prompt for STEWARD
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "brahma"
__position__ = 1
__genesis__ = "0x8ebca34e"  # GenesisByte: parampara % 37 == 0

from pathlib import Path
from typing import Any


class PromptComposer:
    """Composes task playbook + context → enriched prompt"""

    def __init__(self, playbook_tasks_dir: Path = None):
        self.tasks_dir = playbook_tasks_dir or Path(__file__).parent.parent / "playbook" / "tasks"

    def compose(self, task: str, context: dict[str, Any]) -> str:
        """Compose final enriched prompt"""

        # Load base task playbook
        task_md = self._load_task(task)

        # Inject context
        enriched = self._inject_context(task_md, context)

        # Add boot prompt
        final = self._add_boot_prompt(enriched, context)

        return final

    def _load_task(self, task: str) -> str:
        """Load task playbook markdown"""
        task_file = self.tasks_dir / f"{task}.md"

        if not task_file.exists():
            # Fallback to generic task
            return f"""# {task.upper()} Task

## Mission
Execute {task} task.

## Workflow
1. Understand current context
2. Execute task
3. Verify completion

## Success Criteria
✅ Task completed
✅ Tests passing
✅ Changes documented
"""

        with open(task_file) as f:
            return f.read()

    def _inject_context(self, task_md: str, context: dict[str, Any]) -> str:
        """Replace context placeholders in task markdown"""

        # Build replacement map
        replacements = {}

        # Session context
        session = context.get("session", {})
        replacements["${session.phase}"] = session.get("phase", "UNKNOWN")
        replacements["${session.last_task}"] = session.get("last_task", "none")
        replacements["${session.backlog_item}"] = session.get("backlog_item", "none")
        replacements["${session.requirements}"] = ", ".join(session.get("backlog", [])[:3]) or "none"
        replacements["${session.doc_audience}"] = "developers"  # Default
        replacements["${session.focus_area}"] = context.get("manifest", {}).get("focus_area", "general")

        # Git context
        git = context.get("git", {})
        replacements["${git.branch}"] = git.get("branch", "unknown")
        replacements["${git.uncommitted}"] = str(git.get("uncommitted", 0))
        replacements["${git.last_commit}"] = git.get("last_commit", "none")
        replacements["${git.recent_commits}"] = "\n".join(git.get("recent_commits", [])[:3])

        # Test context
        tests = context.get("tests", {})
        failing_tests = tests.get("failing", [])
        replacements["${tests.failing}"] = ", ".join(failing_tests[:5]) if failing_tests else "none"
        replacements["${tests.failing_count}"] = str(len(failing_tests))
        replacements["${tests.status}"] = "passing" if not failing_tests else f"{len(failing_tests)} failing"
        replacements["${tests.errors}"] = ", ".join(tests.get("errors", [])[:3]) or "none"

        # Manifest context
        manifest = context.get("manifest", {})
        replacements["${manifest.project_type}"] = manifest.get("project_type", "unknown")
        replacements["${manifest.test_framework}"] = manifest.get("test_framework", "pytest")
        replacements["${manifest.docs_path}"] = manifest.get("docs_path", "docs/")
        replacements["${manifest.structure}"] = str(manifest.get("structure", {}))

        # Apply replacements
        result = task_md
        for placeholder, value in replacements.items():
            result = result.replace(placeholder, value)

        # Add context section
        context_section = self._format_context_section(context)
        result += "\n\n" + context_section

        return result

    def _format_context_section(self, context: dict[str, Any]) -> str:
        """Format current context as markdown section"""
        session = context.get("session", {})
        git = context.get("git", {})
        tests = context.get("tests", {})
        env = context.get("environment", {})
        memory = context.get("memory", {})
        resolved = context.get("resolved", {})

        failing_count = tests.get("failing_count", 0)
        test_status = "✅ Passing" if failing_count == 0 else f"❌ {failing_count} Failing"

        git_status = "✅ Clean" if git.get("uncommitted", 0) == 0 else f"⚠️ {git.get('uncommitted')} uncommitted"

        env_status = "✅ Ready" if env.get("status") == "ready" else f"⚠️ {env.get('status')}"

        # Build semantic context from memory
        semantic_context = self._format_semantic_context(memory)

        # Build kernel state from resolved context
        kernel_context = self._format_kernel_context(resolved)

        # OPUS-029: Auto-include plugin contexts (SCALABLE PATTERN)
        # Any plugin can register "*_context" keys and they'll be included
        plugin_contexts = self._format_plugin_contexts(resolved)

        return f"""---

## 📊 CURRENT CONTEXT

**Project State:**
- Phase: {session.get("phase", "UNKNOWN")}
- Last Task: {session.get("last_task", "none")}
- Branch: {git.get("branch", "unknown")}

**Status:**
- Tests: {test_status}
- Git: {git_status}
- Environment: {env_status}

{kernel_context}

{plugin_contexts}

{semantic_context}

**Backlog:**
{self._format_backlog(session.get("backlog", []))}

**Recent Commits:**
{self._format_commits(git.get("recent_commits", []))}

---
"""

    def _format_kernel_context(self, resolved: dict) -> str:
        """Format kernel state from resolved PromptContext values"""
        if not resolved:
            return ""

        kernel_status = resolved.get("kernel_status", "not_running")
        if kernel_status == "not_running":
            return "**🔧 Kernel:** not running"

        agents = resolved.get("kernel_agents", "none")
        agents_count = resolved.get("kernel_agents_count", "0")
        ledger_events = resolved.get("kernel_ledger_events", "0")
        inbox_count = resolved.get("inbox_count", "0")

        return f"""**🔧 Kernel:**
- Status: {kernel_status}
- Agents: {agents_count} ({agents})
- Ledger Events: {ledger_events}
- Inbox: {inbox_count} message(s)"""

    def _format_plugin_contexts(self, resolved: dict) -> str:
        """
        Format plugin-provided contexts (OPUS-029 SCALABLE PATTERN).

        Any plugin can register a PromptContext resolver with a key ending in
        "_context" and it will be automatically included here. This allows
        plugin context injection WITHOUT modifying core files.

        Convention:
        - Key pattern: *_context (e.g., opus_context, metrics_context)
        - Value: Pre-formatted markdown string ready for injection
        - Excluded: kernel_* keys (handled separately)

        Args:
            resolved: Dict of resolved PromptContext values

        Returns:
            Formatted markdown string with all plugin contexts
        """
        if not resolved:
            return ""

        # Collect plugin context keys (ending in _context, excluding kernel_*)
        plugin_keys = [key for key in resolved.keys() if key.endswith("_context") and not key.startswith("kernel_")]

        if not plugin_keys:
            return ""

        # Plugin contexts are already formatted - just concatenate
        contexts = []
        for key in sorted(plugin_keys):
            value = resolved.get(key, "")
            if value and value.strip():
                contexts.append(value.strip())

        return "\n\n".join(contexts)

    def _format_semantic_context(self, memory: dict) -> str:
        """Format semantic memory context for prompt injection"""
        if not memory or not memory.get("narrative"):
            return ""

        trajectory = memory.get("trajectory", {})
        domain = memory.get("domain", {})
        recent_sessions = memory.get("narrative", [])[-3:]
        recent_intents = memory.get("intent_history", [])[-3:]

        context = "**🧠 PROJECT UNDERSTANDING:**\n"

        # Domain & concepts
        if domain.get("type") != "general":
            concepts = ", ".join(domain.get("concepts", [])[:5])
            context += f"- Domain: {domain.get('type')} ({concepts})\n"

        # Current trajectory
        if trajectory:
            completed = ", ".join(trajectory.get("completed", [])[:3]) or "None"
            focus = trajectory.get("current_focus", "unknown")
            context += f"- Progress: Completed [{completed}] → Current focus: {focus}\n"

        # Recent evolution
        if recent_sessions:
            context += "- Recent sessions:\n"
            for s in recent_sessions:
                context += f"  • Session {s['session']}: {s['summary']} ({s.get('phase', 'UNKNOWN')})\n"

        # User intents
        if recent_intents:
            context += "- User intents:\n"
            for intent in recent_intents:
                context += f"  • Session {intent['session']}: {intent['intent']}\n"

        # Concerns
        if domain.get("concerns"):
            concerns = ", ".join(domain["concerns"][:3])
            context += f"- Concerns: {concerns}\n"

        return context

    def _format_backlog(self, backlog: list) -> str:
        """Format backlog items"""
        if not backlog:
            return "- (empty)"
        return "\n".join([f"- {item}" for item in backlog[:5]])

    def _format_commits(self, commits: list) -> str:
        """Format recent commits"""
        if not commits:
            return "- (no commits)"
        return "\n".join([f"- {commit}" for commit in commits[:3]])

    def _add_boot_prompt(self, enriched_task: str, context: dict[str, Any]) -> str:
        """
        Add STEWARD boot prompt wrapper.

        The task content is already enriched with context - just return it.
        System prompt is handled separately in boot_sequence.py.
        """
        # Task is already enriched with context - return as-is
        # System prompt (behavior rules, user context) is handled by boot_sequence._get_system_prompt()
        return enriched_task
