"""
pdf_export.py
-------------
Generates a professional PDF report combining all 3 transformation modules.
Uses fpdf2 — completely free, no external services needed.
"""

import re
import unicodedata
from datetime import datetime

# fpdf2's built-in core fonts (Helvetica etc.) only support the Latin-1
# character set. The Groq model frequently returns "smart" punctuation
# (em dashes, curly quotes, ellipses, bullets) that falls outside that
# range and raises FPDFUnicodeEncodingException. We normalise those
# characters to safe ASCII equivalents before anything is written to the
# PDF, rather than switching to a Unicode font (keeps the file small and
# avoids bundling extra font files).
_UNICODE_REPLACEMENTS = {
    "\u2018": "'", "\u2019": "'",       # ' '
    "\u201c": '"', "\u201d": '"',       # " "
    "\u2013": "-", "\u2014": "-",       # – —
    "\u2026": "...",                     # …
    "\u2022": "-", "\u25cf": "-",       # • ●
    "\u00a0": " ",                       # non-breaking space
    "\u2039": "<", "\u203a": ">",       # ‹ ›
    "\u00ab": "<<", "\u00bb": ">>",     # « »
}


def _sanitize(text) -> str:
    """Make text safe for fpdf2's core (Latin-1 only) fonts."""
    if text is None:
        return ""
    text = str(text)
    for bad, good in _UNICODE_REPLACEMENTS.items():
        text = text.replace(bad, good)
    # Strip accents to their base letter (e.g. café -> cafe) instead of
    # leaving combining marks that are also outside Latin-1.
    decomposed = unicodedata.normalize("NFKD", text)
    stripped = "".join(c for c in decomposed if not unicodedata.combining(c))
    # Final safety net: anything still outside Latin-1 becomes "?"
    # instead of crashing PDF generation.
    return stripped.encode("latin-1", "replace").decode("latin-1")


def _clean_text(text: str) -> str:
    """Remove markdown symbols and sanitize for PDF rendering."""
    text = re.sub(r'#{1,3}\s*', '', text)
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    text = re.sub(r'`(.*?)`', r'\1', text)
    return _sanitize(text.strip())


def _split_into_sections(content: str) -> list:
    """Split markdown content into (heading, body) pairs."""
    sections = []
    current_heading = None
    current_body = []

    for line in content.split('\n'):
        line = line.strip()
        if line.startswith('## '):
            if current_heading:
                sections.append((current_heading, '\n'.join(current_body).strip()))
            current_heading = _sanitize(line.replace('## ', '').strip())
            current_body = []
        elif line:
            current_body.append(_clean_text(line))

    if current_heading:
        sections.append((current_heading, '\n'.join(current_body).strip()))

    return sections


def generate_pdf(
    company: str,
    sector: str,
    maturity: str,
    results: dict,
    modules: list,
) -> bytes:
    """
    Generate a professional PDF combining all 3 transformation modules.
    Returns PDF as bytes for Streamlit download.
    """
    try:
        from fpdf import FPDF
    except ImportError:
        # Return a simple placeholder if fpdf2 not installed
        return b"PDF generation requires fpdf2. Run: pip install fpdf2"

    # Sanitize all inputs up front so every downstream use (title, footer,
    # meta table, etc.) is already safe for the Latin-1-only core fonts.
    company = _sanitize(company)
    sector = _sanitize(sector)
    maturity = _sanitize(maturity)

    class PDF(FPDF):
        def header(self):
            pass

        def footer(self):
            self.set_y(-15)
            self.set_font('Helvetica', 'I', 8)
            self.set_text_color(150, 150, 150)
            self.cell(0, 10, f'Transformation Roadmap - {company} - Page {self.page_no()}', align='C')

    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.set_margins(20, 20, 20)

    # ── Cover Page ────────────────────────────────────────────────────────────
    pdf.add_page()

    # Dark header block
    pdf.set_fill_color(13, 21, 38)
    pdf.rect(0, 0, 210, 80, 'F')

    # Accent line
    pdf.set_fill_color(59, 130, 246)
    pdf.rect(0, 0, 210, 3, 'F')

    # Title
    pdf.set_y(25)
    pdf.set_font('Helvetica', 'B', 28)
    pdf.set_text_color(241, 245, 249)
    pdf.cell(0, 12, 'Transformation Roadmap', align='C', ln=True)

    pdf.set_font('Helvetica', '', 14)
    pdf.set_text_color(148, 163, 184)
    pdf.cell(0, 8, company, align='C', ln=True)

    # Reset
    pdf.set_y(95)

    # Meta info box
    pdf.set_fill_color(240, 244, 255)
    pdf.set_draw_color(200, 210, 230)
    pdf.rect(20, 90, 170, 46, 'FD')

    pdf.set_y(97)
    pdf.set_font('Helvetica', 'B', 10)
    pdf.set_text_color(30, 41, 59)
    meta_items = [
        ("Organisation", company),
        ("Sector", sector),
        ("Current Maturity", maturity),
        ("Date Generated", datetime.now().strftime("%d %B %Y")),
    ]
    for label, value in meta_items:
        pdf.set_x(30)
        pdf.set_font('Helvetica', 'B', 9)
        pdf.set_text_color(100, 116, 139)
        pdf.cell(55, 7, label.upper(), ln=False)
        pdf.set_font('Helvetica', '', 9)
        pdf.set_text_color(30, 41, 59)
        pdf.cell(0, 7, value, ln=True)

    # Modules overview
    pdf.set_y(150)
    pdf.set_font('Helvetica', 'B', 11)
    pdf.set_text_color(30, 41, 59)
    pdf.cell(0, 8, 'Modules Included', ln=True, align='C')

    pdf.set_y(162)
    module_labels = [
        ("ERP / SAP", "S/4HANA · Finance · Supply Chain"),
        ("CRM / Salesforce", "Sales · Service · Marketing Cloud"),
        ("Tech Enablement", "Cloud · AI/ML · Data · Integration"),
    ]
    col_w = 55
    start_x = 20
    for i, (title, sub) in enumerate(module_labels):
        x = start_x + i * (col_w + 2.5)
        pdf.set_fill_color(240, 244, 255)
        pdf.set_draw_color(200, 210, 230)
        pdf.rect(x, 160, col_w, 28, 'FD')
        pdf.set_xy(x + 2, 165)
        pdf.set_font('Helvetica', 'B', 9)
        pdf.set_text_color(30, 41, 59)
        pdf.cell(col_w - 4, 6, title, align='C', ln=True)
        pdf.set_x(x + 2)
        pdf.set_font('Helvetica', 'I', 7.5)
        pdf.set_text_color(100, 116, 139)
        pdf.cell(col_w - 4, 5, sub, align='C', ln=True)

    # Disclaimer
    pdf.set_y(210)
    pdf.set_font('Helvetica', 'I', 8)
    pdf.set_text_color(150, 150, 150)
    pdf.multi_cell(
        0, 5,
        "This roadmap was AI-generated for illustrative purposes. Recommendations should be validated "
        "by qualified transformation professionals before implementation.",
        align='C'
    )

    # ── Module Pages ──────────────────────────────────────────────────────────
    module_colors = {
        "erp":  (59, 130, 246),
        "crm":  (245, 158, 11),
        "tech": (6, 182, 212),
    }
    module_titles = {
        "erp":  ("ERP / SAP Transformation Roadmap", "S/4HANA · Finance · Supply Chain · Procurement"),
        "crm":  ("CRM / Salesforce Transformation Roadmap", "Sales Cloud · Service Cloud · Marketing Cloud"),
        "tech": ("Tech Enablement Roadmap", "Cloud Migration · AI/ML · Data Platform · Integration"),
    }

    for module_key in ["erp", "crm", "tech"]:
        content = results.get(module_key, "")
        if not content or content.startswith("⚠️"):
            continue

        pdf.add_page()
        r, g, b = module_colors[module_key]
        title, subtitle = module_titles[module_key]

        # Module header
        pdf.set_fill_color(13, 21, 38)
        pdf.rect(0, 0, 210, 35, 'F')
        pdf.set_fill_color(r, g, b)
        pdf.rect(0, 0, 210, 3, 'F')

        pdf.set_y(8)
        pdf.set_font('Helvetica', 'B', 16)
        pdf.set_text_color(241, 245, 249)
        pdf.cell(0, 9, title, align='C', ln=True)
        pdf.set_font('Helvetica', '', 9)
        pdf.set_text_color(148, 163, 184)
        pdf.cell(0, 6, subtitle, align='C', ln=True)

        pdf.set_y(42)

        # Parse and render sections
        sections = _split_into_sections(content)

        for heading, body in sections:
            # Section heading
            pdf.set_fill_color(r, g, b)
            pdf.set_text_color(255, 255, 255)
            pdf.set_font('Helvetica', 'B', 9)
            pdf.set_x(20)
            pdf.cell(170, 7, f"  {heading.upper()}", fill=True, ln=True)
            pdf.ln(2)

            # Body lines
            lines = [l.strip() for l in body.split('\n') if l.strip()]
            for line in lines:
                # Bullet points
                if line.startswith('- ') or line.startswith('• '):
                    line = line.lstrip('-•').strip()
                    pdf.set_x(24)
                    pdf.set_font('Helvetica', '', 8)
                    pdf.set_text_color(50, 65, 85)
                    pdf.set_fill_color(r, g, b)
                    # Bullet dot
                    pdf.set_xy(22, pdf.get_y() + 1.5)
                    pdf.set_fill_color(r, g, b)
                    pdf.circle(pdf.get_x(), pdf.get_y(), 1, 'F')
                    pdf.set_xy(26, pdf.get_y() - 1.5)
                    pdf.multi_cell(164, 5, line)
                else:
                    pdf.set_x(22)
                    pdf.set_font('Helvetica', '', 8)
                    pdf.set_text_color(50, 65, 85)
                    pdf.multi_cell(166, 5, line)

            pdf.ln(3)

    return bytes(pdf.output())
