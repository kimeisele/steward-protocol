# NAGA RECON REPORT - Phase 2 Active Reconnaissance

> ASHVAMEDHA: The Horse has wandered. Here is what it found.

---

## CLASSIFICATION SUMMARY

| Category | Count | Action |
|----------|-------|--------|
| FLOODED | 7 | Controlled |
| PARTIALLY FLOODED | 3 | Need full integration |
| REBEL | 25+ | Priority targets |
| CIVILIAN | ~10 | Monitor only |

---

## FLOODED (Conquered Territory)

All 7 NAGA services with @naga_service decorator:

| Service | Location | Protocol |
|---------|----------|----------|
| SeshaService | naga/services/sesha.py | SeshaProtocol |
| TakshakaService | naga/services/takshaka.py | TakshakaProtocol |
| VasukiService | naga/services/vasuki.py | VasukiProtocol |
| KaliyaService | naga/services/kaliya.py | KaliyaProtocol |
| NaradaService | naga/services/narada.py | NaradaProtocol |
| ChitraguptaService | naga/services/chitragupta.py | ChitraguptaProtocol |
| PrahladService | naga/services/prahlad.py | PrahladProtocol |

---

## PARTIALLY FLOODED (Uses ServiceRegistry, no @naga_service)

| Service | Location | Has | Needs |
|---------|----------|-----|-------|
| CorrectionOrchestrator | services/correction_dispatcher.py | ServiceRegistry | Full NAGA protocol |
| QuantumHealingResolver | services/healing_resolver.py | ServiceRegistry | Chitragupta profiling |
| NagaStateProxy | services/naga/state_proxy.py | TakshakaProtocol | Already NAGA-aware |

---

## REBELS (Active Targets)

### TIER 1: Core Services (HIGH PRIORITY)

| Service | Location | Indicators | Needs |
|---------|----------|------------|-------|
| **ManifestationService** | services/manifestation_service.py | State mutation, file writes | Narada observation |
| **CapabilityEnforcerService** | services/capability_enforcer.py | Security/permission logic | Takshaka validation |
| **LifecycleService** | services/lifecycle_service.py | Boot/shutdown, resilience | Prahlad resilience |
| **StateService** | state/state_service.py | Core state mutations | Sesha ledger |
| **PersonaManager** | state/persona.py | Identity state | Sesha + Takshaka |

### TIER 2: Opus Assistant (MEDIUM-HIGH)

| Service | Location | Indicators | Needs |
|---------|----------|------------|-------|
| **OpusStateManager** | plugins/opus_assistant/core/state_manager.py | State mutations | Sesha |
| **OpusContextService** | plugins/opus_assistant/core/context_service.py | Context/session | Narada observation |
| **ShivaLifecycleManager** | plugins/opus_assistant/manas/shiva.py | Lifecycle | Prahlad |
| **ActionManager** | plugins/opus_assistant/manas/action_manager.py | Action dispatch | Chitragupta |
| **SenseManager** | plugins/opus_assistant/manas/sense_manager.py | Input processing | Takshaka |
| **KernelTickHandler** | plugins/opus_assistant/events/kernel_tick.py | Event handling | Narada |

### TIER 3: Router Handlers (MEDIUM)

| Service | Location | Needs |
|---------|----------|-------|
| SystemHandler | manas/router/handlers/system_handler.py | Takshaka |
| ResearchHandler | manas/router/handlers/research_handler.py | Narada |
| ShellHandler | manas/router/handlers/shell_handler.py | Takshaka + Kaliya |
| HarnessHandler | manas/router/handlers/harness_handler.py | Chitragupta |
| SutraHandler | manas/router/handlers/sutra_handler.py | Sesha |
| DharmaHandler | manas/router/handlers/audit_handler.py | Prahlad |

### TIER 4: Cartridge Services (MEDIUM)

| Service | Location | Indicators | Needs |
|---------|----------|------------|-------|
| ActionHandlerRegistry | cartridges/system/envoy/action_handlers.py | Central registry | Kulika schema |
| TwitterService | cartridges/system/herald/services/twitter.py | External API | Vasuki |
| RedditService | cartridges/system/herald/services/reddit.py | External API | Vasuki |
| LifecycleManager | cartridges/system/civic/tools/lifecycle_manager.py | Agent lifecycle | Prahlad |

### TIER 5: Other Plugins (LOW-MEDIUM)

| Service | Location | Needs |
|---------|----------|-------|
| VedicStateManager | plugins/vedic_governance/state_manager.py | Sesha |
| TaskManagerPlugin | plugins/task_manager/plugin_main.py | Narada observation |

---

## CIVILIAN (Non-Targets)

These are utilities or base classes - no infrastructure integration needed:

- `BaseHandler` - Abstract base class (template only)
- `NullTaskManager` - Null pattern implementation
- `CoreManagerAdapter` - Adapter pattern
- `ServiceType` (Enum) - Just an enum

---

## INFILTRATION PRIORITY

Based on Detection Criteria and impact:

### IMMEDIATE (Next Sprint)
1. **StateService** - Core state, everything flows through here
2. **ManifestationService** - Doc generation, high visibility
3. **CapabilityEnforcerService** - Security surface

### SHORT-TERM
4. **OpusStateManager** - Plugin state
5. **ActionManager** - Action dispatch hub
6. **SenseManager** - Input validation point

### MEDIUM-TERM
7. Router Handlers (bulk operation - shared BaseHandler pattern)
8. Cartridge services
9. Other plugins

---

## ATTACK VECTORS

### Vector A: Protocol Injection
Add NAGA protocol imports + ServiceRegistry.get() for needed services.

### Vector B: Decorator Addition
Where appropriate, add @naga_service for auto-discovery.

### Vector C: Cortex Wiring
Connect to NagaCortex for observation/profiling.

### Vector D: CorrectionHandler
Register as drift handler where service can heal.

---

## METRICS

- **Total Services Discovered:** 45+
- **FLOODED:** 7 (15%)
- **REBEL:** 25+ (55%)
- **Coverage Gap:** ~40% needs infiltration

---

*Recon complete. Awaiting orders for Phase 3: Systematic Flooding.*
