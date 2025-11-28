# MASTER PLAN: Knowledge Base Asset Generation

## OVERVIEW
This document coordinates the creation of 3 critical knowledge base assets for the VIBE_ALIGNER + GENESIS_BLUEPRINT system.

---

## WORKFLOW

### STEP 1: Send Research Requests (YOU DO THIS)
Send the 3 research request files to a separate Claude instance (or team):

1. **RESEARCH_REQUEST_1_FAE.md** → Get `FAE_constraints.yaml`
2. **RESEARCH_REQUEST_2_FDG.md** → Get `FDG_dependencies.yaml`  
3. **RESEARCH_REQUEST_3_APCE.md** → Get `APCE_rules.yaml`

**Estimated time per research:** 2-4 hours per asset (depending on thoroughness)

**Can be parallelized:** Yes! All 3 can be researched simultaneously by different Claude instances.

---

### STEP 2: Receive & Validate Assets (YOU DO THIS)
When you receive the YAML files, validate them against criteria:

**FAE_constraints.yaml checklist:**
- ✅ At least 50 constraint entries
- ✅ Covers: incompatibilities, NFR conflicts, tech constraints, time estimates
- ✅ Each constraint has: ID, reason, alternatives, scope recommendation
- ✅ Research-backed (not generic fluff)

**FDG_dependencies.yaml checklist:**
- ✅ At least 100 feature entries
- ✅ Covers: required dependencies, optional dependencies, cascading chains
- ✅ Each dependency has: component name, reason, missing consequence
- ✅ Common forgotten dependencies section exists

**APCE_rules.yaml checklist:**
- ✅ At least 50 feature complexity scores
- ✅ Value patterns defined (10-15)
- ✅ Multipliers database (20+)
- ✅ Negotiation templates (10+)
- ✅ Clear MoSCoW mapping logic

---

### STEP 3: Send Assets Back to Me (YOU DO THIS)
Once you have all 3 validated YAML files, send them to me (the Claude instance writing this).

**I will then:**
1. ✅ Create `VIBE_ALIGNER_v3.md` (prompt that uses these assets)
2. ✅ Create `GENESIS_BLUEPRINT_v5.md` (prompt that uses these assets)
3. ✅ Create `GENESIS_UPDATE.md` (new prompt for iterative refinement)
4. ✅ Create implementation guide
5. ✅ Create testing strategy with Golden Dataset starter

---

## WHAT HAPPENS AFTER ASSETS ARE COMPLETE?

### Deliverables I Will Provide:

```
final_system/
├── prompts/
│   ├── VIBE_ALIGNER_v3.md          # Uses FAE, FDG, APCE
│   ├── GENESIS_BLUEPRINT_v5.md     # Uses FAE
│   └── GENESIS_UPDATE.md           # For iterative changes
├── knowledge_base/
│   ├── FAE_constraints.yaml        # From research
│   ├── FDG_dependencies.yaml       # From research
│   └── APCE_rules.yaml             # From research
├── implementation/
│   ├── INTEGRATION_GUIDE.md        # How to wire everything together
│   ├── TESTING_STRATEGY.md         # How to validate the system
│   └── GOLDEN_DATASET_STARTER.md   # Initial test cases
└── examples/
    ├── example_vibe_session.md     # Sample interaction
    └── example_genesis_output.json # Sample architecture
```

---

## TIMELINE ESTIMATE

**If researched sequentially:**
- Research Asset 1 (FAE): 2-4 hours
- Research Asset 2 (FDG): 2-4 hours
- Research Asset 3 (APCE): 2-4 hours
- **Total:** 6-12 hours

**If researched in parallel (3 Claude instances):**
- All 3 assets: 2-4 hours (same time)
- **Total:** 2-4 hours

**After assets returned to me:**
- Prompt creation: 2-3 hours
- Implementation guide: 1 hour
- Testing strategy: 1 hour
- **Total:** 4-5 hours

**GRAND TOTAL:** 10-17 hours for complete professional system

---

## CRITICAL SUCCESS FACTORS

### For Research Phase:
1. **Depth over breadth:** Better to have 50 well-researched constraints than 100 generic ones
2. **Real-world sources:** Prefer actual project post-mortems over theoretical articles
3. **Actionable details:** Each entry must have concrete reasons, not vague descriptions
4. **Consistent format:** YAML structure must be exactly as specified in templates

### For Integration Phase:
1. **Test with real inputs:** Once prompts are ready, test with actual vague project ideas
2. **Iterate on failures:** Build the Golden Dataset from real failures
3. **Validate against anti-SLOP criteria:** Ensure outputs are concrete, not generic

---

## WHAT YOU NEED TO DO NOW

### Immediate Next Steps:

1. **Choose research strategy:**
   - Serial: Send requests one at a time to same Claude instance
   - Parallel: Send all 3 requests to different Claude instances simultaneously

2. **Send research requests:**
   - Copy content of `RESEARCH_REQUEST_1_FAE.md`
   - Send to Claude instance with instruction: "Please execute this research plan and deliver FAE_constraints.yaml"
   - Repeat for REQUEST_2 and REQUEST_3

3. **Wait for deliverables:**
   - You should receive 3 YAML files
   - Validate them against checklists above

4. **Return to me:**
   - Send all 3 YAML files
   - I will create the final prompt system

---

## QUESTIONS?

**If you're unsure about anything:**
- The research requests are self-contained and fully specified
- Each request includes validation criteria
- Each request includes source recommendations
- The receiving Claude instance should have everything needed

**Common questions:**

**Q: Can I modify the research requests?**  
A: Yes, but preserve the deliverable format (YAML structure)

**Q: What if one asset is incomplete?**  
A: Send what you have, I'll identify gaps and you can request targeted follow-up

**Q: Can I start with just 1 asset?**  
A: Yes! We can build iteratively. Start with FAE (most critical for Blind Spot 1)

**Q: How do I know if quality is good enough?**  
A: Use validation checklists in Step 2. If entries are generic/vague, request more depth

---

## READY TO START?

Send the 3 research requests now! 🚀

Once you have the YAML files back, ping me and we'll build the final system.
