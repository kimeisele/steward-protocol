# OPUS-308: Markdown Manifestation Protocol

**Status**: DESIGN PHASE - Military Grade
**Version**: 0.4 FINAL (Red Pen + Razor Applied)
**Date**: 2025-12-26
**Prereqs**: GAD-000 (Operator Inversion), OPUS-023 (Fractal Architecture), OPUS-151 (Markdown Reality)

---

## 0. FOUNDATION: THE OPERATING REALITY

**This document extends OPUS-151 (Markdown Reality) with a PROTOCOL.**

From OPUS-151:
> "The Markdown files are not the map. They are the territory."
> "There is no 'system behind' the markdown. The markdown IS the system."

From GAD-000:
> "Is this designed for an AI to operate on behalf of a human?"

OPUS-308 answers: **How do entities manifest into this reality?**

---

## 1. THE PARADIGM

```
Unix:     "Everything is a file"
Steward:  "Everything manifests as Markdown"
OPUS-151: "Markdown IS the operating reality"
OPUS-308: "Protocol for manifestation into that reality"
```

A Markdown file is not passive storage. It is the **SKIN** of an entity - the bidirectional membrane between internal computation and the Operator's world.

**CRITICAL DISTINCTION:**
- **OPUS-151** defines WHAT markdown files ARE (reality itself)
- **OPUS-308** defines HOW entities manifest into that reality (protocol)

### 1.1 What This Enables

| Capability | Description |
|------------|-------------|
| **Human Readable** | No API needed. Open file, see state. |
| **Bidirectional** | User writes to file, system reads. System writes, user reads. |
| **Versionable** | Git tracks all changes. Full audit trail. |
| **Discoverable** | `ls *.md` = "what exists in this system?" |
| **Debuggable** | System broken? Read the markdown. |
| **Extensible** | New entity type? Spawn new markdown. |

### 1.2 The HOLON Model (From OPUS-023/151)

Each manifestation is a **HOLON** - whole in itself AND part of a greater whole.

```
┌─────────────────────────────────────────────────────────────┐
│                     MANIFESTATION HOLON                      │
│                                                              │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │ ENTITY      │    │   SKIN      │    │ OPERATOR    │     │
│  │ (internal)  │◄──►│  (.md)      │◄──►│ (human/AI)  │     │
│  │             │    │             │    │             │     │
│  │ - Compute   │    │ - @LIVE     │    │ - Read      │     │
│  │ - State     │    │ - @HUMAN    │    │ - Write     │     │
│  │ - Logic     │    │ - @AI       │    │ - Command   │     │
│  └─────────────┘    └─────────────┘    └─────────────┘     │
│                                                              │
│  The SKIN is the bidirectional membrane.                     │
│  The Operator EXISTS in this reality (OPUS-151).             │
│  There is no "behind" - the markdown IS the truth.           │
└─────────────────────────────────────────────────────────────┘
```

### 1.3 GAD-000 Compliance Requirements

Every manifestation MUST pass the GAD-000 Turing Test:

| Requirement | Implementation |
|-------------|----------------|
| **Discoverability** | Manifest header links file to entity |
| **Observability** | @LIVE sections show real-time state |
| **Parseability** | Structured section markers, not prose |
| **Composability** | Consistent schema across all manifestations |
| **Idempotency** | Hash-based dirty tracking prevents redundant writes |
| **Identity** | Entity ID in header enables cryptographic verification |

### 1.4 The Red Pen Principle (CRITICAL)

**"Invisible = Doesn't Exist"** (GAD-000 corollary)

If the Operator writes something invalid, they MUST see feedback IN THE FILE.
Silent failures violate the fundamental transparency contract.

```
ANTI-PATTERN (Silent Failure):
1. User writes invalid command in SETTINGS.md
2. System logs error to stderr
3. User sees: nothing happens
4. User thinks: "system is broken" or "it worked?"
   → VIOLATES GAD-000
```

```
CORRECT PATTERN (Red Pen):
1. User writes invalid command in SETTINGS.md
2. System annotates the error IN THE FILE
3. User sees: their mistake marked with explanation
4. User thinks: "ah, I need to fix this"
   → GAD-000 COMPLIANT
```

**Example - SETTINGS.md with Red Pen annotation:**

```markdown
<!-- @SECTION:commands OWNER:human -->
## Commands

- SET mode=turbo
<!-- @ERROR: Unknown mode 'turbo'. Valid: simulation|live|debug -->

- RESTART agent.herald
<!-- @OK: Executed at 12:34:56 -->

<!-- /@SECTION -->
```

**Implementation Rule:**
- Every @HUMAN section parse MUST produce visible feedback
- Errors are annotated inline with `<!-- @ERROR: ... -->`
- Success is annotated inline with `<!-- @OK: ... -->`
- The file becomes a conversation, not a one-way command queue

### 1.5 Section Crash Isolation (Graceful Degradation)

**"If one part crashes, don't break everything"**

A renderer crash in one section MUST NOT destroy the entire file.
Each section is an isolated fault domain.

```
ANTI-PATTERN (Catastrophic Failure):
1. VerificationPanel throws exception
2. Entire OPUS.md render fails
3. User sees: stale file or empty file
   → VIOLATES DHARMA (no silent failures)
```

```
CORRECT PATTERN (Graceful Degradation):
1. VerificationPanel throws exception
2. That section shows error placeholder
3. All other sections render normally
4. User sees: "Verification: [ERROR: panel crashed - see logs]"
   → DHARMA COMPLIANT
```

**Example - OPUS.md with crashed section:**

```markdown
<!-- @SECTION:verification OWNER:live -->
## Verification Status

<!-- @RENDER_ERROR
  panel: VerificationPanel
  error: "NoneType has no attribute 'status'"
  timestamp: 2025-12-26T14:30:00Z
  trace_id: abc123
-->

⚠️ **Section unavailable** - VerificationPanel failed to render.
See trace_id `abc123` for details.

<!-- /@SECTION -->

<!-- @SECTION:metrics OWNER:live -->
## Metrics
(renders normally - isolated from crash above)
...
<!-- /@SECTION -->
```

**Implementation Rule:**
- Each section renders in try/except
- Crash produces visible `@RENDER_ERROR` annotation
- Other sections continue rendering
- The Operator ALWAYS sees SOMETHING - never blank/stale

---

## 2. MANIFESTATION PROTOCOL

### 2.1 Who Can Manifest?

**ANYTHING** that has:
1. An identity (unique name)
2. State (that can be represented)
3. A reason to exist in human-visible space

| Entity Class | Examples | Manifestation Pattern |
|--------------|----------|----------------------|
| **Agent** | Envoy, Herald, Steward | `{AGENT_NAME}.md` |
| **Plugin** | opus_assistant, interface | `{PLUGIN_OUTPUT}.md` (e.g., OPUS.md) |
| **System** | Kernel, Config | `SETTINGS.md`, `OPERATIONS.md` |
| **State** | Git, Prakriti | `GIT.md`, `STATE.md` |
| **Index** | Navigation, Routing | `INDEX.md`, `MATRIX.md` |
| **Concept** | Architecture, Cognition | `ARCHITECTURE.md`, `COGNITION.md` |
| **Economy** | Budget, Resources | `ECONOMY.md` |
| **Spawned** | User/Agent created | `{CUSTOM}.md` (with approval) |

### 2.2 Manifestation Request Protocol

An entity requests manifestation via its manifest:

```yaml
# In manifest.json or plugin manifest
manifestation:
  enabled: true
  output: "ENVOY.md"
  location: "root"          # root | .vibe | custom path
  type: "bidirectional"     # readonly | bidirectional | snapshot
  schema: "agent_standard"  # predefined schema name
  sections:
    - id: status
      owner: live
    - id: commands
      owner: human
    - id: response
      owner: live
```

### 2.3 Manifestation Types

| Type | Direction | Example | Use Case |
|------|-----------|---------|----------|
| **READONLY** | System → User | OPERATIONS.md | Status dashboards |
| **BIDIRECTIONAL** | System ↔ User | SETTINGS.md | Command interfaces |
| **SNAPSHOT** | System → Archive | STATE.md | Point-in-time state |

---

## 3. DOCUMENT SCHEMA

### 3.1 Universal Header

Every manifested document MUST have:

```markdown
<!--
  @MANIFEST: {entity_id}
  @TYPE: {readonly|bidirectional|snapshot}
  @SCHEMA: {schema_name}
  @VERSION: {schema_version}
  @GENERATED: {timestamp}
-->
# {DOCUMENT_TITLE}

> {Brief description of this document's purpose}
```

### 3.2 Section Ownership Model

```
@LIVE   = System writes, User reads only
@HUMAN  = User writes, System preserves
@AI     = AI writes, User can override
@SHARED = Both can write (merge strategy needed)
```

**Section Syntax:**

```markdown
<!-- @SECTION:status OWNER:live -->
## Status

{content}

<!-- /@SECTION -->
```

### 3.3 Standard Schemas

**Schema: `agent_standard`**
```
- status      (@LIVE)    - Agent state, health
- commands    (@HUMAN)   - User command queue
- response    (@LIVE)    - Agent responses
- notes       (@HUMAN)   - User notes
```

**Schema: `dashboard_readonly`**
```
- header      (@LIVE)    - Title, timestamp
- metrics     (@LIVE)    - Key numbers
- details     (@LIVE)    - Expandable info
```

**Schema: `config_bidirectional`**
```
- settings    (@HUMAN)   - User-editable settings
- status      (@LIVE)    - Current applied state
- pending     (@HUMAN)   - Queued changes
- history     (@LIVE)    - Change log
```

---

## 4. LIFECYCLE

### 4.1 States

```
    ┌─────────┐
    │ DORMANT │ ← Entity exists but not manifested
    └────┬────┘
         │ spawn()
         ▼
    ┌─────────┐
    │  LIVE   │ ← File exists, actively updated
    └────┬────┘
         │ pause() / resume()
         ▼
    ┌─────────┐
    │ PAUSED  │ ← File exists, shows "PAUSED" status
    └────┬────┘
         │ archive()
         ▼
    ┌─────────┐
    │ARCHIVED │ ← Moved to .archive/, immutable
    └────┬────┘
         │ delete()
         ▼
    ┌─────────┐
    │ DELETED │ ← Gone (or tombstone marker)
    └─────────┘
```

### 4.2 Lifecycle Operations

| Operation | Trigger | Action |
|-----------|---------|--------|
| `spawn()` | Entity boot | Create file from schema |
| `update()` | State change | Render new content, preserve @HUMAN |
| `pause()` | Entity pause | Update status section to "PAUSED" |
| `resume()` | Entity resume | Update status section to "ACTIVE" |
| `archive()` | Entity shutdown | Move to `.archive/` with timestamp |
| `delete()` | Permanent removal | Remove file (or leave tombstone) |

### 4.3 Orphan Detection

What if a manifested file exists but its entity doesn't?

```
On boot:
  for each *.md in manifest locations:
    if no entity claims this file:
      mark as ORPHAN
      options: adopt | archive | warn
```

---

## 5. REGISTRY

### 5.1 The Filesystem IS the Registry (Source of Truth)

**Principle:** The filesystem is the *Source of Truth*, but NOT the *Access Pattern*.

**ManifestIndex (Lazy Scan + TTL Cache)**

Start simple. Complex file watchers can come later.

```python
class ManifestIndex:
    """
    In-memory index of all manifestations.

    PHASE 1 (Simple - Start Here):
    - Lazy scan on first access
    - 1-second TTL cache
    - Robust and simple

    PHASE 2 (When Needed):
    - File watcher event listeners
    - Real-time updates
    - Only if PHASE 1 becomes a bottleneck (>50 agents)
    """

    _cache: Dict[str, Path] = {}
    _cache_time: float = 0
    _ttl: float = 1.0  # 1 second

    def find(self, entity_id: str) -> Optional[Path]:
        """O(1) lookup with lazy refresh."""
        if time.time() - self._cache_time > self._ttl:
            self._rebuild()  # Quick scan, ~10ms for 50 files
        return self._cache.get(entity_id)

    def _rebuild(self):
        """Full scan - called lazily, not on every lookup."""
        self._cache.clear()
        for f in Path(".").glob("*.md"):
            if header := self._extract_manifest_id(f):
                self._cache[header] = f
        self._cache_time = time.time()

    # PHASE 2: Add these later if needed
    # def on_file_created(self, path: Path): ...
    # def on_file_deleted(self, path: Path): ...
```

**Razor Check:** Don't build file watchers until you have >50 manifested entities.
A 10ms glob every second is fine for years.

### 5.2 Manifest Header as Identity

The `<!-- @MANIFEST: {id} -->` header links file to entity.

```python
# Using the index (O(1))
def find_manifestation(entity_id):
    return manifest_index.find(entity_id)
```

### 5.3 Location Patterns

| Location | Purpose | Examples |
|----------|---------|----------|
| `./` (root) | Primary interfaces | SETTINGS.md, ENVOY.md, OPUS.md |
| `./.vibe/` | Internal state | session.md, cache.md |
| `./docs/` | Documentation | ARCHITECTURE.md |
| `./.archive/` | Archived manifestations | timestamped copies |

---

## 6. BIDIRECTIONAL PROTOCOL

### 6.1 The Update Cycle

```
    ┌─────────────────────────────────────┐
    │           USER WORLD                │
    │  (Editor, IDE, manual edits)        │
    └──────────────┬──────────────────────┘
                   │
                   ▼ User writes to @HUMAN sections
    ┌─────────────────────────────────────┐
    │         MARKDOWN FILE               │
    │  @LIVE sections + @HUMAN sections   │
    └──────────────┬──────────────────────┘
                   │
                   ▼ System reads @HUMAN, updates @LIVE
    ┌─────────────────────────────────────┐
    │           SYSTEM WORLD              │
    │  (Kernel, Agents, Plugins)          │
    └─────────────────────────────────────┘
```

### 6.2 Conflict Resolution

**Rule:** @HUMAN sections are NEVER overwritten by system.

```
On render:
  1. Read existing file
  2. Extract all @HUMAN sections (preserve exactly)
  3. Render new @LIVE sections
  4. Merge: new @LIVE + preserved @HUMAN
  5. Write atomically
```

### 6.3 Resilient Parsing (Never Lose Data)

**CRITICAL:** Users WILL break the syntax. The parser MUST be forgiving.

| Scenario | Recovery Strategy |
|----------|-------------------|
| Missing `<!-- /@SECTION -->` | Section ends at next `## Header` or EOF |
| Duplicate section ID | Warn, preserve content in `_recovery` section |
| Malformed header | Skip entity binding, treat as manual file |
| Corrupted markers | Preserve raw content, flag for human review |

**Principle:** A broken marker is NEVER a reason to lose user data.

```python
def parse_section(content: str, section_id: str) -> Optional[str]:
    """
    Resilient section extraction.
    If closing tag missing, find next section or EOF.
    """
    start = find_section_start(content, section_id)
    if not start:
        return None

    # Look for explicit close OR implicit boundary
    end = find_section_end(content, start)  # explicit: <!-- /@SECTION -->
    if not end:
        end = find_next_section_or_eof(content, start)  # implicit

    return content[start:end]
```

### 6.4 Hash-Based Change Detection (Infinite Loop Prevention)

**CRITICAL:** File Watcher + Bidirectional Sync = Infinite Loop Risk.

```
The Loop of Death:
1. System updates @LIVE status
2. File Watcher: "Change detected!"
3. System reads for @HUMAN input
4. System re-renders for consistency
5. File Watcher: "Change detected!"
6. GOTO 2
```

**Solution:** Track @HUMAN section hashes.

```python
class ChangeDetector:
    _human_hashes: Dict[Path, str]  # path -> hash of @HUMAN content

    def should_process(self, path: Path) -> bool:
        """Only trigger logic if @HUMAN sections actually changed."""
        current_human = self._extract_human_sections(path)
        current_hash = hash(current_human)

        if self._human_hashes.get(path) == current_hash:
            return False  # System's own write, ignore

        self._human_hashes[path] = current_hash
        return True  # User actually changed something
```

### 6.5 Command Queue Pattern

For bidirectional command interfaces (SETTINGS.md, ENVOY.md):

```markdown
<!-- @SECTION:commands OWNER:human -->
## Commands

- SET mode=simulation
- RESTART agent.herald

<!-- /@SECTION -->

<!-- @SECTION:executed OWNER:live -->
## Executed

- [x] SET mode=simulation (12:34:56)

<!-- /@SECTION -->
```

System:
1. Reads `commands` section
2. Parses commands
3. Executes
4. Moves to `executed` section
5. Clears `commands` section

---

## 7. STANDALONE PATTERN

### 7.1 The Problem

If plugins can spawn markdown files freely, we get chaos:
- Namespace collisions
- Orphaned files
- Uncontrolled proliferation

### 7.2 The Solution: Controlled Spawning

**Principle:** Plugins don't write files directly. They REQUEST manifestation.

```python
# Plugin code (CORRECT)
class MyPlugin:
    def get_manifestation_config(self):
        return {
            "output": "MY_OUTPUT.md",
            "type": "readonly",
            "schema": "dashboard_readonly"
        }

    def render(self) -> str:
        return "# My Content\n..."

# Kernel handles the actual file write
```

**NOT this:**
```python
# Plugin code (WRONG)
class MyPlugin:
    def on_tick(self):
        Path("MY_OUTPUT.md").write_text(...)  # FORBIDDEN
```

### 7.3 Standalone Testing

A plugin can be tested standalone by mocking the manifestation layer:

```python
# In tests
plugin = MyPlugin()
content = plugin.render()
assert "# My Content" in content
# No file system touched
```

---

## 8. IMPLEMENTATION LAYERS

```
┌─────────────────────────────────────────────────────────────┐
│  LAYER 3: SEMANTIC                                          │
│  FilesystemUIProtocol                                       │
│  - update_status(entity, status)                            │
│  - pop_commands(entity) -> List[Command]                    │
│  - get_manifestation(entity) -> Document                    │
│  Plugins use THIS layer only.                               │
├─────────────────────────────────────────────────────────────┤
│  LAYER 2: STRUCTURE                                         │
│  ManifestationService                                       │
│  - spawn(entity, schema) -> Document                        │
│  - render(entity, content) -> merged_content                │
│  - parse_section(doc, section_id) -> content                │
│  - preserve_human_sections(old, new) -> merged              │
│  Uses schema definitions, NOT regex hacks.                  │
├─────────────────────────────────────────────────────────────┤
│  LAYER 1: PHYSICS                                           │
│  KernelIOService (EXISTS)                                   │
│  - atomic_write(path, content)                              │
│  - acquire_lock(path)                                       │
│  - validate_sandbox(path)                                   │
│  NO CHANGES NEEDED.                                         │
└─────────────────────────────────────────────────────────────┘
```

---

## 9. OPEN QUESTIONS

### Q1: Schema Evolution
What happens when a schema changes? Migration strategy?

### Q2: Multi-Entity Manifestation
Can one markdown represent multiple entities? (e.g., AGENTS.md listing all agents)

### ~~Q3: External Editors~~ → ANSWERED (6.3)
~~How do we handle users who edit markdown in ways that break schema?~~
**Resilient Parsing** - never lose data, graceful degradation.

### Q4: Real-time Updates
Should manifestations update on every state change, or on schedule?

### ~~Q5: File Watchers~~ → ANSWERED (5.1, 6.4)
~~Do we implement file watching for instant @HUMAN section detection?~~
**Yes** - with ManifestIndex updates + Hash-Based Change Detection to prevent loops.

---

## 10. CONNECTION TO EXISTING ARCHITECTURE

### 10.1 Relation to Prior OPUS Documents

| Document | Relation | What OPUS-308 Adds |
|----------|----------|-------------------|
| **GAD-000** | Foundation | Manifestations are AI-operable by design |
| **OPUS-014** | Prior art | Unified the @LIVE/@HUMAN markers into formal protocol |
| **OPUS-023** | Fractal model | Manifestations ARE holons with manifest.json physics |
| **OPUS-151** | Philosophy | Protocol for manifesting INTO the markdown reality |

### 10.2 Vocabulary Alignment (OPUS-151)

| Old Term | New Term | Reason |
|----------|----------|--------|
| "render output" | "manifest truth" | Files ARE reality, not reflections |
| "display to user" | "declare to operator" | Operator exists IN the reality |
| "read system state" | "access truth" | No hidden state behind files |
| "generate" | "manifest" | Creation into the operating reality |

### 10.3 Integration with Existing Renderers

The 30+ existing renderers in `vibe_core/plugins/interface/renderers/` will be migrated incrementally using the **Strangler Fig Pattern**:

1. Wrap existing renderer with ManifestationProtocol interface
2. Add manifest header generation
3. Add section ownership markers
4. Register with ManifestIndex
5. Deprecate direct file writes

---

## 11. ARTIFACTS

| Artifact | Location | Status |
|----------|----------|--------|
| **Design Document** | This file | v0.4 FINAL |
| **Schema Definitions** | `config/manifestation.yaml` | COMPLETE |
| **Protocol Interfaces** | `vibe_core/protocols/manifestation.py` | COMPLETE (with Red Pen methods) |

---

## 12. IMPLEMENTATION ROADMAP

### Phase 1: Foundation (Week 1)
- [ ] Implement `ManifestIndex` with file watcher
- [ ] Implement `ChangeDetector` with hash tracking
- [ ] Add manifest header parsing to IOService

### Phase 2: Layer 2 Core (Week 2)
- [ ] Implement `ManifestationService` (spawn, read_structure, update_live)
- [ ] Resilient parser with graceful degradation
- [ ] Unit tests for section extraction

### Phase 3: First Migration - ENVOY.md (Week 3)
- [ ] Migrate `EnvoyRenderer` to ManifestationProtocol
- [ ] Add bidirectional command queue
- [ ] Integration test: human writes command → system executes

### Phase 4: Layer 3 Semantic (Week 4)
- [ ] Implement `SemanticUIProtocol`
- [ ] High-level operations (set_status, get_user_commands)
- [ ] Plugin migration guide

### Phase 5: Full Migration (Ongoing)
- [ ] Migrate remaining renderers one by one
- [ ] Each migration follows Strangler Fig pattern
- [ ] No big-bang rewrite

---

## 13. RELATED DOCUMENTS

| Document | Purpose |
|----------|---------|
| **GAD-000** | Operator Inversion - the foundational law |
| **OPUS-014** | Unified UI Transparency - prior art on @LIVE/@HUMAN |
| **OPUS-023** | Fractal UI Architecture - holon/manifest model |
| **OPUS-151** | Markdown Reality - philosophical foundation |
| **config/manifestation.yaml** | Schema definitions for all file types |
| **manifestation.py** | Protocol interfaces (Layer 2 & 3) |

---

*"The filesystem is not storage. It is the operating reality."*
*"Manifestations are not outputs. They are declarations of truth."*
*— OPUS-151 + OPUS-308*
