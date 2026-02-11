# Lotus Architecture Audit
**Date:** 2026-02-10 | **Branch:** feature/lotus-architecture-audit

## 1. Benchmark Results (Verified)

| Operation | Cold | Warm | Hot Path? |
|---|---|---|---|
| `tick()` | — | **0.26ms** | ✅ YES (250ms budget → 249ms headroom) |
| `rank_words()` vectorized | 328ms | **32ms** | ❌ NO (only on `__call__`) |
| `resonate('dharma')` | 97ms | — | ❌ NO |
| `lotus_core('test')` | **2288ms** | **106ms** | ❌ NO (user-triggered, not heartbeat) |

**Verdict:** Gemini's "1300ms blocking violation" is **wrong for the hot path**. `tick()` is 0.26ms. `rank_words` is never called from the heartbeat loop. The 2.3s cold start is a one-time import/cache penalty, not a per-tick cost.

## 2. Lotus Class Inventory

### A. DUPLICATE DEFINITIONS (Problem)

| Class | File 1 | File 2 | Identical? |
|---|---|---|---|
| `LotusProtocol` | `mahamantra/protocols/_lotus.py:317` | `protocols/substrate/mantra/lotus.py:350` | ~90% same |
| `LotusBase` | `mahamantra/protocols/_lotus.py:359` | `protocols/substrate/mantra/lotus.py:456` | ~85% same |
| `LotusMode` | `mahamantra/protocols/_lotus.py:103` | `protocols/substrate/mantra/lotus.py:146` | Identical |
| `LotusState` | `mahamantra/protocols/_lotus.py:212` | `protocols/substrate/mantra/lotus.py:232` | Different (dataclass vs TypedDict) |
| `LotusRoute` | `mahamantra/protocols/_lotus.py:270` | `protocols/substrate/mantra/lotus.py:249` | Different (dataclass vs TypedDict) |
| `LotusPetal` | `mahamantra/protocols/_lotus.py:118` | `protocols/substrate/mantra/lotus.py:202` | Different (dataclass vs TypedDict) |

**This is the core structural problem.** Two parallel Lotus type systems that diverged.

### B. ACTUAL RUNTIME CLASSES (Used)

| Class | File | Role | Used By |
|---|---|---|---|
| `MahamantraLotus` | `substrate/lotus_core.py` | Root singleton, `__call__`, `tick()`, `vibrate()` | Everything |
| `LotusNode` | `substrate/lotus_types.py` | Auto-discovery tree (`__getattr__` → folder) | `MahamantraLotus` inherits |
| `LotusPath` | `substrate/lotus_types.py` | Path segments for tree traversal | `LotusNode` |
| `LotusBridgeSubscriber` | `services/lotus_bridge.py` | VenuService → Singularity bridge | VenuService beat dispatch |
| `LotusBase` | `protocols/substrate/mantra/lotus.py` | ABC for Lotus-aware services | `ChatService` |

### C. DATA STRUCTURE CLASSES (Adapters)

| Class | File | Role |
|---|---|---|
| `LotusIPRouter` | `adapters/network.py` | O(1) IPv4 routing via 16-ary radix |
| `LotusBio` | `adapters/bio.py` | O(1) DNA k-mer index |
| `_LotusEngine16` | `adapters/routing.py` | 16-bit radix engine |
| `_GenericLotusEngine` | `adapters/routing.py` | N-bit radix engine |

These are **correctly named** — they use the Lotus (16-ary radix) as a data structure. No problem here.

### D. RESEARCH/DEMO (Not production)

| File | Purpose |
|---|---|
| `research/hardware_lotus.py` | Hardware pipeline simulation |
| `research/lotus_acintya.py` | Philosophical exploration |
| `research/lotus_full_spectrum.py` | Full spectrum analysis |
| `research/lotus_radix_n.py` | N-ary radix experiments |
| `research/lotus_tree.py` | Tree visualization |

## 3. The Real Problem: Two Type Systems

```
vibe_core/
├── mahamantra/protocols/_lotus.py      ← "acintya level" (dataclasses)
│   ├── LotusProtocol (Protocol)
│   ├── LotusBase (ABC)
│   ├── LotusMode, LotusPetal, LotusState, LotusRoute (dataclass)
│   ├── LotusTree, LotusHologram
│   └── LotusProtocolDef
│
├── protocols/substrate/mantra/lotus.py  ← "substrate level" (TypedDicts)
│   ├── LotusProtocol (Protocol)         ← DUPLICATE
│   ├── LotusBase (ABC)                  ← DUPLICATE
│   ├── LotusMode                        ← DUPLICATE
│   ├── LotusPetal, LotusNode, LotusState, LotusRoute (TypedDict)
│   ├── LotusHeartbeat
│   └── LotusRegistry
│
├── mahamantra/substrate/lotus_types.py  ← ACTUAL runtime (LotusNode tree)
└── mahamantra/substrate/lotus_core.py   ← ACTUAL runtime (MahamantraLotus)
```

**The runtime uses `lotus_types.py` and `lotus_core.py`.** The two protocol files (`_lotus.py` and `mantra/lotus.py`) are **legacy definitions that diverged** and are barely imported.

## 4. Who Imports What? (Verified)

| File | Importers | Status |
|---|---|---|
| `mahamantra/protocols/_lotus.py` | 6 files (chat_service, chat_refinement, chat_substrate_bridge, _gad, _steward, _graph) | **CANONICAL** |
| `protocols/substrate/mantra/lotus.py` | **0 files** | **DEAD CODE** — marked deprecated |
| `mahamantra/substrate/lotus_types.py` | 2 files (lotus_core, lotus_projection) | **RUNTIME** |
| `mahamantra/substrate/lotus_core.py` | Everything (via `mahamantra` singleton) | **RUNTIME** |

## 5. OS-Graph Mapping (Current State)

| OS Concept | Current Component | Status |
|---|---|---|
| **Kernel** | `Singularity` (tick, broadcast) | ✅ Solid |
| **Heartbeat/Clock** | `VenuOrchestrator` + `VenuService` | ✅ Unified |
| **Process Scheduler** | `ShadowReactor` (position-gated) | ✅ Works |
| **IPC/Bus** | `Singularity._listeners` + `VenuOrchestrator._subscribers` | ✅ Consolidated |
| **Filesystem** | `LotusNode` (folder = existence) | ⚠️ Mixed with FS fallback |
| **Memory** | `Antaranga` (bytearray) | ⚠️ Split-brain risk |
| **Syscall Interface** | `PanchaTattva` (5 questions) | 🔴 Exists as protocol, not as API |
| **Device Drivers** | Adapters (network, bio, audio) | ✅ Clean |
| **Shell** | `lotus_cli.py` | ⚠️ Exists but not unified |

## 6. What's Missing for "Universal OS"

1. **Single Lotus Protocol** — Merge the two diverged definitions into ONE SSOT
2. **Pancha Tattva as Syscall** — The 5 questions should be the ONLY way to interact with the kernel
3. **Semantic Namespace** — `LotusNode.__getattr__` is the right idea but mixes FS discovery with seed data
4. **Input Pipeline** — Text/Audio/Any → RAMA coords → Mantra position → Response (exists but not unified as "the OS interface")
5. **Session/State** — No concept of "user session" or "running process" beyond heartbeat ticks

## 7. Recommended Actions (Priority Order)

1. **DEDUPLICATE:** Determine which `LotusProtocol` is canonical, delete the other
2. **SSOT TYPES:** One file for all Lotus types (merge `_lotus.py` TypedDicts with dataclasses)
3. **PANCHA API:** Formalize the 5 Pancha Tattva questions as the universal interface
4. **NAMESPACE:** Clean `LotusNode` to be pure seed-based (no FS fallback for core paths)
5. **INPUT UNIFICATION:** Single entry point: any input → RAMA → DIW → response
