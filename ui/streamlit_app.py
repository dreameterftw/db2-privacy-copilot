"""
Streamlit UI for Db2 Privacy Copilot.

Quick interactive interface for demonstration purposes.
For production, consider React + API approach.
"""
import json
from datetime import date

import streamlit as st

# Import app modules
import sys
sys.path.insert(0, "..")

from app import agents, audit, consent, erasure
from app.config import settings
from app.db import query

# Page config
st.set_page_config(
    page_title="Db2 Privacy Copilot",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for better UI
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
    }
    .success-box {
        padding: 15px;
        border-radius: 5px;
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        margin: 10px 0;
    }
    .warning-box {
        padding: 15px;
        border-radius: 5px;
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        margin: 10px 0;
    }
    .error-box {
        padding: 15px;
        border-radius: 5px;
        background-color: #f8d7da;
        border-left: 4px solid #dc3545;
        margin: 10px 0;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        background-color: #1f77b4;
        color: white;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #1557a0;
    }
</style>
""", unsafe_allow_html=True)

# Title and intro
st.title("🔒 Db2 Privacy Copilot")
st.markdown("*DPDP Compliance System for IBM Db2*")
st.markdown("---")

# Sidebar navigation
st.sidebar.image("https://via.placeholder.com/150x50/1f77b4/ffffff?text=DB2+Privacy", use_container_width=True)
st.sidebar.markdown("### Navigation")

page = st.sidebar.selectbox(
    "Choose a section",
    [
        "📊 Dashboard",
        "🔍 Discovery",
        "🏷️ Classification",
        "✅ Consent Management",
        "🗑️ Rights Requests",
        "📝 Audit Log",
        "❓ Help & Guide",
    ]
)

# Add contextual help in sidebar
st.sidebar.markdown("---")
st.sidebar.markdown("### 💡 Quick Tips")

if page == "📊 Dashboard":
    st.sidebar.info("Dashboard shows system health and recent activity.")
elif page == "🔍 Discovery":
    st.sidebar.info("Discovery maps your database schema and relationships automatically.")
elif page == "🏷️ Classification":
    st.sidebar.info("Classification identifies PII columns using AI-powered pattern matching.")
elif page == "✅ Consent Management":
    st.sidebar.info("Track and manage user consents with bitemporal precision.")
elif page == "🗑️ Rights Requests":
    st.sidebar.info("Handle erasure requests with AI-assisted planning and human approval.")
elif page == "📝 Audit Log":
    st.sidebar.info("View tamper-proof audit trail with cryptographic verification.")
elif page == "❓ Help & Guide":
    st.sidebar.info("Learn how to use the Privacy Copilot effectively.")

# Session state initialization
if 'schema' not in st.session_state:
    st.session_state.schema = settings.db2_schema


# Dashboard Page
if page == "📊 Dashboard":
    st.header("Dashboard")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # Count tables
        try:
            result = agents.discover_schema(st.session_state.schema)
            table_count = len(result.get('tables', []))
            st.metric("Tables", table_count)
        except Exception as e:
            st.metric("Tables", "N/A")
            st.caption(f"Error: {str(e)[:50]}")
    
    with col2:
        # Count PII columns
        try:
            result = agents.classify_schema(st.session_state.schema)
            pii_count = result.get('pii_columns', 0)
            st.metric("PII Columns", pii_count)
        except Exception as e:
            st.metric("PII Columns", "N/A")
            st.caption(f"Error: {str(e)[:50]}")
    
    with col3:
        # Count pending requests
        try:
            rows = query("""
                SELECT COUNT(*) FROM REQUESTS 
                WHERE STATUS = 'PENDING_APPROVAL'
            """)
            pending = rows[0][0] if rows else 0
            st.metric("Pending Requests", pending)
        except Exception as e:
            st.metric("Pending Requests", "N/A")
            st.caption(f"Error: {str(e)[:50]}")
    
    with col4:
        # Audit records
        try:
            records = audit.get_all_records()
            st.metric("Audit Records", len(records))
        except Exception as e:
            st.metric("Audit Records", "N/A")
            st.caption(f"Error: {str(e)[:50]}")
    
    st.markdown("---")
    
    # Recent activity
    st.subheader("Recent Activity")
    
    try:
        records = audit.get_all_records()[-10:]
        
        if records:
            for record in reversed(records):
                st.write(f"**{record.action}** by {record.actor} - {record.created_at}")
                if record.detail:
                    with st.expander("Details"):
                        st.json(record.detail)
        else:
            st.info("No recent activity")
    except Exception as e:
        st.error(f"Error loading activity: {e}")


# Discovery Page
elif page == "🔍 Discovery":
    st.header("Schema Discovery")
    
    if st.button("🔄 Scan Schema"):
        with st.spinner("Scanning database schema..."):
            try:
                result = agents.discover_schema(st.session_state.schema)
                
                st.success(f"Found {len(result['tables'])} tables")
                
                # Tables
                st.subheader("Tables")
                for table in result['tables']:
                    with st.expander(f"📄 {table}"):
                        cols = result['columns_by_table'].get(table, [])
                        st.write(f"**Columns:** {len(cols)}")
                        
                        # Show columns
                        for col in cols:
                            nullable = "NULL" if col['nullable'] else "NOT NULL"
                            st.text(f"  • {col['name']} ({col['type']}) {nullable}")
                
                # Foreign Keys
                st.subheader("Foreign Key Relationships")
                for fk in result['foreign_keys']:
                    st.write(f"**{fk['child']}** → {fk['parent']}")
                    st.caption(f"FK: {fk['fk_columns']} → PK: {fk['pk_columns']}")
                
            except Exception as e:
                st.error(f"Error: {e}")


# Classification Page
elif page == "🏷️ Classification":
    st.header("PII Classification")
    
    if st.button("🔍 Run Classification"):
        with st.spinner("Classifying columns..."):
            try:
                result = agents.classify_schema(st.session_state.schema)
                
                st.success(f"Classified {result['total_columns']} columns")
                
                # Summary metrics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Columns", result['total_columns'])
                with col2:
                    st.metric("PII Columns", result['pii_columns'])
                with col3:
                    st.metric("Need Review", result['needs_review'])
                
                # By label
                st.subheader("Classification Results")
                
                for label, columns in result['by_label'].items():
                    if label == "NOT_PII":
                        continue
                    
                    with st.expander(f"🏷️ {label} ({len(columns)} columns)"):
                        for col in columns:
                            confidence_pct = f"{col['confidence'] * 100:.1f}%"
                            review_flag = "⚠️ REVIEW" if col['needs_review'] else ""
                            
                            st.write(f"**{col['table']}.{col['column']}**")
                            st.caption(f"Confidence: {confidence_pct} | Method: {col['method']} {review_flag}")
                
            except Exception as e:
                st.error(f"Error: {e}")


# Consent Management Page
elif page == "✅ Consent Management":
    st.header("Consent Management")
    
    tab1, tab2, tab3 = st.tabs(["Grant Consent", "Withdraw Consent", "View Consents"])
    
    with tab1:
        st.subheader("Grant Consent")
        
        with st.form("grant_form"):
            patient_id = st.number_input("Patient ID", min_value=1, step=1)
            purpose = st.selectbox("Purpose", ["MARKETING", "RESEARCH", "TREATMENT", "ANALYTICS"])
            start_date = st.date_input("Start Date", date.today())
            end_date = st.date_input("End Date", date(2027, 12, 31))
            
            if st.form_submit_button("Grant Consent"):
                try:
                    consent.grant(
                        patient_id,
                        purpose,
                        start_date.isoformat(),
                        end_date.isoformat()
                    )
                    st.success(f"✓ Consent granted for patient {patient_id}")
                except Exception as e:
                    st.error(f"Error: {e}")
    
    with tab2:
        st.subheader("Withdraw Consent")
        
        with st.form("withdraw_form"):
            patient_id = st.number_input("Patient ID", min_value=1, step=1, key="withdraw_pid")
            purpose = st.selectbox("Purpose", ["MARKETING", "RESEARCH", "TREATMENT", "ANALYTICS"], key="withdraw_purpose")
            effective_date = st.date_input("Effective Date", date.today())
            
            if st.form_submit_button("Withdraw Consent"):
                try:
                    consent.withdraw(
                        patient_id,
                        purpose,
                        effective_date.isoformat()
                    )
                    st.success(f"✓ Consent withdrawn for patient {patient_id}")
                except Exception as e:
                    st.error(f"Error: {e}")
    
    with tab3:
        st.subheader("View Consents")
        
        patient_id = st.number_input("Patient ID", min_value=1, step=1, key="view_pid")
        
        if st.button("Load Consents"):
            try:
                consents = consent.current_consents(patient_id)
                
                if consents:
                    for c in consents:
                        granted_icon = "✅" if c['granted'] else "❌"
                        st.write(f"{granted_icon} **{c['purpose']}**")
                        st.caption(f"Valid: {c['bus_start']} to {c['bus_end']}")
                else:
                    st.info(f"No consents found for patient {patient_id}")
            except Exception as e:
                st.error(f"Error: {e}")


# Rights Requests Page
elif page == "🗑️ Rights Requests":
    st.header("Rights Requests (Erasure)")
    
    tab1, tab2 = st.tabs(["Create Request", "Approve Requests"])
    
    with tab1:
        st.subheader("Create Erasure Request")
        
        subject_id = st.number_input("Subject ID (Patient ID)", min_value=1, step=1)
        
        if st.button("📋 Generate Plan"):
            with st.spinner("Generating erasure plan..."):
                try:
                    result = agents.plan_erasure(subject_id)
                    
                    if 'error' in result:
                        st.error(result['error'])
                    else:
                        # Show simulation
                        sim = result['simulation']
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Total Steps", sim['total_steps'])
                        with col2:
                            st.metric("Total Rows", sim['total_rows'])
                        with col3:
                            if sim['has_unverified']:
                                st.warning(f"⚠️ {sim['unverified_rules']} unverified rules")
                            else:
                                st.success("✓ All rules verified")
                        
                        # Show plan
                        st.subheader("Execution Plan")
                        
                        for i, step in enumerate(result['steps'], 1):
                            verified_icon = "✓" if step['rule_verified'] else "⚠️"
                            
                            with st.expander(f"{i}. {step['action']} {step['table']} ({step['est_rows']} rows)"):
                                st.write(f"**Action:** {step['action']}")
                                st.write(f"**Reason:** {step['reason']}")
                                st.write(f"**Estimated Rows:** {step['est_rows']}")
                                st.write(f"**Rule Verified:** {verified_icon}")
                                
                                if step['has_sql']:
                                    st.caption("SQL will be generated and validated")
                        
                        # Show plan hash
                        st.info(f"**Plan Hash:** `{result['plan_hash']}`")
                        
                        st.warning("⚠️ This is a DRY RUN - no data has been modified")
                        
                except Exception as e:
                    st.error(f"Error: {e}")
    
    with tab2:
        st.subheader("Approve Requests")
        
        # List pending requests
        try:
            rows = query("""
                SELECT ID, SUBJECT_ID, RECEIVED_AT, DUE_AT
                FROM REQUESTS
                WHERE STATUS = 'PENDING_APPROVAL'
                ORDER BY RECEIVED_AT DESC
            """)
            
            if rows:
                for row in rows:
                    request_id, subject_id, received, due = row
                    
                    with st.expander(f"Request #{request_id} - Subject {subject_id}"):
                        st.write(f"**Received:** {received}")
                        st.write(f"**Due:** {due}")
                        
                        # Get plan details
                        plan_rows = query("""
                            SELECT PLAN_JSON, PLAN_HASH
                            FROM REQUESTS
                            WHERE ID = ?
                        """, (request_id,))
                        
                        if plan_rows:
                            plan_json, plan_hash = plan_rows[0]
                            
                            if plan_json:
                                plan_data = json.loads(plan_json)
                                
                                # Show summary
                                sim = plan_data['simulation']
                                st.write(f"**Steps:** {sim['total_steps']}")
                                st.write(f"**Total Rows:** {sim['total_rows']}")
                                
                                # Approval
                                if st.button(f"✅ Approve Request #{request_id}", key=f"approve_{request_id}"):
                                    st.warning("⚠️ Approval requires DPO role. Use API for actual execution.")
                                    st.code(f"""
# Via API:
curl -X POST \\
  -H "Authorization: Bearer dpo_token" \\
  -H "Content-Type: application/json" \\
  -d '{{"approval_id": "APR-{request_id}"}}' \\
  http://localhost:8000/requests/{request_id}/approve
                                    """)
            else:
                st.info("No pending requests")
        except Exception as e:
            st.error(f"Error: {e}")


# Audit Log Page
elif page == "📝 Audit Log":
    st.header("Audit Log")
    
    # Verify chain
    col1, col2 = st.columns([1, 3])
    
    with col1:
        if st.button("🔍 Verify Chain"):
            try:
                is_valid, error = audit.verify_chain()
                
                if is_valid:
                    st.success("✓ Chain is INTACT")
                else:
                    st.error(f"✗ Chain is BROKEN\n\n{error}")
            except Exception as e:
                st.error(f"Error: {e}")
    
    with col2:
        st.info("The audit chain uses SHA256 hashing. Any tampering will be detected.")
    
    st.markdown("---")
    
    # Recent records
    st.subheader("Recent Audit Records")
    
    limit = st.slider("Number of records", 10, 100, 50)
    
    try:
        records = audit.get_all_records()[-limit:]
        
        if records:
            for record in reversed(records):
                with st.expander(f"#{record.id}: {record.action} by {record.actor}"):
                    st.write(f"**Actor:** {record.actor}")
                    st.write(f"**Action:** {record.action}")
                    st.write(f"**Subject:** {record.subject}")
                    st.write(f"**Created:** {record.created_at}")
                    st.write(f"**Hash:** `{record.hash[:32]}...`")
                    
                    if record.detail:
                        st.json(record.detail)
        else:
            st.info("No audit records found")
    except Exception as e:
        st.error(f"Error: {e}")

# Footer
st.markdown("---")
st.caption("Db2 Privacy Copilot | Decision Support Tool (Not Legal Advice)")


# Help & Guide Page (NEW)
if page == "❓ Help & Guide":
    st.header("Help & Guide")
    
    st.markdown("""
    ### Welcome to Db2 Privacy Copilot! 🚀
    
    This AI-powered system helps you comply with data privacy regulations by:
    - **Discovering** personal data across your database
    - **Classifying** columns with AI-powered pattern matching
    - **Managing** user consents with temporal tracking
    - **Processing** rights requests (erasure, access) safely
    - **Auditing** all actions with cryptographic verification
    """)
    
    st.markdown("---")
    
    # Quick Start Guide
    st.subheader("🎯 Quick Start Guide")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Step 1: Discovery**
        1. Go to 🔍 Discovery
        2. Click "Scan Schema"
        3. Review tables and relationships
        
        **Step 2: Classification**
        1. Go to 🏷️ Classification
        2. Click "Run Classification"
        3. Review PII columns found
        4. Verify flagged items
        """)
    
    with col2:
        st.markdown("""
        **Step 3: Consent Management**
        1. Go to ✅ Consent Management
        2. Grant or withdraw consents
        3. View consent history
        
        **Step 4: Rights Requests**
        1. Go to 🗑️ Rights Requests
        2. Generate erasure plan
        3. Review and approve
        4. Execute safely
        """)
    
    st.markdown("---")
    
    # Common Workflows
    st.subheader("📋 Common Workflows")
    
    workflows = {
        "🔍 Handle Erasure Request": [
            "Navigate to Rights Requests",
            "Enter the subject ID (e.g., patient ID)",
            "Click 'Generate Plan' to see what will be deleted/anonymized",
            "Review the plan carefully - check retention rules",
            "Submit for DPO approval",
            "Once approved, plan executes in single transaction",
            "Check Audit Log to verify completion"
        ],
        "📊 Verify Data Compliance": [
            "Run Discovery to map all tables",
            "Run Classification to identify PII",
            "Review columns marked 'Need Review'",
            "Manually verify classification accuracy",
            "Update retention rules as needed",
            "Check consent coverage for processing activities"
        ],
        "🔐 Audit Trail Verification": [
            "Go to Audit Log page",
            "Click 'Verify Chain' button",
            "System uses SHA256 hashing to detect tampering",
            "Any modification breaks the chain",
            "Green = Intact, Red = Tampered"
        ]
    }
    
    for workflow, steps in workflows.items():
        with st.expander(workflow):
            for i, step in enumerate(steps, 1):
                st.markdown(f"{i}. {step}")
    
    st.markdown("---")
    
    # FAQs
    st.subheader("❓ Frequently Asked Questions")
    
    faqs = {
        "What is PII classification confidence?": """
        Confidence represents how certain the AI is about a column containing PII:
        - **High (>0.7)**: Strong evidence (e.g., column named EMAIL with email patterns)
        - **Medium (0.5-0.7)**: Moderate evidence (e.g., name similarity)
        - **Low (<0.5)**: Weak evidence - marked for manual review
        
        Always review low-confidence classifications manually!
        """,
        
        "How does the guardrail work?": """
        The guardrail is a deterministic code validator (NOT an LLM) that:
        - Checks for banned SQL tokens (DROP, TRUNCATE, etc.)
        - Enforces WHERE clauses on all DELETE/UPDATE
        - Validates parameterized queries (no SQL injection)
        - Requires human approval before execution
        - Binds approval to plan hash (prevents tampering)
        
        Over 60 security tests ensure it blocks malicious SQL.
        """,
        
        "What is bitemporal consent tracking?": """
        Bitemporal tracking maintains TWO time dimensions:
        - **Business Time**: When was consent valid in the real world?
        - **System Time**: When did we know about it?
        
        This lets you answer questions like:
        - "Did patient 123 have MARKETING consent on Jan 1st?" (business time)
        - "What did we believe on Feb 1st?" (system time)
        - "When was consent withdrawn, and when did we record it?"
        
        Critical for regulatory compliance and dispute resolution!
        """,
        
        "Why can't agents execute erasure?": """
        **Safety by design**: Agents can only PROPOSE actions, never execute.
        
        Workflow:
        1. Agent analyzes schema and generates plan
        2. Plan presented to human DPO for review
        3. DPO approves with digital signature
        4. Deterministic code (guardrail) validates plan
        5. Execution in single transaction with rollback
        6. Audit trail records everything
        
        This prevents AI from accidentally (or maliciously) deleting data.
        """,
        
        "How do I update retention rules?": """
        Retention rules are in the RETENTION_RULES table:
        
        ```sql
        UPDATE RETENTION_RULES
        SET ACTION = 'ANONYMISE', REASON = 'Legal hold'
        WHERE TABNAME = 'PRESCRIPTIONS';
        ```
        
        Actions: ERASE, ANONYMISE, RETAIN
        - ERASE: Delete rows
        - ANONYMISE: NULL out PII columns
        - RETAIN: Keep (e.g., for legal compliance)
        
        Mark rules as VERIFIED after legal review!
        """
    }
    
    for question, answer in faqs.items():
        with st.expander(question):
            st.markdown(answer)
    
    st.markdown("---")
    
    # Architecture Overview
    st.subheader("🏗️ System Architecture")
    
    st.markdown("""
    ```
    ┌─────────────────────────────────────────────────────────┐
    │                    User Interface (UI)                   │
    │              Streamlit / React Dashboard                 │
    └─────────────┬───────────────────────────────────────────┘
                  │
    ┌─────────────▼───────────────────────────────────────────┐
    │                    FastAPI Backend                       │
    │       Authentication │ Authorization │ Validation        │
    └─────────────┬───────────────────────────────────────────┘
                  │
    ┌─────────────▼───────────────────────────────────────────┐
    │                   AI Agent Layer (CrewAI)                │
    │   Discovery Agent │ Classification Agent │ Rights Agent  │
    │           [PROPOSE ONLY - NEVER EXECUTE]                 │
    └─────────────┬───────────────────────────────────────────┘
                  │
    ┌─────────────▼───────────────────────────────────────────┐
    │               Core Processing Modules                    │
    │   discovery.py │ classify.py │ consent.py │ erasure.py  │
    └─────────────┬───────────────────────────────────────────┘
                  │
    ┌─────────────▼───────────────────────────────────────────┐
    │              Security Guardrail (guardrail.py)           │
    │     SQL Validation │ Injection Prevention │ Approval     │
    └─────────────┬───────────────────────────────────────────┘
                  │
    ┌─────────────▼───────────────────────────────────────────┐
    │              Audit Chain (audit.py)                      │
    │       SHA256 Hashing │ Tamper Detection │ Trail          │
    └─────────────┬───────────────────────────────────────────┘
                  │
    ┌─────────────▼───────────────────────────────────────────┐
    │                    IBM Db2 Database                      │
    │   Business Tables │ Application Tables │ Temporal Data   │
    └─────────────────────────────────────────────────────────┘
    ```
    """)
    
    st.markdown("---")
    
    # Resources
    st.subheader("📚 Additional Resources")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **Documentation**
        - [Quick Start Guide](../QUICKSTART.md)
        - [Architecture](../docs/architecture.md)
        - [Demo Script](../docs/demo_script.md)
        """)
    
    with col2:
        st.markdown("""
        **API Reference**
        - [API Documentation](http://localhost:8000/docs)
        - [OpenAPI Spec](http://localhost:8000/openapi.json)
        - [Health Check](http://localhost:8000/health)
        """)
    
    with col3:
        st.markdown("""
        **Support**
        - [GitHub Issues](#)
        - [DPDP Act 2023](https://www.meity.gov.in/)
        - [IBM Db2 Docs](https://www.ibm.com/docs/en/db2)
        """)


# Original footer (moved up)
