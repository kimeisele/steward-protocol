# OPUS-128: Harness Verification Edge Cases

> **Status**: IMPLEMENTED
> **Created**: 2025-12-19
> **Author**: MANAS (with Gemini collaboration)
> **Territory**: MANAS (050-099)
> **Depends**: OPUS-083 (DocHarnessAnalyzer)

---

## Overview

This document addresses edge cases in harness verification that were causing false positives and incorrect intent generation. The goal is to make the harness verification system **watertight**.

## Problem Statement

The original DocHarnessAnalyzer had several edge cases it didn't handle:

| Scenario | Old Behavior | Problem |
|----------|-------------|---------|
| SUPERSEDED docs | Generate `harness_broken` | Docs intentionally reference old code |
| TDD contracts (PLANNED) | Generate `harness_broken` | Red harness is the SPEC, not an error |
| Moved files | Flag as missing | Files exist, just at new path |
| Moved patterns | Flag as broken wiring | Patterns exist, just in new file |
| Optional files | Flag as broken | `required=false` means optional |

## Solution: Intent Type Specialization

### New Intent Types

| Intent Type | When Generated | Handler Action |
|------------|----------------|----------------|
| `harness_tdd_contract` | Doc status is PLANNED/IN_PROGRESS | Acknowledge contract, return implementation guidance |
| `harness_stale_reference` | Files/patterns found at different paths | Auto-update harness paths (safe operation) |
| `harness_optional_missing` | Files marked `required=false` missing | Info only, low priority |
| `harness_broken` | Truly broken references (not found anywhere) | Existing behavior |

### SUPERSEDED/DEPRECATED Docs

Documents with `Status: SUPERSEDED` or `Status: DEPRECATED` are **skipped entirely**:
- No intents generated
- No validation performed
- Rationale: These docs intentionally reference old/replaced code

### Status Detection Priority

1. **manifest.json** (authoritative) - If document listed in manifest with status
2. **Document header** - Parse `> **Status**: XXX` from markdown

## Implementation

### Modified Files

```
vibe_core/plugins/opus_assistant/manas/analyzers/doc_harness_analyzer.py
  - Added status detection (_get_doc_status)
  - Added smart file search (_search_file_elsewhere)
  - Added smart pattern search (_search_pattern_elsewhere)
  - Added required flag parsing
  - Updated _result_to_intents for new types

vibe_core/plugins/opus_assistant/manas/intent_router.py
  - Added _handle_tdd_contract
  - Added _handle_stale_reference (auto-updates harness!)
  - Added _handle_optional_missing
```

### Key Data Structures

```python
class HarnessAnalysisResult:
    # OPUS-128 additions
    doc_status: Optional[str]          # SUPERSEDED, PLANNED, etc.
    superseded_by: Optional[str]       # What replaced this doc
    is_tdd_contract: bool              # True if PLANNED/IN_PROGRESS
    skip_validation: bool              # True if SUPERSEDED/DEPRECATED
    files_required: Dict[str, bool]    # path -> required flag
    files_found_elsewhere: Dict[str, str]    # old_path -> new_path
    wiring_found_elsewhere: Dict[str, str]   # pattern -> new_file
```

## Examples

### SUPERSEDED Doc (015a-SECURITY-ADDENDUM.md)

```markdown
> **Status**: SUPERSEDED
> **Superseded By**: OPUS-018, OPUS-019
```

Result: `skip_validation=True`, no intents generated.

### TDD Contract (OPUS with Status: PLANNED)

```markdown
> **Status**: PLANNED
```

Result: `harness_tdd_contract` intent with:
- `status: "RED_IS_CORRECT"`
- `files_to_create: [...]`
- `wiring_to_implement: [...]`

### Stale Reference (OPUS-009)

Pattern `def get_state_paths` was in `plugin_main.py`, now in `sync_holon.py`.

Result: `harness_stale_reference` intent that auto-updates:
```diff
- in: vibe_core/plugins/opus_assistant/plugin_main.py
+ in: vibe_core/state/sync_holon.py
```

### Optional Missing

```yaml
files:
  - path: vibe_core/optional_file.py
    required: false  # <- Only generates low-priority info intent
```

## Philosophy

> "The harness is a TDD contract. Red means NOT YET IMPLEMENTED, not BROKEN."

When a doc has status PLANNED or IN_PROGRESS, a red harness is **correct behavior**. The harness defines WHAT needs to be built, not WHAT is broken.

<!-- @HARNESS
files:
  - path: vibe_core/plugins/opus_assistant/manas/analyzers/doc_harness_analyzer.py
    required: true
    rationale: "Edge case handling implementation"
  - path: vibe_core/plugins/opus_assistant/manas/intent_router.py
    required: true
    rationale: "New intent handlers"

wiring:
  - pattern: "STATUS_SUPERSEDED"
    in: vibe_core/plugins/opus_assistant/manas/analyzers/doc_harness_analyzer.py
  - pattern: "TDD_CONTRACT_STATUSES"
    in: vibe_core/plugins/opus_assistant/manas/analyzers/doc_harness_analyzer.py
  - pattern: "_get_doc_status"
    in: vibe_core/plugins/opus_assistant/manas/analyzers/doc_harness_analyzer.py
  - pattern: "_search_file_elsewhere"
    in: vibe_core/plugins/opus_assistant/manas/analyzers/doc_harness_analyzer.py
  - pattern: "_search_pattern_elsewhere"
    in: vibe_core/plugins/opus_assistant/manas/analyzers/doc_harness_analyzer.py
  - pattern: "_handle_tdd_contract"
    in: vibe_core/plugins/opus_assistant/manas/intent_router.py
  - pattern: "_handle_stale_reference"
    in: vibe_core/plugins/opus_assistant/manas/intent_router.py
  - pattern: "_handle_optional_missing"
    in: vibe_core/plugins/opus_assistant/manas/intent_router.py
-->

---
*OPUS-128: Making harness verification watertight*
