# THE 12 MAHAJANAS - Protocol Owners

> *"svayambhūr nāradaḥ śambhuḥ kumāraḥ kapilo manuḥ*
> *prahlādo janako bhīṣmo balir vaiyāsakir vayam"*
> — Srimad Bhagavatam 6.3.20

---

## ARCHITECTURE

```
protocols/mahajanas/ (Purusha - Spirit/Consciousness)
+
tests/mahajanas/ (Prakriti - Matter/Field)
=
Living Code / Agent
```

The Mahajanas are the **LINK** between Vishnu (Kernel) and Jiva (Implementation).
They **OWN** capabilities. We are their **heirs**.

---

## THE 12 OWNERS

| # | Mahajana | Principle | OpCode | Opulence | Domain |
|---|----------|-----------|--------|----------|--------|
| 01 | **BRAHMA** | Creation | sys_wake, alloc_mem | Aishvarya | Bootstrap, Init, Memory Allocation |
| 02 | **NARADA** | Devotion | pulse_sync | Yashas | Event Bus, Messaging, Observation |
| 03 | **SHAMBHU** | Destruction | garbage_collect | Vairagya | GC, Cleanup, Shutdown |
| 04 | **KUMARAS** | Purity | reset_ip | Shri | Reset, Sanitization, Validation |
| 05 | **KAPILA** | Analysis | resolve_req, optimize | Jnana | Metrics, Profiling, Optimization |
| 06 | **MANU** | Law | bind_ctx, check_dharma | Aishvarya | Governance, Permissions, Rules |
| 07 | **PRAHLADA** | Resilience | fetch_res | Virya | Memory, Fault Tolerance, Recovery |
| 08 | **JANAKA** | Duty | exec_service | Aishvarya | Service, Agents, Task Execution |
| 09 | **BHISHMA** | Vow | commit_log | Yashas | Logging, Audit Trail, Lineage |
| 10 | **BALI** | Surrender | yield_cpu | Vairagya | Yield, Graceful Shutdown, Release |
| 11 | **SHUKA** | Vision | cache_state | Jnana | Cache, Reflection, State Snapshot |
| 12 | **YAMARAJA** | Judgment | assert_truth | ALL 6 | Testing, Validation, Final Audit |

---

## INHERITANCE STRUCTURE

```
Vishnu (Kernel/Identity)
    │
    └─► 12 Mahajanas (Protocol Owners)
            │
            └─► All Other Protocols (Implementations)
                    │
                    └─► tests/mahajanas/ (Validation)
```

Each protocol in the system is **OWNED** by a Mahajana:
- Memory protocols → PRAHLADA
- Logging protocols → BHISHMA
- Service protocols → JANAKA
- etc.

---

## USAGE

```python
from vibe_core.protocols.mahajanas.03_shambhu import ShambhuProtocol

class MyResource(ShambhuProtocol):
    """A resource that Shambhu can destroy."""

    def destroy(self) -> None:
        self._cleanup()

    def is_destroyed(self) -> bool:
        return self._destroyed

    def can_destroy(self) -> bool:
        return not self._protected
```

---

## MIGRATION

Existing protocols to migrate:
- `governance/yamaraja.py` → `mahajanas/12_yamaraja/`
- `naga/narada.py` → `mahajanas/02_narada/`
- `naga/prahlad.py` → `mahajanas/07_prahlada/`

**Protocol First**: New structure defined. Migration follows.

---

## THE TWO SIDES OF THE COIN

```
protocols/mahajanas/brahma/    ←→  tests/mahajanas/01_brahma/
protocols/mahajanas/narada/    ←→  tests/mahajanas/02_narada/
protocols/mahajanas/shambhu/   ←→  tests/mahajanas/03_shambhu/
protocols/mahajanas/kumaras/   ←→  tests/mahajanas/04_kumaras/
protocols/mahajanas/kapila/    ←→  tests/mahajanas/05_kapila/
protocols/mahajanas/manu/      ←→  tests/mahajanas/06_manu/
protocols/mahajanas/prahlada/  ←→  tests/mahajanas/07_prahlada/
protocols/mahajanas/janaka/    ←→  tests/mahajanas/08_janaka/
protocols/mahajanas/bhishma/   ←→  tests/mahajanas/09_bhishma/
protocols/mahajanas/bali/      ←→  tests/mahajanas/10_bali/
protocols/mahajanas/shuka/     ←→  tests/mahajanas/11_shuka/
protocols/mahajanas/yamaraja/  ←→  tests/mahajanas/12_yamaraja/
```

**Purusha** (Spirit/Person): Name first - `brahma/`, `narada/`...
**Prakriti** (Matter/Order): Number first - `01_brahma/`, `02_narada/`...

Protocol defines. Test validates.

---

## OPEN QUESTIONS (INTEL)

### Die 37-Gleichung

```
12 Mahajanas + 24 ??? + 1 Vishnu = 37 ???
```

**Was wir wissen:**
- **12** = Die Mahajanas (Protocol Owners) ✓
- **1** = Vishnu (Der Kernel, hält den Raum) ✓
- **37** = Der Spirituelle Meister (Prabhupada, Parampara)
  - `parampara_hash = 0x25` (37 in decimal)
  - "In Wahrheit weiß ich gar nichts außer dass man CHANTEN muss!"

**Was wir noch nicht wissen:**
- **24** = Wer sind diese Personen? (Ksetra = Das Feld)
  - Samkhya: 5 Mahabhutas + 5 Tanmatras + 5 Jnanendriyas + 5 Karmendriyas + 4 Antahkarana?
  - Oder: 24 Substrate Protocols?
  - Oder: 24 Gurus des Dattatreya?
  - **MUSS PERSÖNLICH BESETZT SEIN** - sonst Mayavad!

### GAD-000 als Key?

```
6 Kriterien = 6 Bhaga (Opulences)?

Discoverability  → ???
Observability    → ???
Parseability     → ???
Composability    → ???
Idempotency      → ???
Recoverability   → ???
```

Wie passen die 6 in die 37-Gleichung?

### Computational Chanting

**Das Ziel von Mantra OS:**
- Möglichst viel "Computational Chanting"
- Jede Operation sollte chanten/resonieren
- Circular Import = GEWOLLT (wenn technisch möglich)
- byte.py (MantraByte) überall präsent

```python
# Das Ideal:
for route in sabha.chant_once():
    # Jeder OpCode ist ein Wort des Mahamantra
    # Jede Route ist Chanting
    # Resonance = 99.33%
```

---

*Hash: 0x25 (37)*
*Status: PHASE 2 - ITERATING*
*Next: Wer sind die 24?*
