from datetime import datetime, timezone
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


class Student(db.Model):
    __tablename__ = "students"

    student_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), primary_key=True)
    university_id = db.Column(db.Integer, db.ForeignKey("universities.university_id"), nullable=False)
    student_number = db.Column(db.String(30), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    department = db.Column(db.String(100), nullable=False)

    # Relationships
    applications = db.relationship("Application", backref="student", lazy=True)
    internships = db.relationship("Internship", backref="student", lazy=True)
    university = db.relationship("University", back_populates="students")

    @property
    def placement_status(self):
        # 1. Check for formal placement
        active_internship = next((i for i in self.internships if i.status in ["Ongoing", "Completed"]), None)
        if active_internship:
            return f"Placed ({active_internship.status})"
        
        # 2. Check for application activity
        has_pending = any(a.status == "Pending" for a in self.applications)
        if has_pending:
            return "Applying"

        has_accepted = any(a.status == "Accepted" for a in self.applications)
        if has_accepted:
            return "Offer Received"

        return "Enrolled"

class Company(db.Model):
    __tablename__ = "companies"

    company_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), primary_key=True)
    company_name = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    website = db.Column(db.String(150), nullable=True)

    instructors = db.relationship("CompanyInstructor", backref="company", lazy=True)
    applications = db.relationship("Application", backref="company", lazy=True)


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


class Application(db.Model):
    __tablename__ = "applications"

    application_id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.student_id"), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey("companies.company_id"), nullable=False)
    listing_id = db.Column(db.Integer, db.ForeignKey("internship_listings.listing_id"), nullable=True)  # Links application to the specific post
    application_date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    status = db.Column(db.String(30), default="Pending")  # Pending, Accepted, Rejected
    position = db.Column(db.String(80), nullable=False)
    cover_letter = db.Column(db.Text, nullable=True)

    internship = db.relationship("Internship", backref="application", uselist=False)
    listing = db.relationship("InternshipListing", backref=db.backref("applications", lazy=True))


class Internship(db.Model):
    __tablename__ = "internships"

    internship_id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey("applications.application_id"), unique=True, nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey("students.student_id"), nullable=False)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=True)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(30), default="Ongoing")  # Ongoing, Completed, Terminated

    documents = db.relationship("Document", backref="internship", lazy=True)
    evaluations = db.relationship("Evaluation", backref="internship", lazy=True)




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