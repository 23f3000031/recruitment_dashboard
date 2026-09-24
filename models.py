from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Candidate(db.Model):
    __tablename__ = 'candidates'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    position = db.Column(db.String(100))
    experience_years = db.Column(db.Float, default=0)
    skills = db.Column(db.Text)
    education = db.Column(db.String(200))
    college = db.Column(db.String(200))
    degree = db.Column(db.String(100))
    graduation_year = db.Column(db.Integer)
    cgpa = db.Column(db.Float)
    backlogs = db.Column(db.Integer, default=0)
    resume_path = db.Column(db.String(300))
    source = db.Column(db.String(50), default='Direct')
    status = db.Column(db.String(30), default='Applied')
    stage = db.Column(db.String(30), default='Applications')
    applied_date = db.Column(db.DateTime, default=datetime.utcnow)
    avatar_color = db.Column(db.String(20), default='blue')
    location = db.Column(db.String(100), default='')
    verification_status = db.Column(db.String(30), default='Pending')
    eligibility = db.Column(db.String(30), default='Pending')
    ocr_confidence = db.Column(db.Float, default=0)
    interviews = db.relationship('Interview', backref='candidate', lazy=True, cascade='all,delete-orphan')
    assessments = db.relationship('Assessment', backref='candidate', lazy=True, cascade='all,delete-orphan')
    documents = db.relationship('Document', backref='candidate', lazy=True, cascade='all,delete-orphan')
    timeline_events = db.relationship('TimelineEvent', backref='candidate', lazy=True, cascade='all,delete-orphan')

    def to_dict(self):
        return {
            'id': self.id, 'name': self.name, 'email': self.email,
            'phone': self.phone, 'position': self.position,
            'experience_years': self.experience_years, 'skills': self.skills,
            'education': self.education, 'college': self.college,
            'degree': self.degree, 'cgpa': self.cgpa, 'backlogs': self.backlogs,
            'source': self.source, 'status': self.status, 'stage': self.stage,
            'applied_date': self.applied_date.strftime('%d %b %Y') if self.applied_date else '',
            'avatar_color': self.avatar_color, 'verification_status': self.verification_status,
            'eligibility': self.eligibility, 'ocr_confidence': self.ocr_confidence
        }

class VCTRecord(db.Model):
    __tablename__ = 'vct_records'
    id = db.Column(db.Integer, primary_key=True)
    candidate_id = db.Column(db.Integer, db.ForeignKey('candidates.id'), nullable=False)
    document_type = db.Column(db.String(100), default='Marksheet')
    extracted_data = db.Column(db.Text)
    ocr_confidence = db.Column(db.Float, default=0)
    eligibility = db.Column(db.String(30), default='Pending')
    verification_status = db.Column(db.String(30), default='Pending Review')
    name_matched = db.Column(db.Boolean, default=False)
    dob_matched = db.Column(db.Boolean, default=False)
    cgpa_verified = db.Column(db.Boolean, default=False)
    eligibility_passed = db.Column(db.Boolean, default=False)
    discrepancy = db.Column(db.String(300), default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    candidate = db.relationship('Candidate', backref='vct_records', lazy=True)

class Interview(db.Model):
    __tablename__ = 'interviews'
    id = db.Column(db.Integer, primary_key=True)
    candidate_id = db.Column(db.Integer, db.ForeignKey('candidates.id'), nullable=False)
    interviewer = db.Column(db.String(100))
    date = db.Column(db.Date)
    time = db.Column(db.String(20))
    round_type = db.Column(db.String(50))
    meet_link = db.Column(db.String(300))
    status = db.Column(db.String(20), default='Scheduled')
    notes = db.Column(db.Text)
    feedback = db.Column(db.Text)
    # Feedback rating fields
    communication = db.Column(db.Integer, default=0)  # 1-5
    technical_skill = db.Column(db.Integer, default=0)  # 1-5
    problem_solving = db.Column(db.Integer, default=0)  # 1-5
    cultural_fit = db.Column(db.Integer, default=0)  # 1-5
    recommendation = db.Column(db.String(20), default='Maybe')  # Strongly Hire / Hire / Maybe / No Hire
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Assessment(db.Model):
    __tablename__ = 'assessments'
    id = db.Column(db.Integer, primary_key=True)
    candidate_id = db.Column(db.Integer, db.ForeignKey('candidates.id'), nullable=False)
    name = db.Column(db.String(200))
    type = db.Column(db.String(50))
    score = db.Column(db.Float)
    max_score = db.Column(db.Float, default=100)
    technical_score = db.Column(db.Float)
    problem_solving = db.Column(db.Float)
    coding_score = db.Column(db.Float)
    accuracy = db.Column(db.Float)
    result = db.Column(db.String(20), default='Pending')
    status = db.Column(db.String(20), default='Pending')
    date = db.Column(db.DateTime, default=datetime.utcnow)

class Document(db.Model):
    __tablename__ = 'documents'
    id = db.Column(db.Integer, primary_key=True)
    candidate_id = db.Column(db.Integer, db.ForeignKey('candidates.id'), nullable=False)
    type = db.Column(db.String(100))
    triggered_by = db.Column(db.String(50), default='System')
    generated_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='Pending')
    file_path = db.Column(db.String(300))

class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50))
    message = db.Column(db.String(300))
    related_id = db.Column(db.Integer, default=0)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class TimelineEvent(db.Model):
    __tablename__ = 'timeline_events'
    id = db.Column(db.Integer, primary_key=True)
    candidate_id = db.Column(db.Integer, db.ForeignKey('candidates.id'), nullable=False)
    event = db.Column(db.String(200))
    description = db.Column(db.String(300))
    stage = db.Column(db.String(30))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200))
    role = db.Column(db.String(50), default='Recruiter')
    avatar = db.Column(db.String(10), default='HR')
    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime)
    jobs = db.relationship('Job', backref='recruiter', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class CodeExecution(db.Model):
    __tablename__ = 'code_executions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    code = db.Column(db.Text)
    language = db.Column(db.String(50), default='python')
    output = db.Column(db.Text)
    status = db.Column(db.String(20), default='success')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<CodeExecution {self.id}>'


class Job(db.Model):
    __tablename__ = 'jobs'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(50))
    location = db.Column(db.String(100))
    openings = db.Column(db.Integer, default=1)
    experience_required = db.Column(db.String(50))
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='Open')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    recruiter_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __repr__(self):
        return f'<Job {self.title}>'