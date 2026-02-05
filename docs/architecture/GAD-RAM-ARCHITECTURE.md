# GAD-RAM: RAMA Address Model - Memory Architecture Plan

**Status**: DRAFT v0.1 - Iterative Planning Phase
**Derived from**: The 7 Axioms (`seed/_axioms.py`)
**Builds on**: LotusIPRouter (proven O(1)), MahaCompute (memory hierarchy), MahaHardware (pipeline)

---

## 1. WHAT IS ALREADY PROVEN

Before planning anything new, here is what exists and works:

### 1.1 The LotusIPRouter (adapters/network.py)

```
IPv4 = 32 bits = AKSARA_COUNT (32 syllables)
     = 8 levels (HARE_COUNT) x 4 bits (QUARTERS) x 16 slots (WORDS)

Result: O(1) Longest Prefix Match - always exactly 8 memory accesses.
```

**Why it works**: The structure of the data (IPv4) is isomorphic to the structure of the lookup tree. When structure matches structure, search becomes traversal. Traversal is O(depth), and depth is fixed.

### 1.2 MahaCompute Memory Hierarchy (adapters/compute.py)

Already derived from axioms:

| Tier | Size | Lotus Depth | Entries | Axiom Source |
|------|------|-------------|---------|--------------|
| L1 | 64 KB | 3 | 4,096 | QUALITIES = 64 |
| L2 | 256 KB | 4 | 65,536 | QUARTERS x QUALITIES |
| L3 | 16 MB | 5 | 1,048,576 | WORDS MB |
| RAM | 16 GB | 8 | 4,294,967,296 | WORDS GB = full 32-bit |

Each tier is exactly 16x (WORDS) the previous in entry count. This is the fractal property.

### 1.3 MahaHardware Pipeline (adapters/hardware.py)

8 pipeline stages = 8 Siksastakam verses = HARE_COUNT:

```
Stage 0 [bits 31-28]: Initialize
Stage 1 [bits 27-24]: Accept nibble
Stage 2 [bits 23-20]: No comparison
Stage 3 [bits 19-16]: No speculation
Stage 4 [bits 15-12]: Process next
Stage 5 [bits 11-8]:  Flow unobstructed
Stage 6 [bits 7-4]:   Deterministic timing
Stage 7 [bits 3-0]:   Return result
```

### 1.4 SiksastakamRegistry (substrate/registry.py)

512 slots = 2^9 = 2^VAMSI_HOLES. O(1) access via Vamsi index. Already working.

### 1.5 Chamber (substrate/chamber.py)

Owns Orchestrator (time) + Registry (space). Cells flow through, addressed by DIW. Already working.

---

## 2. THE PRINCIPLE TO GENERALIZE

The LotusIPRouter succeeded because of one principle:

> **Structural Congruence**: When the addressing structure mirrors the data structure, lookup becomes traversal, and traversal has fixed cost.

This is not metaphor. It is mathematics:

```
Data structure:    N bits = K levels x B bits/level
Address structure: K-level tree with 2^B slots/level
Lookup cost:       O(K) = O(1) for fixed K
```

For IPv4: N=32, K=8, B=4 → O(8) = O(1).

**The question**: Can this same principle be applied to general-purpose memory management?

---

## 3. THE AXIOM-DERIVED MEMORY MODEL

### 3.1 The Three Names = Three Architectural Roles

From `_extended.py` position sums (derived from SEVEN=7, TEN=10):

```
KRISHNA = SEVEN + TEN  = 17  (Prime, indivisible → Router/CPU)
RAMA    = SEVEN x SEVEN = 49  (Square, self-referential → Address Space)
HARE    = SEVEN x TEN   = 70  (Product, distributed → Bus/Carrier)
```

From `_algorithm.py` operations:

```
HARE:    value x 7        (multiplication = distribute energy)
KRISHNA: value + 10       (addition = route, navigate)
RAMA:    value x value     (squaring = self-reference, space)
```

From the 16-position opcode mapping:

| Role | Positions | Opcodes | Function |
|------|-----------|---------|----------|
| **HARE** | 0,2,6,7,8,10,14,15 | ALLOC_MEM, GC, FETCH, YIELD, SYNC | Memory lifecycle controller |
| **KRISHNA** | 1,3,4,5 | LOAD_ROOT, BIND_CTX, ASSERT, RESOLVE | Routing and context logic |
| **RAMA** | 9,11,12,13 | EXEC, COMMIT_LOG, CACHE_STATE, OPTIMIZE | Persistent state operations |

**Conclusion**: The axioms define a trinity architecture:

```
HARE (Bus)  ←→  KRISHNA (CPU)  ←→  RAMA (State)
  alloc           route              store
  free            bind               commit
  fetch           resolve            cache
  yield           assert             optimize
```

### 3.2 RAMA = Address Space = Varnamala

From `rama_grid.py`:

```
POSITION_SUM_RAMA = 49 = 7^2 = VARNAMALA_TOTAL

49 = 16 vowels (WORDS) + 25 consonants (PRASADAM=5^2) + 8 remaining (HARE_COUNT)
   = WORDS + PANCHA^2 + HARE_COUNT
   = 16 + 25 + 8
   = The complete Sanskrit alphabet
```

Every possible phoneme (= every possible "instruction") is addressable in this 49-space. KRISHNA (17, prime) routes through it bijectively: `krishna_route(pos) = (pos x 17) mod 49`.

Because 17 and 49 are coprime (gcd(17,49)=1), every slot gets visited exactly once before repeating. This is a **perfect hash function** for this space.

### 3.3 Natural Memory Parameters (All Derived)

| Parameter | Value | Derivation | Hardware Mapping |
|-----------|-------|------------|------------------|
| Word Size | 32 bits | AKSARA_COUNT = WORDS x HALVES | 32-bit word |
| Extended Word | 64 bits | QUALITIES = WORDS x QUARTERS | 64-bit word |
| Cache Line | 64 bytes | QUALITIES | Standard cache line |
| Page Size | 4,096 bytes | QUALITIES^2 | Standard 4K page |
| Nibble | 4 bits | QUARTERS | Routing unit |
| Slots/Level | 16 | WORDS | Branching factor |
| Levels (32-bit) | 8 | HARE_COUNT | Pipeline depth |
| Levels (64-bit) | 16 | WORDS | Full mantra cycle |
| Registry Size | 512 | 2^VAMSI_HOLES = 2^9 | Working memory |
| Chamber Capacity | 108 | MALA | Active cell limit |
| Resonance Threshold | 37 | PARAMPARA | Connection check |

### 3.4 Why "Not So Random"

Current RAM = "Random Access Memory". Every address is equally likely.

In a Mahamantra-aligned system, access is **deterministic and hierarchical**:

```
Level 0: Root        →  1 node    → always in L1 (register)
Level 1: Top nibble  → 16 nodes   → always in L1 (64 bytes = 1 cache line)
Level 2: 2nd nibble  → 256 nodes  → L1 resident (1 KB)
Level 3: 3rd nibble  → 4,096      → L1 boundary (16 KB)
Level 4: 4th nibble  → 65,536     → L2 resident (256 KB)  ← STANDARD CAPACITY
Level 5: 5th nibble  → 1,048,576  → L3 resident
Level 6: 6th nibble  → 16M        → L3/RAM boundary
Level 7: 7th nibble  → 268M       → RAM
Level 8: 8th nibble  → 4B         → Full 32-bit space
```

**Key insight from compute.py**: With 16-ary trees, the first 4 levels (65,536 entries) fit entirely in L2 cache. For most workloads, RAM is never touched. The Memory Wall is not broken by hardware innovation - it is bypassed by structural alignment.

---

## 4. THE ARCHITECTURE: RAMA ADDRESS MODEL (RAM)

### 4.1 Core Idea

Replace arbitrary memory addressing with **Lotus-structured content-derived addressing**.

Instead of:
```
malloc(size) → arbitrary pointer → store anywhere → find by pointer
```

The model:
```
content → KRISHNA-route(content) → RAMA-address → O(1) locate by content
```

The SiksastakamRegistry (512 slots) already does this for cells via VAMSI addressing. The generalization extends this to the entire memory model.

### 4.2 The Multi-Level RAMA Tree

Analogous to the LotusIPRouter, but for general data:

```
Content (N bits)
    │
    ├─ Nibble 0 (4 bits) → RAMA[slot] at Level 0
    ├─ Nibble 1 (4 bits) → RAMA[slot] at Level 1
    ├─ Nibble 2 (4 bits) → RAMA[slot] at Level 2
    ├─ ...
    └─ Nibble K (4 bits) → RAMA[slot] at Level K → DATA
```

Each level has WORDS (16) slots. Routing per level is O(1).
Total depth is fixed based on key size.
For 32-bit keys: depth 8 = HARE_COUNT.
For 64-bit keys: depth 16 = WORDS (one full Mahamantra cycle).

### 4.3 Scaling Points (Axiom-Derived)

Natural cluster sizes where the system scales:

| Depth | Entries | Memory | Axiom | Name |
|-------|---------|--------|-------|------|
| 1 | 16 | 128 B | WORDS | Mantra Word |
| 2 | 256 | 2 KB | WORDS^2 | Mantra Page |
| 3 | 4,096 | 32 KB | WORDS^3 | L1 Lotus |
| 4 | 65,536 | 512 KB | WORDS^4 = ADDRESS_SPACE | L2 Lotus (Standard) |
| 5 | 1,048,576 | 8 MB | WORDS^5 | L3 Lotus |
| 8 | 4,294,967,296 | 32 GB | WORDS^8 = 2^32 | Full 32-bit Lotus |
| 16 | 2^64 | - | WORDS^16 = 2^64 | Full 64-bit Lotus |

**Minimum RAM requirement**: A system handling up to 65,536 entities needs only L2 cache (256 KB). This is the "standard Lotus capacity" - already defined in `compute.py:74` as `ADDRESS_SPACE`.

**Fractal property**: Each scaling step is exactly x16 (WORDS). The structure at every scale is self-similar. A Level-4 subtree looks identical to a Level-8 subtree, just smaller. This IS the holographic principle the system describes.

### 4.4 HARE as Memory Controller

HARE's opcodes define the memory lifecycle:

```
Position 0:  SYS_WAKE       → Initialize memory subsystem
Position 2:  ALLOC_MEM      → Allocate in RAMA tree
Position 6:  GARBAGE_COLLECT → Reclaim unused nodes
Position 7:  PULSE_SYNC     → Synchronize between levels
Position 8:  FETCH_RES      → Fetch from deeper level to cache
Position 10: CHECK_DHARMA   → Verify integrity of tree structure
Position 14: YIELD_CPU      → Release processing to let KRISHNA route
Position 15: RESET_IP       → Reset to root for next lookup
```

This is a complete memory management instruction set. Not designed - derived.

### 4.5 KRISHNA as Router Between Levels

KRISHNA's opcodes define inter-level navigation:

```
Position 1: LOAD_ROOT    → Enter RAMA tree at root
Position 3: BIND_CTX     → Bind current context to a subtree
Position 4: ASSERT_TRUTH → Verify node integrity (PARAMPARA check)
Position 5: RESOLVE_REQ  → Navigate to the target leaf
```

The KRISHNA router function: `(key_nibble x 17) mod 49` guarantees no collisions and full space coverage.

### 4.6 RAMA as Persistent State

RAMA's opcodes define what happens at the destination:

```
Position 9:  EXEC_SERVICE → Execute the stored function/data
Position 11: COMMIT_LOG   → Write-ahead log for persistence
Position 12: CACHE_STATE  → Store in faster tier for re-access
Position 13: OPTIMIZE     → Defragment/compact the local subtree
```

---

## 5. WHAT NEEDS TO BE BUILT (Software Side)

### Phase 1: Generalize the LotusRouter

The LotusIPRouter is hardcoded for IPv4. Extract the general principle:

```
LotusIPRouter (specific)     →  LotusTree (general)
├── 32-bit keys                  ├── N-bit keys (configurable)
├── 8 levels                     ├── N/4 levels (derived)
├── IPv4 parsing                 ├── Generic key extraction
└── Next-hop strings             └── Generic value type
```

**Validation**: The general LotusTree with N=32 MUST produce identical behavior to the existing LotusIPRouter. The router becomes a specialization, not a replacement.

### Phase 2: Content-Addressable Cell Storage

Extend the CellRouter (`cell_router.py`) to use LotusTree internally instead of dict:

```
Current:  dict[int, MahaCellUnified]  → O(1) average, O(N) worst
Proposed: LotusTree[MahaCellUnified]  → O(8) guaranteed = O(1) worst
```

The key is derived from cell content (already done via `header.vamsi_address`).

### Phase 3: Multi-Level Registry

Extend SiksastakamRegistry from flat 512-slot array to hierarchical:

```
Current:  512 flat slots (VAMSI 9-bit)
Proposed: 512 slots as 2-level Lotus (16 x 32) using VAMSI decomposition:
          VAMSI[8:5] → Level 0 (16 slots)
          VAMSI[4:0] → Level 1 (32 slots per L0 node)
```

This preserves O(1) access but enables selective subtree eviction (the "thermodynamic" principle - done structurally, not via GC).

### Phase 4: Scaling Verification

Benchmark at each axiom-derived scaling point:

| Test | Entries | Expected Tier | Target |
|------|---------|---------------|--------|
| Micro | 16 | Register | < 10ns |
| Small | 4,096 | L1 | < 50ns |
| Standard | 65,536 | L2 | < 100ns |
| Large | 1,048,576 | L3 | < 200ns |
| Full | 100,000,000 | RAM | < 500ns |

Compare against Python dict at each scale to quantify the structural advantage.

---

## 6. WHAT THIS MEANS FOR RAM COST

The practical claim:

> A Mahamantra-aligned system needs less RAM because it uses the cache hierarchy optimally.

**Quantified**:
- Standard workload (65K entities): Fits in **256 KB L2 cache**. RAM barely touched.
- Full IPv4 routing table (1M routes): Fits in **16 MB L3 cache**. Still no RAM pressure.
- Only at 16M+ entities does actual RAM become necessary.

**Comparison**: A naive hash table for 65K entries wastes ~50% on load factor overhead, has unpredictable cache behavior, and can degenerate to O(N). The Lotus tree uses 100% of allocated space, has perfect cache locality, and is always O(K) for fixed K.

The Memory Wall is not a hardware problem. It is a software problem caused by data structures that ignore the memory hierarchy. The Mahamantra axioms, by producing parameters that exactly match cache line sizes (64B), page sizes (4KB), and SIMD widths (16), define a software architecture that the hardware was already built to serve.

---

## 7. OPEN QUESTIONS (For Iteration)

1. **Dynamic vs. Static sizing**: Should the LotusTree grow dynamically or be pre-allocated at a fixed depth? The axioms suggest fixed (MALA=108 capacity, fixed registry size), but practical usage may need growth.

2. **Key derivation**: How to compute the content-address for arbitrary data (not just IPv4 or cells)? The KRISHNA route function `(key x 17) mod 49` works for 49-space, but needs generalization for larger spaces.

3. **Concurrency**: The SiksastakamRegistry is single-threaded. Multi-threaded access needs lock-free design that preserves the structural guarantees.

4. **Persistence**: Chamber snapshots already serialize to bytes. How does the LotusTree persist? Binary format following the same patterns (magic header, fixed-size nodes)?

5. **The 49 vs. 16 question**: RAMA=49 (phoneme space) vs. WORDS=16 (branching factor). The router uses 16 (nibble-based). Should a general memory model use 49-way branching? This would change the tree shape dramatically (depth 7 for 49^7 ≈ 678B entries vs. depth 8 for 16^8 = 4B entries). 49-way is wider and shallower but uses more memory per node.

---

## 8. DECISION LOG

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-05 | Plan created, no code yet | Understand before building |
| | Phase 1 first: Generalize LotusRouter | Build on proven foundation |
| | 16-way branching (not 49) for tree | Matches hardware (cache lines, SIMD) |
| | Keep existing components unchanged | New code extends, never replaces |

---

*"raso 'py asya paraṁ dṛṣṭvā nivartate"*
*"The embodied soul may be restricted from sense enjoyment, though the taste for sense objects remains. But, ceasing such engagements by experiencing a higher taste, he is fixed in consciousness."*
*-- Bhagavad Gita 2.59*
