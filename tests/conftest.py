"""
Pytest configuration and shared fixtures.
"""
import pytest

from app.db import conn


@pytest.fixture
def db_conn():
    """Provide a database connection for tests."""
    c = conn()
    yield c
    c.close()


@pytest.fixture
def sample_patient_id(db_conn):
    """Create a test patient and return the ID."""
    cur = db_conn.cursor()
    cur.execute("""
        INSERT INTO PATIENT (FULL_NM, CUST_MAIL_ID, PH_NO, DOB_DT, GOVT_ID, ADDR1, CITY_NM, PINCODE)
        VALUES ('Test Patient', 'test@example.com', 9876543210, '1990-01-01', 'TESTPAN123', 
                'Test Address', 'Test City', '123456')
    """)
    db_conn.commit()
    
    cur.execute("SELECT ID FROM PATIENT WHERE CUST_MAIL_ID = 'test@example.com'")
    patient_id = cur.fetchone()[0]
    
    yield patient_id
    
    # Cleanup
    cur.execute("DELETE FROM PATIENT WHERE ID = ?", (patient_id,))
    db_conn.commit()
