from app.extensions import db
from datetime import datetime, timezone

class StudentProfile(db.Model):
    __tablename__ = 'student_profiles'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), unique=True, nullable=False)
    branch = db.Column(db.String(150), nullable=True)
    course_name = db.Column(db.String(150), nullable=True)
    job_experience = db.Column(db.String(50), nullable=True)
    job_roles = db.Column(db.String(500), nullable=True)
    company_names = db.Column(db.String(500), nullable=True)
    cgpa = db.Column(db.Numeric(4, 2), nullable=True)
    skills_json = db.Column(db.JSON, nullable=True)
    projects_json = db.Column(db.JSON, nullable=True)
    subjects_of_interest_json = db.Column(db.JSON, nullable=True)
    tools_json = db.Column(db.JSON, nullable=True)
    libraries_json = db.Column(db.JSON, nullable=True)
    frameworks_json = db.Column(db.JSON, nullable=True)
    certificates_json = db.Column(db.JSON, nullable=True)
    preferred_roles_json = db.Column(db.JSON, nullable=True)
    cv_path = db.Column(db.String(255), nullable=True)
    cv_text = db.Column(db.Text, nullable=True)
    ai_extracted_data = db.Column(db.JSON, nullable=True)
    profile_complete = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
