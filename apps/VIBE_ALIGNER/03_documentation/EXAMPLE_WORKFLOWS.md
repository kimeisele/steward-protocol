# EXAMPLE WORKFLOWS - Real-World Usage Scenarios

**VERSION:** 1.0  
**LAST UPDATED:** 2025-01-15  
**PURPOSE:** Concrete examples of the system in action

---

## EXAMPLE 1: Simple CLI Tool (Clean v1.0)

### User Input to VIBE_ALIGNER:

```
I want to build a CLI tool for validating customer data from CSV files. 
It should check emails and phone numbers, then output a clean CSV. 
Needs to be production-ready. I'm a solo developer.
```

### VIBE_ALIGNER Session (Condensed):

**Claude (Education):**
```
Are we building: PROTOTYPE, MVP, or v1.0?
```

**User:**
```
v1.0
```

**Claude (Explanation):**
```
Excellent! A v1.0 means complete, stable solution for your core use case.

What problem are you solving, and for whom?
```

**User:**
```
I need to clean customer data from our CRM exports before importing to our email system.
It's for my own use, processing about 50-100 customers per week.
```

**Claude (Feature Extraction):**
```
✅ AUTO-DETECTED:
- Input: CSV files (from "customer data from CSV files")
- Scale: Solo user (from "my own use, 50-100 per week")
- Config: YAML (from "production-ready")

📋 FEATURES IDENTIFIED:
1. Email validation
2. Phone number validation
3. CSV output

❓ CLARIFYING QUESTIONS (2):

Q1: What format for phone numbers?
    A) International (E.164: +1234567890)
    B) US-only (123-456-7890)
    C) Any format (just check it's numeric)

Q2: What to do with invalid rows?
    A) Remove them completely
    B) Move to separate "invalid.csv" file
    C) Flag them in the same CSV with an "error" column

Answer format: "Q1: A, Q2: B"
```

**User:**
```
Q1: A (international), Q2: B (separate file)
```

**Claude (Validation & Output):**
```
✅ FEASIBILITY CHECK (FAE): All features OK for v1.0
✅ DEPENDENCY CHECK (FDG): Email validation library, phone validation library needed
✅ SCOPE ANALYSIS (APCE): Total complexity: 5 points (well within v1.0 range)

📄 SPECIFICATION COMPLETE

[Provides feature_spec.json - see below]
```

### Feature Spec Output (feature_spec.json):

```json
{
  "project": {
    "name": "Customer Data Validator",
    "category": "CLI Tool",
    "scale": "Solo User",
    "target_scope": "v1.0",
    "core_problem": "Clean CRM exports for email system import",
    "target_users": "Solo developer, internal use"
  },
  "features": [
    {
      "id": "feature_1",
      "name": "CSV Validation",
      "priority": "must_have",
      "complexity_score": 5,
      "estimated_effort": "1-2 weeks",
      "input": {
        "format": "CSV",
        "example": "id,name,email,phone\n1,Alice,alice@example.com,+1234567890",
        "constraints": "Max 1000 rows, required columns: id, name, email, phone"
      },
      "processing": {
        "description": "Validates email format (RFC 5322), validates phone format (E.164), removes invalid rows",
        "external_dependencies": ["email-validator", "phonenumbers"],
        "side_effects": ["Writes validation_errors.log", "Creates invalid.csv"]
      },
      "output": {
        "format": "CSV (2 files: valid.csv, invalid.csv)",
        "example": "valid.csv: cleaned data, invalid.csv: rejected rows with error reasons",
        "success_criteria": "All rows in valid.csv pass validation, all invalid rows in invalid.csv with clear error messages"
      },
      "dependencies": {
        "required": [
          {"component": "email_validation_library", "reason": "Must validate email format", "source": "FDG-XXX"},
          {"component": "phone_validation_library", "reason": "Must validate phone format", "source": "FDG-XXX"}
        ],
        "optional": []
      },
      "fae_validation": {"passed": true, "constraints_checked": [], "issues": []}
    }
  ],
  "scope_negotiation": {
    "total_complexity": 5,
    "complexity_breakdown": {"must_have": 5, "should_have": 0, "wont_have_v1": 0},
    "timeline_estimate": "1-2 weeks",
    "v1_exclusions": []
  },
  "validation": {
    "fae_passed": true,
    "fdg_passed": true,
    "apce_passed": true,
    "all_features_complete": true,
    "ready_for_genesis": true
  }
}
```

### GENESIS_BLUEPRINT Output (architecture.json - Condensed):

```json
{
  "genesis_architecture": {
    "project": {
      "name": "Customer Data Validator",
      "category": "CLI Tool",
      "version": "v1.0"
    },
    "core_modules": [
      {"name": "schema", "purpose": "Data models", "file_path": "core/schema.py"},
      {"name": "entity", "purpose": "Business entities", "file_path": "core/entity.py"},
      {"name": "io", "purpose": "CSV read/write", "file_path": "core/io.py"},
      {"name": "validation", "purpose": "Email/phone validation", "file_path": "core/validation.py"},
      {"name": "config", "purpose": "YAML config loading", "file_path": "core/config.py"},
      {"name": "error", "purpose": "Error handling", "file_path": "core/error.py"},
      {"name": "tracking", "purpose": "Job tracking", "file_path": "core/tracking.py"}
    ],
    "extensions": [
      {
        "name": "csv_validator",
        "purpose": "Validate CSV customer data",
        "implements_feature": "feature_1",
        "uses_core": ["io", "validation", "config", "error"],
        "external_deps": ["email-validator", "phonenumbers"],
        "file_path": "extensions/csv_validator.py"
      }
    ],
    "config_system": {
      "schema": {
        "sections": {
          "global": {
            "fields": [
              {"name": "log_level", "type": "enum", "default": "INFO"},
              {"name": "output_dir", "type": "path", "default": "./output"}
            ]
          },
          "csv_validator": {
            "fields": [
              {"name": "email_strict_mode", "type": "bool", "default": false},
              {"name": "phone_country_code", "type": "string", "default": "US"}
            ]
          }
        }
      }
    },
    "directory_structure": {
      "root": "customer_data_validator/",
      "core": "core/",
      "extensions": "extensions/",
      "config": "config/",
      "tests": "tests/"
    }
  }
}
```

### Result:
- **Planning time:** 10 minutes
- **Estimated implementation:** 1-2 weeks
- **Complexity:** Low (5 points)
- **Ready to build:** ✅

---

## EXAMPLE 2: Scope Negotiation Required

### User Input to VIBE_ALIGNER:

```
I want to build a social media platform with:
- Real-time video streaming
- AI-powered content recommendations
- Multi-language support (20+ languages)
- Custom analytics dashboard
- Live chat
- Stories (like Instagram)
- Content moderation with AI
- In-app purchases
- Push notifications

All for v1.0. Timeline: 3 months.
```

### VIBE_ALIGNER Session (Condensed):

**Claude (After Education Phase):**
```
⚠️ SCOPE ANALYSIS

I've analyzed your 9 major feature requests. The current scope presents significant challenges for a 3-month v1.0.

**Complexity Assessment:**
- Real-time video: 13 points (FAE-001 conflict - v2.0+ feature)
- AI recommendations: 8 points (FAE-004 conflict - requires data)
- Multi-language: 8 points (FAE-007 conflict - 40-60% overhead)
- Custom analytics: 5 points (FAE-005 conflict - build later)
- Live chat: 8 points (FAE-002 conflict - 10 months avg)
- Stories: 5 points
- AI moderation: 8 points
- In-app purchases: 8 points
- Push notifications: 3 points

**Total: 66 points** (5 features flagged as v2.0+)
**Recommended v1.0 max: 50-60 points**

**Timeline Reality Check:**
- Current scope: ~40-48 weeks (10-12 months!)
- Your timeline: 12 weeks (3 months)
- **Gap: 28-36 weeks**

---

**MUST HAVE (v1.0 Core)** - 13 points (~3 months):
1. User authentication (5 pts)
2. Post creation/viewing (5 pts)
3. Push notifications (3 pts)

**WON'T HAVE (v2.0+)** - 53 points:
- Real-time video → Use pre-recorded or embed YouTube/Vimeo
- AI recommendations → Use "Most Popular" sorting for v1.0
- Multi-language → English-only for v1.0
- Custom analytics → Use Google Analytics for v1.0
- Live chat → Add in v1.5 after validating core product
- Stories → v2.0 feature (complex UI/UX)
- AI moderation → Manual moderation for v1.0
- In-app purchases → Defer monetization to v1.5

---

**Reasoning:**
The core of a social platform is: create content, view content, engage.
Everything else is enhancement.

For v1.0, focus on proving users WANT to create and view content.
Then add bells and whistles in v1.5, v2.0.

**Your options:**
A) Proceed with focused v1.0 (3 months, shippable)
B) Keep all features (extend timeline to 10-12 months)
C) Tell me which 2-3 features are absolute non-negotiables

Which option aligns with your goals?
```

**User:**
```
Option A, but can we keep Stories? That's kind of important.
```

**Claude:**
```
Let me re-analyze with Stories included:

**UPDATED MUST HAVE (v1.0)** - 18 points (~4 months):
1. User authentication (5 pts)
2. Post creation/viewing (5 pts)
3. Stories (5 pts)
4. Push notifications (3 pts)

**Timeline:** 4 months (16 weeks) - slightly longer, but achievable.

**Tradeoff:** Stories add UI complexity (temporary content, viewer tracking).
This pushes us slightly over 3 months, but keeps your differentiator.

**Recommendation:** Proceed with this scope.
All other features → v2.0 after launch and user feedback.

Agreed?
```

**User:**
```
Yes, agreed.
```

### Result:
- **Original request:** 9 features, 66 points, 10-12 months
- **Negotiated v1.0:** 4 features, 18 points, 4 months
- **Time saved:** 6-8 months
- **Scope creep prevented:** ✅

---

## EXAMPLE 3: Impossible Feature Rejected

### User Input to VIBE_ALIGNER:

```
I want to build a v1.0 fitness app with real-time heart rate monitoring 
via Bluetooth, AI-powered workout recommendations, and collaborative 
editing of workout plans (like Google Docs). Timeline: 6 weeks.
```

### VIBE_ALIGNER Session (Condensed):

**Claude:**
```
⚠️ FEASIBILITY ISSUES DETECTED

I've analyzed your requirements and identified 3 v1.0 scope conflicts:

---

**Issue 1: Real-time Heart Rate Monitoring (Bluetooth)**

**FAE Violation:** FAE-025 (Bluetooth integration complexity)

**Why it's not v1.0-ready:**
Requires: Bluetooth Low Energy (BLE) implementation, device pairing UX, 
real-time data streaming, battery optimization, cross-platform compatibility 
(iOS/Android differences). Typical implementation: 4-6 weeks JUST for this feature.

**Your timeline:** 6 weeks TOTAL
**This feature alone:** 4-6 weeks

**For v1.0, I recommend:**
- Manual heart rate entry (user types it in)
- Integration with Apple Health/Google Fit (read existing data)

---

**Issue 2: Collaborative Editing (Operational Transform/CRDTs)**

**FAE Violation:** FAE-003 (Real-time collaborative editing)

**Why it's not v1.0-ready:**
Requires conflict resolution algorithms (CRDTs or OT) - this is specialized, 
complex engineering. Google Docs took YEARS to perfect this.

**Typical implementation:** 12+ weeks for basic version

**For v1.0, I recommend:**
- Standard text editor with "last write wins"
- Workout templates (not collaborative)

---

**Issue 3: AI-Powered Recommendations**

**FAE Violation:** FAE-004 (AI/ML recommendation engine)

**Why it's not v1.0-ready:**
Cold start problem (no user data), requires ML infrastructure, data pipeline.

**For v1.0, I recommend:**
- Pre-built workout templates
- Simple "popular workouts" list

---

**REVISED SCOPE (achievable in 6 weeks):**

**MUST HAVE:**
1. User authentication (1 week)
2. Workout logging (manual entry) (1.5 weeks)
3. Workout templates (pre-built) (1 week)
4. Basic stats/history (1.5 weeks)
5. Apple Health integration (read-only) (1 week)

**Total:** 6 weeks, realistic v1.0

**WON'T HAVE (v2.0+):**
- Bluetooth heart rate (v2.0)
- Collaborative editing (v3.0+)
- AI recommendations (v2.0)

---

Shall we proceed with the revised v1.0, or would you like to extend the timeline?
```

**User:**
```
OK, I see your point. Let's go with the revised scope.
```

### Result:
- **Original:** 3 impossible features, 6-week timeline (DOOMED TO FAIL)
- **Negotiated:** 5 achievable features, 6-week timeline (REALISTIC)
- **Crisis averted:** ✅

---

## EXAMPLE 4: Iterative Change (GENESIS_UPDATE)

### Scenario:
User already has architecture for a blog platform. Now wants to add commenting.

### User Input to GENESIS_UPDATE:

```
Add commenting feature to blog posts. Users should be able to:
- Post comments on any blog post
- Reply to comments (nested, 1 level deep)
- Edit their own comments
- Delete their own comments
```

### GENESIS_UPDATE Session (Condensed):

**Claude (Analysis):**
```
🔄 CHANGE ANALYSIS

**Change Type:** ADD_FEATURE
**Feature:** Comments on blog posts (with nested replies)

**Affected Components:**
- Database schema (new Comment table)
- Extensions (new comments extension)
- Config (comment settings)
- API (new endpoints)
- Tests (new test suite)

**Ripple Effects Identified:**
1. Database needs Comment model
2. API needs: POST /comments, GET /comments/:post_id, PUT /comments/:id, DELETE /comments/:id
3. Comments need authentication check (existing auth system)
4. Comments need validation (max length, spam prevention)
5. UI needs comment rendering (if web app)

---

**FEASIBILITY CHECK (FAE):**
✅ Comments = basic CRUD, OK for v1.0
✅ Nested replies (1 level) = manageable
✅ No real-time (no WebSockets needed)

**DEPENDENCY CHECK (FDG):**
Comments require:
- ✅ User authentication (already exists)
- ✅ Storage (already exists)
- ✅ Validation (already exists)
- ➕ Rate limiting (not yet implemented - RECOMMENDED)

**COMPLEXITY IMPACT:**
- Added complexity: +5 points
- Estimated effort: 3-5 days
- New total complexity: 28 points (was 23)

---

**GENERATING DIFF PATCHES...**
```

### Diff Patches Generated:

**Diff 1: architecture.json**
```diff
--- a/architecture.json
+++ b/architecture.json
@@ -45,6 +45,17 @@
       "name": "blog_posts",
       ...
     },
+    {
+      "name": "comments",
+      "purpose": "User comments on blog posts with nested replies",
+      "implements_feature": "feature_comments",
+      "uses_core": ["storage", "validation", "config"],
+      "external_deps": [],
+      "api": [
+        "create_comment(post_id, user_id, content, parent_id=None)",
+        "get_comments(post_id)",
+        "update_comment(comment_id, user_id, content)",
+        "delete_comment(comment_id, user_id)"
+      ],
+      "file_path": "extensions/comments.py"
+    }
   ]
```

**Diff 2: core/storage.py**
```diff
--- a/core/storage.py
+++ b/core/storage.py
@@ -15,6 +15,12 @@
 class BlogPost:
     ...
 
+@dataclass
+class Comment:
+    id: str
+    post_id: str
+    user_id: str
+    content: str
+    parent_id: Optional[str]
+    created_at: datetime
+    updated_at: datetime
```

**Diff 3: config/_schema.yaml**
```diff
--- a/config/_schema.yaml
+++ b/config/_schema.yaml
@@ -23,6 +23,16 @@
       - name: "max_post_length"
         default: 5000
   
+  comments:
+    description: "Comment system configuration"
+    fields:
+      - name: "max_comment_length"
+        type: "int"
+        default: 500
+      - name: "max_nesting_depth"
+        type: "int"
+        default: 1
+      - name: "require_moderation"
+        type: "bool"
+        default: false
```

**Claude (Summary):**
```
✅ UPDATE COMPLETE

**Changes Applied:**
1. Added 'comments' extension (new file: extensions/comments.py)
2. Added Comment model to core/storage.py
3. Added comments config section
4. Added comment tests (new file: tests/extensions/test_comments.py)

**Implementation Notes:**
- Create extensions/comments.py (150 LOC estimated)
- Modify core/storage.py (add Comment model)
- Update config/_schema.yaml and config.yaml
- Create tests/extensions/test_comments.py

**Estimated Effort:** 3-5 days

**No architecture drift:** Existing PostgreSQL database used, existing auth system reused.

[Download update_spec.json]
```

### Result:
- **Change requested:** Add comments
- **Ripple effects:** 4 components affected
- **Diffs generated:** 3 files
- **Architecture drift:** ❌ (prevented)
- **Time to plan:** 3 minutes

---

## EXAMPLE 5: Gap Detection in Action

### User Input to VIBE_ALIGNER:

```
I want a job board platform where companies can post jobs and 
candidates can apply. Companies should be able to review applications.
```

### VIBE_ALIGNER Session (Gap Detection):

**Claude:**
```
✅ FEATURES IDENTIFIED:
1. Job posting (companies)
2. Job application (candidates)
3. Application review (companies)

✅ COMPLETENESS CHECK (FDG)

I've analyzed these features and identified core components you'll need:

**For "Job Posting":**
- ✅ User authentication (for companies)
- ✅ Job database (to store job listings)
- ✅ Form validation (job title, description, requirements)
- ➕ Company profiles (companies need accounts - DID YOU FORGET THIS?)
- ➕ Job expiration/closing (jobs shouldn't stay open forever)

**For "Job Application":**
- ✅ User authentication (for candidates)
- ✅ Application database (to store applications)
- ➕ Resume upload (candidates need to attach resumes - CRITICAL!)
- ➕ Email notifications (notify company of new applications - IMPORTANT!)
- ➕ Application status tracking (draft/submitted/reviewed/accepted/rejected)

**For "Application Review":**
- ✅ Company dashboard (to view applications)
- ➕ Application filtering/search (companies will have many applications)
- ➕ Notes system (companies want to add notes about candidates)
- ➕ Communication system (companies need to contact candidates)

---

**MISSING COMPONENTS YOU FORGOT:**
1. Company profiles (users ≠ companies, need separate entity)
2. Resume upload & storage (critical for applications!)
3. Email notification system (companies MUST know about new applications)
4. Application status workflow (otherwise chaos)
5. Communication system (in-app messaging or email integration)

**Without these, your platform is incomplete.**

---

Shall I include these in the v1.0 specification?

Options:
A) Include all (realistic v1.0) - recommended
B) Exclude some (tell me which are optional)
C) Add more (if I missed anything else)
```

**User:**
```
Yes, include all. And we also need candidate profiles (like a resume page).
```

**Claude:**
```
✅ Added: Candidate profiles

**UPDATED SPECIFICATION:**
1. User authentication (dual roles: company, candidate)
2. Company profiles
3. Candidate profiles
4. Job posting
5. Resume upload & storage
6. Job application
7. Application status workflow
8. Application review dashboard
9. Email notifications
10. Application filtering/search

**Complexity:** 45 points
**Timeline:** 10-12 weeks

This is a complete, shippable v1.0 job board.

Proceeding to generate feature_spec.json...
```

### Result:
- **Original request:** 3 features (vague)
- **After gap detection:** 10 features (complete)
- **Missing components found:** 7
- **Platform completeness:** ✅

---

## KEY TAKEAWAYS

### From Examples:

1. **Example 1:** Clean projects with realistic scope → Fast planning, smooth execution
2. **Example 2:** Scope negotiation saves months of wasted effort
3. **Example 3:** Impossible features get rejected early (not after 3 weeks of coding)
4. **Example 4:** Iterative changes are surgical, prevent drift
5. **Example 5:** Gap detection prevents "Oh shit, we forgot X" moments

### Success Patterns:

✅ **Be specific about timeline** → Better scope negotiation  
✅ **Trust the FAE rejections** → They're research-backed  
✅ **Let FDG suggest deps** → Prevents incomplete implementations  
✅ **Accept APCE priorities** → Ensures shippable v1.0  
✅ **Use UPDATE for changes** → Maintains consistency  

---

**These examples show the system handling real-world complexity. Use them as templates for your own projects!** 📚
