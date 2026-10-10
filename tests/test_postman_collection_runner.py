"""
Automated Execution Verification for Postman Collection v2.1.
Executes all 10 requests from Research_Opportunity_Portal.postman_collection.json
in sequential order against the active Flask backend server (http://127.0.0.1:5000).
Verifies HTTP status codes, JSON responses, dynamic ID capturing, status transitions,
and 404/400 handling.
"""
import json
import urllib.request
import urllib.error
import sys

COLLECTION_PATH = "postman/Research_Opportunity_Portal.postman_collection.json"
BASE_URL = "http://127.0.0.1:5000"


def run_collection():
    print("=" * 75)
    print("EXECUTING POSTMAN COLLECTION v2.1 TEST RUNNER")
    print("=" * 75)
    print(f"Collection File : {COLLECTION_PATH}")
    print(f"Target Base URL : {BASE_URL}")
    print("-" * 75)

    with open(COLLECTION_PATH, 'r') as f:
        collection_data = json.load(f)

    items = collection_data.get('item', [])
    print(f"Total Requests in Collection: {len(items)}\n")

    variables = {
        "baseUrl": BASE_URL,
        "opportunity_id": ""
    }

    results = []

    for idx, item in enumerate(items, start=1):
        name = item['name']
        req = item['request']
        method = req['method']
        raw_url = req['url']['raw']

        # Replace variables in URL
        for k, v in variables.items():
            raw_url = raw_url.replace(f"{{{{{k}}}}}", str(v))

        # Prepare headers
        headers = {}
        for h in req.get('header', []):
            headers[h['key']] = h['value']

        # Prepare body
        body_data = None
        if 'body' in req and req['body'].get('mode') == 'raw':
            raw_body = req['body']['raw']
            for k, v in variables.items():
                raw_body = raw_body.replace(f"{{{{{k}}}}}", str(v))
            body_data = raw_body.encode('utf-8')

        http_req = urllib.request.Request(
            url=raw_url,
            data=body_data,
            headers=headers,
            method=method
        )

        status_code = None
        resp_json = None
        error_msg = None

        try:
            with urllib.request.urlopen(http_req) as response:
                status_code = response.status
                resp_text = response.read().decode('utf-8')
                if resp_text:
                    resp_json = json.loads(resp_text)
        except urllib.error.HTTPError as e:
            status_code = e.code
            resp_text = e.read().decode('utf-8')
            if resp_text:
                try:
                    resp_json = json.loads(resp_text)
                except Exception:
                    resp_json = {"raw": resp_text}
        except Exception as e:
            error_msg = str(e)

        # Verification rules per request
        passed = False
        notes = ""

        if idx == 1:  # Create Opportunity 1
            if status_code == 201 and resp_json and 'id' in resp_json:
                variables['opportunity_id'] = resp_json['id']
                passed = True
                notes = f"Created ID: {resp_json['id']}, Status: {resp_json['status']}"
            else:
                notes = f"Expected 201 with ID, got {status_code}: {resp_json}"

        elif idx == 2:  # Create Opportunity 2
            if status_code == 201 and resp_json and 'id' in resp_json:
                passed = True
                notes = f"Created ID: {resp_json['id']}, Dept: {resp_json['department']}"
            else:
                notes = f"Expected 201 with ID, got {status_code}"

        elif idx == 3:  # Create Opportunity 3
            if status_code == 201 and resp_json and 'id' in resp_json:
                passed = True
                notes = f"Created ID: {resp_json['id']}, Area: {resp_json['research_area']}"
            else:
                notes = f"Expected 201 with ID, got {status_code}"

        elif idx == 4:  # Retrieve All Opportunities
            if status_code == 200 and isinstance(resp_json, list):
                has_target = any(o['id'] == variables['opportunity_id'] for o in resp_json)
                if has_target:
                    passed = True
                    notes = f"Retrieved {len(resp_json)} items; target ID {variables['opportunity_id']} verified"
                else:
                    notes = f"Target ID {variables['opportunity_id']} not found in GET all list"
            else:
                notes = f"Expected 200 array, got {status_code}"

        elif idx == 5:  # Retrieve Opportunity by ID
            if status_code == 200 and resp_json and resp_json.get('id') == variables['opportunity_id']:
                passed = True
                notes = f"Retrieved matching ID {resp_json['id']}, Title: '{resp_json['title'][:30]}...'"
            else:
                notes = f"Expected 200 with ID {variables['opportunity_id']}, got {status_code}"

        elif idx == 6:  # Update Opportunity
            if status_code == 200 and resp_json and resp_json.get('available_positions') == 4:
                passed = True
                notes = f"Updated positions to {resp_json['available_positions']}"
            else:
                notes = f"Expected 200 with updated fields, got {status_code}"

        elif idx == 7:  # Close Opportunity
            if status_code == 200 and resp_json and resp_json.get('status') == "Closed":
                passed = True
                notes = "Status transitioned to 'Closed'"
            else:
                notes = f"Expected 200 with status=Closed, got {status_code}"

        elif idx == 8:  # Delete Opportunity
            if status_code == 200 and resp_json and "deleted" in resp_json.get('message', '').lower():
                passed = True
                notes = "Deleted successfully"
            else:
                notes = f"Expected 200 with delete confirmation, got {status_code}"

        elif idx == 9:  # Retrieve Deleted Opportunity
            if status_code == 404 and resp_json and resp_json.get('error') == "Research opportunity not found":
                passed = True
                notes = "Verified 404 Not Found error response"
            else:
                notes = f"Expected 404, got {status_code}"

        elif idx == 10:  # Invalid Data Request
            if status_code == 400 and resp_json and resp_json.get('error') == "Validation failed":
                passed = True
                notes = "Verified 400 Bad Request with validation error messages"
            else:
                notes = f"Expected 400 validation error, got {status_code}"

        status_str = "PASSED" if passed else "FAILED"
        print(f"[{idx:02d}/10] {name:<35} | {method:<6} | HTTP {status_code} | {status_str} | {notes}")
        results.append({
            "step": idx,
            "name": name,
            "method": method,
            "status_code": status_code,
            "passed": passed,
            "notes": notes
        })

    print("-" * 75)
    all_passed = all(r['passed'] for r in results)
    if all_passed:
        print("ALL 10 POSTMAN COLLECTION REQUESTS EXECUTED AND PASSED (100% SUCCESS)!")
    else:
        print("SOME REQUESTS IN POSTMAN COLLECTION FAILED!")
    print("=" * 75)
    return all_passed


if __name__ == '__main__':
    ok = run_collection()
    sys.exit(0 if ok else 1)
