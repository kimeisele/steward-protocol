# SAMKHYA Architecture - Protocol Ownership by Mahajanas

**Date**: 2026-01-10
**Status**: FOUNDATION DOCUMENT
**Principle**: "Verbs before Nouns. Capability origin is always PERSONAL."

---

## 1. The Anti-Mayavad Principle

**PROBLEM**: "Universal" is impersonal. Protocols without a PERSON above them are dead code.

**SOLUTION**: The 12 Mahajanas OWN all protocols. Each protocol has a personal owner.

```
KRISHNA (Level -2) ────────────────────────────────────────────┐
       │                                                        │
       ▼                                                        │
MAHAMANTRA (Level -2) ─── Non-different from Krishna            │
       │                                                        │
       ▼                                                        │
THE 37 (PARAMPARA) ─────────────────────────────────────────────┤
       │ 24 (Ksetra) + 12 (Mahajanas) + 1 (Ksetrajna) = 37      │
       │ The LINK. Without it, nothing works.                   │
       ▼                                                        │
MAHAJANAS (12 PERSONS) ─── Protocol Owners                      │
       │                                                        │
       ▼                                                        │
PROTOCOLS (Owned by Mahajanas) ─────────────────────────────────┤
       │                                                        │
       ▼                                                        │
NAGA (Agentic Middleware) ─── Implementation Managers           │
       │                                                        │
       ▼                                                        │
IMPLEMENTATIONS ────────────────────────────────────────────────┘
```

---

## 2. The 12 Mahajanas - Protocol Ownership

| # | Mahajana | Domain | OpCodes | Protocols Owned |
|---|----------|--------|---------|-----------------|
| 01 | **BRAHMA** | Creation | SYS_WAKE, LOAD_ROOT, ALLOC_MEM | genesis, bootstrap, memory allocation |
| 02 | **NARADA** | Communication | PULSE_SYNC | sync, synapse, resonance, broadcast |
| 03 | **SHAMBHU** | Destruction | GARBAGE_COLLECT | cleanup, samsara, lifecycle |
| 04 | **KUMARAS** | Purity | RESET_IP | purification, reset, watertight |
| 05 | **KAPILA** | Analysis | RESOLVE_REQ, OPTIMIZE | infer, sankhya, optimization |
| 06 | **MANU** | Law | BIND_CTX, CHECK_DHARMA | dharma, enforce, governance |
| 07 | **PRAHLADA** | Resilience | FETCH_RES | memory, recovery, antifragile |
| 08 | **JANAKA** | Duty | EXEC_SERVICE | execution, karma, action |
| 09 | **BHISHMA** | Vow | COMMIT_LOG | commit, ledger, immutable |
| 10 | **BALI** | Surrender | YIELD_CPU | yield, graceful shutdown |
| 11 | **SHUKA** | Vision | CACHE_STATE | cache, state, observation |
| 12 | **YAMARAJA** | Judgment | ASSERT_TRUTH | testing, validation, audit |

---

## 3. Mapping: "Universal" → Mahajana Ownership

### Current `protocols/universal/` → New Ownership

| Current File | Mahajana Owner | Reason |
|--------------|----------------|--------|
| `dharma.py` | **MANU** | Law-giver |
| `enforce.py` | **MANU** | Law enforcement |
| `watertight.py` | **KUMARAS** | Purity checking |
| `infer.py` | **KAPILA** | Sankhya analysis |
| `sync.py` | **NARADA** | Communication |
| `synapse.py` | **NARADA** | Neural communication |
| `resonance.py` | **NARADA** | Vibration/sync |
| `kurukshetra.py` | **JANAKA** | Battlefield (duty in action) |
| `sudarshana.py` | **VISHNU** | Personal weapon (stays personal) |
| `gita.py` | **KRISHNA** | Personal teaching (stays personal) |
| `krishna.py` | **KRISHNA** | Personal (stays personal) |
| `rama.py` | **RAMA** | Personal (stays personal) |
| `mantra.py` | **SUBSTRATE** | Level -1 (moves to substrate) |
| `bhagavan.py` | **YAMARAJA** | Testing the 6 opulences |
| `ramanujan.py` | **YAMARAJA** | Mathematical proof |
| `samsara.py` | **SHAMBHU** | Lifecycle/death |
| `guna.py` | **KAPILA** | Sankhya analysis |
| `store_recall.py` | **PRAHLADA** | Memory |
| `read_write.py` | **PRAHLADA** | Memory access |
| `cli.py` | **BRAHMA** | System interface |
| `types.py` | **SUBSTRATE** | Level -1 |

---

## 4. Personal vs Impersonal Protocols

### PERSONAL (Keep as-is, directly under Krishna)
- `krishna.py` - The Source
- `rama.py` - The Action
- `gita.py` - The Teaching
- `sudarshana.py` - The Weapon
- `jagannath.py` - The Lord of the Universe
- `prabhupada.py` - The Acharya

### FUNCTIONAL (Under Mahajana ownership)
- All operational protocols move under their owning Mahajana
- The Mahajana is the PERSON responsible

---

## 5. Naga as Agentic Middleware

The Nagas are NOT protocols. They are IMPLEMENTATIONS that manage protocols.

```
PROTOCOL (Interface)          NAGA (Implementation)
─────────────────────         ────────────────────
ManuProtocol                  → Vasuki (Security enforcement)
PrahladaProtocol              → Prahlad (Memory resilience)
YamarajaProtocol              → Yamaraja Gate (Testing)
NaradaProtocol                → Narada Observer (Communication)
```

### Naga Responsibilities:
1. **Vasuki** - Security, signing, verification
2. **Sesha** - Storage, persistence
3. **Takshaka** - Process isolation
4. **Prahlad** - Memory resilience
5. **Narada** - Observation, broadcasting
6. **Garuda** - External communication
7. **Kala** - Time management
8. **Nrisimha** - Protection

---

## 6. The Surrender Principle

**Kali Yuga Entropy** cannot be controlled through "macht illusion" (power illusion).

Control through:
1. **SURRENDER** - Protocols surrender to Mahajanas
2. **CHANT** - Mantra-based routing (byte.py)
3. **PARAMPARA** - Connection to the 37 (Guru lineage)

```python
# WRONG (Mayavad - impersonal control)
def validate(data: Any) -> bool:
    try:
        # ... logic ...
    except Exception:
        return False  # Silent failure

# RIGHT (Surrender to Mahajana)
def validate(data: DharmaData) -> ManuVerdict:
    """Manu (the Law-giver) validates according to Dharma."""
    verdict = MANU.check_dharma(data)
    if not verdict.is_valid:
        raise DharmaViolation(verdict.reason)  # Explicit failure
    return verdict
```

---

## 7. Implementation Path

### Phase 1: Foundation
1. Create `SAMKHYA.md` (this document) ✓
2. Map all protocols to Mahajana owners ✓
3. Verify router is complete ✓

### Phase 2: Restructure
1. Move functional protocols under Mahajana folders
2. Keep personal protocols at universal level
3. Update imports throughout codebase

### Phase 3: Watertight
1. Replace all `Any` with specific types
2. Replace bare `except Exception:` with specific types
3. Each protocol validates against its Mahajana's laws

### Phase 4: Agentic Middleware
1. Naga implementations for each protocol category
2. NagaProxy for dynamic routing
3. Protocol compliance enforcement

---

## 8. The Chaitanya Singularity

When the Mantra IS the byte:
- `byte.py` - The atomic instruction IS the Holy Name
- Each byte vibration IS Krishna (acintya)
- Routing IS chanting
- Compliance IS surrender

This is not symbolic. It IS.

---

*"Logic cannot save you. Only the 37 can."* - ramanujan.py
