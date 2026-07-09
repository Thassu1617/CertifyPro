import os
from datetime import datetime
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, black, white
from reportlab.pdfgen import canvas
import qrcode
from config import Config


GOLD_DARK = HexColor("#b8922a")
GOLD = HexColor("#c9a84c")
GOLD_LIGHT = HexColor("#e8d48b")
WHITE = HexColor("#ffffff")
CREAM = HexColor("#fefcf5")
TEXT_DARK = HexColor("#2c1810")
TEXT_MUTED = HexColor("#8a7a6a")
SIGNATURE_NAME = "P.Thasneem"


def generate_qr(cert_id, output_path):
    verify_url = f"http://localhost:5000/verify/{cert_id}"
    img = qrcode.make(verify_url, box_size=10, border=2)
    img.save(output_path)
    return output_path


def draw_logo(c, x, y, size=36):
    cx, cy = x + size / 2, y - size / 2
    c.setFillColor(GOLD)
    c.circle(cx, cy, size / 2, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 13)
    c.drawCentredString(cx, cy - 4.5, "CP")


def draw_badge(c, cx, cy, radius=40):
    c.setStrokeColor(GOLD_DARK)
    c.setLineWidth(3.5)
    c.circle(cx, cy, radius, fill=0, stroke=1)
    c.setStrokeColor(GOLD)
    c.setLineWidth(1.5)
    c.circle(cx, cy, radius - 6, fill=0, stroke=1)
    c.setFillColor(GOLD_DARK)
    c.setFont("Helvetica-Bold", 8)
    c.drawCentredString(cx, cy + 12, "ISSUED BY")
    c.setFillColor(GOLD)
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(cx, cy - 3, "CertifyPro")
    c.setFillColor(GOLD_DARK)
    c.setFont("Helvetica", 5.5)
    c.drawCentredString(cx, cy - 18, "SYSTEM")


def generate_certificate(student_name, course_name, grade, marks_obtained,
                         total_marks, cert_id, issue_date, issued_by=None):
    if issued_by is None:
        issued_by = SIGNATURE_NAME
    cert_dir = os.path.join(Config.CERTIFICATE_FOLDER, cert_id)
    os.makedirs(cert_dir, exist_ok=True)

    qr_path = os.path.join(cert_dir, "qr.png")
    generate_qr(cert_id, qr_path)

    pdf_path = os.path.join(cert_dir, "certificate.pdf")
    W, H = landscape(A4)

    c = canvas.Canvas(pdf_path, pagesize=landscape(A4))

    c.setFillColor(CREAM)
    c.rect(0, 0, W, H, fill=1, stroke=0)

    c.setFillColor(GOLD)
    c.rect(0, H - 8, W, 8, fill=1, stroke=0)
    c.setFillColor(GOLD_DARK)
    c.rect(0, H - 8, W * 0.35, 8, fill=1, stroke=0)

    c.setFillColor(GOLD)
    c.rect(0, 0, 8, H, fill=1, stroke=0)
    c.setFillColor(GOLD_DARK)
    c.rect(0, 0, 3, H, fill=1, stroke=0)

    margin = 28
    c.setStrokeColor(GOLD)
    c.setLineWidth(2)
    c.rect(margin, margin, W - 2 * margin, H - 2 * margin, fill=0, stroke=1)

    c.setStrokeColor(GOLD_LIGHT)
    c.setLineWidth(0.8)
    inner_margin = 36
    c.rect(inner_margin, inner_margin, W - 2 * inner_margin, H - 2 * inner_margin, fill=0, stroke=1)

    logo_size = 36
    draw_logo(c, inner_margin + 8, H - inner_margin - 8, logo_size)

    c.setFillColor(GOLD_DARK)
    c.setFont("Times-Bold", 15)
    c.drawCentredString(W / 2, H - 50, "CERTIFYPRO")

    c.setFillColor(TEXT_MUTED)
    c.setFont("Times-Roman", 9)
    c.drawCentredString(W / 2, H - 64, "AI-Powered Certificate Generation & Verification System")

    line_y = H - 78
    c.setStrokeColor(GOLD_LIGHT)
    c.setLineWidth(0.6)
    c.line(inner_margin + 80, line_y, W - inner_margin - 80, line_y)

    c.setFillColor(GOLD_DARK)
    c.setFont("Times-Bold", 32)
    c.drawCentredString(W / 2, H - 120, "Certificate of Completion")

    c.setFillColor(TEXT_MUTED)
    c.setFont("Times-Roman", 13)
    c.drawCentredString(W / 2, H - 148, "This is to certify that")

    try:
        c.setFillColor(GOLD_DARK)
        c.setFont("Times-Bold", 26)
        c.drawCentredString(W / 2, H - 183, student_name)
    except Exception:
        c.setFillColor(GOLD_DARK)
        c.setFont("Helvetica-Bold", 24)
        c.drawCentredString(W / 2, H - 183, student_name)

    c.setFillColor(TEXT_MUTED)
    c.setFont("Times-Roman", 13)
    c.drawCentredString(W / 2, H - 208, "has successfully completed the course")

    c.setFillColor(GOLD_DARK)
    c.setFont("Times-Bold", 18)
    c.drawCentredString(W / 2, H - 234, course_name)

    c.setFillColor(TEXT_MUTED)
    c.setFont("Times-Roman", 11)
    c.drawCentredString(W / 2, H - 254, "with a grade of")

    c.setFillColor(GOLD)
    c.setFont("Times-Bold", 24)
    c.drawCentredString(W / 2, H - 280, grade)

    grade_pct = (marks_obtained / total_marks * 100) if total_marks > 0 else 0
    c.setFillColor(TEXT_MUTED)
    c.setFont("Times-Roman", 10)
    c.drawCentredString(W / 2, H - 298, f"Score: {marks_obtained:.1f}/{total_marks:.0f}  |  Percentage: {grade_pct:.1f}%")

    sep_y = H - 318
    c.setStrokeColor(GOLD_LIGHT)
    c.setLineWidth(0.4)
    c.line(inner_margin + 80, sep_y, W - inner_margin - 80, sep_y)

    date_str = issue_date.strftime("%B %d, %Y") if hasattr(issue_date, 'strftime') else str(issue_date)

    # ── Left column: signature + issue info ──
    left_x = margin + 40
    sig_w = 160

    c.setStrokeColor(GOLD)
    c.setLineWidth(1.2)
    c.line(left_x, 195, left_x + sig_w, 195)
    c.setFillColor(GOLD_DARK)
    c.setFont("Times-Bold", 10)
    c.drawString(left_x, 181, SIGNATURE_NAME)
    c.setFillColor(TEXT_MUTED)
    c.setFont("Times-Roman", 8)
    c.drawString(left_x, 169, "Authorized Signature")

    c.setFillColor(TEXT_DARK)
    c.setFont("Times-Roman", 9)
    c.drawString(left_x, 148, f"Issue Date: {date_str}")
    c.drawString(left_x, 134, f"Certificate ID: {cert_id}")

    # ── Center: gold badge ──
    draw_badge(c, W / 2, 140, radius=40)

    # ── Right column: issued by + QR ──
    right_x = W - margin - 40

    c.setFillColor(TEXT_DARK)
    c.setFont("Times-Bold", 9)
    c.drawRightString(right_x, 195, f"Issued by: {issued_by}")
    c.setFillColor(TEXT_MUTED)
    c.setFont("Times-Roman", 8)
    c.drawRightString(right_x, 183, "System Administrator")

    qr_size = 60
    qr_x = right_x - qr_size
    c.drawImage(qr_path, qr_x, 115, width=qr_size, height=qr_size, preserveAspectRatio=True)

    c.setFillColor(TEXT_MUTED)
    c.setFont("Times-Roman", 7)
    c.drawRightString(right_x, 38, "Verify at: http://localhost:5000/verify/" + cert_id)

    c.save()
    return pdf_path, qr_path
