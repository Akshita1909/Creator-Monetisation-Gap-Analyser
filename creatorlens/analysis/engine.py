"""Analysis Engine — regression, feature importance, monetisation efficiency, cohorts."""
from __future__ import annotations
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import r2_score
from sklearn.ensemble import GradientBoostingRegressor


FEATURE_COLS = [
    "log_subscribers",
    "engagement_rate",
    "upload_frequency",
    "channel_age_days",
    "avg_views_per_video",
    "video_count",
]

FEATURE_LABELS = {
    "log_subscribers": "Subscriber Count (log)",
    "engagement_rate": "Engagement Rate",
    "upload_frequency": "Upload Frequency",
    "channel_age_days": "Channel Age (days)",
    "avg_views_per_video": "Avg Views / Video",
    "video_count": "Total Videos",
}


def run_regression(df: pd.DataFrame) -> dict:
    """
    Fit linear & gradient boosting models.
    Returns feature importances, model scores, coefficients.
    """
    df = df.dropna(subset=FEATURE_COLS + ["log_revenue"])
    X = df[FEATURE_COLS].values
    y = df["log_revenue"].values

    # Linear regression
    pipe_lr = Pipeline([
        ("scaler", StandardScaler()),
        ("model", Ridge(alpha=1.0)),
    ])
    pipe_lr.fit(X, y)
    y_pred_lr = pipe_lr.predict(X)
    r2_lr = r2_score(y, y_pred_lr)

    coefficients = dict(zip(FEATURE_COLS, pipe_lr.named_steps["model"].coef_))

    # Gradient Boosting for non-linear feature importance
    gbr = GradientBoostingRegressor(n_estimators=100, max_depth=3, random_state=42)
    gbr.fit(X, y)
    y_pred_gbr = gbr.predict(X)
    r2_gbr = r2_score(y, y_pred_gbr)

    importances = dict(zip(FEATURE_COLS, gbr.feature_importances_))

    return {
        "r2_linear": round(r2_lr, 4),
        "r2_gbr": round(r2_gbr, 4),
        "linear_coefficients": coefficients,
        "gbr_importances": importances,
        "feature_labels": FEATURE_LABELS,
        "model_lr": pipe_lr,
        "model_gbr": gbr,
    }


def compute_efficiency_scores(df: pd.DataFrame, model_results: dict) -> pd.DataFrame:
    """
    Monetisation Efficiency Score = actual_revenue / predicted_revenue_for_their_sub_count.
    Score > 1 → over-monetised; < 1 → under-monetised.
    """
    df = df.copy()
    model = model_results["model_gbr"]

    valid = df.dropna(subset=FEATURE_COLS + ["log_revenue"]).copy()
    X = valid[FEATURE_COLS].values
    predicted_log_revenue = model.predict(X)
    predicted_revenue = 10 ** predicted_log_revenue
    actual_revenue = valid["estimated_monthly_revenue"].values

    efficiency = actual_revenue / np.maximum(predicted_revenue, 1)
    valid["predicted_revenue"] = predicted_revenue.round(2)
    valid["efficiency_score"] = efficiency.round(4)
    valid["is_outlier"] = efficiency >= 3.0

    return valid


def detect_outliers(df_with_scores: pd.DataFrame) -> pd.DataFrame:
    """Return channels earning 3x above expected."""
    return df_with_scores[df_with_scores["is_outlier"]].sort_values(
        "efficiency_score", ascending=False
    )


def cohort_analysis(df: pd.DataFrame) -> dict:
    """Group by subscriber tier and compute cohort stats."""
    tier_order = ["Micro (10K–50K)", "Mid (50K–500K)", "Large (500K+)"]
    df = df.copy()
    df["subscriber_tier"] = pd.Categorical(
        df["subscriber_tier"], categories=tier_order, ordered=True
    )
    cohorts = (
        df.groupby("subscriber_tier", observed=True)
        .agg(
            count=("channel_id", "count"),
            avg_revenue=("estimated_monthly_revenue", "mean"),
            median_revenue=("estimated_monthly_revenue", "median"),
            avg_engagement=("engagement_rate", "mean"),
            avg_upload_freq=("upload_frequency", "mean"),
            avg_views=("avg_views_per_video", "mean"),
        )
        .reset_index()
    )
    cohorts.columns = [
        "Tier", "Count", "Avg Revenue ($)", "Median Revenue ($)",
        "Avg Engagement Rate", "Avg Upload Freq (mo)", "Avg Views/Video"
    ]
    cohorts = cohorts.round(2)

    # Niche cohort
    niche_cohort = (
        df.groupby(["niche", "subscriber_tier"], observed=True)
        .agg(avg_revenue=("estimated_monthly_revenue", "mean"))
        .reset_index()
    )

    return {
        "tier_cohort": cohorts,
        "niche_cohort": niche_cohort,
    }


def top_efficient_channels(df_with_scores: pd.DataFrame, n: int = 20) -> pd.DataFrame:
    """Top N most monetisation-efficient channels."""
    cols = [
        "channel_name", "niche", "subscriber_count",
        "estimated_monthly_revenue", "predicted_revenue",
        "efficiency_score", "engagement_rate", "upload_frequency",
    ]
    available = [c for c in cols if c in df_with_scores.columns]
    return (
        df_with_scores[available]
        .sort_values("efficiency_score", ascending=False)
        .head(n)
        .reset_index(drop=True)
    )


def niche_heatmap_data(df: pd.DataFrame) -> pd.DataFrame:
    """Build engagement bucket × niche pivot for heatmap."""
    df = df.copy()
    df["engagement_bucket"] = pd.cut(
        df["engagement_rate"],
        bins=[0, 0.02, 0.04, 0.06, 0.10, 1.0],
        labels=["<2%", "2-4%", "4-6%", "6-10%", ">10%"],
    )
    pivot = df.pivot_table(
        values="estimated_monthly_revenue",
        index="engagement_bucket",
        columns="niche",
        aggfunc="median",
        observed=True,
    ).fillna(0)
    return pivot
