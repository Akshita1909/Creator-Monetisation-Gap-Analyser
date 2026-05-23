"""Shared helpers for formatting, tiers, and display."""
from __future__ import annotations
import math


def fmt_number(n: float | int, decimals: int = 1) -> str:
    """Format large numbers as 12.3K, 4.5M, etc."""
    if n >= 1_000_000:
        return f"{n/1_000_000:.{decimals}f}M"
    if n >= 1_000:
        return f"{n/1_000:.{decimals}f}K"
    return str(int(n))


def fmt_currency(n: float) -> str:
    """Format as $1,234."""
    if n >= 1_000_000:
        return f"${n/1_000_000:.2f}M"
    if n >= 1_000:
        return f"${n/1_000:.1f}K"
    return f"${n:.0f}"


def subscriber_tier(subs: int) -> str:
    if subs < 50_000:
        return "Micro (10K–50K)"
    if subs < 500_000:
        return "Mid (50K–500K)"
    return "Large (500K+)"


def engagement_label(rate: float) -> str:
    if rate >= 0.06:
        return "🔥 Viral"
    if rate >= 0.04:
        return "⚡ High"
    if rate >= 0.02:
        return "📊 Average"
    return "❄️ Low"


def clamp(val: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, val))


NICHE_COLORS = {
    "finance":   "#00d4aa",
    "fitness":   "#ff6b6b",
    "comedy":    "#ffd93d",
    "education": "#6bcb77",
    "tech":      "#4d96ff",
    "unknown":   "#aaaaaa",
}
