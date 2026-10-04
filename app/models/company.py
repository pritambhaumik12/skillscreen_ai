from app.extensions import db
import uuid
from datetime import datetime, timezone

def generate_uuid():
    return str(uuid.uuid4())

class Company(db.Model):
    __tablename__ = 'companies'
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    name = db.Column(db.String(150), nullable=False)
    website = db.Column(db.String(255), nullable=True)
    recruiter_owner_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    verification_status = db.Column(db.String(50), default='pending')
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
