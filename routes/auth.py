from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from app import db
from database.models import User, Student

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        flash("You are already logged in.", "info")
        if current_user.role == "admin":
            return redirect(url_for("admin.dashboard"))
        return redirect(url_for("student.dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        full_name = request.form.get("full_name", "").strip()
        student_id = request.form.get("student_id", "").strip()
        department = request.form.get("department", "").strip()
        semester = request.form.get("semester", 1)

        errors = []
        if not username or len(username) < 3:
            errors.append("Username must be at least 3 characters.")
        if not email or "@" not in email:
            errors.append("Please enter a valid email address.")
        if not password or len(password) < 6:
            errors.append("Password must be at least 6 characters.")
        if password != confirm_password:
            errors.append("Passwords do not match.")
        if not full_name:
            errors.append("Full name is required.")
        if not student_id:
            errors.append("Student ID is required.")

        if errors:
            for error in errors:
                flash(error, "error")
            return render_template("auth/register.html")

        if User.query.filter_by(username=username).first():
            flash("Username already taken. Please choose another.", "error")
            return render_template("auth/register.html")

        if User.query.filter_by(email=email).first():
            flash("Email already registered. Try logging in.", "error")
            return render_template("auth/register.html")

        if Student.query.filter_by(student_id=student_id).first():
            flash("Student ID already exists.", "error")
            return render_template("auth/register.html")

        try:
            user = User(
                username=username,
                email=email,
                password_hash=generate_password_hash(password),
                role="student",
                full_name=full_name,
            )
            db.session.add(user)
            db.session.flush()

            student = Student(
                user_id=user.id,
                student_id=student_id,
                department=department if department else None,
                semester=int(semester) if semester else 1,
            )
            db.session.add(student)
            db.session.commit()

            flash(f"Welcome, {full_name}! Registration successful. Please login.", "success")
            return redirect(url_for("auth.login"))

        except Exception as e:
            db.session.rollback()
            flash("An error occurred during registration. Please try again.", "error")

    return render_template("auth/register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        flash("You are already logged in.", "info")
        if current_user.role == "admin":
            return redirect(url_for("admin.dashboard"))
        return redirect(url_for("student.dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            flash("Please enter both username and password.", "error")
            return render_template("auth/login.html")

        user = User.query.filter_by(username=username).first()

        if not user:
            flash("No account found with that username.", "error")
            return render_template("auth/login.html")

        if not check_password_hash(user.password_hash, password):
            flash("Incorrect password. Please try again.", "error")
            return render_template("auth/login.html")

        if user.role == "admin":
            flash("Admin login is restricted. Use the admin portal.", "error")
            return render_template("auth/login.html")

        login_user(user)
        flash(f"Welcome back, {user.full_name}!", "success")

        return redirect(url_for("student.dashboard"))

    return render_template("auth/login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    full_name = current_user.full_name
    logout_user()
    flash(f"You have been logged out. See you again, {full_name}!", "info")
    return redirect(url_for("auth.login"))
