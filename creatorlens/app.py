"""
CreatorLens — Monetisation Gap Analyser
Streamlit multi-page app with dark YouTube aesthetic.
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
import pandas as pd
import numpy as np
import time

from data.collector import load_data
from analysis.engine import (
    run_regression, compute_efficiency_scores,
    detect_outliers, cohort_analysis, top_efficient_channels, niche_heatmap_data,
)
from analysis.gap import compute_gap_score, gap_label
from analysis.visualizations import (
    scatter_subs_vs_revenue, feature_importance_bar,
    cohort_revenue_line, niche_heatmap, gauge_chart,
    efficiency_scatter, radar_gap_chart,
)
from utils.helpers import fmt_currency, fmt_number, subscriber_tier, engagement_label, NICHE_COLORS
from utils.youtube_api import fetch_channel_stats, extract_channel_id

# ── Page config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CreatorLens",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@300;400;600&family=Space+Grotesk:wght@400;600;700&display=swap');

/* ─ Root */
:root {
    --yt-red:     #ff0000;
    --yt-dark:    #0f0f0f;
    --yt-card:    #161616;
    --yt-border:  #272727;
    --yt-text:    #e8e8e8;
    --yt-muted:   #aaaaaa;
    --yt-green:   #00d4aa;
    --yt-yellow:  #ffd93d;
    --yt-blue:    #4d96ff;
    --font-mono:  'IBM Plex Mono', monospace;
    --font-ui:    'Space Grotesk', sans-serif;
}

/* ─ Global */
.stApp { background: var(--yt-dark); color: var(--yt-text); font-family: var(--font-ui); }
.block-container { padding-top: 1.5rem; padding-bottom: 2rem; }
h1,h2,h3,h4 { font-family: var(--font-ui); color: var(--yt-text); }

/* ─ Sidebar */
[data-testid="stSidebar"] {
    background: #0a0a0a !important;
    border-right: 1px solid var(--yt-border);
}
[data-testid="stSidebar"] .stRadio label {
    color: var(--yt-muted) !important;
    font-family: var(--font-mono) !important;
    font-size: 0.85rem;
    transition: color 0.2s;
}
[data-testid="stSidebar"] .stRadio label:hover { color: var(--yt-text) !important; }

/* ─ KPI Cards */
.kpi-card {
    background: var(--yt-card);
    border: 1px solid var(--yt-border);
    border-radius: 10px;
    padding: 1.2rem 1.4rem;
    transition: border-color 0.25s, transform 0.2s;
}
.kpi-card:hover { border-color: var(--yt-red); transform: translateY(-2px); }
.kpi-label {
    font-family: var(--font-mono);
    font-size: 0.72rem;
    color: var(--yt-muted);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 0.4rem;
}
.kpi-value {
    font-family: var(--font-mono);
    font-size: 1.9rem;
    font-weight: 600;
    line-height: 1.1;
}
.kpi-sub {
    font-size: 0.75rem;
    color: var(--yt-muted);
    margin-top: 0.3rem;
}

/* ─ Section headers */
.section-head {
    font-family: var(--font-mono);
    font-size: 0.7rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: var(--yt-red);
    border-left: 3px solid var(--yt-red);
    padding-left: 0.7rem;
    margin: 1.5rem 0 0.8rem;
}

/* ─ Logo */
.logo-wrap {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    padding: 1.2rem 1rem 0.6rem;
}
.logo-icon { font-size: 1.6rem; }
.logo-text { font-family: var(--font-ui); font-weight: 700; font-size: 1.15rem; }
.logo-sub { font-family: var(--font-mono); font-size: 0.62rem; color: var(--yt-muted); }

/* ─ Rec cards */
.rec-card {
    background: linear-gradient(135deg, #1a0000 0%, #0f0f0f 100%);
    border: 1px solid #3a0000;
    border-radius: 8px;
    padding: 0.9rem 1.1rem;
    margin-bottom: 0.6rem;
    font-size: 0.9rem;
}

/* ─ Gap dimension bar */
.gap-bar-row {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    margin-bottom: 0.5rem;
    font-family: var(--font-mono);
    font-size: 0.8rem;
}
.gap-bar-label { width: 130px; color: var(--yt-muted); }
.gap-bar-track { flex: 1; background: #1e1e1e; border-radius: 4px; height: 8px; }
.gap-bar-fill { height: 8px; border-radius: 4px; }

/* ─ Inputs */
.stTextInput input, .stSelectbox select, .stNumberInput input {
    background: var(--yt-card) !important;
    border: 1px solid var(--yt-border) !important;
    color: var(--yt-text) !important;
    font-family: var(--font-mono) !important;
    border-radius: 6px !important;
}
.stTextInput input:focus { border-color: var(--yt-red) !important; }

/* ─ Buttons */
.stButton button {
    background: var(--yt-red) !important;
    color: white !important;
    border: none !important;
    font-family: var(--font-ui) !important;
    font-weight: 600 !important;
    border-radius: 6px !important;
    padding: 0.45rem 1.4rem !important;
    transition: opacity 0.2s !important;
}
.stButton button:hover { opacity: 0.88 !important; }

/* ─ DataFrame */
.stDataFrame { border: 1px solid var(--yt-border); border-radius: 8px; }

/* ─ Divider */
hr { border-color: var(--yt-border); }

/* ─ Plotly chart containers */
.js-plotly-plot { border-radius: 10px; }

/* ─ Metric delta */
[data-testid="stMetric"] { background: transparent; }
</style>
""", unsafe_allow_html=True)


# ── Cache data loading ───────────────────────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner=False)
def get_data():
    return load_data()


@st.cache_data(ttl=3600, show_spinner=False)
def get_analysis(df_hash):
    df = st.session_state["_df"]
    results = run_regression(df)
    df_scored = compute_efficiency_scores(df, results)
    cohorts = cohort_analysis(df_scored)
    return results, df_scored, cohorts


# ── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="logo-wrap">
        <div class="logo-icon">🎬</div>
        <div>
            <div class="logo-text">CreatorLens</div>
            <div class="logo-sub">Monetisation Gap Analyser</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    page = st.radio(
        "Navigate",
        ["📊  Overview Dashboard", "🔍  Channel Analyser", "📈  Cohort Analysis"],
        label_visibility="collapsed",
    )
    st.markdown("---")

    with st.expander("⚙️ Settings", expanded=False):
        show_outliers = st.checkbox("Highlight outliers", value=True)
        log_scale = st.checkbox("Log scale on scatter", value=True)

    st.markdown("""
    <div style='font-family:IBM Plex Mono;font-size:0.62rem;color:#555;padding:1rem 0 0;'>
    Data: 500-row seed dataset<br>
    Model: Gradient Boosting<br>
    Rev proxy: avg_views × CPM × 0.45
    </div>
    """, unsafe_allow_html=True)


# ── Load data ────────────────────────────────────────────────────────────────
with st.spinner("Loading dataset…"):
    df = get_data()
    st.session_state["_df"] = df

df_hash = len(df)
with st.spinner("Running analysis models…"):
    reg_results, df_scored, cohorts = get_analysis(df_hash)


# ═══════════════════════════════════════════════════════════════════════════
# PAGE 1 — OVERVIEW DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════
if page == "📊  Overview Dashboard":
    st.markdown("## 📊 Overview Dashboard")
    st.caption(f"Analysing **{len(df):,} channels** across 5 niches · Seed dataset")

    # ── KPI Cards ────────────────────────────────────────────────────────
    st.markdown('<div class="section-head">Key Metrics</div>', unsafe_allow_html=True)
    k1, k2, k3, k4 = st.columns(4)

    avg_rev = df["estimated_monthly_revenue"].mean()
    avg_eng = df["engagement_rate"].mean()
    top_niche = df.groupby("niche")["estimated_monthly_revenue"].mean().idxmax()
    biggest_gap_ch = df_scored.nsmallest(1, "efficiency_score")["channel_name"].values[0]

    with k1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Avg Monthly Revenue</div>
            <div class="kpi-value" style="color:#ff0000">{fmt_currency(avg_rev)}</div>
            <div class="kpi-sub">across all channels</div>
        </div>""", unsafe_allow_html=True)

    with k2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Avg Engagement Rate</div>
            <div class="kpi-value" style="color:#ffd93d">{avg_eng*100:.2f}%</div>
            <div class="kpi-sub">{engagement_label(avg_eng)}</div>
        </div>""", unsafe_allow_html=True)

    with k3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Best Monetising Niche</div>
            <div class="kpi-value" style="color:#00d4aa">{top_niche.upper()}</div>
            <div class="kpi-sub">highest avg revenue</div>
        </div>""", unsafe_allow_html=True)

    with k4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Biggest Efficiency Gap</div>
            <div class="kpi-value" style="color:#ff6b6b;font-size:1.1rem">{biggest_gap_ch[:18]}</div>
            <div class="kpi-sub">lowest efficiency score</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # ── Charts row 1 ─────────────────────────────────────────────────────
    c1, c2 = st.columns([3, 2])
    with c1:
        st.markdown('<div class="section-head">Subscribers vs Revenue</div>', unsafe_allow_html=True)
        st.plotly_chart(scatter_subs_vs_revenue(df), use_container_width=True)

    with c2:
        st.markdown('<div class="section-head">Revenue Predictors</div>', unsafe_allow_html=True)
        st.plotly_chart(
            feature_importance_bar(reg_results["gbr_importances"], reg_results["feature_labels"]),
            use_container_width=True,
        )

    # ── Charts row 2 ─────────────────────────────────────────────────────
    c3, c4 = st.columns([2, 3])
    with c3:
        st.markdown('<div class="section-head">Model Performance</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="kpi-card" style="margin-bottom:0.6rem">
            <div class="kpi-label">Linear R²</div>
            <div class="kpi-value" style="color:#4d96ff;font-size:1.5rem">{reg_results['r2_linear']:.4f}</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Gradient Boost R²</div>
            <div class="kpi-value" style="color:#00d4aa;font-size:1.5rem">{reg_results['r2_gbr']:.4f}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="section-head" style="margin-top:1rem">Niche Distribution</div>', unsafe_allow_html=True)
        niche_counts = df["niche"].value_counts().reset_index()
        niche_counts.columns = ["niche", "count"]
        import plotly.graph_objects as go
        fig_pie = go.Figure(go.Pie(
            labels=niche_counts["niche"],
            values=niche_counts["count"],
            marker=dict(colors=[NICHE_COLORS.get(n, "#aaa") for n in niche_counts["niche"]]),
            hole=0.6,
            textfont=dict(color="#e8e8e8"),
        ))
        fig_pie.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#e8e8e8"),
            margin=dict(l=0,r=0,t=0,b=0),
            showlegend=True,
            legend=dict(bgcolor="rgba(0,0,0,0)"),
            height=200,
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    with c4:
        st.markdown('<div class="section-head">Monetisation Efficiency vs Subscribers</div>', unsafe_allow_html=True)
        st.plotly_chart(efficiency_scatter(df_scored), use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════════
# PAGE 2 — CHANNEL ANALYSER
# ═══════════════════════════════════════════════════════════════════════════
elif page == "🔍  Channel Analyser":
    st.markdown("## 🔍 Channel Analyser")
    st.caption("Paste a YouTube channel URL or enter stats manually to get your monetisation gap score.")

    tab_url, tab_manual = st.tabs(["🔗 YouTube URL", "✍️ Manual Input"])

    channel_data = None

    with tab_url:
        url_input = st.text_input(
            "YouTube Channel URL",
            placeholder="https://www.youtube.com/@MrBeast or https://www.youtube.com/channel/UCX6…",
        )
        niche_sel = st.selectbox("Niche", ["finance", "fitness", "comedy", "education", "tech", "unknown"])

        if st.button("Analyse Channel 🚀", key="btn_url"):
            if not url_input:
                st.warning("Please enter a URL.")
            else:
                with st.spinner("Fetching channel data from YouTube API…"):
                    time.sleep(0.5)
                    identifier = extract_channel_id(url_input) or url_input
                    stats = fetch_channel_stats(identifier)

                if stats is None:
                    st.info(
                        "⚠️ YouTube API key not set or channel not found. "
                        "Set `YOUTUBE_API_KEY` in `.env` to enable live lookups. "
                        "**Using demo mode instead:**",
                        icon="ℹ️"
                    )
                    # Demo fallback: pick a random channel from dataset
                    sample = df.sample(1).iloc[0].to_dict()
                    channel_data = {**sample, "niche": niche_sel}
                else:
                    channel_data = {**stats, "niche": niche_sel}

    with tab_manual:
        st.markdown("##### Enter your channel's stats manually")
        mc1, mc2 = st.columns(2)
        with mc1:
            m_name = st.text_input("Channel Name", value="My Channel")
            m_subs = st.number_input("Subscribers", min_value=1000, value=50000, step=1000)
            m_views = st.number_input("Avg Views / Video", min_value=100, value=5000, step=100)
            m_eng = st.slider("Engagement Rate (%)", 0.1, 15.0, 4.0, 0.1) / 100
        with mc2:
            m_niche = st.selectbox("Niche", ["finance","fitness","comedy","education","tech","unknown"], key="m_niche")
            m_upload = st.slider("Uploads / Month", 0.5, 30.0, 4.0, 0.5)
            m_age = st.number_input("Channel Age (days)", min_value=30, value=730)
            m_country = st.selectbox("Country", ["US","UK","IN","CA","AU","DE","BR","FR","JP","MX"])

        if st.button("Calculate Gap Score", key="btn_manual"):
            channel_data = {
                "channel_name": m_name,
                "niche": m_niche,
                "subscriber_count": m_subs,
                "avg_views_per_video": m_views,
                "engagement_rate": m_eng,
                "upload_frequency": m_upload,
                "channel_age_days": m_age,
                "country": m_country,
                "estimated_monthly_revenue": (m_views * m_upload * 0.003),
            }

    # ── Results ───────────────────────────────────────────────────────────
    if channel_data:
        st.markdown("---")
        gap_result = compute_gap_score(channel_data, df)
        score = gap_result["gap_score"]
        label, color = gap_label(score)

        st.markdown(f"### Results for **{channel_data.get('channel_name','Channel')}**")

        r1, r2, r3 = st.columns([2, 2, 3])

        with r1:
            st.plotly_chart(gauge_chart(score, label, color), use_container_width=True)
            st.markdown(f"<div style='text-align:center;font-size:1.2rem;font-weight:700;color:{color}'>{label}</div>", unsafe_allow_html=True)

        with r2:
            st.markdown("#### Channel Stats")
            stats_to_show = {
                "Subscribers": fmt_number(channel_data.get("subscriber_count", 0)),
                "Avg Views/Video": fmt_number(channel_data.get("avg_views_per_video", 0)),
                "Engagement Rate": f"{channel_data.get('engagement_rate',0)*100:.2f}%",
                "Upload Freq": f"{channel_data.get('upload_frequency',0):.1f}/mo",
                "Niche": channel_data.get("niche","?").upper(),
                "Est. Revenue": fmt_currency(channel_data.get("estimated_monthly_revenue",0)),
            }
            for k, v in stats_to_show.items():
                st.markdown(f"""
                <div style='display:flex;justify-content:space-between;
                    border-bottom:1px solid #222;padding:0.3rem 0;
                    font-family:IBM Plex Mono;font-size:0.82rem;'>
                    <span style='color:#aaa'>{k}</span>
                    <span style='color:#e8e8e8'>{v}</span>
                </div>""", unsafe_allow_html=True)

        with r3:
            st.markdown("#### Gap Radar")
            st.plotly_chart(radar_gap_chart(gap_result["raw_gaps"]), use_container_width=True)

        # Benchmark
        if gap_result["benchmark_stats"]:
            bench = gap_result["benchmark_stats"]
            st.markdown('<div class="section-head">Benchmark vs Similar Channels</div>', unsafe_allow_html=True)
            b1, b2, b3, b4 = st.columns(4)
            b1.metric("Median Niche Revenue", fmt_currency(bench["median_revenue"]))
            b2.metric("Median Engagement", f"{bench['median_engagement']*100:.2f}%")
            b3.metric("Median Upload Freq", f"{bench['median_upload_freq']:.1f}/mo")
            b4.metric("Your Revenue Percentile", f"{bench['percentile_revenue']:.0f}th")

        # Recommendations
        st.markdown('<div class="section-head">Top 3 Recommendations</div>', unsafe_allow_html=True)
        for i, rec in enumerate(gap_result["recommendations"], 1):
            st.markdown(f'<div class="rec-card"><b>#{i}</b> {rec}</div>', unsafe_allow_html=True)

        # Gap breakdown
        with st.expander("📐 Full Gap Breakdown", expanded=False):
            gap_labels_map = {
                "engagement_gap":    "Engagement Quality",
                "upload_gap":        "Upload Frequency",
                "views_per_sub_gap": "Views per Subscriber",
                "age_gap":           "Channel Age",
                "niche_gap":         "Niche CPM Potential",
            }
            for gap_key, val in gap_result["ranked_gaps"]:
                pct = int(val * 100)
                bar_color = "#ff0000" if pct > 60 else "#ffd93d" if pct > 30 else "#00d4aa"
                st.markdown(f"""
                <div class="gap-bar-row">
                    <div class="gap-bar-label">{gap_labels_map.get(gap_key, gap_key)}</div>
                    <div class="gap-bar-track">
                        <div class="gap-bar-fill" style="width:{pct}%;background:{bar_color}"></div>
                    </div>
                    <div style="width:35px;text-align:right;color:#aaa">{pct}%</div>
                </div>""", unsafe_allow_html=True)
            st.markdown("---")
            for gap_key, _ in gap_result["ranked_gaps"]:
                recs = gap_result["all_recommendations"].get(gap_key, [])
                if recs:
                    st.markdown(f"**{gap_labels_map.get(gap_key, gap_key)}**")
                    for r in recs:
                        st.markdown(f"- {r}")


# ═══════════════════════════════════════════════════════════════════════════
# PAGE 3 — COHORT ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════
elif page == "📈  Cohort Analysis":
    st.markdown("## 📈 Cohort Analysis")
    st.caption("Comparing revenue trends, engagement, and efficiency across subscriber tiers and niches.")

    # Row 1: Cohort line + heatmap
    ch1, ch2 = st.columns([2, 3])
    with ch1:
        st.markdown('<div class="section-head">Revenue by Subscriber Tier</div>', unsafe_allow_html=True)
        st.plotly_chart(cohort_revenue_line(cohorts["tier_cohort"]), use_container_width=True)

        # Cohort table
        st.markdown('<div class="section-head">Cohort Summary</div>', unsafe_allow_html=True)
        disp = cohorts["tier_cohort"].copy()
        disp["Avg Revenue ($)"] = disp["Avg Revenue ($)"].apply(lambda x: f"${x:,.0f}")
        disp["Median Revenue ($)"] = disp["Median Revenue ($)"].apply(lambda x: f"${x:,.0f}")
        disp["Avg Engagement Rate"] = disp["Avg Engagement Rate"].apply(lambda x: f"{x*100:.2f}%")
        st.dataframe(disp, use_container_width=True, hide_index=True)

    with ch2:
        st.markdown('<div class="section-head">Niche × Engagement → Median Revenue</div>', unsafe_allow_html=True)
        pivot = niche_heatmap_data(df_scored)
        st.plotly_chart(niche_heatmap(pivot), use_container_width=True)

    st.markdown("---")

    # Row 2: Top efficient channels
    st.markdown('<div class="section-head">Top 20 Most Monetisation-Efficient Channels</div>', unsafe_allow_html=True)
    top20 = top_efficient_channels(df_scored, n=20)
    display_top = top20.copy()

    # Format columns
    if "subscriber_count" in display_top.columns:
        display_top["subscriber_count"] = display_top["subscriber_count"].apply(fmt_number)
    if "estimated_monthly_revenue" in display_top.columns:
        display_top["estimated_monthly_revenue"] = display_top["estimated_monthly_revenue"].apply(fmt_currency)
    if "predicted_revenue" in display_top.columns:
        display_top["predicted_revenue"] = display_top["predicted_revenue"].apply(fmt_currency)
    if "efficiency_score" in display_top.columns:
        display_top["efficiency_score"] = display_top["efficiency_score"].apply(lambda x: f"{x:.2f}×")
    if "engagement_rate" in display_top.columns:
        display_top["engagement_rate"] = display_top["engagement_rate"].apply(lambda x: f"{x*100:.2f}%")
    if "upload_frequency" in display_top.columns:
        display_top["upload_frequency"] = display_top["upload_frequency"].apply(lambda x: f"{x:.1f}/mo")

    display_top.columns = [c.replace("_", " ").title() for c in display_top.columns]
    st.dataframe(display_top, use_container_width=True, hide_index=True)

    # Row 3: Niche breakdown
    st.markdown('<div class="section-head">Revenue by Niche & Tier</div>', unsafe_allow_html=True)
    nc = cohorts["niche_cohort"]
    import plotly.express as px
    tier_order = ["Micro (10K–50K)", "Mid (50K–500K)", "Large (500K+)"]
    color_map = {n: NICHE_COLORS.get(n, "#aaa") for n in nc["niche"].unique()}
    fig_bar = px.bar(
        nc,
        x="subscriber_tier",
        y="avg_revenue",
        color="niche",
        barmode="group",
        color_discrete_map=color_map,
        category_orders={"subscriber_tier": tier_order},
        labels={"avg_revenue": "Avg Revenue ($)", "subscriber_tier": "Subscriber Tier"},
        title="Avg Monthly Revenue: Niche × Tier",
    )
    fig_bar.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e8e8e8", family="IBM Plex Mono"),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
        margin=dict(l=20,r=20,t=40,b=20),
    )
    fig_bar.update_xaxes(gridcolor="rgba(255,255,255,0.07)")
    fig_bar.update_yaxes(gridcolor="rgba(255,255,255,0.07)")
    st.plotly_chart(fig_bar, use_container_width=True)
