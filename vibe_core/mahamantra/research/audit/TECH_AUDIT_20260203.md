# TECHNICAL AUDIT REPORT: Steward Protocol Mahamantra
**Date**: 2026-02-03  
**Commits analyzed**: Last 48h (124 commits)  
**Codebase**: vibe_core/mahamantra/ (346 Python files, 97,405 LOC)

---

## EXECUTION ARCHITECTURE (Verified via AST Analysis)

### Entry Point Chain
```
python -m vibe_core.mahamantra "input"
  ↓ __main__.py:main() [7 imports, 6 function calls]
  ↓ adapters/cli.get_adapter().execute()
  ↓ mahamantra(input)  # Callable instance, not function
  ↓ MahamantraLotus.__call__() [_mahamantra_lotus.py:233]
  ↓ ExecuteResult dict
```

### Lazy Loading Mechanism
- **__init__.py** uses `__getattr__` (line 35) for O(1) import time
- `mahamantra` resolves to `get_mahamantra()` → singleton instance
- **NO circular dependencies detected** (AST-based cycle finder: 0 results)

### Import Dependency Stats
```
protocols._seed:       154 imports (SSOT)
substrate.seed:         36 imports
substrate.algorithm.maha: 9 imports
adapters.compression:   8 imports
```

---

## CORE COMPUTATION FLOW (from __call__)

### 9 NavaBhakti Steps (Line 233-420 in _mahamantra_lotus.py)
1. **SRAVANAM**: Input → str/MahaCell
2. **KIRTANAM**: MahaCompression.compress() → seed (int)
3. **PADA_SEVANAM**: MahaModularSynth.transform(seed) → attractor
4. **ARCANAM**: seed % 37 == 0 (parampara check)
5. **VANDANAM**: GitaResonance.match(attractor) → verse
6. **DASYAM**: attractor % 16 → position (0-15)
7. **SAKHYAM**: MahaCellUnified.create() [if needed]
8. **ATMA_NIVEDANAM**: Return ExecuteResult

### Dependencies (traced)
```python
# Line 274
compressor = MahaCompression()  # adapters/compression.py

# Line 284
synth = MahaModularSynth(default_preset="quantum")  # substrate/algorithm/maha.py

# Line 298
verse = match_attractor(attractor)  # adapters/gita_resonance.py
```

---

## DEAD CODE ANALYSIS

### Unused Functions (0 usages detected)
```
orchestrator.py:
  - verify_divinity()
  - harmonize()
  - is_sunya()
  - extract_diw()

_types.py:
  - LilaState (class)
  - GitaRoute (class)

adapters/classification.py:
  - MahaClassifier (entire class)
  - lotus_array(), ipv4_router(), neural_network(), blockchain()
```

**Total dead LOC estimate**: ~2,000-3,000 (in adapters/classification.py alone)

---

## CLI ARCHITECTURE

### Entry Points Found
1. **mahamantra/__main__.py** ← THE ONE (current)
2. cli/unified_cli.py (deprecated warnings present)
3. cli/main.py (delegates to mahamantra)
4. mahamantra/cli/entry.py (deprecated warnings present)
5. mahamantra/cli/steward.py (wraps mahamantra instance)

### CLI Adapter (adapters/cli.py)
- **CellFingerprint** matching (multi-dimensional):
  - position (0-15)
  - payload_size
  - prana
  - cycle
- Calls: `mahamantra(input)` at line 143, 171

---

## TEST COVERAGE

### Test Files
```
tests/mahamantra/: 127 test files
tests/hardening/: test_mahamantra_substrate_attacks.py
tests/unit/services/: test_maha_compute_service.py
```

### Critical Tests Missing (grep found no matches)
- No tests for MahamantraLotus.__call__ directly
- No integration tests for full entry → output flow
- Chamber/Sankirtan have tests but in separate files

---

## RECENT CHANGES (Last 12 hours - Git Log)

### Syllable Infrastructure (PR #717)
```
feat(research): add ResonanceResponder - Intent to Syllables pipeline
  → resonance_response.py (557 LOC)
feat(research): wire UniversalPhoneticBridge into resonance pipeline
  → Adds Varga/Sthana phonetic analysis
```

**Location**: research/ folder (not in production import path)

### CLI Consolidation (PR #711)
```
feat(cli): MAHAMANTRA IS THE KING - unified entry point
refactor(cli): rename maha_cli.py to cli.py - "das maha steigt dir zu Kopf"
docs(cli): add consolidation plan + deprecation warnings
```

**Status**: Partially complete (4/5 entry points marked deprecated)

### NAGA Flood (PR #714, #716)
```
fix(naga): complete NAGA flood to ~95% - cognitive layer blessed
fix(naga): add _naga_flooded blessing to key services
```

**Effect**: Auto-blessing via `__mahajana__` attribute (186 files now have it)

---

## KERNEL ARCHITECTURE

### Two Kernels Detected

**1. MahaKernel** (mahamantra/kernel/maha_kernel.py - 287 LOC)
- Implements PanchaTattvaProtocol
- Uses MahamantraLotus.__call__ for execution
- Delegates ALL to mahamantra

**2. RealVibeKernel** (kernel_impl.py - 200+ LOC read)
- Legacy implementation
- Already integrated: `mahamantra.bootstrap(silent=True)` at line 170
- Wraps services with MahamantraProxy (Balarama Pattern)

**Relationship**: Migration in progress, both functional

---

## CHAMBER/SANKIRTAN INFRASTRUCTURE

### SankirtanChamber (substrate/chamber.py)
```python
class SankirtanChamber:
    _orchestrator: VenuOrchestrator
    _registry: SiksastakamRegistry (512 slots)
    _resonator: MahaResonator
    
    def dance(cell) → cell_out  # Single transform
    def kirtan(cell, cycles=1)  # 16-step round
    def sankirtan(cells)        # Multi-cell
```

**Capacity**: MALA = 108 cells  
**Modes**: SOLO, CALL_RESPONSE, CHORUS

### Auto-Wiring (substrate/sankirtan.py - 1,468 LOC!)
```python
# 4-Phase Pipeline
GENESIS  (0-3):  WAKE/LOAD/ALLOC
DHARMA   (4-7):  COMPILE/CHECK
KARMA    (8-11): EXEC/INJECT
MOKSHA   (12-15): FLUSH/LOG/SEAL
```

**Injects**:
```python
__mahajana__ = "guardian_name"
__position__ = 0-15
__genesis__ = "0x..." (% 37 == 0)
```

**Coverage**: 60+ folder mappings in FOLDER_MAHAJANA_MAP

---

## IMPORT STATISTICS (from __init__.py)

### Exports via __all__ (68 items)
- MahamantraLotus (class)
- mahamantra (singleton instance)
- 16+ constants (WORDS, TRINITY, PARAMPARA, etc.)
- 10+ protocols (GADProtocol, MahaCell, etc.)
- 20+ adapters and utilities

### Lazy Loading Coverage
- All adapters: Lazy
- All protocols: Lazy (via __getattr__)
- substrate modules: Partially lazy
- research/: NOT in lazy load path

---

## RESEARCH FOLDER STATUS

### Size
```
research/: ~36,000 LOC (37% of total mahamantra/)
- resonance_response.py: 557 LOC (production-ready)
- git/lab.py: 237 LOC  
- CLI/: 4 analysis docs
```

### External Imports Found
```
8 files import from research/
Most used:
  - research.maha_compression (deprecated, use adapters/)
  - research.resonance_response (NEW, used in chat.py)
```

### Production vs Research
- resonance_response.py imports production modules (MahaModularSynth, GitaResonance)
- Can be promoted to adapters/

---

## MAHAMANTRA ALGORITHM (substrate/algorithm/maha.py - 816 LOC)

### Classes
```python
class MahaAlgorithm16:
    def transform(seed) → value  # Standard 16-step

class MahaModularSynth:
    def transform(seed, preset="quantum") → value  # Parameterized
```

### Optimization
```python
# 8:2:2 Algebraic Form
_MAHA_OSCILLATE_LUT: Tuple[int, ...] (137 entries)
# O(1) lookup for mod=137
# O(9) for other mods (vs O(16) naive)
```

### Presets
- classical: mod=17
- quantum: mod=137 (default)
- trinity: mod=3
- pancha: mod=5
- wide: mod=512

---

## FINDINGS SUMMARY

### Working Well
1. Entry point is clean (__main__.py → cli adapter → mahamantra instance)
2. NO circular dependencies (AST verified)
3. Lazy loading reduces import time
4. Algorithm is optimized (O(1) for standard case)
5. Test coverage exists (127 files)

### Technical Debt
1. 5 entry points (1 active, 4 deprecated but not removed)
2. Dead code in adapters/classification.py (~2k LOC unused)
3. research/ folder needs audit (36k LOC, unclear what's prod vs experiment)
4. Duplicate service definitions (services/ vs protocols/mahajanas/)
5. steward.py wraps mahamantra but adds no value (pure formatter)

### No Evidence Found For
- Circular imports (searched, found 0)
- Missing SSOT (protocols._seed used by 154 files)
- Broken imports (AST parsing succeeded on all files)

---

## FILES ANALYZED
- Total Python files: 346
- Failed to parse: 0
- With mahajana declaration: 186
- Test files: 127
- Dead functions found: 30+
