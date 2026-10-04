from app.extensions import db
import uuid
from datetime import datetime, timezone

def generate_uuid():
    return str(uuid.uuid4())

class InterviewTemplate(db.Model):
    __tablename__ = 'interview_templates'
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    drive_id = db.Column(db.String(36), db.ForeignKey('placement_drives.id'), nullable=False)
    role_title = db.Column(db.String(150), nullable=False)
    language = db.Column(db.String(50), default='en')
    duration_seconds = db.Column(db.Integer, default=1800)
    question_count = db.Column(db.Integer, default=5)
    follow_up_limit = db.Column(db.Integer, default=1)
    coding_question_count = db.Column(db.Integer, default=1)
    rubric_json = db.Column(db.JSON, nullable=True)
    proctoring_rules_json = db.Column(db.JSON, nullable=True)
    feedback_visibility = db.Column(db.String(50), default='summary')
    version = db.Column(db.Integer, default=1)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

class Question(db.Model):
    __tablename__ = 'questions'
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    template_id = db.Column(db.String(36), db.ForeignKey('interview_templates.id'), nullable=False)
    sequence_no = db.Column(db.Integer, nullable=False)
    type = db.Column(db.String(50), nullable=False)
    difficulty = db.Column(db.String(50), nullable=True)
    prompt = db.Column(db.Text, nullable=False)
    expected_topics_json = db.Column(db.JSON, nullable=True)
    model_answer_json = db.Column(db.JSON, nullable=True)
    coding_task_json = db.Column(db.JSON, nullable=True)
    is_follow_up_allowed = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

class InterviewSession(db.Model):
    __tablename__ = 'interview_sessions'
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    invitation_id = db.Column(db.String(36), db.ForeignKey('invitations.id'), nullable=False)
    student_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    template_id = db.Column(db.String(36), db.ForeignKey('interview_templates.id'), nullable=False)
    status = db.Column(db.String(50), default='not_started')
    consent_version = db.Column(db.String(50), nullable=True)
    consented_at = db.Column(db.DateTime, nullable=True)
    started_at = db.Column(db.DateTime, nullable=True)
    ended_at = db.Column(db.DateTime, nullable=True)
    last_activity_at = db.Column(db.DateTime, nullable=True)
    current_sequence = db.Column(db.Integer, default=1)
    coding_attempts_used = db.Column(db.Integer, default=0)
    integrity_status = db.Column(db.String(50), default='good')
    recording_storage_key = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
