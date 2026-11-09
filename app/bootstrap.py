"""
Bootstrap script to initialize the Db2 database with all required tables.

Run this after starting the Db2 container and before seeding data.
"""
import sys
from pathlib import Path

from app.db import check_db2_version, run_sql_file


def main():
    """Initialize the database schema and application tables."""
    print("=" * 60)
    print("Db2 Privacy Copilot - Database Bootstrap")
    print("=" * 60)
    
    # Check Db2 version
    print("\n1. Checking Db2 version...")
    try:
        version = check_db2_version()
        print(f"   ✓ Db2 version: {version}")
        
        # Check for vector support (needs 12.1.2+)
        if "12.1.2" not in version and "12.1.3" not in version and not version.startswith("12.1.2"):
            print(f"   ⚠ Warning: Vector support requires Db2 12.1.2 or later")
            print(f"      Current version may not support all features")
    except Exception as e:
        print(f"   ✗ Error checking version: {e}")
        print(f"   Continuing anyway...")
    
    # Run SQL scripts in order
    sql_files = [
        "sql/00_schema_clinic.sql",
        "sql/01_app_tables.sql",
        "sql/02_consent_temporal.sql",
    ]
    
    for i, sql_file in enumerate(sql_files, 2):
        print(f"\n{i}. Executing {sql_file}...")
        try:
            run_sql_file(sql_file)
            print(f"   ✓ Completed")
        except Exception as e:
            print(f"   ✗ Error: {e}")
            print(f"\n   This may be normal if tables already exist.")
            print(f"   Check manually if needed: db2 connect to clinic")
            # Don't exit - allow continuation
    
    print("\n" + "=" * 60)
    print("Bootstrap complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("  1. Run: python eval/seed.py")
    print("  2. Run: pytest")
    print("  3. Start API: uvicorn app.api:app --reload")
    print()


if __name__ == "__main__":
    main()
