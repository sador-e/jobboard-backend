import enum
import datetime
import uuid
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

# Enum for User roles
class UserRole(enum.Enum):
    APPLICANT = "applicant"
    COMPANY = "company"

# Enum for Job Status
class JobStatus(enum.Enum):
    DRAFT = "Draft"
    OPEN = "Open"
    CLOSED = "Closed"

# Enum for Application Status
class ApplicationStatus(enum.Enum):
    APPLIED = "Applied"
    REVIEWED = "Reviewed"
    INTERVIEW = "Interview"
    REJECTED = "Rejected"
    HIRED = "Hired"


def generate_uuid():
    return str(uuid.uuid4())


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password = db.Column(db.String(200), nullable=False)  # hashed password
    role = db.Column(db.Enum(UserRole), nullable=False)
    is_verified = db.Column(db.Boolean, default=False)
    email_verification_token = db.Column(db.String(200), nullable=True)
    token_expiration = db.Column(db.DateTime, nullable=True)

    jobs = db.relationship("Job", backref="creator", lazy=True)
    applications = db.relationship("Application", backref="applicant", lazy=True)

    def __repr__(self):
        return f"<User {self.email}>"

    # New: Password hashing and checking methods
    def set_password(self, plaintext_password):
        self.password = generate_password_hash(plaintext_password)

    def check_password(self, plaintext_password):
        return check_password_hash(self.password, plaintext_password)


class Job(db.Model):
    __tablename__ = "jobs"

    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(2000), nullable=False)
    location = db.Column(db.String(255), nullable=True)
    status = db.Column(db.Enum(JobStatus), default=JobStatus.DRAFT, nullable=False)
    created_by = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    applications = db.relationship("Application", backref="job", lazy=True)

    def __repr__(self):
        return f"<Job {self.title} by {self.created_by}>"


class Application(db.Model):
    __tablename__ = "applications"

    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    applicant_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False)
    job_id = db.Column(db.String(36), db.ForeignKey("jobs.id"), nullable=False)
    resume_link = db.Column(db.String(500), nullable=False)
    cover_letter = db.Column(db.String(200), nullable=True)
    status = db.Column(db.Enum(ApplicationStatus), default=ApplicationStatus.APPLIED, nullable=False)
    applied_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('applicant_id', 'job_id', name='unique_application_per_job'),
    )

    def __repr__(self):
        return f"<Application {self.id} by {self.applicant_id} for Job {self.job_id}>"
