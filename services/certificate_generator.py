import os
import uuid
from datetime import datetime
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, black, white, Color
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet
import qrcode
from config import Config


GOLD = HexColor("#c9a84c")
DARK_BG = HexColor("#1a1a2e")
ACCENT = HexColor("#6c63ff")


def generate_qr(cert_id, output_path):
    verify_url = f"http://localhost:5000/verify/{cert_id}"
    img = qrcode.make(verify_url, box_size=10, border=2)
    img.save(output_path)
    return output_path


def generate_certificate(student_name, course_name, grade, marks_obtained,
                         total_marks, cert_id, issue_date, issued_by="System Administrator"):
    cert_dir = os.path.join(Config.CERTIFICATE_FOLDER, cert_id)
    os.makedirs(cert_dir, exist_ok=True)

    qr_path = os.path.join(cert_dir, "qr.png")
    generate_qr(cert_id, qr_path)

    pdf_path = os.path.join(cert_dir, "certificate.pdf")
    W, H = landscape(A4)

    c = canvas.Canvas(pdf_path, pagesize=landscape(A4))

    c.setFillColor(DARK_BG)
    c.rect(0, 0, W, H, fill=1, stroke=0)

    margin = 20
    c.setStrokeColor(GOLD)
    c.setLineWidth(3)
    c.rect(margin, margin, W - 2 * margin, H - 2 * margin, fill=0, stroke=1)

    c.setStrokeColor(GOLD)
    c.setLineWidth(1)
    inner_margin = 28
    c.rect(inner_margin, inner_margin, W - 2 * inner_margin, H - 2 * inner_margin, fill=0, stroke=1)

    c.setFillColor(GOLD)
    c.setFont("Times-Bold", 14)
    c.drawCentredString(W / 2, H - 55, "CERTIFYPRO")

    c.setFillColor(HexColor("#ffffff"))
    c.setFont("Times-Roman", 10)
    c.drawCentredString(W / 2, H - 70, "AI-Powered Certificate Generation & Verification System")

    line_y = H - 80
    c.setStrokeColor(GOLD)
    c.setLineWidth(0.5)
    c.line(margin + 80, line_y, W - margin - 80, line_y)

    c.setFillColor(HexColor("#ffffff"))
    c.setFont("Times-Bold", 36)
    c.drawCentredString(W / 2, H - 130, "Certificate of Completion")

    c.setFillColor(HexColor("#cccccc"))
    c.setFont("Times-Roman", 14)
    c.drawCentredString(W / 2, H - 155, "This is to certify that")

    try:
        c.setFillColor(ACCENT)
        c.setFont("Times-Bold", 28)
        c.drawCentredString(W / 2, H - 192, student_name)
    except Exception:
        c.setFillColor(ACCENT)
        c.setFont("Helvetica-Bold", 26)
        c.drawCentredString(W / 2, H - 192, student_name)

    c.setFillColor(HexColor("#cccccc"))
    c.setFont("Times-Roman", 14)
    c.drawCentredString(W / 2, H - 215, "has successfully completed the course")

    c.setFillColor(HexColor("#ffffff"))
    c.setFont("Times-Bold", 20)
    c.drawCentredString(W / 2, H - 242, course_name)

    c.setFillColor(HexColor("#cccccc"))
    c.setFont("Times-Roman", 12)
    c.drawCentredString(W / 2, H - 262, f"with a grade of")

    c.setFillColor(GOLD)
    c.setFont("Times-Bold", 22)
    c.drawCentredString(W / 2, H - 287, f"{grade}")

    grade_pct = (marks_obtained / total_marks * 100) if total_marks > 0 else 0
    c.setFillColor(HexColor("#aaaaaa"))
    c.setFont("Times-Roman", 11)
    c.drawCentredString(W / 2, H - 305, f"Score: {marks_obtained:.1f}/{total_marks:.0f}  |  Percentage: {grade_pct:.1f}%")

    c.setStrokeColor(GOLD)
    c.setLineWidth(0.3)
    c.line(margin + 60, H - 320, W - margin - 60, H - 320)

    date_str = issue_date.strftime("%B %d, %Y") if hasattr(issue_date, 'strftime') else str(issue_date)
    c.setFillColor(HexColor("#aaaaaa"))
    c.setFont("Times-Roman", 10)
    c.drawString(margin + 40, 55, f"Issue Date: {date_str}")

    c.drawString(margin + 40, 42, f"Certificate ID: {cert_id}")

    c.setFont("Times-Roman", 10)
    c.drawRightString(W - margin - 40, 55, f"Issued by: {issued_by}")

    c.setFillColor(HexColor("#aaaaaa"))
    c.setFont("Times-Roman", 9)
    c.drawCentredString(W / 2, 38, "Verify this certificate at: http://localhost:5000/verify/" + cert_id)

    c.drawImage(qr_path, W - 130, 45, width=70, height=70, preserveAspectRatio=True)

    sig_y = 85
    c.setStrokeColor(GOLD)
    c.setLineWidth(1.5)
    c.line(margin + 40, sig_y, margin + 180, sig_y)
    c.setFillColor(HexColor("#cccccc"))
    c.setFont("Times-Roman", 9)
    c.drawString(margin + 40, sig_y - 14, "Authorized Signature")

    c.setStrokeColor(GOLD)
    c.setLineWidth(1.5)
    c.line(W - margin - 180, sig_y, W - margin - 40, sig_y)
    c.setFillColor(HexColor("#cccccc"))
    c.setFont("Times-Roman", 9)
    c.drawRightString(W - margin - 40, sig_y - 14, issued_by)

    c.save()
    return pdf_path, qr_path
