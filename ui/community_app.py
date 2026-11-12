"""Standalone sample-data presentation for Streamlit Community Cloud."""

from collections.abc import Mapping, Sequence

import streamlit as st

st.set_page_config(
    page_title="Db2 Privacy Copilot | Sample presentation",
    page_icon="🔒",
    layout="wide",
)

TABLES = [
    {"Table": "PATIENT", "Columns": 6, "Rows": 3, "Purpose": "Synthetic patient profile"},
    {"Table": "APPOINTMENT", "Columns": 4, "Rows": 3, "Purpose": "Appointment records"},
    {"Table": "PRESCRIPTION", "Columns": 4, "Rows": 2, "Purpose": "Prescription records"},
    {"Table": "LAB_REPORT", "Columns": 4, "Rows": 2, "Purpose": "Lab result records"},
]

CLASSIFICATIONS = [
    {
        "Table.Column": "PATIENT.FULL_NM",
        "Candidate label": "PERSON_NAME",
        "Confidence": "98%",
        "Review": "Review",
    },
    {
        "Table.Column": "PATIENT.CUST_MAIL_ID",
        "Candidate label": "EMAIL",
        "Confidence": "99%",
        "Review": "Review",
    },
    {
        "Table.Column": "PATIENT.PHONE_NO",
        "Candidate label": "PHONE",
        "Confidence": "96%",
        "Review": "Review",
    },
    {
        "Table.Column": "PATIENT.DOB",
        "Candidate label": "DATE_OF_BIRTH",
        "Confidence": "93%",
        "Review": "Review",
    },
    {
        "Table.Column": "PATIENT.GOVT_ID",
        "Candidate label": "GOVERNMENT_ID",
        "Confidence": "91%",
        "Review": "Review",
    },
    {
        "Table.Column": "PRESCRIPTION.DRUG_NM",
        "Candidate label": "HEALTH_DATA",
        "Confidence": "88%",
        "Review": "Review",
    },
]

CONSENTS = [
    {
        "Patient": "Demo Patient 001",
        "Purpose": "TREATMENT",
        "Status": "Granted",
        "Valid through": "2027-12-31",
    },
    {
        "Patient": "Demo Patient 002",
        "Purpose": "RESEARCH",
        "Status": "Granted",
        "Valid through": "2026-12-31",
    },
]

AUDIT_EVENTS = [
    {"Time": "2026-03-05 10:15", "Actor": "Analyst", "Event": "Schema discovery viewed"},
    {"Time": "2026-03-05 10:21", "Actor": "Analyst", "Event": "Classification results reviewed"},
    {"Time": "2026-03-05 10:34", "Actor": "DPO", "Event": "Sample rights plan inspected"},
]


def render_table(rows: Sequence[Mapping[str, object]]) -> None:
    """Render fixed sample rows without loading optional dataframe libraries."""
    if not rows:
        return

    headers = list(rows[0])
    markdown = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    markdown.extend(
        "| " + " | ".join(str(row.get(header, "")) for header in headers) + " |" for row in rows
    )
    st.markdown("\n".join(markdown))


st.title("🔒 Db2 Privacy Copilot")
st.caption("Privacy operations workspace · presentation build")
st.warning(
    "**Sample-data presentation only.** This app displays synthetic fixtures in "
    "memory. It does not connect to FastAPI or Db2, and it does not save or execute "
    "requests. Do not enter real personal data."
)

section = st.sidebar.radio(
    "Presentation",
    ["Overview", "Discovery", "Classification", "Consents", "Rights requests", "Audit trail"],
)
st.sidebar.info("All records are fictional, read-only examples. No backend is running.")

if section == "Overview":
    st.subheader("Privacy workflow at a glance")
    metrics = st.columns(4)
    metrics[0].metric("Sample tables", len(TABLES))
    metrics[1].metric("Synthetic records", 10)
    metrics[2].metric("PII candidates", len(CLASSIFICATIONS))
    metrics[3].metric("Consent records", len(CONSENTS))
    st.markdown(
        "Explore a sample schema, review candidate classifications, and see how "
        "consent, rights-request, and audit workflows are represented."
    )
    st.info(
        "This hosted entry point is intentionally separate from the full local "
        "application, which requires the FastAPI service and a database."
    )

elif section == "Discovery":
    st.subheader("Schema discovery")
    st.write("Example tables and relationships from a fictional clinic dataset.")
    render_table(TABLES)
    st.markdown("**Sample relationships**")
    st.write("- `APPOINTMENT.PATIENT_ID` → `PATIENT.ID`")
    st.write("- `PRESCRIPTION.PATIENT_ID` → `PATIENT.ID`")
    st.write("- `LAB_REPORT.PATIENT_ID` → `PATIENT.ID`")

elif section == "Classification":
    st.subheader("Personal-data candidates")
    st.caption("Illustrative labels and confidence values; human review is required.")
    render_table(CLASSIFICATIONS)

elif section == "Consents":
    st.subheader("Consent ledger")
    st.caption("Fictional sample records; this presentation cannot grant or withdraw consent.")
    render_table(CONSENTS)

elif section == "Rights requests":
    st.subheader("Rights-request planning")
    render_table(
        [
            {
                "Request": "SAMPLE-001",
                "Subject": "Demo Patient 001",
                "Status": "Example plan · not submitted",
                "Review": "Human review required",
            }
        ]
    )
    st.info("Creating, approving, or executing a request is disabled in this presentation.")

else:
    st.subheader("Example audit activity")
    render_table(AUDIT_EVENTS)
    st.info(
        "These rows are display fixtures, not records from the audit service. "
        "This presentation does not verify a live audit chain."
    )

st.divider()
st.caption(
    "Demo boundary: bundled synthetic sample data only · in-memory/read-only · "
    "no FastAPI, Db2, authentication provider, or persistent storage."
)
