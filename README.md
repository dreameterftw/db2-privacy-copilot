# 🔒 Db2 Privacy Copilot

> An agentic DPDP/GDPR compliance system for IBM Db2 — discover, classify, and act on personal data with AI-powered planning and deterministic safety guardrails.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![IBM Db2](https://img.shields.io/badge/IBM-Db2-blue.svg)](https://www.ibm.com/db2)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## What It Does

Db2 Privacy Copilot automates the most tedious parts of data privacy compliance:

| Capability | Description |
|---|---|
| **🔍 Discovery** | Auto-maps schema, FK relationships, and safe deletion order |
| **🏷️ Classification** | Detects PII (email, phone, PAN, Aadhaar, health data) using AI + regex |
| **✅ Consent Ledger** | Bitemporal tracking — "what was valid when, as we knew it" |
| **🗑️ Rights Requests** | AI-planned, human-approved, guardrail-validated erasure/anonymisation |
| **📝 Audit Trail** | SHA256 hash-chained log — any tampering is detected |
| **🛡️ Guardrail** | Deterministic SQL validator — blocks injection, DDL, missing WHERE clauses |

---

## Architecture

```
┌───────────────────────────────────────────────────────────┐
│               Streamlit UI  /  FastAPI REST                │
└────────────────────────┬──────────────────────────────────┘
                         │
┌────────────────────────▼──────────────────────────────────┐
│            CrewAI Agents (PROPOSE ONLY — never execute)    │
│   DiscoveryAgent  │  ClassificationAgent  │  RightsAgent   │
└────────────────────────┬──────────────────────────────────┘
                         │
┌────────────────────────▼──────────────────────────────────┐
│              Core Modules (Python)                         │
│  discovery  │  classify  │  consent  │  erasure  │  audit  │
└────────────────────────┬──────────────────────────────────┘
                         │
┌────────────────────────▼──────────────────────────────────┐
│           Security Guardrail (deterministic code)          │
│      SQL shape check │ banned tokens │ approval gate       │
└────────────────────────┬──────────────────────────────────┘
                         │
┌────────────────────────▼──────────────────────────────────┐
│                    IBM Db2 (Docker)                        │
│   Clinic schema │ PII_MAP │ CONSENT │ REQUESTS │ AUDIT_LOG │
└───────────────────────────────────────────────────────────┘
```

**Key safety principle**: Agents can only **propose** — execution requires human approval, then passes through the deterministic guardrail.

The Db2 connection is implemented with `ibm_db`/`ibm_db_dbi` in `app/db.py`.
Schema discovery and classification query the live Db2 catalog and sample
columns, while consent, erasure plans, and the audit chain persist to Db2 tables.
CrewAI is a required project dependency and is wired to read-only/planning tools
in `app/agents.py`; the agents do not execute destructive SQL.

---

## Quick Start

```bash
# 1. Clone
git clone https://github.com/dreameterftw/db2-privacy-copilot.git
cd db2-privacy-copilot

# 2. Setup (creates .venv and .env)
bash setup.sh          # Linux/Mac
setup.bat              # Windows

# 3. Edit .env — set a strong DB2 password
nano .env

# 4. Start Db2 in Docker (takes ~10 min on first run)
docker compose up -d
docker compose logs -f db2   # wait for "Setup has completed"

# 5. Bootstrap database & seed test data
source .venv/bin/activate
python app/bootstrap.py
python eval/seed.py

# 6. Run tests
pytest -v

# 7. Launch UI
streamlit run ui/app.py

# 8. Or launch API
uvicorn app.api:app --reload
# → http://localhost:8000/docs
```

See [QUICKSTART.md](QUICKSTART.md) for a detailed 30-minute walkthrough.
For the public HTTPS demo, protected CI/CD deployment, and rollback steps, see
[the deployment guide](deploy/README.md).

---

## Project Structure

```
db2-privacy-copilot/
├── app/
│   ├── agents.py       # CrewAI agent definitions + tool wrappers
│   ├── api.py          # FastAPI REST backend
│   ├── audit.py        # SHA256 hash-chained audit log
│   ├── bootstrap.py    # Database initialization
│   ├── classify.py     # PII classification engine
│   ├── config.py       # Settings (pydantic-settings)
│   ├── consent.py      # Bitemporal consent ledger
│   ├── db.py           # Db2 connection & query utilities
│   ├── discovery.py    # Schema catalog scanner + FK graph
│   ├── erasure.py      # Dry-run planner + executor
│   └── guardrail.py    # Deterministic SQL validator
├── ui/
│   └── app.py            # Multi-page Streamlit dashboard
├── eval/
│   ├── seed.py         # Synthetic clinic data generator
│   └── run_eval.py     # Classification evaluation harness
├── sql/
│   ├── 00_schema_clinic.sql    # 7-table clinic schema
│   ├── 01_app_tables.sql       # PII_MAP, REQUESTS, AUDIT_LOG …
│   ├── 02_consent_temporal.sql # Bitemporal CONSENT table
│   └── 03_rcac_examples.sql    # Row & Column Access Control
├── tests/              # 150+ pytest tests
├── docs/
│   ├── architecture.md
│   └── demo_script.md
├── docker-compose.yml
├── pyproject.toml
└── QUICKSTART.md
```

---

## Implementation Status

| Phase | Description | Status |
|---|---|---|
| 0 | Environment, Docker, synthetic data | ✅ Complete |
| 1 | Schema discovery (FK graph, delete order) | ✅ Complete |
| 2 | PII classification (regex + name heuristics) | ✅ Complete |
| 3 | Bitemporal consent ledger | ✅ Complete |
| 4 | Rights requests, guardrail, audit chain | ✅ Complete |
| 5 | CrewAI agents, FastAPI, Streamlit UI | ✅ Complete |
| 6 | Evaluation, hardening, polish | 📋 In progress |
| 7 | RAG over DPDP Act, RCAC proposals | 📋 Stretch goal |

---

## Security Design

### What the guardrail blocks
- `DROP`, `TRUNCATE`, `ALTER`, `GRANT`, `REVOKE`, `CREATE`
- Stacked statements (`;` separator)
- SQL comments (`--`, `/* */`)
- Missing `WHERE` clause
- Non-parameterized values (no `?` placeholder)
- Tables not in the approved plan
- Always-true conditions (`1=1`, `'a'='a'`)

### Approval workflow
```
Agent generates plan → DPO reviews → DPO approves (signs with ID)
  → Guardrail validates each statement
    → Executor runs single transaction
      → Rollback on any error
        → Audit record appended to chain
```

### Audit chain
Every record contains `hash(prev_hash + content)`. Changing any record invalidates all subsequent hashes — tamper-evident by design.

---

## API Overview

```bash
# Auth header: Authorization: Bearer <token>
# Test tokens: viewer_token | analyst_token | dpo_token

GET  /health                      # Component health check
GET  /discovery/{schema}          # Scan schema (VIEWER+)
GET  /classification/{schema}     # Run PII classification (ANALYST+)
POST /consent/grant               # Grant consent (ANALYST+)
POST /consent/withdraw            # Withdraw consent (ANALYST+)
GET  /consent/{patient_id}        # View consents (VIEWER+)
POST /requests                    # Create erasure request (ANALYST+)
GET  /requests                    # List requests (VIEWER+)
GET  /requests/{id}               # Get request detail (VIEWER+)
POST /requests/{id}/approve       # Approve & execute (DPO only)
GET  /audit                       # Audit log (VIEWER+)
GET  /audit/verify                # Verify chain (DPO only)
GET  /audit/subject/{id}          # Subject audit trail (VIEWER+)
```

Interactive docs: `http://localhost:8000/docs`

---

## Running Tests

```bash
# All tests
pytest -v

# Specific modules
pytest tests/test_guardrail.py -v    # 58 security tests
pytest tests/test_audit.py -v        # 30 chain tests
pytest tests/test_erasure.py -v      # 35 planner tests
pytest tests/test_classify.py -v     # 25 PII detection tests
pytest tests/test_consent.py -v      # 20 temporal tests

# With coverage
pytest --cov=app --cov-report=html
```

---

## Configuration

All settings live in `.env` (see [.env.example](.env.example)):

```env
DB2_HOST=localhost
DB2_PORT=50000
DB2_DB=clinic
DB2_USER=db2inst1
DB2_PASSWORD=replace-with-a-strong-password
DB2_SCHEMA=DB2INST1

API_SECRET_KEY=change-this-in-production
PII_VALUE_THRESHOLD=0.30
PII_NAME_THRESHOLD=0.35
DEFAULT_REQUEST_DEADLINE_DAYS=30
```

---

## Development

```bash
# Install with dev extras
pip install -e ".[dev,ui]"

# Lint
ruff check app/ tests/

# Type check
mypy app/

# Security scan
bandit -r app/

# Pre-commit hooks
pre-commit install
```

---

## Contributing

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Run tests (`pytest -v`)
4. Run lint (`ruff check .`)
5. Submit a pull request

---

## License

MIT — see [LICENSE](LICENSE) for details.

---

## Acknowledgements

- [IBM Db2](https://www.ibm.com/db2) — database engine with temporal table support
- [CrewAI](https://crewai.com) — multi-agent orchestration
- [LangChain](https://python.langchain.com) — LLM tooling
- [FastAPI](https://fastapi.tiangolo.com) — REST API framework
- [Streamlit](https://streamlit.io) — rapid UI development
- [NetworkX](https://networkx.org) — FK graph analysis
- India's [DPDP Act 2023](https://www.meity.gov.in/data-protection-framework) — compliance target
