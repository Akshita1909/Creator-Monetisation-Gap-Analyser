"""Data collection module — loads seed CSV or fetches from YouTube API, caches in SQLite."""
from __future__ import annotations
import os
import sqlite3
import logging
from pathlib import Path
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).parent
SEED_CSV = DATA_DIR / "seed_data.csv"
CACHE_DB  = DATA_DIR / "cache.db"


# ── SQLite helpers ──────────────────────────────────────────────────────────

def _get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(CACHE_DB)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS channels (
            channel_id TEXT PRIMARY KEY,
            channel_name TEXT,
            niche TEXT,
            country TEXT,
            subscriber_count INTEGER,
            view_count INTEGER,
            video_count INTEGER,
            avg_views_per_video INTEGER,
            engagement_rate REAL,
            upload_frequency REAL,
            channel_age_days INTEGER,
            estimated_monthly_revenue REAL,
            fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    return conn


def cache_channels(df: pd.DataFrame) -> None:
    """Upsert channels into SQLite cache."""
    conn = _get_conn()
    cols = [
        "channel_id","channel_name","niche","country",
        "subscriber_count","view_count","video_count",
        "avg_views_per_video","engagement_rate","upload_frequency",
        "channel_age_days","estimated_monthly_revenue"
    ]
    df_sub = df[[c for c in cols if c in df.columns]].copy()
    df_sub.to_sql("channels", conn, if_exists="replace", index=False)
    conn.close()


def load_from_cache() -> pd.DataFrame | None:
    """Load from SQLite if populated."""
    if not CACHE_DB.exists():
        return None
    try:
        conn = _get_conn()
        df = pd.read_sql("SELECT * FROM channels", conn)
        conn.close()
        if len(df) >= 10:
            return df
    except Exception as e:
        logger.warning(f"Cache read failed: {e}")
    return None


# ── Main loader ─────────────────────────────────────────────────────────────

def load_data(force_refresh: bool = False) -> pd.DataFrame:
    """
    Load channel data with fallback priority:
      1. SQLite cache (unless force_refresh)
      2. Seed CSV
    Enriches with derived features.
    """
    if not force_refresh:
        cached = load_from_cache()
        if cached is not None:
            logger.info(f"Loaded {len(cached)} channels from cache.")
            return _enrich(cached)

    # Fallback: seed CSV
    if SEED_CSV.exists():
        df = pd.read_csv(SEED_CSV)
        logger.info(f"Loaded {len(df)} rows from seed CSV.")
        cache_channels(df)
        return _enrich(df)

    raise FileNotFoundError("No data source available. Seed CSV missing and cache empty.")


def _enrich(df: pd.DataFrame) -> pd.DataFrame:
    """Add derived columns used by analysis."""
    df = df.copy()

    # Subscriber tier
    def _tier(s):
        if s < 50_000:  return "Micro (10K–50K)"
        if s < 500_000: return "Mid (50K–500K)"
        return "Large (500K+)"
    df["subscriber_tier"] = df["subscriber_count"].apply(_tier)

    # Revenue per 1K subscribers (monetisation efficiency proxy)
    df["rev_per_1k_subs"] = (
        df["estimated_monthly_revenue"] / (df["subscriber_count"] / 1000)
    ).round(4)

    # Log-transform for regression
    df["log_subscribers"] = np.log10(df["subscriber_count"].clip(lower=1))
    df["log_revenue"] = np.log10(df["estimated_monthly_revenue"].clip(lower=0.01))
    df["log_avg_views"] = np.log10(df["avg_views_per_video"].clip(lower=1))

    return df


def upsert_channel(channel_data: dict) -> None:
    """Insert or update a single channel fetched from API."""
    df = pd.DataFrame([channel_data])
    conn = _get_conn()
    df.to_sql("channels", conn, if_exists="append", index=False)
    conn.close()
