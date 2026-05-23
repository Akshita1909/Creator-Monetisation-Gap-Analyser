"""Plotly visualizations for CreatorLens — dark YouTube aesthetic."""
from __future__ import annotations
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from utils.helpers import NICHE_COLORS, fmt_currency, fmt_number

# ── Theme ──────────────────────────────────────────────────────────────────
BG = "rgba(0,0,0,0)"
PAPER = "rgba(0,0,0,0)"
GRID = "rgba(255,255,255,0.07)"
TEXT_COLOR = "#e8e8e8"
ACCENT = "#ff0000"
FONT = "IBM Plex Mono"

LAYOUT_BASE = dict(
    paper_bgcolor=PAPER,
    plot_bgcolor=BG,
    font=dict(color=TEXT_COLOR, family=FONT, size=12),
    margin=dict(l=20, r=20, t=40, b=20),
    legend=dict(bgcolor="rgba(0,0,0,0)", borderwidth=0),
)

AXIS_BASE = dict(
    gridcolor=GRID,
    zerolinecolor=GRID,
    linecolor="rgba(255,255,255,0.1)",
    tickfont=dict(color=TEXT_COLOR, size=11),
    title_font=dict(color=TEXT_COLOR),
)


def scatter_subs_vs_revenue(df: pd.DataFrame) -> go.Figure:
    """Scatter: subscribers vs estimated revenue, coloured by niche."""
    color_map = {n: NICHE_COLORS[n] for n in df["niche"].unique() if n in NICHE_COLORS}

    fig = px.scatter(
        df,
        x="subscriber_count",
        y="estimated_monthly_revenue",
        color="niche",
        color_discrete_map=color_map,
        hover_name="channel_name",
        hover_data={
            "subscriber_count": ":,",
            "estimated_monthly_revenue": ":.2f",
            "engagement_rate": ":.3f",
            "niche": True,
        },
        log_x=True,
        log_y=True,
        title="Subscribers vs Monthly Revenue",
        labels={
            "subscriber_count": "Subscribers (log)",
            "estimated_monthly_revenue": "Est. Revenue/mo ($, log)",
        },
        opacity=0.75,
        size_max=14,
    )
    fig.update_traces(marker=dict(size=7, line=dict(width=0.5, color="#000")))
    fig.update_layout(**LAYOUT_BASE)
    fig.update_xaxes(**AXIS_BASE)
    fig.update_yaxes(**AXIS_BASE)
    return fig


def feature_importance_bar(importances: dict, labels: dict) -> go.Figure:
    """Horizontal bar chart for GBR feature importances."""
    items = sorted(importances.items(), key=lambda x: x[1])
    features = [labels.get(k, k) for k, _ in items]
    values = [v for _, v in items]
    colors = [f"rgba(255,{int(v*255)},0,0.85)" for v in np.array(values) / max(values)]

    fig = go.Figure(go.Bar(
        x=values,
        y=features,
        orientation="h",
        marker=dict(color=colors, line=dict(width=0)),
        text=[f"{v:.3f}" for v in values],
        textposition="outside",
        textfont=dict(color=TEXT_COLOR, size=11),
    ))
    fig.update_layout(
        title="Revenue Predictor Importance",
        xaxis_title="Importance Score",
        **LAYOUT_BASE,
    )
    fig.update_xaxes(**AXIS_BASE)
    fig.update_yaxes(**{**AXIS_BASE, "tickfont": dict(color=TEXT_COLOR, size=12)})
    return fig


def cohort_revenue_line(cohort_df: pd.DataFrame) -> go.Figure:
    """Line chart: avg/median revenue across subscriber tiers."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=cohort_df["Tier"],
        y=cohort_df["Avg Revenue ($)"],
        mode="lines+markers",
        name="Avg Revenue",
        line=dict(color=ACCENT, width=2.5),
        marker=dict(size=9, color=ACCENT),
    ))
    fig.add_trace(go.Scatter(
        x=cohort_df["Tier"],
        y=cohort_df["Median Revenue ($)"],
        mode="lines+markers",
        name="Median Revenue",
        line=dict(color="#ffd93d", width=2, dash="dash"),
        marker=dict(size=9, color="#ffd93d"),
    ))
    fig.update_layout(
        title="Revenue by Subscriber Tier",
        yaxis_title="Monthly Revenue (USD)",
        **LAYOUT_BASE,
    )
    fig.update_xaxes(**AXIS_BASE)
    fig.update_yaxes(**AXIS_BASE)
    return fig


def niche_heatmap(pivot_df: pd.DataFrame) -> go.Figure:
    """Heatmap: niche × engagement bucket → median revenue."""
    fig = go.Figure(go.Heatmap(
        z=pivot_df.values,
        x=list(pivot_df.columns),
        y=list(pivot_df.index.astype(str)),
        colorscale=[
            [0.0, "#0d0d0d"],
            [0.3, "#3a0000"],
            [0.6, "#9b0000"],
            [1.0, "#ff0000"],
        ],
        showscale=True,
        text=[[f"${v:,.0f}" for v in row] for row in pivot_df.values],
        texttemplate="%{text}",
        hovertemplate="Niche: %{x}<br>Engagement: %{y}<br>Median Revenue: %{text}<extra></extra>",
        colorbar=dict(tickfont=dict(color=TEXT_COLOR)),
    ))
    fig.update_layout(
        title="Niche × Engagement → Median Revenue",
        xaxis_title="Niche",
        yaxis_title="Engagement Rate Bucket",
        **LAYOUT_BASE,
    )
    return fig


def gauge_chart(score: float, label: str, color: str) -> go.Figure:
    """Gauge for gap score."""
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        title={"text": "Monetisation Gap Score", "font": {"color": TEXT_COLOR, "size": 14}},
        number={"font": {"color": color, "size": 36}},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": TEXT_COLOR, "tickwidth": 1},
            "bar": {"color": color, "thickness": 0.25},
            "bgcolor": "rgba(30,30,30,0.5)",
            "borderwidth": 0,
            "steps": [
                {"range": [0,  20], "color": "rgba(0,212,170,0.2)"},
                {"range": [20, 40], "color": "rgba(107,203,119,0.2)"},
                {"range": [40, 60], "color": "rgba(255,217,61,0.2)"},
                {"range": [60, 80], "color": "rgba(255,107,107,0.2)"},
                {"range": [80,100], "color": "rgba(200,0,0,0.2)"},
            ],
        },
    ))
    fig.update_layout(
        paper_bgcolor=PAPER,
        font=dict(color=TEXT_COLOR, family=FONT),
        height=220,
        margin=dict(l=10, r=10, t=30, b=10),
    )
    return fig


def efficiency_scatter(df: pd.DataFrame) -> go.Figure:
    """Scatter: subscribers vs efficiency score, highlight outliers."""
    df = df.copy()
    df["dot_color"] = df["is_outlier"].map({True: "#ff0000", False: "#4d96ff"})
    df["dot_label"] = df["is_outlier"].map({True: "🔥 Outlier", False: "Normal"})

    fig = go.Figure()
    for label, color in [("Normal", "#4d96ff"), ("🔥 Outlier", "#ff0000")]:
        sub = df[df["dot_label"] == label]
        fig.add_trace(go.Scatter(
            x=sub["subscriber_count"],
            y=sub["efficiency_score"],
            mode="markers",
            name=label,
            marker=dict(color=color, size=7 if label == "Normal" else 11, opacity=0.8),
            hovertext=sub["channel_name"],
            hovertemplate="<b>%{hovertext}</b><br>Subs: %{x:,}<br>Efficiency: %{y:.2f}x<extra></extra>",
        ))
    fig.add_hline(y=1.0, line=dict(color="#ffd93d", dash="dash", width=1.5),
                  annotation_text="Expected", annotation_font_color=TEXT_COLOR)
    fig.add_hline(y=3.0, line=dict(color="#ff0000", dash="dot", width=1.5),
                  annotation_text="3× Outlier threshold", annotation_font_color="#ff6b6b")
    fig.update_layout(
        title="Monetisation Efficiency vs Subscribers",
        xaxis_title="Subscribers",
        yaxis_title="Efficiency Score (actual / predicted)",
        xaxis_type="log",
        **LAYOUT_BASE,
    )
    fig.update_xaxes(**AXIS_BASE)
    fig.update_yaxes(**AXIS_BASE)
    return fig


def radar_gap_chart(raw_gaps: dict) -> go.Figure:
    """Radar chart showing gap dimensions for a channel."""
    labels = {
        "engagement_gap":    "Engagement",
        "upload_gap":        "Upload Freq",
        "views_per_sub_gap": "Views/Sub",
        "age_gap":           "Channel Age",
        "niche_gap":         "Niche CPM",
    }
    cats = [labels[k] for k in raw_gaps]
    vals = [raw_gaps[k] * 100 for k in raw_gaps]
    cats += [cats[0]]
    vals += [vals[0]]

    fig = go.Figure(go.Scatterpolar(
        r=vals,
        theta=cats,
        fill="toself",
        fillcolor="rgba(255,0,0,0.2)",
        line=dict(color=ACCENT, width=2),
        name="Gap Dimensions",
    ))
    fig.update_layout(
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            angularaxis=dict(tickfont=dict(color=TEXT_COLOR), linecolor=GRID),
            radialaxis=dict(
                visible=True, range=[0, 100],
                tickfont=dict(color=TEXT_COLOR, size=9),
                gridcolor=GRID,
            ),
        ),
        paper_bgcolor=PAPER,
        font=dict(color=TEXT_COLOR, family=FONT),
        margin=dict(l=40, r=40, t=40, b=40),
        showlegend=False,
        height=300,
    )
    return fig
