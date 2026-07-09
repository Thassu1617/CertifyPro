from flask import Blueprint, render_template, flash, redirect, url_for, request, jsonify
from flask_login import login_required, current_user
from database.models import Marks, Prediction, Exam, Question, StudentAnswer, ExamResult, Student, Course, Enrollment, Certificate
from app import db
from datetime import datetime

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
    exam_pred = Prediction.query.join(Course, Prediction.course_id == Course.id).filter(
        Prediction.student_id == student.id,
        Prediction.score > 0
    ).order_by(Prediction.created_at.desc()).first()

    return render_template(
        "student/dashboard.html",
        student=student,
        enrollments=enrollments,
        marks=marks,
        certificates=certificates,
        predictions=predictions,
        pred=pred,
        exam_pred=exam_pred,
        avg_marks=avg_marks,
    )


@student_bp.route("/courses")
@login_required
def courses():
    student = current_user.student
    if not student:
        flash("Student profile not found.", "error")
        return redirect(url_for("main.index"))
    all_courses = Course.query.order_by(Course.course_name).all()
    enrolled_ids = {e.course_id for e in student.enrollments}
    available_courses = [c for c in all_courses if c.id not in enrolled_ids]
    return render_template("student/courses.html", student=student, enrollments=student.enrollments, available_courses=available_courses, enrolled_courses=enrolled_ids)


@student_bp.route("/courses/enroll/<int:course_id>", methods=["POST"])
@login_required
def enroll_course(course_id):
    student = current_user.student
    if not student:
        flash("Student profile not found.", "error")
        return redirect(url_for("main.index"))

    course = Course.query.get_or_404(course_id)
    existing = Enrollment.query.filter_by(student_id=student.id, course_id=course_id).first()
    if existing:
        flash("Already enrolled in this course.", "info")
    else:
        enrollment = Enrollment(student_id=student.id, course_id=course_id, status="active")
        db.session.add(enrollment)
        db.session.commit()
        flash(f"Successfully enrolled in {course.course_name}!", "success")

    return redirect(url_for("student.courses"))


@student_bp.route("/courses/review/<int:course_id>")
@login_required
def course_review(course_id):
    student = current_user.student
    if not student:
        flash("Student profile not found.", "error")
        return redirect(url_for("main.index"))

    course = Course.query.get_or_404(course_id)
    enrollment = Enrollment.query.filter_by(student_id=student.id, course_id=course_id).first()
    if not enrollment:
        flash("You are not enrolled in this course.", "error")
        return redirect(url_for("student.courses"))

    published_exams = Exam.query.filter_by(course_id=course_id, is_published=True).order_by(Exam.created_at).all()
    exam_data = []
    for exam in published_exams:
        result = ExamResult.query.filter_by(student_id=student.id, exam_id=exam.id).first()
        exam_data.append({"exam": exam, "result": result})

    return render_template("student/course_review.html", course=course, exams=exam_data)


@student_bp.route("/certificates")
@login_required
def certificates():
    student = current_user.student
    if not student:
        flash("Student profile not found.", "error")
        return redirect(url_for("main.index"))
    return render_template("student/certificates.html", student=student, certificates=student.certificates)


# ─── Online Exam System ─────────────────────────────────────────────────────────

@student_bp.route("/exams")
@login_required
def exams():
    student = current_user.student
    if not student:
        flash("Student profile not found.", "error")
        return redirect(url_for("main.index"))

    published_exams = Exam.query.filter_by(is_published=True).order_by(Exam.created_at.desc()).all()

    exam_data = []
    for exam in published_exams:
        result = ExamResult.query.filter_by(student_id=student.id, exam_id=exam.id).first()
        answers_count = StudentAnswer.query.filter_by(student_id=student.id, exam_id=exam.id).count()
        exam_data.append({
            "exam": exam,
            "result": result,
            "has_started": answers_count > 0,
        })

    return render_template("student/exams.html", exam_data=exam_data)


@student_bp.route("/exams/start/<int:exam_id>")
@login_required
def start_exam(exam_id):
    student = current_user.student
    if not student:
        flash("Student profile not found.", "error")
        return redirect(url_for("main.index"))

    exam = Exam.query.get_or_404(exam_id)

    if not exam.is_published:
        flash("Exam is not available.", "error")
        return redirect(url_for("student.exams"))

    existing = ExamResult.query.filter_by(student_id=student.id, exam_id=exam_id).first()
    if existing:
        flash("You have already submitted this exam.", "error")
        return redirect(url_for("student.exam_result", exam_id=exam_id))

    questions = Question.query.filter_by(exam_id=exam_id).order_by(Question.id).all()

    if not questions:
        flash("No questions in this exam yet.", "error")
        return redirect(url_for("student.exams"))

    return render_template(
        "student/take_exam.html",
        exam=exam,
        questions=questions,
        total_questions=len(questions),
    )


@student_bp.route("/exams/submit/<int:exam_id>", methods=["POST"])
@login_required
def submit_exam(exam_id):
    student = current_user.student
    if not student:
        return jsonify({"error": "Student not found"}), 400

    exam = Exam.query.get_or_404(exam_id)

    existing = ExamResult.query.filter_by(student_id=student.id, exam_id=exam_id).first()
    if existing:
        return jsonify({"error": "Already submitted"}), 400

    questions = Question.query.filter_by(exam_id=exam_id).all()
    score = 0
    correct_count = 0
    total_qs = len(questions)

    StudentAnswer.query.filter_by(student_id=student.id, exam_id=exam_id).delete()
    db.session.flush()

    for question in questions:
        answer_key = f"q_{question.id}"
        selected = request.form.get(answer_key, "").strip().upper()

        if selected in ("A", "B", "C", "D"):
            is_correct = selected == question.correct_answer
            if is_correct:
                score += question.marks
                correct_count += 1

            answer = StudentAnswer(
                student_id=student.id,
                exam_id=exam_id,
                question_id=question.id,
                selected_answer=selected,
                is_correct=is_correct,
            )
            db.session.add(answer)
        else:
            answer = StudentAnswer(
                student_id=student.id,
                exam_id=exam_id,
                question_id=question.id,
                selected_answer=None,
                is_correct=False,
            )
            db.session.add(answer)

    total_marks = sum(q.marks for q in questions)
    percentage = round((score / total_marks * 100), 2) if total_marks > 0 else 0
    passed = percentage >= exam.passing_percentage

    result = ExamResult(
        student_id=student.id,
        exam_id=exam_id,
        score=score,
        percentage=percentage,
        total_marks=total_marks,
        total_questions=total_qs,
        correct_answers=correct_count,
        passed=passed,
    )
    db.session.add(result)
    db.session.flush()

    # Auto-generate ML predictions
    try:
        from services.exam_predictor import predict as ml_predict
        ml_result = ml_predict(
            percentage=percentage,
            attendance=0,
            quiz_scores=0,
            assignment_scores=0,
            exam_marks=score,
        )
        pred = Prediction(
            student_id=student.id,
            course_id=exam.course_id,
            score=score,
            total_marks=total_marks,
            percentage=percentage,
            predicted_pass=ml_result["predicted_pass"],
            predicted_grade=ml_result["predicted_grade"],
            predicted_performance=ml_result["predicted_performance"],
            confidence_score=ml_result["confidence_score"],
        )
        db.session.add(pred)
    except Exception:
        pass

    # Auto-generate certificate if score >= 70%
    cert_generated = None
    if percentage >= 70:
        try:
            import uuid
            from services.certificate_generator import generate_certificate as gen_pdf
            existing_cert = Certificate.query.filter_by(student_id=student.id, course_id=exam.course_id).first()
            if not existing_cert:
                cert_id = f"CERT-{uuid.uuid4().hex[:12].upper()}"
                if percentage >= 90:
                    grade = "A+"
                elif percentage >= 80:
                    grade = "A"
                elif percentage >= 70:
                    grade = "B"
                else:
                    grade = "C"
                pdf_path, qr_path = gen_pdf(
                    student_name=student.user.full_name,
                    course_name=exam.course.course_name,
                    grade=grade,
                    marks_obtained=score,
                    total_marks=total_marks,
                    cert_id=cert_id,
                    issue_date=datetime.utcnow(),
                    issued_by="CertifyPro System",
                )
                rel_pdf = f"certificates_output/{cert_id}/certificate.pdf"
                rel_qr = f"certificates_output/{cert_id}/qr.png"
                cert = Certificate(
                    cert_id=cert_id,
                    student_id=student.id,
                    course_id=exam.course_id,
                    grade=grade,
                    marks_obtained=score,
                    total_marks=total_marks,
                    completion_date=datetime.utcnow(),
                    pdf_path=rel_pdf,
                    qr_code_path=rel_qr,
                    is_valid=True,
                    issued_by="CertifyPro System",
                )
                db.session.add(cert)
                cert_generated = cert_id
        except Exception:
            pass

    db.session.commit()

    return redirect(url_for("student.exam_result", exam_id=exam_id))


@student_bp.route("/exams/result/<int:exam_id>")
@login_required
def exam_result(exam_id):
    student = current_user.student
    if not student:
        flash("Student profile not found.", "error")
        return redirect(url_for("main.index"))

    exam = Exam.query.get_or_404(exam_id)
    result = ExamResult.query.filter_by(student_id=student.id, exam_id=exam_id).first()

    if not result:
        flash("No result found for this exam.", "error")
        return redirect(url_for("student.exams"))

    answers = StudentAnswer.query.filter_by(student_id=student.id, exam_id=exam_id).order_by(StudentAnswer.question_id).all()
    questions = Question.query.filter_by(exam_id=exam_id).order_by(Question.id).all()

    from services.exam_predictor import predict as ml_predict
    fresh = ml_predict(
        percentage=result.percentage,
        attendance=0,
        quiz_scores=0,
        assignment_scores=0,
        exam_marks=result.score,
    )
    prediction = Prediction.query.filter_by(student_id=student.id, course_id=exam.course_id).order_by(Prediction.created_at.desc()).first()
    if prediction and (prediction.predicted_grade != fresh["predicted_grade"] or prediction.predicted_performance != fresh["predicted_performance"]):
        prediction.predicted_pass = fresh["predicted_pass"]
        prediction.predicted_grade = fresh["predicted_grade"]
        prediction.predicted_performance = fresh["predicted_performance"]
        prediction.confidence_score = fresh["confidence_score"]
        db.session.commit()
        prediction = Prediction.query.get(prediction.id)

    certificate = Certificate.query.filter_by(student_id=student.id, course_id=exam.course_id).first()

    return render_template(
        "student/exam_result.html",
        exam=exam,
        result=result,
        answers=answers,
        questions=questions,
        prediction=prediction,
        certificate=certificate,
    )


@student_bp.route("/certificates/download/<int:cert_id>")
@login_required
def download_certificate(cert_id):
    import os
    from config import Config
    from flask import send_file
    student = current_user.student
    if not student:
        flash("Student not found.", "error")
        return redirect(url_for("main.index"))
    cert = Certificate.query.get_or_404(cert_id)
    if cert.student_id != student.id:
        flash("Certificate not found.", "error")
        return redirect(url_for("student.dashboard"))
    pdf_abs = os.path.join(Config.CERTIFICATE_FOLDER, cert.cert_id, "certificate.pdf")
    if not os.path.isfile(pdf_abs):
        flash("PDF file not found on disk.", "error")
        return redirect(url_for("student.dashboard"))
    return send_file(pdf_abs, as_attachment=True, download_name=f"{cert.cert_id}.pdf")
