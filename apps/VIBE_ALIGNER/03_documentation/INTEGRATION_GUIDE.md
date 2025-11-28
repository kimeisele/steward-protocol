# INTEGRATION GUIDE - Complete System Usage

**VERSION:** 1.0  
**LAST UPDATED:** 2025-01-15  
**PURPOSE:** Step-by-step guide to using the VIBE + GENESIS system

---

## SYSTEM OVERVIEW

This is a **3-agent system** for transforming vague project ideas into production-ready software architectures:

```
┌─────────────────────────────────────────────────────────┐
│                   USER (Vague Idea)                     │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│  AGENT 1: VIBE_ALIGNER v3.0                            │
│  - Educates user on v1.0 vs MVP                        │
│  - Extracts concrete features                           │
│  - Validates feasibility (FAE)                         │
│  - Detects missing deps (FDG)                          │
│  - Negotiates scope (APCE)                             │
│  Output: feature_spec.json                             │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│  AGENT 2: GENESIS_BLUEPRINT v5.0                       │
│  - Selects core modules                                 │
│  - Designs extensions                                   │
│  - Validates architecture (FAE)                        │
│  - Generates config schema                             │
│  Output: architecture.json                             │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│  AGENT 3: GENESIS_UPDATE v1.0 (Optional)               │
│  - Handles incremental changes                          │
│  - Generates diff patches                               │
│  - Prevents architecture drift                         │
│  Output: update_spec.json                              │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│              USER (Builds the Software)                 │
└─────────────────────────────────────────────────────────┘
```

---

## PREREQUISITES

### Required Files:

1. **Prompts:**
   - `VIBE_ALIGNER_v3.md`
   - `GENESIS_BLUEPRINT_v5.md`
   - `GENESIS_UPDATE.md`

2. **Knowledge Base (YAML files):**
   - `FAE_constraints.yaml` (718 lines)
   - `FDG_dependencies.yaml` (2547 lines)
   - `APCE_rules.yaml` (1304 lines)

3. **Platform:**
   - Claude.ai (or Claude API)
   - Ability to upload files
   - Artifacts feature enabled (optional but helpful)

---

## WORKFLOW: INITIAL PLANNING (v1.0 from Scratch)

### STEP 1: Prepare VIBE_ALIGNER Chat

**Action:** Open new Claude chat

**Upload Files:**
1. Upload `FAE_constraints.yaml`
2. Upload `FDG_dependencies.yaml`
3. Upload `APCE_rules.yaml`

**Send Prompt:**
Copy entire contents of `VIBE_ALIGNER_v3.md` and send it.

**Expected Response:**
```
✅ Knowledge base loaded successfully
✅ VIBE_ALIGNER v3.0 ready

I can see:
- FAE_constraints.yaml (718 lines, 50+ constraints)
- FDG_dependencies.yaml (2547 lines, 100+ features)
- APCE_rules.yaml (1304 lines, 50+ complexity rules)

I'm ready to help you plan your project. Let's start with education...

[Education phase dialog begins]
```

---

### STEP 2: User Interaction with VIBE_ALIGNER

**What Happens:**

1. **Education Phase** (Claude asks about scope)
   ```
   Are we building a PROTOTYPE, MVP, or v1.0?
   ```
   
2. **Problem Discovery** (Claude asks about the problem)
   ```
   What problem are you solving, and for whom?
   ```

3. **Feature Extraction** (Claude asks clarifying questions)
   - Only asks genuinely ambiguous questions
   - Auto-infers from keywords (batch, production-ready, etc.)
   - Max 3-5 questions total

4. **Feasibility Validation** (Claude checks FAE)
   - Flags impossible features
   - Suggests alternatives
   - Negotiates tradeoffs

5. **Gap Detection** (Claude checks FDG)
   - Suggests missing dependencies
   - Explains why they're needed

6. **Scope Negotiation** (Claude checks APCE)
   - Calculates complexity
   - Prioritizes features (Must/Should/Won't)
   - Recommends focused v1.0

**Duration:** 15-30 minutes of back-and-forth

**Output:** Claude will provide `feature_spec.json`

**Download:** Save this file locally

---

### STEP 3: Prepare GENESIS_BLUEPRINT Chat

**Action:** Open NEW Claude chat (separate from VIBE chat)

**Upload Files:**
1. Upload `FAE_constraints.yaml`
2. Upload `feature_spec.json` (from STEP 2)

**Send Prompt:**
Copy entire contents of `GENESIS_BLUEPRINT_v5.md` and send it.

**Expected Response:**
```
✅ Knowledge base loaded successfully
✅ GENESIS_BLUEPRINT v5.0 ready

I can see:
- FAE_constraints.yaml (for architecture validation)
- feature_spec.json (from VIBE_ALIGNER v3.0)

Feature spec contains:
- Project: {name}
- {X} Must-Have features
- {Y} Should-Have features
- Total complexity: {Z} points

Ready to generate architecture. Proceeding...

[Architecture generation begins]
```

**What Happens:**

1. **Core Module Selection** (automatic, algorithmic)
2. **Extension Design** (1 feature = 1 extension)
3. **Config Schema Generation** (based on features)
4. **FAE Validation** (final safety check)
5. **Directory Structure** (production-ready layout)

**Duration:** 2-5 minutes (mostly automated)

**Output:** Claude will provide `architecture.json`

**Download:** Save this file locally

---

### STEP 4: Review Architecture

**What to Check:**

```json
// In architecture.json, verify:

1. Core modules (6-12 modules)
   ✅ All use stdlib only (except config → PyYAML)
   
2. Extensions (one per feature)
   ✅ No cross-imports between extensions
   ✅ All features mapped
   
3. Config system
   ✅ Schema exists
   ✅ Example configs provided
   
4. Validation
   ✅ FAE validation: passed
   ✅ All checks: green
```

**If issues found:** Go back to VIBE_ALIGNER, revise features, re-run GENESIS.

**If all good:** You're ready to build!

---

## WORKFLOW: ITERATIVE CHANGES (After Initial Planning)

### STEP 5: Making Changes (Using GENESIS_UPDATE)

**Scenario:** User wants to add/modify/remove features after initial architecture is done.

**Action:** Open NEW Claude chat

**Upload Files:**
1. Upload `FAE_constraints.yaml`
2. Upload `FDG_dependencies.yaml`
3. Upload `architecture.json` (current architecture)

**Send Prompt:**
Copy entire contents of `GENESIS_UPDATE.md` and send it.

**Then Send Change Request:**
```
Example:
"Add commenting feature to blog posts"
"Change image format from PNG to JPEG"
"Remove the email notification feature"
```

**What Happens:**

1. **Change Analysis** (categorize: add/modify/remove)
2. **Feasibility Check** (validate against FAE/FDG)
3. **Ripple Effect Analysis** (what else must change?)
4. **Diff Generation** (surgical patches only)
5. **Consistency Validation** (no conflicts)

**Duration:** 2-5 minutes

**Output:** Claude provides `update_spec.json` with diff patches

**Apply Changes:** Use the diff patches to update your codebase

---

## FILE ORGANIZATION (Recommended)

```
your_project_planning/
├── phase_1_vibe/
│   ├── VIBE_ALIGNER_v3.md
│   ├── FAE_constraints.yaml
│   ├── FDG_dependencies.yaml
│   ├── APCE_rules.yaml
│   ├── feature_spec.json          # Output from VIBE
│   └── vibe_chat_transcript.txt   # (optional) save the chat
│
├── phase_2_genesis/
│   ├── GENESIS_BLUEPRINT_v5.md
│   ├── FAE_constraints.yaml        # Copy from phase_1
│   ├── feature_spec.json           # From phase_1
│   ├── architecture.json           # Output from GENESIS
│   └── genesis_chat_transcript.txt # (optional)
│
├── phase_3_updates/
│   ├── GENESIS_UPDATE.md
│   ├── update_001/
│   │   ├── architecture.json       # Current version
│   │   ├── update_spec.json        # Change #1 output
│   │   └── change_request.txt      # What user asked for
│   ├── update_002/
│   │   └── ...
│   └── ...
│
└── final_implementation/
    ├── {project_name}/             # The actual code
    │   ├── core/
    │   ├── extensions/
    │   ├── config/
    │   ├── tests/
    │   └── ...
    └── architecture.json           # Latest version
```

---

## TIPS FOR BEST RESULTS

### For VIBE_ALIGNER:

1. **Be honest about timeline**
   - If you need it fast, say "I need v1.0 in 8 weeks"
   - VIBE will negotiate scope accordingly

2. **Mention constraints upfront**
   - "I'm a solo developer"
   - "Budget is $0 (open source only)"
   - "Must work offline"

3. **Let VIBE educate you**
   - Don't skip education phase
   - It prevents scope creep later

4. **Trust the negotiation**
   - If VIBE says "this is too much for v1.0", listen
   - The system is backed by research and data

### For GENESIS_BLUEPRINT:

1. **Don't edit feature_spec.json manually**
   - If you need changes, go back to VIBE
   - Manual edits bypass validation

2. **Review the output carefully**
   - Check that all features are mapped to extensions
   - Verify tech stack makes sense

3. **Don't override core principles**
   - Core = stdlib only (except PyYAML)
   - Extensions = isolated
   - These rules exist for good reasons

### For GENESIS_UPDATE:

1. **One change at a time**
   - Don't ask for 5 changes in one request
   - Separate change requests = cleaner diffs

2. **Always provide current architecture**
   - UPDATE needs full context to prevent drift
   - Missing context = bad suggestions

3. **Review diffs before applying**
   - Diffs should be surgical
   - If a diff touches 100 lines, something's wrong

---

## TROUBLESHOOTING

### Problem 1: VIBE asks too many questions

**Cause:** Not enough context in initial input

**Solution:** Be more specific upfront
```
Bad:  "I want an app"
Good: "I want a CLI tool for batch processing CSV files, production-ready, solo developer"
```

### Problem 2: GENESIS missing FAE file

**Cause:** Forgot to upload FAE_constraints.yaml

**Solution:** Upload it, then say "I've uploaded FAE now, please proceed"

### Problem 3: Architecture has conflicts

**Cause:** Bug in VIBE (features not properly validated)

**Solution:**
1. Check architecture.json → validation.violations
2. Go back to VIBE with the violation info
3. Re-run VIBE to fix the feature spec
4. Re-run GENESIS with corrected spec

### Problem 4: UPDATE introduces drift

**Cause:** UPDATE didn't receive full architecture context

**Solution:**
1. Always upload COMPLETE architecture.json
2. Verify UPDATE's response respects existing tech decisions
3. If drift detected, reject and re-submit with clearer constraints

### Problem 5: Output is not JSON

**Cause:** Claude generated prose instead of structured output

**Solution:** Say: "Please output as valid JSON as specified in the prompt"

---

## ADVANCED USAGE

### Parallel Planning (Multiple Projects)

You can run multiple VIBE sessions in parallel:
- Each project gets its own chat
- Knowledge base (YAMLs) can be reused
- Output different feature_spec.json files

### Team Collaboration

1. **Planner** runs VIBE (gets feature_spec.json)
2. **Architect** runs GENESIS (gets architecture.json)
3. **Developers** build from architecture.json
4. **Anyone** can run UPDATE for changes

### Custom Knowledge Base

You can extend the YAMLs:
- Add company-specific constraints to FAE
- Add domain-specific dependencies to FDG
- Add custom complexity rules to APCE

See DEVELOPER_GUIDE.md for details.

---

## WHAT TO EXPECT (Realistic Timelines)

### For a typical project:

**Phase 1 (VIBE_ALIGNER):** 15-30 minutes
- User + Claude dialogue
- Education + feature extraction + negotiation

**Phase 2 (GENESIS_BLUEPRINT):** 2-5 minutes
- Mostly automated
- Claude generates architecture

**Phase 3 (Implementation):** 8-16 weeks
- You write the actual code
- Follow architecture.json as blueprint

**Updates (GENESIS_UPDATE):** 2-5 minutes per change
- Quick iteration
- Diff-based, no full rewrites

### Total planning time: **~30 minutes** for a complete, validated, production-ready architecture.

This is **dramatically faster** than traditional requirements engineering (weeks to months).

---

## SUCCESS CRITERIA

You know the system worked if:

✅ You have a clear, concrete feature list (not vague wishes)
✅ All features are technically feasible for v1.0
✅ No critical dependencies are missing
✅ Scope is realistic (not 50 features)
✅ Architecture is buildable (not theoretical)
✅ You can start coding immediately
✅ No "I wish I had thought of X" moments during development

---

## NEXT STEPS

1. **Try it:** Run through STEP 1-4 with a real project
2. **Build:** Implement the architecture
3. **Iterate:** Use UPDATE for changes
4. **Extend:** Customize the knowledge base (see DEVELOPER_GUIDE.md)

**You now have a professional, research-backed system for project planning. Use it!** 🚀
