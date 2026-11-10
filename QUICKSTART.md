# Quick Start Guide

Get the Db2 Privacy Copilot running in 30 minutes.

## Prerequisites

- **Docker** (for Db2 Community Edition)
- **Python 3.11+**
- At least 4GB RAM available for the Db2 container
- Internet connection (for initial Docker image pull)

## Step 1: Clone and Setup (5 min)

```bash
# Clone the repository
git clone <your-repo-url>
cd db2-privacy-copilot

# Run setup script
# On Linux/Mac:
bash setup.sh

# On Windows:
setup.bat
```

## Step 2: Configure Environment (1 min)

Edit `.env` and set a strong password:

```bash
# .env
DB2_PASSWORD=replace-with-a-strong-password
```

## Step 3: Start Db2 (10 min)

```bash
# Start the container
docker compose up -d

# Watch the logs (this will take 5-10 minutes)
docker compose logs -f db2

# Wait for this message:
# "(*) Setup has completed."
```

**Tip:** On first run, Db2 needs to initialize the database. This is normal and only happens once.

## Step 4: Initialize Database (2 min)

```bash
# Activate virtual environment
# On Linux/Mac:
source .venv/bin/activate

# On Windows:
.venv\Scripts\activate.bat

# Run bootstrap script
python app/bootstrap.py
```

Expected output:
```
============================================================
Db2 Privacy Copilot - Database Bootstrap
============================================================

1. Checking Db2 version...
   ✓ Db2 version: SQL12012

2. Executing sql/00_schema_clinic.sql...
   ✓ Completed

3. Executing sql/01_app_tables.sql...
   ✓ Completed

4. Executing sql/02_consent_temporal.sql...
   ✓ Completed
...
```

## Step 5: Seed Test Data (2 min)

```bash
python eval/seed.py
```

This creates:
- 100 synthetic patients with realistic PII
- Appointments, prescriptions, lab reports, etc.
- Ground-truth labels for evaluation
- Challenging edge cases (hidden PANs, decoy columns, etc.)

## Step 6: Run Tests (2 min)

```bash
pytest -v
```

All tests should pass. If any fail, check:
1. Db2 is running: `docker compose ps`
2. Connection settings in `.env` are correct
3. Bootstrap completed successfully

## Step 7: Explore (5-10 min)

### Option A: Use Python directly

```python
# Discovery
from app import discovery
discovery.columns("DB2INST1")
discovery.fk_edges("DB2INST1")
discovery.delete_order("DB2INST1", "PATIENT")

# Classification (Phase 2 - coming next)
# from app import classify
# classify.run("DB2INST1")

# Consent (Phase 3 - coming next)
# from app.consent import grant, withdraw, valid_on
# grant(patient_id=1, purpose="MARKETING", start="2026-01-01")
```

### Option B: Use SQL directly

```bash
# Connect to Db2
docker exec -it db2-privacy-copilot-db2-1 bash
su - db2inst1
db2 connect to clinic

# Explore the schema
db2 "SELECT TABNAME FROM SYSCAT.TABLES WHERE TABSCHEMA='DB2INST1'"

# Look at sample data
db2 "SELECT ID, FULL_NM, CUST_MAIL_ID FROM PATIENT FETCH FIRST 5 ROWS ONLY"

# Check PII map (after classification)
db2 "SELECT * FROM PII_MAP"

# Check retention rules
db2 "SELECT * FROM RETENTION_RULES"
```

### Option C: Run the API (when available)

```bash
uvicorn app.api:app --reload

# Visit http://localhost:8000/docs for interactive API docs
```

## What's Included

After setup, you have:

✓ Db2 12.x running in Docker with vector support  
✓ Synthetic clinic database with 100+ patients  
✓ Application tables (PII_MAP, REQUESTS, AUDIT_LOG, CONSENT, etc.)  
✓ Ground-truth labels for evaluation (`eval/labels.csv`)  
✓ Working tests demonstrating database connectivity  

## Next Steps

Follow the **Development Plan** in README.md to build out each phase:

- **Phase 1:** Discovery (map schema and foreign keys)
- **Phase 2:** Classification (detect PII)
- **Phase 3:** Consent ledger (bitemporal tracking)
- **Phase 4:** Rights requests (erasure with approval)
- **Phase 5:** Agent layer and API
- **Phase 6:** Evaluation and polish

## Troubleshooting

### Db2 container won't start
```bash
# Check logs
docker compose logs db2

# Common issues:
# - Not enough memory (needs 4GB+)
# - Port 50000 already in use
# - Previous db2data folder has wrong permissions
```

### "Connection refused" errors
```bash
# Make sure Db2 is fully initialized
docker compose logs db2 | grep "Setup has completed"

# If not done, wait longer (can take 10 minutes on first run)
```

### Python import errors
```bash
# Make sure virtual environment is activated
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate.bat  # Windows

# Reinstall dependencies
pip install -e ".[dev]"
```

### Database connection fails
```bash
# Check .env file
cat .env

# Test connection
python -c "from app.db import conn; c = conn(); print('✓ Connected'); c.close()"
```

### "Table already exists" errors
This is normal if you run bootstrap multiple times. The script will continue.

## Getting Help

- Check the detailed README.md for architecture and design
- Review docs/demo_script.md for usage examples
- Check the Phase descriptions for implementation guidance
- File an issue with error logs and steps to reproduce

## Clean Slate Reset

If you want to start fresh:

```bash
# Stop and remove containers
docker compose down

# Remove Db2 data
rm -rf db2data/  # Linux/Mac
rmdir /s db2data  # Windows

# Recreate .env
rm .env
cp .env.example .env
# Edit .env with your password

# Start over from Step 3
docker compose up -d
```

---

**Ready?** Head to the main README.md and start implementing Phase 1!
