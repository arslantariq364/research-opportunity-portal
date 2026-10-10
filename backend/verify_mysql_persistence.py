"""
Direct MySQL Database Persistence Verification Utility for Phase 4.
Validates that:
1. Operations go to the real MySQL database (research_portal on localhost:3306).
2. Creating an opportunity persists in the raw MySQL table.
3. Updating modifies the raw MySQL row.
4. Closing sets status='Closed' in raw MySQL.
5. Deletion removes the specific row from MySQL.
6. Refreshing data retrieves current MySQL data.
7. Never modifies or deletes unrelated records.
"""
import os
import sys
import pymysql

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)

for path in (PROJECT_ROOT, CURRENT_DIR):
    if path not in sys.path:
        sys.path.insert(0, path)

from backend.app import create_app
from backend.config import Config


def verify_mysql_persistence():
    print("=" * 75)
    print("PHASE 4: REAL MYSQL PERSISTENCE & TABLE-LEVEL AUDIT")
    print("=" * 75)
    print(f"Target Database : {Config.DB_NAME} at {Config.DB_HOST}:{Config.DB_PORT}")
    print(f"Database User    : {Config.DB_USER}")
    print("-" * 75)

    # 1. Establish direct PyMySQL connection for independent out-of-band verification
    db_conn = pymysql.connect(
        host=Config.DB_HOST,
        port=int(Config.DB_PORT),
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=Config.DB_NAME,
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True
    )

    app = create_app(Config)
    client = app.test_client()

    disposable_payload = {
        "title": "DISPOSABLE_PHASE4_AUDIT_RECORD",
        "description": "Disposable test opportunity for direct MySQL table-level audit.",
        "research_area": "Automated Quality Assurance",
        "faculty_name": "QA Audit Lead",
        "department": "Computer Science",
        "required_skills": "PyMySQL, Postman, Flask-SQLAlchemy",
        "available_positions": 2,
        "application_deadline": "2026-11-15",
        "status": "Open"
    }

    test_id = None
    all_success = True

    try:
        with db_conn.cursor() as cursor:
            # Baseline check: count existing records
            cursor.execute("SELECT COUNT(*) AS cnt FROM research_opportunities")
            initial_count = cursor.fetchone()['cnt']
            print(f"Initial existing records in MySQL table: {initial_count}")

            # -------------------------------------------------------------
            # STEP 1: Create record via API and verify in raw MySQL table
            # -------------------------------------------------------------
            print("\n[Step 1] Creating record via POST /api/opportunities...")
            post_res = client.post('/api/opportunities', json=disposable_payload)
            assert post_res.status_code == 201, f"Expected 201, got {post_res.status_code}"
            post_data = post_res.get_json()
            test_id = post_data['id']
            print(f"  -> API returned 201 with generated ID: {test_id}")

            # Raw SQL verification in MySQL
            cursor.execute("SELECT * FROM research_opportunities WHERE id = %s", (test_id,))
            raw_row = cursor.fetchone()
            assert raw_row is not None, f"Record with ID {test_id} not found in MySQL!"
            assert raw_row['title'] == disposable_payload['title']
            assert raw_row['status'] == 'Open'
            assert raw_row['available_positions'] == 2
            print(f"  -> Direct MySQL SELECT confirmed row exists: ID={raw_row['id']}, title='{raw_row['title']}', status='{raw_row['status']}'")

            # -------------------------------------------------------------
            # STEP 2: Update record via API and verify in raw MySQL table
            # -------------------------------------------------------------
            print("\n[Step 2] Updating record via PUT /api/opportunities/<id>...")
            update_payload = {
                "title": "UPDATED_DISPOSABLE_PHASE4_AUDIT_RECORD",
                "available_positions": 5
            }
            put_res = client.put(f'/api/opportunities/{test_id}', json=update_payload)
            assert put_res.status_code == 200, f"Expected 200, got {put_res.status_code}"
            print("  -> API returned 200 for update")

            # Raw SQL verification in MySQL
            cursor.execute("SELECT title, available_positions FROM research_opportunities WHERE id = %s", (test_id,))
            updated_raw = cursor.fetchone()
            assert updated_raw['title'] == update_payload['title']
            assert updated_raw['available_positions'] == 5
            print(f"  -> Direct MySQL SELECT confirmed updated row: title='{updated_raw['title']}', positions={updated_raw['available_positions']}")

            # -------------------------------------------------------------
            # STEP 3: Close opportunity via API and verify in raw MySQL table
            # -------------------------------------------------------------
            print("\n[Step 3] Closing opportunity via PUT status='Closed'...")
            close_res = client.put(f'/api/opportunities/{test_id}', json={"status": "Closed"})
            assert close_res.status_code == 200, f"Expected 200, got {close_res.status_code}"
            print("  -> API returned 200 for closing")

            # Raw SQL verification in MySQL
            cursor.execute("SELECT status FROM research_opportunities WHERE id = %s", (test_id,))
            closed_raw = cursor.fetchone()
            assert closed_raw['status'] == 'Closed'
            print(f"  -> Direct MySQL SELECT confirmed status in database is now '{closed_raw['status']}'")

            # -------------------------------------------------------------
            # STEP 4: Delete record via API and verify removal in raw MySQL
            # -------------------------------------------------------------
            print("\n[Step 4] Deleting opportunity via DELETE /api/opportunities/<id>...")
            del_res = client.delete(f'/api/opportunities/{test_id}')
            assert del_res.status_code == 200, f"Expected 200, got {del_res.status_code}"
            print("  -> API returned 200 for delete")

            # Raw SQL verification in MySQL
            cursor.execute("SELECT COUNT(*) AS cnt FROM research_opportunities WHERE id = %s", (test_id,))
            del_count = cursor.fetchone()['cnt']
            assert del_count == 0, f"Expected 0 records for ID {test_id}, found {del_count}"
            print("  -> Direct MySQL SELECT confirmed record has been deleted (0 rows found)")

            # Final count check: ensures no other records were impacted
            cursor.execute("SELECT COUNT(*) AS cnt FROM research_opportunities")
            final_count = cursor.fetchone()['cnt']
            assert final_count == initial_count, f"Table record count mismatch: initial={initial_count}, final={final_count}"
            print(f"  -> Record count matches initial baseline: {final_count} records remain intact")

            # -------------------------------------------------------------
            # STEP 5: Verify frontend data refresh retrieves accurate data
            # -------------------------------------------------------------
            print("\n[Step 5] Verifying API GET /api/opportunities reflects updated data...")
            get_all_res = client.get('/api/opportunities')
            assert get_all_res.status_code == 200
            all_opps = get_all_res.get_json()
            assert not any(o['id'] == test_id for o in all_opps), "Deleted record still appears in GET all response!"
            print(f"  -> GET /api/opportunities returned {len(all_opps)} active records; deleted record {test_id} not present")

    except Exception as e:
        print(f"\nAUDIT FAILED with error: {e}")
        all_success = False
    finally:
        # Safety cleanup: ensure test record is definitely deleted if exception occurred
        if test_id is not None:
            with db_conn.cursor() as cursor:
                cursor.execute("DELETE FROM research_opportunities WHERE id = %s", (test_id,))
            db_conn.commit()
        db_conn.close()

    print("\n" + "=" * 75)
    if all_success:
        print("REAL MYSQL DATABASE AUDIT PASSED 100%! DATA IS REAL AND PERSISTENT.")
    else:
        print("REAL MYSQL DATABASE AUDIT FAILED!")
    print("=" * 75)
    return all_success


if __name__ == '__main__':
    success = verify_mysql_persistence()
    sys.exit(0 if success else 1)
