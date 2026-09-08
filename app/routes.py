import os
import uuid
from werkzeug.utils import secure_filename
from flask import send_from_directory, current_app
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from .services import Student, db, register_user, authenticate_user
from datetime import datetime, timezone, date, timedelta
from . import db
from .models import Application, Company, Internship, InternshipListing, University, User, Document, LogbookEntry
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
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        role = request.form.get("role")

        # Collect role-specific profile data
        profile_data = {}

        if role == "Student":
            profile_data = {
                "student_number": request.form.get("student_number", "").strip(),
                "first_name": request.form.get("first_name", "").strip(),
                "last_name": request.form.get("last_name", "").strip(),
                "department": request.form.get("department", "").strip(),
                "university_id": request.form.get("university_id")
            }
        elif role == "Company":
            profile_data = {
                "company_name": request.form.get("company_name", "").strip(),
                "address": request.form.get("address", "").strip(),
                "website": request.form.get("website", "").strip()
            }
        elif role == "University":
            profile_data = {
                "university_name": request.form.get("university_name", "").strip(),
                "department": request.form.get("uni_department", "").strip() or None
            }

        # Delegate account creation and uniqueness checks to services
        success, msg = register_user(username, email, password, role, profile_data=profile_data)
        if not success:
            flash(msg, "danger")
            return redirect(url_for("main.register"))

        # Tailor flash message based on approval requirement
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
@main.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        flash("Please log in to access your dashboard.", "warning")
        return redirect(url_for("main.login"))

    user_id = session["user_id"]
    role = session.get("role")

    if role == "Admin":
        return redirect(url_for("main.admin_dashboard"))

    elif role == "University":
        university = University.query.filter_by(university_id=user_id).first()
        students = Student.query.filter_by(university_id=user_id).all() if university else []
        student_ids = [s.student_id for s in students]

        # Fetch all internships for students of this university
        uni_internships = (
            Internship.query.filter(Internship.student_id.in_(student_ids))
            .order_by(Internship.created_at.desc())
            .all()
            if student_ids else []
        )

        approved_placements_count = sum(1 for i in uni_internships if i.status == "Approved")
        pending_evaluations_count = sum(1 for i in uni_internships if i.status == "Pending Evaluation")

        return render_template(
            "university_dashboard.html",
            university=university,
            students=students,
            uni_internships=uni_internships,
            total_students=len(students),
            approved_placements_count=approved_placements_count,
            pending_evaluations_count=pending_evaluations_count
        )

    elif role == "Company":
        company = Company.query.filter_by(company_id=user_id).first()
        
        listings = (
            InternshipListing.query.filter_by(company_id=user_id)
            .order_by(InternshipListing.created_at.desc())
            .all()
            if company else []
        )
        
        applications = (
            Application.query.filter_by(company_id=user_id)
            .order_by(Application.application_date.desc())
            .all()
            if company else []
        )

        # Internships assigned to this company (for the logbook review table)
        company_internships = (
            Internship.query.filter_by(company_id=user_id)
            .order_by(Internship.created_at.desc())
            .all()
            if company else []
        )

        pending_applicants = [a for a in applications if a.status == "Pending"]
        active_interns_count = sum(1 for i in company_internships if i.status == "Ongoing")

        return render_template(
            "company_dashboard.html",
            company=company,
            listings=listings,
            total_listings=len(listings),
            applications=applications,
            pending_applicants_count=len(pending_applicants),
            company_internships=company_internships,
            active_interns_count=active_interns_count
        )

    elif role == "Student":
        student = Student.query.filter_by(student_id=user_id).first()
        applications = (
            Application.query.filter_by(student_id=user_id)
            .order_by(Application.application_date.desc())
            .all()
            if student else []
        )

        # Offers awaiting student decision
        offers = [a for a in applications if a.status == "Offered"]

        # Active or scheduled placement
        active_internship = (
            Internship.query.filter(
                Internship.student_id == user_id,
                Internship.status.in_(["Scheduled", "Ongoing", "Pending Evaluation", "Approved"])
            )
            .order_by(Internship.created_at.desc())
            .first()
            if student else None
        )

        # Sum of supervisor-approved hours
        approved_hours_total = 0
        if active_internship:
            approved_hours_total = sum(
                entry.hours_worked for entry in active_internship.logbook_entries if entry.status == "Approved"
            )

        return render_template(
            "student_dashboard.html",
            student=student,
            applications=applications,
            offers=offers,
            total_applications=len(applications),
            active_internship=active_internship,
            active_placement=active_internship,
            approved_hours_total=approved_hours_total
        )

    return render_template("dashboard.html")

@main.route("/application/<int:app_id>/decide", methods=["POST"])
def decide_application(app_id):
    if "user_id" not in session or session.get("role") != "Company":
        flash("Unauthorized access.", "danger")
        return redirect(url_for("main.dashboard"))

    application = Application.query.get_or_404(app_id)

    # Validate company ownership
    if application.company_id != session["user_id"]:
        flash("You do not have permission to modify this application.", "danger")
        return redirect(url_for("main.dashboard"))

    action = request.form.get("action")

    if action == "accept":
        # Check if the candidate has already committed to another placement
        active_placement = Internship.query.filter(
            Internship.student_id == application.student_id,
            Internship.status.in_(["Ongoing", "Scheduled", "Pending Evaluation", "Approved"])
        ).first()

        if active_placement:
            flash(f"Candidate {application.student.first_name} has already finalized another placement.", "warning")
            return redirect(url_for("main.dashboard"))

        # Transition application to 'Offered'
        application.status = "Offered"

        flash(
            f"Offer extended to {application.student.first_name} {application.student.last_name}. "
            "Placement will initialize once the student accepts the offer.",
            "success"
        )

    elif action == "reject":
        application.status = "Rejected"
        flash(f"Application for {application.student.first_name} {application.student.last_name} rejected.", "info")

    else:
        flash("Invalid decision action.", "danger")
        return redirect(url_for("main.dashboard"))

    db.session.commit()
    return redirect(url_for("main.dashboard"))

@main.route("/application/<int:app_id>/accept-offer", methods=["POST"])
def accept_offer(app_id):
    if "user_id" not in session or session.get("role") != "Student":
        flash("Unauthorized action.", "danger")
        return redirect(url_for("main.login"))

    student_id = session["user_id"]
    chosen_app = Application.query.get_or_404(app_id)

    if chosen_app.student_id != student_id or chosen_app.status != "Offered":
        flash("Invalid offer selection.", "danger")
        return redirect(url_for("main.dashboard"))

    # Guard: check if student already has an active placement
    existing_placement = Internship.query.filter(
        Internship.student_id == student_id,
        Internship.status.in_(["Ongoing", "Scheduled", "Pending Evaluation", "Approved"])
    ).first()

    if existing_placement:
        flash("You already have an active internship commitment.", "warning")
        return redirect(url_for("main.dashboard"))

    listing = chosen_app.listing
    today = date.today()

    # Determine status: "Scheduled" if start_date is in the future, otherwise "Ongoing"
    initial_status = "Scheduled" if listing.start_date and listing.start_date > today else "Ongoing"

    # Create official Internship inheriting predefined listing dates
    internship = Internship(
        application_id=chosen_app.application_id,
        student_id=student_id,
        company_id=listing.company_id,
        listing_id=listing.listing_id,
        start_date=listing.start_date or today,
        end_date=listing.end_date,
        required_hours=listing.required_hours or 240.0,
        status=initial_status
    )
    db.session.add(internship)

    # Mark this application as Accepted
    chosen_app.status = "Accepted"
    # Note: chosen_app.student.placement_status is computed dynamically via @property

    # Auto-withdraw any other pending or offered applications for this student
    other_apps = Application.query.filter(
        Application.student_id == student_id,
        Application.application_id != chosen_app.application_id,
        Application.status.in_(["Pending", "Offered"])
    ).all()

    for other in other_apps:
        other.status = "Withdrawn"

    db.session.commit()

    flash(f"Congratulations! You accepted the offer from {chosen_app.company.company_name}. Placement scheduled!", "success")
    return redirect(url_for("main.logbook", internship_id=internship.internship_id))

from datetime import datetime, date

@main.route("/internship/create", methods=["GET", "POST"])
def create_internship():
    if "user_id" not in session or session.get("role") != "Company":
        flash("Unauthorized access.", "danger")
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":
        title = request.form.get("title")
        department = request.form.get("department")
        location = request.form.get("location")
        description = request.form.get("description")
        requirements = request.form.get("requirements")

        # Parse term dates & hours
        raw_start = request.form.get("start_date")
        raw_end = request.form.get("end_date")
        raw_hours = request.form.get("required_hours")

        start_date = datetime.strptime(raw_start, "%Y-%m-%d").date() if raw_start else date.today()
        end_date = datetime.strptime(raw_end, "%Y-%m-%d").date() if raw_end else (date.today())
        required_hours = float(raw_hours) if raw_hours else 240.0

        if end_date <= start_date:
            flash("End date must be after start date.", "danger")
            return redirect(request.url)

        new_listing = InternshipListing(
            company_id=session["user_id"],
            title=title,
            department=department,
            location=location,
            description=description,
            requirements=requirements,
            start_date=start_date,
            end_date=end_date,
            required_hours=required_hours
        )
        db.session.add(new_listing)
        db.session.commit()

        flash("Internship listing created successfully!", "success")
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

    # Block if student already has an ongoing placement
    active_placement = Internship.query.filter_by(student_id=session["user_id"], status="Ongoing").first()
    if active_placement:
        flash("You cannot apply for new internships while you have an ongoing active placement.", "warning")
        return redirect(url_for("main.dashboard"))

    listing = InternshipListing.query.get_or_404(listing_id)

    # Check if the listing is closed
    if not listing.is_active:
        flash("This position has been closed and is no longer accepting applications.", "warning")
        return redirect(url_for("main.browse_internships"))

    # Block duplicate submissions
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



@main.route("/listing/<int:listing_id>/toggle", methods=["POST"])
def toggle_listing_status(listing_id):
    if "user_id" not in session:
        return redirect(url_for("main.login"))

    listing = InternshipListing.query.get_or_404(listing_id)

    # Allow only the posting Company or an Admin
    if session.get("role") != "Admin" and listing.company_id != session.get("user_id"):
        flash("You are not authorized to update this listing.", "danger")
        return redirect(url_for("main.dashboard"))

    listing.is_active = not listing.is_active
    db.session.commit()

    status_str = "reopened" if listing.is_active else "closed"
    flash(f"Listing '{listing.title}' has been {status_str}.", "success")
    return redirect(request.referrer or url_for("main.dashboard"))


@main.route("/listing/<int:listing_id>/delete", methods=["POST"])
def delete_listing(listing_id):
    if "user_id" not in session:
        return redirect(url_for("main.login"))

    listing = InternshipListing.query.get_or_404(listing_id)

    # Allow only the posting Company or an Admin
    if session.get("role") != "Admin" and listing.company_id != session.get("user_id"):
        flash("You are not authorized to delete this listing.", "danger")
        return redirect(url_for("main.dashboard"))

    try:
        db.session.delete(listing)
        db.session.commit()
        flash(f"Listing '{listing.title}' was deleted permanently.", "success")
    except Exception:
        db.session.rollback()
        flash("Could not delete listing due to existing applications. Consider closing it instead.", "warning")

    return redirect(request.referrer or url_for("main.dashboard"))

# 14-day grace period after end_date for retroactive logging, reviews, and sign-offs
SUBMISSION_GRACE_PERIOD_DAYS = 14


# 1. VIEW LOGBOOK & HANDLE STUDENT DAILY SUBMISSIONS
@main.route("/internship/<int:internship_id>/logbook", methods=["GET", "POST"])
def logbook(internship_id):
    if "user_id" not in session:
        return redirect(url_for("main.login"))

    user_id = session["user_id"]
    role = session.get("role")
    internship = Internship.query.get_or_404(internship_id)

    # Permission check: Student owner, Company host, University coordinator, or Admin
    is_student = (role == "Student" and internship.student_id == user_id)
    is_company = (role == "Company" and internship.company_id == user_id)
    is_uni = (role == "University" and internship.student.university_id == user_id)
    is_admin = (role == "Admin")

    if not (is_student or is_company or is_uni or is_admin):
        flash("You are not authorized to view this internship logbook.", "danger")
        return redirect(url_for("main.dashboard"))

    grace_deadline = internship.end_date + timedelta(days=SUBMISSION_GRACE_PERIOD_DAYS)
    is_submission_window_open = (date.today() <= grace_deadline)

    # --- Student Submission (Daily or Retroactive) ---
    if request.method == "POST":
        if not is_student:
            flash("Only the enrolled student can submit daily logs.", "danger")
            return redirect(url_for("main.logbook", internship_id=internship_id))

        if internship.status != "Ongoing":
            flash(f"Cannot submit entries: Internship status is '{internship.status}'.", "warning")
            return redirect(url_for("main.logbook", internship_id=internship_id))

        if not is_submission_window_open:
            flash(f"The submission grace period expired on {grace_deadline.strftime('%b %d, %Y')}. Logbook is locked.", "danger")
            return redirect(url_for("main.logbook", internship_id=internship_id))

        raw_date = request.form.get("entry_date")
        raw_hours = request.form.get("hours_worked", 8.0)
        tasks = request.form.get("tasks_performed", "").strip()
        learnings = request.form.get("learnings", "").strip()

        try:
            entry_date = datetime.strptime(raw_date, "%Y-%m-%d").date()
            hours_worked = float(raw_hours)
        except (ValueError, TypeError):
            flash("Invalid date or hours format provided.", "danger")
            return redirect(url_for("main.logbook", internship_id=internship_id))

        # Date validations
        if entry_date < internship.start_date:
            flash(f"Work date cannot precede the internship start date ({internship.start_date}).", "danger")
            return redirect(url_for("main.logbook", internship_id=internship_id))

        if entry_date > internship.end_date:
            flash(f"Work date cannot exceed the official placement end date ({internship.end_date}).", "danger")
            return redirect(url_for("main.logbook", internship_id=internship_id))

        if entry_date > date.today():
            flash("You cannot log work for future calendar dates.", "danger")
            return redirect(url_for("main.logbook", internship_id=internship_id))

        if hours_worked <= 0 or hours_worked > 12:
            flash("Logged work hours per day must be between 0.5 and 12.0.", "danger")
            return redirect(url_for("main.logbook", internship_id=internship_id))

        # Check for existing entry on this date
        existing_entry = LogbookEntry.query.filter_by(
            internship_id=internship.internship_id,
            entry_date=entry_date
        ).first()

        if existing_entry:
            # If flagged by supervisor for revision, allow in-place edit & reset to Pending
            if existing_entry.status == "Needs Revision":
                existing_entry.hours_worked = hours_worked
                existing_entry.tasks_performed = tasks
                existing_entry.learnings = learnings if learnings else None
                existing_entry.status = "Pending"
                db.session.commit()
                flash(f"Entry for {entry_date} revised and resubmitted for supervisor approval.", "success")
                return redirect(url_for("main.logbook", internship_id=internship_id))
            else:
                flash(f"An entry for {entry_date} already exists (Status: {existing_entry.status}).", "warning")
                return redirect(url_for("main.logbook", internship_id=internship_id))

        # Create new logbook entry
        new_entry = LogbookEntry(
            internship_id=internship.internship_id,
            entry_date=entry_date,
            hours_worked=hours_worked,
            tasks_performed=tasks,
            learnings=learnings if learnings else None,
            status="Pending"
        )
        db.session.add(new_entry)
        db.session.commit()
        flash(f"Work entry for {entry_date} logged successfully.", "success")
        return redirect(url_for("main.logbook", internship_id=internship_id))

    # --- GET Display ---
    entries = LogbookEntry.query.filter_by(internship_id=internship_id).order_by(LogbookEntry.entry_date.desc()).all()
    approved_hours = sum(e.hours_worked for e in entries if e.status == "Approved")
    progress_pct = min(100, int((approved_hours / internship.required_hours) * 100)) if internship.required_hours else 0

    # Max date selectable in the calendar input: min(today, end_date)
    max_selectable_date = min(date.today(), internship.end_date).isoformat()

    return render_template(
        "logbook.html",
        internship=internship,
        entries=entries,
        approved_hours=approved_hours,
        progress_pct=progress_pct,
        today_date=date.today().isoformat(),
        max_selectable_date=max_selectable_date,
        grace_deadline=grace_deadline,
        is_submission_window_open=is_submission_window_open
    )

# 2. COMPANY SUPERVISOR: APPROVE / REQUEST REVISION ON AN ENTRY
@main.route("/logbook/entry/<int:entry_id>/review", methods=["POST"])
def review_logbook_entry(entry_id):
    if "user_id" not in session or session.get("role") not in ["Company", "Admin"]:
        flash("Unauthorized action.", "danger")
        return redirect(url_for("main.dashboard"))

    entry = LogbookEntry.query.get_or_404(entry_id)

    # Verify company ownership
    if session.get("role") != "Admin" and entry.internship.company_id != session.get("user_id"):
        flash("You are not authorized to review entries for this candidate.", "danger")
        return redirect(url_for("main.dashboard"))

    # GUARD: Lock approved entries permanently from further review actions
    if entry.status == "Approved":
        flash(f"Entry for {entry.entry_date} is already approved and locked against further revisions.", "warning")
        return redirect(url_for("main.logbook", internship_id=entry.internship_id))

    status = request.form.get("status")
    feedback = request.form.get("feedback", "").strip()

    if status not in ["Approved", "Needs Revision"]:
        flash("Invalid review decision status.", "danger")
        return redirect(url_for("main.logbook", internship_id=entry.internship_id))

    entry.status = status
    entry.supervisor_feedback = feedback if feedback else None
    entry.reviewed_at = datetime.now(timezone.utc)
    db.session.commit()

    flash(f"Entry for {entry.entry_date} marked as '{status}'.", "success")
    return redirect(url_for("main.logbook", internship_id=entry.internship_id))

# 3. STUDENT: SUBMIT INTERNSHIP TO UNIVERSITY FOR FINAL EVALUATION
@main.route("/internship/<int:internship_id>/submit-final", methods=["POST"])
def submit_final_internship(internship_id):
    if "user_id" not in session:
        return redirect(url_for("main.login"))

    internship = Internship.query.get_or_404(internship_id)

    if session.get("role") != "Student" or internship.student_id != session.get("user_id"):
        flash("Unauthorized action.", "danger")
        return redirect(url_for("main.dashboard"))

    if internship.status != "Ongoing":
        flash(f"Cannot submit: Internship status is '{internship.status}'.", "warning")
        return redirect(url_for("main.logbook", internship_id=internship.internship_id))

    internship.status = "Pending Evaluation"
    db.session.commit()
    flash("Internship completed and submitted to your university coordinator for academic grading.", "success")
    return redirect(url_for("main.logbook", internship_id=internship.internship_id))


# 4. UNIVERSITY: RECORD ACADEMIC EVALUATION & GRADE
@main.route("/internship/<int:internship_id>/evaluate", methods=["POST"])
def evaluate_internship(internship_id):
    if "user_id" not in session or session.get("role") not in ["University", "Admin"]:
        flash("Unauthorized access.", "danger")
        return redirect(url_for("main.dashboard"))

    internship = Internship.query.get_or_404(internship_id)

    # Calculate total verified hours
    approved_hours = sum(
        e.hours_worked for e in internship.logbook_entries if e.status == "Approved"
    )
    required_hours = internship.required_hours or 240.0

    # Guard 1: Verify the placement status or submission state
    # If the student has not formally submitted for evaluation, block grading
    if internship.status not in ["Pending Evaluation", "Completed"]:
        # Guard 2: Alternatively check date and hour completion
        if date.today() < internship.end_date:
            flash(
                f"Cannot evaluate early: Internship is active until {internship.end_date.strftime('%b %d, %Y')}.",
                "warning",
            )
            return redirect(url_for("main.logbook", internship_id=internship_id))

        if approved_hours < required_hours:
            flash(
                f"Cannot evaluate: Student has completed {approved_hours}/{required_hours} approved hours.",
                "warning",
            )
            return redirect(url_for("main.logbook", internship_id=internship_id))

    decision = request.form.get("decision")
    grade = request.form.get("grade", "").strip()
    notes = request.form.get("notes", "").strip()

    if decision not in ["Approved", "Rejected"]:
        flash("Invalid decision.", "danger")
        return redirect(url_for("main.logbook", internship_id=internship_id))

    internship.status = decision  # Sets to Approved (Passed) or Rejected
    internship.grade = grade
    internship.evaluation_notes = notes
    internship.evaluated_at = date.today()

    db.session.commit()
    flash(f"Academic evaluation submitted: {decision} ({grade}).", "success")
    return redirect(url_for("main.logbook", internship_id=internship_id))


@main.route("/internship/<int:internship_id>/report")
def internship_report(internship_id):
    if "user_id" not in session:
        return redirect(url_for("main.login"))

    user_id = session["user_id"]
    role = session.get("role")
    internship = Internship.query.get_or_404(internship_id)

    # Authorization check
    is_student = (role == "Student" and internship.student_id == user_id)
    is_company = (role == "Company" and internship.company_id == user_id)
    is_uni = (role == "University" and getattr(internship.student, "university_id", None) == user_id)
    is_admin = (role == "Admin")

    if not (is_student or is_company or is_uni or is_admin):
        flash("You are not authorized to view this internship dossier.", "danger")
        return redirect(url_for("main.dashboard"))

    # Gather approved log entries in chronological order
    approved_entries = LogbookEntry.query.filter_by(
        internship_id=internship.internship_id,
        status="Approved"
    ).order_by(LogbookEntry.entry_date.asc()).all()

    total_approved_hours = sum(entry.hours_worked for entry in approved_entries)
    required_hours = internship.required_hours or 240.0

    return render_template(
        "internship_report.html",
        internship=internship,
        approved_entries=approved_entries,
        total_approved_hours=total_approved_hours,
        required_hours=required_hours,
        generated_date=date.today()
    )