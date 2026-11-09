"""
Integration tests for end-to-end workflows.

These tests verify that all components work together correctly.
"""
import json

import pytest

from app import agents, audit, consent, erasure
from app.config import settings
from app.db import conn, query


@pytest.fixture
def integration_patient(db_conn):
    """Create a patient with full related data for integration testing."""
    cur = db_conn.cursor()
    
    # Insert patient
    cur.execute("""
        INSERT INTO PATIENT (FULL_NM, CUST_MAIL_ID, PH_NO, DOB_DT, GOVT_ID, ADDR1, CITY_NM, PINCODE)
        VALUES ('Integration Test', 'integration@test.com', 7777777777, '1980-01-01', 
                'INTTST1234I', 'Test St', 'Test City', '777777')
    """)
    db_conn.commit()
    
    cur.execute("SELECT ID FROM PATIENT WHERE CUST_MAIL_ID = 'integration@test.com'")
    patient_id = cur.fetchone()[0]
    
    # Insert appointment
    cur.execute("""
        INSERT INTO APPOINTMENT (PATIENT_ID, APPT_DT, APPT_TIME, DOCTOR_NM, REASON, STATUS)
        VALUES (?, '2026-12-01', '14:00:00', 'Dr. Integration', 'Test', 'SCHEDULED')
    """, (patient_id,))
    
    # Insert billing (should be RETAINED)
    cur.execute("""
        INSERT INTO BILLING (PATIENT_ID, BILL_DT, AMOUNT, INVOICE_NO, FISCAL_YEAR)
        VALUES (?, '2026-12-01', 1000.00, 'INT-TEST-001', '2026-27')
    """, (patient_id,))
    
    db_conn.commit()
    
    yield patient_id
    
    # Cleanup
    try:
        cur.execute("DELETE FROM BILLING WHERE PATIENT_ID = ?", (patient_id,))
        cur.execute("DELETE FROM APPOINTMENT WHERE PATIENT_ID = ?", (patient_id,))
        cur.execute("DELETE FROM PATIENT WHERE ID = ?", (patient_id,))
        db_conn.commit()
    except:
        pass


class TestDiscoveryToClassification:
    """Test discovery → classification workflow."""
    
    def test_discover_then_classify(self):
        """Test that discovery and classification work together."""
        schema = settings.db2_schema
        
        # Discovery
        discovery_result = agents.discover_schema(schema)
        assert 'tables' in discovery_result
        assert len(discovery_result['tables']) > 0
        
        # Classification uses discovery results implicitly
        classification_result = agents.classify_schema(schema)
        assert 'total_columns' in classification_result
        assert classification_result['total_columns'] > 0
        
        # Verify PII was found
        assert classification_result['pii_columns'] > 0


class TestConsentWorkflow:
    """Test consent grant → query → withdraw workflow."""
    
    def test_full_consent_lifecycle(self, integration_patient):
        """Test granting, querying, and withdrawing consent."""
        patient_id = integration_patient
        
        # Grant consent
        consent.grant(patient_id, "INTEGRATION_TEST", "2026-01-01", "2026-12-31")
        
        # Query - should be valid in June
        assert consent.valid_on(patient_id, "INTEGRATION_TEST", "2026-06-01")
        
        # Query - should be invalid before start
        assert not consent.valid_on(patient_id, "INTEGRATION_TEST", "2025-12-31")
        
        # Withdraw
        consent.withdraw(patient_id, "INTEGRATION_TEST", "2026-07-01")
        
        # Query - should still be valid before withdrawal
        assert consent.valid_on(patient_id, "INTEGRATION_TEST", "2026-06-15")
        
        # Query - should be invalid after withdrawal
        assert not consent.valid_on(patient_id, "INTEGRATION_TEST", "2026-07-15")
        
        # Check history exists
        history = consent.history(patient_id, "INTEGRATION_TEST")
        assert len(history) > 0


class TestErasureWorkflow:
    """Test complete erasure workflow: plan → approve → execute."""
    
    def test_plan_to_execution(self, integration_patient, db_conn):
        """Test full erasure workflow."""
        patient_id = integration_patient
        
        # Step 1: Plan
        plan_result = agents.plan_erasure(patient_id)
        assert 'plan_hash' in plan_result
        assert 'steps' in plan_result
        
        # Verify BILLING is in plan as RETAIN
        billing_step = next(
            (s for s in plan_result['steps'] if s['table'] == 'BILLING'),
            None
        )
        assert billing_step is not None
        assert billing_step['action'] == 'RETAIN'
        
        # Step 2: Get full plan for execution
        steps = erasure.plan(patient_id)
        plan_hash_value = erasure.plan_hash(steps)
        
        # Verify hash matches
        assert plan_hash_value == plan_result['plan_hash']
        
        # Step 3: Verify data exists before execution
        cur = db_conn.cursor()
        cur.execute("SELECT COUNT(*) FROM PATIENT WHERE ID = ?", (patient_id,))
        patient_count_before = cur.fetchone()[0]
        assert patient_count_before == 1
        
        cur.execute("SELECT COUNT(*) FROM APPOINTMENT WHERE PATIENT_ID = ?", (patient_id,))
        appt_count_before = cur.fetchone()[0]
        assert appt_count_before > 0
        
        cur.execute("SELECT COUNT(*) FROM BILLING WHERE PATIENT_ID = ?", (patient_id,))
        billing_count_before = cur.fetchone()[0]
        assert billing_count_before > 0
        
        # Step 4: Execute
        erasure.execute(
            steps,
            patient_id,
            "integration_test@example.com",
            "INT-TEST-001",
            plan_hash_value
        )
        
        # Step 5: Verify results
        # Patient should be deleted
        cur.execute("SELECT COUNT(*) FROM PATIENT WHERE ID = ?", (patient_id,))
        patient_count_after = cur.fetchone()[0]
        assert patient_count_after == 0
        
        # Appointment should be deleted
        cur.execute("SELECT COUNT(*) FROM APPOINTMENT WHERE PATIENT_ID = ?", (patient_id,))
        appt_count_after = cur.fetchone()[0]
        assert appt_count_after == 0
        
        # Billing should be RETAINED
        cur.execute("SELECT COUNT(*) FROM BILLING WHERE PATIENT_ID = ?", (patient_id,))
        billing_count_after = cur.fetchone()[0]
        assert billing_count_after == billing_count_before  # Still there!
        
        # Step 6: Verify audit trail
        audit_records = audit.get_records_by_subject(patient_id)
        erasure_records = [r for r in audit_records if r.action == "ERASURE"]
        assert len(erasure_records) > 0
        
        # Verify audit detail
        latest = erasure_records[-1]
        assert latest.actor == "integration_test@example.com"
        assert "approval_id" in latest.detail
        assert latest.detail["approval_id"] == "INT-TEST-001"


class TestAuditIntegrity:
    """Test audit chain integrity across operations."""
    
    def test_audit_chain_maintained(self, integration_patient):
        """Test that audit chain stays intact through operations."""
        patient_id = integration_patient
        
        # Verify chain before
        is_valid_before, _ = audit.verify_chain()
        assert is_valid_before
        
        # Perform operations
        audit.append("test1", "TEST_ACTION_1", patient_id, {"test": 1})
        audit.append("test2", "TEST_ACTION_2", patient_id, {"test": 2})
        audit.append("test3", "TEST_ACTION_3", patient_id, {"test": 3})
        
        # Verify chain after
        is_valid_after, error = audit.verify_chain()
        assert is_valid_after, f"Chain broken: {error}"


class TestAgentToAPI:
    """Test agent tools → API integration."""
    
    def test_agent_tools_match_api_format(self):
        """Test that agent tools return API-compatible formats."""
        schema = settings.db2_schema
        
        # Test discovery tool
        discovery_result = agents.discover_schema(schema)
        assert isinstance(discovery_result, dict)
        assert 'schema' in discovery_result
        assert 'tables' in discovery_result
        
        # Test classification tool
        classification_result = agents.classify_schema(schema)
        assert isinstance(classification_result, dict)
        assert 'total_columns' in classification_result
        assert 'pii_columns' in classification_result


class TestErrorHandling:
    """Test error handling and rollback."""
    
    def test_execution_rollback_on_error(self, integration_patient, db_conn):
        """Test that errors during execution roll back everything."""
        patient_id = integration_patient
        
        # Generate plan
        steps = erasure.plan(patient_id)
        
        # Inject a bad SQL statement in one step
        # (This simulates an error during execution)
        for step in steps:
            if step.sql and 'APPOINTMENT' in step.sql:
                # Make SQL invalid
                step.sql = 'INVALID SQL STATEMENT'
                break
        
        plan_hash_value = erasure.plan_hash(steps)
        
        # Count rows before
        cur = db_conn.cursor()
        cur.execute("SELECT COUNT(*) FROM PATIENT WHERE ID = ?", (patient_id,))
        patient_count_before = cur.fetchone()[0]
        
        # Try to execute (should fail and rollback)
        with pytest.raises(Exception):
            erasure.execute(
                steps,
                patient_id,
                "error_test@example.com",
                "ERROR-TEST-001",
                plan_hash_value
            )
        
        # Verify nothing was deleted (rollback worked)
        cur.execute("SELECT COUNT(*) FROM PATIENT WHERE ID = ?", (patient_id,))
        patient_count_after = cur.fetchone()[0]
        assert patient_count_after == patient_count_before  # Still there!


class TestEndToEndDemo:
    """Test complete demo workflow."""
    
    def test_complete_demo_flow(self, integration_patient):
        """Test the complete demo flow as shown to users."""
        patient_id = integration_patient
        schema = settings.db2_schema
        
        # 1. Discovery
        discovery_result = agents.discover_schema(schema)
        assert len(discovery_result['tables']) >= 7  # Our clinic tables
        
        # 2. Classification
        classification_result = agents.classify_schema(schema)
        assert classification_result['pii_columns'] > 0
        
        # 3. Consent management
        consent.grant(patient_id, "DEMO", "2026-01-01")
        assert consent.valid_on(patient_id, "DEMO", "2026-06-01")
        
        consent.withdraw(patient_id, "DEMO", "2026-07-01")
        assert not consent.valid_on(patient_id, "DEMO", "2026-07-15")
        
        # 4. Rights request planning
        plan_result = agents.plan_erasure(patient_id)
        assert plan_result['simulation']['total_steps'] > 0
        
        # 5. Audit verification
        is_valid, error = audit.verify_chain()
        assert is_valid, f"Audit chain broken: {error}"
        
        # All steps completed successfully!


@pytest.mark.slow
class TestPerformance:
    """Performance tests for large operations."""
    
    def test_classification_performance(self):
        """Test that classification completes in reasonable time."""
        import time
        
        start = time.time()
        agents.classify_schema(settings.db2_schema)
        duration = time.time() - start
        
        # Should complete in under 2 minutes
        assert duration < 120, f"Classification took {duration}s (> 120s)"
    
    def test_planning_performance(self, integration_patient):
        """Test that planning completes quickly."""
        import time
        
        start = time.time()
        agents.plan_erasure(integration_patient)
        duration = time.time() - start
        
        # Should complete in under 5 seconds
        assert duration < 5, f"Planning took {duration}s (> 5s)"
