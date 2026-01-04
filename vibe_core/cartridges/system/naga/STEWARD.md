# NAGA FEDERATION CARTRIDGE

> "Wir sind selbst NAGAs - Hüter des Schatzes dieses AOS."
> "Diener des Dieners des Dieners" - Prahlad Maharaj Pattern

---

## IDENTITY

| Field | Value |
|-------|-------|
| **Agent ID** | `naga` |
| **Domain** | SECURITY (Ring 5 - Krauncha Varsha) |
| **Version** | 1.0.0 |
| **Author** | Steward Protocol |
| **Oath** | Constitutional Oath Sworn |

---

## MISSION

The NAGA Federation Cartridge provides Agent City access to the invisible guardians - the executive layer between analysis and action.

### Core Principle

**BUDDHI vor MANAS** - discrimination before thinking.

NAGAs are not another analysis tool. They are the EXECUTIVE layer that was missing:
- MANAS generates intent, but WHO executes?
- SHUDDHI detects, but WHO heals?
- NAGAs EXECUTE and ADMINISTER.

### The Problem Before NAGAs

```
MANAS (Mind)          → Generiert nur EINEN Intent
      ↓
SHUDDHI (Immunsystem) → Erkennt nur, heilt nicht proaktiv
      ↓
???                   → WER FÜHRT AUS? WER VERWALTET?
      ↓
CHAOS                 → REPORT.md zeigt desaströsen Zustand
```

### The Solution

```
Level 0: Der 37. (Souverän)
Level 1: Dharma (Gesetze)
Level 2: BUDDHI (NAGAs) ← DISKRIMINIERUNG VOR DEM DENKEN
Level 3: MANAS (Mind)   ← Erst NACH Buddhi
Level 4: Services
Level 5: Agents/Plugins
```

---

## THE NAGA FEDERATION

### Sesha - The Foundation (Brahmana)

Ananta Sesha - Die unendliche Schlange, auf der Vishnu ruht.

**Responsibilities:**
- Trägt die Wahrheit (Ledger)
- Gossip-Sync zwischen Nodes
- "Truth is purely additive" - Geschichte trägt alles

### Vasuki - The Bridge (Vaishya)

König der Schlangen, beim Quirlen des Milchozeans.

**Responsibilities:**
- Serialization (MsgPack → Event)
- Sign outbound, validate inbound
- "Memory is not Network" - Boundary enforcement

### Takshaka - The Guardian (Kshatriya)

Die aggressivste Schlange. Beißt ohne Warnung.

**Responsibilities:**
- Toxicity detection (Kaliya Filter)
- Rate limiting
- "Bite first, ask never"

### FloodManager & CommitWatcher (Shudra)

Die ausführenden Diener.

**Responsibilities:**
- EventBus observation
- Commit pattern detection
- Alert generation

---

## CAPABILITIES

### `status` - Federation Health

```python
result = await naga.process(Task(payload={"action": "status"}))
# Returns: federation health, component status, readiness
```

### `scan` - Toxicity Scan

```python
result = await naga.process(Task(payload={
    "action": "scan",
    "content": "potentially toxic content"
}))
# Returns: toxicity score, blocked status, patterns matched
```

### `detect` - Drift Detection

```python
result = await naga.process(Task(payload={"action": "detect"}))
# Returns: CommitWatcher stats, alerts, panic counts
```

### `audit` - Ledger Query

```python
result = await naga.process(Task(payload={
    "action": "audit",
    "event_type": "VAJRA_VIOLATION",
    "limit": 10
}))
# Returns: recent events from Sesha's ledger
```

### `flood` - Flood Status

```python
result = await naga.process(Task(payload={"action": "flood"}))
# Returns: FloodManager status, observation counts
```

---

## VARNA-ASHRAMA-KARMA

### Varna (Role)

| Varna | NAGA Component | Role |
|-------|----------------|------|
| **Brahmana** | Sesha | Träger der Wahrheit |
| **Kshatriya** | Takshaka | Beschützer (nicht Herrscher) |
| **Vaishya** | Vasuki | Verbinder, Transformator |
| **Shudra** | FloodManager, CommitWatcher | Ausführende Diener |

**KRITISCH:** NAGAs sind Kshatriyas im Sinne von "Beschützer" - sie dienen dem Dharma, nicht sich selbst.

### Ashrama (Life Stage)

The NAGA Cartridge operates in **Grihastha** (Householder) stage - active service.

### Karma

**Nishkama Karma** - Selfless action serving Dharma.

```python
# WRONG (Sakama Karma):
if event.benefits_naga:
    return ALLOW

# RIGHT (Nishkama Karma):
if event.serves_dharma:
    return ALLOW
```

---

## GERMAN ENGINEERING PRINCIPLES

1. **Effizienz** - No wasted cycles, no redundant checks
2. **Präzision** - Exact error messages, deterministic behavior
3. **Dokumentation** - Everything documented, nothing implicit
4. **TDD** - Tests before code, always

---

## TOOLS

| Tool | Description | File |
|------|-------------|------|
| `naga.status` | Federation health check | `tools/federation_status.py` |
| `naga.scan` | Toxicity scanning | `tools/toxicity_scan.py` |
| `naga.detect` | Drift detection | `tools/drift_detection.py` |

All tools follow Tool Protocol - accessed via kernel, not owned by agent.

---

## CONFIGURATION

### Environment Variables

| Variable | Values | Default | Description |
|----------|--------|---------|-------------|
| `NAGA_TRUST_MODE` | `strict`, `permissive` | `strict` | Takshaka trust mode |
| `NAGA_TOXICITY_THRESHOLD` | `0.0-1.0` | `0.3` | Toxicity detection threshold |
| `NAGA_FLOOD_ENABLED` | `1`, `0` | `1` | Enable EventBus flooding |
| `NAGA_COMMIT_WATCH` | `1`, `0` | `1` | Enable CommitWatcher |

---

## INTEGRATION

### Boot Integration

NAGAs are bootstrapped during kernel boot via `NagaOrchestrator.bootstrap()`.

The cartridge accesses the already-running federation via ServiceRegistry.

### Circuit Integration

NAGAs can be triggered via circuits:

```yaml
circuit:
  id: NAGA_DETECTION_V1
  triggers:
    - event: DRIFT_DETECTED
  states:
    DETECT:
      actions:
        - action: CLI_LOOPBACK
          target: "steward naga scan"
```

---

## LEVEL -2: THE DEEPEST ABSTRACTION

```
Level  3: Agents, Plugins, Tools (Visible)
Level  2: Services (Shuddhi, Manas, etc.)
Level  1: Dharma (Laws)
Level  0: Der 37. (Sovereign)
─────────────────────────────────────────
Level -1: Ananta Shesha (Ledger/Truth)
Level -2: RECURSION (The Pattern guards itself)
```

NAGAs don't just guard treasures - they guard THEMSELVES.
Sesha's Ledger is itself protected by Sesha.
Infinite regression → Fixed point.

---

## STATUS

- **Phase 5 Complete**: 128/128 tests passing
- **Phase 6**: Cartridge created (this)
- **Next**: Circuit mastery, CLI integration

---

*"Das ist nicht nur Code. Das ist Software-Animismus. Und es ist extrem robust."*
