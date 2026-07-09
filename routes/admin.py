import os
from datetime import datetime
from flask import Blueprint, render_template, jsonify, flash, redirect, url_for, request
from flask_login import login_required, current_user
from functools import wraps
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
from app import db
from database.models import Student, Course, Certificate, Prediction, Marks, User, Enrollment
from config import Config
from services.predictor import predict as ml_predict

admin_bp = Blueprint("admin", __name__)


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != "admin":
            flash("Admin access required", "error")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated


def save_profile_image(file):
    if not file or file.filename == "":
        return None
    filename = secure_filename(file.filename)
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "jpg"
    import uuid
    new_name = f"profile_{uuid.uuid4().hex[:8]}.{ext}"
    upload_dir = os.path.join(Config.UPLOAD_FOLDER, "profiles")
    os.makedirs(upload_dir, exist_ok=True)
    file.save(os.path.join(upload_dir, new_name))
    return f"uploads/profiles/{new_name}"


@admin_bp.route("/dashboard")
@login_required
def dashboard():
    total_students = Student.query.count()
    total_certificates = Certificate.query.count()
    total_courses = Course.query.count()
    total_predictions = Prediction.query.count()

    recent_certs = Certificate.query.order_by(Certificate.created_at.desc()).limit(5).all()
    recent_preds = Prediction.query.order_by(Prediction.created_at.desc()).limit(5).all()

    grade_data = db.session.query(
        Certificate.grade, db.func.count(Certificate.id)
    ).group_by(Certificate.grade).all()

    monthly_certs = db.session.query(
        db.func.strftime("%Y-%m", Certificate.created_at),
        db.func.count(Certificate.id)
    ).group_by(db.func.strftime("%Y-%m", Certificate.created_at)).order_by(
        db.func.strftime("%Y-%m", Certificate.created_at)
    ).all()

    stats = {
        "students": total_students,
        "certificates": total_certificates,
        "courses": total_courses,
        "predictions": total_predictions,
    }

    return render_template(
        "admin/dashboard.html",
        stats=stats,
        recent_certs=recent_certs,
        recent_preds=recent_preds,
        grade_data=dict(grade_data),
        monthly_certs=[{"month": m, "count": c} for m, c in monthly_certs],
    )


@admin_bp.route("/api/stats")
@login_required
def api_stats():
    return jsonify({
        "students": Student.query.count(),
        "certificates": Certificate.query.count(),
        "courses": Course.query.count(),
        "predictions": Prediction.query.count(),
    })


@admin_bp.route("/students")
@login_required
def students():
    page = request.args.get("page", 1, type=int)
    per_page = 10
    query = request.args.get("q", "").strip()

    base_query = Student.query.join(User)

    if query:
        base_query = base_query.filter(
            User.full_name.contains(query)
            | Student.student_id.contains(query)
            | User.email.contains(query)
            | Student.department.contains(query)
        )

    total = base_query.count()
    students_page = base_query.order_by(Student.id.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    total_pages = max(1, (total + per_page - 1) // per_page)

    start_idx = (page - 1) * per_page + 1 if total > 0 else 0
    end_idx = min(page * per_page, total)

    return render_template(
        "admin/students.html",
        students=students_page.items,
        query=query,
        page=page,
        total_pages=total_pages,
        total=total,
        start_idx=start_idx,
        end_idx=end_idx,
        per_page=per_page,
    )


@admin_bp.route("/students/add", methods=["GET", "POST"])
@login_required
def add_student():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        full_name = request.form.get("full_name", "").strip()
        student_id_val = request.form.get("student_id", "").strip()
        department = request.form.get("department", "").strip()
        semester = request.form.get("semester", 1)
        phone = request.form.get("phone", "").strip()
        address = request.form.get("address", "").strip()

        errors = []
        if not username or len(username) < 3:
            errors.append("Username must be at least 3 characters.")
        if not email or "@" not in email:
            errors.append("Valid email is required.")
        if not password or len(password) < 6:
            errors.append("Password must be at least 6 characters.")
        if not full_name:
            errors.append("Full name is required.")
        if not student_id_val:
            errors.append("Student ID is required.")

        if errors:
            for e in errors:
                flash(e, "error")
            return render_template("admin/add_student.html")

        if User.query.filter_by(username=username).first():
            flash("Username already taken.", "error")
            return render_template("admin/add_student.html")
        if User.query.filter_by(email=email).first():
            flash("Email already registered.", "error")
            return render_template("admin/add_student.html")
        if Student.query.filter_by(student_id=student_id_val).first():
            flash("Student ID already exists.", "error")
            return render_template("admin/add_student.html")

        try:
            photo = save_profile_image(request.files.get("profile_image"))
            user = User(
                username=username, email=email,
                password_hash=generate_password_hash(password),
                role="student", full_name=full_name,
            )
            db.session.add(user)
            db.session.flush()
            student = Student(
                user_id=user.id, student_id=student_id_val,
                department=department, semester=int(semester) if semester else 1,
                phone=phone, address=address, profile_image=photo,
            )
            db.session.add(student)
            db.session.commit()
            flash(f"Student '{full_name}' added successfully!", "success")
            return redirect(url_for("admin.students"))
        except Exception as e:
            db.session.rollback()
            flash(f"Error adding student: {str(e)}", "error")

    return render_template("admin/add_student.html")


@admin_bp.route("/students/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_student(id):
    student = Student.query.get_or_404(id)

    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip()
        department = request.form.get("department", "").strip()
        semester = request.form.get("semester", 1)
        phone = request.form.get("phone", "").strip()
        address = request.form.get("address", "").strip()
        new_password = request.form.get("new_password", "")

        if not full_name:
            flash("Full name is required.", "error")
            return render_template("admin/edit_student.html", student=student)

        if email and email != student.user.email:
            if User.query.filter_by(email=email).first():
                flash("Email already in use by another user.", "error")
                return render_template("admin/edit_student.html", student=student)
            student.user.email = email

        student.user.full_name = full_name
        student.department = department
        student.semester = int(semester) if semester else 1
        student.phone = phone
        student.address = address

        if new_password:
            if len(new_password) >= 6:
                student.user.password_hash = generate_password_hash(new_password)
            else:
                flash("Password must be at least 6 characters.", "error")
                return render_template("admin/edit_student.html", student=student)

        photo = save_profile_image(request.files.get("profile_image"))
        if photo:
            student.profile_image = photo

        db.session.commit()
        flash(f"Student '{full_name}' updated successfully!", "success")
        return redirect(url_for("admin.students"))

    return render_template("admin/edit_student.html", student=student)


@admin_bp.route("/students/view/<int:id>")
@login_required
def view_student(id):
    student = Student.query.get_or_404(id)
    enrollments = student.enrollments
    marks = student.marks
    certificates = student.certificates
    predictions = student.predictions
    return render_template(
        "admin/view_student.html", student=student,
        enrollments=enrollments, marks=marks,
        certificates=certificates, predictions=predictions,
    )


@admin_bp.route("/students/delete/<int:id>", methods=["POST"])
@login_required
def delete_student(id):
    student = Student.query.get_or_404(id)
    full_name = student.user.full_name
    user_id = student.user_id
    db.session.delete(student)
    User.query.filter_by(id=user_id).delete()
    db.session.commit()
    flash(f"Student '{full_name}' deleted successfully.", "success")
    return redirect(url_for("admin.students"))


@admin_bp.route("/courses")
@login_required
def courses():
    page = request.args.get("page", 1, type=int)
    per_page = 10
    query = request.args.get("q", "").strip()

    base_query = Course.query

    if query:
        base_query = base_query.filter(
            Course.course_code.contains(query)
            | Course.course_name.contains(query)
        )

    total = base_query.count()
    courses_page = base_query.order_by(Course.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    total_pages = max(1, (total + per_page - 1) // per_page)
    start_idx = (page - 1) * per_page + 1 if total > 0 else 0
    end_idx = min(page * per_page, total)

    return render_template(
        "admin/courses.html",
        courses=courses_page.items,
        query=query,
        page=page,
        total_pages=total_pages,
        total=total,
        start_idx=start_idx,
        end_idx=end_idx,
        per_page=per_page,
    )


@admin_bp.route("/courses/add", methods=["GET", "POST"])
@login_required
def add_course():
    if request.method == "POST":
        course_code = request.form.get("course_code", "").strip().upper()
        course_name = request.form.get("course_name", "").strip()
        credits = request.form.get("credits", 3)
        description = request.form.get("description", "").strip()

        errors = []
        if not course_code:
            errors.append("Course code is required.")
        if not course_name:
            errors.append("Course name is required.")

        if errors:
            for e in errors:
                flash(e, "error")
            return render_template("admin/add_course.html")

        if Course.query.filter_by(course_code=course_code).first():
            flash("Course code already exists.", "error")
            return render_template("admin/add_course.html")

        try:
            course = Course(
                course_code=course_code,
                course_name=course_name,
                credits=int(credits) if credits else 3,
                description=description,
            )
            db.session.add(course)
            db.session.commit()
            flash(f"Course '{course_name}' added successfully!", "success")
            return redirect(url_for("admin.courses"))
        except Exception as e:
            db.session.rollback()
            flash(f"Error adding course: {str(e)}", "error")

    return render_template("admin/add_course.html")


@admin_bp.route("/courses/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_course(id):
    course = Course.query.get_or_404(id)

    if request.method == "POST":
        course_code = request.form.get("course_code", "").strip().upper()
        course_name = request.form.get("course_name", "").strip()
        credits = request.form.get("credits", 3)
        description = request.form.get("description", "").strip()

        if not course_name:
            flash("Course name is required.", "error")
            return render_template("admin/edit_course.html", course=course)

        if course_code and course_code != course.course_code:
            if Course.query.filter_by(course_code=course_code).first():
                flash("Course code already in use.", "error")
                return render_template("admin/edit_course.html", course=course)
            course.course_code = course_code

        course.course_name = course_name
        course.credits = int(credits) if credits else 3
        course.description = description
        db.session.commit()
        flash(f"Course '{course_name}' updated successfully!", "success")
        return redirect(url_for("admin.courses"))

    return render_template("admin/edit_course.html", course=course)


@admin_bp.route("/courses/view/<int:id>")
@login_required
def view_course(id):
    course = Course.query.get_or_404(id)
    enrollments = Enrollment.query.filter_by(course_id=id).all()
    cert_count = Certificate.query.filter_by(course_id=id).count()
    return render_template(
        "admin/view_course.html", course=course, enrollments=enrollments, cert_count=cert_count
    )


@admin_bp.route("/courses/delete/<int:id>", methods=["POST"])
@login_required
def delete_course(id):
    course = Course.query.get_or_404(id)
    name = course.course_name
    Enrollment.query.filter_by(course_id=id).delete()
    db.session.delete(course)
    db.session.commit()
    flash(f"Course '{name}' deleted successfully.", "success")
    return redirect(url_for("admin.courses"))


@admin_bp.route("/marks")
@login_required
def marks():
    page = request.args.get("page", 1, type=int)
    per_page = 10
    query = request.args.get("q", "").strip()

    base_query = Marks.query.join(Student).join(User).join(Course)

    if query:
        base_query = base_query.filter(
            User.full_name.contains(query)
            | Student.student_id.contains(query)
            | Course.course_code.contains(query)
            | Course.course_name.contains(query)
        )

    total = base_query.count()
    marks_page = base_query.order_by(Marks.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    total_pages = max(1, (total + per_page - 1) // per_page)
    start_idx = (page - 1) * per_page + 1 if total > 0 else 0
    end_idx = min(page * per_page, total)

    return render_template(
        "admin/marks.html",
        marks=marks_page.items,
        query=query,
        page=page,
        total_pages=total_pages,
        total=total,
        start_idx=start_idx,
        end_idx=end_idx,
        per_page=per_page,
    )


@admin_bp.route("/marks/add", methods=["GET", "POST"])
@login_required
def add_marks():
    students = Student.query.join(User).order_by(User.full_name).all()
    courses = Course.query.order_by(Course.course_name).all()

    if request.method == "POST":
        student_id = request.form.get("student_id", type=int)
        course_id = request.form.get("course_id", type=int)
        semester = request.form.get("semester", 1, type=int)
        exam_type = request.form.get("exam_type", "final")
        attendance = request.form.get("attendance", 0, type=float)
        assignments = request.form.get("assignments", 0, type=float)
        quiz_scores = request.form.get("quiz_scores", 0, type=float)
        marks_obtained = request.form.get("marks_obtained", 0, type=float)
        total_marks = request.form.get("total_marks", 100, type=float)

        errors = []
        if not student_id or not Student.query.get(student_id):
            errors.append("Valid student is required.")
        if not course_id or not Course.query.get(course_id):
            errors.append("Valid course is required.")
        if marks_obtained < 0 or marks_obtained > total_marks:
            errors.append("Obtained marks must be between 0 and total marks.")
        if total_marks <= 0:
            errors.append("Total marks must be greater than 0.")
        if not (0 <= attendance <= 100):
            errors.append("Attendance must be between 0 and 100.")
        if not (0 <= assignments <= 100):
            errors.append("Assignment marks must be between 0 and 100.")
        if not (0 <= quiz_scores <= 100):
            errors.append("Quiz marks must be between 0 and 100.")
        if not (1 <= semester <= 12):
            errors.append("Semester must be between 1 and 12.")

        existing = Marks.query.filter_by(student_id=student_id, course_id=course_id, semester=semester, exam_type=exam_type).first()
        if existing:
            errors.append("Marks already exist for this student, course, semester, and exam type.")

        if errors:
            for e in errors:
                flash(e, "error")
            return render_template("admin/add_marks.html", students=students, courses=courses)

        try:
            mark = Marks(
                student_id=student_id, course_id=course_id,
                semester=semester, exam_type=exam_type,
                attendance=attendance, assignments=assignments,
                quiz_scores=quiz_scores, marks_obtained=marks_obtained,
                total_marks=total_marks,
            )
            db.session.add(mark)
            db.session.flush()

            result = ml_predict(attendance, assignments, quiz_scores)
            pred = Prediction(
                student_id=student_id, course_id=course_id,
                predicted_pass=result["predicted_pass"],
                predicted_grade=result["predicted_grade"],
                predicted_performance=result["predicted_performance"],
                confidence_score=result["confidence_score"],
            )
            db.session.add(pred)
            db.session.commit()
            flash("Marks added successfully! AI prediction generated.", "success")
            return redirect(url_for("admin.marks"))
        except Exception as e:
            db.session.rollback()
            flash(f"Error: {str(e)}", "error")

    return render_template("admin/add_marks.html", students=students, courses=courses)


@admin_bp.route("/marks/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_marks(id):
    mark = Marks.query.get_or_404(id)
    students = Student.query.join(User).order_by(User.full_name).all()
    courses = Course.query.order_by(Course.course_name).all()

    if request.method == "POST":
        student_id = request.form.get("student_id", type=int)
        course_id = request.form.get("course_id", type=int)
        semester = request.form.get("semester", 1, type=int)
        exam_type = request.form.get("exam_type", "final")
        attendance = request.form.get("attendance", 0, type=float)
        assignments = request.form.get("assignments", 0, type=float)
        quiz_scores = request.form.get("quiz_scores", 0, type=float)
        marks_obtained = request.form.get("marks_obtained", 0, type=float)
        total_marks = request.form.get("total_marks", 100, type=float)

        errors = []
        if not student_id or not Student.query.get(student_id):
            errors.append("Valid student is required.")
        if not course_id or not Course.query.get(course_id):
            errors.append("Valid course is required.")
        if marks_obtained < 0 or marks_obtained > total_marks:
            errors.append("Obtained marks must be between 0 and total marks.")
        if total_marks <= 0:
            errors.append("Total marks must be greater than 0.")
        if not (0 <= attendance <= 100):
            errors.append("Attendance must be between 0 and 100.")
        if not (0 <= assignments <= 100):
            errors.append("Assignment marks must be between 0 and 100.")
        if not (0 <= quiz_scores <= 100):
            errors.append("Quiz marks must be between 0 and 100.")
        if not (1 <= semester <= 12):
            errors.append("Semester must be between 1 and 12.")

        dup = Marks.query.filter(
            Marks.student_id == student_id,
            Marks.course_id == course_id,
            Marks.semester == semester,
            Marks.exam_type == exam_type,
            Marks.id != id,
        ).first()
        if dup:
            errors.append("Marks already exist for this student, course, semester, and exam type.")

        if errors:
            for e in errors:
                flash(e, "error")
            return render_template("admin/edit_marks.html", mark=mark, students=students, courses=courses)

        mark.student_id = student_id
        mark.course_id = course_id
        mark.semester = semester
        mark.exam_type = exam_type
        mark.attendance = attendance
        mark.assignments = assignments
        mark.quiz_scores = quiz_scores
        mark.marks_obtained = marks_obtained
        mark.total_marks = total_marks

        result = ml_predict(attendance, assignments, quiz_scores)
        existing_pred = Prediction.query.filter_by(student_id=student_id, course_id=course_id).first()
        if existing_pred:
            existing_pred.predicted_pass = result["predicted_pass"]
            existing_pred.predicted_grade = result["predicted_grade"]
            existing_pred.predicted_performance = result["predicted_performance"]
            existing_pred.confidence_score = result["confidence_score"]
        else:
            pred = Prediction(
                student_id=student_id, course_id=course_id,
                predicted_pass=result["predicted_pass"],
                predicted_grade=result["predicted_grade"],
                predicted_performance=result["predicted_performance"],
                confidence_score=result["confidence_score"],
            )
            db.session.add(pred)
        db.session.commit()
        flash("Marks updated successfully! Prediction refreshed.", "success")
        return redirect(url_for("admin.marks"))

    return render_template("admin/edit_marks.html", mark=mark, students=students, courses=courses)


@admin_bp.route("/marks/delete/<int:id>", methods=["POST"])
@login_required
def delete_marks(id):
    mark = Marks.query.get_or_404(id)
    db.session.delete(mark)
    db.session.commit()
    flash("Marks entry deleted successfully.", "success")
    return redirect(url_for("admin.marks"))


@admin_bp.route("/predictions")
@login_required
def predictions():
    page = request.args.get("page", 1, type=int)
    per_page = 10
    query = request.args.get("q", "").strip()

    base_query = Prediction.query.join(Student).join(User).join(Course)

    if query:
        base_query = base_query.filter(
            User.full_name.contains(query)
            | Student.student_id.contains(query)
            | Course.course_code.contains(query)
            | Course.course_name.contains(query)
        )

    total = base_query.count()
    preds_page = base_query.order_by(Prediction.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    total_pages = max(1, (total + per_page - 1) // per_page)
    start_idx = (page - 1) * per_page + 1 if total > 0 else 0
    end_idx = min(page * per_page, total)

    return render_template(
        "admin/predictions.html",
        predictions=preds_page.items,
        query=query,
        page=page,
        total_pages=total_pages,
        total=total,
        start_idx=start_idx,
        end_idx=end_idx,
    )


@admin_bp.route("/predictions/retrain", methods=["POST"])
@login_required
def retrain_predictions():
    try:
        import subprocess, sys
        subprocess.run([sys.executable, "ML_model/train.py"], cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))), check=True)
        import importlib
        import services.predictor
        importlib.reload(services.predictor)
        flash("Model retrained successfully!", "success")
    except Exception as e:
        flash(f"Retrain failed: {str(e)}", "error")
    return redirect(url_for("admin.predictions"))


@admin_bp.route("/certificates")
@login_required
def certificates():
    page = request.args.get("page", 1, type=int)
    per_page = 10
    query = request.args.get("q", "").strip()

    base_query = Certificate.query.join(Student).join(User).join(Course)

    if query:
        base_query = base_query.filter(
            User.full_name.contains(query)
            | Student.student_id.contains(query)
            | Course.course_code.contains(query)
            | Course.course_name.contains(query)
            | Certificate.cert_id.contains(query)
        )

    total = base_query.count()
    certs_page = base_query.order_by(Certificate.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    total_pages = max(1, (total + per_page - 1) // per_page)
    start_idx = (page - 1) * per_page + 1 if total > 0 else 0
    end_idx = min(page * per_page, total)

    return render_template(
        "admin/certificates.html",
        certificates=certs_page.items,
        query=query,
        page=page,
        total_pages=total_pages,
        total=total,
        start_idx=start_idx,
        end_idx=end_idx,
    )


@admin_bp.route("/certificates/generate", methods=["GET", "POST"])
@login_required
def generate_certificate():
    students = Student.query.join(User).order_by(User.full_name).all()
    courses = Course.query.order_by(Course.course_name).all()

    if request.method == "POST":
        student_id = request.form.get("student_id", type=int)
        course_id = request.form.get("course_id", type=int)
        marks_obtained = request.form.get("marks_obtained", 0, type=float)
        total_marks = request.form.get("total_marks", 100, type=float)
        grade = request.form.get("grade", "").strip().upper()
        issued_by = request.form.get("issued_by", "System Administrator").strip()

        errors = []
        student = Student.query.get(student_id)
        course = Course.query.get(course_id)
        if not student:
            errors.append("Valid student is required.")
        if not course:
            errors.append("Valid course is required.")
        if not grade:
            errors.append("Grade is required.")

        existing = Certificate.query.filter_by(student_id=student_id, course_id=course_id).first()
        if existing:
            errors.append("Certificate already exists for this student and course.")

        if errors:
            for e in errors:
                flash(e, "error")
            return render_template("admin/generate_certificate.html", students=students, courses=courses)

        import uuid
        cert_id = f"CERT-{uuid.uuid4().hex[:12].upper()}"
        issue_date = datetime.utcnow()

        from services.certificate_generator import generate_certificate as gen_pdf
        try:
            pdf_path, qr_path = gen_pdf(
                student_name=student.user.full_name,
                course_name=course.course_name,
                grade=grade,
                marks_obtained=marks_obtained,
                total_marks=total_marks,
                cert_id=cert_id,
                issue_date=issue_date,
                issued_by=issued_by,
            )

            rel_pdf = f"certificates_output/{cert_id}/certificate.pdf"
            rel_qr = f"certificates_output/{cert_id}/qr.png"

            cert = Certificate(
                cert_id=cert_id,
                student_id=student_id,
                course_id=course_id,
                grade=grade,
                marks_obtained=marks_obtained,
                total_marks=total_marks,
                completion_date=issue_date,
                pdf_path=rel_pdf,
                qr_code_path=rel_qr,
                is_valid=True,
                issued_by=issued_by,
            )
            db.session.add(cert)
            db.session.commit()
            flash(f"Certificate {cert_id} generated successfully!", "success")
            return redirect(url_for("admin.certificates"))
        except Exception as e:
            flash(f"Certificate generation failed: {str(e)}", "error")

    return render_template("admin/generate_certificate.html", students=students, courses=courses)


@admin_bp.route("/certificates/download/<int:id>")
@login_required
def download_certificate(id):
    cert = Certificate.query.get_or_404(id)
    pdf_abs = os.path.join(Config.CERTIFICATE_FOLDER, cert.cert_id, "certificate.pdf")
    if not os.path.isfile(pdf_abs):
        flash("PDF file not found on disk.", "error")
        return redirect(url_for("admin.certificates"))
    from flask import send_file
    return send_file(pdf_abs, as_attachment=True, download_name=f"{cert.cert_id}.pdf")


@admin_bp.route("/certificates/view/<int:id>")
@login_required
def view_certificate(id):
    cert = Certificate.query.get_or_404(id)
    return render_template("admin/view_certificate.html", cert=cert)


@admin_bp.route("/certificates/revoke/<int:id>", methods=["POST"])
@login_required
def revoke_certificate(id):
    cert = Certificate.query.get_or_404(id)
    cert.is_valid = not cert.is_valid
    db.session.commit()
    status = "revoked" if not cert.is_valid else "reinstated"
    flash(f"Certificate {cert.cert_id} {status}.", "success")
    return redirect(url_for("admin.view_certificate", id=cert.id))
