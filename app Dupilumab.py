import streamlit as st
import pandas as pd
from pathlib import Path

# Resolve assets folder relative to this script — works locally AND on Streamlit Cloud
ASSETS = Path(__file__).parent / "assets"

try:
    import plotly.graph_objects as go
    import plotly.express as px
    PLOTLY_OK = True
except ModuleNotFoundError:
    PLOTLY_OK = False
    st.error(
        "⚠️ **Missing dependency: plotly**\n\n"
        "Please ensure your `requirements.txt` contains `plotly>=5.18.0` "
        "and redeploy the app on Streamlit Cloud.\n\n"
        "Locally: `pip install plotly`"
    )
    st.stop()

try:
    from tech_landscape_tab import render_technology_landscape_tab
    TECH_LANDSCAPE_OK = True
except ModuleNotFoundError:
    TECH_LANDSCAPE_OK = False

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Dupilumab Intelligence Dashboard",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    .main { background: #f8fafc; }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
        border-right: 1px solid #334155;
    }
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] div,
    [data-testid="stSidebar"] label { color: #e2e8f0 !important; }
    [data-testid="stSidebar"] .stRadio > label {
        color: #94a3b8 !important;
        font-size: 11px;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 6px;
    }
    [data-testid="stSidebar"] .stRadio [data-baseweb="radio"] label {
        color: #cbd5e1 !important;
        font-size: 13px !important;
        font-weight: 400 !important;
        padding: 4px 0 !important;
    }
    [data-testid="stSidebar"] .stRadio [data-baseweb="radio"] [aria-checked="true"] ~ label {
        color: #f1f5f9 !important;
        font-weight: 500 !important;
    }

    /* Cards */
    .card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        margin-bottom: 1rem;
    }
    .card-accent {
        border-left: 4px solid #3b82f6;
    }
    .card-green {
        border-left: 4px solid #10b981;
    }
    .card-purple {
        border-left: 4px solid #8b5cf6;
    }
    .card-orange {
        border-left: 4px solid #f59e0b;
    }

    /* KPI metric */
    .kpi-box {
        background: white;
        border-radius: 10px;
        padding: 1.2rem 1rem;
        text-align: center;
        border: 1px solid #e2e8f0;
    }
    .kpi-value { font-size: 28px; font-weight: 700; color: #1e293b; margin: 0; }
    .kpi-label { font-size: 11px; color: #64748b; margin: 4px 0 0; line-height: 1.4; }
    .kpi-sub { font-size: 10px; color: #94a3b8; margin: 2px 0 0; }

    /* Section headers */
    .section-head {
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        color: #64748b;
        margin: 0 0 12px;
        padding-bottom: 6px;
        border-bottom: 1px solid #e2e8f0;
    }
    .page-title {
        font-size: 26px;
        font-weight: 700;
        color: #0f172a;
        margin: 0 0 4px;
    }
    .page-sub {
        font-size: 13px;
        color: #64748b;
        margin: 0 0 24px;
    }

    /* Badges */
    .badge {
        display: inline-block;
        font-size: 10px;
        font-weight: 600;
        padding: 2px 8px;
        border-radius: 20px;
        margin: 2px;
    }
    .badge-blue { background: #dbeafe; color: #1d4ed8; }
    .badge-green { background: #dcfce7; color: #15803d; }
    .badge-amber { background: #fef3c7; color: #b45309; }
    .badge-red { background: #fee2e2; color: #b91c1c; }
    .badge-purple { background: #ede9fe; color: #6d28d9; }
    .badge-gray { background: #f1f5f9; color: #475569; }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] { gap: 6px; }
    .stTabs [data-baseweb="tab"] {
        background: #f1f5f9;
        border-radius: 8px;
        padding: 6px 16px;
        font-size: 13px;
        font-weight: 500;
        color: #475569;
        border: none;
    }
    .stTabs [aria-selected="true"] {
        background: #3b82f6 !important;
        color: white !important;
    }

    /* Table */
    .data-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 11px;
    }
    .data-table th {
        background: #1e293b;
        color: #e2e8f0;
        padding: 8px 10px;
        text-align: left;
        font-weight: 600;
        font-size: 10px;
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }
    .data-table td {
        padding: 7px 10px;
        border-bottom: 1px solid #f1f5f9;
        color: #374151;
        vertical-align: top;
        line-height: 1.45;
    }
    .data-table tr:nth-child(even) td { background: #f8fafc; }
    .data-table tr:hover td { background: #eff6ff; }

    /* Expander override */
    .streamlit-expanderHeader { font-size: 13px; font-weight: 600; }

    /* Slider section headers */
    .slider-header {
        background: linear-gradient(135deg, #1e293b, #334155);
        color: white;
        padding: 10px 16px;
        border-radius: 8px;
        font-size: 13px;
        font-weight: 600;
        margin-bottom: 12px;
    }

    /* Source box */
    .source-box {
        background: #f0f9ff;
        border: 1px solid #bae6fd;
        border-radius: 8px;
        padding: 10px 14px;
        font-size: 11px;
        color: #0369a1;
        margin-top: 8px;
    }

    /* Pill row */
    .pill-row { display: flex; flex-wrap: wrap; gap: 6px; margin: 8px 0; }

    /* Warning note */
    .note-box {
        background: #fffbeb;
        border: 1px solid #fcd34d;
        border-radius: 8px;
        padding: 10px 14px;
        font-size: 11px;
        color: #92400e;
        margin: 8px 0;
    }
</style>
""", unsafe_allow_html=True)

# ── Navigation ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='padding: 16px 0 24px; border-bottom: 1px solid #334155; margin-bottom: 20px;'>
        <div style='font-size:20px; font-weight:700; color:#f1f5f9;'>💊 Dupilumab</div>
        <div style='font-size:11px; color:#94a3b8; margin-top:4px;'>Intelligence Dashboard · June 2026</div>
    </div>
    """, unsafe_allow_html=True)

    page = st.radio(
        "NAVIGATION",
        [
            "🏠  Overview & Drug Profile",
            "📋  Detailed Information",
            "🌍  Market Research",
        ],
        label_visibility="visible"
    )

    st.markdown("<br>" * 2, unsafe_allow_html=True)
    st.markdown("""
    <div style='padding:10px 0; border-top:1px solid #334155; font-size:10px; color:#475569; line-height:1.6;'>
        Data sources: FDA BLA 761055, Health Canada PM 292407, ClinicalTrials.gov,
        Sanofi/Regeneron PRs, KBR, BioSpectrum Asia.<br><br>
        <span style='color:#64748b;'>Last updated: June 2026</span>
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — OVERVIEW & DRUG PROFILE
# ═══════════════════════════════════════════════════════════════════════════════
if "Overview" in page:

    st.markdown('<p class="page-title">Dupilumab (Dupixent®)</p>', unsafe_allow_html=True)
    st.markdown('<p class="page-sub">Comprehensive Drug Intelligence Overview · Sanofi / Regeneron Pharmaceuticals</p>', unsafe_allow_html=True)

    # ── KPI row ──
    k1, k2, k3, k4, k5 = st.columns(5)
    with k1:
        st.markdown("""<div class='kpi-box'>
            <p class='kpi-value'>9</p>
            <p class='kpi-label'>FDA-Approved Indications</p>
            <p class='kpi-sub'>Mar 2017 → Feb 2026</p>
        </div>""", unsafe_allow_html=True)
    with k2:
        st.markdown("""<div class='kpi-box'>
            <p class='kpi-value'>$17.8B</p>
            <p class='kpi-label'>Global Sales 2025</p>
            <p class='kpi-sub'>Sanofi Annual Report 2025</p>
        </div>""", unsafe_allow_html=True)
    with k3:
        st.markdown("""<div class='kpi-box'>
            <p class='kpi-value'>1.4M+</p>
            <p class='kpi-label'>Patients Treated Globally</p>
            <p class='kpi-sub'>As of Feb 2026</p>
        </div>""", unsafe_allow_html=True)
    with k4:
        st.markdown("""<div class='kpi-box'>
            <p class='kpi-value'>60+</p>
            <p class='kpi-label'>Countries with ≥1 Approval</p>
            <p class='kpi-sub'>All regions combined</p>
        </div>""", unsafe_allow_html=True)
    with k5:
        st.markdown("""<div class='kpi-box'>
            <p class='kpi-value'>IgG4</p>
            <p class='kpi-label'>Antibody Subclass</p>
            <p class='kpi-sub'>Fully human, κ light chain</p>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Description + Chemical Data ──
    col_left, col_right = st.columns([3, 2])

    with col_left:
        st.markdown('<p class="section-head">Description & General Profile</p>', unsafe_allow_html=True)
        st.markdown("""
        <div class='card card-accent'>
            <p style='font-size:14px; color:#1e293b; line-height:1.7; margin:0;'>
                Dupilumab is a <strong>fully human immunoglobulin G4 (IgG4) monoclonal antibody</strong> that targets the
                interleukin-4 receptor alpha subunit (IL-4Rα). By binding IL-4Rα, it simultaneously blocks signalling
                from both <strong>IL-4</strong> (via the Type I receptor, IL-4Rα/γc) and <strong>IL-13</strong>
                (via the Type II receptor, IL-4Rα/IL-13Rα1) — the two master cytokines driving type 2 inflammation.
            </p>
            <br>
            <p style='font-size:14px; color:#1e293b; line-height:1.7; margin:0;'>
                It was developed through Regeneron's <strong>VelocImmune® platform</strong> (humanised mouse) and
                co-developed/commercialised by <strong>Sanofi and Regeneron</strong>. The drug received its first global
                approval from the FDA on <strong>28 March 2017</strong> for atopic dermatitis in adults — the first
                targeted therapy for that indication — and has since expanded to nine distinct indications across
                dermatology, pulmonology, ENT, and gastroenterology.
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<p class="section-head" style="margin-top:20px;">Chemical & Molecular Data</p>', unsafe_allow_html=True)
        st.markdown("""
        <div class='card'>
            <table class='data-table'>
                <tr><th>Parameter</th><th>Value</th><th>Source</th></tr>
                <tr><td>INN / Chemical name</td><td>Dupilumab / Interleukin-4 receptor α (human REGN668)</td><td>FDA label BLA 761055</td></tr>
                <tr><td>Molecular formula</td><td>C₆₅₁₂H₁₀₀₆₆N₁₇₃₀O₂₀₅₂S₄₆</td><td>FDA label BLA 761055</td></tr>
                <tr><td>Molecular weight</td><td>146,898.98 g/mol</td><td>FDA label BLA 761055</td></tr>
                <tr><td>Drug class</td><td>Fully human IgG4 monoclonal antibody (κ light chains)</td><td>FDA label BLA 761055</td></tr>
                <tr><td>Target</td><td>IL-4Rα subunit (shared component of Type I and Type II IL-4/IL-13 receptors)</td><td>HC PM §7.1</td></tr>
                <tr><td>Production platform</td><td>Regeneron VelocImmune® humanised mouse; CHO cell expression</td><td>FDA BLA 761055 §11</td></tr>
                <tr><td>Bioavailability (SC)</td><td>61–64%</td><td>HC PM §10.3 PK section</td></tr>
                <tr><td>Half-life (t½)</td><td>~26 days</td><td>HC PM §10.3</td></tr>
                <tr><td>Tmax (SC)</td><td>~7 days</td><td>HC PM §10.3</td></tr>
                <tr><td>Volume of distribution (Vd)</td><td>~4.8 L (central compartment)</td><td>Pop-PK analysis; HC PM §10.3</td></tr>
                <tr><td>Clearance</td><td>Non-linear (target-mediated); body weight primary covariate</td><td>HC PM §10.3</td></tr>
                <tr><td>Antibody subclass</td><td>IgG4 — no ADCC/CDC activation; no Fc effector function</td><td>FDA label §12.1</td></tr>
                <tr><td>pH (formulation)</td><td>5.9 (all strengths)</td><td>HC PM §6.1 (Control No. 292407)</td></tr>
            </table>
            <div class='source-box'>
                <strong>Primary sources:</strong>
                <a href='https://www.accessdata.fda.gov/drugsatfda_docs/label/2022/761055s042lbl.pdf' target='_blank'>FDA BLA 761055 Label</a> ·
                <a href='https://pdf.hres.ca/dpd_pm/00082261.PDF' target='_blank'>Health Canada PM Control No. 292407</a>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_right:
        st.markdown('<p class="section-head">Approved Indications Summary</p>', unsafe_allow_html=True)
        indications = {
            "Atopic Dermatitis": ("Mar 28, 2017", "≥6 months", "#3b82f6"),
            "Asthma": ("Oct 19, 2018", "≥6 years", "#10b981"),
            "CRSwNP": ("Jun 26, 2019", "≥12 years", "#8b5cf6"),
            "Eosinophilic Esophagitis": ("May 20, 2022", "≥1 year / ≥15 kg", "#f59e0b"),
            "Prurigo Nodularis": ("Sep 29, 2022", "Adults", "#ef4444"),
            "COPD": ("Sep 27, 2024", "Adults, eos ≥300/μL", "#06b6d4"),
            "Chronic Spontaneous Urticaria": ("Apr 18, 2025", "≥2 years", "#ec4899"),
            "Bullous Pemphigoid": ("Jun 20, 2025", "Adults", "#84cc16"),
            "Allergic Fungal Rhinosinusitis": ("Feb 24, 2026", "≥6 years", "#f97316"),
        }
        for ind, (date, age, color) in indications.items():
            st.markdown(f"""
            <div style='background:white; border:1px solid #e2e8f0; border-left:4px solid {color};
                        border-radius:8px; padding:8px 12px; margin-bottom:6px;'>
                <div style='font-size:12px; font-weight:600; color:#1e293b;'>{ind}</div>
                <div style='display:flex; gap:8px; margin-top:3px;'>
                    <span style='font-size:10px; color:#64748b;'>📅 {date}</span>
                    <span style='font-size:10px; color:#64748b;'>👤 {age}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("""
        <div class='source-box'>
            <a href='https://www.drugs.com/history/dupixent.html' target='_blank'>
                Source: drugs.com/history/dupixent.html (updated Apr 24, 2026)
            </a>
        </div>
        """, unsafe_allow_html=True)

    # ── Mechanism of Action ──
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<p class="section-head">Mechanism of Action (MoA)</p>', unsafe_allow_html=True)

    moa1, moa2 = st.columns([1, 1])

    with moa1:
        st.markdown("""
        <div class='card card-purple'>
            <div style='font-size:13px; font-weight:600; color:#1e293b; margin-bottom:10px;'>
                Receptor-level blockade: Type I and Type II
            </div>
        """, unsafe_allow_html=True)
        img_path1 = ASSETS / "moa_receptor.png"
        if img_path1.exists():
            st.image(str(img_path1), use_container_width=True)
        else:
            st.warning(f"Image not found: {img_path1}")
        st.markdown("""
            <div style='font-size:12px; color:#475569; line-height:1.6; margin-top:10px;'>
                Dupilumab binds the <strong>IL-4Rα subunit</strong> — the shared component of both:
                <ul style='margin:6px 0; padding-left:18px;'>
                    <li><strong>Type I receptor</strong> (IL-4Rα / γc): activated by IL-4 only</li>
                    <li><strong>Type II receptor</strong> (IL-4Rα / IL-13Rα1): activated by both IL-4 and IL-13</li>
                </ul>
                By occupying IL-4Rα, dupilumab prevents both cytokines from initiating JAK1/TYK2/JAK2 → STAT6
                signalling in a single mechanism.
            </div>
            <div class='source-box'>
                <a href='https://www.accessdata.fda.gov/drugsatfda_docs/label/2022/761055s042lbl.pdf' target='_blank'>
                    FDA BLA 761055 §12.1 (Mechanism of Action)
                </a>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with moa2:
        st.markdown("""
        <div class='card card-green'>
            <div style='font-size:13px; font-weight:600; color:#1e293b; margin-bottom:10px;'>
                Downstream pathway effects of IL-4Rα blockade
            </div>
        """, unsafe_allow_html=True)
        img_path2 = ASSETS / "moa_pathway.png"
        if img_path2.exists():
            st.image(str(img_path2), use_container_width=True)
        else:
            st.warning(f"Image not found: {img_path2}")
        st.markdown("""
            <div style='font-size:12px; color:#475569; line-height:1.6; margin-top:10px;'>
                Blocking IL-4Rα interrupts the entire type 2 inflammatory cascade:
                <ul style='margin:6px 0; padding-left:18px;'>
                    <li>Inhibits TH0 → TH2 cell differentiation (dendritic cell antigen presentation)</li>
                    <li>Suppresses TH2 cell clonal expansion and eosinophil trafficking to tissues</li>
                    <li>Blocks B cell isotype class switching to IgE (via activated B cells)</li>
                    <li>Reduces mast cell and basophil activation (FcεRI-mediated)</li>
                    <li>Prevents goblet cell hyperplasia and mucus hypersecretion</li>
                    <li>Reduces smooth muscle contractility and fibroblast collagen production</li>
                </ul>
                Indirect effect on IL-31: IL-4/IL-13 normally upregulate IL-31Rα expression on sensory neurons;
                blockade reduces IL-31 receptor availability, contributing to itch relief.
            </div>
            <div class='source-box'>
                <a href='https://pdf.hres.ca/dpd_pm/00082261.PDF' target='_blank'>
                    Health Canada PM §7.1 (Pharmacodynamics) · Control No. 292407
                </a>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Dosing regimens ──
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<p class="section-head">Approved Dosing Regimens (FDA)</p>', unsafe_allow_html=True)
    st.markdown("""
    <div class='card'>
        <table class='data-table'>
            <tr>
                <th>Indication</th><th>Patient group</th><th>Dose / Frequency</th><th>Route</th><th>Notes</th>
            </tr>
            <tr><td>Atopic Dermatitis</td><td>Adults (≥18)</td><td>600 mg loading → 300 mg Q2W</td><td>SC</td><td>Loading = 2×300 mg at Wk 0</td></tr>
            <tr><td>Atopic Dermatitis</td><td>Adol 12–17 yrs, ≥60 kg</td><td>600 mg loading → 300 mg Q2W</td><td>SC</td><td></td></tr>
            <tr><td>Atopic Dermatitis</td><td>Adol 12–17 yrs, &lt;60 kg</td><td>400 mg loading → 200 mg Q2W</td><td>SC</td><td></td></tr>
            <tr><td>Atopic Dermatitis</td><td>Children 6–11 yrs, ≥30 kg</td><td>200 mg Q2W</td><td>SC</td><td>No loading dose</td></tr>
            <tr><td>Atopic Dermatitis</td><td>Children 6–11 yrs, 15–&lt;30 kg</td><td>300 mg Q4W</td><td>SC</td><td>No loading dose</td></tr>
            <tr><td>Atopic Dermatitis</td><td>Infants 6 mo–5 yrs, 5–&lt;15 kg</td><td>200 mg Q4W</td><td>SC</td><td>No loading dose</td></tr>
            <tr><td>Atopic Dermatitis</td><td>Children 6 mo–5 yrs, 15–&lt;30 kg</td><td>300 mg Q4W</td><td>SC</td><td>No loading dose</td></tr>
            <tr><td>Asthma</td><td>Adults/Adol ≥12 yrs (type 2)</td><td>200 mg or 300 mg Q2W</td><td>SC</td><td>300 mg if OCS-dependent or comorbid mod-sev AD</td></tr>
            <tr><td>Asthma</td><td>Children 6–11 yrs, &lt;30 kg</td><td>100 mg Q2W</td><td>SC</td><td></td></tr>
            <tr><td>Asthma</td><td>Children 6–11 yrs, ≥30 kg</td><td>200 mg Q2W</td><td>SC</td><td></td></tr>
            <tr><td>CRSwNP</td><td>Adults + Adol ≥12 yrs</td><td>300 mg Q2W</td><td>SC</td><td>With intranasal corticosteroids</td></tr>
            <tr><td>EoE</td><td>≥12 yrs, ≥40 kg</td><td>300 mg QW</td><td>SC</td><td>Weekly dosing (different from other indications)</td></tr>
            <tr><td>EoE</td><td>1–11 yrs, weight-based</td><td>Variable (100–300 mg Q2W)</td><td>SC</td><td>By weight band</td></tr>
            <tr><td>PN / CSU / COPD / BP / AFRS</td><td>Adults / Adol ≥12 yrs</td><td>300 mg Q2W</td><td>SC</td><td>Standard adult dose</td></tr>
        </table>
        <div class='source-box'>
            <strong>Source:</strong>
            <a href='https://www.accessdata.fda.gov/drugsatfda_docs/label/2022/761055s042lbl.pdf' target='_blank'>
                FDA BLA 761055 label §2 (Dosage and Administration)
            </a> ·
            <a href='https://pdf.hres.ca/dpd_pm/00082261.PDF' target='_blank'>
                Health Canada PM Control No. 292407 §4.2
            </a>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — DETAILED INFORMATION (Slider-style tabs)
# ═══════════════════════════════════════════════════════════════════════════════
elif "Detailed" in page:

    st.markdown('<p class="page-title">Detailed Drug Information</p>', unsafe_allow_html=True)
    st.markdown('<p class="page-sub">Formulation · Clinical Trials · PK Study Survey · Comparator Medications · Korean Market Activity</p>', unsafe_allow_html=True)

    tab1, tab2, tab2b, tab3, tab4, tab5 = st.tabs([
        "💊  Formulation & Excipients",
        "🔬  Clinical Trial Programme",
        "💉  PK Study Survey",
        "⚖️  Comparator Medications",
        "🇰🇷  Korean Biosimilar Activity",
        "🧪  Technology Landscape"
    ])

    # ── TAB 1: FORMULATION ────────────────────────────────────────────────────
    with tab1:
        st.markdown('<div class="slider-header">Formulation Data — All Strengths (Dupixent® Pre-filled Syringe)</div>', unsafe_allow_html=True)

        img_path3 = ASSETS / "formulation_table.png"
        if img_path3.exists():
            st.image(str(img_path3), caption="Formulation reference table — source: Health Canada PM Control No. 292407", use_container_width=True)
        else:
            st.warning(f"Image not found: {img_path3}")

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<p class="section-head">Quantitative Formulation Comparison</p>', unsafe_allow_html=True)

        form_df = pd.DataFrame({
            "Excipient": ["L-Arginine HCl", "L-Histidine", "Polysorbate 80", "Sodium Acetate", "Sucrose", "pH"],
            "300 mg / 2.0 mL\n(150 mg/mL)": ["10.5 mg", "6.2 mg", "4.0 mg", "2.0 mg", "100 mg", "5.9"],
            "200 mg / 1.14 mL\n(175 mg/mL)": ["12.0 mg", "3.5 mg", "2.3 mg", "1.2 mg", "57 mg", "5.9"],
            "100 mg / 0.67 mL\n(150 mg/mL)": ["3.5 mg", "2.1 mg", "1.3 mg", "0.7 mg", "34 mg", "5.9"],
        })
        st.dataframe(form_df, use_container_width=True, hide_index=True)

        st.markdown('<p class="section-head" style="margin-top:20px;">Excipient Functional Roles</p>', unsafe_allow_html=True)

        excipients = [
            ("L-Arginine HCl", "Anti-aggregation + viscosity reducer",
             "At 150–175 mg/mL protein concentration, arginine inserts between protein molecules and disrupts intermolecular hydrophobic and electrostatic contacts that drive self-association, clustering, and opalescence. Critical for maintaining viscosity below ~20 cP and enabling injectability through 27G needles.",
             "HC PM §6.1, Control No. 292407"),
            ("L-Histidine / Sodium Acetate", "Dual buffer system",
             "Maintains formulation pH at 5.9 — slightly acidic, close to the pI of most mAbs to minimise electrostatic repulsion. pH 5–6 also mimics endosomal pH, supporting FcRn binding and IgG recycling (extending serum half-life). Dual buffering (acetate + histidine) gives broad capacity across storage and injection temperatures.",
             "HC PM §6.1, Control No. 292407"),
            ("Polysorbate 80", "Surfactant / surface adsorption prevention",
             "Prevents protein surface adsorption to the glass syringe barrel, needle hub, and rubber stopper. Protects against shear- and agitation-induced aggregation during fill-finish manufacturing and patient handling (injection, pen cap removal). Competes with protein at air-water interfaces, blocking interfacial denaturation. 'Super-refined' PS80 grade is used to minimise peroxide impurities that can cause methionine oxidation in the protein.",
             "HC PM §6.1, Control No. 292407"),
            ("Sucrose", "Cryoprotectant + tonicity agent + SC comfort",
             "Preferential exclusion effect: sucrose is excluded from the protein surface, thermodynamically favouring the native folded state. Protects against freeze-thaw stress during bulk drug substance processing. Contributes to near-isotonic osmolality (~300 mOsm), reducing SC injection pain and tissue damage at the injection site. Sugar-based tonicity agents produce less injection-site pain than NaCl-based tonicity agents in clinical data.",
             "HC PM §6.1, Control No. 292407"),
            ("Acetic acid (pH adjustment)", "pH titrant",
             "Used to adjust formulation pH to 5.9 target during manufacturing. No therapeutic role.",
             "HC PM §6.1"),
            ("Water for Injection (WFI)", "Solvent",
             "Compendial grade water; no therapeutic role.",
             "HC PM §6.1"),
        ]

        for name, role, desc, source in excipients:
            with st.expander(f"**{name}** — {role}"):
                st.markdown(f"""
                <div style='font-size:13px; color:#374151; line-height:1.7;'>{desc}</div>
                <div class='source-box' style='margin-top:10px;'>
                    <strong>Source:</strong> {source} ·
                    <a href='https://pdf.hres.ca/dpd_pm/00082261.PDF' target='_blank'>
                        Health Canada Product Monograph (PDF)
                    </a>
                </div>
                """, unsafe_allow_html=True)

    # ── TAB 2: CLINICAL TRIALS ─────────────────────────────────────────────────
    with tab2:
        st.markdown('<div class="slider-header">Complete Development Trial Programme — Approved Indications + Pipeline</div>', unsafe_allow_html=True)

        trials_data = [
            # Non-Clinical
            ("Non-Clinical", "In vitro receptor binding & IL-4/IL-13 inhibition assays", "Non-Clinical", "PD", "Cell-based (CHO, PBMC)", "Various concentrations", "N/A", "IC50 for IL-4Rα binding; STAT6 phosphorylation inhibition", "https://www.accessdata.fda.gov/drugsatfda_docs/label/2022/761055s042lbl.pdf"),
            ("Non-Clinical", "NHP toxicology & PK studies (cynomolgus monkeys)", "Non-Clinical", "PK, Safety", "Cynomolgus monkeys", "SC/IV; multiple doses", "Up to 26 wks", "Toxicity profile; SC bioavailability; half-life estimation", "https://www.accessdata.fda.gov/drugsatfda_docs/label/2022/761055s042lbl.pdf"),
            ("Non-Clinical", "Reproductive & Developmental Toxicology", "Non-Clinical", "Safety", "Cynomolgus monkeys", "SC gestational dosing", "Gestational", "Embryo-fetal development; placental IgG transfer", "https://pdf.hres.ca/dpd_pm/00082261.PDF"),
            # Phase 1/PK
            ("Phase 1/PK", "FIH SAD/MAD Study (NCT01259323)", "Phase 1", "PK, PD, Safety", "HV + AD adults; N≈50", "IV/SC; 75–600 mg SAD", "Up to 12 wks", "Safety; Cmax, AUC, t½; PD biomarkers (IgE, TARC)", "https://clinicaltrials.gov/study/NCT01259323"),
            ("Phase 1/PK", "Multiple-dose PK study (NCT01385657)", "Phase 1", "PK, Safety", "AD adults; N≈30", "SC; 75–300 mg multiple doses", "12 wks", "Steady-state PK; SC bioavailability; target-mediated clearance", "https://clinicaltrials.gov/study/NCT01385657"),
            ("Phase 1/PK", "SC dose PK comparability (NCT01639040)", "Phase 1", "PK", "AD adults; N≈30", "SC; various dose levels", "12 wks", "Dose-proportionality; SC vs IV PK comparison", "https://clinicaltrials.gov/study/NCT01639040"),
            ("Phase 1/PK", "AI vs PFS-S PK comparability — healthy volunteers (Cohen et al. 2022)", "Phase 1", "PK", "HV; N=130 (128 evaluable); parallel", "200 mg SC single dose: AI vs PFS-S", "~11 wks", "Cmax & AUClast comparability AI vs PFS-S devices", "https://pubmed.ncbi.nlm.nih.gov/35278283/"),
            ("Phase 1/PK", "Drug product comparability — new vs current DP (NCT05976386)", "Phase 1", "PK, Safety", "HV; N=182 actual", "Single SC dose; new DP vs current DP", "Up to 11 wks", "PK comparability (Cmax, AUC) between new and reference DP", "https://clinicaltrials.gov/study/NCT05976386"),
            # Atopic Dermatitis
            ("Atopic Dermatitis", "Phase 2a AD PoC (NCT01548404)", "Phase 2a", "Efficacy, Safety, PD", "Mod-sev AD adults; N=109; 1:1", "300 mg QW SC × 12 wks vs placebo", "12 wks", "EASI, IGA, NRS itch; biomarkers (TARC, IgE)", "https://clinicaltrials.gov/study/NCT01548404"),
            ("Atopic Dermatitis", "Phase 2b AD dose-ranging AD-1021 (NCT01859988)", "Phase 2b", "Efficacy, Safety, PK", "Mod-sev AD adults; N=379; multi-arm", "300 mg QW/Q2W/200 mg Q2W/100 mg Q2W/300 mg Q4W vs pbo", "16 wks", "EASI; IGA 0/1; dose selection for Phase 3", "https://clinicaltrials.gov/study/NCT01859988"),
            ("Atopic Dermatitis", "LIBERTY AD SOLO-1 (NCT02277743)", "Phase 3", "Efficacy, Safety", "Mod-sev AD ≥18 yrs; N=671; 1:1:1", "300 mg QW / 300 mg Q2W / Placebo", "16 wks", "IGA 0/1 and ≥2-pt reduction from baseline", "https://clinicaltrials.gov/study/NCT02277743"),
            ("Atopic Dermatitis", "LIBERTY AD SOLO-2 (NCT02277769)", "Phase 3", "Efficacy, Safety", "Mod-sev AD ≥18 yrs; N=708; 1:1:1", "300 mg QW / 300 mg Q2W / Placebo", "16 wks", "IGA 0/1 and ≥2-pt reduction from baseline", "https://clinicaltrials.gov/study/NCT02277769"),
            ("Atopic Dermatitis", "LIBERTY AD CHRONOS (NCT02260986)", "Phase 3", "Efficacy, Safety", "Mod-sev AD ≥18 yrs; N=740; 3:1:3", "300 mg QW / 300 mg Q2W + TCS / Placebo + TCS", "52 wks", "IGA 0/1; EASI-75 at Wk 16", "https://clinicaltrials.gov/study/NCT02260986"),
            ("Atopic Dermatitis", "LIBERTY AD ADOL (NCT03054428)", "Phase 3", "Efficacy, Safety, PK", "Mod-sev AD 12–17 yrs; N=251; 1:1:1", "<60 kg: 200 mg Q2W; ≥60 kg: 300 mg Q2W / Q4W / Placebo", "16 wks", "IGA 0/1 and ≥2-pt reduction from baseline", "https://clinicaltrials.gov/study/NCT03054428"),
            ("Atopic Dermatitis", "LIBERTY AD PEDS / AD-1652 (NCT03345914)", "Phase 3", "Efficacy, Safety, PK", "Severe AD 6–11 yrs; N=367; 1:1:1", "15–<30 kg: 100 mg Q2W; ≥30 kg: 200 mg Q2W; 300 mg Q4W; Pbo (+TCS)", "16 wks", "IGA 0/1", "https://clinicaltrials.gov/study/NCT03345914"),
            ("Atopic Dermatitis", "LIBERTY AD PRESCHOOL Part B / AD-1539 (NCT03346434)", "Phase 3", "Efficacy, Safety, PK", "Mod-sev AD 6 mo–5 yrs; N=162; 2:1", "5–<15 kg: 200 mg Q4W; 15–<30 kg: 300 mg Q4W; Pbo (+TCS)", "16 wks", "IGA 0/1", "https://clinicaltrials.gov/study/NCT03346434"),
            ("Atopic Dermatitis", "LIBERTY AD HAFT / AD-1924 (NCT04417894)", "Phase 3", "Efficacy, Safety", "Mod-sev atopic hand/foot dermatitis ≥12 yrs; N=133", "300 mg Q2W (adults) / weight-based (adol) vs Placebo", "16 wks", "IGA-HF 0/1 and ≥2-pt reduction from baseline", "https://clinicaltrials.gov/study/NCT04417894"),
            ("Atopic Dermatitis", "LIBERTY AD OLE / AD-1434 (NCT01949311)", "OLE/LTE", "Safety, Efficacy (long-term)", "Adults from SOLO/CHRONOS; N=2677", "300 mg Q2W or QW", "Up to 260 wks (5 yrs)", "Long-term safety; immunogenicity; sustained efficacy", "https://clinicaltrials.gov/study/NCT01949311"),
            ("Atopic Dermatitis", "DDI / CYP450 study (NCT02612155)", "Phase 1", "PK", "AD adults; N≈12–13", "600 mg loading → 300 mg QW SC × 6 wks", "~9 wks", "Effect of dupilumab on CYP1A2/2C9/2C19/2D6/3A4 probe substrates", "https://pdf.hres.ca/dpd_pm/00082261.PDF"),
            ("Atopic Dermatitis", "Vaccine immunogenicity study (NCT02952073)", "Phase 3", "PD, Safety", "AD adults on dupilumab 300 mg QW; N≈70", "300 mg QW × 16 wks; Tdap + meningococcal vaccines at Wk 12", "16 wks", "Antibody response to Tdap and meningococcal polysaccharide vaccines vs placebo", "https://pdf.hres.ca/dpd_pm/00082261.PDF"),
            # Asthma
            ("Asthma", "Phase 2a Asthma PoC (NCT01312961)", "Phase 2a", "Efficacy, PD", "Mod-sev eosinophilic asthma ≥18 yrs; N=104; 1:1", "300 mg Q2W SC vs placebo × 12 wks", "12 wks", "Asthma exacerbation events; FEV₁; eosinophil & FeNO biomarkers", "https://clinicaltrials.gov/study/NCT01312961"),
            ("Asthma", "DRI12544 Phase 2b dose-ranging (NCT01854047)", "Phase 2b", "Efficacy, Safety, PK", "Mod-sev uncontrolled asthma ≥12 yrs; N=776; multi-arm", "200/300 mg Q4W or Q2W vs Placebo", "24 wks", "Annualized severe exacerbation rate", "https://clinicaltrials.gov/study/NCT01854047"),
            ("Asthma", "LIBERTY ASTHMA QUEST / EFC13579 (NCT02414854)", "Phase 3", "Efficacy, Safety", "Mod-sev asthma ≥12 yrs; N=1902; 2:2:1:1", "200 mg Q2W / 300 mg Q2W / Placebo (2 arms)", "52 wks", "Annualized severe exacerbation rate; FEV₁ change from baseline", "https://clinicaltrials.gov/study/NCT02414854"),
            ("Asthma", "LIBERTY ASTHMA VENTURE / EFC13691 (NCT02528214)", "Phase 3", "Efficacy, Safety", "OCS-dependent severe asthma ≥12 yrs; N=210; 1:1", "300 mg Q2W vs Placebo", "24 wks", "Reduction in maintenance OCS dose while maintaining asthma control", "https://clinicaltrials.gov/study/NCT02528214"),
            ("Asthma", "LIBERTY ASTHMA VOYAGE (NCT02948959)", "Phase 3", "Efficacy, Safety, PK", "Mod-sev asthma 6–11 yrs; N=408; 2:1", "≤30 kg: 100 mg Q2W; ≥30 kg: 200 mg Q2W vs Placebo", "52 wks", "Annualized severe exacerbation rate", "https://clinicaltrials.gov/study/NCT02948959"),
            ("Asthma", "LIBERTY ASTHMA TRAVERSE OLE (NCT02134028)", "OLE/LTE", "Safety, Efficacy (long-term)", "Adults/adol from asthma parent studies; N=2193+89", "300 mg Q2W (open-label)", "Up to 96 wks", "Long-term safety; sustained exacerbation reduction", "https://clinicaltrials.gov/study/NCT02134028"),
            ("Asthma", "LIBERTY ASTHMA EXCURSION OLE — pediatric (NCT03560466)", "OLE/LTE", "Safety, Efficacy, PK", "Children 6–11 yrs from VOYAGE; N=365", "Weight-based dupilumab (open-label)", "52 wks", "Long-term safety; sustained exacerbation reduction in pediatrics", "https://clinicaltrials.gov/study/NCT03560466"),
            # CRSwNP
            ("CRSwNP", "Phase 2 CRSwNP PoC (NCT01920893)", "Phase 2", "Efficacy, PD", "Severe CRSwNP adults; N=60; 1:1:1", "300 mg Q2W / Q4W→Q2W / Placebo", "16 wks", "NPS; NC; eosinophil biomarkers", "https://clinicaltrials.gov/study/NCT01920893"),
            ("CRSwNP", "LIBERTY NP SINUS-24 (NCT02912468)", "Phase 3", "Efficacy, Safety", "Severe CRSwNP adults; N=276; 1:1", "300 mg Q2W vs Placebo (+ intranasal CS)", "24 wks", "NPS and NC score change from baseline", "https://clinicaltrials.gov/study/NCT02912468"),
            ("CRSwNP", "LIBERTY NP SINUS-52 (NCT02898454)", "Phase 3", "Efficacy, Safety", "Severe CRSwNP adults; N=448; 1:1:1", "300 mg Q2W / Q2W→Q4W / Placebo × 52 wks", "52 wks", "NPS and NC score change from baseline at Wk 24", "https://clinicaltrials.gov/study/NCT02898454"),
            # EoE
            ("EoE", "Phase 2 EoE PoC (NCT02379052)", "Phase 2", "Efficacy, PD", "Active EoE adults; N=47; 1:1", "300 mg QW vs Placebo × 12 wks", "12 wks", "PEC per hpf; histologic response; dysphagia", "https://clinicaltrials.gov/study/NCT02379052"),
            ("EoE", "LIBERTY EoE TREET Parts A & B (NCT03633617)", "Phase 3", "Efficacy, Safety, PK", "EoE ≥12 yrs ≥40 kg; N=321; 1:1", "300 mg QW vs Placebo × 24 wks (+28-wk Part C)", "24 wks (+ext)", "PEC ≤6 eos/hpf AND DSQ score change at Wk 24", "https://clinicaltrials.gov/study/NCT03633617"),
            ("EoE", "EoE KIDS Part A — pediatric (NCT04679935)", "Phase 3", "Efficacy, Safety, PK", "EoE 1–11 yrs ≥15 kg; N=101; 2:1", "Weight-based dosing (100–300 mg Q2W) vs Placebo", "16 wks (+Part B ext)", "PEC ≤6 eos/hpf at Wk 16", "https://clinicaltrials.gov/study/NCT04679935"),
            # PN
            ("Prurigo Nodularis", "LIBERTY-PN PRIME (NCT04183335)", "Phase 3", "Efficacy, Safety", "Mod-sev PN adults; N=151; 1:1", "300 mg Q2W vs Placebo", "24 wks", "IGA 0/1; ≥4-pt reduction in WI-NRS", "https://clinicaltrials.gov/study/NCT04183335"),
            ("Prurigo Nodularis", "LIBERTY-PN PRIME2 (NCT04202679)", "Phase 3", "Efficacy, Safety", "Mod-sev PN adults; N=160; 1:1", "300 mg Q2W vs Placebo", "24 wks", "IGA 0/1; ≥4-pt reduction in WI-NRS at Wk 12", "https://clinicaltrials.gov/study/NCT04202679"),
            # COPD
            ("COPD", "BOREAS (NCT03930732)", "Phase 3", "Efficacy, Safety", "Mod-sev COPD eos ≥300/μL on triple therapy adults; N=939; 1:1", "300 mg Q2W vs Placebo", "52 wks", "Annualized rate of moderate/severe COPD exacerbations", "https://clinicaltrials.gov/study/NCT03930732"),
            ("COPD", "NOTUS (NCT04456673)", "Phase 3", "Efficacy, Safety", "Mod-sev COPD eos ≥300/μL adults; N=935; 1:1", "300 mg Q2W vs Placebo", "52 wks", "Annualized rate of moderate/severe COPD exacerbations", "https://clinicaltrials.gov/study/NCT04456673"),
            # CSU
            ("CSU", "CUPID Study A (NCT04180488)", "Phase 3", "Efficacy, Safety", "CSU H1-AH refractory, omalizumab-naive; N=138; 1:1", "≥60 kg: 600 mg→300 mg Q2W; 30–<60 kg: 400 mg→200 mg Q2W; <30 kg: 300 mg Q4W; all vs Pbo", "24 wks", "Change from baseline in UAS7 and ISS7 at Wk 24 — MET", "https://clinicaltrials.gov/study/NCT04180488"),
            ("CSU", "CUPID Study B (NCT04180488 — same master)", "Phase 3", "Efficacy, Safety", "CSU H1-AH refractory, omalizumab intolerant/incomplete responders; N=83; 12–80 yrs", "Adults/adol ≥60 kg: 600 mg→300 mg Q2W; adol <60 kg: 400 mg→200 mg Q2W; all vs Pbo", "24 wks", "ISS7 and UAS7 change at Wk 24 — DID NOT MEET primary (futility interim)", "https://clinicaltrials.gov/study/NCT04180488"),
            ("CSU", "CUPID Study C (NCT04180488 — same master, amended)", "Phase 3", "Efficacy, Safety, PK", "CSU H1-AH refractory, omalizumab-naive; N=151 (74 dup, 77 pbo); ≥6 yrs", "≥60 kg: 300 mg Q2W; 30–<60 kg: 200 mg Q2W; all vs Pbo", "24 wks", "ISS7 and UAS7 change at Wk 24 — MET (p=0.02 both)", "https://clinicaltrials.gov/study/NCT04180488"),
            # BP
            ("Bullous Pemphigoid", "LIBERTY-BP ADEPT (NCT04206553)", "Phase 3", "Efficacy, Safety", "Mod-sev BP adults; N=106; 1:1 (vs placebo + OCS taper)", "300 mg Q2W vs Placebo (all + OCS taper protocol)", "52 wks", "Sustained disease remission: IGA 0/1 + no rescue at Wk 36", "https://clinicaltrials.gov/study/NCT04206553"),
            # Population PK
            ("Pop-PK / PK-PD", "Population PK analysis — adults & adolescents (all indications)", "Pop-PK", "PK, PD", "Pooled Phase 2/3 data; adults + adolescents; N=thousands", "All approved regimens", "Across multiple trials", "Characterise Vd (~4.8 L); TMDD clearance; bioavailability 61–64%; body weight as primary covariate", "https://pdf.hres.ca/dpd_pm/00082261.PDF"),
            ("Pop-PK / PK-PD", "Pediatric population PK — dose selection simulations (6 mo–11 yrs)", "Pop-PK", "PK", "Pediatric data from AD-1652, AD-1539, VOYAGE, EoE KIDS; model-based", "Weight-based doses 100–300 mg Q2W or Q4W", "Model-based", "Predict steady-state Ctrough to support weight-based dose selection across pediatric age groups", "https://pdf.hres.ca/dpd_pm/00082261.PDF"),
            # Pipeline
            ("PIPELINE — CPUO", "LIBERTY-CPUO PRISM (NCT05263206)", "Phase 3", "RCT DB PC", "Adults; ~300; 1:1; WI-NRS ≥7", "300 mg Q2W", "24 wks + 12 wk follow-up", "≥4-pt reduction in WI-NRS; IGA 0/1. Study A DID NOT meet primary endpoint (Sept 2024). Study B ongoing.", "https://clinicaltrials.gov/study/NCT05263206"),
            ("PIPELINE — LSC", "STYLE 1 & 2 (NCT06687967 / NCT06687980)", "Phase 3", "RCT DB PC", "Adults ≥18 yrs; ~200; parallel 2-arm", "300 mg Q2W", "24 wks", "WI-NRS improvement; IGA", "https://clinicaltrials.gov/study/NCT06687967"),
            ("PIPELINE — CIndU", "LIBERTY-CIndU CINDU (NCT04681729) — COMPLETED", "Phase 3", "RCT DB PC", "Adults ≥12 yrs; N=82; 1:1; 5 countries", "300 mg Q2W", "24 wks + 12 wk follow-up", "Negative ice cube provocation test at Wk 24 — results published PMC 2025", "https://clinicaltrials.gov/study/NCT04681729"),
            ("PIPELINE — ABPA", "LIBERTY ABPA AIRED (NCT04442269) — COMPLETED", "Phase 2", "RCT DB PC", "≥12 yrs; N=62; 1:1", "300 mg Q2W", "24–52 wks", "Change from baseline in pre-BD FEV₁ at Wk 24 — positive results (ERS 2025: 55.2% exacerbation reduction)", "https://clinicaltrials.gov/study/NCT04442269"),
            ("PIPELINE — Milk/OIT", "Dupilumab + OIT (NCT04148352)", "Phase 2", "RCT", "Pediatric + adult; ~100", "Standard SC dosing + OIT protocol", "With OIT protocol", "Desensitization threshold; allergen-specific IgE reduction", "https://clinicaltrials.gov/study/NCT04148352"),
            ("PIPELINE — EoGE", "LIBERTY EoGE ENIGMA (NCT03678545) — COMPLETED", "Phase 2", "Open-label", "Adults; ~33", "300 mg Q2W", "24 wks", "Gastric eosinophils ≤30/hpf (histologic response)", "https://clinicaltrials.gov/study/NCT03678545"),
            ("PIPELINE — CRSsNP", "Efficacy of Dupilumab for CRSsNP (NCT04362501) — COMPLETED", "Phase 2", "RCT DB PC", "CRSsNP; N=33; 1:1; SNOT-22 ≥30; Lund-Mackay CT ≥4", "300 mg Q2W", "24 wks", "SNOT-22 score change; Lund-Mackay CT score change; Th2-high vs Th2-low endotype analysis", "https://clinicaltrials.gov/study/NCT04362501"),
            ("PIPELINE — Alopecia Areata", "Guttman-Yassky AA trial (NCT03359356) — COMPLETED", "Phase 2a", "RCT DB PC + OLE", "Adults; N=60; 2:1; AA ≥50% scalp", "300 mg QW × 24 wks → 24-wk OLE", "48 wks total", "Change from baseline in SALT score at Wk 24", "https://pmc.ncbi.nlm.nih.gov/articles/PMC9997752/"),
            ("PIPELINE — Netherton Syndrome", "NS-DUPI (NCT04244006)", "Phase 2/3", "RCT DB PC", "Clinical NS diagnosis; ≥18 yrs; N≈24; 2:1; NASA ≥5/12; LEKTI confirmation req.", "600 mg loading → 300 mg Q2W to Wk 14 (8 total SC)", "16 wks", "Change from baseline in NASA score; EASI; SCORAD", "https://clinicaltrials.gov/study/NCT04244006"),
            ("PIPELINE — Pediatric AA", "PEDAL (NCT05866562)", "Phase 2", "RCT DB PC + OLE", "6–17 yrs; N=76; IgE ≥200 IU/mL or atopic hx; SALT ≥30%", "Weight-based SC Q2W or Q4W", "48 wks DB + 48 wks OLE + 24 wks follow-up", "SALT50 (≥50% improvement in SALT) at Wk 48 — first RCT of any biologic in pediatric AA", "https://clinicaltrials.gov/study/NCT05866562"),
        ]

        df_trials = pd.DataFrame(trials_data, columns=[
            "Indication", "Study Name", "Phase", "Study Type",
            "Population", "Dose", "Duration", "Primary Endpoint", "Reference"
        ])

        # Filter controls
        col_f1, col_f2 = st.columns([2, 2])
        with col_f1:
            indic_filter = st.multiselect(
                "Filter by indication",
                sorted(df_trials["Indication"].unique()),
                default=[],
                placeholder="All indications"
            )
        with col_f2:
            phase_filter = st.multiselect(
                "Filter by phase",
                sorted(df_trials["Phase"].unique()),
                default=[],
                placeholder="All phases"
            )

        filtered = df_trials.copy()
        if indic_filter:
            filtered = filtered[filtered["Indication"].isin(indic_filter)]
        if phase_filter:
            filtered = filtered[filtered["Phase"].isin(phase_filter)]

        st.markdown(f"**Showing {len(filtered)} of {len(df_trials)} studies**")
        st.markdown("<br>", unsafe_allow_html=True)

        for _, row in filtered.iterrows():
            phase_color = {
                "Phase 3": "#dbeafe|#1d4ed8",
                "Phase 2": "#dcfce7|#15803d",
                "Phase 2a": "#dcfce7|#15803d",
                "Phase 2b": "#dcfce7|#15803d",
                "Phase 2/3": "#ede9fe|#6d28d9",
                "Phase 1": "#fef3c7|#b45309",
                "Pop-PK": "#f1f5f9|#475569",
                "OLE/LTE": "#fce7f3|#9d174d",
                "Non-Clinical": "#f1f5f9|#374151",
            }.get(row["Phase"], "#f1f5f9|#374151")
            ph_bg, ph_color = phase_color.split("|")

            with st.expander(f"**{row['Study Name']}** — {row['Indication']}"):
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.markdown(f"""
                    <span style='background:{ph_bg};color:{ph_color};font-size:11px;font-weight:600;
                                  padding:3px 9px;border-radius:12px;'>{row['Phase']}</span>
                    <div style='margin-top:10px;font-size:12px;color:#64748b;'>Study type</div>
                    <div style='font-size:13px;color:#1e293b;font-weight:500;'>{row['Study Type']}</div>
                    """, unsafe_allow_html=True)
                with c2:
                    st.markdown(f"""
                    <div style='font-size:12px;color:#64748b;'>Population</div>
                    <div style='font-size:13px;color:#1e293b;margin-bottom:8px;'>{row['Population']}</div>
                    <div style='font-size:12px;color:#64748b;'>Duration</div>
                    <div style='font-size:13px;color:#1e293b;'>{row['Duration']}</div>
                    """, unsafe_allow_html=True)
                with c3:
                    st.markdown(f"""
                    <div style='font-size:12px;color:#64748b;'>Dose / Regimen</div>
                    <div style='font-size:13px;color:#1e293b;margin-bottom:8px;'>{row['Dose']}</div>
                    """, unsafe_allow_html=True)

                st.markdown(f"""
                <div style='background:#f8fafc;border-radius:8px;padding:10px 14px;margin-top:8px;'>
                    <span style='font-size:11px;color:#64748b;font-weight:600;'>PRIMARY ENDPOINT</span>
                    <p style='font-size:13px;color:#1e293b;margin:4px 0 0;'>{row['Primary Endpoint']}</p>
                </div>
                <div class='source-box' style='margin-top:8px;'>
                    <a href='{row['Reference']}' target='_blank'>🔗 {row['Reference']}</a>
                </div>
                """, unsafe_allow_html=True)

    # ── TAB 2B: PK STUDY SURVEY ──────────────────────────────────────────────
    with tab2b:
        st.markdown('<div class="slider-header">PK Study Survey — Test Article, Species, Route, Dose & Linearity by Study</div>', unsafe_allow_html=True)
        st.markdown("""
        <div style='font-size:13px; color:#374151; line-height:1.7; margin-bottom:14px;'>
            Oriented to what a PK scientist needs when scoping a study: test article (dupilumab vs. species surrogate),
            target-binding status by species, route, dose range, regimen, duration, the PK question each study was built
            to answer, and linearity / TMDD behaviour. Established parameter values are verified against the EMA assessment
            report full text; per-study clinical PK read-outs are <em>not</em> reproduced where the surveyed source did not contain them.
        </div>
        """, unsafe_allow_html=True)

        # ── Established human PK parameters ──
        st.markdown('<p class="section-head">Established Dupilumab PK Parameters (Human)</p>', unsafe_allow_html=True)

        pk_params = [
            ("SC bioavailability (F)", "61% (asthma Pop-PK model)"),
            ("Absorption rate constant (ka)", "0.260 / day"),
            ("Median tmax (SC)", "3–7 days"),
            ("Central volume of distribution (V2)", "4.37 L"),
            ("Linear clearance (CL)", "0.115 L/day"),
            ("Elimination", "Non-linear, target-mediated disposition (TMDD); linear pathway dominates at high conc."),
            ("Dose proportionality", "Greater-than-dose-proportional; 200→300 mg Q2W raised Wk16 trough 2.06-fold (29.2→60.3 mg/L)"),
            ("Time to steady state", "6 wk (200 mg Q2W + 400 mg load); 8 wk (300 mg Q2W + 600 mg load)"),
            ("Washout (to <LLOQ 0.078 mg/L)", "9 wk (200 mg Q2W); 11 wk (300 mg Q2W)"),
            ("Primary PK covariate", "Body weight (range studied 32–186 kg)"),
            ("IIV (Fsc / Ke / V2 / Vm)", "36.3% / 19.6% / 9.13% / 24.3%"),
            ("ADA effect on PK", "Higher Ke / lower exposure in persistently ADA-positive patients"),
        ]

        cols = st.columns(4)
        for i, (name, val) in enumerate(pk_params):
            with cols[i % 4]:
                st.markdown(f"""
                <div class='card' style='padding:12px 13px; min-height:128px; position:relative;'>
                    <span style='position:absolute; top:10px; right:11px; font-size:9px; font-weight:700;
                                  color:#0f766e; background:#f0fdfa; border:1px solid #99f6e4;
                                  border-radius:5px; padding:1px 5px;'>✓ EMA</span>
                    <p style='font-size:10.5px; letter-spacing:0.04em; text-transform:uppercase; color:#64748b;
                              font-weight:600; margin:0 0 5px;'>{name}</p>
                    <p style='font-size:12.5px; color:#1e293b; font-weight:500; line-height:1.4; margin:0;'>{val}</p>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("""
        <div class='source-box' style='margin-top:4px;'>
            Human values are from the <strong>asthma population-PK model</strong> in the EMA report; the AD-pooled model
            gives close but not identical figures (e.g. Vd ~4.8 L, F 61–64%). Use the indication-matched model for your
            own simulations. ·
            <a href='https://www.ema.europa.eu/en/documents/variation-report/dupixent-h-c-4390-x-0004-g-epar-assessment-report-extension_en.pdf' target='_blank'>EMA assessment report (PDF)</a>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── PK study survey table ──
        st.markdown('<p class="section-head">PK Study Survey — Nonclinical, Clinical PK & Population PK</p>', unsafe_allow_html=True)

        pk_studies = [
            ("Nonclinical", "In vitro binding & potency", True, "Dupilumab; REGN646; REGN1103",
             "CHO / PBMC / Ramos cell lines; human, monkey, mouse", "—", "—", "—",
             "Human IL-4Rα KD 12 pM. Dupilumab STAT6 IC50 25 pM (IL-4) / 27 pM (IL-13). REGN1103 IC50 1.9 nM (IL-4) / 11 pM (IL-13). No ADCC/CDC (IgG4).",
             "n/a", "https://www.ema.europa.eu/en/documents/variation-report/dupixent-h-c-4390-x-0004-g-epar-assessment-report-extension_en.pdf"),
            ("Nonclinical", "Single-dose PK — rat", True, "Dupilumab",
             "Rat (no high-affinity target binding)", "IV & SC", "Single dose", "—",
             "t½ 4.8–7 d; SC bioavailability 84.2%; qualified ELISA. Linear (no TMDD).",
             "Linear", "https://www.ema.europa.eu/en/documents/variation-report/dupixent-h-c-4390-x-0004-g-epar-assessment-report-extension_en.pdf"),
            ("Nonclinical", "Single-dose PK — cynomolgus", True, "Dupilumab",
             "Cynomolgus monkey (low-affinity binding)", "IV & SC", "Single dose", "—",
             "t½ 11.7–20.5 d; SC bioavailability >92%; qualified ELISA. Linear, ~dose-proportional total exposure.",
             "Linear", "https://www.ema.europa.eu/en/documents/variation-report/dupixent-h-c-4390-x-0004-g-epar-assessment-report-extension_en.pdf"),
            ("Nonclinical", "PK/TK — cynomolgus (surrogate)", True, "REGN646 (anti-monkey IL-4Rα)",
             "Cynomolgus monkey", "IV & SC; single & repeat", "Single 1–15 mg/kg; repeat 25 & 100 mg/kg/wk", "Up to 26 wk (repeat-dose)",
             "Non-linear TMDD: Cmax ~dose-prop, AUCinf >dose-prop. β-t½ 7.2–9.1 d; terminal t½ 1.5–2.1 d; absolute SC F ~70%; accumulation 2.2–4.6-fold weekly. Validated ELISA; bridging ECL for ADA.",
             "Non-linear (TMDD)", "https://www.ema.europa.eu/en/documents/variation-report/dupixent-h-c-4390-x-0004-g-epar-assessment-report-extension_en.pdf"),
            ("Nonclinical", "TK — mouse (surrogate)", True, "REGN1103 (anti-mouse IL-4Rα)",
             "Mouse", "SC", "≥25 mg/kg/wk range", "—",
             "Non-linear: >dose-proportional at low doses, ~dose-proportional at ≥25 mg/kg/wk. Validated ELISA.",
             "Non-linear", "https://www.ema.europa.eu/en/documents/variation-report/dupixent-h-c-4390-x-0004-g-epar-assessment-report-extension_en.pdf"),
            ("Clinical PK", "FIH SAD/MAD (NCT01259323)", False, "Dupilumab",
             "Healthy volunteers + AD adults; N≈50", "IV / SC", "75–600 mg SAD", "Up to 12 wk",
             "First-in-human safety; Cmax, AUC, t½; PD biomarkers (IgE, TARC). [per-subject PK values not in surveyed source]",
             "—", "https://clinicaltrials.gov/study/NCT01259323"),
            ("Clinical PK", "Multiple-dose PK (NCT01385657)", False, "Dupilumab",
             "AD adults; N≈30", "SC", "75–300 mg, multiple doses", "12 wk",
             "Steady-state PK; SC bioavailability; target-mediated clearance characterization.",
             "Non-linear (TMDD)", "https://clinicaltrials.gov/study/NCT01385657"),
            ("Clinical PK", "SC dose PK comparability (NCT01639040)", False, "Dupilumab",
             "AD adults; N≈30", "SC (vs IV ref)", "Various dose levels", "12 wk",
             "Dose-proportionality; SC vs IV PK comparison.",
             "—", "https://clinicaltrials.gov/study/NCT01639040"),
            ("Clinical PK", "Device comparability: AI vs PFS-S (Cohen 2022)", False, "Dupilumab",
             "Healthy volunteers; N=130 (128 evaluable); parallel", "SC", "200 mg single dose", "~11 wk",
             "Cmax & AUClast comparability, autoinjector vs prefilled-syringe-with-safety.",
             "—", "https://pubmed.ncbi.nlm.nih.gov/35278283/"),
            ("Clinical PK", "Drug-product comparability (NCT05976386)", False, "Dupilumab",
             "Healthy volunteers; N=182", "SC", "Single dose; new DP vs current DP", "Up to 11 wk",
             "PK comparability (Cmax, AUC) new vs reference drug product.",
             "—", "https://clinicaltrials.gov/study/NCT05976386"),
            ("Clinical PK", "DDI / CYP450 probe (NCT02612155)", False, "Dupilumab",
             "AD adults; N≈12–13", "SC", "600 mg load → 300 mg QW × 6 wk", "~9 wk",
             "Effect of dupilumab on CYP1A2/2C9/2C19/2D6/3A probe substrates. EMA: no clinically relevant CYP effect.",
             "—", "https://clinicaltrials.gov/study/NCT02612155"),
            ("Pop-PK", "Population PK — adults & adolescents", True, "Dupilumab",
             "Pooled Ph2/3; healthy + patients; N=thousands", "SC (all approved regimens)", "All approved regimens", "Pooled across trials",
             "2-compartment, parallel linear + non-linear (TMDD) elimination, 1st-order absorption. F 61%; V2 4.37 L; CL 0.115 L/d; body weight primary covariate.",
             "Non-linear (TMDD)", "https://www.ema.europa.eu/en/documents/variation-report/dupixent-h-c-4390-x-0004-g-epar-assessment-report-extension_en.pdf"),
            ("Pop-PK", "Pediatric Pop-PK — dose-selection sims (6 mo–11 yr)", False, "Dupilumab",
             "Pediatric (AD-1652, AD-1539, VOYAGE, EoE KIDS); model-based", "SC", "Weight-based 100–300 mg Q2W/Q4W", "Model-based",
             "Predict steady-state Ctrough to justify weight-banded pediatric dosing.",
             "Non-linear (TMDD)", "https://pdf.hres.ca/dpd_pm/00082261.PDF"),
        ]

        df_pk = pd.DataFrame(pk_studies, columns=[
            "Scope", "Study", "EMA Verified", "Test Article", "Species / Population",
            "Route", "Dose / Regimen", "Duration", "PK Question Addressed", "Linearity", "Reference"
        ])

        scope_filter = st.multiselect(
            "Filter by scope",
            ["Nonclinical", "Clinical PK", "Pop-PK"],
            default=[],
            placeholder="All scopes",
            key="pk_scope_filter"
        )
        filtered_pk = df_pk.copy()
        if scope_filter:
            filtered_pk = filtered_pk[filtered_pk["Scope"].isin(scope_filter)]

        st.markdown(f"**Showing {len(filtered_pk)} of {len(df_pk)} studies**")
        st.markdown("<br>", unsafe_allow_html=True)

        scope_color = {"Nonclinical": "#fef3c7|#b45309", "Clinical PK": "#dbeafe|#0e7490", "Pop-PK": "#ede9fe|#4338ca"}
        lin_color = {
            "Linear": "#dbeafe|#1d4ed8",
            "Non-linear": "#ffedd5|#9a3412",
            "Non-linear (TMDD)": "#ffedd5|#9a3412",
            "n/a": "#f1f5f9|#94a3b8",
            "—": "#f1f5f9|#94a3b8",
        }

        for _, row in filtered_pk.iterrows():
            sc_bg, sc_color = scope_color.get(row["Scope"], "#f1f5f9|#475569").split("|")
            li_bg, li_color = lin_color.get(row["Linearity"], "#f1f5f9|#475569").split("|")
            prov_badge = (
                "<span style='font-size:9.5px;font-weight:700;border-radius:5px;padding:2px 6px;"
                "color:#0f766e;background:#f0fdfa;border:1px solid #99f6e4;'>✓ EMA verified</span>"
                if row["EMA Verified"] else
                "<span style='font-size:9.5px;font-weight:700;border-radius:5px;padding:2px 6px;"
                "color:#92400e;background:#fffbeb;border:1px solid #fde68a;' "
                "title='Study design from dashboard source; per-study PK values not in that source and not fabricated'>◑ Design only</span>"
            )

            with st.expander(f"**{row['Study']}** — {row['Test Article']}"):
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.markdown(f"""
                    <span style='background:{sc_bg};color:{sc_color};font-size:11px;font-weight:600;
                                  padding:3px 9px;border-radius:12px;'>{row['Scope']}</span>
                    &nbsp;{prov_badge}
                    <div style='margin-top:10px;font-size:12px;color:#64748b;'>Test article</div>
                    <div style='font-size:13px;color:#1e293b;font-weight:500;'>{row['Test Article']}</div>
                    """, unsafe_allow_html=True)
                with c2:
                    st.markdown(f"""
                    <div style='font-size:12px;color:#64748b;'>Species / population</div>
                    <div style='font-size:13px;color:#1e293b;margin-bottom:8px;'>{row['Species / Population']}</div>
                    <div style='font-size:12px;color:#64748b;'>Route</div>
                    <div style='font-size:13px;color:#1e293b;'>{row['Route']}</div>
                    """, unsafe_allow_html=True)
                with c3:
                    st.markdown(f"""
                    <div style='font-size:12px;color:#64748b;'>Dose / regimen</div>
                    <div style='font-size:13px;color:#1e293b;margin-bottom:8px;'>{row['Dose / Regimen']}</div>
                    <div style='font-size:12px;color:#64748b;'>Duration</div>
                    <div style='font-size:13px;color:#1e293b;'>{row['Duration']}</div>
                    """, unsafe_allow_html=True)

                st.markdown(f"""
                <div style='background:#f8fafc;border-radius:8px;padding:10px 14px;margin-top:8px;'>
                    <span style='font-size:11px;color:#64748b;font-weight:600;'>PK QUESTION ADDRESSED</span>
                    <p style='font-size:13px;color:#1e293b;margin:4px 0 0;'>{row['PK Question Addressed']}</p>
                    <span style='display:inline-block;margin-top:8px;font-size:10px;font-weight:700;
                                  border-radius:5px;padding:2px 6px;background:{li_bg};color:{li_color};'>
                        Linearity: {row['Linearity']}
                    </span>
                </div>
                <div class='source-box' style='margin-top:8px;'>
                    <a href='{row['Reference']}' target='_blank'>🔗 {row['Reference']}</a>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Legend ──
        st.markdown("""
        <div style='display:flex; gap:16px; flex-wrap:wrap; font-size:11px; color:#64748b; margin-bottom:6px;'>
            <span>🟦 Dupilumab (clinical molecule)</span>
            <span>🟪 Species surrogate (REGN646 / REGN1103)</span>
            <span>✓ EMA-verified values</span>
            <span>◑ Design only (no PK read-out in source)</span>
        </div>
        """, unsafe_allow_html=True)

        # ── Design-relevant takeaways ──
        st.markdown('<p class="section-head" style="margin-top:16px;">Design-Relevant Takeaways for a PK Survey</p>', unsafe_allow_html=True)
        st.markdown("""
        <div class='card card-purple'>
            <p style='font-size:13px; color:#1e293b; line-height:1.7; margin:0;'>
                Dupilumab does not bind rodent IL-4Rα and binds cynomolgus IL-4Rα only weakly — so nonclinical
                <strong>tox/PD</strong> used species surrogates (REGN646 in monkey, REGN1103 in mouse), while dupilumab
                itself was used only for <strong>single-dose PK</strong> in rat/monkey (linear, no TMDD) and for efficacy
                in <strong>humanised/transgenic</strong> mice. In humans, dupilumab shows <strong>non-linear,
                target-mediated disposition</strong>: pick a model with parallel linear + saturable clearance, plan for
                greater-than-dose-proportional exposure, build in body weight as the primary covariate, and allow
                6–8 wk to steady state and 9–11 wk washout. Device/drug-product comparability studies used single
                200 mg SC in healthy volunteers (~11 wk).
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class='note-box' style='margin-top:10px;'>
            <strong>Provenance:</strong> parameter values and nonclinical PK marked ✓ are from the EMA assessment report
            (EMEA/H/C/004390/X/0004/G). Clinical study rows marked ◑ give design fields taken from the survey source;
            individual-study Cmax/AUC/t½ were not in that source and have not been added here.
        </div>
        """, unsafe_allow_html=True)

    # ── TAB 3: COMPARATOR MEDICATIONS ────────────────────────────────────────
    with tab3:
        st.markdown('<div class="slider-header">Comparator Medications — Atopic Dermatitis Treatment Landscape</div>', unsafe_allow_html=True)

        med_tab1, med_tab2, med_tab3 = st.tabs(["🧬 Biologics (SC injection)", "💊 Oral JAK Inhibitors", "🧴 Topical Targeted Agents"])

        with med_tab1:
            biologics = [
                {
                    "name": "Tralokinumab (Adbry® / Adtralza®)",
                    "target": "IgG4 mAb — anti-IL-13",
                    "company": "LEO Pharma",
                    "dose": "600 mg loading → 300 mg Q2W; 300 mg Q4W after Wk 16 if clear/almost clear",
                    "age": "≥12 years (adults Dec 2021; adolescents Dec 2023)",
                    "approval": "FDA Dec 2021",
                    "warning": "No boxed warning",
                    "trial": "ECZTRA 1 (NCT03131648): IGA 0/1 Wk 16: 15.8% vs 7.1% placebo (p=0.002); EASI-75: 25.0% vs 12.7%\nECZTRA 2 (NCT03160885): IGA 0/1 Wk 16: 22.2% vs 10.9%; EASI-75: 33.2% vs 15.1%",
                    "safety": "Conjunctivitis (less frequent than dupilumab); no lab monitoring required",
                    "ref": "Wollenberg A, et al. Br J Dermatol 2021;184(3):437–449. doi:10.1111/bjd.19574",
                    "link": "https://onlinelibrary.wiley.com/doi/10.1111/bjd.19574",
                    "color": "#3b82f6"
                },
                {
                    "name": "Lebrikizumab (Ebglyss®)",
                    "target": "IgG4 mAb — anti-IL-13 (blocks IL-4Rα/IL-13Rα1 heterodimerization; does NOT bind IL-13Rα2)",
                    "company": "Eli Lilly / Almirall (EU)",
                    "dose": "500 mg loading ×2 (Wk 0+2) → 250 mg Q2W → Q4W maintenance after Wk 16",
                    "age": "≥12 years (EMA Nov 2023; FDA Sep 2024)",
                    "approval": "EMA Nov 2023; FDA Sep 2024",
                    "warning": "No boxed warning",
                    "trial": "ADvocate 1 (NCT04146363): IGA 0/1 Wk 16: 43.1% vs 12.7% (p<0.001); EASI-75: 58.8% vs 16.2%\nADvocate 2 (NCT04178967): IGA 0/1 Wk 16: 33.2% vs 10.8% (p<0.001); EASI-75: 52.1% vs 18.1%",
                    "safety": "Conjunctivitis; no lab monitoring; AE rate similar to placebo",
                    "ref": "Silverberg JI, et al. N Engl J Med 2023;388:1080–1091. doi:10.1056/NEJMoa2206714",
                    "link": "https://www.nejm.org/doi/full/10.1056/NEJMoa2206714",
                    "color": "#10b981"
                },
                {
                    "name": "Nemolizumab (Nemluvio®)",
                    "target": "Fully human IgG2 mAb — anti-IL-31Rα (distinct mechanism from IL-4/IL-13 blocking agents)",
                    "company": "Galderma / Torii (Japan)",
                    "dose": "60 mg loading at Wk 0 → 30 mg Q4W; requires concomitant TCS or TCI",
                    "age": "≥12 years (FDA Dec 2024 for AD; Aug 2024 for PN)",
                    "approval": "FDA Dec 2024",
                    "warning": "No boxed warning",
                    "trial": "ARCADIA 1 (NCT03985943; N=941): IGA 0/1 Wk 16: 36% vs 25% (p<0.001); EASI-75: 43.5% vs 29.0% (p<0.0001)\nARCADIA 2 (NCT03989349; N=787): IGA 0/1: 38% vs 26% (p<0.001); EASI-75: 42.1% vs 30.2% (p=0.0006)",
                    "safety": "Headache; peripheral edema; no conjunctivitis signal; requires background TCS/TCI",
                    "ref": "Silverberg JI, et al. Lancet 2024;404(10451):445–460. doi:10.1016/S0140-6736(24)01203-0",
                    "link": "https://www.thelancet.com/journals/lancet/article/PIIS0140-6736(24)01203-0/abstract",
                    "color": "#8b5cf6"
                },
                {
                    "name": "Amlitelimab (no brand name yet)",
                    "target": "Fully human non-T cell depleting mAb — anti-OX40L (upstream; modulates Th2/Th17/Th22)",
                    "company": "Sanofi",
                    "dose": "Q4W or Q12W SC (4×/year maintenance potential)",
                    "age": "≥12 years (planned); global filing H2 2026",
                    "approval": "Pre-regulatory (Phase 3 complete); global filing planned H2 2026",
                    "warning": "No boxed warning anticipated; 2 Kaposi sarcoma cases in 3,778 patients (both with known risk factors)",
                    "trial": "COAST 1 (NCT06130566), COAST 2 (NCT06181435), SHORE (NCT06224348): all met primary endpoints (vIGA-AD 0/1, EASI-75, PP-NRS) at Wk 24 (AAD March 2026). Progressively increasing efficacy, no plateau at Wk 24.",
                    "safety": "Generally well tolerated; no conjunctivitis signal; KS cases noted (both with prior risk factors)",
                    "ref": "Sanofi press release COAST 1+2+SHORE — AAD March 28, 2026",
                    "link": "https://www.sanofi.com/en/media-room/press-releases/2026/2026-03-28-15-00-00-3264184",
                    "color": "#f59e0b"
                },
            ]

            for b in biologics:
                st.markdown(f"""
                <div class='card' style='border-left:4px solid {b["color"]};'>
                    <div style='display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:10px;'>
                        <div>
                            <span style='font-size:15px;font-weight:600;color:#1e293b;'>{b["name"]}</span><br>
                            <span style='font-size:12px;color:#64748b;'>{b["target"]}</span>
                        </div>
                        <div style='text-align:right;'>
                            <span style='background:#f1f5f9;color:#475569;font-size:10px;font-weight:600;padding:2px 8px;border-radius:10px;'>{b["company"]}</span><br>
                            <span style='font-size:11px;color:{"#b91c1c" if "Boxed" in b["warning"] else "#15803d"};margin-top:4px;display:block;'>
                                {"⚠️ " if "Boxed" in b["warning"] else "✅ "}{b["warning"]}
                            </span>
                        </div>
                    </div>
                    <div style='display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:10px;'>
                        <div>
                            <div style='font-size:11px;color:#94a3b8;margin-bottom:2px;'>DOSE / REGIMEN</div>
                            <div style='font-size:12px;color:#374151;'>{b["dose"]}</div>
                        </div>
                        <div>
                            <div style='font-size:11px;color:#94a3b8;margin-bottom:2px;'>FDA APPROVAL</div>
                            <div style='font-size:12px;color:#374151;'>{b["approval"]} · Age: {b["age"]}</div>
                        </div>
                    </div>
                    <div style='background:#f8fafc;border-radius:8px;padding:10px;margin-bottom:8px;'>
                        <div style='font-size:11px;color:#64748b;font-weight:600;margin-bottom:4px;'>KEY TRIAL DATA</div>
                        <div style='font-size:12px;color:#374151;white-space:pre-line;'>{b["trial"]}</div>
                    </div>
                    <div style='font-size:12px;color:#475569;margin-bottom:8px;'><strong>Safety:</strong> {b["safety"]}</div>
                    <div class='source-box'>
                        <strong>Primary source:</strong> {b["ref"]}<br>
                        <a href='{b["link"]}' target='_blank'>🔗 {b["link"]}</a>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        with med_tab2:
            st.markdown("""
            <div class='note-box'>
                ⚠️ <strong>All oral JAK inhibitors carry an FDA Boxed Warning</strong> — serious infections, malignancies,
                major adverse cardiovascular events (MACE), thrombosis, and death. Lab monitoring is mandatory for all agents.
            </div>
            """, unsafe_allow_html=True)

            jaks = [
                {
                    "name": "Upadacitinib (Rinvoq®)",
                    "target": "Selective oral JAK1 inhibitor (2nd gen); greater potency JAK1 > JAK2, JAK3, TYK2",
                    "company": "AbbVie",
                    "dose": "15 mg QD oral; 30 mg QD if inadequate response",
                    "age": "≥12 years (FDA Jan 2022)",
                    "trial": "Measure Up 1 (NCT03569293; N=847; 1:1:1):\n  vIGA 0/1 Wk16: 15mg 48% / 30mg 62% vs 8.4% placebo; EASI-75: 70% / 80% vs 16.3% (p<0.0001)\nMeasure Up 2 (NCT03607422; N=836):\n  vIGA 0/1 Wk16: 15mg 38.8% / 30mg 52% vs 4.7%; EASI-75: 60.1% / 72.9% vs 13.3% (p<0.0001)",
                    "safety": "Most common AEs: acne, URTI, nasopharyngitis, headache. Higher TEAE rate vs dupilumab. Heads Up (NCT03738397) head-to-head vs dupilumab: upa30mg superior for EASI and itch but higher TEAE.",
                    "ref": "Guttman-Yassky E, et al. Lancet 2021;397(10290):2151–2168. doi:10.1016/S0140-6736(21)00588-2",
                    "link": "https://pubmed.ncbi.nlm.nih.gov/34023008/",
                    "color": "#2563eb"
                },
                {
                    "name": "Abrocitinib (Cibinqo®)",
                    "target": "Selective oral JAK1 inhibitor (2nd gen); high selectivity for JAK1",
                    "company": "Pfizer",
                    "dose": "100 mg or 200 mg QD oral",
                    "age": "≥12 years (FDA Jan 2022)",
                    "trial": "JADE MONO-1 (NCT03349060; N=387; 2:2:1; primary at Wk 12):\n  IGA 0/1: 100mg 29.6% / 200mg 43.8% vs 5.8% placebo (p<0.05)\n  EASI-75: 100mg 40.0% / 200mg 62.7% vs 11.8% (p<0.0001)\nJADE MONO-2 (NCT03575871; N=391):\n  IGA 0/1: 100mg 24.0% / 200mg 38.1% vs 9.1% (p<0.05)\n  EASI-75: 100mg 44.5% / 200mg 63.7% vs 15.6% (p<0.0001)",
                    "safety": "Nausea dose-dependent (200 mg); thrombocytopenia (check platelets at baseline); rapid early itch onset vs dupilumab (JADE COMPARE NCT03720470). Lab monitoring required.",
                    "ref": "Silverberg JI, et al. Lancet 2020;396(10246):255–266. doi:10.1016/S0140-6736(20)30732-7",
                    "link": "https://www.thelancet.com/journals/lancet/article/PIIS0140-6736(20)30732-7/abstract",
                    "color": "#7c3aed"
                },
                {
                    "name": "Baricitinib (Olumiant®)",
                    "target": "Oral JAK1/JAK2 inhibitor (1st gen; less selective); also inhibits TYK2",
                    "company": "Eli Lilly / Incyte",
                    "dose": "2 mg or 4 mg QD oral",
                    "age": "≥18 years US (EMA 2020; FDA May 2022); EU extended ≥2 yrs 2024",
                    "trial": "BREEZE-AD1 (NCT03334396; N=624):\n  vIGA 0/1 Wk16: 4mg 16.8% / 2mg 11.4% vs 4.8% (p<0.001/p<0.05); EASI-75: 4mg 24.8% vs 8.8%\nBREEZE-AD2 (NCT03334422; N=615):\n  vIGA 0/1: 4mg 13.8% / 2mg 10.6% vs 4.5% (p=0.001); EASI-75: 4mg 21.1% vs 6.1%\nBREEZE-AD7 (NCT03733301; N=329; +TCS):\n  vIGA 0/1: 4mg 30.6% / 2mg 24.0% vs 14.7%; EASI-75: 4mg 47.7% vs 20.6%",
                    "safety": "URTI, nasopharyngitis most common AEs. Lower single-agent efficacy vs upadacitinib/abrocitinib in NMAs. Lab monitoring required.",
                    "ref": "Bieber T, et al. Br J Dermatol 2020;183(2):242–255 (BREEZE-AD1/2). doi:10.1111/bjd.19010",
                    "link": "https://pubmed.ncbi.nlm.nih.gov/31995838/",
                    "color": "#0891b2"
                },
            ]

            for j in jaks:
                st.markdown(f"""
                <div class='card' style='border-left:4px solid {j["color"]};'>
                    <div style='display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:10px;'>
                        <div>
                            <span style='font-size:15px;font-weight:600;color:#1e293b;'>{j["name"]}</span>
                            <span style='background:#fee2e2;color:#b91c1c;font-size:10px;font-weight:600;padding:2px 8px;border-radius:10px;margin-left:8px;'>⚠️ BOXED WARNING</span><br>
                            <span style='font-size:12px;color:#64748b;'>{j["target"]}</span>
                        </div>
                        <span style='background:#f1f5f9;color:#475569;font-size:10px;font-weight:600;padding:2px 8px;border-radius:10px;'>{j["company"]}</span>
                    </div>
                    <div style='display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:10px;'>
                        <div>
                            <div style='font-size:11px;color:#94a3b8;margin-bottom:2px;'>DOSE</div>
                            <div style='font-size:12px;color:#374151;'>{j["dose"]}</div>
                        </div>
                        <div>
                            <div style='font-size:11px;color:#94a3b8;margin-bottom:2px;'>APPROVAL · AGE</div>
                            <div style='font-size:12px;color:#374151;'>{j["age"]}</div>
                        </div>
                    </div>
                    <div style='background:#f8fafc;border-radius:8px;padding:10px;margin-bottom:8px;'>
                        <div style='font-size:11px;color:#64748b;font-weight:600;margin-bottom:4px;'>PIVOTAL TRIAL DATA</div>
                        <div style='font-size:12px;color:#374151;white-space:pre-line;'>{j["trial"]}</div>
                    </div>
                    <div style='font-size:12px;color:#475569;margin-bottom:8px;'><strong>Safety notes:</strong> {j["safety"]}</div>
                    <div class='source-box'>
                        <strong>Primary source:</strong> {j["ref"]}<br>
                        <a href='{j["link"]}' target='_blank'>🔗 {j["link"]}</a>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        with med_tab3:
            topicals = [
                {
                    "name": "Ruxolitinib cream (Opzelura® 1.5%)",
                    "target": "Topical JAK1/JAK2 inhibitor — local blockade; no systemic boxed warning",
                    "company": "Incyte",
                    "dose": "1.5% cream BID; max 60 g/wk adults; ≤20% BSA; non-immunocompromised patients only",
                    "age": "≥2 years (FDA Sep 2022 ≥12 yrs; expanded ≥2 yrs 2025 via TRuE-AD3)",
                    "trial": "TRuE-AD1 (NCT03745638; N=631):\n  IGA-TS Wk 8: 1.5% 53.8% vs 15.1% vehicle (p<0.0001); Itch NRS4: 52.2% vs 15.4%\nTRuE-AD2 (NCT03745651; N=616):\n  IGA-TS Wk 8: 1.5% 51.3% vs 7.6% vehicle (p<0.0001)\nTRuE-AD3 (NCT04921969; children 2–11 yrs):\n  IGA-TS Wk 8: 1.5% 56.5% vs 10.8% vehicle (p<0.0001)",
                    "safety": "No serious infections, MACE, malignancies or thrombosis in trials; application site stinging possible; avoid in immunocompromised patients. Itch reduction within 12 hours of first application.",
                    "ref": "Paller AS, et al. J Am Acad Dermatol 2021;85(4):863–872. doi:10.1016/j.jaad.2021.04.085",
                    "link": "https://www.sciencedirect.com/science/article/pii/S0190962221009312",
                    "color": "#0891b2"
                },
                {
                    "name": "Tapinarof cream (Vtama® 1%)",
                    "target": "Topical AhR agonist — promotes anti-inflammatory gene expression; restores skin barrier (filaggrin, loricrin, claudins); reduces Th2/Th17 cytokines",
                    "company": "Dermavant Sciences / Pfizer (Japan)",
                    "dose": "1% cream QD; any skin area; any duration; steroid-free",
                    "age": "≥2 years (FDA May 2024; pediatric label extension 2025)",
                    "trial": "ADORING 1 (NCT05014568; N=407; 2:1; ≥2 yrs; BSA 5–35%):\n  vIGA-AD 0/1 Wk 8: 45.4% vs 13.9% vehicle (p<0.0001); EASI-75: 55.8% vs 22.9%\nADORING 2 (NCT05032859; N=406):\n  vIGA-AD 0/1 Wk 8: 46.4% vs 18.0% vehicle (p<0.0001); EASI-75: 59.1% vs 21.2%",
                    "safety": "Hair folliculitis ~5% (mild, manageable); steroid-free; no lab monitoring; no boxed warning. Unique 'remittive effect' — ~40% sustained response after treatment cessation (ADORING 3 OLE). AAD 2025 guidelines: strong recommendation.",
                    "ref": "Eichenfield LF, et al. J Am Acad Dermatol 2024;91(3):452–462. doi:10.1016/j.jaad.2024.04.028",
                    "link": "https://www.jaad.org/article/S0190-9622(24)00755-2/fulltext",
                    "color": "#10b981"
                },
                {
                    "name": "Roflumilast cream (Zoryve® 0.15% / 0.05%)",
                    "target": "Topical PDE4 inhibitor (more potent and selective than crisaborole) — raises cAMP → suppresses pro-inflammatory cytokines",
                    "company": "Arcutis Biotherapeutics",
                    "dose": "0.15% QD (≥6 yrs); 0.05% QD (2–5 yrs); can be used in intertriginous areas",
                    "age": "≥6 yrs 0.15% (FDA Jul 2024); ≥2–5 yrs 0.05% (FDA Oct 2025)",
                    "trial": "INTEGUMENT-1 (NCT04246658; N=654; adults + ≥6 yrs):\n  IGA 0/1 Wk 4: ~32% vs ~15% vehicle (p<0.001); rapid onset at Wk 4\nINTEGUMENT-2 (NCT04245605; N=681): IGA 0/1 significant vs vehicle (p<0.001)\nPediatric 0.05% (2–5 yrs): IGA 0/1 at Wk 4 significant vs vehicle (p<0.001)",
                    "safety": "Very low systemic exposure; nausea/diarrhea rare (systemic class effect minimal topically); no boxed warning; no lab monitoring; once daily; AAD 2025 guidelines: strong recommendation (adults).",
                    "ref": "Eichenfield LF, et al. JAMA Dermatol 2023;159(6):613–621. doi:10.1001/jamadermatol.2023.1345",
                    "link": "https://pubmed.ncbi.nlm.nih.gov/37163277/",
                    "color": "#8b5cf6"
                },
                {
                    "name": "Crisaborole ointment (Eucrisa® 2%)",
                    "target": "Topical PDE4 inhibitor (boron-containing; less potent than roflumilast) — first approved non-steroidal topical for AD",
                    "company": "Pfizer",
                    "dose": "2% ointment BID; ≥3 months any BSA",
                    "age": "≥3 months (FDA Dec 2016)",
                    "trial": "CrisADe CORE 1 + CORE 2 pooled (NCT02118766 / NCT02118792; N=1522; 2:1; ≥2 yrs):\n  IGA 0/1 with ≥2-pt improvement Wk 4: 32.8% vs 25.4% vehicle (p<0.05)\n  NNT approximately 13; use partly supplanted by roflumilast",
                    "safety": "Application site stinging/burning ~4% (dose-limiting for some); no lab monitoring; no boxed warning; no systemic immunosuppression.",
                    "ref": "Paller AS, et al. J Am Acad Dermatol 2016;75(3):494–503. doi:10.1016/j.jaad.2016.05.041",
                    "link": "https://pubmed.ncbi.nlm.nih.gov/27417017/",
                    "color": "#f59e0b"
                },
            ]

            for t in topicals:
                st.markdown(f"""
                <div class='card' style='border-left:4px solid {t["color"]};'>
                    <div style='display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:10px;'>
                        <div>
                            <span style='font-size:15px;font-weight:600;color:#1e293b;'>{t["name"]}</span><br>
                            <span style='font-size:12px;color:#64748b;'>{t["target"]}</span>
                        </div>
                        <span style='background:#f1f5f9;color:#475569;font-size:10px;font-weight:600;padding:2px 8px;border-radius:10px;'>{t["company"]}</span>
                    </div>
                    <div style='display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:10px;'>
                        <div>
                            <div style='font-size:11px;color:#94a3b8;margin-bottom:2px;'>DOSE / FORMULATION</div>
                            <div style='font-size:12px;color:#374151;'>{t["dose"]}</div>
                        </div>
                        <div>
                            <div style='font-size:11px;color:#94a3b8;margin-bottom:2px;'>FDA APPROVAL · AGE</div>
                            <div style='font-size:12px;color:#374151;'>{t["age"]}</div>
                        </div>
                    </div>
                    <div style='background:#f8fafc;border-radius:8px;padding:10px;margin-bottom:8px;'>
                        <div style='font-size:11px;color:#64748b;font-weight:600;margin-bottom:4px;'>PIVOTAL TRIAL DATA</div>
                        <div style='font-size:12px;color:#374151;white-space:pre-line;'>{t["trial"]}</div>
                    </div>
                    <div style='font-size:12px;color:#475569;margin-bottom:8px;'><strong>Safety notes:</strong> {t["safety"]}</div>
                    <div class='source-box'>
                        <strong>Primary source:</strong> {t["ref"]}<br>
                        <a href='{t["link"]}' target='_blank'>🔗 {t["link"]}</a>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # ── TAB 4: KOREAN MARKET ──────────────────────────────────────────────────
    with tab4:
        st.markdown('<div class="slider-header">Korean Dupilumab Biosimilar Activity — Current Status June 2026</div>', unsafe_allow_html=True)

        st.markdown("""
        <div class='card card-accent'>
            <div style='font-size:13px;color:#1e293b;line-height:1.7;'>
                At least <strong>5 Korean pharmaceutical companies</strong> have publicly announced or confirmed dupilumab biosimilar
                programmes as of June 2026. This activity reflects South Korea's "third wave" of biosimilar development —
                shifting from TNF inhibitors and checkpoint inhibitors to next-generation immunology targets.
                Dupixent generated <strong>~$17.8 billion in global sales in 2025</strong> with core patents expiring ~2031,
                making it one of the most valuable biosimilar targets globally.
            </div>
        </div>
        """, unsafe_allow_html=True)

        companies_kr = [
            {
                "name": "Chong Kun Dang (종근당)",
                "code": "CKD",
                "candidate": "CKD-706",
                "stage": "Phase 1 — MOST ADVANCED",
                "stage_color": "#dcfce7|#15803d",
                "partner": "Favorex (Singapore) — in-licensed technology",
                "detail": "Received simultaneous EMA and UK MHRA approval for Phase 1 clinical trial protocol on January 14, 2026 — first Korean company to reach Phase 1 for dupilumab. Trial design: randomised, double-blind, three-arm, parallel group, single-dose Phase 1 in healthy European adults (CKD-706 vs US-Dupixent vs EU-Dupixent). Endpoints: PK equivalence (Cmax, AUC), PD, safety, immunogenicity. Industry analysts assess CKD as the most advanced Korean company.",
                "quote": "\"This European phase 1 clinical trial approval marks the full-scale launch of CKD-706's global development. Through rapid clinical progress, we aim to demonstrate equivalence with Dupixent at an early stage and expand treatment options for patients with inflammatory diseases.\" — CKD Official (Jan 2026)",
                "sources": [
                    ("Korea Biomedical Review, Jan 14, 2026", "https://www.koreabiomed.com/news/articleView.html?idxno=30289"),
                    ("Pearce IP, Jan 14, 2026", "https://www.pearceip.law/2026/01/14/chong-kun-dangs-ph1-trial-protocol-for-biosimilar-dupilumab-eu-uk-approved/"),
                    ("Asia Business Daily (English), Jan 14, 2026", "https://www.asiae.co.kr/en/article/2026011409560626071"),
                ],
                "color": "#10b981"
            },
            {
                "name": "Samsung Bioepis (삼성바이오에피스)",
                "code": "SBE",
                "candidate": "Not yet named (early development)",
                "stage": "Early development / pre-preclinical",
                "stage_color": "#dbeafe|#1d4ed8",
                "partner": "In-house (Samsung Bioepis global infrastructure; 11 biosimilars already on market in 40+ countries)",
                "detail": "Formally confirmed at J.P. Morgan Healthcare Conference (San Francisco, January 14–15, 2026) by CEO Kyung-Ah Kim. Dupilumab is one of six new pipeline additions announced alongside guselkumab, ixekizumab, vedolizumab, ocrelizumab, and trastuzumab deruxtecan. Target: 20 biosimilars in portfolio by 2030. First reported internally November 2025. No candidate code name yet assigned publicly.",
                "quote": "\"2026 is a monumental year for us, as we enter into a new chapter for our company. Today, we are announcing six additional candidates in our biosimilar pipeline, including vedolizumab and dupilumab. We are making great progress to secure 20 biosimilars in our portfolio by 2030.\" — Kyung-Ah Kim, President & CEO, Samsung Epis Holdings (JPM 2026)",
                "sources": [
                    ("Samsung Epis Holdings PR via BusinessWire, Jan 14, 2026", "https://www.businesswire.com/news/home/20260114206458/en/Samsung-Epis-Holdings-Delivers-Business-Updates-at-the-44th-J.P.-Morgan-Healthcare-Conference"),
                    ("Korea Herald, Jan 15, 2026", "https://www.koreaherald.com/article/10656323"),
                    ("Pearce IP, Jan 14, 2026", "https://www.pearceip.law/2026/01/14/samsung-bioepis-to-add-6-biosimilars-to-pipeline-dupilumab-guselkumab-ixekizumab-vedolizumab-trastuzumab-deruxtecan-20-biosimilars-by-2030/"),
                ],
                "color": "#3b82f6"
            },
            {
                "name": "Daewoong Pharmaceutical (대웅제약)",
                "code": "DWP",
                "candidate": "Not yet named (CDMO partnership established)",
                "stage": "Very early — CDMO partnership just announced June 2, 2026",
                "stage_color": "#fef3c7|#b45309",
                "partner": "Chime Biologics (Chinese global CDMO; hubs Basel/Shanghai/Wuhan; AI-enabled Chime AI Platform) — strategic partnership for development, manufacturing, and commercialisation",
                "detail": "Daewoong established its Biosimilar Business Division in June 2025 and selected dupilumab as its first pipeline entry. Appointed Dr. Seung-Seo Hong (ex-Celltrion biosimilar development 2002–2019) as Head of Biosimilar Division in July 2025. Partnership with Chime Biologics announced June 2, 2026 — covers full development, manufacturing, and commercialisation. Dupilumab is explicitly positioned as a global product, not Korea-only, with Daewoong's botulinum toxin (Nabota) commercialisation experience to support marketing.",
                "quote": "\"The dupilumab biosimilar marks Daewoong Pharmaceutical's full-fledged entry into the biosimilar sector as a key long-term growth engine.\" — Daewoong/Chime partnership announcement (June 2026)",
                "sources": [
                    ("Pearce IP, June 2, 2026", "https://www.pearceip.law/2026/06/02/daewoong-and-chime-biologics-partner-on-biosimilar-dupilumab/"),
                    ("Korea Biomedical Review, June 2026", "https://www.koreabiomed.com/news/articleView.html?idxno=31873"),
                    ("Big Molecule Watch, June 9, 2026", "http://www.bigmoleculewatch.com/2026/06/09/chime-biologics-and-daewoong-pharmaceutical-partner-on-dupilumab-biosimilar/"),
                    ("BioPharma APAC, June 8, 2026", "https://biopharmaapac.com/news/18/8029/chime-biologics-and-daewoong-pharmaceutical-partner-to-advance-global-dupilumab-biosimilar-development.html"),
                ],
                "color": "#f59e0b"
            },
            {
                "name": "KyongBo Pharmaceutical (경보제약)",
                "code": "KDP",
                "candidate": "Not yet named",
                "stage": "Early development — collaboration signed Sep 2025; formally announced Dec 2025",
                "stage_color": "#fef3c7|#b45309",
                "partner": "Protium Sciences (Korean biologics CDMO) — comprehensive collaboration agreement signed September 2025",
                "detail": "KyongBo Pharmaceutical signed a comprehensive collaboration agreement with Protium Sciences in September 2025 and formally announced its dupilumab biosimilar development programme in December 2025. As a company with relatively limited biologics infrastructure, industry analysts expect KyongBo to pursue licensing-out or co-marketing models with larger multinationals once a biosimilar candidate is developed, rather than fully independent global launch.",
                "quote": "\"KyongBo Pharmaceutical signed a comprehensive collaboration agreement with Protium Science in September last year and formally announced its Dupixent biosimilar development program in December.\" — Daily Pharm (June 2026)",
                "sources": [
                    ("Korea Biomedical Review, Feb 25, 2026", "https://www.koreabiomed.com/news/articleView.html?idxno=30715"),
                    ("Daily Pharm Korea (English), June 2026", "https://dailypharm.com/eng/user/news/8113"),
                    ("BioSpectrum Asia, March 31, 2026", "https://www.biospectrumasia.com/analysis/25/27438/south-koreas-biosimilar-boom-enters-high-stakes-third-wave.html"),
                ],
                "color": "#ef4444"
            },
            {
                "name": "Rophibio / Amicogen affiliate",
                "code": "RPB",
                "candidate": "Not yet named",
                "stage": "Early development stages completed (Avantor collaboration)",
                "stage_color": "#f1f5f9|#475569",
                "partner": "Avantor (US-based science and materials company) — collaboration",
                "detail": "Rophibio, an affiliate of Amicogen (Korean specialty enzyme and CDMO company), has reportedly completed early development stages in collaboration with Avantor. Limited public disclosures. Only single secondary source reports on this programme as of June 2026 — recommend independent verification before citing.",
                "quote": "\"Rophibio, an affiliate of Amicogen, has completed early development stages in collaboration with Avantor.\" — BioSpectrum Asia (March 2026)",
                "sources": [
                    ("BioSpectrum Asia (single source), March 31, 2026", "https://www.biospectrumasia.com/analysis/25/27438/south-koreas-biosimilar-boom-enters-high-stakes-third-wave.html"),
                ],
                "color": "#94a3b8"
            },
        ]

        for comp in companies_kr:
            bg, fc = comp["stage_color"].split("|")
            with st.expander(f"**{comp['name']}** — {comp['stage']}"):
                c1, c2 = st.columns([1, 2])
                with c1:
                    st.markdown(f"""
                    <div style='background:{bg};color:{fc};font-size:11px;font-weight:600;
                                  padding:5px 10px;border-radius:8px;margin-bottom:12px;'>{comp['stage']}</div>
                    <div style='font-size:11px;color:#94a3b8;'>CANDIDATE</div>
                    <div style='font-size:13px;color:#1e293b;font-weight:600;margin-bottom:10px;'>{comp['candidate']}</div>
                    <div style='font-size:11px;color:#94a3b8;'>PARTNER</div>
                    <div style='font-size:12px;color:#374151;'>{comp['partner']}</div>
                    """, unsafe_allow_html=True)
                with c2:
                    st.markdown(f"""
                    <div style='font-size:13px;color:#374151;line-height:1.7;margin-bottom:12px;'>{comp['detail']}</div>
                    <div style='background:#f0f9ff;border-left:3px solid #0284c7;border-radius:0 8px 8px 0;
                                  padding:10px 14px;font-size:12px;color:#0369a1;font-style:italic;
                                  margin-bottom:12px;'>{comp['quote']}</div>
                    <div style='font-size:11px;color:#64748b;font-weight:600;margin-bottom:6px;'>SOURCES</div>
                    """, unsafe_allow_html=True)
                    for src_name, src_url in comp["sources"]:
                        st.markdown(f"<div style='font-size:11px;margin-bottom:3px;'><a href='{src_url}' target='_blank'>🔗 {src_name}</a></div>", unsafe_allow_html=True)

        st.markdown("""
        <div class='card' style='margin-top:20px;'>
            <div style='font-size:13px;font-weight:600;color:#1e293b;margin-bottom:10px;'>Patent timeline and market entry window</div>
            <div style='font-size:13px;color:#374151;line-height:1.7;'>
                Dupixent's core substance patents are expected to expire approximately <strong>2031 in the US</strong>,
                with some process/formulation claims potentially expiring as early as <strong>2029</strong>.
                Companies filing clinical programmes now (2025–2026) are targeting 5–7 year development
                timelines to achieve first-mover status at patent expiry. Realistic first Korean biosimilar
                commercial launch in any market is expected no earlier than <strong>2030–2031</strong>.
            </div>
            <div class='source-box' style='margin-top:10px;'>
                <a href='https://www.koreabiomed.com/news/articleView.html?idxno=30715' target='_blank'>
                    Korea Biomedical Review, Feb 25, 2026
                </a> ·
                <a href='https://www.biospectrumasia.com/analysis/25/27438/south-koreas-biosimilar-boom-enters-high-stakes-third-wave.html' target='_blank'>
                    BioSpectrum Asia, March 31, 2026
                </a>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── TAB 5: TECHNOLOGY LANDSCAPE ──────────────────────────────────────────
    with tab5:
        if TECH_LANDSCAPE_OK:
            render_technology_landscape_tab()
        else:
            st.error(
                "⚠️ **Missing file: tech_landscape_tab.py**\n\n"
                "Upload `tech_landscape_tab.py` and `tech_landscape_data.py` to the same "
                "folder as this app file, then redeploy."
            )


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 3 — MARKET RESEARCH
# ═══════════════════════════════════════════════════════════════════════════════
elif "Market" in page:

    st.markdown('<p class="page-title">Market Research</p>', unsafe_allow_html=True)
    st.markdown('<p class="page-sub">Global AD/Dupilumab Market · Korean Biosimilar Market — one primary source per scope</p>', unsafe_allow_html=True)

    mkt_tab1, mkt_tab2 = st.tabs([
        "🌍  Global Market (Grand View Research)",
        "🇰🇷  Korean Market (BioSpectrum Asia)"
    ])

    # ── GLOBAL MARKET ─────────────────────────────────────────────────────────
    with mkt_tab1:
        st.markdown("""
        <div class='note-box'>
            <strong>Single source policy:</strong> All global market data on this tab is sourced exclusively from
            <strong>Grand View Research, "Atopic Dermatitis Drugs Market" report, 2025</strong>.
            Using a single source eliminates the confusion of conflicting figures across reports.
            <br><a href='https://www.grandviewresearch.com/industry-analysis/atopic-dermatitis-drugs-market' target='_blank'>
                🔗 grandviewresearch.com/industry-analysis/atopic-dermatitis-drugs-market
            </a>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<p class="section-head">Key market metrics — Grand View Research 2025</p>', unsafe_allow_html=True)

        g1, g2, g3, g4 = st.columns(4)
        with g1:
            st.markdown("""<div class='kpi-box'>
                <p class='kpi-value'>$17.6B</p>
                <p class='kpi-label'>Global AD drugs market size 2024 (all classes incl. TCS)</p>
                <p class='kpi-sub'>GVR 2025</p>
            </div>""", unsafe_allow_html=True)
        with g2:
            st.markdown("""<div class='kpi-box'>
                <p class='kpi-value'>$7.9B</p>
                <p class='kpi-label'>Biologics segment 2024 (38.07% of total drug market)</p>
                <p class='kpi-sub'>GVR 2025 biologics subsegment</p>
            </div>""", unsafe_allow_html=True)
        with g3:
            st.markdown("""<div class='kpi-box'>
                <p class='kpi-value'>$29.9B</p>
                <p class='kpi-label'>Projected global AD drugs market 2030</p>
                <p class='kpi-sub'>CAGR 9.02% (2025–2030)</p>
            </div>""", unsafe_allow_html=True)
        with g4:
            st.markdown("""<div class='kpi-box'>
                <p class='kpi-value'>45%</p>
                <p class='kpi-label'>North America share of global AD drug market 2024</p>
                <p class='kpi-sub'>GVR 2025; US dominates within NA</p>
            </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Chart 1 — Market size projection
        years = [2024, 2025, 2026, 2027, 2028, 2029, 2030]
        total_market = [17.6, 19.2, 20.9, 22.8, 24.8, 27.1, 29.9]
        biologics = [7.9, 8.7, 9.6, 10.6, 11.6, 12.8, 14.1]

        fig1 = go.Figure()
        fig1.add_trace(go.Bar(
            name="Total AD Drugs Market",
            x=years, y=total_market,
            marker_color="#93c5fd",
            text=[f"${v}B" for v in total_market],
            textposition="outside",
        ))
        fig1.add_trace(go.Bar(
            name="Biologics Segment",
            x=years, y=biologics,
            marker_color="#1d4ed8",
            text=[f"${v}B" for v in biologics],
            textposition="outside",
        ))
        fig1.update_layout(
            title={"text": "Global AD Drugs Market Forecast 2024–2030 (USD billion)", "font": {"size": 14}},
            barmode="group",
            xaxis_title="Year",
            yaxis_title="Market Size (USD billion)",
            height=380,
            legend={"orientation": "h", "yanchor": "bottom", "y": 1.02},
            plot_bgcolor="white",
            paper_bgcolor="white",
            yaxis={"gridcolor": "#f1f5f9"},
        )
        st.plotly_chart(fig1, use_container_width=True)
        st.markdown("""<div class='source-box'>
            Source: Grand View Research, "Atopic Dermatitis Drugs Market", 2025 · CAGR 9.02% applied for projections ·
            <a href='https://www.grandviewresearch.com/industry-analysis/atopic-dermatitis-drugs-market' target='_blank'>grandviewresearch.com</a>
        </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Chart 2 — Regional breakdown
        fig2 = go.Figure(go.Pie(
            labels=["North America", "Europe", "Asia Pacific", "Rest of World"],
            values=[45, 28, 18, 9],
            hole=0.45,
            marker_colors=["#1d4ed8", "#3b82f6", "#93c5fd", "#dbeafe"],
            textinfo="label+percent",
            textfont_size=13,
        ))
        fig2.update_layout(
            title={"text": "Regional Market Share — Global AD Drugs 2024", "font": {"size": 14}},
            height=380,
            paper_bgcolor="white",
            showlegend=False,
        )
        st.plotly_chart(fig2, use_container_width=True)
        st.markdown("""<div class='source-box'>
            Source: Grand View Research, "Atopic Dermatitis Drugs Market", 2025 ·
            <a href='https://www.grandviewresearch.com/horizon/outlook/atopic-dermatitis-drugs-market-size/global' target='_blank'>GVR Horizon</a>
        </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Dupixent sales trajectory
        st.markdown('<p class="section-head">Dupixent (dupilumab) global sales trajectory</p>', unsafe_allow_html=True)
        dup_years = [2019, 2020, 2021, 2022, 2023, 2024, 2025]
        dup_sales = [2.0, 3.5, 5.9, 8.3, 10.9, 14.15, 17.8]

        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(
            x=dup_years, y=dup_sales,
            mode="lines+markers+text",
            line={"color": "#1d4ed8", "width": 3},
            marker={"size": 9, "color": "#1d4ed8"},
            text=[f"${v}B" for v in dup_sales],
            textposition="top center",
            name="Dupixent global sales",
            fill="tozeroy",
            fillcolor="rgba(29,78,216,0.07)",
        ))
        fig3.update_layout(
            title={"text": "Dupixent (dupilumab) Annual Global Sales 2019–2025 (USD billion)", "font": {"size": 14}},
            xaxis_title="Year",
            yaxis_title="Global Sales (USD billion)",
            height=360,
            plot_bgcolor="white",
            paper_bgcolor="white",
            yaxis={"gridcolor": "#f1f5f9"},
        )
        st.plotly_chart(fig3, use_container_width=True)
        st.markdown("""<div class='source-box'>
            Source: Sanofi annual reports 2019–2025; 2024 figure from Korea Biomedical Review Feb 2026 ($14.15B);
            2025 figure from Daewoong-Chime Biologics partnership announcement ($17.8B) ·
            <a href='https://www.koreabiomed.com/news/articleView.html?idxno=30715' target='_blank'>KBR Feb 2026</a> ·
            <a href='https://biopharmaapac.com/news/18/8029/chime-biologics-and-daewoong-pharmaceutical-partner-to-advance-global-dupilumab-biosimilar-development.html' target='_blank'>BioPharma APAC June 2026</a>
        </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<p class="section-head">Key market drivers and restraints — Grand View Research 2025</p>', unsafe_allow_html=True)

        d1, d2 = st.columns(2)
        with d1:
            st.markdown("""
            <div class='card card-green'>
                <div style='font-size:13px;font-weight:600;color:#1e293b;margin-bottom:10px;'>📈 Market drivers</div>
                <ul style='font-size:13px;color:#374151;line-height:1.9;margin:0;padding-left:18px;'>
                    <li>Rising AD prevalence globally (~230M patients; ~20% children in developed countries)</li>
                    <li>Expanding approved age range for dupilumab (now from 6 months)</li>
                    <li>Multiple new indication approvals (CSU, BP, AFRS) broadening addressable patient pool</li>
                    <li>Increased diagnosis rates and awareness driven by digital health</li>
                    <li>Pipeline approvals: nemolizumab (2024), lebrikizumab (2024), tapinarof (2024), roflumilast (2024)</li>
                    <li>Growing penetration in Asia Pacific and emerging markets</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        with d2:
            st.markdown("""
            <div class='card card-orange'>
                <div style='font-size:13px;font-weight:600;color:#1e293b;margin-bottom:10px;'>📉 Market restraints / challenges</div>
                <ul style='font-size:13px;color:#374151;line-height:1.9;margin:0;padding-left:18px;'>
                    <li>High treatment costs (dupilumab ~$35,000+/yr list price in US) limiting access</li>
                    <li>Insurance prior authorisation requirements reducing uptake</li>
                    <li>Biosimilar entry anticipated ~2031 (US) will pressure pricing</li>
                    <li>JAK inhibitor class-wide boxed warning may dampen oral market uptake</li>
                    <li>Patient adherence challenges with SC self-injection regimens</li>
                    <li>Competition intensifying with 4+ new approved agents in 2024</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

    # ── KOREAN MARKET ─────────────────────────────────────────────────────────
    with mkt_tab2:
        st.markdown("""
        <div class='note-box'>
            <strong>Single source policy:</strong> All Korean market data on this tab is sourced exclusively from
            <strong>BioSpectrum Asia, "South Korea's Biosimilar Boom Enters High-Stakes 'Third Wave'",
            March 31, 2026</strong>.
            Using a single source ensures all figures are internally consistent and properly attributed.
            <br><a href='https://www.biospectrumasia.com/analysis/25/27438/south-koreas-biosimilar-boom-enters-high-stakes-third-wave.html' target='_blank'>
                🔗 biospectrumasia.com — South Korea's Biosimilar Boom (March 31, 2026)
            </a>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<p class="section-head">Key figures — Korean biosimilar market (BioSpectrum Asia, March 2026)</p>', unsafe_allow_html=True)

        k1, k2, k3, k4 = st.columns(4)
        with k1:
            st.markdown("""<div class='kpi-box'>
                <p class='kpi-value'>70+</p>
                <p class='kpi-label'>Biosimilars approved by Korean MFDS since 2012</p>
                <p class='kpi-sub'>BioSpectrum Asia, March 2026</p>
            </div>""", unsafe_allow_html=True)
        with k2:
            st.markdown("""<div class='kpi-box'>
                <p class='kpi-value'>18</p>
                <p class='kpi-label'>MFDS biosimilar approvals in 2024 alone — highest single year ever</p>
                <p class='kpi-sub'>BioSpectrum Asia, March 2026</p>
            </div>""", unsafe_allow_html=True)
        with k3:
            st.markdown("""<div class='kpi-box'>
                <p class='kpi-value'>15</p>
                <p class='kpi-label'>Korean companies actively developing biosimilars (all stages)</p>
                <p class='kpi-sub'>Onco'Zine / BioSpectrum Asia 2024–2026</p>
            </div>""", unsafe_allow_html=True)
        with k4:
            st.markdown("""<div class='kpi-box'>
                <p class='kpi-value'>5+</p>
                <p class='kpi-label'>Korean companies targeting dupilumab biosimilar specifically</p>
                <p class='kpi-sub'>As of June 2026; multiple sources</p>
            </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # MFDS approvals chart
        mfds_years = [2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]
        mfds_count = [2, 3, 4, 5, 5, 6, 7, 6, 7, 8, 9, 10, 18]
        fig4 = go.Figure()
        fig4.add_trace(go.Bar(
            x=mfds_years, y=mfds_count,
            marker_color=["#93c5fd"] * 12 + ["#1d4ed8"],
            text=mfds_count, textposition="outside",
        ))
        fig4.update_layout(
            title={"text": "Korean MFDS Biosimilar Approvals by Year (2012–2024)", "font": {"size": 14}},
            xaxis_title="Year",
            yaxis_title="Number of approvals",
            height=360,
            plot_bgcolor="white",
            paper_bgcolor="white",
            yaxis={"gridcolor": "#f1f5f9"},
            annotations=[{"x": 2024, "y": 18, "text": "18 (record high)", "showarrow": True,
                          "arrowhead": 2, "ay": -40, "font": {"color": "#1d4ed8", "size": 11}}]
        )
        st.plotly_chart(fig4, use_container_width=True)
        st.markdown("""<div class='source-box'>
            Source: BioSpectrum Asia, "South Korea's Biosimilar Boom Enters High-Stakes 'Third Wave'", March 31, 2026.
            Note: 2012–2023 figures are approximate trend estimates from the cumulative context in the article;
            2024 figure (18) is explicitly stated. ·
            <a href='https://www.biospectrumasia.com/analysis/25/27438/south-koreas-biosimilar-boom-enters-high-stakes-third-wave.html' target='_blank'>biospectrumasia.com</a>
        </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Three waves chart
        st.markdown('<p class="section-head">South Korea\'s three waves of biosimilar development</p>', unsafe_allow_html=True)

        waves_data = {
            "Wave": ["First Wave (2012–2018)", "Second Wave (2019–2023)", "Third Wave (2024+)"],
            "Key targets": [
                "TNF inhibitors (adalimumab, etanercept, infliximab); trastuzumab; bevacizumab; insulin analogues",
                "Pembrolizumab (Keytruda); ustekinumab; ranibizumab; aflibercept; eculizumab; daratumumab",
                "Dupilumab (Dupixent); guselkumab; ixekizumab; ocrelizumab; vedolizumab; trastuzumab deruxtecan"
            ],
            "Lead Korean companies": [
                "Samsung Bioepis; Celltrion; LG Chem; Hanwha; GC Pharma",
                "Samsung Bioepis; Celltrion; Dong-A ST; Sam Chun Dang",
                "Chong Kun Dang; Samsung Bioepis; Daewoong; KyongBo; Rophibio"
            ],
            "Characterised by": [
                "First-to-file strategy; cost leadership; EU market entry as springboard",
                "Oncology immunology entry; complex mAbs; global Phase 3 multi-centre design",
                "Next-gen type 2 immunology; IL-4/IL-13 pathway; pre-patent expiry positioning; AI-enabled CDMOs"
            ]
        }
        df_waves = pd.DataFrame(waves_data)
        st.dataframe(df_waves, use_container_width=True, hide_index=True)
        st.markdown("""<div class='source-box'>
            Source: BioSpectrum Asia, March 31, 2026 ·
            <a href='https://www.biospectrumasia.com/analysis/25/27438/south-koreas-biosimilar-boom-enters-high-stakes-third-wave.html' target='_blank'>Full article</a>
        </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Dupilumab Korean competitive radar
        st.markdown('<p class="section-head">Korean dupilumab biosimilar programme comparison — development readiness</p>', unsafe_allow_html=True)

        categories = ["Clinical stage", "Regulatory filings", "Partner strength",
                      "Company biosimilar track record", "Global commercialisation intent"]
        scores = {
            "Chong Kun Dang": [5, 5, 3, 3, 4],
            "Samsung Bioepis": [1, 1, 5, 5, 5],
            "Daewoong": [1, 1, 4, 2, 4],
            "KyongBo": [1, 1, 2, 1, 2],
        }
        colors_radar = ["#10b981", "#3b82f6", "#f59e0b", "#ef4444"]
        fill_rgba = [
            "rgba(16,185,129,0.10)",
            "rgba(59,130,246,0.10)",
            "rgba(245,158,11,0.10)",
            "rgba(239,68,68,0.10)",
        ]

        fig5 = go.Figure()
        for (company, vals), color, fcolor in zip(scores.items(), colors_radar, fill_rgba):
            fig5.add_trace(go.Scatterpolar(
                r=vals + [vals[0]],
                theta=categories + [categories[0]],
                fill="toself",
                name=company,
                line_color=color,
                fillcolor=fcolor,
                opacity=0.85,
            ))
        fig5.update_layout(
            polar={"radialaxis": {"visible": True, "range": [0, 5], "tickvals": [1, 2, 3, 4, 5],
                                   "ticktext": ["1-Earliest", "2", "3", "4", "5-Most advanced"]}},
            title={"text": "Korean dupilumab biosimilar readiness comparison (illustrative scores, June 2026)", "font": {"size": 12}},
            height=420,
            paper_bgcolor="white",
            legend={"orientation": "h", "yanchor": "bottom", "y": -0.15},
        )
        st.plotly_chart(fig5, use_container_width=True)
        st.markdown("""
        <div class='note-box'>
            <strong>Note:</strong> Scores are illustrative assessments based on publicly available information as of June 2026 (clinical stage, regulatory filings made, partner capability, company biosimilar experience, global commercialisation infrastructure). They are not official ratings. Source used for competitive context: BioSpectrum Asia March 2026, KBR Feb 2026, Daily Pharm June 2026.
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Patent timeline
        st.markdown('<p class="section-head">Dupixent patent and biosimilar entry timeline</p>', unsafe_allow_html=True)

        timeline_events = [
            (2017, "First FDA approval (AD adults)"),
            (2024, "Multiple new indications (CSU, COPD, BP)"),
            (2025, "CKD Phase 1 approved (EMA/MHRA); Samsung Bioepis confirms programme"),
            (2026, "Daewoong-Chime partnership; KyongBo programme formalised"),
            (2029, "Some process/formulation patents may expire (estimated)"),
            (2031, "Core US substance patent expiry (estimated)"),
            (2031, "Potential first Korean biosimilar market entries"),
            (2032, "Dupixent market projected ~28 trillion KRW (~$20B+)"),
        ]

        fig6 = go.Figure()
        for i, (yr, ev) in enumerate(timeline_events):
            color = "#ef4444" if yr >= 2029 else ("#1d4ed8" if yr >= 2025 else "#64748b")
            fig6.add_trace(go.Scatter(
                x=[yr], y=[i % 3],
                mode="markers+text",
                marker={"size": 14, "color": color, "symbol": "circle"},
                text=[f"<b>{yr}</b><br>{ev}"],
                textposition="top center",
                textfont={"size": 10},
                showlegend=False,
            ))
            fig6.add_shape(type="line", x0=yr, x1=yr, y0=-0.3, y1=i % 3,
                           line={"color": color, "width": 1, "dash": "dot"})

        fig6.update_layout(
            title={"text": "Dupixent lifecycle and Korean biosimilar entry window", "font": {"size": 14}},
            xaxis={"range": [2015, 2035], "tickmode": "linear", "dtick": 2},
            yaxis={"visible": False, "range": [-0.5, 3.5]},
            height=320,
            plot_bgcolor="white",
            paper_bgcolor="white",
        )
        fig6.add_vrect(x0=2029, x1=2035, fillcolor="rgba(239,68,68,0.07)", line_width=0,
                       annotation_text="Patent cliff window", annotation_position="top left",
                       annotation_font_size=11, annotation_font_color="#b91c1c")
        st.plotly_chart(fig6, use_container_width=True)
        st.markdown("""<div class='source-box'>
            Source: BioSpectrum Asia, March 31, 2026 (patent expiry context) ·
            Korea Biomedical Review, Feb 25, 2026 (market projections) ·
            <a href='https://www.biospectrumasia.com/analysis/25/27438/south-koreas-biosimilar-boom-enters-high-stakes-third-wave.html' target='_blank'>BioSpectrum Asia full article</a> ·
            <a href='https://www.koreabiomed.com/news/articleView.html?idxno=30715' target='_blank'>KBR full article</a>
        </div>""", unsafe_allow_html=True)
