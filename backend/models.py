"""
SQLAlchemy models for University Research Opportunity Portal.
Defines schema for the research_opportunities table.
"""
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class ResearchOpportunity(db.Model):
    """
    Model representing a university research opportunity.
    Matches schema definition in database/schema.sql.
    """
    __tablename__ = 'research_opportunities'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    research_area = db.Column(db.String(255), nullable=False)
    faculty_name = db.Column(db.String(255), nullable=False)
    department = db.Column(db.String(255), nullable=False)
    required_skills = db.Column(db.Text, nullable=False)  # Comma-separated string
    available_positions = db.Column(db.Integer, nullable=False)
    application_deadline = db.Column(db.Date, nullable=False)
    status = db.Column(
        db.Enum('Open', 'Closed', name='opportunity_status'),
        nullable=False,
        default='Open'
    )

    __table_args__ = (
        db.CheckConstraint('available_positions > 0', name='chk_available_positions_positive'),
        db.CheckConstraint("status IN ('Open', 'Closed')", name='chk_status_valid'),
    )

    def to_dict(self):
        """Serialize model instance to a dictionary representation."""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'research_area': self.research_area,
            'faculty_name': self.faculty_name,
            'department': self.department,
            'required_skills': self.required_skills,
            'available_positions': self.available_positions,
            'application_deadline': self.application_deadline.isoformat() if self.application_deadline else None,
            'status': self.status
        }

    def __repr__(self):
        return f"<ResearchOpportunity id={self.id} title='{self.title}' status='{self.status}'>"
