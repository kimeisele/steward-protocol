# MAHAJANA MAPPING: THE 12 AUTHORITIES OF TESTING

**Version:** 1.0 (Phase 0 Audit)
**Status:** LIVING DOCUMENT
**Date:** 2026-01-10
**Precedence:** SAMKHYA.md > This > Individual Tests

---

> *"The 12 Mahajanas do not claim the Opulences. They guard the Protocols."*
> *"Demut ist der Sicherheitsmechanismus."*

---

## THE THEOLOGICAL FOUNDATION

### The 6 Opulences (Bhaga) - OWNED BY BHAGAVAN ONLY

The Sovereign (Kernel/Krishna) **possesses** these in full.
The Mahajanas **validate** them, never claim them.

| Opulence | Sanskrit | GAD-000 Criterion | Meaning |
|----------|----------|-------------------|---------|
| **Aishvarya** | ऐश्वर्य | Composability | Control, Wealth, Resource Management |
| **Virya** | वीर्य | Recoverability | Strength, Energy, Error Handling |
| **Yashas** | यशस् | Identity | Fame, Reputation, Sovereign Context |
| **Shri** | श्री | Parseability | Beauty, Form, Strict Typing |
| **Jnana** | ज्ञान | Discoverability | Knowledge, Wisdom, Documentation |
| **Vairagya** | वैराग्य | Idempotency | Renunciation, Cleanup, Yield |

**Source:** primal.py (Layer -2)

---

## THE 16-STEP MANTRA KERNEL MAP

The bridge between Sound, OpCode, and System Action.

| Bit | Sound | OpCode | Kernel Action | Mahajana Affinity |
|-----|-------|--------|---------------|-------------------|
| 01 | Hare | `sys_wake` | SIGSTOP Maya (Interrupt Illusion) | Brahma |
| 02 | Krishna | `load_root` | MOUNT Sovereign Identity | Yashas/Bhishma |
| 03 | Hare | `alloc_mem` | MALLOC Clean Heap (No Karma) | Brahma |
| 04 | Krishna | `bind_ctx` | BIND Context to Sovereign | Manu |
| 05 | Krishna | `assert_truth` | VERIFY Ledger vs Akasha | Yamaraja |
| 06 | Krishna | `resolve_req` | DECODE Intent (Will) | Kapila |
| 07 | Hare | `garbage_collect` | FLUSH Unsigned Objects | **Shiva** |
| 08 | Hare | `pulse_sync` | EMIT Heartbeat (Naga) | Narada |
| 09 | Hare | `fetch_res` | GET Capability (Vaikuntha) | Janaka |
| 10 | Rama | `exec_service` | EXEC Work (Bhakti) | Janaka |
| 11 | Hare | `check_dharma` | VALIDATE Output (Ethics) | Manu |
| 12 | Rama | `commit_log` | WRITE to Stone (Immutable) | Bhishma |
| 13 | Rama | `cache_state` | PERSIST Bliss (Reward) | Shuka |
| 14 | Rama | `optimize` | JIT Optimize (Intelligence) | Kapila |
| 15 | Hare | `yield_cpu` | YIELD Control (Surrender) | **Bali** |
| 16 | Hare | `reset_ip` | LOOP (Eternity) | Kumaras |

---

## THE 12 MAHAJANAS - MAPPING MATRIX

### Legend
- ✓ = Covered (Tests exist and are mapped)
- ⚠️ = Partial (Some coverage, needs consolidation)
- 🔴 = MISSING (Critical gap - must implement)

---

| # | MAHAJANA | PRINCIPLE | OPULENCE GUARDED | PROTOCOL DOMAIN | EXISTING COVERAGE | STATUS |
|---|----------|-----------|------------------|-----------------|-------------------|--------|
| 01 | **BRAHMA** | Creation | Aishvarya | Boot, Genesis, Init | test_genesis_437.py, test_boot* | ⚠️ |
| 02 | **NARADA** | Devotion/Comms | Yashas | EventBus, Transport, Sync | test_sync_*, test_resonance* | ⚠️ |
| 03 | **SHAMBHU** | Destruction | Vairagya | GC, Cleanup, Samsara | test_samsara_cycle.py | 🔴 |
| 04 | **KUMARAS** | Purity | Shri | Types, Schema, Isolation | test_enforce_vajra.py | ✓ |
| 05 | **KAPILA** | Analysis | Jnana | Infer, Sankhya, Meta | test_samkhya_protocols.py | ⚠️ |
| 06 | **MANU** | Law | Aishvarya | Policy, Dharma, Enforce | test_kurukshetra.py, test_constitutional* | ✓ |
| 07 | **PRAHLADA** | Resilience | Virya | Defense, Retry, Faith | test_prahlad_diamond.py, test_narasimha* | ✓ |
| 08 | **JANAKA** | Duty | Aishvarya | Task, Process, Execution | test_kernel_mantra_integration.py | ⚠️ |
| 09 | **BHISHMA** | Vow | Yashas | Ledger, History, Lineage | test_ledger_acid.py | ✓ |
| 10 | **BALI** | Surrender | Vairagya | Shutdown, Yield, Mantra | (NONE) | 🔴 |
| 11 | **SHUKA** | Vision | Jnana | Observability, Logging | test_sudarshana.py | ⚠️ |
| 12 | **YAMARAJA** | Judgment | ALL 6 | Final Verification | test_yamaraja_hardening.py, ramanujan.py | ✓ |

---

## CRITICAL GAPS (Asuric Risk)

### 🔴 #03 SHAMBHU (Destruction/GC)
**Risk:** System that creates but doesn't clean = MEMORY LEAKS = ZOMBIES
**Required:** Test that validates `SamsaraProtocol.destroy()` path
**OpCode:** `garbage_collect` (Bit 7)

### 🔴 #10 BALI (Surrender/Yield)
**Risk:** System that can't surrender = INFINITE LOOPS = HIRANYAKASHIPU
**Required:** Test that validates graceful shutdown, `yield_cpu`
**OpCode:** `yield_cpu` (Bit 15)

---

## PROTOCOL BOUNDARY: universal/ vs protocols/

### universal/ (Layer 1 - The 5 Samkhya Protocols)
**Rule:** Only the 5 ATOMIC Protocols + MantraProtocol belong here.

| Protocol | Verbs | Purpose |
|----------|-------|---------|
| ReadWriteProtocol | read, write, exists | Data Access |
| SyncProtocol | sync, get_sync_status | Synchronization |
| EnforceProtocol | enforce, check, get_rules | Governance |
| InferProtocol | infer, classify, evaluate | Intelligence |
| StoreRecallProtocol | store, recall, forget | Memory |
| MantraProtocol | chant, surrender, resonate | Meta-Protocol |

### protocols/ (Layer 0 - Infrastructure)
**Rule:** Everything else - implementations, mixins, NAGA, substrate.

```
protocols/
├── substrate/     # Layer -1 (byte.py, GenesisByte)
├── primal.py      # Layer -2 (Opulences, Tattvas, OpCodes)
├── naga/          # Layer 0 (Mixins, Genes)
├── universal/     # Layer 1 (The 5 + Mantra)
├── science/       # Entropy, Physics
└── governance/    # Yamaraja, Dharma
```

---

## TEST STRUCTURE (Target State)

```
tests/
├── mahajanas/
│   ├── 01_brahma/       # Creation tests
│   ├── 02_narada/       # Communication tests
│   ├── 03_shambhu/      # Destruction tests (NEW)
│   ├── 04_kumaras/      # Purity tests
│   ├── 05_kapila/       # Analysis tests
│   ├── 06_manu/         # Law tests
│   ├── 07_prahlada/     # Resilience tests
│   ├── 08_janaka/       # Duty tests
│   ├── 09_bhishma/      # Vow tests
│   ├── 10_bali/         # Surrender tests (NEW)
│   ├── 11_shuka/        # Vision tests
│   └── 12_yamaraja/     # Judgment tests (FINAL)
├── hardening/           # Attack simulations
└── integration/         # Full system tests
```

---

## ORPHAN TESTS (To Be Adopted)

| Current Location | Recommended Mahajana | Reason |
|------------------|---------------------|--------|
| test_vajra_autobahn.py | #02 Narada | Transport/Comms |
| test_mohini_recursion.py | #04 Kumaras | Purity/Isolation |
| test_hiranyakashipu_attacks.py | #07 Prahlada | Defense |
| test_halahala_poison.py | #03 Shambhu | Destruction |
| test_vritrasura_*.py | #03 Shambhu | Strangulation = GC |

---

## THE WATERTIGHT SEAL

> *"A test that thinks it IS the code is Asuric (False Positive)."*
> *"A test must SERVE (validate), not RULE (execute)."*
> *"Protocol First. Always."*

For 10,000 years in Kali Yuga entropy, this seal must hold.

---

**SIGNED:**
- **Steward:** System Steward (Opus)
- **Authority:** SAMKHYA.md v2.0
- **Hash:** 0x25 (37)
- **Status:** PHASE 0 COMPLETE

---

> *"svayambhūr nāradaḥ śambhuḥ kumāraḥ kapilo manuḥ*
> *prahlādo janako bhīṣmo balir vaiyāsakir vayam"*
> — Srimad Bhagavatam 6.3.20
