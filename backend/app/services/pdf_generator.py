import io
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Register a Unicode-compatible font if available on OS
UNICODE_FONT = 'Helvetica'
for name, font_path in [
    ("Mangal", r"C:\Windows\Fonts\mangal.ttf"),
    ("Arial", r"C:\Windows\Fonts\arial.ttf"),
    ("SegoeUI", r"C:\Windows\Fonts\segoeui.ttf"),
    ("DejaVu", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
]:
    if Path(font_path).is_file():
        try:
            pdfmetrics.registerFont(TTFont(name, font_path))
            UNICODE_FONT = name
            break
        except Exception:
            pass


def generate_pdf_bytes(doc_data: Dict[str, Any]) -> bytes:
    """Generate binary PDF content for document with Unicode & Rupee symbol support."""
    buffer = io.BytesIO()
    pdf = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    story = []
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName=UNICODE_FONT,
        fontSize=16,
        leading=20,
        textColor=colors.HexColor('#1E293B'),
        alignment=1,  # Centered
        spaceAfter=15
    )

    section_title_style = ParagraphStyle(
        'SecTitle',
        parent=styles['Heading2'],
        fontName=UNICODE_FONT,
        fontSize=12,
        leading=15,
        textColor=colors.HexColor('#0F172A'),
        spaceBefore=10,
        spaceAfter=5
    )

    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontName=UNICODE_FONT,
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#334155'),
        spaceAfter=8
    )

    disclaimer_style = ParagraphStyle(
        'DisclaimerText',
        parent=styles['Normal'],
        fontName=UNICODE_FONT,
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor('#64748B'),
        alignment=1
    )

    # Document Header
    title_text = doc_data.get("title", "LEGAL NOTICE / COMPLAINT")
    story.append(Paragraph(f"<b>{title_text}</b>", title_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#CBD5E1'), spaceAfter=15))

    # Meta Table (Date, Reference, Quality Score)
    now_str = datetime.now(timezone.utc).strftime("%B %d, %Y")
    doc_id = str(doc_data.get("document_id") or doc_data.get("id") or "N/A")[:8]
    quality = doc_data.get("quality_score") or doc_data.get("quality", 8.0)

    meta_data = [
        [
            Paragraph(f"<b>Date:</b> {now_str}", body_style),
            Paragraph(f"<b>Ref ID:</b> {doc_id}", body_style),
            Paragraph(f"<b>Quality Rating:</b> {quality}/10", body_style)
        ]
    ]
    meta_table = Table(meta_data, colWidths=[180, 180, 140])
    meta_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 10))

    # Render Document Content Sections
    sections = doc_data.get("sections", [])
    for sec in sections:
        sec_title = sec.get("title", "")
        sec_content = sec.get("content", "")

        if sec_title:
            story.append(Paragraph(f"<b>{sec_title}</b>", section_title_style))

        lines = sec_content.split("\n")
        for line in lines:
            if line.strip():
                clean_line = (
                    line.replace("<", "&lt;")
                        .replace(">", "&gt;")
                        .replace("₹", "Rs. ")  # Ensure Rupee symbol safety across all ReportLab fonts
                )
                story.append(Paragraph(clean_line, body_style))

        story.append(Spacer(1, 6))

    # Signature Block
    story.append(Spacer(1, 15))
    sig_data = [
        [Paragraph("<b>ISSUED BY / COMPLAINANT:</b>", body_style), Paragraph("<b>VERIFICATION & SIGNATURE:</b>", body_style)],
        [Paragraph("____________________________<br/>Aggrieved Litigant", body_style), Paragraph("____________________________<br/>Date: _______________", body_style)]
    ]
    sig_table = Table(sig_data, colWidths=[250, 250])
    sig_table.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP')]))
    story.append(sig_table)

    # Mandatory Legal Disclaimer Footer
    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#E2E8F0'), spaceAfter=10))
    disclaimer_text = doc_data.get("disclaimer") or (
        "MANDATORY DISCLAIMER: LegalAId provides AI-assisted document drafting based on database statutory text. "
        "It does not constitute legal advice or replace a licensed advocate. Verify applicable law for your situation."
    )
    story.append(Paragraph(f"<i>{disclaimer_text}</i>", disclaimer_style))

    pdf.build(story)
    buffer.seek(0)
    return buffer.getvalue()
