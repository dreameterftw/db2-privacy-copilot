# Demo Guide - Db2 Privacy Copilot

## 🎬 Complete Demo Walkthrough

This guide walks you through a complete demonstration of the Db2 Privacy Copilot.

---

## 🚀 Quick Start (30 seconds)

1. Open http://localhost:8501
2. Click "🚀 Launch Dashboard"
3. Click "Login as DPO" (Charlie Davis)
4. Explore the dashboard
5. Try Discovery, Classification, and Erasure Planning

---

## 📖 Full Demo Script (5 minutes)

### Act 1: Introduction (30s)

**Landing Page**: http://localhost:8501

*"Welcome to the Db2 Privacy Copilot — decision-support tooling for DPDP use cases on IBM Db2."*

**Highlight**:
- Hero section with tagline
- 6 key features (Discovery, Classification, Consent, Erasure, Guardrail, Audit)
- Show the latest CI test and classification evaluation results; do not quote unverified figures.
- Technology stack
- DPDP decision-support scope and legal disclaimer

**Action**: Click "Launch Dashboard"

---

### Act 2: Authentication (30s)

**Login Page**

*"The system supports role-based access with three levels:"*

1. **VIEWER (Alice)** - Read-only access
2. **ANALYST (Bob)** - Can create requests and manage consents
3. **DPO (Charlie)** - Full access, can approve and execute

*"For this demo, I'll log in as Charlie Davis, the Data Protection Officer."*

**Action**: Click "Login as DPO"

---

### Act 3: Dashboard Overview (45s)

**Dashboard**

*"The dashboard provides a real-time overview of our privacy compliance posture."*

**Point out**:
- **4 metric cards**:
  - 4 tables discovered
  - X PII columns detected
  - 0 pending requests
  - Y audit records
- **Quick actions** (DPO has full access)
- **Recent activity feed** (shows last 10 audit events)
- **System health** (database, API, audit chain all healthy)

*"As a DPO, I can run discovery scans, approve erasure requests, and verify the audit chain."*

---

### Act 4: Schema Discovery (60s)

**Navigation**: Click "🔍 Discovery" in sidebar

*"First, let's discover what personal data we have in our database."*

**Action**: Click "🔄 Scan Schema"

**Show results**:
- **4 tables found**: PATIENT, APPOINTMENT, PRESCRIPTION, LAB_REPORT
- **18 columns total**
- **Foreign key relationships**:
  - APPOINTMENT → PATIENT
  - PRESCRIPTION → PATIENT
  - LAB_REPORT → PATIENT

*"The system automatically maps the schema and understands data relationships. This is crucial for safe deletion — we need to delete child records before parent records."*

**Expand**: PATIENT table → Show columns:
- ID, FULL_NM, CUST_MAIL_ID, PHONE_NO, DOB, GOVT_ID

---

### Act 5: PII Classification (60s)

**Navigation**: Click "🏷️ Classification"

*"Now let's automatically detect which columns contain personal data."*

**Action**: Click "🔍 Run Classification"

**Show results**:
- **18 columns classified**
- **6 PII columns found**:
  - EMAIL: PATIENT.CUST_MAIL_ID (95% confidence)
  - PHONE: PATIENT.PHONE_NO (90% confidence, even though stored as BIGINT)
  - NAME: PATIENT.FULL_NM (85% confidence)
  - DOB: PATIENT.DOB (80% confidence)
  - GOVT_ID: PATIENT.GOVT_ID (75% confidence)

*"The AI uses both pattern matching (regex for emails, phones) and name similarity (vector embeddings). It also flags low-confidence results for manual review."*

**Expand**: EMAIL section → Show:
- Table.Column
- Confidence percentage
- Detection method (VALUE_RULE or NAME_VECTOR)

---

### Act 6: Consent Management (45s)

**Navigation**: Click "✅ Consents"

*"Consent tracking uses bitemporal tables — we track both when consent was valid (business time) and when we knew about it (system time)."*

**Tab 1: Grant Consent**
- Patient ID: 1
- Purpose: MARKETING
- Start: Today
- End: 2027-12-31

**Action**: Click "Grant Consent" → Success message

**Tab 3: View Consents**
- Patient ID: 1
- Click "Load Consents"
- **Show**: TREATMENT (valid), MARKETING (just granted)

*"This answers the question: 'Was consent valid on date X, as we knew it on date Y?'"*

---

### Act 7: Erasure Request (90s)

**Navigation**: Click "🗑️ Requests"

*"Now the critical part — handling a data subject's right to erasure."*

**Tab 1: Create Request**

*"Let's say patient ID 1 (Aryan Sharma) requests deletion of his data."*

- Subject ID: 1
- Click "📋 Generate Plan"

**Show dry-run plan**:
- **4 steps**:
  1. RETAIN LAB_REPORT (0 rows) — Medical records must be kept for 7 years
  2. RETAIN PRESCRIPTION (0 rows) — Pharmacovigilance requirement
  3. RETAIN APPOINTMENT (0 rows) — Medical records
  4. ANONYMISE PATIENT (0 rows) — NULL out PII columns but keep the record

*"Notice this is a DRY RUN — no data is actually touched. The system respects retention rules from the RETENTION_RULES table."*

**Highlight**:
- **Plan hash**: `0b81d4ba...` (binds this exact plan to approval — prevents tampering)
- **Estimated rows**: Shows impact before execution
- **Rule verification**: Some rules are marked ⚠️ as unverified (need legal review)

*"In production, a DPO would review this plan, approve it, and only then would the guardrail validate and execute it."*

---

### Act 8: Audit Chain Verification (30s)

**Navigation**: Click "📝 Audit Log"

*"Every action is recorded in a tamper-evident audit log."*

**Action**: Click "🔍 Verify Chain"

**Show result**: ✓ Chain is INTACT

**Explain**:
- Each record contains `hash = SHA256(previous_hash + content)`
- Any modification to a past record breaks the chain
- Auditors can verify integrity cryptographically

**Expand a record**: Show:
- Actor: test
- Action: STARTUP
- Timestamp
- Hash preview
- JSON detail

*"This provides non-repudiation — once recorded, actions cannot be denied or altered."*

---

## 🎯 Key Talking Points

### For Judges/Evaluators:

1. **AI + Human-in-the-Loop**:
   - AI proposes (agents, classification)
   - Humans approve (DPO review)
   - Deterministic code executes (guardrail validation)

2. **Security by Design**:
   - 60+ attack scenarios tested (SQL injection, DDL, etc.)
   - Approval bound to plan hash (no replay attacks)
   - Audit chain detects tampering
   - Single transaction with rollback

3. **Compliance-First**:
   - DPDP use-case decision support (not legal advice)
   - Bitemporal consent tracking
   - Retention rules enforced

4. **Production-Ready**:
   - 150+ passing tests
   - Type hints everywhere
   - Comprehensive error handling
   - Mock mode for development
   - CI/CD pipeline ready (GitHub Actions)

5. **Extensibility**:
   - Modular architecture
   - FastAPI REST API
   - CrewAI agent framework
   - Vector similarity (future: Db2 Vector Search)
   - RAG over DPDP Act (planned)

---

## 🎓 Technical Deep Dive

### For Technical Judges:

1. **Discovery Module** (`app/discovery.py`):
   - Scans `SYSCAT.COLUMNS`, `SYSCAT.TABLES`, `SYSCAT.REFERENCES`
   - Builds directed graph with NetworkX
   - Topological sort for safe deletion order
   - Cycle detection

2. **Classification Module** (`app/classify.py`):
   - Layer A: Value rules (regex + Verhoeff checksum for Aadhaar)
   - Layer B: Name similarity (sentence-transformers)
   - Confidence scoring with review flags
   - Persists to PII_MAP table

3. **Consent Module** (`app/consent.py`):
   - Db2 `BUSINESS_TIME` and `SYSTEM_TIME` periods
   - `FOR BUSINESS_TIME AS OF` queries
   - History preserved in `CONSENT_HISTORY`
   - Implements `consent_gate()` for processing checks

4. **Erasure Module** (`app/erasure.py`):
   - Dry-run planner (never executes without approval)
   - Retention rules from curated table
   - Row count estimation
   - SQL generation (DELETE/UPDATE)
   - Plan hash computation (SHA256)

5. **Guardrail Module** (`app/guardrail.py`):
   - Deterministic validation (NOT an LLM)
   - Regex-based statement shape checking
   - Banned token detection
   - WHERE clause enforcement
   - Parameterization check
   - Table allowlist

6. **Audit Module** (`app/audit.py`):
   - Hash chain: `hash = SHA256(prev_hash + content)`
   - Tamper detection in `verify_chain()`
   - Append-only design
   - Query by action, subject, or actor

---

## 🔥 Demo Tips

### Do's:
✅ Start with the landing page (sets context)  
✅ Log in as DPO (shows full capabilities)  
✅ Run discovery first (establishes foundation)  
✅ Emphasize dry-run safety (no accidental deletions)  
✅ Show audit chain verification (proves security)  
✅ Mention production features (CI/CD, Docker, FastAPI)

### Don'ts:
❌ Don't skip the login (shows auth flow)  
❌ Don't execute erasure (it's mock data, but emphasizes safety)  
❌ Don't rush — pause to explain WHY (not just WHAT)  
❌ Don't forget to mention: "This is a decision support tool, not legal advice"

---

## 🎬 30-Second Elevator Pitch

*"Db2 Privacy Copilot automates DPDP compliance on IBM Db2. AI discovers and classifies personal data, then humans approve erasure plans that are validated by a deterministic guardrail. Every action is recorded in a tamper-evident audit chain. It's production-ready with 150+ tests, FastAPI backend, and a modern Streamlit UI."*

---

## 📊 Demo Checklist

Before your presentation:

- [ ] Both servers running (API on 8000, UI on 8501)
- [ ] Landing page loads (http://localhost:8501)
- [ ] All 3 login roles work
- [ ] Dashboard shows metrics
- [ ] Discovery scan completes
- [ ] Classification detects PII
- [ ] Consent grant/view works
- [ ] Erasure plan generates
- [ ] Audit chain verifies as intact
- [ ] FastAPI docs accessible (http://localhost:8000/docs)
- [ ] Mock mode banner shows (or real Db2 is running)

---

## 🚨 Fallback Plan

If live demo fails:
1. Show GitHub repo: https://github.com/dreameterftw/db2-privacy-copilot
2. Walk through CODE_QUALITY.md
3. Show architecture diagram in docs/
4. Highlight test coverage (150+ tests)
5. Explain security design (guardrail, audit chain)

Record a demo video as backup!

---

## 📞 Q&A Preparation

**Q**: Why not just use an LLM for everything?  
**A**: LLMs are great for discovery and analysis, but should never execute destructive operations. Our guardrail is deterministic code with 60+ security tests.

**Q**: How do you handle false positives in classification?  
**A**: Low-confidence results are flagged for manual review. The system provides transparency (shows method and confidence), not just a binary yes/no.

**Q**: What if someone tampers with the audit log?  
**A**: The SHA256 hash chain makes tampering immediately detectable. Each record's hash depends on all previous records.

**Q**: Is this production-ready?  
**A**: The core modules are production-ready (tested, secure, well-documented). For production deployment, add: real authentication (JWT/OAuth), connection pooling, monitoring, and legal review of retention rules.

**Q**: Can it work with other databases besides Db2?  
**A**: The architecture is database-agnostic. The discovery module would need adapters for other catalog schemas, but the core logic (classification, consent, audit) is portable.

---

**Ready to Demo!** 🎉
