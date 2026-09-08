from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from .models import Admin, User, Student, Company, Application, Internship, Evaluation, University

# --- Authentication Services ---

def register_user(username, email, password, role, profile_data=None, university_id=None):
    if profile_data is None:
        profile_data = {}

    # Support university_id if passed as a standalone argument
    if university_id and "university_id" not in profile_data:
        profile_data["university_id"] = university_id

    # 1. Check for duplicate username or email
    existing_user = User.query.filter(
        (User.username == username) | (User.email == email)
    ).first()
    if existing_user:
        return None, "Username or email already exists."

    # 2. Validate Student fields before creating User record
    if role == "Student":
        student_num = profile_data.get("student_number", "").strip()
        uni_id = profile_data.get("university_id")

        if not student_num:
            return None, "Official student number is required."

        if not uni_id:
            return None, "Affiliated university is required."

        # Verify composite uniqueness: student number must be unique per university
        existing_student = Student.query.filter_by(
            university_id=int(uni_id),
            student_number=student_num
        ).first()

        if existing_student:
            return None, f"Student number '{student_num}' is already registered for this institution."

    # 3. Create core User record
    hashed_password = generate_password_hash(password)
    is_approved_status = True if role == "Student" else False

    new_user = User(
        username=username,
        email=email,
        password=hashed_password,
        role=role,
        is_approved=is_approved_status
    )
    db.session.add(new_user)
    db.session.flush()

    # 4. Create child role profile records
    if role == "Student":
        student_profile = Student(
            student_id=new_user.user_id,
            university_id=int(profile_data["university_id"]),
            student_number=profile_data["student_number"].strip(),
            first_name=profile_data.get("first_name", username).strip(),
            last_name=profile_data.get("last_name", "Student").strip(),
            department=profile_data.get("department", "Engineering").strip()
        )
        db.session.add(student_profile)

    elif role == "Company":
        company_name = profile_data.get("company_name", username).strip()
        address = profile_data.get("address", "").strip()
        website = profile_data.get("website", "").strip() or None

        # Address cannot be null or empty
        if not address:
            address = "Pending Setup"

        company_profile = Company(
            company_id=new_user.user_id,
            company_name=company_name,
            address=address,
            website=website
        )
        db.session.add(company_profile)

    elif role == "University":
        uni_name = profile_data.get("university_name", "").strip()
        if not uni_name:
            uni_name = username  # Fallback to username if name is left blank

        dept = profile_data.get("department")
        if dept:
            dept = dept.strip()

        university_profile = University(
            university_id=new_user.user_id,
            university_name=uni_name,
            department=dept
        )
        db.session.add(university_profile)

    elif role == "Admin":
        admin_profile = Admin(
            admin_id=new_user.user_id,
            first_name=username,
            last_name="Administrator",
            admin_level="Standard"
        )
        db.session.add(admin_profile)

    db.session.commit()
    return new_user, "Registration successful."

def authenticate_user(identifier, password):
    # Query matching either email or username
    user = User.query.filter(
        (User.email == identifier) | (User.username == identifier)
    ).first()

    if not user or not check_password_hash(user.password, password):
        return None, "Invalid email/username or password."

    return user, "Authentication successful."
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