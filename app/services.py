from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from .models import User, Student, Company, Application, Internship, Evaluation, University

# --- Authentication Services ---

def register_user(username, email, password, role):
    # Check if user already exists
    existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
    if existing_user:
        return None, "Username or email already exists."

    hashed_password = generate_password_hash(password)
    
    # FIX: Companies and Universities must start unapproved (False)
    is_approved_status = True if role == 'Student' else False

    new_user = User(
        username=username,
        email=email,
        password=hashed_password,
        role=role,
        is_approved=is_approved_status
    )
    
    db.session.add(new_user)
    db.session.commit()
    return new_user, "Registration successful."

def authenticate_user(email, password):
    """Verify user credentials against stored password hash."""
    user = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.password, password):
        return user
    return None

# --- Application & Query Services ---

def get_student_by_user_id(user_id):
    """Retrieve student profile by user ID."""
    return Student.query.get(user_id)

def get_company_by_user_id(user_id):
    """Retrieve company profile by user ID."""
    return Company.query.get(user_id)

def get_all_companies():
    """Retrieve list of all registered companies."""
    return Company.query.all()

def get_student_applications(student_id):
    """Retrieve all applications submitted by a specific student."""
    return Application.query.filter_by(student_id=student_id).order_by(Application.application_date.desc()).all()

def get_company_applications(company_id):
    """Retrieve all applications received by a specific company."""
    return Application.query.filter_by(company_id=company_id).order_by(Application.application_date.desc()).all()

def create_application(student_id, company_id, position, cover_letter=""):
    """Create a new internship application."""
    application = Application(
        student_id=student_id,
        company_id=company_id,
        position=position,
        cover_letter=cover_letter,
        status="Pending"
    )
    db.session.add(application)
    db.session.commit()
    return application

def update_application_status(application_id, new_status):
    """Update status of an application (Accepted/Rejected)."""
    app_record = Application.query.get(application_id)
    if app_record and new_status in ["Accepted", "Rejected", "Pending"]:
        app_record.status = new_status
        db.session.commit()
        return app_record
    return None