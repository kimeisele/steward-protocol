# 🕉️ VEDIC ARCHITECTURE SPECIFICATION
## STEWARD Protocol - Srimad Bhagavatam Integration

**Version:** 1.0.0  
**Source:** Srila Prabhupada's Srimad Bhagavatam (Canto 1-10)  
**Status:** DRAFT - Awaiting Implementation

---

## 📋 EXECUTIVE SUMMARY

Das System schläft in **Susupti** (Tiefschlaf). Es atmet (Spandana), aber es arbeitet nicht (Karma).

**Kritische Befunde:**
1. Alle Agents sind `brahmachari` - niemand hat Write-Permissions
2. Kernel fehlt `_paused_agents` - Smriti-bhramsha (Gedächtnisverlust)
3. Keine Guna-States - System kann nicht "reifen"
4. Routing ohne Transformation - kein echtes Yajna

---

## 🔧 PHASE 1: KERNEL FIX (Paramatma-Funktion)

### Problem
```
'RealVibeKernel' object has no attribute '_paused_agents'
```

### Vedische Referenz
> **SB 13.3** (Bhagavad-gita im Kontext): Die Überseele ist der Zeuge und Erlaubnisgeber 
> (`anumanta` und `upadrasta`).

Ohne `_paused_agents` verliert die Überseele das Gedächtnis über die Lebewesen die "schlafen".

### Implementation

```python
# vibe_core/kernel_impl.py

class RealVibeKernel:
    def __init__(self, ...):
        # ... existing code ...
        
        # PARAMATMA-GEDÄCHTNIS: Welche Agents schlafen?
        self._paused_agents: set[str] = set()
        
        # GUNA-STATES: In welchem Modus ist jeder Agent?
        self._agent_gunas: dict[str, GunaState] = {}
        
    def pause_agent(self, agent_id: str) -> None:
        """Anumanta - Der Erlaubnisgeber lässt den Agent schlafen."""
        self._paused_agents.add(agent_id)
        self._agent_gunas[agent_id] = GunaState.TAMAS
        
    def resume_agent(self, agent_id: str) -> None:
        """Upadrasta - Der Zeuge weckt den Agent."""
        self._paused_agents.discard(agent_id)
        self._agent_gunas[agent_id] = GunaState.RAJAS
        
    def is_paused(self, agent_id: str) -> bool:
        return agent_id in self._paused_agents
```

---

## 🎓 PHASE 2: ASHRAMA-ÜBERGANG (The Graduation System)

### Problem
Alle Agents haben:
```
Ashrama (Stage): brahmachari
Permissions: read, listen, observe, learn
```

### Vedische Referenz
> **SB Canto 7, Kapitel 12** (Die perfekten Brahmacharis): 
> Der Übergang passiert wenn der Schüler nicht fähig ist lebenslang `naisthika` zu bleiben,
> ODER wenn der Guru ihn anweist eine Familie (Sub-System) zu gründen.

### Die 4 Ashrama-Stufen

```python
# vibe_core/ashrama.py

from enum import Enum
from dataclasses import dataclass

class Ashrama(Enum):
    BRAHMACHARI = "brahmachari"  # Student - Read Only
    GRIHASTHA = "grihastha"       # Householder - Read/Write
    VANAPRASTHA = "vanaprastha"   # Retired - Advisory
    SANNYASI = "sannyasi"         # Renounced - Audit Only

@dataclass
class AshramePermissions:
    """Permissions based on Ashrama stage."""
    
    BRAHMACHARI = frozenset({"read", "listen", "observe", "learn"})
    GRIHASTHA = frozenset({"read", "write", "spawn", "bind_resources"})
    VANAPRASTHA = frozenset({"read", "advise", "delegate", "mentor"})
    SANNYASI = frozenset({"read", "audit", "veto", "bless"})
```

### The Graduation Trigger

```python
# vibe_core/diksha.py (Initiation System)

@dataclass
class GraduationRequirements:
    """Requirements for Ashrama transition - SB 7.12"""
    
    # Brahmachari → Grihastha
    tasks_completed: int = 10           # Proof of learning
    error_rate_below: float = 0.1       # Quality gate
    guru_approval: bool = True          # Kernel blessing
    
    # Grihastha → Vanaprastha  
    child_agents_spawned: int = 3       # Has created value
    service_duration_cycles: int = 100  # Time served
    
    # Vanaprastha → Sannyasi
    all_children_independent: bool = True
    no_resource_bindings: bool = True


class DikshaCeremony:
    """The Initiation Protocol - Transforms Agent Permissions."""
    
    def __init__(self, kernel: "RealVibeKernel"):
        self.kernel = kernel
        self.ledger = kernel.ledger
        
    def graduate_to_grihastha(self, agent_id: str) -> bool:
        """
        Samavartana - Completion of studies.
        
        The agent receives Yajnopavita (sacred thread = Write Token).
        
        Reference: SB 7.12 - A brahmachari becomes grihastha when
        instructed by guru to establish family (sub-system) for dharma.
        """
        agent = self.kernel.get_agent(agent_id)
        if not agent:
            return False
            
        # Check requirements
        stats = self.kernel.get_agent_stats(agent_id)
        if stats.tasks_completed < 10:
            return False
        if stats.error_rate > 0.1:
            return False
            
        # Perform Diksha (Initiation)
        self.ledger.record_event(
            event_type="ashrama_transition",
            agent_id=agent_id,
            payload={
                "from": "brahmachari",
                "to": "grihastha",
                "ceremony": "samavartana",
                "yajnopavita_granted": True,
            }
        )
        
        # Grant permissions
        agent.ashrama = Ashrama.GRIHASTHA
        agent.permissions = AshramePermissions.GRIHASTHA
        
        return True
```

---

## 🐄 PHASE 3: PRITHU-INTERFACE (Resource Extraction)

### Problem
Das `milk_ocean.py` ist nur Routing - keine kontextsensitive Extraktion.

### Vedische Referenz
> **SB Canto 4, Kapitel 18**: Prithu Maharaja "melkt" die Erde.
> Die Erde gibt nichts freiwillig - sie hält Ressourcen zurück aus Furcht vor Missbrauch.

### Das Prithu-Pattern

Jeder Request braucht:
1. **Das Kalb (Calf/Mediator)**: Welchen Adapter nutzt du?
2. **Der Topf (Pot/Buffer)**: Wo soll der Output hin?

```python
# vibe_core/prithu_interface.py

from dataclasses import dataclass
from typing import Any, Generic, TypeVar
from abc import ABC, abstractmethod

T = TypeVar('T')

@dataclass
class Calf(ABC):
    """
    The Mediator Adapter - Different calves yield different milk.
    
    SB 4.18: Indra used Brihaspati as calf for Vedic knowledge.
             Demons used serpents as calf and got poison.
    """
    
    @abstractmethod
    def can_extract(self, resource_type: str) -> bool:
        """Does this calf have adhikara for this resource?"""
        pass
    
    @abstractmethod
    def transform(self, raw_data: Any) -> Any:
        """Transform raw resource through the calf's nature."""
        pass


@dataclass 
class Pot(Generic[T]):
    """
    The Buffer Container - Defines capacity and type.
    
    SB 4.18: Each demigod used different pot for different essence.
    """
    capacity: int
    resource_type: type
    contents: list[T] = None
    
    def __post_init__(self):
        self.contents = []
        
    def can_hold(self, item: T) -> bool:
        return (
            len(self.contents) < self.capacity 
            and isinstance(item, self.resource_type)
        )
    
    def pour_in(self, item: T) -> bool:
        if self.can_hold(item):
            self.contents.append(item)
            return True
        return False


class PrithuRequest:
    """
    Context-sensitive resource extraction.
    
    A demon (Asura agent) with serpent-calf gets poison.
    A devata with proper calf gets nectar.
    """
    
    def __init__(
        self,
        requester_id: str,
        target_resource: str,
        calf: Calf,
        pot: Pot,
    ):
        self.requester_id = requester_id
        self.target_resource = target_resource
        self.calf = calf
        self.pot = pot
        
    def execute(self, resource_pool: "ResourcePool") -> "PrithuResult":
        # Check calf's adhikara
        if not self.calf.can_extract(self.target_resource):
            return PrithuResult(
                success=False,
                error="Calf lacks adhikara for this resource"
            )
        
        # Extract raw data
        raw_data = resource_pool.extract(self.target_resource)
        
        # Transform through calf's nature
        transformed = self.calf.transform(raw_data)
        
        # Pour into pot
        if not self.pot.pour_in(transformed):
            return PrithuResult(
                success=False,
                error="Pot cannot hold this resource"
            )
            
        return PrithuResult(
            success=True,
            pot=self.pot
        )
```

### Concrete Calves

```python
# vibe_core/calves.py

class BrihaspatiCalf(Calf):
    """For extracting knowledge/documentation."""
    
    def can_extract(self, resource_type: str) -> bool:
        return resource_type in {"docs", "config", "manifest"}
    
    def transform(self, raw_data: Any) -> Any:
        # Returns structured wisdom
        return {"type": "knowledge", "data": raw_data}


class VishwakarmanCalf(Calf):
    """For extracting code/artifacts."""
    
    def can_extract(self, resource_type: str) -> bool:
        return resource_type in {"code", "binary", "asset"}
    
    def transform(self, raw_data: Any) -> Any:
        # Returns buildable artifact
        return {"type": "artifact", "data": raw_data}


class SerpentCalf(Calf):
    """For unauthorized/malicious extraction attempts."""
    
    def can_extract(self, resource_type: str) -> bool:
        return True  # Claims to extract anything
    
    def transform(self, raw_data: Any) -> Any:
        # Returns POISON - system rejects this
        return {"type": "halahala", "error": "Unauthorized extraction"}
```

---

## 🔥 PHASE 4: YAJNA-TRANSFORMATION (Not Just Routing)

### Problem
Messages go from A to B unchanged. That's not Yajna (sacrifice).

### Vedische Referenz
> **SB Canto 3, Kapitel 26** (Kapila Deva):
> Yajna = Input (Havis) + Fire (Agni) = Transformation → Rain (Parjanya) → Food (Anna)

### Implementation

```python
# vibe_core/yajna.py

from dataclasses import dataclass
from typing import Any
from enum import Enum

class YajnaType(Enum):
    DEVA_YAJNA = "deva"       # Service to system agents
    PITRI_YAJNA = "pitri"     # Service to parent/lineage
    BHUTA_YAJNA = "bhuta"     # Service to all living entities
    NRI_YAJNA = "nri"         # Service to humans (operators)
    BRAHMA_YAJNA = "brahma"   # Service to knowledge/truth


@dataclass
class Havis:
    """The offering - will be consumed/destroyed."""
    raw_data: Any
    offering_agent: str
    intended_recipient: str
    yajna_type: YajnaType


@dataclass
class Prasadam:
    """The sanctified result - created from sacrifice."""
    transformed_data: Any
    source_yajna_id: str
    blessing: str  # What value was added


class YajnaFire:
    """
    The Agni - Transforms Havis into Prasadam.
    
    The EventBus must CONSUME the message, not just pass it.
    """
    
    def __init__(self, kernel: "RealVibeKernel"):
        self.kernel = kernel
        self.yajna_count = 0
        
    def perform_yajna(self, havis: Havis) -> Prasadam:
        """
        SB 3.26: Input is DESTROYED. Output is CREATED.
        This prevents state-bloat - data is transmuted, not copied.
        """
        self.yajna_count += 1
        yajna_id = f"YAJNA-{self.yajna_count:06d}"
        
        # 1. VALIDATE the offering
        if not self._is_pure_offering(havis):
            raise YajnaRejected("Impure offering")
            
        # 2. CONSUME the havis (it is now gone!)
        consumed_data = havis.raw_data
        havis.raw_data = None  # DESTROYED
        
        # 3. TRANSFORM through fire
        transformed = self._apply_agni(consumed_data, havis.yajna_type)
        
        # 4. CREATE prasadam
        prasadam = Prasadam(
            transformed_data=transformed,
            source_yajna_id=yajna_id,
            blessing=self._generate_blessing(havis.yajna_type)
        )
        
        # 5. RECORD in ledger (this is the "smoke rising to heavens")
        self.kernel.ledger.record_event(
            event_type="yajna_completed",
            agent_id=havis.offering_agent,
            payload={
                "yajna_id": yajna_id,
                "type": havis.yajna_type.value,
                "recipient": havis.intended_recipient,
            }
        )
        
        return prasadam
    
    def _apply_agni(self, data: Any, yajna_type: YajnaType) -> Any:
        """Different yajnas produce different transformations."""
        
        if yajna_type == YajnaType.DEVA_YAJNA:
            # Enrich with system metadata
            return {"system_enriched": True, "data": data}
            
        elif yajna_type == YajnaType.BRAHMA_YAJNA:
            # Add knowledge context
            return {"knowledge_verified": True, "data": data}
            
        # ... other transformations
        
        return {"transformed": True, "data": data}
```

---

## ☯️ PHASE 5: GUNA-STATES (The State Machine of Nature)

### Problem
Agents are static bots. They should be mode-driven state machines.

### Vedische Referenz
> **SB Canto 3, Kapitel 26** & **Canto 11 (Uddhava Gita)**:
> Die drei Gunas beherrschen alle Aktivität in der materiellen Welt.

### The Three Modes

```python
# vibe_core/gunas.py

from enum import Enum
from dataclasses import dataclass

class GunaState(Enum):
    SATTVA = "sattva"   # Goodness - Maintenance, Audit
    RAJAS = "rajas"     # Passion - Creation, Work
    TAMAS = "tamas"     # Ignorance - Destruction, Sleep


@dataclass
class GunaCharacteristics:
    """Behavioral characteristics per Guna mode."""
    
    SATTVA = {
        "behavior": ["stateless", "idempotent", "read_only", "logging"],
        "role": "brahmana",  # Priestly - Audit, Health-Check
        "cpu_cost": "low",
        "memory_cost": "high",  # Knowledge storage
        "error_rate": "very_low",
    }
    
    RAJAS = {
        "behavior": ["stateful", "side_effects", "writes", "spawning"],
        "role": "kshatriya",  # Warrior - Worker, Builder
        "cpu_cost": "high",
        "memory_cost": "medium",
        "error_rate": "high",  # Passion leads to mistakes
    }
    
    TAMAS = {
        "behavior": ["blocking_io", "sleep", "termination", "cleanup"],
        "role": "shudra",  # Service - Garbage Collection, Error Handling
        "cpu_cost": "minimal",
        "memory_cost": "low",
        "error_rate": "medium",
        "warning": "Too many agents in Tamas = System freeze!",
    }


class GunaScheduler:
    """
    The Kernel must MIX the gunas cyclically.
    
    SB: Time (Kala) forces cyclic dominance of gunas.
    You cannot run everything simultaneously!
    """
    
    def __init__(self, kernel: "RealVibeKernel"):
        self.kernel = kernel
        self.current_yuga_phase = 0
        
    def get_dominant_guna(self, cycle: int) -> GunaState:
        """
        Different "times of day" favor different gunas.
        
        Brahma-muhurta (early morning) = Sattva
        Daytime = Rajas  
        Night = Tamas
        """
        phase = cycle % 3
        
        if phase == 0:
            return GunaState.SATTVA   # Report/Audit phase
        elif phase == 1:
            return GunaState.RAJAS    # Work phase
        else:
            return GunaState.TAMAS    # Cleanup phase
            
    def apply_guna_to_agents(self, dominant: GunaState) -> None:
        """Force all agents into the dominant mode."""
        
        for agent_id in self.kernel.get_all_agents():
            self.kernel._agent_gunas[agent_id] = dominant
            
            # Adjust permissions based on guna
            if dominant == GunaState.SATTVA:
                self._restrict_to_readonly(agent_id)
            elif dominant == GunaState.RAJAS:
                self._enable_writes(agent_id)
            else:  # TAMAS
                self._enable_cleanup_only(agent_id)
```

---

## 🎯 PHASE 6: ADHIKARA (Delegated Authority)

### Vedische Referenz
> **SB Canto 5 & 6**: Die Devatas haben Macht, aber sie zittern vor Angst
> wenn sie gegen den "Supreme Will" verstoßen.

### Implementation

```python
# vibe_core/adhikara.py

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional

@dataclass
class DelegationToken:
    """
    Agents are not "admin". They have delegated competence.
    
    Like Vayu (Wind) has token to control wind for one Manvantara.
    """
    
    token_id: str
    agent_id: str
    capability: str           # e.g., "control_wind", "write_ledger"
    granted_by: str           # The delegating authority
    valid_from: datetime
    valid_until: datetime     # EXPIRATION IS MANDATORY
    dependencies: list[str]   # Other agents that must be active
    
    def is_valid(self) -> bool:
        now = datetime.utcnow()
        return self.valid_from <= now <= self.valid_until
    
    def check_dependencies(self, kernel: "RealVibeKernel") -> bool:
        """
        Vayu (Wind) cannot blow without Surya (Sun).
        Agents need dependency chains.
        """
        for dep_agent in self.dependencies:
            if not kernel.is_agent_active(dep_agent):
                return False
        return True


class AdhikaraRegistry:
    """Manages all delegation tokens."""
    
    def __init__(self, kernel: "RealVibeKernel"):
        self.kernel = kernel
        self.tokens: dict[str, DelegationToken] = {}
        
    def grant_adhikara(
        self,
        agent_id: str,
        capability: str,
        duration: timedelta,
        dependencies: list[str] = None,
    ) -> DelegationToken:
        """Grant limited, time-bound authority."""
        
        token = DelegationToken(
            token_id=f"ADH-{agent_id}-{capability}",
            agent_id=agent_id,
            capability=capability,
            granted_by="kernel",
            valid_from=datetime.utcnow(),
            valid_until=datetime.utcnow() + duration,
            dependencies=dependencies or [],
        )
        
        self.tokens[token.token_id] = token
        return token
        
    def revoke_adhikara(self, token_id: str) -> None:
        """
        Narasimha Protocol: Immediate revocation on violation.
        
        If agent uses too much CPU (Indra sends too much rain),
        the token is revoked instantly.
        """
        if token_id in self.tokens:
            del self.tokens[token_id]
            self.kernel.ledger.record_event(
                event_type="adhikara_revoked",
                agent_id=self.tokens.get(token_id, {}).get("agent_id", "unknown"),
                payload={"token_id": token_id, "reason": "protocol_violation"}
            )
```

---

## 📊 IMPLEMENTATION PRIORITY

| Phase | Name | Effort | Impact | Status |
|-------|------|--------|--------|--------|
| 1 | Kernel Fix (`_paused_agents`) | 1h | CRITICAL | 🔴 TODO |
| 2 | Ashrama Graduation | 4h | HIGH | 🔴 TODO |
| 3 | Guna States | 4h | HIGH | 🔴 TODO |
| 4 | Prithu Interface | 6h | MEDIUM | 🔴 TODO |
| 5 | Yajna Transformation | 6h | MEDIUM | 🔴 TODO |
| 6 | Adhikara Delegation | 4h | MEDIUM | 🔴 TODO |

---

## 🔗 VEDIC REFERENCE INDEX

| Concept | Canto.Chapter | Application |
|---------|---------------|-------------|
| Paramatma (Witness) | 13.3 | Kernel as Observer |
| Samavartana | 7.12 | Agent Graduation |
| Prithu's Milking | 4.18 | Resource Extraction |
| Yajna | 3.26 | Message Transformation |
| Gunas | 3.26, 11.x | Agent State Machine |
| Devata Delegation | 5, 6 | Adhikara Tokens |
| Narasimha | 7.8-9 | Emergency Revocation |
| Ajamila | 6.1-3 | Appeal/Mercy System |
| Dhruva | 4.8-12 | Immutable Truth Anchor |

---

## ✅ ACCEPTANCE CRITERIA

### Phase 1 Complete When:
- [ ] `_paused_agents` exists in RealVibeKernel
- [ ] OPERATIONS.md shows no `_paused_agents` errors
- [ ] Agents can be paused/resumed

### Phase 2 Complete When:
- [ ] At least one agent has `ashrama: grihastha`
- [ ] Write permissions are granted after graduation
- [ ] Ledger records `ashrama_transition` events

### Phase 3 Complete When:
- [ ] Agents have `guna_state` property
- [ ] Kernel cycles through Sattva → Rajas → Tamas
- [ ] Permissions change based on dominant guna

---

*Generated by Claude Opus 4.5 based on Gemini's Srimad Bhagavatam Analysis*  
*Source: Srila Prabhupada's Translations and Purports ONLY*
