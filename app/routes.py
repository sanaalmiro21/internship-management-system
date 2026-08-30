from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from .services import register_user, authenticate_user

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
            session["user_id"] = user.user_id
            session["username"] = user.username
            session["role"] = user.role
            flash(f"Welcome back, {user.username}!", "success")
            return redirect(url_for("main.dashboard"))
        else:
            flash("Invalid email or password.", "danger")
            return redirect(url_for("main.login"))

    return render_template("login.html")

@main.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        flash("Please log in to access your dashboard.", "warning")
        return redirect(url_for("main.login"))

    return render_template("dashboard.html", username=session.get("username"), role=session.get("role"))

@main.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("main.login"))