"""
diagrams.py
-----------
Lightweight, dependency-free SVG diagram generation for the app.
No graphviz / matplotlib required — just plain SVG strings that
Streamlit can render inline via st.markdown(..., unsafe_allow_html=True).

Two kinds of visuals:
1. Architecture diagram — a simple, illustrative box-and-arrow layout
   per module (ERP / CRM / Tech) showing how the pieces typically fit
   together.
2. Phase flow diagram — pulls the "Phase 1 / 2 / 3" headings out of the
   AI-generated roadmap text and renders them as a left-to-right flow.
"""

import re

def compact_html(html: str) -> str:
    """Collapse to a single line with no blank lines or leading
    whitespace. Streamlit's markdown renderer only passes multi-line
    content through as raw HTML when it's one continuous block — any
    blank line inside it (which our multi-line f-strings introduce) or
    left-over indentation (>=4 spaces) makes it fall back to rendering
    the rest as a literal, unrendered code block."""
    lines = [ln.strip() for ln in html.strip().splitlines() if ln.strip()]
    return " ".join(lines)


# ── Static "typical architecture" layouts per module ───────────────────────
ARCHITECTURE_LAYOUTS = {
    "erp": [
        "Legacy ERP & Point Systems",
        "Data Migration & Cleansing",
        "SAP S/4HANA Core\n(Finance · Supply Chain · HR)",
        "Reporting & Analytics Layer",
    ],
    "crm": [
        "Customer Data Sources",
        "Data Integration Layer",
        "Salesforce Core\n(Sales · Service · Marketing Cloud)",
        "Customer 360 & Analytics",
    ],
    "tech": [
        "Legacy Infrastructure",
        "Cloud Migration\n(AWS / Azure / GCP)",
        "Platform Layer\n(APIs · Data · Security)",
        "AI/ML & Innovation Layer",
    ],
}


def _wrap_lines(label: str):
    """Split a label on explicit \n markers into separate tspan lines."""
    return label.split("\n")


def _box_with_text(x, y, w, h, label, color, text_size=11.5):
    lines = _wrap_lines(label)
    line_height = text_size + 3
    total_h = line_height * len(lines)
    start_y = y + h / 2 - total_h / 2 + line_height * 0.75

    tspans = "".join(
        f'<tspan x="{x + w / 2}" y="{start_y + i * line_height}">{ln}</tspan>'
        for i, ln in enumerate(lines)
    )

    return f'''
    <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10"
          fill="{color}22" stroke="{color}" stroke-width="1.5"/>
    <text text-anchor="middle" font-family="Inter, sans-serif"
          font-size="{text_size}" font-weight="600" fill="#e2e8f0">
      {tspans}
    </text>
    '''


def _arrow(x1, y, x2, color):
    return f'''
    <line x1="{x1}" y1="{y}" x2="{x2 - 8}" y2="{y}"
          stroke="{color}" stroke-width="2" marker-end="url(#arrowhead-{color.lstrip('#')})"/>
    '''


def render_architecture_diagram(module_key: str, color: str) -> str:
    """Return an SVG string showing a simple, illustrative architecture
    flow for the given module (erp / crm / tech)."""
    labels = ARCHITECTURE_LAYOUTS.get(module_key, ARCHITECTURE_LAYOUTS["tech"])
    n = len(labels)

    box_w, box_h = 160, 70
    gap = 40
    total_w = n * box_w + (n - 1) * gap
    width = total_w + 40
    height = box_h + 40
    y = 20

    boxes_svg = ""
    arrows_svg = ""
    for i, label in enumerate(labels):
        x = 20 + i * (box_w + gap)
        boxes_svg += _box_with_text(x, y, box_w, box_h, label, color)
        if i < n - 1:
            arrows_svg += _arrow(x + box_w, y + box_h / 2, x + box_w + gap, color)

    marker_id = f"arrowhead-{color.lstrip('#')}"
    svg = f'''
    <svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg"
         style="width:100%; height:auto; display:block;">
      <defs>
        <marker id="{marker_id}" markerWidth="8" markerHeight="8"
                refX="6" refY="4" orient="auto">
          <path d="M0,0 L8,4 L0,8 Z" fill="{color}"/>
        </marker>
      </defs>
      {arrows_svg}
      {boxes_svg}
    </svg>
    '''
    return compact_html(svg)


# ── Phase flow, parsed from AI-generated content ────────────────────────────
_PHASE_HEADING_RE = re.compile(
    r'^##\s*Phase\s*(\d+)\s*:?\s*([^(\n]+?)\s*(\([^)]*\))?\s*$',
    re.MULTILINE,
)


def extract_phases(content: str):
    """Pull Phase headings like '## Phase 1: Foundation (Months 1-4)' out of
    the AI-generated markdown. Returns a list of dicts, falls back to a
    generic 3-phase placeholder if none are found."""
    phases = []
    for match in _PHASE_HEADING_RE.finditer(content or ""):
        num, title, sub = match.groups()
        phases.append({
            "label": f"Phase {num}",
            "title": title.strip(),
            "sub": (sub or "").strip("()"),
        })

    if not phases:
        phases = [
            {"label": "Phase 1", "title": "Foundation", "sub": ""},
            {"label": "Phase 2", "title": "Core Implementation", "sub": ""},
            {"label": "Phase 3", "title": "Optimise & Scale", "sub": ""},
        ]
    return phases


def render_phase_flow(content: str, color: str) -> str:
    """Return an SVG left-to-right flow diagram of the roadmap phases."""
    phases = extract_phases(content)
    n = len(phases)

    box_w, box_h = 175, 78
    gap = 36
    total_w = n * box_w + (n - 1) * gap
    width = total_w + 40
    height = box_h + 40
    y = 20

    boxes_svg = ""
    arrows_svg = ""
    for i, phase in enumerate(phases):
        x = 20 + i * (box_w + gap)

        boxes_svg += f'''
        <rect x="{x}" y="{y}" width="{box_w}" height="{box_h}" rx="10"
              fill="{color}18" stroke="{color}" stroke-width="1.5"/>
        <rect x="{x}" y="{y}" width="{box_w}" height="22" rx="10"
              fill="{color}"/>
        <rect x="{x}" y="{y + 11}" width="{box_w}" height="11" fill="{color}"/>
        <text x="{x + box_w / 2}" y="{y + 15}" text-anchor="middle"
              font-family="Inter, sans-serif" font-size="10" font-weight="700"
              letter-spacing="0.06em" fill="#ffffff">{phase["label"].upper()}</text>
        <text x="{x + box_w / 2}" y="{y + 45}" text-anchor="middle"
              font-family="Inter, sans-serif" font-size="12" font-weight="600"
              fill="#e2e8f0">{phase["title"]}</text>
        <text x="{x + box_w / 2}" y="{y + 63}" text-anchor="middle"
              font-family="Inter, sans-serif" font-size="9.5"
              fill="#94a3b8">{phase["sub"]}</text>
        '''

        if i < n - 1:
            arrows_svg += _arrow(x + box_w, y + box_h / 2, x + box_w + gap, color)

    marker_id = f"arrowhead-{color.lstrip('#')}"
    svg = f'''
    <svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg"
         style="width:100%; height:auto; display:block;">
      <defs>
        <marker id="{marker_id}" markerWidth="8" markerHeight="8"
                refX="6" refY="4" orient="auto">
          <path d="M0,0 L8,4 L0,8 Z" fill="{color}"/>
        </marker>
      </defs>
      {arrows_svg}
      {boxes_svg}
    </svg>
    '''
    return compact_html(svg)
