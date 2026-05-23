"""Gap Calculator — score a channel and generate actionable recommendations."""
from __future__ import annotations
import numpy as np
import pandas as pd
from typing import Optional


# Weights for each gap dimension (must sum to 1.0)
GAP_WEIGHTS = {
    "engagement_gap":   0.30,
    "upload_gap":       0.20,
    "views_per_sub_gap":0.25,
    "age_gap":          0.10,
    "niche_gap":        0.15,
}

# Ideal benchmarks per niche
NICHE_BENCHMARKS = {
    "finance":   {"engagement_rate": 0.040, "upload_frequency": 3.0, "cpm": 12.0},
    "fitness":   {"engagement_rate": 0.060, "upload_frequency": 5.0, "cpm":  5.5},
    "comedy":    {"engagement_rate": 0.075, "upload_frequency": 6.0, "cpm":  3.5},
    "education": {"engagement_rate": 0.050, "upload_frequency": 4.0, "cpm":  8.0},
    "tech":      {"engagement_rate": 0.045, "upload_frequency": 4.0, "cpm":  9.5},
    "unknown":   {"engagement_rate": 0.045, "upload_frequency": 4.0, "cpm":  7.0},
}

RECOMMENDATIONS = {
    "engagement_gap": [
        "💬 Add clear calls-to-action (ask viewers to comment their opinion).",
        "📌 Pin a question in comments within 30 min of upload for early engagement.",
        "🎯 Use polls, community posts, and end-screen cards to extend interaction.",
        "✂️ Shorten average video length — engagement rate drops sharply after 8 min.",
    ],
    "upload_gap": [
        "📅 Build a content calendar and commit to a consistent upload schedule.",
        "🎬 Batch-film 3–4 videos in one session to maintain consistency.",
        "📝 Create evergreen content that stays relevant, reducing production pressure.",
        "🔔 Use Shorts to maintain presence during low-production weeks.",
    ],
    "views_per_sub_gap": [
        "🖼️ A/B test thumbnails — bright colours and faces outperform text-heavy designs.",
        "📢 Optimise titles with high-search-volume keywords (use TubeBuddy or VidIQ).",
        "📧 Send community posts 1 hr before upload to warm up the algorithm.",
        "🔗 Cross-promote on Instagram Reels / TikTok to drive external traffic.",
    ],
    "niche_gap": [
        "💰 Pivot toward higher-CPM content formats (reviews, comparisons, tutorials).",
        "🤝 Pursue brand sponsorships directly — 10K-channel deals often beat AdSense.",
        "🎓 Add a mid-roll affiliate link for software/tools relevant to your niche.",
        "🌍 Create country-specific playlists to capture US/UK audience (higher CPM).",
    ],
    "age_gap": [
        "📂 Organise older videos into playlists to drive watch-time on aged content.",
        "🔄 Re-upload top 5 best performers with updated titles and thumbnails.",
        "🏷️ Conduct a tag and description audit on your 20 oldest high-view videos.",
    ],
}


def compute_gap_score(channel: dict, df_benchmark: Optional[pd.DataFrame] = None) -> dict:
    """
    Score a channel's monetisation gap vs benchmarks.
    Returns gap score (0–100, higher = bigger gap) and ranked recommendations.
    """
    niche = channel.get("niche", "unknown").lower()
    bench = NICHE_BENCHMARKS.get(niche, NICHE_BENCHMARKS["unknown"])

    subs = max(channel.get("subscriber_count", 1), 1)
    engagement = channel.get("engagement_rate", 0.03)
    upload_freq = channel.get("upload_frequency", 2.0)
    avg_views = channel.get("avg_views_per_video", 1000)
    channel_age = channel.get("channel_age_days", 365)
    revenue = channel.get("estimated_monthly_revenue", 0)

    # ── 1. Engagement gap ───────────────────────────────────────────────────
    ideal_engagement = bench["engagement_rate"]
    engagement_gap_raw = max(0, (ideal_engagement - engagement) / ideal_engagement)
    engagement_gap = min(1.0, engagement_gap_raw)

    # ── 2. Upload frequency gap ─────────────────────────────────────────────
    ideal_upload = bench["upload_frequency"]
    upload_gap = min(1.0, max(0, (ideal_upload - upload_freq) / ideal_upload))

    # ── 3. Views-per-subscriber gap ─────────────────────────────────────────
    views_per_sub = avg_views / subs
    ideal_views_per_sub = 0.15  # industry rough benchmark
    views_per_sub_gap = min(1.0, max(0, (ideal_views_per_sub - views_per_sub) / ideal_views_per_sub))

    # ── 4. Channel age gap (newer channels penalised) ───────────────────────
    ideal_age = 730  # ~2 years
    age_gap = min(1.0, max(0, (ideal_age - channel_age) / ideal_age))

    # ── 5. Niche CPM gap ────────────────────────────────────────────────────
    max_cpm = max(p["cpm"] for p in NICHE_BENCHMARKS.values())
    niche_gap = 1 - (bench["cpm"] / max_cpm)

    raw_gaps = {
        "engagement_gap":    engagement_gap,
        "upload_gap":        upload_gap,
        "views_per_sub_gap": views_per_sub_gap,
        "age_gap":           age_gap,
        "niche_gap":         niche_gap,
    }

    # Weighted composite gap
    weighted = sum(raw_gaps[k] * GAP_WEIGHTS[k] for k in GAP_WEIGHTS)
    gap_score = round(weighted * 100, 1)

    # Rank gaps by severity
    ranked = sorted(raw_gaps.items(), key=lambda x: x[1] * GAP_WEIGHTS[x[0]], reverse=True)

    # Top 3 recommendations (one per top gap)
    top_recs = []
    for gap_key, _ in ranked[:3]:
        recs = RECOMMENDATIONS.get(gap_key, [])
        if recs:
            top_recs.append(recs[0])

    # Benchmark comparison (if df provided)
    benchmark_stats = {}
    if df_benchmark is not None:
        tier_df = df_benchmark[df_benchmark["niche"] == niche] if niche != "unknown" else df_benchmark
        if len(tier_df) == 0:
            tier_df = df_benchmark
        benchmark_stats = {
            "median_revenue": tier_df["estimated_monthly_revenue"].median(),
            "median_engagement": tier_df["engagement_rate"].median(),
            "median_upload_freq": tier_df["upload_frequency"].median(),
            "percentile_revenue": _percentile(revenue, tier_df["estimated_monthly_revenue"]),
        }

    return {
        "gap_score": gap_score,
        "raw_gaps": raw_gaps,
        "ranked_gaps": ranked,
        "recommendations": top_recs,
        "all_recommendations": {k: RECOMMENDATIONS.get(k, []) for k, _ in ranked},
        "benchmark_stats": benchmark_stats,
    }


def _percentile(value: float, series: pd.Series) -> float:
    """What percentile does value sit in within series?"""
    return round((series < value).mean() * 100, 1)


def gap_label(score: float) -> tuple[str, str]:
    """Return (label, colour) for a gap score."""
    if score < 20:
        return "🏆 Excellent", "#00d4aa"
    if score < 40:
        return "✅ Good", "#6bcb77"
    if score < 60:
        return "⚠️ Room to Improve", "#ffd93d"
    if score < 80:
        return "🚨 Significant Gap", "#ff6b6b"
    return "💀 Critical Gap", "#ff0000"
