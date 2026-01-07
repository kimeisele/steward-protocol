# UNION.md - Protocol Compliance Audit

**Layer:** 1 (Universal)
**Status:** YAMARAJA AUDIT
**Precedence:** Constitution → GAD-000 → This

---

## GAD-000 COMPLIANCE MATRIX

| Protocol | D | O | P | C | I | R | VERDICT |
|----------|:---:|:---:|:---:|:---:|:---:|:---:|:-------:|
| **OmProtocol** | ✅ | ✅ | ✅ | ✅ | ❓ | ❓ | ⚠️ |
| KrishnaProtocol | ✅ | ❌ | ✅ | ✅ | ✅ | ❓ | 🔴 |
| RamaProtocol | ✅ | ❌ | ✅ | ✅ | ❌ | ❓ | 🔴 |
| MantraProtocol | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| InferProtocol | ✅ | ✅ | ✅ | ✅ | ❓ | ❌ | 🔴 |
| EnforceProtocol | ✅ | ✅ | ✅ | ✅ | ✅ | ⚠️ | ⚠️ |
| ReadWriteProtocol | ✅ | ⚠️ | ✅ | ✅ | ✅ | ✅ | ⚠️ |
| StoreRecallProtocol | ✅ | ❌ | ✅ | ✅ | ✅ | ❓ | 🔴 |
| SyncProtocol | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| UnionProtocol | ✅ | ✅ | ✅ | ❌ | ✅ | ❌ | 🔴 |

**Legend:**
- D = Discoverability (introspection)
- O = Observability (status/metrics)
- P = Parseability (typed errors)
- C = Composability (pipeable)
- I = Idempotency (safe retry)
- R = Recoverability (fallback defined)

---

## RED TESTS (Failing)

### 🔴 RED-001: KrishnaProtocol missing `get_status()`
**Requirement:** GAD-000 Observability
**File:** `krishna.py`
**Problem:** No way to observe identity state.
**Fix:** Add `def get_identity_status(self) -> IdentityStatus`

### 🔴 RED-002: RamaProtocol `perform_dharma` not idempotent
**Requirement:** GAD-000 Idempotency  
**File:** `rama.py`
**Problem:** No `idempotency_key` parameter.
**Fix:** Add `idempotency_key: Optional[str] = None`

### 🔴 RED-003: RamaProtocol missing observability
**Requirement:** GAD-000 Observability
**File:** `rama.py`
**Problem:** No way to see pending/running dharmas.
**Fix:** Add `def list_pending_dharmas(self) -> List[DharmaStatus]`

### 🔴 RED-004: InferProtocol no fallback defined
**Requirement:** GAD-000 Recoverability
**File:** `infer.py`
**Problem:** What happens if inference fails?
**Fix:** Add `fallback: Optional[Inference] = None` param

### 🔴 RED-005: StoreRecallProtocol missing observability
**Requirement:** GAD-000 Observability
**File:** `store_recall.py`
**Problem:** No `list_keys()` or memory stats.
**Fix:** Add `def get_memory_stats(self) -> MemoryStats`

### 🔴 RED-006: UnionProtocol not composable
**Requirement:** GAD-000 Composability
**File:** `union.py`
**Problem:** `get_living_entities()` returns list, not iterator.
**Fix:** Return `Iterator[EntityStatus]` for streaming.

### 🔴 RED-007: UnionProtocol no recoverability
**Requirement:** GAD-000 Recoverability
**File:** `union.py`
**Problem:** What if entity scan fails mid-way?
**Fix:** Add `timeout` + partial result handling.

---

## YELLOW WARNINGS

### ⚠️ WARN-001: OmProtocol idempotency unclear
**Question:** Is `chant_mahamantra()` safe to retry?
**Action:** Document retry semantics.

### ⚠️ WARN-002: EnforceProtocol fallback ambiguous
**Question:** What's the default verdict on error?
**Action:** Document `DENY` as fail-closed default.

### ⚠️ WARN-003: ReadWriteProtocol observability weak
**Question:** No `list_keys()` method.
**Action:** Consider adding for discoverability.

---

## GREEN (Passing)

| Check | Status |
|-------|:------:|
| All protocols have `@runtime_checkable` | ✅ |
| All return typed dataclasses | ✅ |
| All accept `SovereignContext` | ✅ |
| MantraOpCode has 16 members | ✅ |
| MAHAMANTRA_SEQUENCE is 16 steps | ✅ |
| No `Any` in public signatures | ✅ |
| All imports resolve | ✅ |

---

## CONSTITUTION COMPLIANCE

| Artikel | Requirement | Status |
|---------|-------------|:------:|
| I: Identität | SovereignContext everywhere | ✅ |
| II: Rechenschaft | Audit trail possible | ⚠️ |
| III: Governance | Typed constraints | ✅ |
| IV: Transparenz | Observable state | 🔴 |
| V: Zustimmung | Context=consent | ✅ |
| VI: Interop | Protocols standard | ✅ |

---

## NEXT ACTIONS

1. [ ] Fix RED-001: Add `get_identity_status()` to KrishnaProtocol
2. [ ] Fix RED-002: Add `idempotency_key` to RamaProtocol
3. [ ] Fix RED-003: Add `list_pending_dharmas()`
4. [ ] Fix RED-004: Add fallback param to InferProtocol
5. [ ] Fix RED-005: Add `get_memory_stats()`
6. [ ] Fix RED-006: Make UnionProtocol streaming
7. [ ] Fix RED-007: Add timeout + partial handling

---

*Audited: 2026-01-08 00:58*
*Auditor: YAMARAJA*
