from app.extensions import db
import uuid
from datetime import datetime, timezone

def generate_uuid():
    return str(uuid.uuid4())

class PlacementDrive(db.Model):
    __tablename__ = 'placement_drives'
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    company_id = db.Column(db.String(36), db.ForeignKey('companies.id'), nullable=False)
    college_id = db.Column(db.String(36), nullable=True) # can be null for open drives
    created_by_user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    role_title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    eligibility_json = db.Column(db.JSON, nullable=True)
    application_deadline = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(50), default='draft') # draft, published, closed
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

class Invitation(db.Model):
    __tablename__ = 'invitations'
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    drive_id = db.Column(db.String(36), db.ForeignKey('placement_drives.id'), nullable=False)
    student_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    template_id = db.Column(db.String(36), nullable=False) # points to InterviewTemplate
    status = db.Column(db.String(50), default='invited') # invited, accepted, expired, withdrawn
    invited_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    expires_at = db.Column(db.DateTime, nullable=True)
    accepted_at = db.Column(db.DateTime, nullable=True)
