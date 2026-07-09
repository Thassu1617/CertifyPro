from datetime import datetime
from flask import Blueprint, render_template, request
from database.models import Certificate, Student, User, Course

main_bp = Blueprint("main", __name__)


@main_bp.app_context_processor
def inject_now():
    return {"now": datetime.now}


@main_bp.route("/")
def index():
    return render_template("index.html")


@main_bp.route("/verify")
@main_bp.route("/verify/<cert_id>")
def verify(cert_id=None):
    if cert_id:
        cert = Certificate.query.filter_by(cert_id=cert_id).first()
        if not cert:
            return render_template("verify.html", cert=None, not_found=cert_id, search_value=cert_id)
        return render_template("verify.html", cert=cert, not_found=False, search_value=cert_id)

    search = request.args.get("cert_id", "").strip()
    if search:
        cert = Certificate.query.filter_by(cert_id=search).first()
        if not cert:
            return render_template("verify.html", cert=None, not_found=search, search_value=search)
        return render_template("verify.html", cert=cert, not_found=False, search_value=search)

    return render_template("verify.html", cert=None, not_found=False, search_value="")
