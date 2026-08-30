from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from .services import db, register_user, authenticate_user
from . import db
from .models import User
main = Blueprint("main", __name__)

@main.route("/")
def index():
    return render_template("index.html")

@main.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        role = request.form.get("role")

        user, msg = register_user(username, email, password, role)
        if not user:
            flash(msg, "danger")
            return redirect(url_for("main.register"))

        # Tailor the flash message based on whether approval is required
        if role in ["Company", "University"]:
            flash("Registration successful! Your account is pending Admin approval before you can log in.", "warning")
        else:
            flash("Registration successful! Please log in.", "success")
            
        return redirect(url_for("main.login"))

    return render_template("register.html")

@main.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = authenticate_user(email, password)
        if user:
            # EXACT PLACEMENT: Check approval status before creating the session
            if not user.is_approved and user.role in ["Company", "University"]:
                flash("Your account is pending Admin approval.", "warning")
                return redirect(url_for("main.login"))

            # If approved (or if they are a Student/Admin), log them in
            session["user_id"] = user.user_id
            session["username"] = user.username
            session["role"] = user.role
            flash(f"Welcome back, {user.username}!", "success")
            return redirect(url_for("main.dashboard"))
        else:
            flash("Invalid email or password.", "danger")
            return redirect(url_for("main.login"))

    return render_template("login.html")
@main.route('/dashboard')
def dashboard():
    role = session.get("role")
    
    if not role:
        flash("Please log in to access your dashboard.", "warning")
        return redirect(url_for('main.login'))
        
    if role == 'Admin':
        return redirect(url_for('main.admin_dashboard'))
    elif role == 'Student':
        return render_template('student_dashboard.html')
    elif role == 'Company':
        return render_template('company_dashboard.html')
    elif role == 'University':
        return render_template('university_dashboard.html')
        
    return redirect(url_for('main.login'))

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