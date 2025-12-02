# ARCHITECTURE PROCESS - The Living System

> **Status:** PROPOSAL
> **Origin:** Reverse-engineered from vibe-agency (the birthplace)
> **Purpose:** Formalize architecture management as an AGENT-DRIVEN PROCESS

---

## The Problem

The current `docs/architecture/` is chaos:
- 20+ flat files with no hierarchy
- Plans mixed with specs mixed with reports
- No clear ownership or maintenance process
- GAD references in code (36!) but only 2 documented

**The original vibe-agency had this solved.** We lost it.

---

## The 3D Architecture Matrix

From vibe-agency, the architecture is a **3-dimensional matrix**:

```
         ┌─────────────────────────────────────────────────┐
         │               VAD (Verification)                │
         │   Cross-cutting tests that verify integration   │
         │   "Does X work with Y across all layers?"       │
         └─────────────────────────────────────────────────┘
                              ↓
    ┌─────────────────────────────────────────────────────────┐
    │                    LAD (Layers)                         │
    │   Deployment layers with graceful degradation           │
    │   "WHERE does this run?"                                │
    └─────────────────────────────────────────────────────────┘
                              ↓
    ┌─────────────────────────────────────────────────────────┐
    │                    GAD (Pillars)                        │
    │   Functional architecture domains                       │
    │   "WHAT does this do?"                                  │
    └─────────────────────────────────────────────────────────┘
```

### GAD: Global Architecture Dimension (WHAT)

8 functional pillars, each with 100 slots:

| Pillar | Range | Name | Description |
|--------|-------|------|-------------|
| **GAD-0XX** | 000-099 | Foundation | Core principles (GAD-000 = Operator Inversion) |
| **GAD-1XX** | 100-199 | Planning & Research | Discovery, analysis |
| **GAD-2XX** | 200-299 | Orchestration | SDLC, workflow, state machines |
| **GAD-3XX** | 300-399 | Agent Framework | Agent lifecycle, runtime |
| **GAD-4XX** | 400-499 | Quality & Testing | Auditor, linting, tests |
| **GAD-5XX** | 500-599 | Runtime Engineering | Kernel, syscalls, circuits |
| **GAD-6XX** | 600-699 | Knowledge | Semantic graph, RAG, embeddings |
| **GAD-7XX** | 700-799 | STEWARD Governance | Protocol, trust, verification |
| **GAD-8XX** | 800-899 | Integration | External systems, APIs |

**Numbering Convention:**
- `GAD-X00` = EPIC (pillar overview)
- `GAD-X01..X99` = Individual specs within pillar

### LAD: Layer Architecture Dimension (WHERE)

3 deployment layers with **graceful degradation**:

| Layer | Name | Requirements | Capabilities |
|-------|------|--------------|--------------|
| **LAD-1** | Browser | Zero setup | Manual only, prompt-based |
| **LAD-2** | Claude Code | Local tools | Automation, file access |
| **LAD-3** | Full Runtime | Cloud services | Full kernel, multi-agent |

**Key Insight:** System MUST degrade L3→L2→L1 gracefully!

### VAD: Verification Architecture Dimension (HOW)

Cross-cutting tests that verify GADs work together across LADs:

| VAD | Tests | GADs Involved |
|-----|-------|---------------|
| **VAD-001** | Core Workflow | GAD-2XX × GAD-4XX × GAD-5XX |
| **VAD-002** | Knowledge Integration | GAD-5XX × GAD-6XX |
| **VAD-003** | Layer Degradation | All GADs across LAD-1..3 |
| **VAD-004** | Safety Layer | GAD-4XX × GAD-7XX × GAD-5XX |

---

## The Process (Agent-Driven)

### Phase 1: Discovery (AUTOMATED)

Scripts in `scripts/` run analysis:

```bash
python scripts/analyze_gad_references.py   # Find undocumented GADs
python scripts/extract_gad_spec.py --all   # Generate drafts from code
python scripts/validate_manifests.py       # Check agent compliance
python scripts/run_all_analyzers.py        # Master report
```

**Output:** `ANALYSIS_REPORT.md` + `drafts/GAD-XXXX_DRAFT.md`

### Phase 2: Triage (HUMAN-IN-LOOP)

Human reviews drafts and decides:
1. **Promote** → Move from `drafts/` to `GAD-XXX/`
2. **Refine** → Edit draft, re-extract
3. **Archive** → Code is legacy, mark deprecated

### Phase 3: Placement (AGENT-ASSISTED)

SCRIBE agent places specs in correct pillar:

```
docs/architecture/
├── GAD-0XX/
│   └── GAD-000_Operator_Inversion.md
├── GAD-5XX/
│   ├── GAD-500_Runtime_Engineering.md (EPIC)
│   ├── GAD-509_Circuit_Breaker.md
│   ├── GAD-510_Operational_Quotas.md
│   ├── GAD-511_Neural_Adapter.md
│   └── GAD-5500_Neuro_Symbolic_OS.md
├── LAD/
│   ├── LAD-1_Browser.md
│   ├── LAD-2_Claude_Code.md
│   └── LAD-3_Full_Runtime.md
├── VAD/
│   ├── VAD-001_Core_Workflow.md
│   └── VAD-003_Layer_Degradation.md
├── drafts/           # Pending review
├── scripts/          # Analysis tools
└── archive/          # Deprecated
```

### Phase 4: Verification (CONTINUOUS)

VAD tests run on every commit:
- `tests/architecture/test_vad001_core_workflow.py`
- `tests/architecture/test_vad003_degradation.py`

**CI blocks merge if VAD tests fail.**

---

## The Loop (Closing It)

```
┌─────────────────────────────────────────────────────────┐
│                    CODE CHANGES                          │
└─────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│         Phase 1: analyze_gad_references.py              │
│         (Automated - finds new/changed GAD refs)        │
└─────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│         Phase 2: extract_gad_spec.py                    │
│         (Automated - generates draft specs)             │
└─────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│         Phase 3: HUMAN REVIEW                           │
│         (Approve/Refine/Archive)                        │
└─────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│         Phase 4: SCRIBE places in GAD-XXX/              │
│         (Agent-assisted organization)                   │
└─────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│         Phase 5: VAD tests verify                       │
│         (CI blocks if broken)                           │
└─────────────────────────────────────────────────────────┘
                         │
                         ▼
                    [LOOP BACK]
```

---

## Migration Plan

### Step 1: Create Directory Structure

```bash
mkdir -p docs/architecture/{GAD-0XX,GAD-1XX,GAD-2XX,GAD-3XX,GAD-4XX,GAD-5XX,GAD-6XX,GAD-7XX,GAD-8XX,LAD,VAD,archive}
```

### Step 2: Move Existing Specs

| Current File | New Location | Pillar |
|--------------|--------------|--------|
| GAD-000.md (root) | GAD-0XX/GAD-000_Operator_Inversion.md | Foundation |
| GAD-1000.md | GAD-1XX/GAD-1000_*.md | Planning |
| VEDA4_COGNITIVE_CIRCUITS.md | GAD-5XX/GAD-5500_Neuro_Symbolic_OS.md | Runtime |

### Step 3: Archive Legacy Plans

Move to `archive/`:
- AGENT_CITY_OFFLINE_PLAN.md
- PHOENIX_VIMANA_UNIFIED_BOOT_PLAN.md
- UNIVERSE_MIGRATION_PLAN.md
- (completed/obsolete plans)

### Step 4: Generate Missing EPICs

Each pillar needs a GAD-X00 overview doc:
- GAD-500_Runtime_Engineering.md (EPIC for GAD-5XX)
- GAD-700_STEWARD_Governance.md (EPIC for GAD-7XX)
- etc.

### Step 5: Create Initial VAD Tests

Port from vibe-agency:
- VAD-001: Core Workflow verification
- VAD-003: Layer Degradation verification

---

## Ownership

| Artifact | Owner | Maintenance |
|----------|-------|-------------|
| GAD-0XX | CIVIC (governance) | Constitutional changes only |
| GAD-1XX..8XX | SCRIBE | Auto-extract + human review |
| LAD | ARCHITECT | Deployment layer changes |
| VAD | AUDITOR | Test maintenance |
| scripts/ | ENGINEER | Tool improvements |
| drafts/ | SCRIBE | Staging area |

---

## Success Criteria

The loop is closed when:

1. **Every GAD reference in code has a spec** (0 undocumented)
2. **VAD tests pass on every commit** (CI enforced)
3. **Degradation works** (L3→L2→L1 graceful)
4. **Agents maintain it** (minimal HIL)

---

*This document itself will be placed in GAD-1XX once the structure exists.*
