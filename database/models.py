from database import db
from flask_login import UserMixin
from datetime import datetime
import hashlib


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="student")
    full_name = db.Column(db.String(120))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    student = db.relationship("Student", backref="user", uselist=False, lazy=True)


class Student(db.Model):
    __tablename__ = "students"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    student_id = db.Column(db.String(20), unique=True, nullable=False)
    department = db.Column(db.String(100))
    semester = db.Column(db.Integer)
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    profile_image = db.Column(db.String(200))
    enrollments = db.relationship("Enrollment", backref="student", lazy=True)
    marks = db.relationship("Marks", backref="student", lazy=True)
    predictions = db.relationship("Prediction", backref="student", lazy=True)
    certificates = db.relationship("Certificate", backref="student", lazy=True)


class Course(db.Model):
    __tablename__ = "courses"
    id = db.Column(db.Integer, primary_key=True)
    course_code = db.Column(db.String(20), unique=True, nullable=False)
    course_name = db.Column(db.String(150), nullable=False)
    credits = db.Column(db.Integer, default=3)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    enrollments = db.relationship("Enrollment", backref="course", lazy=True)


class Enrollment(db.Model):
    __tablename__ = "enrollments"
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"), nullable=False)
    enrolled_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default="active")


class Marks(db.Model):
    __tablename__ = "marks"
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"), nullable=False)
    marks_obtained = db.Column(db.Float, nullable=False)
    total_marks = db.Column(db.Float, nullable=False, default=100)
    attendance = db.Column(db.Float, default=0)
    assignments = db.Column(db.Float, default=0)
    quiz_scores = db.Column(db.Float, default=0)
    semester = db.Column(db.Integer)
    exam_type = db.Column(db.String(50), default="final")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    course = db.relationship("Course", backref="marks", lazy=True)


class Prediction(db.Model):
    __tablename__ = "predictions"
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"), nullable=False)
    score = db.Column(db.Float, default=0)
    total_marks = db.Column(db.Float, default=0)
    percentage = db.Column(db.Float, default=0)
    predicted_pass = db.Column(db.String(10))
    predicted_grade = db.Column(db.String(5))
    predicted_performance = db.Column(db.String(30))
    confidence_score = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    course = db.relationship("Course", backref="predictions", lazy=True)


class Certificate(db.Model):
    __tablename__ = "certificates"
    id = db.Column(db.Integer, primary_key=True)
    cert_id = db.Column(db.String(50), unique=True, nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"), nullable=False)
    grade = db.Column(db.String(5), nullable=False)
    marks_obtained = db.Column(db.Float)
    total_marks = db.Column(db.Float)
    completion_date = db.Column(db.DateTime, default=datetime.utcnow)
    pdf_path = db.Column(db.String(300))
    qr_code_path = db.Column(db.String(300))
    is_valid = db.Column(db.Boolean, default=True)
    issued_by = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    course = db.relationship("Course", backref="certificates", lazy=True)


class VerificationLog(db.Model):
    __tablename__ = "verification_logs"
    id = db.Column(db.Integer, primary_key=True)
    cert_id = db.Column(db.String(50), nullable=False)
    verified_by = db.Column(db.String(100))
    ip_address = db.Column(db.String(50))
    status = db.Column(db.String(20))
    verified_at = db.Column(db.DateTime, default=datetime.utcnow)


class Exam(db.Model):
    __tablename__ = "exams"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"), nullable=False)
    duration_minutes = db.Column(db.Integer, nullable=False, default=60)
    total_questions = db.Column(db.Integer, nullable=False, default=0)
    passing_percentage = db.Column(db.Float, nullable=False, default=40)
    max_marks = db.Column(db.Float, nullable=False, default=100)
    is_published = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    course = db.relationship("Course", backref="exams", lazy=True)
    questions = db.relationship("Question", backref="exam", lazy=True, cascade="all, delete-orphan")
    results = db.relationship("ExamResult", backref="exam", lazy=True, cascade="all, delete-orphan")


class Question(db.Model):
    __tablename__ = "questions"
    id = db.Column(db.Integer, primary_key=True)
    exam_id = db.Column(db.Integer, db.ForeignKey("exams.id"), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    option_a = db.Column(db.String(300), nullable=False)
    option_b = db.Column(db.String(300), nullable=False)
    option_c = db.Column(db.String(300), nullable=False)
    option_d = db.Column(db.String(300), nullable=False)
    correct_answer = db.Column(db.String(1), nullable=False)
    marks = db.Column(db.Float, nullable=False, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class StudentAnswer(db.Model):
    __tablename__ = "student_answers"
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    exam_id = db.Column(db.Integer, db.ForeignKey("exams.id"), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey("questions.id"), nullable=False)
    selected_answer = db.Column(db.String(1))
    is_correct = db.Column(db.Boolean, default=False)
    answered_at = db.Column(db.DateTime, default=datetime.utcnow)
    student = db.relationship("Student", backref="answers", lazy=True)
    question = db.relationship("Question", backref="answers", lazy=True)


class ExamResult(db.Model):
    __tablename__ = "exam_results"
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    exam_id = db.Column(db.Integer, db.ForeignKey("exams.id"), nullable=False)
    score = db.Column(db.Float, nullable=False, default=0)
    percentage = db.Column(db.Float, nullable=False, default=0)
    total_marks = db.Column(db.Float, nullable=False, default=0)
    total_questions = db.Column(db.Integer, nullable=False, default=0)
    correct_answers = db.Column(db.Integer, nullable=False, default=0)
    passed = db.Column(db.Boolean, default=False)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    student = db.relationship("Student", backref="exam_results", lazy=True)
