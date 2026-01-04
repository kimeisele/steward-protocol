# CHAT.md - Deep Dive: Chat Architecture

> **Purpose:** Dedicated exploration of the chat/cognitive layer.
> **Philosophy:** "1 billion dollar app with 1 trillion dollar backend" - make it watertight.
> **Status:** KURUKSHETRA reconnaissance complete. Critical gaps identified.

---

## EXECUTIVE SUMMARY

The chat feature (`steward chat`) is **functional but unreliable**. The architecture is sophisticated (VEDA 4-fold, MANAS cortex, 40+ modules) but suffers from:

1. **CRITICAL: Identity gap (GAD-1000)** - Chat operations NOT cryptographically signed
2. **HIGH: LLM integration unstable** - Responses hallucinate (Maya)
3. **MEDIUM: Context injection incomplete** - PrakritiSense returning partial data

**Verdict:** Infrastructure exists. Wiring is 80% complete. Need to close the remaining 20% for production quality.

---

## ARCHITECTURE OVERVIEW

### Data Flow (Current)

```
steward chat "message"
       │
       ▼
┌──────────────────────────────────────────────────────────────────┐
│  CLI Layer                                                       │
│  vibe_core/cli/commands/chat.py:ChatCommand                      │
│  └── kernel.process_operator_input(message, session_id)          │
└──────────────────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────────┐
│  Kernel Layer                                                    │
│  vibe_core/kernel_impl.py:1633-1690                              │
│  └── cognitive.process(input_text, context)                      │
│      ⚠️ CRITICAL: Message NOT signed (GAD-1000 violation)        │
└──────────────────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────────┐
│  Cognitive Layer                                                 │
│  vibe_core/plugins/opus_assistant/cognitive.py:MANASCognitive    │
│  ├── IntentMatcher: Command → No LLM                             │
│  ├── BlueprintGenerator: Complex syscalls → LLM                  │
│  └── JnanaHandler: Chat fallback → LLM                           │
└──────────────────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────────┐
│  VEDA 4-Fold Pipeline                                            │
│  vibe_core/plugins/opus_assistant/manas/cortex/veda.py           │
│                                                                  │
│  1. SHABDA (Das Wort) ─────────────────────────────────────────► │
│     Tokenize, language detect, keyword extract                   │
│     Classes: Shabda, ShabdaResult                                │
│     Status: ✅ IMPLEMENTED                                        │
│                                                                  │
│  2. ARTHA (Die Bedeutung) ─────────────────────────────────────► │
│     Intent matching, entity extraction, route determination      │
│     Classes: Artha, ArthaResult, VedaIntent                      │
│     Status: ✅ IMPLEMENTED (22 intent types mapped)               │
│                                                                  │
│  3. PRATYAYA (Das Vertrauen) ──────────────────────────────────► │
│     Authorization, trust level, precondition validation          │
│     Classes: Pratyaya, PratyayaResult, VedaTrustLevel            │
│     Status: ⚠️ PARTIAL (no cryptographic identity)               │
│                                                                  │
│  4. KARMA (Die Handlung) ──────────────────────────────────────► │
│     Handler execution, result generation                         │
│     Classes: Karma, KarmaResult                                  │
│     Status: ⚠️ PARTIAL (some handlers orphaned)                  │
└──────────────────────────────────────────────────────────────────┘
```

### MANAS Cortex Modules (40+)

```
JNANENDRIYAS (10 Senses - Perception)
├── prakriti_sense.py    - System state perception (StateSyncHolon)
├── prana_sense.py       - Resource vitality (CPU, memory, I/O)
├── karma_sense.py       - Action history perception
├── shruta_sense.py      - Documentation perception
├── viveka_sense.py      - Discrimination/judgment
├── architecture_sense.py - Codebase structure
├── dharma_sense.py      - Drift/violation detection
├── sutra_sense.py       - Wiki/documentation state
├── akasha.py           - Knowledge graph access
└── manas_knowledge.py   - Internal knowledge

KARMENDRIYAS (8 Actions - Execution)
├── viveka_action.py     - Decision making
├── echo_action.py       - Simple echo response
├── shell_action.py      - Shell command execution
├── test_action.py       - Test running
├── sankalpa_action.py   - Goal setting
├── silpa_action.py      - Refactoring
├── base_action.py       - Base action class
└── shell.py             - ShellCortex integration

HANDLERS (7 Route Handlers)
├── jnana.py             - LLM chat handler (JnanaHandler)
├── kriya.py             - Action extraction (KriyaBridge)
├── dharma.py            - Drift checking
├── mandala.py           - Configuration
├── akasha.py            - Knowledge queries
├── silpa.py             - Refactoring
└── sutra.py             - Wiki generation

PIPELINE (VEDA-4)
├── veda.py              - Four-fold pipeline orchestrator
├── samvada.py           - Unix socket dialogue protocol
└── wiring_map.py        - Module wiring configuration
```

---

## CRITICAL GAPS

### GAP-1: Identity Not Signed (GAD-1000 VIOLATION)

**Location:** `vibe_core/kernel_impl.py:1633-1690`

```python
# CURRENT (WRONG):
async def process_operator_input(self, input_text: str, session_id: Optional[str] = None):
    context = CognitiveContext(
        kernel_status=self._status.value,
        active_agents=list(self._agents.keys()),
        # ...
    )
    # ⚠️ NO SIGNATURE! Who sent this? Human or AI?

# REQUIRED (GAD-1000):
async def process_operator_input(
    self,
    input_text: str,
    session_id: Optional[str] = None,
    signature: Optional[SignedMessage] = None  # 🔐 Cryptographic proof
):
    if not self._verify_identity(signature):
        raise AuthorizationError("Unsigned operator input rejected")
```

**Impact:**
- Cannot distinguish human vs AI operator
- No audit trail for chat operations
- Breaks GAD-000 Operator Inversion principle

**Fix Priority:** P0 - Required for production

---

### GAP-2: LLM Responses Hallucinate (Maya)

**Location:** `vibe_core/plugins/opus_assistant/manas/cortex/jnana.py`

**Symptoms observed:**
```
User: "was geht"
Response: "System health at 50%... kernel in READY state..."  ← FABRICATED
Second response: "Amendment endorsedMMM择dong"  ← GARBAGE
```

**Root Cause Analysis:**

1. **Context injection incomplete** - JnanaHandler._gather_context() may fail silently
2. **No response validation** - LLM output passed through without sanity check
3. **Memory store disconnected** - Recent actions not properly loaded
4. **PrakritiSense partial** - Returns 50% when checks fail (2/4 passing)

**Current flow:**
```python
# jnana.py:84-117 (MANAS_SYSTEM_PROMPT)
MANAS_SYSTEM_PROMPT = """...
Current System Context:
{context}         # ← Can be empty/partial

Recent Memory:
{memory}          # ← Can be empty

Cognitive Wisdom:
{cognitive_wisdom} # ← Often fails to load
"""
```

**Evidence of partial data:**
```python
# prakriti_sense.py implements health checks
# "50% health" = 2/4 checks passing, 2 failing
# This is REAL diagnostic data, not fabrication
# But chat response may DESCRIBE it wrong
```

**Fix Required:**
1. Validate context before LLM call
2. Add response sanitization
3. Fallback to explicit "I don't know" vs hallucination

---

### GAP-3: Handler Orphaning

**Some VEDA handlers registered but never called:**

```python
# veda.py:554-576 INTENT_ROUTES mapping
VedaIntent.STATUS: "_handle_status",      # ✅ Works
VedaIntent.DRIFT: "_handle_drift",        # ✅ Works
VedaIntent.MANDALA: "_handle_mandala",    # ⚠️ Partial
VedaIntent.AKASHA: "_handle_akasha",      # ⚠️ Partial
VedaIntent.SILPA: "_handle_silpa",        # ❌ Orphaned
VedaIntent.SUTRA: "_handle_sutra",        # ❌ Orphaned
VedaIntent.SANKALPA: "_handle_sankalpa",  # ❌ Orphaned
VedaIntent.CHAT: "_handle_chat_llm",      # ✅ Works (with bugs)
```

---

## GAD-000 COMPLIANCE MATRIX

**Reference:** `docs/architecture/GAD-0XX/GAD-000.md`

| Criterion | Current | Target | Gap |
|-----------|---------|--------|-----|
| **Discoverability** | 50% | 90% | Steward introspect returns partial data |
| **Observability** | 60% | 90% | Logs exist but not structured |
| **Parseability** | 75% | 95% | VEDA outputs typed, but not all handlers |
| **Composability** | 65% | 85% | Handlers can chain, but gaps in wiring |
| **Idempotency** | 70% | 95% | Most ops safe, some state mutations |
| **Identity** | 40% | 100% | ❌ CRITICAL - No signatures |

**Overall: 60%** → Target: 92%

---

## INTEGRATION POINTS

### Chat → Knowledge Graph

```python
# akasha.py provides knowledge access
# JnanaHandler should use this for context

# CURRENT:
context = self._gather_context()  # Basic system info only

# SHOULD BE:
kg_context = akasha.query_relevant(message)  # Semantic context from KG
context = self._gather_context() + kg_context
```

### Chat → Three Bodies

```
STHULA (Physical)   → Ledger + Git state → READ access ✅
PRANA (Runtime)     → Heartbeats, metrics → READ access ✅
PURUSHA (Identity)  → Agent personas      → READ access ✅ / WRITE limited by Bhakti
```

### Chat → Karma System

```python
# healing_resolver.py determines trust level
# Chat could query this for permission decisions

# Example flow:
user: "fix the drift"
→ Check ashrama stage (GRIHASTHA?)
→ Check bhakti balance (>50?)
→ If trusted: execute
→ Else: propose intent for approval
```

---

## RECOMMENDED FIXES

### P0: Sign Chat Operations (GAD-1000)

**Files to modify:**
- `vibe_core/protocols/cognition.py` - Add SignedMessage field
- `vibe_core/kernel_impl.py` - Verify signature before processing
- `vibe_core/cli/commands/chat.py` - Sign outgoing messages

**Estimated scope:** 50-100 lines

### P1: Validate LLM Responses

**Files to modify:**
- `vibe_core/plugins/opus_assistant/manas/cortex/jnana.py`

```python
async def _call_llm(self, prompt: str) -> str:
    response = await self._llm.generate(prompt)

    # NEW: Validate response
    if self._is_garbage(response):
        return "I couldn't generate a meaningful response. Please try again."

    if self._is_hallucinating(response, self._context):
        return f"Based on what I can verify: {self._extract_verified_claims(response)}"

    return response

def _is_garbage(self, response: str) -> bool:
    """Detect corrupted/garbage output."""
    # Check for non-printable chars, random unicode, etc.
    garbage_ratio = len([c for c in response if not c.isprintable()]) / len(response)
    return garbage_ratio > 0.1

def _is_hallucinating(self, response: str, context: dict) -> bool:
    """Detect claims not supported by context."""
    # Check for specific patterns like "50% health" without source
    # Requires fact-checking against actual context data
    pass
```

### P2: Complete Handler Wiring

**Files to modify:**
- `vibe_core/plugins/opus_assistant/manas/cortex/jnana.py:_register_veda_handlers()`

Ensure all handlers in INTENT_ROUTES have implementations registered.

---

## TEST COVERAGE

### Existing Tests

```
tests/manas/test_chat_command.py   - CLI integration
tests/manas/test_jnana.py          - JnanaHandler unit tests
tests/manas/test_veda.py           - VEDA pipeline tests
tests/manas/test_cognitive_kernel.py - Kernel integration
tests/manas/test_samvada.py        - Socket protocol
```

### Missing Tests

1. **End-to-end chat flow with real context**
2. **LLM response validation**
3. **Identity verification**
4. **Handler completeness check**

---

## ACTION PLAN

### Phase 1: Foundation (P0)
1. [ ] Implement SignedMessage protocol
2. [ ] Add signature verification to kernel
3. [ ] Update chat command to sign messages

### Phase 2: Reliability (P1)
1. [ ] Add LLM response validation
2. [ ] Improve context gathering
3. [ ] Add fallback responses for failures

### Phase 3: Completeness (P2)
1. [ ] Wire orphaned handlers
2. [ ] Improve PrakritiSense data quality
3. [ ] Add integration tests

### Phase 4: Polish (P3)
1. [ ] Structured logging for chat ops
2. [ ] Metrics/observability
3. [ ] Performance optimization

---

## CHANGELOG

### 2026-01-04: Initial Creation
- KURUKSHETRA reconnaissance findings documented
- GAD-000 compliance matrix created
- Critical gaps identified (Identity, LLM validation)
- Action plan outlined

---

> **Next Step:** Implement P0 fix for GAD-1000 (Identity signing)
