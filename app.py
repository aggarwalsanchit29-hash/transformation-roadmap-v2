"""
Transformation Roadmap Generator
---------------------------------
Generates structured transformation roadmaps across ERP/SAP,
CRM/Salesforce, and Tech Enablement modules for any sector.

Run: streamlit run app.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
from modules import SECTORS, MATURITY_LEVELS, get_module_context
from transformation import generate_module
from pdf_export import generate_pdf
from diagrams import render_architecture_diagram, render_phase_flow, compact_html

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Transformation Roadmap Generator",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=DM+Serif+Display:wght@400;700&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    .stApp { background-color: #080c14; color: #e2e8f0; }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d1526 0%, #080c14 100%);
        border-right: 1px solid #1a2744;
    }
    [data-testid="stSidebar"] * { color: #e2e8f0 !important; }

    .hero {
        background: linear-gradient(135deg, #0d1526 0%, #111d3a 100%);
        border: 1px solid #1a2744;
        border-radius: 14px;
        padding: 2.2rem 2.5rem;
        margin-bottom: 1.5rem;
        position: relative;
        overflow: hidden;
    }
    .hero::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
        background: linear-gradient(90deg, #3b82f6, #8b5cf6, #06b6d4);
    }
    .hero h1 {
        font-family: 'DM Serif Display', serif;
        font-size: 2rem;
        color: #f1f5f9;
        margin: 0 0 0.4rem 0;
    }
    .hero p { color: #64748b; margin: 0; font-size: 0.9rem; }

    .module-card {
        background: #0d1526;
        border: 1px solid #1a2744;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        transition: border-color 0.2s;
    }
    .module-card:hover { border-color: #3b82f6; }

    .module-header {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin-bottom: 1rem;
        padding-bottom: 0.75rem;
        border-bottom: 1px solid #1a2744;
    }
    .module-icon {
        width: 40px; height: 40px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.2rem;
        flex-shrink: 0;
    }
    .module-title {
        font-weight: 600;
        color: #f1f5f9;
        font-size: 1rem;
    }
    .module-subtitle {
        font-size: 0.75rem;
        color: #64748b;
        margin-top: 0.1rem;
    }

    .roadmap-content {
        background: #0d1526;
        border: 1px solid #1a2744;
        border-radius: 10px;
        padding: 1.8rem;
        line-height: 1.85;
        color: #cbd5e1;
        font-size: 0.9rem;
    }
    .roadmap-content h2 {
        color: #f1f5f9;
        font-size: 0.95rem;
        font-weight: 600;
        margin: 1.4rem 0 0.5rem 0;
        padding-bottom: 0.35rem;
        border-bottom: 1px solid #1a2744;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }
    .roadmap-content h2:first-child { margin-top: 0; }
    .roadmap-content ul { padding-left: 1.2rem; }
    .roadmap-content li { margin-bottom: 0.3rem; }

    .phase-badge {
        display: inline-block;
        padding: 0.2rem 0.65rem;
        border-radius: 20px;
        font-size: 0.7rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin-right: 0.4rem;
        margin-bottom: 0.3rem;
    }
    .phase-1 { background: rgba(59,130,246,0.15); color: #60a5fa; border: 1px solid rgba(59,130,246,0.3); }
    .phase-2 { background: rgba(139,92,246,0.15); color: #a78bfa; border: 1px solid rgba(139,92,246,0.3); }
    .phase-3 { background: rgba(6,182,212,0.15); color: #22d3ee; border: 1px solid rgba(6,182,212,0.3); }

    .maturity-bar {
        background: #1a2744;
        border-radius: 6px;
        height: 6px;
        margin-top: 0.4rem;
        overflow: hidden;
    }
    .maturity-fill {
        height: 100%;
        border-radius: 6px;
        background: linear-gradient(90deg, #3b82f6, #8b5cf6);
    }

    .summary-card {
        background: #0d1526;
        border: 1px solid #1a2744;
        border-radius: 10px;
        padding: 1.2rem;
        text-align: center;
    }
    .summary-number {
        font-size: 2rem;
        font-weight: 700;
        color: #f1f5f9;
        line-height: 1;
    }
    .summary-label {
        font-size: 0.72rem;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin-top: 0.3rem;
    }

    .stButton > button {
        background: linear-gradient(135deg, #2563eb, #7c3aed) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        width: 100% !important;
        padding: 0.65rem !important;
        font-size: 0.9rem !important;
    }
    .stButton > button:hover { opacity: 0.85 !important; }

    .stTextInput > div > div > input {
        background: #0d1526 !important;
        border: 1px solid #1a2744 !important;
        border-radius: 8px !important;
        color: #e2e8f0 !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 3px rgba(59,130,246,0.15) !important;
    }
    .stSelectbox > div > div {
        background: #0d1526 !important;
        border: 1px solid #1a2744 !important;
        border-radius: 8px !important;
        color: #e2e8f0 !important;
    }

    .stTabs [data-baseweb="tab-list"] {
        background: #0d1526;
        border-radius: 8px;
        padding: 4px;
        gap: 4px;
        border: 1px solid #1a2744;
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 6px;
        color: #64748b;
        font-size: 0.85rem;
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        background: #111d3a !important;
        color: #e2e8f0 !important;
    }

    .info-bar {
        background: rgba(59,130,246,0.08);
        border: 1px solid rgba(59,130,246,0.25);
        border-radius: 8px;
        padding: 0.85rem 1.2rem;
        color: #93c5fd;
        font-size: 0.85rem;
        margin-bottom: 1.5rem;
    }

    .stProgress > div > div {
        background: linear-gradient(90deg, #3b82f6, #8b5cf6) !important;
    }

    hr { border-color: #1a2744 !important; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:0.5rem 0 1.5rem 0; border-bottom:1px solid #1a2744; margin-bottom:1.5rem;">
        <div style="font-size:1.1rem; font-weight:700; color:#f1f5f9;">🗺️ Transformation Roadmap</div>
        <div style="font-size:0.75rem; color:#64748b; margin-top:0.25rem;">AI-powered · Free · Instant</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("**🏢 Organisation**")
    company_name = st.text_input(
        "Company",
        placeholder="e.g. Barclays, NHS, Tesco...",
        label_visibility="collapsed"
    )

    st.markdown("<div style='margin-top:1rem'></div>", unsafe_allow_html=True)
    st.markdown("**🏭 Sector**")
    selected_sector = st.selectbox(
        "Sector",
        list(SECTORS.keys()),
        format_func=lambda x: f"{SECTORS[x]['icon']} {x}",
        label_visibility="collapsed"
    )

    st.markdown("<div style='margin-top:1rem'></div>", unsafe_allow_html=True)
    st.markdown("**📊 Current Maturity Level**")
    selected_maturity = st.selectbox(
        "Maturity",
        list(MATURITY_LEVELS.keys()),
        label_visibility="collapsed"
    )

    st.markdown("<div style='margin-top:1.5rem'></div>", unsafe_allow_html=True)
    generate_btn = st.button("🚀 Generate Roadmap", use_container_width=True)

    maturity_pct = MATURITY_LEVELS[selected_maturity]["pct"]
    st.markdown(f"""
    <div style="margin-top:1rem;">
        <div style="font-size:0.72rem; color:#64748b; margin-bottom:0.4rem;">
            Maturity: {selected_maturity}
        </div>
        <div class="maturity-bar">
            <div class="maturity-fill" style="width:{maturity_pct}%"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="margin-top:2rem; padding-top:1.5rem; border-top:1px solid #1a2744;
                font-size:0.75rem; color:#64748b; line-height:1.7;">
        <strong style="color:#94a3b8;">3 Modules Generated</strong><br>
        🔷 ERP / SAP Roadmap<br>
        🔶 CRM / Salesforce Roadmap<br>
        🔹 Tech Enablement Roadmap<br><br>
        <strong style="color:#94a3b8;">Output</strong><br>
        📄 Combined PDF download
    </div>
    """, unsafe_allow_html=True)

# ── Main ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <h1>🗺️ Transformation Roadmap Generator</h1>
    <p>AI-generated ERP, CRM & Tech transformation roadmaps — tailored by sector and maturity level</p>
</div>
""", unsafe_allow_html=True)

# Welcome state
if not generate_btn or not company_name:
    c1, c2, c3 = st.columns(3)
    modules_info = [
        ("🔷", "#3b82f6", "ERP / SAP", "S/4HANA migration, finance transformation, process standardisation"),
        ("🔶", "#f59e0b", "CRM / Salesforce", "Sales Cloud, Service Cloud, Marketing Cloud adoption roadmap"),
        ("🔹", "#06b6d4", "Tech Enablement", "Cloud migration, AI/ML, data platform, integration architecture"),
    ]
    for col, (icon, color, title, desc) in zip([c1, c2, c3], modules_info):
        with col:
            st.markdown(f"""
            <div class="module-card" style="text-align:center; padding:1.8rem; border-color:{color}30;">
                <div style="font-size:2.5rem; margin-bottom:0.75rem;">{icon}</div>
                <div style="font-weight:700; color:#f1f5f9; font-size:1rem; margin-bottom:0.4rem;">{title}</div>
                <div style="font-size:0.8rem; color:#64748b;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("""
    <div class="info-bar">
        💡 Enter your organisation name and select your sector, then click
        <strong>Generate Roadmap</strong> to get all 3 modules instantly with a PDF download.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="module-card">
        <div style="font-size:0.7rem; font-weight:700; color:#64748b; text-transform:uppercase;
                    letter-spacing:0.1em; margin-bottom:1rem;">Example Organisations</div>
        <div style="display:grid; grid-template-columns:repeat(3,1fr); gap:1.5rem;">
            <div>
                <div style="font-size:0.72rem; color:#64748b; margin-bottom:0.5rem;">🏦 Financial Services</div>
                <div style="font-size:0.85rem; color:#cbd5e1; line-height:1.8;">Barclays · HSBC<br>Lloyds · Aviva</div>
            </div>
            <div>
                <div style="font-size:0.72rem; color:#64748b; margin-bottom:0.5rem;">🏥 Healthcare</div>
                <div style="font-size:0.85rem; color:#cbd5e1; line-height:1.8;">NHS Trust · Bupa<br>AstraZeneca · GSK</div>
            </div>
            <div>
                <div style="font-size:0.72rem; color:#64748b; margin-bottom:0.5rem;">🛒 Retail</div>
                <div style="font-size:0.85rem; color:#cbd5e1; line-height:1.8;">Tesco · M&S<br>Sainsbury's · ASOS</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── Generate Roadmap ──────────────────────────────────────────────────────────
if generate_btn and company_name:
    sector_info = SECTORS[selected_sector]
    maturity_info = MATURITY_LEVELS[selected_maturity]
    context = get_module_context(selected_sector, selected_maturity)

    # Header
    st.markdown(f"""
    <div style="display:flex; align-items:center; gap:1rem; margin-bottom:1.5rem;">
        <div style="width:52px; height:52px; border-radius:10px;
                    background:{sector_info['color']}18; border:1px solid {sector_info['color']}40;
                    display:flex; align-items:center; justify-content:center;
                    font-size:1.4rem; flex-shrink:0;">
            {sector_info['icon']}
        </div>
        <div>
            <div style="font-family:'DM Serif Display',serif; font-size:1.8rem; color:#f1f5f9;">
                {company_name}
            </div>
            <div style="color:#64748b; font-size:0.82rem; margin-top:0.15rem;">
                {selected_sector} &nbsp;·&nbsp; {selected_maturity} Maturity
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Generate all 3 modules
    modules = [
        {
            "key": "erp",
            "title": "ERP / SAP",
            "subtitle": "S/4HANA · Finance · Supply Chain",
            "icon": "🔷",
            "color": "#3b82f6",
        },
        {
            "key": "crm",
            "title": "CRM / Salesforce",
            "subtitle": "Sales · Service · Marketing Cloud",
            "icon": "🔶",
            "color": "#f59e0b",
        },
        {
            "key": "tech",
            "title": "Tech Enablement",
            "subtitle": "Cloud · AI/ML · Data · Integration",
            "icon": "🔹",
            "color": "#06b6d4",
        },
    ]

    # Progress bar while generating
    progress = st.progress(0, text="Generating transformation roadmap...")
    results = {}

    for i, module in enumerate(modules):
        progress.progress(
            (i + 1) * 30,
            text=f"Generating {module['title']} module..."
        )
        results[module["key"]] = generate_module(
            company=company_name,
            sector=selected_sector,
            maturity=selected_maturity,
            module_type=module["key"],
            context=context,
        )

    progress.progress(100, text="Roadmap complete!")
    progress.empty()

    # Summary row
    c1, c2, c3 = st.columns(3)
    summary_items = [
        ("3", "Modules Generated"),
        ("12-18", "Months Timeline"),
        (maturity_info["next"], "Target Maturity"),
    ]
    for col, (num, label) in zip([c1, c2, c3], summary_items):
        with col:
            st.markdown(f"""
            <div class="summary-card">
                <div class="summary-number">{num}</div>
                <div class="summary-label">{label}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div style='margin-top:1.5rem'></div>", unsafe_allow_html=True)

    # Tabs for each module
    tab1, tab2, tab3 = st.tabs([
        "🔷 ERP / SAP",
        "🔶 CRM / Salesforce",
        "🔹 Tech Enablement"
    ])

    tab_map = {tab1: "erp", tab2: "crm", tab3: "tech"}
    for tab, key in tab_map.items():
        module = next(m for m in modules if m["key"] == key)
        with tab:
            st.markdown(f"""
            <div class="module-header" style="margin-bottom:1rem;">
                <div class="module-icon" style="background:{module['color']}18; border:1px solid {module['color']}30;">
                    {module['icon']}
                </div>
                <div>
                    <div class="module-title">{module['title']} Transformation Roadmap</div>
                    <div class="module-subtitle">{module['subtitle']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            content = results[key]
            if content.startswith("⚠️"):
                st.error(content)
            else:
                # Basic visual diagrams: illustrative architecture + phase flow
                arch_svg = render_architecture_diagram(key, module["color"])
                phase_svg = render_phase_flow(content, module["color"])

                st.markdown(compact_html(f"""
                <div class="module-card" style="padding:1.2rem 1.2rem 0.6rem 1.2rem;">
                    <div style="font-size:0.7rem; font-weight:700; color:#64748b;
                                text-transform:uppercase; letter-spacing:0.08em; margin-bottom:0.8rem;">
                        📐 Illustrative Architecture
                    </div>
                    {arch_svg}
                </div>
                <div class="module-card" style="padding:1.2rem 1.2rem 0.6rem 1.2rem;">
                    <div style="font-size:0.7rem; font-weight:700; color:#64748b;
                                text-transform:uppercase; letter-spacing:0.08em; margin-bottom:0.8rem;">
                        🧭 Roadmap Phases
                    </div>
                    {phase_svg}
                </div>
                """), unsafe_allow_html=True)

                st.markdown(
                    f'<div class="roadmap-content">{content}</div>',
                    unsafe_allow_html=True
                )

    # PDF Download
    st.markdown("<div style='margin-top:1.5rem'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size:0.7rem; font-weight:700; color:#64748b; text-transform:uppercase;
                letter-spacing:0.1em; margin-bottom:0.75rem;">Download Full Report</div>
    """, unsafe_allow_html=True)

    col_pdf, col_md = st.columns(2)

    with col_pdf:
        if not any(v.startswith("⚠️") for v in results.values()):
            pdf_bytes = generate_pdf(
                company=company_name,
                sector=selected_sector,
                maturity=selected_maturity,
                results=results,
                modules=modules,
            )
            st.download_button(
                label="⬇️ Download PDF Report",
                data=pdf_bytes,
                file_name=f"{company_name.replace(' ','_')}_Transformation_Roadmap.pdf",
                mime="application/pdf",
                use_container_width=True,
            )

    with col_md:
        md_content = f"# {company_name} — Transformation Roadmap\n\n"
        md_content += f"**Sector:** {selected_sector} | **Maturity:** {selected_maturity}\n\n---\n\n"
        for module in modules:
            md_content += f"## {module['icon']} {module['title']}\n\n{results[module['key']]}\n\n---\n\n"

        st.download_button(
            label="⬇️ Download Markdown",
            data=md_content,
            file_name=f"{company_name.replace(' ','_')}_Transformation_Roadmap.md",
            mime="text/markdown",
            use_container_width=True,
        )
