"""
Phase 1 verification tests.
Validates Flask app factory, health endpoints, configuration loading, and SQLAlchemy model definition.
"""
from datetime import date
from backend.models import ResearchOpportunity, db

def test_app_creation(app):
    """Verify application factory successfully instantiates Flask app."""
    assert app is not None
    assert app.config['TESTING'] is True

def test_health_endpoint(client):
    """Verify health check endpoint returns 200 OK and valid JSON."""
    response = client.get('/api/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'ok'
    assert data['phase'] in (1, 2)

def test_root_endpoint(client):
    """Verify root status endpoint returns 200 OK."""
    response = client.get('/')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'ready'

def test_model_schema_definition():
    """Verify ResearchOpportunity model columns match schema requirements."""
    assert ResearchOpportunity.__tablename__ == 'research_opportunities'
    columns = {col.name: col for col in ResearchOpportunity.__table__.columns}
    
    expected_columns = [
        'id', 'title', 'description', 'research_area', 'faculty_name',
        'department', 'required_skills', 'available_positions',
        'application_deadline', 'status'
    ]
    
    for col_name in expected_columns:
        assert col_name in columns, f"Column '{col_name}' missing from ResearchOpportunity model"

    # Verify primary key and nullability
    assert columns['id'].primary_key is True
    assert columns['title'].nullable is False
    assert columns['description'].nullable is False
    assert columns['research_area'].nullable is False
    assert columns['faculty_name'].nullable is False
    assert columns['department'].nullable is False
    assert columns['required_skills'].nullable is False
    assert columns['available_positions'].nullable is False
    assert columns['application_deadline'].nullable is False
    assert columns['status'].nullable is False

def test_model_crud_in_memory(app):
    """Verify ResearchOpportunity model can be instantiated and persisted."""
    with app.app_context():
        opportunity = ResearchOpportunity(
            title="AI in Healthcare Diagnostics",
            description="Investigating deep learning architectures for anomaly detection in medical imaging.",
            research_area="Artificial Intelligence",
            faculty_name="Dr. Sarah Ahmed",
            department="Computer Science",
            required_skills="Python, PyTorch, Computer Vision",
            available_positions=2,
            application_deadline=date(2026, 12, 31),
            status="Open"
        )
        db.session.add(opportunity)
        db.session.commit()

        retrieved = ResearchOpportunity.query.filter_by(title="AI in Healthcare Diagnostics").first()
        assert retrieved is not None
        assert retrieved.id is not None
        assert retrieved.available_positions == 2
        assert retrieved.status == "Open"

        data_dict = retrieved.to_dict()
        assert data_dict['title'] == "AI in Healthcare Diagnostics"
        assert data_dict['status'] == "Open"
        assert data_dict['application_deadline'] == "2026-12-31"
