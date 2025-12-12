# OPUS-029: Fractal OPUS Plugin Architecture

> **Status**: 📋 PLANNING (NOT IMPLEMENTED)
> **Created**: 2025-12-12
> **Author**: Claude Opus 4
> **Depends On**: OPUS-015 (Container Format), OPUS-020 (Container Migration), OPUS-010 (Verification)
> **Purpose**: Extract verification logic into container-compatible plugin
> **Problem**: 700 LOC verification logic trapped in renderer panel, STATUS is binary fiction
> **Scope**: Plugin architecture, NOT implementation

---

## Executive Summary

**Problem Statement:**

1. **Verification logic is trapped** in `verification.py` panel (700 LOC)
2. **STATUS is binary fiction** - "IMPLEMENTED" vs "NOT" ignores reality
3. **Renderer mixing concerns** - InterfacePlugin renders AND verifies
4. **Not container-ready** - Panel can't be packed as `.vibe`

**Proposed Solution:**

Extract verification engine into a **proper KernelPlugin** that:
- Follows OPUS-015 container format (Holon structure)
- Replaces STATUS with **CONFIDENCE** (auto-generated metric)
- Exposes API for renderer to query (separation of concerns)
- Is container-compatible from day 1

---

## Architecture Analysis

### Current State

```
vibe_core/plugins/interface/
    ├── plugin_main.py              # InterfacePlugin
    └── renderers/opus/
        ├── renderer.py             # OpusRenderer
        └── panels/
            └── verification.py     # 700 LOC verification logic (TRAPPED)
```

**Problems:**
- Panel does verification AND rendering (violates SRP)
- Cannot be tested in isolation
- Cannot be reused by CLI or other tools
- Not container-packable

### Target State

```
vibe_core/plugins/opus/              # NEW PLUGIN
    ├── manifest.json                # Holon metadata
    ├── plugin_main.py               # OpusPlugin (KernelPlugin)
    ├── verification_engine.py       # @HARNESS verification logic
    ├── confidence_calculator.py     # STATUS → CONFIDENCE
    ├── harness_parser.py            # YAML @HARNESS extraction
    ├── drift_detector.py            # Code-doc drift detection
    └── tests/
        └── test_verification.py     # Unit tests

vibe_core/plugins/interface/renderers/opus/
    └── panels/
        └── verification.py          # NOW: Just renders data from OpusPlugin
```

---

## Container Compatibility Requirements (OPUS-015/020)

### manifest.json Template

```json
{
  "id": "opus",
  "version": "1.0.0",
  "type": "plugin",
  "execution": {
    "mode": "thread",
    "runtime": "python3.11"
  },
  "entry_point": "plugin_main.py",
  "dependencies": [],
  "capabilities": ["verification", "confidence", "drift_detection"]
}
```

### Holon Structure (OPUS-015 Section 1)

```
vibe_core/plugins/opus/
    ├── manifest.json          # [0] ALWAYS FIRST
    ├── content/               # [2] Payload
    │   ├── plugin_main.py     # Entry point
    │   ├── verification_engine.py
    │   ├── confidence_calculator.py
    │   ├── harness_parser.py
    │   └── drift_detector.py
    └── tests/                 # [4] Quality gate
        ├── test_verification.py
        ├── test_confidence.py
        └── test_harness_parser.py
```

### Shadowing Rule (OPUS-020)

When deployed:
```bash
# Development mode: folder loaded directly
vibe_core/plugins/opus/

# Production mode: container shadows folder
vibe_core/plugins/opus.vibe  # WINS over folder
```

---

## Design Decisions

### 1. STATUS → CONFIDENCE Paradigm

**Current (Binary Fiction):**
```
Status: IMPLEMENTED | NOT_IMPLEMENTED
```

**Proposed (Continuous Reality):**
```python
@dataclass
class DocumentConfidence:
    doc_name: str
    overall: float           # 0.0 - 1.0
    files_exist: float       # Component scores
    tests_pass: float
    wiring_verified: float
    absent_clean: float
    config_exists: float
    semantic_passes: float
    drift_age_days: int      # How stale is the verification?
    last_verified: datetime
```

**Benefits:**
- No more "IMPLEMENTED" lies
- Auto-generated from metrics
- Software is never "done" - always in progress
- Confidence degrades over time (drift detection)

### 2. Separation of Concerns

| Component | Responsibility |
|-----------|----------------|
| `OpusPlugin` | Boot, API exposure, kernel integration |
| `VerificationEngine` | @HARNESS verification logic |
| `ConfidenceCalculator` | Metrics → confidence score |
| `HarnessParser` | YAML extraction from markdown |
| `DriftDetector` | Code changed but doc didn't |
| `VerificationPanel` | **Only renders** data from plugin |

### 3. Plugin API Contract

```python
class OpusPlugin(KernelPlugin):
    """Fractal OPUS Architecture Plugin."""

    @property
    def plugin_id(self) -> str:
        return "opus"

    def get_document_confidence(self, doc_name: str) -> DocumentConfidence:
        """Get confidence score for a single document."""

    def get_all_confidences(self) -> List[DocumentConfidence]:
        """Get confidence scores for all OPUS documents."""

    def verify_document(self, doc_name: str) -> VerificationResult:
        """Run verification for a single document."""

    def detect_drift(self) -> List[DriftReport]:
        """Find documents where code changed but doc didn't."""

    def cmd_opus_verify(self, doc: str = None) -> Dict[str, Any]:
        """CLI command: steward opus verify [doc]"""

    def cmd_opus_confidence(self) -> Dict[str, Any]:
        """CLI command: steward opus confidence"""
```

### 4. Renderer Integration

```python
# panels/verification.py (AFTER refactor)
class VerificationPanel(BasePanel):
    def render(self) -> str:
        # Get data from OpusPlugin (no more embedded logic!)
        opus_plugin = self._kernel.get_plugin("opus")
        if not opus_plugin:
            return "## Verification\n\n_OpusPlugin not loaded_"

        confidences = opus_plugin.get_all_confidences()
        return self._format_confidences(confidences)
```

---

## Migration Strategy

### Phase 1: Create Plugin Skeleton
- Create `vibe_core/plugins/opus/` folder structure
- Create `manifest.json` (container-compatible)
- Create `plugin_main.py` with empty methods
- **NO LOGIC YET** - just structure

### Phase 2: Extract HarnessParser
- Move `_extract_harness()` to `harness_parser.py`
- Add unit tests
- Verify existing renderer still works (backward compatible)

### Phase 3: Extract VerificationEngine
- Move all `_verify_*` methods to `verification_engine.py`
- Keep panel as thin wrapper
- Add integration tests

### Phase 4: Add ConfidenceCalculator
- Implement STATUS → CONFIDENCE transformation
- Add drift detection
- Update renderer to use new confidence API

### Phase 5: Container Packaging
- Test packing as `.vibe`
- Verify shadowing works
- Update OPUS-020 with real example

---

## Risk Analysis

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Breaking existing verification | Medium | High | Phase-by-phase, backward compatible |
| Circular dependency (plugin → renderer) | Low | Medium | Clean API boundary |
| Performance regression | Low | Low | Cache verification results |
| Container compatibility issues | Medium | Medium | Test early, follow OPUS-015 exactly |

---

## Success Criteria

| Criterion | Status | Evidence |
|-----------|--------|----------|
| Plugin passes `pack_vibe.py` | ❓ | Can create `.vibe` container |
| Renderer uses plugin API | ❓ | No embedded verification logic |
| CONFIDENCE replaces STATUS | ❓ | Auto-generated scores |
| CLI commands work | ❓ | `steward opus verify` |
| Existing verification unchanged | ❓ | Same output, different source |
| All tests pass | ❓ | Unit + integration |

---

## NOT In Scope

- Rewriting the entire verification logic (just extracting)
- Adding new verification types (later phase)
- UI changes beyond confidence display
- OPUS document format changes

---

## Questions for Review

1. **Plugin priority**: Should OpusPlugin boot before or after InterfacePlugin?
2. **Caching**: How long to cache verification results?
3. **Drift threshold**: How many days before confidence degrades?
4. **CLI integration**: Should this expose `steward opus` subcommands?

---

## Related Documents

- **OPUS-010**: Verification Protocol (concept)
- **OPUS-015**: Container Format (Holon structure)
- **OPUS-020**: Container Migration (development workflow)
- **OPUS-023**: Fractal UI Architecture
- **GAD-000**: Operator Inversion (API design)

---

**Author**: Claude Opus 4
**Date**: 2025-12-12
**Status**: 📋 PLANNING - This is an architecture proposal, NOT implementation
