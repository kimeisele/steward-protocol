"""Project Memory - Semantic layer for STEWARD intelligence

Tracks project narrative, domain understanding, evolution, and intent history
across sessions. This is the "brain" that makes STEWARD understand the full picture.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class ProjectMemoryManager:
    """Manages semantic project memory across sessions"""

    def __init__(self, project_root: Path, sqlite_store=None):
        """
        Initialize project memory manager.

        Args:
            project_root: Root directory of the project
            sqlite_store: Optional SQLiteStore instance for dual-write mode (ARCH-003)
        """
        self.project_root = project_root
        self.memory_file = project_root / ".vibe" / "project_memory.json"
        self.sqlite_store = sqlite_store
        self._ensure_vibe_dir()

    def _ensure_vibe_dir(self):
        """Ensure .vibe directory exists"""
        vibe_dir = self.project_root / ".vibe"
        vibe_dir.mkdir(exist_ok=True)

    def load(self) -> dict[str, Any]:
        """Load project memory (creates default if doesn't exist)"""
        if not self.memory_file.exists():
            return self._create_default_memory()

        try:
            with open(self.memory_file) as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            # Corrupted file - fallback to default
            return self._create_default_memory()

    def save(self, memory: dict[str, Any], mission_id: int | None = None):
        """
        Save project memory to disk (and optionally to SQLite).

        Args:
            memory: Project memory dict
            mission_id: Optional mission ID for dual-write to SQLite (ARCH-003)
        """
        self._ensure_vibe_dir()

        # Write to JSON (source of truth in Shadow Mode Phase 1)
        with open(self.memory_file, "w") as f:
            json.dump(memory, f, indent=2)

        # ARCH-003: Dual Write Mode - also write to SQLite if mission_id provided
        if self.sqlite_store and mission_id:
            try:
                from datetime import datetime

                timestamp = datetime.utcnow().isoformat() + "Z"
                self.sqlite_store._map_project_memory_to_sql(memory, mission_id, timestamp)
                logger.debug(f"✅ Dual-write project memory to SQLite: mission_id={mission_id}")
            except Exception as e:
                # Non-fatal - JSON is source of truth in Shadow Mode Phase 1
                logger.warning(f"⚠️ SQLite dual-write for project memory failed (non-fatal): {e}")

    def update_after_session(
        self,
        session_summary: str,
        context: dict[str, Any],
        user_input: str = "",
        commits: list[str] = None,
    ):
        """Update memory after a session completes"""
        memory = self.load()

        # Add session to narrative
        session_num = len(memory["narrative"]) + 1
        memory["narrative"].append(
            {
                "session": session_num,
                "summary": session_summary,
                "date": datetime.now().isoformat(),
                "phase": context.get("session", {}).get("phase", "UNKNOWN"),
            }
        )

        # Extract and track intents from user input
        intents = self._extract_intents(user_input, session_num)
        memory["intent_history"].extend(intents)

        # Update trajectory based on context
        self._update_trajectory(memory, context, commits or [])

        # Update domain understanding
        self._update_domain(memory, context, user_input)

        # Trim history if too long (keep last 50 sessions)
        if len(memory["narrative"]) > 50:
            memory["narrative"] = memory["narrative"][-50:]
        if len(memory["intent_history"]) > 100:
            memory["intent_history"] = memory["intent_history"][-100:]

        self.save(memory)

    def get_semantic_summary(self) -> str:
        """Generate human-readable summary of project memory"""
        memory = self.load()

        if not memory["narrative"]:
            return "📝 No session history yet - this is the first session."

        recent = memory["narrative"][-5:]
        trajectory = memory["trajectory"]
        domain = memory["domain"]

        summary = f"""🧠 PROJECT MEMORY SUMMARY

📖 Project: {memory.get("project_id", "Unknown")}
🎯 Domain: {domain.get("type", "general")} ({len(domain.get("concepts", []))} concepts)

📈 TRAJECTORY:
  Phase: {trajectory["phase"]}
  Focus: {trajectory["current_focus"]}
  Completed: {", ".join(trajectory.get("completed", []))}
  Blockers: {", ".join(trajectory.get("blockers", [])) or "None"}

📚 RECENT SESSIONS ({len(recent)} of {len(memory["narrative"])}):
"""
        for s in recent:
            summary += f"  • Session {s['session']}: {s['summary']} ({s.get('phase', 'UNKNOWN')})\n"

        if memory["intent_history"]:
            recent_intents = memory["intent_history"][-3:]
            summary += "\n💡 RECENT INTENTS:\n"
            for intent in recent_intents:
                summary += f"  • Session {intent['session']}: {intent['intent']}\n"

        if domain.get("concerns"):
            summary += "\n⚠️  USER CONCERNS:\n"
            for concern in domain["concerns"][:3]:
                summary += f"  • {concern}\n"

        return summary

    def _create_default_memory(self) -> dict[str, Any]:
        """Create default memory structure"""
        return {
            "_schema_version": "1.0",
            "_created": datetime.now().isoformat(),
            "project_id": self._infer_project_id(),
            "narrative": [],
            "domain": {
                "type": "general",
                "concepts": [],
                "concerns": [],
            },
            "trajectory": {
                "phase": "PLANNING",
                "completed": [],
                "current_focus": "initialization",
                "blockers": [],
            },
            "intent_history": [],
        }

    def _infer_project_id(self) -> str:
        """Infer project ID from manifest or directory name"""
        manifest_file = self.project_root / "project_manifest.json"
        if manifest_file.exists():
            try:
                with open(manifest_file) as f:
                    manifest = json.load(f)
                    return manifest.get("project_id", self.project_root.name)
            except (json.JSONDecodeError, OSError):
                pass
        return self.project_root.name

    def _extract_intents(self, user_input: str, session_num: int) -> list[dict]:
        """Extract user intents from input using keyword matching"""
        intents = []
        user_lower = user_input.lower()

        # Payment/billing related
        if any(kw in user_lower for kw in ["payment", "stripe", "billing", "checkout"]):
            intents.append(
                {"session": session_num, "intent": "payment integration", "confidence": "high"}
            )

        # Testing related
        if any(kw in user_lower for kw in ["test", "pytest", "failing test"]):
            intents.append(
                {"session": session_num, "intent": "fix failing tests", "confidence": "high"}
            )

        # Deployment related
        if any(kw in user_lower for kw in ["deploy", "production", "release"]):
            intents.append({"session": session_num, "intent": "deployment", "confidence": "high"})

        # Documentation
        if any(kw in user_lower for kw in ["document", "readme", "docs"]):
            intents.append(
                {"session": session_num, "intent": "documentation", "confidence": "high"}
            )

        # Refactoring
        if any(kw in user_lower for kw in ["refactor", "cleanup", "improve"]):
            intents.append(
                {"session": session_num, "intent": "refactoring", "confidence": "medium"}
            )

        # Bug fixing
        if any(kw in user_lower for kw in ["bug", "fix", "error", "issue"]):
            intents.append({"session": session_num, "intent": "bug fixing", "confidence": "high"})

        return intents

    def _update_trajectory(self, memory: dict, context: dict, commits: list[str]):
        """Update project trajectory based on context"""
        trajectory = memory["trajectory"]
        session = context.get("session", {})

        # Update phase
        current_phase = session.get("phase", trajectory["phase"])
        if current_phase != trajectory["phase"]:
            # Phase changed - mark old phase as completed
            if trajectory["phase"] not in trajectory["completed"]:
                trajectory["completed"].append(trajectory["phase"])
            trajectory["phase"] = current_phase

        # Update focus from context
        if session.get("last_task"):
            trajectory["current_focus"] = session["last_task"]

        # Track blockers from test failures
        tests = context.get("tests", {})
        if tests.get("failing"):
            trajectory["blockers"] = [
                f"{len(tests['failing'])} failing tests in {tests.get('framework', 'pytest')}"
            ]
        else:
            trajectory["blockers"] = []

    def _update_domain(self, memory: dict, context: dict, user_input: str):
        """Update domain understanding from context and user input"""
        domain = memory["domain"]
        manifest = context.get("manifest", {})

        # Infer domain type from manifest
        if manifest.get("project_type"):
            domain["type"] = manifest["project_type"]

        # Extract concepts from user input
        user_lower = user_input.lower()
        concept_keywords = {
            "booking": ["booking", "reservation", "schedule"],
            "payment": ["payment", "stripe", "billing", "checkout"],
            "authentication": ["auth", "login", "user", "signup"],
            "api": ["api", "rest", "graphql", "endpoint"],
            "database": ["database", "sql", "postgres", "migration"],
            "testing": ["test", "pytest", "coverage"],
        }

        for concept, keywords in concept_keywords.items():
            if any(kw in user_lower for kw in keywords):
                if concept not in domain["concepts"]:
                    domain["concepts"].append(concept)

        # Extract concerns (PCI, security, performance, etc.)
        concern_keywords = {
            "PCI compliance": ["pci", "compliance", "security"],
            "performance": ["performance", "slow", "optimize", "speed"],
            "scalability": ["scale", "scaling", "load"],
            "data privacy": ["privacy", "gdpr", "data protection"],
        }

        for concern, keywords in concern_keywords.items():
            if any(kw in user_lower for kw in keywords):
                if concern not in domain["concerns"]:
                    domain["concerns"].append(concern)
