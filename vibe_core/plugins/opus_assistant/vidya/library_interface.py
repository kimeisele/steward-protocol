"""
VIDYA Library Interface - Local Knowledge Orchestration.

OPUS-033: Orchestration over Implementation

"Before building something new, check if we already know how."
    - Senior Partner Directive

This module provides access to the local knowledge directory:
- Indexes existing blueprints and capabilities
- Searches for relevant prior art
- Stores successful patterns for reuse

Note: There's no existing "Librarian" cartridge, so this module
provides lightweight local file operations. For web research,
use ResearchInterface instead.

Directory Structure:
    knowledge/
    ├── capabilities/     # Stored capability blueprints
    ├── patterns/         # Design patterns and templates
    ├── failures/         # Failed attempts (for learning)
    └── drafts/           # Work in progress
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prahlada"
__position__ = 9
__genesis__ = "0xa06b0246"  # GenesisByte: parampara % 37 == 0

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("VIDYA.Library")


@dataclass
class Blueprint:
    """A stored capability blueprint."""

    name: str
    description: str
    code: Dict[str, str]  # filename -> content
    created_at: str
    tags: List[str] = field(default_factory=list)
    success_rate: float = 0.0
    usage_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "code": self.code,
            "created_at": self.created_at,
            "tags": self.tags,
            "success_rate": self.success_rate,
            "usage_count": self.usage_count,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Blueprint":
        """Create from dictionary."""
        return cls(
            name=data["name"],
            description=data.get("description", ""),
            code=data.get("code", {}),
            created_at=data.get("created_at", datetime.utcnow().isoformat()),
            tags=data.get("tags", []),
            success_rate=data.get("success_rate", 0.0),
            usage_count=data.get("usage_count", 0),
        )


@dataclass
class LibrarySearchResult:
    """Result from a library search."""

    query: str
    found: bool
    blueprints: List[Blueprint] = field(default_factory=list)
    total_count: int = 0


class LibraryInterface:
    """
    Orchestration layer for local knowledge access.

    This class manages the knowledge/ directory:
    - Index and search existing blueprints
    - Store new successful patterns
    - Track failures for learning

    Philosophy: Learn from history. Don't repeat failures.
    """

    def __init__(self, workspace: Optional[Path] = None):
        """
        Initialize library interface.

        Args:
            workspace: Workspace root (defaults to cwd)
        """
        self._workspace = workspace or Path.cwd()
        self._knowledge_dir = self._workspace / "knowledge"
        self._index: Dict[str, Blueprint] = {}
        self._indexed = False

    def _ensure_dirs(self) -> None:
        """Ensure knowledge directories exist."""
        dirs = [
            self._knowledge_dir,
            self._knowledge_dir / "capabilities",
            self._knowledge_dir / "patterns",
            self._knowledge_dir / "failures",
            self._knowledge_dir / "drafts",
        ]
        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)

    def _ensure_indexed(self) -> None:
        """Ensure the library is indexed."""
        if self._indexed:
            return

        self._ensure_dirs()
        self._build_index()
        self._indexed = True

    def _build_index(self) -> None:
        """Build index of all blueprints."""
        self._index.clear()

        # Index capabilities
        cap_dir = self._knowledge_dir / "capabilities"
        if cap_dir.exists():
            for bp_file in cap_dir.glob("*.json"):
                try:
                    data = json.loads(bp_file.read_text())
                    blueprint = Blueprint.from_dict(data)
                    self._index[blueprint.name] = blueprint
                except Exception as e:
                    logger.warning(f"Could not load blueprint {bp_file}: {e}")

        # Index patterns
        pat_dir = self._knowledge_dir / "patterns"
        if pat_dir.exists():
            for bp_file in pat_dir.glob("*.json"):
                try:
                    data = json.loads(bp_file.read_text())
                    blueprint = Blueprint.from_dict(data)
                    self._index[f"pattern:{blueprint.name}"] = blueprint
                except Exception as e:
                    logger.warning(f"Could not load pattern {bp_file}: {e}")

        logger.debug(f"📚 Library indexed: {len(self._index)} blueprints")

    def search(self, query: str, tags: Optional[List[str]] = None) -> LibrarySearchResult:
        """
        Search the library for relevant blueprints.

        Args:
            query: Search query (searches name and description)
            tags: Optional tag filter

        Returns:
            LibrarySearchResult with matching blueprints
        """
        self._ensure_indexed()

        query_lower = query.lower()
        matches = []

        for name, blueprint in self._index.items():
            # Check name match
            if query_lower in name.lower():
                matches.append(blueprint)
                continue

            # Check description match
            if query_lower in blueprint.description.lower():
                matches.append(blueprint)
                continue

            # Check tag match
            if tags:
                if any(t in blueprint.tags for t in tags):
                    matches.append(blueprint)

        return LibrarySearchResult(
            query=query,
            found=len(matches) > 0,
            blueprints=matches,
            total_count=len(matches),
        )

    def get_blueprint(self, name: str) -> Optional[Blueprint]:
        """
        Get a specific blueprint by name.

        Args:
            name: Blueprint name

        Returns:
            Blueprint or None if not found
        """
        self._ensure_indexed()
        return self._index.get(name)

    def store_blueprint(
        self,
        name: str,
        description: str,
        code: Dict[str, str],
        tags: Optional[List[str]] = None,
        category: str = "capabilities",
    ) -> bool:
        """
        Store a new blueprint.

        Args:
            name: Blueprint name
            description: Description
            code: Dict of filename -> content
            tags: Optional tags
            category: "capabilities", "patterns", or "failures"

        Returns:
            True if stored successfully
        """
        self._ensure_dirs()

        blueprint = Blueprint(
            name=name,
            description=description,
            code=code,
            created_at=datetime.utcnow().isoformat(),
            tags=tags or [],
        )

        # Determine target directory
        if category == "capabilities":
            target_dir = self._knowledge_dir / "capabilities"
        elif category == "patterns":
            target_dir = self._knowledge_dir / "patterns"
        elif category == "failures":
            target_dir = self._knowledge_dir / "failures"
        else:
            target_dir = self._knowledge_dir / "drafts"

        # Write blueprint
        bp_file = target_dir / f"{name}.json"
        try:
            bp_file.write_text(json.dumps(blueprint.to_dict(), indent=2))
            logger.info(f"📚 Stored blueprint: {name} in {category}")

            # Update index
            key = name if category == "capabilities" else f"{category}:{name}"
            self._index[key] = blueprint

            return True
        except Exception as e:
            logger.error(f"Failed to store blueprint {name}: {e}")
            return False

    def store_draft(
        self,
        name: str,
        code: Dict[str, str],
        description: str = "",
    ) -> Path:
        """
        Store code as a draft (work in progress).

        Args:
            name: Draft name
            code: Dict of filename -> content
            description: Optional description

        Returns:
            Path to draft directory
        """
        self._ensure_dirs()

        draft_dir = self._knowledge_dir / "drafts" / name
        draft_dir.mkdir(parents=True, exist_ok=True)

        # Write code files
        for filename, content in code.items():
            (draft_dir / filename).write_text(content)

        # Write metadata
        meta = {
            "name": name,
            "description": description,
            "created_at": datetime.utcnow().isoformat(),
            "files": list(code.keys()),
        }
        (draft_dir / "draft.json").write_text(json.dumps(meta, indent=2))

        logger.info(f"📝 Stored draft: {name}")
        return draft_dir

    def promote_draft(self, name: str, tags: Optional[List[str]] = None) -> bool:
        """
        Promote a draft to a full capability blueprint.

        Args:
            name: Draft name
            tags: Optional tags

        Returns:
            True if promoted successfully
        """
        draft_dir = self._knowledge_dir / "drafts" / name
        if not draft_dir.exists():
            logger.warning(f"Draft not found: {name}")
            return False

        # Read draft metadata
        meta_file = draft_dir / "draft.json"
        if not meta_file.exists():
            logger.warning(f"Draft metadata not found: {name}")
            return False

        meta = json.loads(meta_file.read_text())

        # Read code files
        code = {}
        for filename in meta.get("files", []):
            file_path = draft_dir / filename
            if file_path.exists():
                code[filename] = file_path.read_text()

        # Store as capability
        success = self.store_blueprint(
            name=name,
            description=meta.get("description", ""),
            code=code,
            tags=tags or [],
            category="capabilities",
        )

        if success:
            # Remove draft
            import shutil

            shutil.rmtree(draft_dir)
            logger.info(f"🎉 Draft promoted to capability: {name}")

        return success

    def record_failure(
        self,
        name: str,
        code: Dict[str, str],
        error: str,
        reason: str = "",
    ) -> bool:
        """
        Record a failed capability attempt (for learning).

        Args:
            name: Capability name
            code: The failed code
            error: Error message
            reason: Why it failed

        Returns:
            True if recorded successfully
        """
        return self.store_blueprint(
            name=f"{name}_failed_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            description=f"FAILED: {error}\nReason: {reason}",
            code=code,
            tags=["failed", "learning"],
            category="failures",
        )

    def has_capability(self, name: str) -> bool:
        """
        Check if a capability already exists.

        Args:
            name: Capability name

        Returns:
            True if capability exists
        """
        self._ensure_indexed()
        return name in self._index

    def get_stats(self) -> Dict[str, Any]:
        """Get library statistics."""
        self._ensure_indexed()

        capabilities = sum(1 for k in self._index if not k.startswith(("pattern:", "failure:")))
        patterns = sum(1 for k in self._index if k.startswith("pattern:"))
        failures = sum(1 for k in self._index if k.startswith("failure:"))

        return {
            "total_blueprints": len(self._index),
            "capabilities": capabilities,
            "patterns": patterns,
            "failures": failures,
            "knowledge_dir": str(self._knowledge_dir),
        }

    def refresh_index(self) -> None:
        """Force refresh of the library index."""
        self._indexed = False
        self._ensure_indexed()
        logger.info("📚 Library index refreshed")
