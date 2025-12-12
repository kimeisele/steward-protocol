# OPUS - Architectural Decision Records

> **OPUS** = **O**perational **P**lan for **U**nified **S**ystem

This folder contains verifiable architectural documentation for the Steward Protocol.

---

## For Senior Architects

**Your job is verification, not documentation.**

Every OPUS doc claims something is implemented. Your job:
1. **READ** the doc's claims
2. **VERIFY** with `@HARNESS` - grep the files, run the tests
3. **UPDATE** status to reflect reality (not wishful thinking)

### @HARNESS Verification

Each doc should have a `<!-- @HARNESS ... -->` section that is **machine-verifiable**:

```yaml
<!-- @HARNESS
files:
  - path: vibe_core/loaders/container_loader.py
    required: true
tests:
  - tests/unit/test_container_loader.py
wiring:
  - pattern: "class ContainerMounter"
    in: vibe_core/loaders/container_loader.py
absent:
  - pattern: "TODO.*container"
    in: vibe_core/loaders/container_loader.py
-->
```

**Run verification:** The OPUS.md panel auto-verifies these.

---

## Document Index

### Master
| Doc | Title | Focus |
|-----|-------|-------|
| [000](000-INDEX.md) | **Index** | Master navigation (start here) |

### Foundation (001-010)
| Doc | Title | Focus |
|-----|-------|-------|
| [001](001-KERNEL-EXTRACTION.md) | Kernel Extraction | Reduce kernel_impl.py to microkernel |
| [002](002-PHOENIX-CONFIG.md) | Phoenix Config | Config system architecture |
| [003](003-AOS-FOUNDATION-REPAIR.md) | AOS Foundation | Base system fixes |
| [004](004-BOOT-SEQUENCE-AUDIT.md) | Boot Sequence | Kernel boot analysis |
| [005](005-UNIFICATION-ROADMAP.md) | Unification | Consolidation plan |
| [006](006-GAD000-COMPLIANCE-AUDIT.md) | GAD-000 Compliance | Read-without-execute audit |
| [008](008-PRAKRITI-PROTOTYPE.md) | Prakriti Prototype | Internal state workflow |
| [009](009-UNIFIED-STATE-PRAKRITI.md) | Prakriti State | State management |
| [010](010-VERIFICATION-PROTOCOL.md) | Verification | @HARNESS system |

### System (011-015)
| Doc | Title | Focus |
|-----|-------|-------|
| [011](011-LAYERED-ROUTER.md) | Layered Router | Intent routing |
| [012](012-SYSTEM-AGENTS.md) | System Agents | Core agent definitions |
| [014](014-UNIFIED-UI-TRANSPARENCY.md) | UI Transparency | Glass box principles |
| [015](015-CONTAINER-FORMAT.md) | Container Format | `.vibe` container spec |
| [015a](015a-SECURITY-ADDENDUM.md) | Security Addendum | P0 security fixes |

### Operations (016-022)
| Doc | Title | Focus |
|-----|-------|-------|
| [016](016-RUNTIME-SEPARATION.md) | Runtime Separation | CODE/CONFIG/RUNTIME |
| [017](017-SECURITY-AUDIT.md) | Security Audit | Initial security review |
| [018](018-SENIOR-SECURITY-AUDIT.md) | Senior Security | P0-P2 security roadmap |
| [019](019-P0-RELEASE-MILESTONE.md) | P0 Release | Release checklist |
| [020](020-CONTAINER-MIGRATION.md) | Container Migration | Full container strategy |
| [021](021-TEST-ARCHITECTURE.md) | Test Architecture | Test system design |
| [022](022-KERNEL-SCALING.md) | Kernel Scaling | Ephemeral cities, scheduler, federation |

---

## Naming Convention

```
XXX-DESCRIPTIVE-NAME.md
```

- **XXX** = 3-digit number (001-999)
- **DESCRIPTIVE-NAME** = UPPERCASE-WITH-DASHES
- Numbers are chronological, not priority

**Archive:** Non-OPUS files are in `archive/` subdirectory.

---

## Status Rules

| Status | Meaning | Evidence Required |
|--------|---------|-------------------|
| ✅ | Verified working | @HARNESS passes, file:line refs |
| ❌ | Not implemented | Missing files or stub code |
| 🚨 | Violation found | Forbidden pattern detected |
| ⚪ | Unverified | No @HARNESS section |

**A doc without @HARNESS is unverified. Unverified = Untrusted.**

---

## Quick Commands

```bash
# Verify a specific doc's claims
grep -n "TODO\|FIXME\|NotImplementedError" <file_mentioned_in_doc>

# Check if file exists
ls -la <claimed_path>

# Run tests for a component
python -m pytest tests/unit/test_<component>.py -v

# Regenerate OPUS.md verification panel
python boot.py boot
```

---

## Philosophy

> "A doc claiming '✅ implemented' without @HARNESS proof is FICTION."

The verification panel in OPUS.md cross-references every doc against the actual codebase. Red means broken. Green means verified. Grey means unverified.

**Trust the code, not the docs.**
