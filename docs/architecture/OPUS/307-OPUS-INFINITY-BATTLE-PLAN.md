# OPUS-∞ BATTLE PLAN: 24H Sprint - Total System Mastery

**Generated**: 2025-12-26
**Status**: ACTIVE
**Mission**: Complete system consolidation, fix all critical issues, achieve total clarity

---

## EXECUTIVE SUMMARY

8 parallel deep-dive agents analyzed the entire codebase:
- **5,680 Python files** | **154 YAML configs** | **20MB vibe_core**
- **156 OPUS docs** | **13 GAD docs** | **218+ total architecture docs**

### Key Metrics Discovered

| Component | Count | Status |
|-----------|-------|--------|
| Cartridges | 31 | 17 working, 5 broken, 9 incomplete |
| Plugins | 32 | 25 enabled, complex dependency graph |
| Circuits | 24+ | Mixed status |
| Sections | 21 | All loading |
| Tools | 64+ | Via CartridgeService |
| MANAS files | 102 | 80% complete |
| TODOs/FIXMEs | 95+ | Mixed priorities |

---

## CRITICAL ISSUES (P0 - Fix Immediately)

### 1. Security: Signature Verification NOT IMPLEMENTED
**Files**:
- `vibe_core/cartridges/system/archivist/tools/audit_tool.py:101`

**Issue**: Audit tool accepts well-formed signatures without REAL verification
**Status**: ✅ FIXED (OPUS-307)
**Fix Applied**: Real ECDSA verification via crypto.verify_signature()
- Uses trusted keyring from .steward/trusted_keys/
- Graceful fallback if no key available or ecdsa not installed

### 2. Event Emitter Not Wired
**File**: `vibe_core/cortex/engines/circuit_engine.py:928`
**Issue**: `TODO: Wire up event emitter` - Circuit execution missing event emission
**Status**: ✅ FIXED (OPUS-307)
**Fix Applied**: Created _create_emit_event_callback() that wires ActionContext to EventBus

### 3. Task Router Integration Missing
**File**: `vibe_core/task_management/task_manager.py:267`
**Issue**: Legacy MilkOcean router removed, using default MEDIUM priority
**Status**: ✅ FIXED (OPUS-307)
**Fix Applied**: Priority mapping from task priority (0-100) to routing priority (0-3)

### 4. PATH Lobotomy (OPUS-025) - 75% Incomplete
**Issue**: 105+ instances of hardcoded `Path("data/...")` scattered
**Impact**: Cannot reconfigure paths dynamically
**Status**: ⏳ NOT ADDRESSED (needs systematic audit)
**Fix**: Migrate all to `config.paths.data.resolve("key")`

### 5. OPUS-174 Lobotomy Fix - ARCHITECTURAL DECISION
**File**: `vibe_core/plugins/opus_assistant/manas/action_manager.py:576-582`
**Issue**: Returns "requires manual .gitignore edit" instead of auto-fixing
**Status**: ⚠️ INTENTIONALLY NOT FIXED
**Reason**: MANAS is a COGNITIVE KERNEL - it DETECTS and creates INTENTS, but does NOT ACT.
Auto-fixing .gitignore would violate this principle. Also, .gitignore is VISNU-protected.
The detection is valuable; the "fix" correctly requires human intervention.

---

## HIGH PRIORITY ISSUES (P1 - Fix This Sprint)

### Cartridges/Agents

| Issue | File | Status |
|-------|------|--------|
| CLEANER not implemented | `cleaner/cartridge_main.py:39` | ⚠️ GENESIS STUB - Leave as-is |
| ENGINEER agent stub | `engineer/cartridge_main.py:495` | TODO: agent logic |
| HERALD deprecated methods | `herald/cartridge_main.py` | 4 deprecated funcs |
| MANAS cartridge minimal | `manas/cartridge_main.py` | Incomplete |

### Plugins

| Issue | File | Status |
|-------|------|--------|
| ENVOY config missing | `envoy/plugin_main.py:727` | ✅ FIXED - config/envoy.yaml created |
| Doctor offline mode | `doctor/plugin_main.py:86` | TODO: clarify DI |
| TOOLS→ENVOY dependency | `envoy/plugin_main.py:120` | ✅ VERIFIED - Enforced by RuntimeError |

### MANAS Cognitive Kernel

| Issue | File | Status |
|-------|------|--------|
| MAYA simulator unused | `maya_simulator.py` | ✅ FALSE - Integrated in IntentRouter:1020 |
| AKSHARA not integrated | `akshara.py` | ✅ FALSE - Used by 6+ files (viveka, triggers, etc.) |
| Disharmony detection only | `disharmony_detector.py` | ⚠️ CORRECT - MANAS detects, doesn't fix |
| DOJO training incomplete | `dojo/` | ✅ FALSE - Integrated in CognitiveKernel + Maya |
| SILPA refactoring | `cortex/silpa_action.py:844` | TODO: parse commands |

**NOTE**: Original analysis was WRONG about MANAS. Deep dive revealed:
- MAYA: Pre-flight simulation for HIGH/CRITICAL risk intents (Inception model)
- AKSHARA: Sanskrit phonemic resonance matrix for synaptic wiring
- DOJO: Training system with curricula, rooms, synaptic seeding

### Phoenix Config

| Issue | File | Status |
|-------|------|--------|
| No config dir override | `config.py:141` | ✅ FIXED - PHOENIX_CONFIG_DIR env var |
| No validation at load | `config.py:249-272` | ✅ FIXED - validate() now called |
| No schema validation | All sections | No type coercion |
| Circular deps possible | Section loading | No detection |

---

## MEDIUM PRIORITY (P2 - Complete After P0/P1)

### Documentation Gaps
- [ ] Module-level README.md for major subsystems
- [ ] Standardize docstring format (Google-style)
- [ ] Plugin developer guide
- [ ] Deployment & operations runbook
- [ ] Agent wiring diagram

### Technical Debt
- [ ] HERALD→MARKETER content generation migration
- [ ] WATCHMAN + AUDITOR consolidation candidate
- [ ] CHRONICLE + ARCHIVIST consolidation candidate
- [ ] Remove deprecated v2.0 cleanup markers
- [ ] Tool Protocol enforcement (all agents via `self.system.execute_tool()`)

### Testing
- [ ] End-to-end circuit execution tests
- [ ] TaskKernel integration tests
- [ ] MANAS comprehensive test coverage

---

## ARCHITECTURE STRENGTHS (Don't Break)

1. **GAD-000 Compliance**: Operator Inversion paradigm solid
2. **VEDA-4 Auto-Discovery**: Fractal plugin/cartridge/circuit loading
3. **Prakriti State**: Unified state management working
4. **ServiceRegistry DI**: Clean dependency injection
5. **Synaptic Learning**: Hebbian weight updates functional
6. **Dharma Gate**: Ethics checking before execution
7. **VISNU Protection**: 21 kernel files locked

---

## BOOT DEPENDENCY GRAPH

```
Priority 0:   KERNEL (eternal)
Priority 3:   KALA (time first)
Priority 4:   NODE_PULSE (uses KALA)
Priority 5:   STEWARD_PROTOCOL, SARGA_CYCLE, TOOLS ← CRITICAL
Priority 10:  LIFECYCLE, PROCESS_ISOLATION, NEXUS_HOLON
Priority 15:  ENVOY (MUST boot after TOOLS!)
Priority 50:  OPUS_ASSISTANT (MANAS deferred)
Priority 95:  TASK_MANAGER
Priority 100: INTERFACE (renders last)
```

**CRITICAL**: TOOLS (5) → ENVOY (15) dependency must be preserved!

---

## EXECUTION PLAN

### Wave 1: Security & Core (2-4 hours)
1. Fix signature verification in audit_tool.py
2. Wire event emitter in circuit_engine.py
3. Integrate UnifiedRouter in task_manager.py

### Wave 2: Plugin/Cartridge Completion (4-6 hours)
4. Complete CLEANER cartridge process()
5. Create envoy.yaml config section
6. Integrate MAYA simulator in cognitive_kernel
7. Fix OPUS-174 lobotomy repair intent

### Wave 3: Phoenix Config Hardening (2-3 hours)
8. Add PHOENIX_CONFIG_DIR env var support
9. Add validation at load time
10. Add dependency declarations to manifests

### Wave 4: PATH Lobotomy Resolution (4-6 hours)
11. Audit all hardcoded paths
12. Migrate to config.paths.resolve()
13. Test dynamic path configuration

### Wave 5: Testing & Documentation (2-4 hours)
14. Add critical path tests
15. Update OPUS-307 with final status
16. Document all fixes

---

## FILES TO MODIFY

### Critical Path Files
```
vibe_core/cartridges/system/archivist/tools/audit_tool.py
vibe_core/cortex/engines/circuit_engine.py
vibe_core/task_management/task_manager.py
vibe_core/plugins/opus_assistant/manas/action_manager.py
vibe_core/plugins/opus_assistant/manas/cognitive_kernel.py
vibe_core/phoenix/config.py
vibe_core/plugins/envoy/plugin_main.py
vibe_core/cartridges/system/cleaner/cartridge_main.py
```

### Config Files to Create/Update
```
config/envoy.yaml (NEW)
config/phoenix.yaml (update)
```

---

## SUCCESS CRITERIA

1. [ ] All P0 issues resolved and tested
2. [ ] Signature verification actually validates
3. [ ] Event emitter wired and emitting
4. [ ] Task router dynamically prioritizing
5. [ ] PATH lobotomy < 25% remaining
6. [ ] MANAS cognitive kernel at 90%+ complete
7. [ ] All tests passing
8. [ ] Commit and push with clean pre-commit

---

## NOTES

- **Don't touch boot_sequence.py** - It works, 98% coverage, risky to modify
- **ManifestRegistry is fine** - Generic loader, not a consolidation target
- **ServiceRegistry is DI** - Use it, don't bypass
- **Pre-commit hooks active** - VISNU protection, ruff format, all must pass

---

*"Ein System, ein Service, ein Cache. Jetzt mit totaler Klarheit."*
