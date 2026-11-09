"""
Database connection and query utilities.

Safety assumptions:
- All values are passed via parameterized queries (? placeholders)
- All identifiers come from the Db2 catalog, never from user input
- Connections are short-lived and closed after use

Production Recommendations:
- Implement connection pooling for better performance
- Add connection timeout and retry logic
- Consider using SQLAlchemy for ORM capabilities
- Add query caching for frequently accessed data
- Implement read replicas for scalability
- Add database health monitoring
"""
from typing import Any, Optional

import ibm_db
import ibm_db_dbi

from app.config import get_dsn


def conn() -> ibm_db_dbi.Connection:
    """
    Create a new Db2 connection.
    
    Returns:
        ibm_db_dbi.Connection: Database connection
        
    Raises:
        Exception: If connection fails
    """
    return ibm_db_dbi.connect(get_dsn(), "", "")


def query(sql: str, params: tuple = ()) -> Optional[list[tuple[Any, ...]]]:
    """
    Execute a query and return results.
    
    Args:
        sql: SQL query with ? placeholders for parameters
        params: Tuple of parameter values
        
    Returns:
        List of result rows, or None for non-SELECT queries
        
    Safety:
        - Uses parameterized queries exclusively
        - Closes connection after use
    """
    c = conn()
    try:
        cur = c.cursor()
        cur.execute(sql, params)
        if cur.description:  # SELECT query
            return cur.fetchall()
        c.commit()
        return None
    finally:
        c.close()


def execute(sql: str, params: tuple = ()) -> int:
    """
    Execute a non-query statement (INSERT, UPDATE, DELETE).
    
    Args:
        sql: SQL statement with ? placeholders
        params: Tuple of parameter values
        
    Returns:
        Number of rows affected
    """
    c = conn()
    try:
        cur = c.cursor()
        cur.execute(sql, params)
        rowcount = cur.rowcount
        c.commit()
        return rowcount
    finally:
        c.close()


def check_db2_version() -> str:
    """
    Check Db2 version to ensure vector support is available.
    
    Returns:
        str: Db2 service level
        
    Raises:
        RuntimeError: If version check fails
    """
    try:
        result = query("SELECT SERVICE_LEVEL FROM SYSIBMADM.ENV_INST_INFO")
        if result and len(result) > 0:
            return result[0][0]
        raise RuntimeError("Could not determine Db2 version")
    except Exception as e:
        raise RuntimeError(f"Db2 version check failed: {e}")


def run_sql_file(filepath: str) -> None:
    """
    Execute SQL statements from a file.
    
    Args:
        filepath: Path to SQL file
        
    Note:
        Statements must be separated by semicolons.
        Does not support complex PL/SQL blocks.
        
    Raises:
        FileNotFoundError: If SQL file doesn't exist
        Exception: If SQL execution fails
    """
    try:
        with open(filepath, "r") as f:
            sql_content = f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"SQL file not found: {filepath}")
    
    # Split by semicolon and execute each statement
    statements = [s.strip() for s in sql_content.split(";") if s.strip()]
    
    c = conn()
    errors = []
    
    try:
        cur = c.cursor()
        for i, stmt in enumerate(statements, 1):
            # Skip comments and empty lines
            if stmt.startswith("--") or not stmt:
                continue
            try:
                cur.execute(stmt)
            except Exception as e:
                error_msg = f"Statement #{i} failed: {stmt[:50]}... Error: {e}"
                print(f"Warning: {error_msg}")
                errors.append(error_msg)
        c.commit()
    except Exception as e:
        c.rollback()
        raise Exception(f"Fatal error executing {filepath}: {e}")
    finally:
        c.close()
    
    if errors:
        print(f"\n⚠️  {len(errors)} statement(s) failed (non-fatal)")
        print("This is normal if tables already exist.")
