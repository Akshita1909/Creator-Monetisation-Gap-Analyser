"""YouTube Data API v3 wrapper with quota-safe helpers."""
from __future__ import annotations
import os
import re
import time
import logging
from typing import Optional
import requests

logger = logging.getLogger(__name__)

_API_BASE = "https://www.googleapis.com/youtube/v3"


def _get_api_key() -> Optional[str]:
    return os.getenv("YOUTUBE_API_KEY")


def extract_channel_id(url_or_handle: str) -> Optional[str]:
    """Extract channel ID or handle from various YouTube URL formats."""
    patterns = [
        r"youtube\.com/channel/([UC][\w-]{22})",
        r"youtube\.com/@([\w.-]+)",
        r"youtube\.com/c/([\w.-]+)",
        r"youtube\.com/user/([\w.-]+)",
    ]
    for pat in patterns:
        m = re.search(pat, url_or_handle)
        if m:
            return m.group(1)
    # Maybe bare channel ID
    if re.match(r"^UC[\w-]{22}$", url_or_handle.strip()):
        return url_or_handle.strip()
    return None


def resolve_handle_to_channel_id(handle: str, api_key: str) -> Optional[str]:
    """Resolve @handle or custom URL to UCxxx channel ID."""
    url = f"{_API_BASE}/search"
    params = {
        "part": "snippet",
        "q": handle,
        "type": "channel",
        "maxResults": 1,
        "key": api_key,
    }
    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        items = resp.json().get("items", [])
        if items:
            return items[0]["snippet"]["channelId"]
    except Exception as e:
        logger.warning(f"Handle resolution failed: {e}")
    return None


def fetch_channel_stats(channel_id_or_handle: str) -> Optional[dict]:
    """
    Fetch channel statistics from YouTube API.
    Returns None if no API key or request fails.
    """
    api_key = _get_api_key()
    if not api_key:
        logger.warning("No YOUTUBE_API_KEY set — returning None.")
        return None

    channel_id = channel_id_or_handle
    if not re.match(r"^UC[\w-]{22}$", channel_id_or_handle):
        channel_id = resolve_handle_to_channel_id(channel_id_or_handle, api_key)
        if not channel_id:
            return None

    url = f"{_API_BASE}/channels"
    params = {
        "part": "snippet,statistics,contentDetails",
        "id": channel_id,
        "key": api_key,
    }
    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        items = resp.json().get("items", [])
        if not items:
            return None
        item = items[0]
        stats = item.get("statistics", {})
        snippet = item.get("snippet", {})

        subscriber_count = int(stats.get("subscriberCount", 0))
        view_count = int(stats.get("viewCount", 0))
        video_count = int(stats.get("videoCount", 1))
        avg_views = view_count // max(video_count, 1)

        # Channel age
        published = snippet.get("publishedAt", "")
        if published:
            from datetime import datetime, timezone
            pub_dt = datetime.fromisoformat(published.replace("Z", "+00:00"))
            age_days = (datetime.now(timezone.utc) - pub_dt).days
        else:
            age_days = 365

        # Upload frequency — estimate from video count and age
        upload_freq = (video_count / max(age_days, 1)) * 30  # per month

        # Engagement proxy (we can't get likes without extra call easily)
        engagement_rate = 0.04  # default fallback

        estimated_monthly_revenue = (avg_views * upload_freq * 0.003)

        return {
            "channel_id": channel_id,
            "channel_name": snippet.get("title", "Unknown"),
            "niche": "unknown",
            "country": snippet.get("country", "US"),
            "subscriber_count": subscriber_count,
            "view_count": view_count,
            "video_count": video_count,
            "avg_views_per_video": avg_views,
            "engagement_rate": engagement_rate,
            "upload_frequency": round(upload_freq, 2),
            "channel_age_days": age_days,
            "estimated_monthly_revenue": round(estimated_monthly_revenue, 2),
        }
    except Exception as e:
        logger.error(f"YouTube API error: {e}")
        return None
