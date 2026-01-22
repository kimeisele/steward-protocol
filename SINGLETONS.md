# SINGLETONS AUDIT - P0 Technical Debt

**Status:** IN PROGRESS
**Problem:** ~50+ Singletons bypass ServiceRegistry = NAGA-invisible islands
**Solution:** All singletons → ServiceRegistry.register() → NagaProxy wrapping

---

## ARCHITECTURE REMINDER

```
MAHAMANTRA (ROOT!)
    ↓
ServiceRegistry (DI Container)
    ↓
NagaProxy wrapping (when blessing enabled)
    ↓
Observable services (Narada sees all)
```

**OM is NOT root. MAHAMANTRA is root.**

---

## SINGLETON CATEGORIES

### 1. NAGA INFRASTRUCTURE (P0 - DONE!)

| File | Singleton | Protocol | Status |
|------|-----------|----------|--------|
| `naga/kulika.py` | `KulikaRegistry._instance` | `KulikaProtocol` | ✅ DONE |
| `naga/identity.py` | `NagaFederationIdentity._instance` | `NagaFederationIdentity` | ✅ DONE |
| `naga/mixins/vasuki.py` | `_vasuki_instance` | - | ✅ OK (per-instance cache) |
| `naga/mixins/takshaka.py` | `_takshaka_instance` | - | ✅ OK (per-instance cache) |
| `naga/mixins/sesha.py` | `_sesha_instance` | - | ✅ OK (per-instance cache) |
| `plugins/opus_assistant/events/syscall_listener.py` | `_syscall_listener_instance` | `SyscallListener` | ✅ DONE |

**NOTE**: The mixins (Vasuki, Takshaka, Sesha) are NOT global singletons! They cache
ServiceRegistry lookups per-instance (`self._*_instance`), which is correct pattern.

### 2. MAHAMANTRA SUBSTRATE (P0 - DONE!)

| File | Singleton | Protocol | Status |
|------|-----------|----------|--------|
| `mahamantra/substrate/prabhupada.py` | `_instance` | `PrabhupadaProtocol` | ✅ DONE |
| `mahamantra/substrate/phonetic_bridge.py` | `_bridge_instance` | `UniversalPhoneticBridge` | ✅ DONE |
| `mahamantra/protocols/_declaration.py` | `DeclarationRegistry._instance` | `DeclarationRegistry` | ✅ DONE |
| `mahamantra/protocols/_bridge.py` | `BridgeRegistry._instance` | `BridgeRegistry` | ✅ DONE |
| `mahamantra/protocols/_steward.py` | `StewardSystem._instance` | `StewardSystem` | ✅ DONE |

**NOTE**: All MAHAMANTRA substrate services are marked with `_naga_flooded = True`
(core infrastructure, no NagaProxy auto-wrap).

### 3. MAHAJANA PROTOCOLS (P0 - DONE!)

| File | Singleton | Protocol | Status |
|------|-----------|----------|--------|
| `protocols/mahajanas/narada/types/event_bus.py` | `_event_bus_instance` | `EventBusProtocol` | ✅ DONE |
| `protocols/mahajanas/brahma/types/sarga.py` | `_sarga_instance` | `SargaBootSequence` | ✅ DONE |
| `protocols/mahajanas/manu/types/pulse.py` | `PulseManager._instance` | `PulseManager` | ✅ DONE |
| `protocols/mahajanas/kapila/types/topology.py` | `_topology_instance` | `BhuMandalaTopology` | ✅ DONE |
| `protocols/mahajanas/nrisimha/types/narasimha.py` | `_narasimha_instance` | `NarasimhaProtocol` | ✅ DONE |

**NOTE**: All Mahajana services get auto-wrapped with NagaProxy (they're not infrastructure,
so they don't have `_naga_flooded = True`).

### 4. CORE SERVICES (P1 - DONE!)

| File | Singleton | Protocol | Status |
|------|-----------|----------|--------|
| `plugin_service.py` | `PluginService._instance` | `PluginServiceProtocol` | ✅ DONE |
| `section_service.py` | `SectionService._instance` | `SectionServiceProtocol` | ✅ DONE |
| `cartridge_service.py` | `CartridgeService._instance` | `CartridgeProtocol` | ✅ DONE |
| `circuit_service.py` | `CircuitService._instance` | `CircuitServiceProtocol` | ✅ DONE |
| `genesis/service.py` | `GenesisService._instance` | `GenesisService` | ✅ DONE |
| `services/learning_loop.py` | `LearningLoop._instance` | `LearningLoop` | ✅ DONE |

### 5. CLI & REGISTRY (P1 - DONE!)

| File | Singleton | Protocol | Status |
|------|-----------|----------|--------|
| `cli/command_registry.py` | `CommandRegistry._instance` | `CommandRegistry` | ✅ DONE |
| `cli/cartridge_bridge.py` | `LazyCartridgeRegistry._instance` | `LazyCartridgeRegistry` | ✅ DONE |
| `cli/ci_cli.py` | `CIManifest._instance` | `CIManifest` | ✅ DONE |
| `unified_registry.py` | `UnifiedRegistry._instance` | `UnifiedRegistry` | ✅ DONE |

### 6. STATE & COGNITIVE (P1)

| File | Singleton | Protocol | Status |
|------|-----------|----------|--------|
| `state/cognitive_weaver.py` | `_weaver_instance` | `CognitiveWeaverProtocol` | TODO |
| `runtime/context_loader.py` | `_context_instance` | `ContextManagerProtocol` | TODO |
| `plugins/opus_assistant/manas/cognitive_kernel.py` | class-level | `CognitiveKernelProtocol` | TODO |
| `plugins/opus_assistant/manas/akshara.py` | `Varnamala._instance` | `VarnamalaProtocol` | TODO |
| `plugins/opus_assistant/manas/triggers.py` | `SynapseVocabulary._instance` | `SynapseProtocol` | TODO |

### 7. PROTOCOLS & GOVERNANCE (P2)

| File | Singleton | Protocol | Status |
|------|-----------|----------|--------|
| `protocols/om.py` | `OM._instance` | `OMProtocol` | TODO |
| `protocols/governance/bridge.py` | `ProtocolBridge._instance` | `ProtocolBridgeProtocol` | TODO |
| `protocols/universal/types.py` | `_instance` | varies | TODO |
| `genesis/templates.py` | `TemplateRegistry._instance` | `TemplateRegistryProtocol` | TODO |

### 8. TOOLS & CARTRIDGES (P2)

| File | Singleton | Protocol | Status |
|------|-----------|----------|--------|
| `cartridges/system/auditor/tools/invariant_tool.py` | `_judge_instance` | `InvariantEngineProtocol` | TODO |
| `loaders/code_module_loader.py` | `_instance_cache` | `CodeRegistryProtocol` | TODO |
| `factory.py` | `_kernel_instance` | `KernelProtocol` | TODO |

---

## ALREADY FIXED (DONE)

| File | Singleton | Protocol | Commit |
|------|-----------|----------|--------|
| `runtime/providers/factory.py` | - | `LLMProvider` | `28d042b0` |
| `knowledge/graph.py` | `_graph_instance` | `KnowledgeGraphProtocol` | `28d042b0` |
| `services/kapila_service.py` | - | `KapilaProtocol` | `28d042b0` |
| `services/chat_nadi.py` | - | `ChatNadi` | `e17989a3` |
| `services/udana_router.py` | - | `UdanaRouter` | `e17989a3` |
| `services/chat_indriya.py` | - | `IndriyaProtocol` | `3e7179fc` |

---

## FIX PATTERN

```python
# BEFORE (raw singleton - BAD!)
_instance: Optional[MyService] = None

def get_my_service() -> MyService:
    global _instance
    if _instance is None:
        _instance = MyService()
    return _instance

# AFTER (ServiceRegistry - GOOD!)
def get_my_service() -> MyService:
    from vibe_core.di import ServiceRegistry

    existing = ServiceRegistry.get(MyServiceProtocol)
    if existing is not None:
        return existing

    instance = MyService()
    ServiceRegistry.register(MyServiceProtocol, instance)
    logger.info("MyService registered via ServiceRegistry (NAGA-observed)")

    return ServiceRegistry.get(MyServiceProtocol)
```

---

## PROGRESS TRACKER

- [x] Phase 0: ChatService dependencies (LLM, Knowledge, Kapila) - DONE
- [x] Phase 1: NAGA Infrastructure (3 real singletons + 3 OK mixins) - DONE
- [x] Phase 2: Mahamantra Substrate (5 singletons) - DONE
- [x] Phase 3: Mahajana Protocols (5 singletons) - DONE
- [x] Phase 4: Core Services (6 singletons) - DONE
- [x] Phase 5: CLI & Registry (4 singletons) - DONE
- [ ] Phase 6: State & Cognitive (5 singletons)
- [ ] Phase 7: Protocols & Governance (4 singletons)
- [ ] Phase 8: Tools & Cartridges (3 singletons)

**Total: ~17 singletons remaining** (was 43, 26 done so far)

---

## VERIFICATION

After each phase, run:
```bash
python -c "
from vibe_core.di import ServiceRegistry
ServiceRegistry.enable_naga_blessing()
# ... import and call get_* functions ...
# Verify type is NagaProxy
"
```

---

## NOTES

1. **Order matters**: NAGA first, then services that depend on NAGA
2. **Protocol required**: Each singleton needs a Protocol for ServiceRegistry key
3. **Circular imports**: Watch out for import cycles when adding ServiceRegistry
4. **Tests**: Run `pytest tests/ -k "service_name"` after each fix
