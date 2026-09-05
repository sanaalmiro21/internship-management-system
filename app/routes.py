import os
import uuid
from werkzeug.utils import secure_filename
from flask import send_from_directory, current_app
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from .services import Student, db, register_user, authenticate_user
from datetime import datetime, timezone, date, timedelta
from . import db
from .models import Application, Company, Internship, InternshipListing, University, User, Document
ALLOWED_EXTENSIONS = {"pdf", "docx", "doc"}

main = Blueprint("main", __name__)

@main.route("/")
def index():
    return render_template("index.html")
@main.route("/register", methods=["GET", "POST"])
def register():
    # Fetch approved universities so students can select their institution
    approved_universities = University.query.join(User).filter(User.is_approved == True).all()

    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        role = request.form.get("role")
        
        # Grab university_id only if the role being registered is a student
        university_id = request.form.get("university_id") if role == 'Student' else None

        # Pass university_id (and other student fields if your function accepts them)
        user, msg = register_user(username, email, password, role, university_id=university_id)
        if not user:
            flash(msg, "danger")
            return redirect(url_for("main.register"))

        # Tailor the flash message based on whether approval is required
        if role in ["Company", "University"]:
            flash("Registration successful! Your account is pending Admin approval before you can log in.", "warning")
        else:
            flash("Registration successful! Please log in.", "success")
            
        return redirect(url_for("main.login"))

    return render_template("register.html", universities=approved_universities)

@main.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        identifier = request.form.get("identifier")
        password = request.form.get("password")

        user, msg = authenticate_user(identifier, password)
        if not user:
            flash(msg, "danger")
            return redirect(url_for("main.login"))

        if not user.is_approved and user.role in ["Company", "University"]:
            flash("Your account is pending admin approval.", "warning")
            return redirect(url_for("main.login"))

        session["user_id"] = user.user_id
        session["username"] = user.username
        session["role"] = user.role

        flash(f"Welcome back, {user.username}!", "success")
        return redirect(url_for("main.dashboard"))

    return render_template("login.html")

@main.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        flash("Please log in to access your dashboard.", "warning")
        return redirect(url_for("main.login"))

    role = session.get("role")

    if role == "Admin":
        return redirect(url_for("main.admin_dashboard"))

    elif role == "University":
        university = University.query.filter_by(university_id=session["user_id"]).first()
        students = Student.query.filter_by(university_id=session["user_id"]).all() if university else []
        return render_template(
            "university_dashboard.html",
            university=university,
            students=students,
            total_students=len(students)
        )

    elif role == "Company":
        company = Company.query.filter_by(company_id=session["user_id"]).first()
        listings = (
            InternshipListing.query.filter_by(company_id=session["user_id"])
            .order_by(InternshipListing.created_at.desc())
            .all()
            if company else []
        )
        
        applications = (
            Application.query.filter_by(company_id=session["user_id"])
            .order_by(Application.application_date.desc())
            .all()
            if company else []
        )

        pending_applicants = [a for a in applications if a.status == "Pending"]
        
        active_interns_count = Internship.query.join(Application).filter(
            Application.company_id == session["user_id"],
            Internship.status == "Ongoing"
        ).count()

        return render_template(
            "company_dashboard.html",
            company=company,
            listings=listings,
            total_listings=len(listings),
            applications=applications,
            pending_applicants_count=len(pending_applicants),
            active_interns_count=active_interns_count
        )

    elif role == "Student":
        student = Student.query.filter_by(student_id=session["user_id"]).first()
        applications = (
            Application.query.filter_by(student_id=session["user_id"])
            .order_by(Application.application_date.desc())
            .all()
        )
        
        # Query active ongoing internship placement
        active_placement = (
            Internship.query.filter_by(student_id=session["user_id"], status="Ongoing")
            .first()
        )

        return render_template(
            "student_dashboard.html",
            student=student,
            applications=applications,
            total_applications=len(applications),
            active_placement=active_placement
        )

    return render_template("dashboard.html")


@main.route("/applications/<int:app_id>/decide", methods=["POST"])
def decide_application(app_id):
    if "user_id" not in session or session.get("role") != "Company":
        flash("Unauthorized access.", "danger")
        return redirect(url_for("main.dashboard"))

    application = Application.query.get_or_404(app_id)

    if application.company_id != session["user_id"]:
        flash("You do not have permission to modify this application.", "danger")
        return redirect(url_for("main.dashboard"))

    action = request.form.get("action")

    if action == "accept":
        application.status = "Accepted"

        existing_internship = Internship.query.filter_by(application_id=application.application_id).first()
        if not existing_internship:
            start = date.today()
            end = start + timedelta(days=90)

            new_placement = Internship(
                application_id=application.application_id,
                student_id=application.student_id,
                title=application.position,
                description=f"Internship placement at {application.company.company_name}",
                start_date=start,
                end_date=end,
                status="Ongoing"
            )
            db.session.add(new_placement)

        flash(f"Candidate {application.student.first_name} {application.student.last_name} accepted! Formal placement initialized.", "success")

    elif action == "reject":
        application.status = "Rejected"
        flash(f"Application for {application.student.first_name} {application.student.last_name} rejected.", "info")

    db.session.commit()
    return redirect(url_for("main.dashboard"))


@main.route("/internships/create", methods=["GET", "POST"])
def create_internship():
    if "user_id" not in session or session.get("role") != "Company":
        flash("Unauthorized access. Only approved companies can post listings.", "danger")
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":
        title = request.form.get("title")
        department = request.form.get("department")
        location = request.form.get("location")
        description = request.form.get("description")
        requirements = request.form.get("requirements")

        if not title or not department or not location or not description:
            flash("Please fill in all required fields.", "danger")
            return redirect(url_for("main.create_internship"))

        new_listing = InternshipListing(
            company_id=session["user_id"],
            title=title.strip(),
            department=department.strip(),
            location=location.strip(),
            description=description.strip(),
            requirements=requirements.strip() if requirements else None
        )
        db.session.add(new_listing)
        db.session.commit()

        flash("Internship position published successfully!", "success")
        return redirect(url_for("main.dashboard"))

    return render_template("create_internship.html")

@main.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("main.login"))

@main.route('/admin/dashboard')
def admin_dashboard():
    # Security check using your custom session logic
    if session.get("role") != 'Admin':
        flash('Access denied. Administrator privileges required.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    # Fetch all users whose accounts are not yet approved
    pending_users = User.query.filter_by(is_approved=False).all()
    return render_template('admin_dashboard.html', pending_users=pending_users)


@main.route('/admin/approve/<int:user_id>', methods=['POST'])
def approve_user(user_id):
    # Security check using your custom session logic
    if session.get("role") != 'Admin':
        return redirect(url_for('main.dashboard'))
        
    # Find the user and update their status
    user = User.query.get_or_404(user_id)
    user.is_approved = True
    db.session.commit()
    
    flash(f'{user.role} account for {user.username} has been approved.', 'success')
    return redirect(url_for('main.admin_dashboard'))

@main.route('/admin/reject/<int:user_id>', methods=['POST'])
def reject_user(user_id):
    if session.get("role") != 'Admin':
        return redirect(url_for('main.dashboard'))
        
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    
    flash(f'{user.role} account for {user.username} has been rejected and removed.', 'danger')
    return redirect(url_for('main.admin_dashboard'))

# 1. Browse All Available Internships
@main.route("/internships")
def browse_internships():
    listings = InternshipListing.query.filter_by(is_active=True).order_by(InternshipListing.created_at.desc()).all()

    applied_listing_ids = []
    has_active_placement = False

    if session.get("role") == "Student" and "user_id" in session:
        applied_listing_ids = [
            app.listing_id for app in Application.query.filter_by(student_id=session["user_id"]).all()
        ]
        # Check if the student currently holds an ongoing placement
        has_active_placement = (
            Internship.query.filter_by(student_id=session["user_id"], status="Ongoing").first() is not None
        )

    return render_template(
        "browse_internships.html",
        listings=listings,
        applied_listing_ids=applied_listing_ids,
        has_active_placement=has_active_placement
    )


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@main.route("/internships/<int:listing_id>/apply", methods=["GET", "POST"])
def apply_internship(listing_id):
    if "user_id" not in session or session.get("role") != "Student":
        flash("Only enrolled students can apply for internships.", "danger")
        return redirect(url_for("main.browse_internships"))

    active_placement = Internship.query.filter_by(student_id=session["user_id"], status="Ongoing").first()
    if active_placement:
        flash("You cannot apply for new internships while you have an ongoing active placement.", "warning")
        return redirect(url_for("main.dashboard"))

    listing = InternshipListing.query.get_or_404(listing_id)

    existing_app = Application.query.filter_by(
        student_id=session["user_id"],
        listing_id=listing.listing_id
    ).first()
    if existing_app:
        flash("You have already applied for this position.", "warning")
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":
        cover_letter = request.form.get("cover_letter", "").strip()
        uploaded_file = request.files.get("resume")

        # 1. Create Application record first to obtain its ID
        new_application = Application(
            student_id=session["user_id"],
            company_id=listing.company_id,
            listing_id=listing.listing_id,
            position=listing.title,
            cover_letter=cover_letter,
            status="Pending"
        )
        db.session.add(new_application)
        db.session.flush()

        # 2. Process file attachment if provided
        if uploaded_file and uploaded_file.filename != "":
            if not allowed_file(uploaded_file.filename):
                db.session.rollback()
                flash("Invalid file format. Only PDF, DOC, and DOCX documents are accepted.", "danger")
                return redirect(url_for("main.apply_internship", listing_id=listing.listing_id))

            clean_filename = secure_filename(uploaded_file.filename)
            unique_filename = f"cv_usr{session['user_id']}_{uuid.uuid4().hex[:8]}_{clean_filename}"
            save_path = os.path.join(current_app.config["UPLOAD_FOLDER"], unique_filename)
            uploaded_file.save(save_path)

            doc_record = Document(
                user_id=session["user_id"],
                application_id=new_application.application_id,
                document_type="CV",
                file_path=unique_filename
            )
            db.session.add(doc_record)

        db.session.commit()
        flash(f"Application submitted successfully for {listing.title}!", "success")
        return redirect(url_for("main.dashboard"))

    return render_template("apply_internship.html", listing=listing)


@main.route("/documents/<int:document_id>/download")
def download_document(document_id):
    if "user_id" not in session:
        flash("Please sign in to access documents.", "warning")
        return redirect(url_for("main.login"))

    doc = Document.query.get_or_404(document_id)

    # Access control: Only document owner, target company, or an admin can access
    allowed = False
    if session.get("role") == "Admin":
        allowed = True
    elif doc.user_id == session.get("user_id"):
        allowed = True
    elif session.get("role") == "Company" and doc.application:
        if doc.application.company_id == session.get("user_id"):
            allowed = True

    if not allowed:
        flash("Unauthorized access to this document.", "danger")
        return redirect(url_for("main.dashboard"))

    return send_from_directory(
        current_app.config["UPLOAD_FOLDER"],
        doc.file_path,
        as_attachment=True
    )