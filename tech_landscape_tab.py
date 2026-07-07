"""
tech_landscape_tab.py

Renders the "Technology Landscape" tab for the Dupilumab Intelligence
Dashboard, styled to match the app's existing card/badge/source-box CSS
(defined in app.py's <style> block — this module does not inject its own CSS).

Usage in app.py:

    from tech_landscape_tab import render_technology_landscape_tab
    ...
    with tab5:
        render_technology_landscape_tab()

Requires: streamlit, plotly, tech_landscape_data.py in the same folder.
"""

import streamlit as st
import plotly.graph_objects as go

from tech_landscape_data import ENTRIES, LAST_UPDATED, entries_with_concentration

# ── Stage ordering for the x-axis of the positioning chart ────────────────────
STAGE_X = {
    "Proof-of-concept": 0,
    "Platform PoC": 0.6,
    "Preclinical": 1.2,
    "Internal R&D": 1.2,
    "Phase 1": 2.2,
    "Phase 3": 2.8,
    "CDMO service available": 3.3,
    "Commercial": 3.8,
}
STAGE_TICKS = [0, 0.6, 1.2, 2.2, 2.8, 3.3, 3.8]
STAGE_LABELS = ["Proof-of-\nconcept", "Platform\nPoC", "Preclinical /\nInternal",
                "Phase 1", "Phase 3", "CDMO\nservice", "Commercial"]

# Category → left-border / marker colour, matched to the app's existing palette
CATEGORY_COLOR = {
    "Liquid + excipient": "#3b82f6",     # blue — same family as card-accent
    "Enzyme co-formulation": "#f59e0b",  # amber — same family as card-orange
    "Suspension / particle": "#10b981",  # green — same family as card-green
    "Crystalline": "#8b5cf6",            # purple — same family as card-purple
    "Internal": "#ef4444",               # red — stands out deliberately
}

# Phase → (badge background, badge text colour), matched to the app's existing badge palette
PHASE_BADGE = {
    "Commercial": ("#dcfce7", "#15803d"),
    "CDMO service available": ("#dbeafe", "#1d4ed8"),
    "Phase 3": ("#ede9fe", "#6d28d9"),
    "Phase 1": ("#fef3c7", "#b45309"),
    "Preclinical": ("#fef3c7", "#b45309"),
    "Platform PoC": ("#fce7f3", "#9d174d"),
    "Proof-of-concept": ("#f1f5f9", "#475569"),
    "Internal R&D": ("#fee2e2", "#b91c1c"),
}


def _positioning_chart():
    plotted = entries_with_concentration()
    by_category = {}
    for e in plotted:
        by_category.setdefault(e["category"], []).append(e)

    fig = go.Figure()
    for category, items in by_category.items():
        fig.add_trace(go.Scatter(
            x=[STAGE_X.get(e["phase"], 1.2) for e in items],
            y=[e["concentration_mgml"] for e in items],
            mode="markers+text",
            name=category,
            text=[e["name"] for e in items],
            textposition="top center",
            textfont={"size": 10, "color": "#475569"},
            marker={
                "size": [22 if e["id"] == "our_platform" else 15 for e in items],
                "color": CATEGORY_COLOR.get(category, "#94a3b8"),
                "line": {"width": 2, "color": "white"},
            },
            hovertemplate="<b>%{text}</b><br>%{y} mg/mL<extra></extra>",
        ))

    fig.update_layout(
        title={"text": "Concentration vs. development stage — all tracked technologies", "font": {"size": 14}},
        xaxis={
            "title": "Development stage",
            "tickmode": "array",
            "tickvals": STAGE_TICKS,
            "ticktext": STAGE_LABELS,
            "range": [-0.4, 4.2],
            "gridcolor": "#f1f5f9",
        },
        yaxis={"title": "Concentration (mg/mL)", "range": [0, 680], "gridcolor": "#f1f5f9"},
        height=440,
        margin={"t": 50, "b": 70},
        plot_bgcolor="white",
        paper_bgcolor="white",
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.08, "x": 0},
    )
    return fig


def render_technology_landscape_tab():
    st.markdown(
        '<div class="slider-header">High-Concentration SC Delivery — Technology Landscape</div>',
        unsafe_allow_html=True,
    )
    st.markdown(f"""
    <div style='font-size:13px; color:#374151; line-height:1.7; margin-bottom:14px;'>
        Benchmarks Dupixent and our internal platform against {len(ENTRIES)} tracked high-concentration
        and large-volume subcutaneous delivery technologies — enzyme co-formulation, suspension/particle,
        crystalline, and conventional liquid-excipient approaches. Last research pass: {LAST_UPDATED.isoformat()}.
    </div>
    """, unsafe_allow_html=True)

    # ── KPI row ──
    n_commercial = sum(1 for e in ENTRIES if e["phase"] == "Commercial")
    n_with_conc = len(entries_with_concentration())
    top = max(entries_with_concentration(), key=lambda e: e["concentration_mgml"])
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(f"""<div class='kpi-box'>
            <p class='kpi-value'>{len(ENTRIES)}</p>
            <p class='kpi-label'>Technologies tracked</p>
            <p class='kpi-sub'>Across 5 mechanism categories</p>
        </div>""", unsafe_allow_html=True)
    with k2:
        st.markdown(f"""<div class='kpi-box'>
            <p class='kpi-value'>{n_with_conc}</p>
            <p class='kpi-label'>With a comparable mg/mL figure</p>
            <p class='kpi-sub'>Enzyme platforms excluded (volume, not concentration)</p>
        </div>""", unsafe_allow_html=True)
    with k3:
        st.markdown(f"""<div class='kpi-box'>
            <p class='kpi-value'>{top['concentration_mgml']}+</p>
            <p class='kpi-label'>Highest reported (mg/mL)</p>
            <p class='kpi-sub'>{top['name']} &amp; our platform (tied)</p>
        </div>""", unsafe_allow_html=True)
    with k4:
        st.markdown(f"""<div class='kpi-box'>
            <p class='kpi-value'>{n_commercial}</p>
            <p class='kpi-label'>Already commercial</p>
            <p class='kpi-sub'>Mostly enzyme co-formulation / liquid</p>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Positioning chart ──
    st.plotly_chart(_positioning_chart(), use_container_width=True)
    st.markdown("""
    <div class='source-box'>
        Only entries with a directly comparable mg/mL figure are plotted. Enzyme co-formulation platforms
        (ENHANZE, ALT-B4) enable large-volume delivery rather than raising concentration, so they sit outside
        this axis — see their cards below for details instead.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Filter + cards ──
    st.markdown('<p class="section-head">Full technology list</p>', unsafe_allow_html=True)

    all_categories = sorted({e["category"] for e in ENTRIES})
    cat_filter = st.multiselect(
        "Filter by mechanism",
        all_categories,
        default=[],
        placeholder="All mechanisms",
        key="tech_landscape_cat_filter",
    )
    filtered = [e for e in ENTRIES if (not cat_filter or e["category"] in cat_filter)]

    st.markdown(f"**Showing {len(filtered)} of {len(ENTRIES)} technologies**")
    st.markdown("<br>", unsafe_allow_html=True)

    for entry in filtered:
        bg, fc = PHASE_BADGE.get(entry["phase"], ("#f1f5f9", "#475569"))
        border_color = CATEGORY_COLOR.get(entry["category"], "#94a3b8")
        star = " ⭐" if entry["id"] == "our_platform" else ""

        with st.expander(f"**{entry['name']}{star}** — {entry['developer']}"):
            c1, c2 = st.columns([1, 2])
            with c1:
                st.markdown(f"""
                <span style='background:{bg};color:{fc};font-size:11px;font-weight:600;
                              padding:3px 9px;border-radius:12px;'>{entry['phase']}</span>
                &nbsp;
                <span style='background:#f1f5f9;color:#475569;font-size:11px;font-weight:600;
                              padding:3px 9px;border-radius:12px;'>{entry['category']}</span>
                <div style='margin-top:12px;font-size:11px;color:#94a3b8;'>DEVELOPER</div>
                <div style='font-size:13px;color:#1e293b;font-weight:500;margin-bottom:10px;'>{entry['developer']}</div>
                <div style='font-size:11px;color:#94a3b8;'>CONCENTRATION</div>
                <div style='font-size:14px;color:#1e293b;font-weight:600;line-height:1.4;'>{entry['concentration_display']}</div>
                """, unsafe_allow_html=True)
            with c2:
                st.markdown(f"""
                <div style='background:#f8fafc;border-radius:8px;padding:10px 14px;border-left:3px solid {border_color};'>
                    <span style='font-size:11px;color:#64748b;font-weight:600;'>MECHANISM</span>
                    <p style='font-size:13px;color:#1e293b;line-height:1.6;margin:4px 0 0;'>{entry['mechanism_long']}</p>
                </div>
                """, unsafe_allow_html=True)

                if entry["deals"]:
                    deals_html = "".join(f"<li style='margin-bottom:3px;'>{d}</li>" for d in entry["deals"])
                    st.markdown(f"""
                    <div style='margin-top:10px;'>
                        <span style='font-size:11px;color:#64748b;font-weight:600;'>DEAL / PARTNERSHIP ACTIVITY</span>
                        <ul style='font-size:12px;color:#374151;line-height:1.6;margin:4px 0 0;padding-left:18px;'>
                            {deals_html}
                        </ul>
                    </div>
                    """, unsafe_allow_html=True)

                if entry["source_url"]:
                    st.markdown(f"""
                    <div class='source-box' style='margin-top:10px;'>
                        <strong>Source:</strong> {entry['source_name']} ·
                        <a href='{entry["source_url"]}' target='_blank'>🔗 {entry['source_url']}</a>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class='note-box' style='margin-top:10px;'>
                        <strong>Source:</strong> {entry['source_name']} — internal data, no external link.
                    </div>
                    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"""
    <div class='note-box'>
        <strong>Maintenance note:</strong> this landscape moves fast — 5 of the {len(ENTRIES)} entries above
        reflect news from the last 12 months (Sanofi/Alteogen dupilumab disclosure, Halozyme's Elektrofi and
        Surf Bio acquisitions, the Halozyme–Vertex Hypercon deal, and Nanoform's first biologics exclusivity
        deal). Re-check periodically rather than treating this as a one-time snapshot. To update a figure,
        edit the corresponding entry in <code>tech_landscape_data.py</code>.
    </div>
    """, unsafe_allow_html=True)
