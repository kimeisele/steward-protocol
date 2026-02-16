# SYSTEM MAP — Production Systems for Energy Flow Integration

## 1. TWO INPUT PIPELINES (Currently Disconnected)

### A: `mahamantra("text")` — Lotus __call__ (lotus_core.py)
5 TattvaGates × 9 NavaBhakti steps. Deterministic. No LLM.
- PARSE: input → RAMA coords → seed (MahaCompression)
- VALIDATE: seed → attractor (synth) → parampara check (ShadowOracle)
- EXECUTE: resonant words (rank_words) + Gita verse match
- RESULT: position/guardian/quarter + RAMA phoneme signature
- SYNC: MahaCellUnified → CellRouter → Chamber.kirtan() → Yajna cycle
Returns: massive dict with vibration, verse, cell, antaranga state.

### B: `ChatService.chat()` — Chat Pipeline (services/chat_service.py)
- _compute_resonance(): keyword routing → Mahajana position
- MahajanaChat.respond(): LLM provider.invoke() with guardian persona
- FloodedMahajanaChat: 12 NAGA genes (audit, security, persistence)
Uses REAL external LLM. Does NOT use Antaranga or Chamber.

### THE GAP
Pipeline A computes deterministically but produces a dict, not language.
Pipeline B produces language but uses external LLM, not inner computation.
**The research engine bridges this gap.**

## 2. INNER CHAMBER — Antaranga (substrate/antaranga.py)
512 slots × 32 bytes = 16KB RAM. collide() for resonance, apply_diw() for modulation.
Owned by SankirtanChamber (production) and MahaLanguageEngine (research, separate).

## 3. OUTER CHAMBER — Sankirtana (substrate/chamber.py)
Owns: VenuOrchestrator + SiksastakamRegistry + AntarangaRegistry.
Methods: dance(), kirtan(), sankirtan(), spell_kirtan(), resonate_words().
Used by Lotus.__call__() at GATE 4 (SYNC).

## 4. INTENT — MantraKernel (kernel/intent.py)
MantraIntent(type, target, params, priority, requester, parampara_vector).
11 IntentTypes → MantraOpCode → Mahajana guardian.
MantraKernel.resolve(intent) → IntentResolver → IntentResult.
Resolvers must be manually registered. No auto-discovery yet.

## 5. SENSES — Indriya Protocol (protocols/_indriya.py, _sense.py)
5 Jnanendriyas: SROTRA(ear/logs), TVAK(skin/fs), CAKSU(eye/AST), JIHVA(tongue/tests), GHRANA(nose/smells)
5 Karmendriyas: VAK(voice), PANI(hands), PADA(feet), PAYU(cleanup), UPASTHA(creation)
5 Vrttis: PRAMANA/VIPARYAYA/VIKALPA/NIDRA/SMRTI
ManasProtocol: coordinates all senses → AggregatePerception → total_pain → chanting frequency.
**Status:** Protocols defined. No production implementations.

## 6. NADI — Message Passing (substrate/nadi.py)
5 types (Pancha Prana): PRANA/APANA/VYANA/UDANA/SAMANA.
9 operations (NavaBhakti): RECEIVE/SEND/CACHE/PROCESS/VALIDATE/REQUEST/DELEGATE/CONNECT/COMMIT.
LocalNadi: in-process hub, thread-safe, GAD-compliant. ChatService has _nadi but optional.

## 7. CELLS (substrate/cell.py, cell_router.py)
MahaCellUnified: 72-byte header + payload. Lifecycle: prana/integrity/cycle.
CellRouter: O(1) registry. Auto-registered via from_content().
CellularHealer (dharma/kumaras/healing_intent.py): CST fragment-level healing → Maya-sync.

## 8. SINGULARITY (kernel/singularity.py)
The `mahamantra` object. ProtocolRouter for all 16 guardians (dynamic import).
Owns: MahaCompression, LotusIPRouter, CellRouter, MahamantraProxy.
tick() → advances Kala + VenuOrchestrator.step() → DIW → broadcast.

## 9. CHAT (chat.py)
MahajanaChat: guardian-specific LLM chat with runtime PromptContext.
FloodedMahajanaChat: 12 NAGA genes wrapping every interaction.
guardian_chat(), routed_chat(), flooded_routed_chat() convenience functions.
get_guardian_for_message() uses ChatService._compute_resonance().

## 10. CLI COMMANDS (commands.py)
cli_chant(): SankirtanChamber.dance() + ShadowReactor Yajna cycle.
cli_listen(): subscribe to tick events.
cli_resolve(): MantraKernel.resolve(MantraIntent).
cli_serve(): Vimana network server.
cli_veda(): Gita verse lookup + resonance.
All capability-based, no hardcoded if/else.

## 11. GATE PROVIDERS (substrate/gate_providers.py)
5 providers at each TattvaGate: MantraGate(PARSE), StorageGate(VALIDATE),
InferGate(EXECUTE), SyncGate(RESULT), EnforceGate(SYNC).
Observers only — track stats, validate, but don't alter flow.
wire_gate_providers() exists but NOT called in boot sequence yet.

## 12. VENU SERVICE (services/venu_service.py)
250ms tick. MantraClock with 16 positions.
BeatSubscriberProtocol: OuroborosSubscriber(18s), ShuddhiSubscriber(36s),
KalaBridgeSubscriber, JagannathSubscriber.

---

## WHAT'S MISSING FOR INTEGRATION

1. **No language output from Pipeline A** — Lotus.__call__ returns a dict, not text
2. **No inner-chamber energy in Pipeline B** — Chat uses external LLM only
3. **No Manas/Buddhi coordinator** — Senses defined but not implemented
4. **MantraKernel resolvers not auto-discovered** — must be manually registered
5. **Gate providers not wired at boot** — exist but idle
6. **Research engine in research/ = dead code** — must migrate to production

## CLEAN INTEGRATION PATH (No Dirty Coupling)

The research MahaLanguageEngine does what neither pipeline does alone:
deterministic language generation from inner chamber resonance.

To integrate cleanly:
1. Engine lives in substrate/ or adapters/ (not research/)
2. Engine implements a Protocol (not imported directly)
3. Lotus.__call__ can optionally invoke it at GATE 2 (EXECUTE/SMARANAM)
4. ResonanceBridge converts output → MantraIntent (already built)
5. MantraKernel resolves the intent (existing infrastructure)
6. No Pipeline B changes needed — Chat can optionally use engine output as context
