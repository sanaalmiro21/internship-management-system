
from datetime import datetime, timezone, date
from sqlalchemy import UniqueConstraint
from . import db

class User(db.Model):
    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # student, company, university, admin
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    is_approved = db.Column(db.Boolean, default=False)
    
    # Subtype Relationships
    student_profile = db.relationship("Student", backref="user", uselist=False, cascade="all, delete-orphan")
    company_profile = db.relationship("Company", backref="user", uselist=False, cascade="all, delete-orphan")
    university_profile = db.relationship("University", backref="user", uselist=False, cascade="all, delete-orphan")
    admin_profile = db.relationship("Admin", backref="user", uselist=False, cascade="all, delete-orphan")

class University(db.Model):
    __tablename__ = "universities"

    university_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), primary_key=True)
    university_name = db.Column(db.String(150), nullable=False)
    department = db.Column(db.String(100), nullable=True)

    # Relationships
    students = db.relationship("Student", back_populates="university", lazy=True)
    supervisors = db.relationship("UniversitySupervisor", backref="university", lazy=True)
    evaluated_internships = db.relationship("Internship", back_populates="evaluator", lazy=True)


class Company(db.Model):
    __tablename__ = "companies"

    company_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), primary_key=True)
    company_name = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    website = db.Column(db.String(150), nullable=True)

    instructors = db.relationship("CompanyInstructor", backref="company", lazy=True)
    received_applications = db.relationship("Application", back_populates="company", lazy=True)
    company_internships = db.relationship("Internship", back_populates="company", lazy=True)


class Student(db.Model):
    __tablename__ = "students"

    student_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), primary_key=True)
    university_id = db.Column(db.Integer, db.ForeignKey("universities.university_id"), nullable=False)
    student_number = db.Column(db.String(30), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    department = db.Column(db.String(100), nullable=False)

    __table_args__ = (
        UniqueConstraint("university_id", "student_number", name="uq_student_university_number"),
    )

    # Relationships (Using clean back_populates pairs)
    university = db.relationship("University", back_populates="students")
    applications = db.relationship("Application", back_populates="student", lazy=True)
    internships = db.relationship("Internship", back_populates="student", lazy=True)

    @property
    def placement_status(self):
        # 1. Check for formal placement
        active_internship = next((i for i in self.internships if i.status in ["Ongoing", "Scheduled", "Approved"]), None)
        if active_internship:
            return f"Placed ({active_internship.status})"
        
        # 2. Check for offer
        has_offer = any(a.status == "Offered" for a in self.applications)
        if has_offer:
            return "Offer Received"

        # 3. Check for active application
        has_pending = any(a.status == "Pending" for a in self.applications)
        if has_pending:
            return "Applying"

        return "Enrolled"


class Application(db.Model):
    __tablename__ = "applications"

    application_id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.student_id"), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey("companies.company_id"), nullable=False)
    listing_id = db.Column(db.Integer, db.ForeignKey("internship_listings.listing_id"), nullable=False)
    
    position = db.Column(db.String(120), nullable=False)
    cover_letter = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default="Pending")  # 'Pending', 'Offered', 'Accepted', 'Rejected', 'Withdrawn'
    application_date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Explicit bidirectional relationships
    student = db.relationship("Student", back_populates="applications")
    company = db.relationship("Company", back_populates="received_applications")
    listing = db.relationship("InternshipListing", backref=db.backref("applications", lazy=True))
    internship = db.relationship("Internship", back_populates="application", uselist=False)


class Internship(db.Model):
    __tablename__ = "internships"

    internship_id = db.Column(db.Integer, primary_key=True)
    
    application_id = db.Column(db.Integer, db.ForeignKey("applications.application_id"), nullable=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.student_id"), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey("companies.company_id"), nullable=False)
    listing_id = db.Column(db.Integer, db.ForeignKey("internship_listings.listing_id"), nullable=True)

    # Duration & Hours Tracking
    start_date = db.Column(db.Date, nullable=False, default=date.today)
    end_date = db.Column(db.Date, nullable=False)
    required_hours = db.Column(db.Float, default=240.0, nullable=False)

    # Lifecycle: 'Scheduled', 'Ongoing', 'Pending Evaluation', 'Approved', 'Rejected'
    status = db.Column(db.String(30), default="Ongoing", nullable=False)

    # University Final Academic Evaluation
    grade = db.Column(db.String(20), nullable=True)
    evaluation_notes = db.Column(db.Text, nullable=True)
    evaluated_by = db.Column(db.Integer, db.ForeignKey("universities.university_id"), nullable=True)
    evaluated_at = db.Column(db.DateTime, nullable=True)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships matched to their explicit pairs
    application = db.relationship("Application", back_populates="internship")
    student = db.relationship("Student", back_populates="internships")
    company = db.relationship("Company", back_populates="company_internships")
    evaluator = db.relationship("University", back_populates="evaluated_internships")
    listing = db.relationship("InternshipListing", backref=db.backref("associated_internships", lazy=True))

class Admin(db.Model):
    __tablename__ = "admins"

    admin_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    admin_level = db.Column(db.String(30), default="Standard")


class CompanyInstructor(db.Model):
    __tablename__ = "company_instructors"

    instructor_id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey("companies.company_id"), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    position = db.Column(db.String(80), nullable=False)
    phone = db.Column(db.String(30), nullable=True)

    evaluations = db.relationship("Evaluation", backref="instructor", lazy=True)


class UniversitySupervisor(db.Model):
    __tablename__ = "university_supervisors"

    supervisor_id = db.Column(db.Integer, primary_key=True)
    university_id = db.Column(db.Integer, db.ForeignKey("universities.university_id"), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    position = db.Column(db.String(80), nullable=False)
    phone = db.Column(db.String(30), nullable=True)

    evaluations = db.relationship("Evaluation", backref="supervisor", lazy=True)


class LogbookEntry(db.Model):
    __tablename__ = "logbook_entries"

    entry_id = db.Column(db.Integer, primary_key=True)
    internship_id = db.Column(db.Integer, db.ForeignKey("internships.internship_id"), nullable=False)
    
    # Work day tracking
    entry_date = db.Column(db.Date, nullable=False)
    hours_worked = db.Column(db.Float, nullable=False, default=8.0)
    tasks_performed = db.Column(db.Text, nullable=False)
    learnings = db.Column(db.Text, nullable=True)

    # Supervisor Review: 'Pending', 'Approved', 'Needs Revision'
    status = db.Column(db.String(20), default="Pending", nullable=False)
    supervisor_feedback = db.Column(db.Text, nullable=True)
    reviewed_at = db.Column(db.DateTime, nullable=True)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationship
    internship = db.relationship("Internship", backref=db.backref("logbook_entries", cascade="all, delete-orphan", lazy=True))

    # Constraint: one log entry per calendar day per internship
    __table_args__ = (
        db.UniqueConstraint("internship_id", "entry_date", name="uq_internship_entry_date"),
    )



class Evaluation(db.Model):
    __tablename__ = "evaluations"

    evaluation_id = db.Column(db.Integer, primary_key=True)
    internship_id = db.Column(db.Integer, db.ForeignKey("internships.internship_id"), nullable=False)
    instructor_id = db.Column(db.Integer, db.ForeignKey("company_instructors.instructor_id"), nullable=True)
    supervisor_id = db.Column(db.Integer, db.ForeignKey("university_supervisors.supervisor_id"), nullable=True)
    score = db.Column(db.Float, nullable=False)
    comment = db.Column(db.Text, nullable=True)
    evaluation_date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    evaluation_type = db.Column(db.String(50), nullable=False)  # Company, University

class InternshipListing(db.Model):
    __tablename__ = "internship_listings"

    listing_id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey("companies.company_id"), nullable=False)
    title = db.Column(db.String(120), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(120), nullable=False)  # e.g., Remote, Istanbul, On-Site
    description = db.Column(db.Text, nullable=False)
    requirements = db.Column(db.Text, nullable=True)

    # Predefined Placement Duration & Requirement
    start_date = db.Column(db.Date, nullable=False, default=date.today)
    end_date = db.Column(db.Date, nullable=False)
    required_hours = db.Column(db.Float, default=240.0, nullable=False)

    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationship to Company
    company = db.relationship("Company", backref=db.backref("listings", lazy=True, cascade="all, delete-orphan"))

class Document(db.Model):
    __tablename__ = "documents"

    document_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    application_id = db.Column(db.Integer, db.ForeignKey("applications.application_id"), nullable=True)
    internship_id = db.Column(db.Integer, db.ForeignKey("internships.internship_id"), nullable=True)
    document_type = db.Column(db.String(50), nullable=False)  # CV, Agreement, Evaluation, Report
    file_path = db.Column(db.String(255), nullable=False)
    upload_date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # User & Application relationships
    user = db.relationship("User", backref="documents")
    application = db.relationship("Application", backref=db.backref("documents", lazy=True))
    # (Notice: No 'internship = ...' here, because Internship defines the backref)