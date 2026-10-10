"""
Real MySQL Database Integration Test Utility.
Safely tests the full CRUD lifecycle against the real MySQL database configured in .env.
Creates a temporary identifiable record, reads it, updates it, changes status to Closed,
deletes it, and verifies 404 Not Found.
"""
import sys
import os

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)

for path in (PROJECT_ROOT, CURRENT_DIR):
    if path not in sys.path:
        sys.path.insert(0, path)

from backend.app import create_app
from backend.config import Config


def run_mysql_integration_test():
    print("=" * 70)
    print("University Research Opportunity Portal - Real MySQL Integration Test")
    print("=" * 70)
    print(f"Target Database: {Config.DB_NAME} at {Config.DB_HOST}:{Config.DB_PORT}")
    print(f"Database User:   {Config.DB_USER}")
    print("-" * 70)

    app = create_app(Config)
    client = app.test_client()

    test_payload = {
        "title": "TEMPORARY_TEST_OPPORTUNITY_PHASE2",
        "description": "Integration test record for MySQL persistence verification in Phase 2.",
        "research_area": "Systems Engineering",
        "faculty_name": "Integration Test Runner",
        "department": "Computer Science",
        "required_skills": "Python, MySQL, REST API",
        "available_positions": 1,
        "application_deadline": "2026-12-31",
        "status": "Open"
    }

    test_id = None
    all_passed = True

    try:
        # STEP 1: POST /api/opportunities
        print("[1/6] POST /api/opportunities (Create opportunity)...")
        post_res = client.post('/api/opportunities', json=test_payload)
        if post_res.status_code != 201:
            print(f"  FAILED: Expected status 201, got {post_res.status_code}. Response: {post_res.get_data(as_text=True)}")
            return False
        created_data = post_res.get_json()
        test_id = created_data.get('id')
        print(f"  SUCCESS: Record created in MySQL with ID: {test_id}")
        assert created_data['title'] == test_payload['title']
        assert created_data['status'] == 'Open'

        # STEP 2: GET /api/opportunities/<id>
        print(f"[2/6] GET /api/opportunities/{test_id} (Retrieve by ID)...")
        get_res = client.get(f'/api/opportunities/{test_id}')
        if get_res.status_code != 200:
            print(f"  FAILED: Expected status 200, got {get_res.status_code}")
            return False
        fetched_data = get_res.get_json()
        print(f"  SUCCESS: Retrieved record matching title: '{fetched_data['title']}'")
        assert fetched_data['id'] == test_id

        # STEP 3: PUT /api/opportunities/<id> (Partial field update)
        print(f"[3/6] PUT /api/opportunities/{test_id} (Partial update available_positions to 3)...")
        put_res = client.put(f'/api/opportunities/{test_id}', json={"available_positions": 3})
        if put_res.status_code != 200:
            print(f"  FAILED: Expected status 200, got {put_res.status_code}")
            return False
        updated_data = put_res.get_json()
        print(f"  SUCCESS: Updated available_positions to: {updated_data['available_positions']}")
        assert updated_data['available_positions'] == 3

        # STEP 4: PUT /api/opportunities/<id> (Change status to Closed)
        print(f"[4/6] PUT /api/opportunities/{test_id} (Change status to Closed)...")
        status_res = client.put(f'/api/opportunities/{test_id}', json={"status": "Closed"})
        if status_res.status_code != 200:
            print(f"  FAILED: Expected status 200, got {status_res.status_code}")
            return False
        status_data = status_res.get_json()
        print(f"  SUCCESS: Updated status to: '{status_data['status']}'")
        assert status_data['status'] == "Closed"

        # STEP 5: DELETE /api/opportunities/<id>
        print(f"[5/6] DELETE /api/opportunities/{test_id} (Delete record)...")
        del_res = client.delete(f'/api/opportunities/{test_id}')
        if del_res.status_code != 200:
            print(f"  FAILED: Expected status 200, got {del_res.status_code}")
            return False
        print(f"  SUCCESS: Deleted record. Message: {del_res.get_json().get('message')}")

        # STEP 6: GET /api/opportunities/<id> (Verify 404 after deletion)
        print(f"[6/6] GET /api/opportunities/{test_id} (Verify 404 Not Found)...")
        verify_res = client.get(f'/api/opportunities/{test_id}')
        if verify_res.status_code != 404:
            print(f"  FAILED: Expected status 404, got {verify_res.status_code}")
            return False
        print(f"  SUCCESS: Verified record is deleted from MySQL (received HTTP 404 Not Found).")

    except Exception as e:
        print(f"EXCEPTION during integration testing: {e}")
        all_passed = False
    finally:
        # Safety cleanup: ensure test record is deleted if still present
        if test_id is not None:
            cleanup_check = client.get(f'/api/opportunities/{test_id}')
            if cleanup_check.status_code == 200:
                print(f"Cleanup: Removing residual test record {test_id}...")
                client.delete(f'/api/opportunities/{test_id}')

    print("=" * 70)
    if all_passed:
        print("REAL MYSQL INTEGRATION TEST COMPLETED SUCCESSFULLY!")
    else:
        print("REAL MYSQL INTEGRATION TEST FAILED!")
    print("=" * 70)
    return all_passed


if __name__ == '__main__':
    success = run_mysql_integration_test()
    sys.exit(0 if success else 1)
