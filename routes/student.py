from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from database.models import Marks, Prediction

student_bp = Blueprint("student", __name__)


@student_bp.route("/dashboard")
@login_required
def dashboard():
    student = current_user.student
    if not student:
        flash("Student profile not found.", "error")
        return redirect(url_for("main.index"))

    enrollments = student.enrollments
    marks = student.marks
    certificates = student.certificates
    predictions = student.predictions

    avg_marks = 0
    if marks:
        total_pct = sum((m.marks_obtained / m.total_marks * 100) for m in marks if m.total_marks > 0)
        avg_marks = round(total_pct / len(marks), 1)

    pred = predictions[-1] if predictions else None

    return render_template(
        "student/dashboard.html",
        student=student,
        enrollments=enrollments,
        marks=marks,
        certificates=certificates,
        predictions=predictions,
        pred=pred,
        avg_marks=avg_marks,
    )


@student_bp.route("/courses")
@login_required
def courses():
    student = current_user.student
    if not student:
        flash("Student profile not found.", "error")
        return redirect(url_for("main.index"))
    return render_template("student/courses.html", student=student, enrollments=student.enrollments)


@student_bp.route("/certificates")
@login_required
def certificates():
    student = current_user.student
    if not student:
        flash("Student profile not found.", "error")
        return redirect(url_for("main.index"))
    return render_template("student/certificates.html", student=student, certificates=student.certificates)
