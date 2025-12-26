# OPUS-308: FilesystemUI Protocol - The Holographic Fractal Interface

**Status**: DESIGN PHASE
**Generated**: 2025-12-26
**Depends On**: OPUS-023, OPUS-117, OPUS-152, OPUS-307
**Model**: claude-opus-4-5-20251101

---

## EXECUTIVE SUMMARY

**The Problem**: 511 file I/O operations scattered across the codebase. 50+ independent YAML/JSON loaders. 4+ separate markdown rendering systems. NO unified protocol for "Markdown as UI".

**The Solution**: A holographic fractal `FilesystemUIProtocol` that lives in `vibe_core/protocols/` and is implemented by a `FilesystemUIService` in `vibe_core/services/`.

**The Paradigm Shift**: Traditional apps use React + API + Backend. Steward Protocol uses **Markdown files as the user interface**. The filesystem IS the UI.

---

## THE FRAGMENTATION PROBLEM

### Current State (Discovered by OPUS-307 Deep-Dive)

```
                    FRAGMENTATION MAP

     ┌──────────────────────────────────────────────┐
     │         511 File I/O Operations              │
     │      scattered across vibe_core              │
     ├──────────────────────────────────────────────┤
     │                                              │
     │  SETTINGS.md ← SettingsSync                 │
     │               ← SettingsExecutor            │
     │               ← DocRenderer                 │
     │                                              │
     │  ENVOY.md    ← EnvoySync                    │
     │               ← PlaybookRouter              │
     │               ← DocRenderer                 │
     │                                              │
     │  OPERATIONS.md ← DocRenderer (only)         │
     │                                              │
     │  config/*.yaml ← 7+ ad-hoc loaders          │
     │  manifest.json ← ManifestRegistry (good!)   │
     │  *.jsonl      ← 5+ independent ledgers      │
     │                                              │
     │  NO UNIFIED ABSTRACTION!                    │
     └──────────────────────────────────────────────┘
```

### What's Missing

1. **No `FileSystemUIProtocol`** in `vibe_core/protocols/`
2. **No unified `MarkdownDocument` abstraction**
3. **No central file I/O service** (IOService exists but underused)
4. **No file watchers** (documented but not implemented)
5. **Each plugin rolls its own** `yaml.safe_load()`

---

## THE HOLOGRAPHIC FRACTAL SOLUTION

### Design Principle: VEDA-4 All The Way Down

From OPUS-117 "The Holographic Fractal Lasagne":
> "The same pattern repeats at every layer."

**VEDA-4 Pattern** (SHABDA → ARTHA → PRATYAYA → KARMA):
1. **SHABDA** (Capture Intent) → What file/document?
2. **ARTHA** (Validate Meaning) → What type? What structure?
3. **PRATYAYA** (Verify Conditions) → Does it exist? Is it valid?
4. **KARMA** (Execute Action) → Read/Write/Transform

This is how plugins, cartridges, circuits, and sections already work. Now files do too.

---

## ARCHITECTURE: THREE LAYERS

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     LAYER 1: PROTOCOL                                   │
│                vibe_core/protocols/filesystem.py                       │
│                                                                         │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │ @runtime_checkable                                              │   │
│   │ class FilesystemUIProtocol(Protocol):                          │   │
│   │     def scan(path, types) → List[DocumentInfo]                 │   │
│   │     def read(path) → FilesystemUIResult                        │   │
│   │     def write(path, content) → FilesystemUIResult              │   │
│   │     def parse_commands(path) → List[Command]  # SETTINGS.md    │   │
│   │     def render(doc: Document) → str                            │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
├─────────────────────────────────────────────────────────────────────────┤
│                     LAYER 2: SERVICE                                    │
│               vibe_core/services/filesystem_ui.py                      │
│                                                                         │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │ class FilesystemUIService:                                      │   │
│   │     """Registered in ServiceRegistry at boot."""                │   │
│   │                                                                 │   │
│   │     # Unified file I/O (replaces 511 scattered operations)     │   │
│   │     def read_file(path) → str                                  │   │
│   │     def write_file(path, content) → bool                       │   │
│   │     def read_yaml(path) → Dict                                 │   │
│   │     def write_yaml(path, data) → bool                          │   │
│   │     def read_json(path) → Dict                                 │   │
│   │     def write_json(path, data) → bool                          │   │
│   │                                                                 │   │
│   │     # Markdown Document abstraction                             │   │
│   │     def parse_markdown(path) → MarkdownDocument                │   │
│   │     def render_markdown(doc) → str                             │   │
│   │     def extract_commands(path) → List[Command]                 │   │
│   │                                                                 │   │
│   │     # VEDA-4 discovery                                          │   │
│   │     def discover(path, types) → List[DocumentInfo]             │   │
│   │     def validate(path) → ValidationResult                      │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
├─────────────────────────────────────────────────────────────────────────┤
│                     LAYER 3: DOCUMENTS                                  │
│                 vibe_core/documents/*.py                               │
│                                                                         │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │ # Document Types (fractal - same interface, different behavior) │   │
│   │                                                                 │   │
│   │ MarkdownDocument    - Base markdown abstraction                 │   │
│   │ BidirectionalDoc    - SETTINGS.md, ENVOY.md (user ↔ system)    │   │
│   │ ConfigDocument      - YAML/JSON configuration                   │   │
│   │ LedgerDocument      - JSONL append-only logs                    │   │
│   │ ManifestDocument    - manifest.json (already good via Registry) │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## PROTOCOL DEFINITION

### vibe_core/protocols/filesystem.py

```python
"""
FilesystemUI Protocol - OPUS-308

Unified interface for filesystem operations as UI.
The filesystem IS the interface. GAD-000 Transparency.

Pattern: VEDA-4 (SHABDA → ARTHA → PRATYAYA → KARMA)
Mirrors: PluginServiceProtocol + CapabilityProtocol
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol, runtime_checkable
from enum import Enum


class DocumentType(Enum):
    """Document types in the filesystem UI."""
    MARKDOWN = "markdown"           # .md files
    BIDIRECTIONAL = "bidirectional" # SETTINGS.md, ENVOY.md (user ↔ system)
    YAML = "yaml"                   # .yaml/.yml config
    JSON = "json"                   # .json data
    JSONL = "jsonl"                 # .jsonl ledgers (append-only)
    MANIFEST = "manifest"           # manifest.json (via ManifestRegistry)
    TEXT = "text"                   # Plain text


@dataclass
class DocumentInfo:
    """Metadata for discovered documents (VEDA-4 SHABDA stage)."""
    document_id: str
    path: Path
    document_type: DocumentType
    size_bytes: int
    modified_ts: float
    encoding: str = "utf-8"
    sections: List[str] = field(default_factory=list)  # For markdown: headers


@dataclass
class FilesystemUIResult:
    """Unified result type (mirrors CapabilityResult)."""
    success: bool
    output: Any = None
    error: Optional[str] = None
    operation: str = ""  # "read", "write", "parse", "render"
    path: Optional[Path] = None
    execution_time_ms: float = 0.0


@dataclass
class Command:
    """Parsed command from bidirectional document (SETTINGS.md)."""
    raw: str
    action: str
    target: Optional[str] = None
    args: Dict[str, Any] = field(default_factory=dict)
    line_number: int = 0


@runtime_checkable
class FilesystemUIProtocol(Protocol):
    """
    Protocol for filesystem operations as UI.

    THE FILESYSTEM IS THE UI.

    - Read/write files atomically
    - Parse markdown into structured documents
    - Extract commands from bidirectional docs
    - Render documents to markdown
    - Discover documents via VEDA-4 pattern
    """

    # VEDA-4 SHABDA: Discovery
    def discover(
        self,
        path: Path,
        document_types: Optional[List[DocumentType]] = None,
        recursive: bool = True,
    ) -> List[DocumentInfo]:
        """Discover documents in path (SHABDA stage)."""
        ...

    # VEDA-4 ARTHA: Read & Parse
    def read(self, path: Path) -> FilesystemUIResult:
        """Read document content."""
        ...

    def parse(self, path: Path) -> FilesystemUIResult:
        """Parse document into structured form."""
        ...

    # VEDA-4 PRATYAYA: Validate
    def validate(self, path: Path) -> FilesystemUIResult:
        """Validate document format and content."""
        ...

    # VEDA-4 KARMA: Write & Transform
    def write(self, path: Path, content: str) -> FilesystemUIResult:
        """Write content to document (atomic)."""
        ...

    def render(self, document: Any) -> str:
        """Render structured document to string."""
        ...

    # Bidirectional Document Support (SETTINGS.md, ENVOY.md)
    def extract_commands(self, path: Path) -> List[Command]:
        """Extract user commands from bidirectional document."""
        ...

    def update_status(self, path: Path, section: str, status: str) -> FilesystemUIResult:
        """Update status section in bidirectional document."""
        ...


@runtime_checkable
class MarkdownDocumentProtocol(Protocol):
    """Protocol for structured markdown documents."""

    @property
    def path(self) -> Path: ...

    @property
    def sections(self) -> Dict[str, str]: ...

    def get_section(self, header: str) -> Optional[str]: ...

    def set_section(self, header: str, content: str) -> None: ...

    def to_markdown(self) -> str: ...

    @classmethod
    def from_markdown(cls, path: Path, content: str) -> "MarkdownDocumentProtocol": ...
```

---

## SERVICE IMPLEMENTATION

### vibe_core/services/filesystem_ui.py

```python
"""
FilesystemUI Service - OPUS-308

Unified implementation of FilesystemUIProtocol.
Registered in ServiceRegistry at boot.

Replaces:
- 511 scattered file I/O operations
- 7+ ad-hoc config loaders
- 4+ markdown rendering systems
- 5+ independent ledger implementations
"""

import json
import yaml
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field

from vibe_core.protocols.filesystem import (
    FilesystemUIProtocol,
    DocumentType,
    DocumentInfo,
    FilesystemUIResult,
    Command,
)
from vibe_core.services.registry import ServiceRegistry

logger = logging.getLogger(__name__)


@dataclass
class MarkdownDocument:
    """Structured markdown document."""
    path: Path
    title: str = ""
    sections: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    raw_content: str = ""

    def get_section(self, header: str) -> Optional[str]:
        return self.sections.get(header)

    def set_section(self, header: str, content: str) -> None:
        self.sections[header] = content

    def to_markdown(self) -> str:
        """Render back to markdown."""
        lines = []
        if self.title:
            lines.append(f"# {self.title}\n")
        for header, content in self.sections.items():
            lines.append(f"## {header}\n")
            lines.append(content)
            lines.append("")
        return "\n".join(lines)

    @classmethod
    def from_markdown(cls, path: Path, content: str) -> "MarkdownDocument":
        """Parse markdown into structured document."""
        doc = cls(path=path, raw_content=content)
        current_section = ""
        current_content = []

        for line in content.split("\n"):
            if line.startswith("# ") and not doc.title:
                doc.title = line[2:].strip()
            elif line.startswith("## "):
                if current_section:
                    doc.sections[current_section] = "\n".join(current_content)
                current_section = line[3:].strip()
                current_content = []
            else:
                current_content.append(line)

        if current_section:
            doc.sections[current_section] = "\n".join(current_content)

        return doc


class FilesystemUIService(FilesystemUIProtocol):
    """
    Unified filesystem UI service.

    Single source of truth for all file operations.
    Registered in ServiceRegistry for DI.
    """

    def __init__(self):
        self._cache: Dict[Path, DocumentInfo] = {}
        self._documents: Dict[Path, MarkdownDocument] = {}

    # =========================================================================
    # VEDA-4 SHABDA: Discovery
    # =========================================================================

    def discover(
        self,
        path: Path,
        document_types: Optional[List[DocumentType]] = None,
        recursive: bool = True,
    ) -> List[DocumentInfo]:
        """Discover documents using VEDA-4 SHABDA pattern."""
        results = []

        if not path.exists():
            return results

        pattern = "**/*" if recursive else "*"

        for file_path in path.glob(pattern):
            if not file_path.is_file():
                continue

            doc_type = self._detect_type(file_path)
            if document_types and doc_type not in document_types:
                continue

            info = DocumentInfo(
                document_id=str(file_path),
                path=file_path,
                document_type=doc_type,
                size_bytes=file_path.stat().st_size,
                modified_ts=file_path.stat().st_mtime,
            )
            results.append(info)
            self._cache[file_path] = info

        return results

    def _detect_type(self, path: Path) -> DocumentType:
        """Detect document type from path."""
        suffix = path.suffix.lower()
        name = path.name.lower()

        # Bidirectional docs (special markdown)
        if name in ("settings.md", "envoy.md"):
            return DocumentType.BIDIRECTIONAL

        # By extension
        if suffix == ".md":
            return DocumentType.MARKDOWN
        elif suffix in (".yaml", ".yml"):
            return DocumentType.YAML
        elif suffix == ".json":
            if name == "manifest.json":
                return DocumentType.MANIFEST
            return DocumentType.JSON
        elif suffix == ".jsonl":
            return DocumentType.JSONL

        return DocumentType.TEXT

    # =========================================================================
    # VEDA-4 ARTHA: Read & Parse
    # =========================================================================

    def read(self, path: Path) -> FilesystemUIResult:
        """Read document content."""
        try:
            content = path.read_text(encoding="utf-8")
            return FilesystemUIResult(
                success=True,
                output=content,
                operation="read",
                path=path,
            )
        except Exception as e:
            return FilesystemUIResult(
                success=False,
                error=str(e),
                operation="read",
                path=path,
            )

    def parse(self, path: Path) -> FilesystemUIResult:
        """Parse document into structured form."""
        result = self.read(path)
        if not result.success:
            return result

        doc_type = self._detect_type(path)

        try:
            if doc_type in (DocumentType.MARKDOWN, DocumentType.BIDIRECTIONAL):
                doc = MarkdownDocument.from_markdown(path, result.output)
                self._documents[path] = doc
                return FilesystemUIResult(
                    success=True,
                    output=doc,
                    operation="parse",
                    path=path,
                )
            elif doc_type == DocumentType.YAML:
                data = yaml.safe_load(result.output)
                return FilesystemUIResult(
                    success=True,
                    output=data,
                    operation="parse",
                    path=path,
                )
            elif doc_type in (DocumentType.JSON, DocumentType.MANIFEST):
                data = json.loads(result.output)
                return FilesystemUIResult(
                    success=True,
                    output=data,
                    operation="parse",
                    path=path,
                )
            else:
                return result  # Plain text, no parsing needed
        except Exception as e:
            return FilesystemUIResult(
                success=False,
                error=f"Parse error: {e}",
                operation="parse",
                path=path,
            )

    # =========================================================================
    # VEDA-4 PRATYAYA: Validate
    # =========================================================================

    def validate(self, path: Path) -> FilesystemUIResult:
        """Validate document format and content."""
        result = self.parse(path)
        if not result.success:
            return FilesystemUIResult(
                success=False,
                error=f"Validation failed: {result.error}",
                operation="validate",
                path=path,
            )

        # Add type-specific validation here
        return FilesystemUIResult(
            success=True,
            output={"valid": True},
            operation="validate",
            path=path,
        )

    # =========================================================================
    # VEDA-4 KARMA: Write & Transform
    # =========================================================================

    def write(self, path: Path, content: str) -> FilesystemUIResult:
        """Write content atomically."""
        try:
            # Atomic write via temp file
            temp_path = path.with_suffix(path.suffix + ".tmp")
            temp_path.write_text(content, encoding="utf-8")
            temp_path.replace(path)

            # Invalidate cache
            self._cache.pop(path, None)
            self._documents.pop(path, None)

            return FilesystemUIResult(
                success=True,
                output=len(content),
                operation="write",
                path=path,
            )
        except Exception as e:
            return FilesystemUIResult(
                success=False,
                error=str(e),
                operation="write",
                path=path,
            )

    def render(self, document: Any) -> str:
        """Render document to string."""
        if isinstance(document, MarkdownDocument):
            return document.to_markdown()
        elif isinstance(document, dict):
            return yaml.dump(document, default_flow_style=False)
        return str(document)

    # =========================================================================
    # Bidirectional Document Support
    # =========================================================================

    def extract_commands(self, path: Path) -> List[Command]:
        """Extract commands from bidirectional doc (SETTINGS.md, ENVOY.md)."""
        result = self.parse(path)
        if not result.success:
            return []

        doc = result.output
        commands = []

        # Look for command section
        cmd_section = doc.get_section("Commands") or doc.get_section("Queue")
        if not cmd_section:
            return []

        for i, line in enumerate(cmd_section.split("\n")):
            line = line.strip()
            if line.startswith("- ") or line.startswith("* "):
                cmd_text = line[2:].strip()
                if cmd_text and not cmd_text.startswith("~~"):
                    commands.append(Command(
                        raw=cmd_text,
                        action=cmd_text.split()[0] if cmd_text else "",
                        line_number=i,
                    ))

        return commands

    def update_status(self, path: Path, section: str, status: str) -> FilesystemUIResult:
        """Update status section in bidirectional document."""
        result = self.parse(path)
        if not result.success:
            return result

        doc = result.output
        doc.set_section(section, status)

        return self.write(path, doc.to_markdown())

    # =========================================================================
    # Convenience Methods (replace scattered operations)
    # =========================================================================

    def read_yaml(self, path: Path) -> Dict:
        """Read and parse YAML file."""
        result = self.parse(path)
        return result.output if result.success else {}

    def write_yaml(self, path: Path, data: Dict) -> bool:
        """Write data as YAML."""
        content = yaml.dump(data, default_flow_style=False, sort_keys=False)
        result = self.write(path, content)
        return result.success

    def read_json(self, path: Path) -> Dict:
        """Read and parse JSON file."""
        result = self.parse(path)
        return result.output if result.success else {}

    def write_json(self, path: Path, data: Dict) -> bool:
        """Write data as JSON."""
        content = json.dumps(data, indent=2)
        result = self.write(path, content)
        return result.success

    def append_jsonl(self, path: Path, entry: Dict) -> bool:
        """Append to JSONL ledger."""
        try:
            with open(path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")
            return True
        except Exception as e:
            logger.error(f"JSONL append failed: {e}")
            return False

    def read_jsonl(self, path: Path) -> List[Dict]:
        """Read all entries from JSONL ledger."""
        entries = []
        try:
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        entries.append(json.loads(line))
        except Exception as e:
            logger.error(f"JSONL read failed: {e}")
        return entries


# =========================================================================
# Service Registration
# =========================================================================

def register_filesystem_ui_service():
    """Register FilesystemUIService in ServiceRegistry."""
    service = FilesystemUIService()
    ServiceRegistry.register("filesystem_ui", service)
    return service
```

---

## INTEGRATION PLAN

### Phase 1: Protocol & Service (Immediate)

1. Create `vibe_core/protocols/filesystem.py` with protocol definition
2. Create `vibe_core/services/filesystem_ui.py` with implementation
3. Register service at boot in `vibe_core/runtime/boot_sequence.py`
4. Add to `__init__.py` exports

### Phase 2: Migrate SETTINGS.md (Week 1)

1. Update `SettingsSync` to use `FilesystemUIService`
2. Replace direct file I/O with service calls
3. Use `extract_commands()` instead of manual parsing
4. Use `update_status()` for status updates

### Phase 3: Migrate ENVOY.md (Week 1)

1. Update `EnvoySync` to use `FilesystemUIService`
2. Replace direct file I/O with service calls
3. Unify command extraction pattern

### Phase 4: Migrate Config Loaders (Week 2)

1. Update plugin config loaders to use `read_yaml()`
2. Replace 7+ ad-hoc loaders with service calls
3. Centralize validation

### Phase 5: Migrate Ledgers (Week 2)

1. Update 5+ JSONL implementations to use `append_jsonl()` / `read_jsonl()`
2. Standardize ledger format
3. Add optional schema validation

### Phase 6: Migrate Remaining (Week 3+)

1. Audit all 511 file I/O operations
2. Route through FilesystemUIService
3. Add telemetry/logging

---

## SUCCESS CRITERIA

1. **One protocol** for all filesystem UI operations
2. **One service** registered in ServiceRegistry
3. **Zero ad-hoc** `yaml.safe_load()` or `json.load()` calls
4. **Atomic writes** for all document updates
5. **Unified parsing** for markdown documents
6. **VEDA-4 pattern** for discovery and loading

---

## THE PARADIGM SHIFT

```
BEFORE: React + API + Backend
        └── Complex, opaque, hard to debug

AFTER:  Markdown Files = User Interface
        └── Simple, transparent, GAD-000 compliant

        Boot kernel → Interact via markdown

        SETTINGS.md = Command queue
        ENVOY.md    = Task dispatch
        *.yaml      = Configuration
        *.jsonl     = Event ledger

        THE FILESYSTEM IS THE UI.
```

---

*"Ein Service, ein Protocol, ein Cache. Holographic Fractal Markdown as UI."*
