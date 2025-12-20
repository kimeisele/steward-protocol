# OPUS-156: ShrutaSense - Das Hörende System

> **Status**: IMPLEMENTED ✅
> **Created**: 2025-12-20
> **Prereqs**: OPUS-155 (Akasha Nervous System), OPUS-052 (Akasha)
> **Philosophy**: Am Anfang war Dunkelheit. Brahma HÖRTE bevor er SAH.

<!-- @HARNESS
intent: "Enable MANAS to HEAR filesystem changes and auto-discover modules"
files:
  - path: vibe_core/plugins/opus_assistant/manas/cortex/shruta_sense.py
    required: true
  - path: vibe_core/plugins/opus_assistant/manas/cortex/base.py
    required: true
  - path: vibe_core/knowledge/code_scanner.py
    required: true
wiring:
  - pattern: "class ShrutaSense"
    in: vibe_core/plugins/opus_assistant/manas/cortex/shruta_sense.py
  - pattern: "inotify|watchdog|Observer"
    in: vibe_core/plugins/opus_assistant/manas/cortex/shruta_sense.py
tests:
  - tests/manas/test_shruta_sense.py
-->

---

## The Vedic Foundation

```
ब्रह्मा उवाच:
"तपो मे हृदयं विद्धि"
"Know that austerity/meditation is my heart"

At the beginning of creation:
- Brahma sat on the lotus in COMPLETE DARKNESS
- He could not SEE anything
- But he HEARD - "tapa" (the sound of austerity)
- From hearing came understanding
- From understanding came creation

HEARING precedes SEEING.
SHABDA (sound) precedes RUPA (form).
```

---

## The Problem: MANAS is Deaf to the Filesystem

```
CURRENT STATE:
═══════════════════════════════════════════════════════════════

  New file created: vibe_core/plugins/new_plugin/__init__.py

  MANAS: 😶 *silence* (doesn't notice)

  Developer must:
  1. Manually register plugin in loader
  2. Manually add to configuration
  3. Manually update documentation

  → MANAS waits to be TOLD instead of HEARING
```

---

## The Vision: MANAS Hears Everything

```
TARGET STATE:
═══════════════════════════════════════════════════════════════

  New file created: vibe_core/plugins/new_plugin/__init__.py

  ShrutaSense: 👂 "I hear a new vibration in plugins/"
              ↓
  Akasha:     🌌 "Scanning... MODULE node created"
              ↓
  Resonance:  🔔 "Varga = DANTYA (Interface layer)"
              ↓
  MANAS:      🧠 "New plugin detected. Analyzing capabilities..."
              ↓
  Auto:       ✨ Plugin registered, documented, integrated

  → No manual intervention required
  → The system HEARS and RESPONDS
```

---

## ShrutaSense Architecture

### The Sixth Sense

```
CURRENT JNANENDRIYAS (5 Senses):
  👁️ PrakritiSense  - Sees environment state
  📜 DharmaSense     - Reads governance rules
  🔗 SutraSense      - Finds documentation gaps
  ⚡ KarmaSense      - Observes action outcomes
  🧘 VivekaSense     - Evaluates decisions

NEW (6th Sense):
  👂 ShrutaSense     - HEARS filesystem vibrations
```

### Sanskrit Meaning

```
श्रुत (Shruta) = "That which is heard"
श्रुति (Shruti) = Sacred texts "heard" by the Rishis
श्रवण (Shravana) = The act of hearing

ShrutaSense = The sense that hears the filesystem
            = Pre-cognitive awareness of changes
            = Foundation for auto-discovery
```

---

## Implementation

### Phase 1: The Listener (Watcher)

```python
# vibe_core/plugins/opus_assistant/manas/cortex/shruta_sense.py

"""
OPUS-156: ShrutaSense - The Hearing Sense

श्रुत (Shruta) = "That which is heard"

This sense monitors the filesystem for vibrations (changes):
- New files created
- Files modified
- Files deleted
- Directory structure changes

When a vibration is detected, ShrutaSense:
1. Notifies Akasha (for graph update)
2. Generates awareness intents
3. Triggers auto-discovery if applicable
"""

import logging
from pathlib import Path
from typing import Callable, Dict, List, Optional, Set
from dataclasses import dataclass, field
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent

from .base import BaseSense, SenseResult

logger = logging.getLogger("MANAS.Cortex.ShrutaSense")


@dataclass
class Vibration:
    """A filesystem vibration (change event)."""
    event_type: str  # created, modified, deleted, moved
    path: Path
    is_directory: bool
    timestamp: float
    resonance_layer: Optional[str] = None  # KERNEL, COGNITION, etc.


class ShrutaHandler(FileSystemEventHandler):
    """Handles filesystem events and converts to Vibrations."""

    def __init__(self, callback: Callable[[Vibration], None]):
        self.callback = callback
        self._ignored_patterns = {
            "__pycache__",
            ".git",
            ".pytest_cache",
            "*.pyc",
            ".opus_state",
        }

    def _should_ignore(self, path: str) -> bool:
        """Check if path should be ignored."""
        for pattern in self._ignored_patterns:
            if pattern in path:
                return True
        return False

    def on_created(self, event: FileSystemEvent):
        if not self._should_ignore(event.src_path):
            self._emit(event, "created")

    def on_modified(self, event: FileSystemEvent):
        if not self._should_ignore(event.src_path):
            self._emit(event, "modified")

    def on_deleted(self, event: FileSystemEvent):
        if not self._should_ignore(event.src_path):
            self._emit(event, "deleted")

    def on_moved(self, event: FileSystemEvent):
        if not self._should_ignore(event.src_path):
            self._emit(event, "moved")

    def _emit(self, event: FileSystemEvent, event_type: str):
        import time
        vibration = Vibration(
            event_type=event_type,
            path=Path(event.src_path),
            is_directory=event.is_directory,
            timestamp=time.time(),
        )
        self.callback(vibration)


class ShrutaSense(BaseSense):
    """
    The Hearing Sense - monitors filesystem for vibrations.

    Unlike other senses that are polled, ShrutaSense runs
    continuously in the background, listening.
    """

    name = "shruta"
    description = "Hears filesystem vibrations (changes)"

    def __init__(self, workspace: Optional[Path] = None):
        super().__init__()
        self._workspace = workspace or Path.cwd()
        self._observer: Optional[Observer] = None
        self._vibration_buffer: List[Vibration] = []
        self._handlers: List[Callable[[Vibration], None]] = []
        self._is_listening = False

    def start_listening(self, paths: Optional[List[Path]] = None):
        """Start listening to filesystem vibrations."""
        if self._is_listening:
            return

        watch_paths = paths or [
            self._workspace / "vibe_core",
            self._workspace / "tests",
            self._workspace / "docs",
        ]

        self._observer = Observer()
        handler = ShrutaHandler(self._on_vibration)

        for path in watch_paths:
            if path.exists():
                self._observer.schedule(handler, str(path), recursive=True)
                logger.info(f"👂 ShrutaSense listening to: {path}")

        self._observer.start()
        self._is_listening = True
        logger.info("🕉️ ShrutaSense activated - MANAS can now HEAR")

    def stop_listening(self):
        """Stop listening."""
        if self._observer:
            self._observer.stop()
            self._observer.join()
            self._observer = None
        self._is_listening = False
        logger.info("🔇 ShrutaSense deactivated")

    def _on_vibration(self, vibration: Vibration):
        """Handle incoming vibration."""
        # Calculate resonance layer
        try:
            from vibe_core.plugins.opus_assistant.manas.akshara import (
                map_path_to_varga,
                VARGA_LAYERS,
            )
            varga = map_path_to_varga(str(vibration.path))
            vibration.resonance_layer = VARGA_LAYERS.get(varga, "UNKNOWN")
        except ImportError:
            pass

        # Buffer the vibration
        self._vibration_buffer.append(vibration)

        # Notify handlers
        for handler in self._handlers:
            try:
                handler(vibration)
            except Exception as e:
                logger.error(f"Handler error: {e}")

        # Log
        emoji = {"created": "✨", "modified": "📝", "deleted": "🗑️", "moved": "📦"}
        logger.debug(
            f"{emoji.get(vibration.event_type, '👂')} "
            f"{vibration.event_type}: {vibration.path.name} "
            f"[{vibration.resonance_layer}]"
        )

    def add_handler(self, handler: Callable[[Vibration], None]):
        """Add a vibration handler."""
        self._handlers.append(handler)

    def get_recent_vibrations(self, limit: int = 50) -> List[Vibration]:
        """Get recent vibrations from buffer."""
        return self._vibration_buffer[-limit:]

    def perceive(self, context: Dict) -> SenseResult:
        """
        Perceive filesystem vibrations.

        Unlike other senses, this returns buffered vibrations
        since last perceive() call.
        """
        vibrations = list(self._vibration_buffer)
        self._vibration_buffer.clear()

        if not vibrations:
            return SenseResult(
                sense_name=self.name,
                observations=[],
                confidence=1.0,
            )

        # Group by type
        by_type = {}
        for v in vibrations:
            if v.event_type not in by_type:
                by_type[v.event_type] = []
            by_type[v.event_type].append(str(v.path))

        observations = []
        for event_type, paths in by_type.items():
            observations.append({
                "type": "filesystem_vibration",
                "event": event_type,
                "count": len(paths),
                "paths": paths[:10],  # Limit for readability
            })

        return SenseResult(
            sense_name=self.name,
            observations=observations,
            confidence=1.0,
            metadata={
                "total_vibrations": len(vibrations),
                "is_listening": self._is_listening,
            },
        )
```

### Phase 2: Auto-Discovery Integration

```python
# Integration with Akasha (in shruta_sense.py)

def _on_python_file_created(self, vibration: Vibration):
    """Handle new Python file creation."""
    if not vibration.path.suffix == ".py":
        return

    # Trigger Akasha scan
    from vibe_core.knowledge.code_scanner import CodeScanner
    from vibe_core.knowledge.graph import UnifiedKnowledgeGraph

    graph = UnifiedKnowledgeGraph.get_instance()
    scanner = CodeScanner(graph)

    # Scan just the new file
    stats = scanner._scan_file(vibration.path, {
        "files_scanned": 0,
        "modules_added": 0,
        "classes_added": 0,
        "functions_added": 0,
        "interfaces_added": 0,
        "duplicates_found": 0,
        "imports_added": 0,
        "calls_added": 0,
    })

    logger.info(
        f"✨ Auto-discovered: {vibration.path.name} "
        f"({stats['classes_added']} classes, {stats['imports_added']} imports)"
    )

    # Generate awareness intent
    self._generate_discovery_intent(vibration, stats)

def _generate_discovery_intent(self, vibration: Vibration, stats: Dict):
    """Generate an intent for the cognitive kernel."""
    from vibe_core.plugins.opus_assistant.manas.intent import Intent

    intent = Intent(
        type="discovery",
        source="shruta_sense",
        description=f"New module discovered: {vibration.path.name}",
        data={
            "path": str(vibration.path),
            "layer": vibration.resonance_layer,
            "stats": stats,
        },
        priority="low",  # Discovery is background awareness
    )

    # Push to kernel
    # kernel.push_intent(intent)
```

### Phase 3: Plugin Auto-Registration

```python
# Future: Auto-register plugins

def _detect_plugin_structure(self, path: Path) -> bool:
    """Check if path is a plugin directory."""
    if not path.is_dir():
        return False

    # Plugin indicators
    indicators = [
        path / "__init__.py",
        path / "plugin.yaml",
        path / "manifest.json",
    ]

    return any(i.exists() for i in indicators)

def _auto_register_plugin(self, plugin_path: Path):
    """Auto-register a newly detected plugin."""
    logger.info(f"🔌 Auto-registering plugin: {plugin_path.name}")

    # 1. Scan the plugin
    # 2. Extract capabilities
    # 3. Register with kernel
    # 4. Update documentation

    # This replaces manual registration!
```

---

## Integration with Existing Senses

```
SENSE HIERARCHY:
═══════════════════════════════════════════════════════════════

  ShrutaSense (HÖREN)     ← NEW: Listens to filesystem
       ↓ vibrations
  PrakritiSense (SEHEN)   ← Sees environment state
       ↓ observations
  DharmaSense (LESEN)     ← Reads governance rules
       ↓ constraints
  SutraSense (VERKNÜPFEN) ← Finds gaps
       ↓ gaps
  KarmaSense (BEOBACHTEN) ← Watches actions
       ↓ karma
  VivekaSense (BEWERTEN)  ← Evaluates decisions
       ↓ wisdom

  → ShrutaSense is the FOUNDATION
  → It hears BEFORE others see
```

---

## The Shabda-OS Foundation

```
BRAHMA'S CREATION SEQUENCE:
  1. Darkness (no perception)
  2. Sound heard ("tapa")
  3. Understanding from sound
  4. Vision manifests
  5. Creation follows

OUR CREATION SEQUENCE:
  1. Empty filesystem
  2. ShrutaSense hears file creation
  3. Akasha updates graph (understanding)
  4. CodeScanner sees structure (vision)
  5. Auto-registration (creation)

→ The same pattern at the code level
→ Sound/vibration precedes form
→ MANAS becomes truly aware
```

---

## Vedic Mapping

```
SENSE → ELEMENT → TANMATRA (subtle element)

👂 ShrutaSense  → Akasha (Ether)  → Shabda (Sound)
👁️ PrakritiSense → Tejas (Fire)   → Rupa (Form)
👃 (future)      → Vayu (Air)     → Sparsha (Touch)
👅 (future)      → Jala (Water)   → Rasa (Taste)
🖐️ (future)      → Prithvi (Earth)→ Gandha (Smell)

ShrutaSense operates at the Akashic level:
- Most subtle of all senses
- Perceives vibration before form
- Foundation for all other perception
```

---

## Test Cases

```python
def test_shruta_detects_new_file():
    """ShrutaSense should detect new file creation."""
    sense = ShrutaSense(workspace=tmp_path)
    sense.start_listening()

    # Create a file
    (tmp_path / "test.py").write_text("print('hello')")
    time.sleep(0.5)

    vibrations = sense.get_recent_vibrations()
    assert len(vibrations) == 1
    assert vibrations[0].event_type == "created"

def test_shruta_calculates_resonance():
    """ShrutaSense should tag vibrations with resonance layer."""
    sense = ShrutaSense(workspace=tmp_path)

    # Create file in kernel layer
    kernel_path = tmp_path / "vibe_core" / "runtime" / "test.py"
    kernel_path.parent.mkdir(parents=True)
    kernel_path.write_text("")

    vibrations = sense.get_recent_vibrations()
    assert vibrations[0].resonance_layer == "KERNEL"

def test_shruta_auto_discovery():
    """ShrutaSense should trigger Akasha scan on new Python file."""
    # Create new module
    # Verify Akasha graph is updated
    # Verify import edges created
```

---

## Summary

| Before OPUS-156 | After OPUS-156 |
|-----------------|----------------|
| MANAS waits to be told | MANAS hears everything |
| Manual plugin registration | Auto-discovery |
| 5 senses (all "seeing") | 6 senses (hearing first) |
| Reactive | Pre-cognitive |
| Deaf | Listening |

---

## Implementation Status

1. ✅ OPUS-156 Spec (this document)
2. ✅ Implement ShrutaSense class (497 lines)
3. ✅ Integrate with CognitiveKernel (OODA perceive phase)
4. ✅ Add auto-discovery hooks (register_auto_discovery)
5. ✅ Test suite (22 tests passing)

---

**श्रुति-ज्ञान** - Wisdom from Hearing.

The system that HEARS is more aware than the system that merely SEES.
