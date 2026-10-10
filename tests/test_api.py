"""
Automated unit tests for University Research Opportunity Portal REST API.
Validates all Phase 2 endpoints, validation rules, HTTP status codes, and persistence.
"""
import json
import pytest

SAMPLE_VALID_OPPORTUNITY = {
    "title": "Quantum Machine Learning",
    "description": "Investigating variational quantum eigensolvers for chemical simulations.",
    "research_area": "Quantum Computing",
    "faculty_name": "Dr. Sarah Ahmed",
    "department": "Computer Science",
    "required_skills": "Python, Qiskit, Linear Algebra",
    "available_positions": 3,
    "application_deadline": "2026-11-30",
    "status": "Open"
}


# ==============================================================================
# TEST 1: POST creates an opportunity and returns 201
# ==============================================================================
def test_post_creates_opportunity_201(client):
    """Verify POST /api/opportunities creates a record and returns 201 with created object."""
    response = client.post(
        '/api/opportunities',
        data=json.dumps(SAMPLE_VALID_OPPORTUNITY),
        content_type='application/json'
    )
    assert response.status_code == 201
    data = response.get_json()
    assert 'id' in data
    assert data['id'] is not None
    assert data['title'] == SAMPLE_VALID_OPPORTUNITY['title']
    assert data['description'] == SAMPLE_VALID_OPPORTUNITY['description']
    assert data['research_area'] == SAMPLE_VALID_OPPORTUNITY['research_area']
    assert data['faculty_name'] == SAMPLE_VALID_OPPORTUNITY['faculty_name']
    assert data['department'] == SAMPLE_VALID_OPPORTUNITY['department']
    assert data['required_skills'] == SAMPLE_VALID_OPPORTUNITY['required_skills']
    assert data['available_positions'] == 3
    assert data['application_deadline'] == "2026-11-30"
    assert data['status'] == "Open"


# ==============================================================================
# TEST 2: GET returns all opportunities
# ==============================================================================
def test_get_all_opportunities_200(client):
    """Verify GET /api/opportunities retrieves all stored opportunities as an array."""
    # Initially empty or previously added
    res_initial = client.get('/api/opportunities')
    assert res_initial.status_code == 200
    initial_count = len(res_initial.get_json())

    # Add two distinct records
    client.post('/api/opportunities', json=SAMPLE_VALID_OPPORTUNITY)
    second_opp = {
        **SAMPLE_VALID_OPPORTUNITY,
        "title": "Robotics Vision Navigation",
        "status": "Closed"
    }
    client.post('/api/opportunities', json=second_opp)

    res = client.get('/api/opportunities')
    assert res.status_code == 200
    opportunities = res.get_json()
    assert isinstance(opportunities, list)
    assert len(opportunities) == initial_count + 2

    titles = [o['title'] for o in opportunities]
    assert "Quantum Machine Learning" in titles
    assert "Robotics Vision Navigation" in titles


# ==============================================================================
# TEST 3: GET by ID returns the correct opportunity
# ==============================================================================
def test_get_by_id_200(client):
    """Verify GET /api/opportunities/<id> returns the specified opportunity."""
    create_res = client.post('/api/opportunities', json=SAMPLE_VALID_OPPORTUNITY)
    assert create_res.status_code == 201
    created_id = create_res.get_json()['id']

    get_res = client.get(f'/api/opportunities/{created_id}')
    assert get_res.status_code == 200
    data = get_res.get_json()
    assert data['id'] == created_id
    assert data['title'] == SAMPLE_VALID_OPPORTUNITY['title']
    assert data['faculty_name'] == SAMPLE_VALID_OPPORTUNITY['faculty_name']


# ==============================================================================
# TEST 4: GET nonexistent ID returns 404
# ==============================================================================
def test_get_nonexistent_id_404(client):
    """Verify GET /api/opportunities/<id> returns 404 for nonexistent or invalid IDs."""
    res_missing = client.get('/api/opportunities/999999')
    assert res_missing.status_code == 404
    data = res_missing.get_json()
    assert "error" in data
    assert data["error"] == "Research opportunity not found"

    # Also test non-integer invalid string ID
    res_invalid_id = client.get('/api/opportunities/not-an-id')
    assert res_invalid_id.status_code == 404


# ==============================================================================
# TEST 5: PUT successfully updates an opportunity
# ==============================================================================
def test_put_updates_opportunity_200(client):
    """Verify PUT /api/opportunities/<id> updates specified fields and returns 200."""
    create_res = client.post('/api/opportunities', json=SAMPLE_VALID_OPPORTUNITY)
    created_id = create_res.get_json()['id']

    update_payload = {
        "title": "Advanced Quantum ML and Optimization",
        "available_positions": 5
    }
    put_res = client.put(f'/api/opportunities/{created_id}', json=update_payload)
    assert put_res.status_code == 200
    updated_data = put_res.get_json()
    assert updated_data['id'] == created_id
    assert updated_data['title'] == "Advanced Quantum ML and Optimization"
    assert updated_data['available_positions'] == 5
    # Unchanged fields remain intact
    assert updated_data['faculty_name'] == SAMPLE_VALID_OPPORTUNITY['faculty_name']
    assert updated_data['status'] == "Open"


# ==============================================================================
# TEST 6: PUT changes status from Open to Closed
# ==============================================================================
def test_put_changes_status_open_to_closed(client):
    """Verify PUT can change status from Open to Closed."""
    create_res = client.post('/api/opportunities', json=SAMPLE_VALID_OPPORTUNITY)
    created_id = create_res.get_json()['id']
    assert create_res.get_json()['status'] == "Open"

    put_res = client.put(f'/api/opportunities/{created_id}', json={"status": "Closed"})
    assert put_res.status_code == 200
    assert put_res.get_json()['status'] == "Closed"

    # Verify retrieval reflects Closed
    get_res = client.get(f'/api/opportunities/{created_id}')
    assert get_res.get_json()['status'] == "Closed"


# ==============================================================================
# TEST 7: DELETE removes an opportunity
# ==============================================================================
def test_delete_removes_opportunity_200(client):
    """Verify DELETE /api/opportunities/<id> removes the record and returns 200."""
    create_res = client.post('/api/opportunities', json=SAMPLE_VALID_OPPORTUNITY)
    created_id = create_res.get_json()['id']

    del_res = client.delete(f'/api/opportunities/{created_id}')
    assert del_res.status_code == 200
    assert "deleted successfully" in del_res.get_json()['message']


# ==============================================================================
# TEST 8: GET after DELETE returns 404
# ==============================================================================
def test_get_after_delete_returns_404(client):
    """Verify that requesting an ID after deletion returns 404 Not Found."""
    create_res = client.post('/api/opportunities', json=SAMPLE_VALID_OPPORTUNITY)
    created_id = create_res.get_json()['id']

    client.delete(f'/api/opportunities/{created_id}')

    get_res = client.get(f'/api/opportunities/{created_id}')
    assert get_res.status_code == 404
    assert get_res.get_json()['error'] == "Research opportunity not found"


# ==============================================================================
# TEST 9: Missing required field returns 400
# ==============================================================================
def test_missing_required_field_400(client):
    """Verify POST returns 400 when any required field is missing."""
    incomplete_payload = dict(SAMPLE_VALID_OPPORTUNITY)
    del incomplete_payload['title']

    res = client.post('/api/opportunities', json=incomplete_payload)
    assert res.status_code == 400
    data = res.get_json()
    assert data['error'] == "Validation failed"
    assert "title" in data['messages']


# ==============================================================================
# TEST 10: Negative or invalid available_positions returns 400
# ==============================================================================
def test_negative_or_zero_available_positions_400(client):
    """Verify available_positions <= 0 or non-integer returns 400."""
    # Negative number
    res_neg = client.post('/api/opportunities', json={
        **SAMPLE_VALID_OPPORTUNITY,
        "available_positions": -2
    })
    assert res_neg.status_code == 400
    assert "available_positions" in res_neg.get_json()['messages']

    # Zero
    res_zero = client.post('/api/opportunities', json={
        **SAMPLE_VALID_OPPORTUNITY,
        "available_positions": 0
    })
    assert res_zero.status_code == 400

    # Boolean passed as integer (e.g. True)
    res_bool = client.post('/api/opportunities', json={
        **SAMPLE_VALID_OPPORTUNITY,
        "available_positions": True
    })
    assert res_bool.status_code == 400


# ==============================================================================
# TEST 11: Invalid application_deadline returns 400
# ==============================================================================
def test_invalid_application_deadline_400(client):
    """Verify malformed or impossible dates return 400."""
    # Bad format
    res_format = client.post('/api/opportunities', json={
        **SAMPLE_VALID_OPPORTUNITY,
        "application_deadline": "30-11-2026"
    })
    assert res_format.status_code == 400
    assert "application_deadline" in res_format.get_json()['messages']

    # Impossible date (e.g. Feb 30)
    res_impossible = client.post('/api/opportunities', json={
        **SAMPLE_VALID_OPPORTUNITY,
        "application_deadline": "2026-02-30"
    })
    assert res_impossible.status_code == 400
    assert "application_deadline" in res_impossible.get_json()['messages']


# ==============================================================================
# TEST 12: Invalid status returns 400
# ==============================================================================
def test_invalid_status_400(client):
    """Verify status values other than 'Open' or 'Closed' return 400."""
    res = client.post('/api/opportunities', json={
        **SAMPLE_VALID_OPPORTUNITY,
        "status": "Pending"
    })
    assert res.status_code == 400
    assert "status" in res.get_json()['messages']


# ==============================================================================
# TEST 13: Malformed JSON returns 400
# ==============================================================================
def test_malformed_json_400(client):
    """Verify malformed JSON or invalid body returns 400 Bad Request."""
    res = client.post(
        '/api/opportunities',
        data="INVALID{JSON:PAYLOAD",
        content_type='application/json'
    )
    assert res.status_code == 400
    assert "error" in res.get_json()


# ==============================================================================
# TEST 14: Unexpected fields are handled correctly (rejected with 400)
# ==============================================================================
def test_unexpected_fields_rejected_400(client):
    """Verify unsupported fields are rejected with 400 on POST and PUT."""
    payload_with_extra = {
        **SAMPLE_VALID_OPPORTUNITY,
        "budget": 50000,
        "secret_token": "abc123xyz"
    }
    res_post = client.post('/api/opportunities', json=payload_with_extra)
    assert res_post.status_code == 400
    data = res_post.get_json()
    assert "budget" in data['messages']
    assert "secret_token" in data['messages']

    # Test unexpected field on PUT as well
    create_res = client.post('/api/opportunities', json=SAMPLE_VALID_OPPORTUNITY)
    created_id = create_res.get_json()['id']

    res_put = client.put(f'/api/opportunities/{created_id}', json={"unknown_col": "val"})
    assert res_put.status_code == 400
    assert "unknown_col" in res_put.get_json()['messages']


# ==============================================================================
# TEST 15: Saved changes persist across separate database requests
# ==============================================================================
def test_saved_changes_persist_across_requests(client):
    """Verify created and updated opportunities persist cleanly across distinct calls."""
    # 1. Create opportunity
    create_res = client.post('/api/opportunities', json=SAMPLE_VALID_OPPORTUNITY)
    assert create_res.status_code == 201
    created_id = create_res.get_json()['id']

    # 2. Separate request to read it
    get1 = client.get(f'/api/opportunities/{created_id}')
    assert get1.status_code == 200
    assert get1.get_json()['title'] == SAMPLE_VALID_OPPORTUNITY['title']

    # 3. Update in a separate request
    put_res = client.put(f'/api/opportunities/{created_id}', json={
        "department": "Electrical & Computer Engineering",
        "available_positions": 4
    })
    assert put_res.status_code == 200

    # 4. Read again in a third request to ensure persistence
    get2 = client.get(f'/api/opportunities/{created_id}')
    assert get2.status_code == 200
    data2 = get2.get_json()
    assert data2['department'] == "Electrical & Computer Engineering"
    assert data2['available_positions'] == 4
    assert data2['title'] == SAMPLE_VALID_OPPORTUNITY['title']


# ==============================================================================
# ADDITIONAL EDGE CASE TESTS
# ==============================================================================
def test_empty_and_whitespace_strings_rejected_400(client):
    """Verify empty or whitespace-only string fields return 400."""
    res_empty = client.post('/api/opportunities', json={
        **SAMPLE_VALID_OPPORTUNITY,
        "title": "   "
    })
    assert res_empty.status_code == 400
    assert "title" in res_empty.get_json()['messages']


def test_post_default_status_is_open(client):
    """Verify that if status is omitted in POST, it defaults to 'Open'."""
    payload_without_status = dict(SAMPLE_VALID_OPPORTUNITY)
    del payload_without_status['status']

    res = client.post('/api/opportunities', json=payload_without_status)
    assert res.status_code == 201
    assert res.get_json()['status'] == "Open"


def test_put_nonexistent_returns_404(client):
    """Verify PUT to a nonexistent ID returns 404."""
    res = client.put('/api/opportunities/999999', json={"title": "New Title"})
    assert res.status_code == 404
    assert res.get_json()['error'] == "Research opportunity not found"


def test_delete_nonexistent_returns_404(client):
    """Verify DELETE to a nonexistent ID returns 404."""
    res = client.delete('/api/opportunities/999999')
    assert res.status_code == 404
    assert res.get_json()['error'] == "Research opportunity not found"
