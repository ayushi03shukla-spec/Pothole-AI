"""
utils/pdf_export.py
Builds a PDF report of a user's detection history using reportlab.
"""

import os
import uuid
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
)


def generate_pdf_report(detections: list, user_name: str, report_folder: str) -> str:
    """
    detections: list of Detection.to_dict() results
    Returns the full path of the generated PDF file.
    """
    os.makedirs(report_folder, exist_ok=True)
    filename = f"pothole_report_{uuid.uuid4().hex[:8]}.pdf"
    full_path = os.path.join(report_folder, filename)

    doc = SimpleDocTemplate(full_path, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("Pothole AI — Detection Report", styles["Title"]))
    elements.append(Paragraph(f"User: {user_name}", styles["Normal"]))
    elements.append(
        Paragraph(f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}", styles["Normal"])
    )
    elements.append(Spacer(1, 16))

    table_data = [["ID", "Date", "Potholes", "Confidence", "Severity", "Location"]]
    for d in detections:
        location = (
            f"{d['latitude']:.4f}, {d['longitude']:.4f}"
            if d["latitude"] is not None and d["longitude"] is not None else "—"
        )
        table_data.append([
            str(d["id"]),
            (d["detected_at"] or "")[:10],
            str(d["pothole_count"]),
            f"{d['confidence']:.2f}" if d["confidence"] is not None else "—",
            (d["severity"] or "—").upper(),
            location,
        ])

    table = Table(table_data, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2c3e50")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f4f6f7")]),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ]))
    elements.append(table)

    doc.build(elements)
    return full_path
