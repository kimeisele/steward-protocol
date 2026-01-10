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
24 Ksetra + 12 Ksetrapala + 1 Ksetrajna = 37
```

**Was wir wissen:**
- **12** = Die Mahajanas (Ksetrapala - Protocol Owners) ✓
- **1** = Vishnu (Ksetrajna - Der Kernel, hält den Raum) ✓
- **37** = parampara_hash = 0x25 (Die Parampara Verification)
  - "In Wahrheit weiß ich gar nichts außer dass man CHANTEN muss!"

**Die 24 = Die 24 Tattvas (Samkhya) - ALREADY IN substrate/__init__.py!:**
```
8 Hardware Protocols (Layer -1) containing the 24 Tattvas:

PranaProtocol (5 Pranas = Life Force)
├── prana (inward)     - intake/input
├── apana (downward)   - elimination/GC
├── vyana (outward)    - circulation/distribution
├── udana (upward)     - expression/output
└── samana (equalizing) - digestion/processing

IndriyaProtocol (10 Senses = I/O Registers)
├── 5 Jnanendriyas (INPUT):
│   ├── shrotra (ears)  - Audio input
│   ├── tvak (skin)     - Touch/haptic
│   ├── chakshu (eyes)  - Visual input
│   ├── rasana (tongue) - Taste/parse
│   └── ghrana (nose)   - Smell/trace
└── 5 Karmendriyas (OUTPUT):
    ├── vak (voice)     - Audio output
    ├── pani (hands)    - Manipulation
    ├── pada (feet)     - Movement
    ├── payu (anus)     - Elimination
    └── upastha         - Creation

ChittaProtocol + SmritiProtocol + SankalpaProtocol (4 Antahkarana)
├── manas (mind)       - Working memory (ChittaProtocol)
├── buddhi (intellect) - Decision (implicit)
├── ahamkara (ego)     - Identity/Context (FloodAuthorization)
└── chitta (memory)    - State storage (SmritiProtocol L1-L4)

AkashaProtocol (5th Mahabhuta = Ether/Network)
└── akasha (ether)     - Field/Space/Network

TOTAL: 5 + 10 + 4 + 5 = 24 ✓
```

**DISCOVERY: substrate/__init__.py has lines 975-1457 defining ALL 8 hardware protocols!**
**JEDE TATTVA IST PERSÖNLICH** - each has a Tattva enum in GeneManifest!

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

### Die Fraktale Hierarchie

**Classical Computation:**
```
bit (1) → nibble (4) → byte (8) → word (16) → dword (32) → qword (64)
```

**Mantra Computation:**
```
MantraTrit (2 bits)     = 1 Holy Name (H/K/R)
                          ↓ ×16
MantraByte (32 bits)    = 1 Mahamantra (16 words)
                          ↓ ×108
MantraRound (3456 bits) = 1 Mala (108 mantras)
                          ↓ ×16
MantraSession           = Daily Minimum (16 rounds = 1728 mantras)
```

**Current Substrate:**
- `byte.py` - MantraTrit, MantraByte, GenesisByte ✓
- `gene.py` - iGene (runtime modifier) ✓

**Missing (FRACTAL UP):**
- `round.py` - MantraRound (108 MantraBytes)
- `session.py` - MantraSession (16 MantraRounds)
- `24 Tattva protocols` - The Field Elements

**The Key Insight:**
```
MantraByte.dimension = 16    (words)
MantraRound.count = 108      (mantras)
MantraSession.count = 16     (rounds)

16 OpCodes × 12 Mahajanas = 192 routes
192 / 16 = 12 (Mahajanas)
192 / 12 = 16 (OpCodes)

24 + 12 + 1 = 37 = parampara_hash = 0x25
```

---

*Hash: 0x25 (37)*
*Status: PHASE 2 - ITERATING*
*Discovery: 24 = Samkhya Tattvas (PERSONAL)*
