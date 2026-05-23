# 🎬 CreatorLens — Monetisation Gap Analyser

> Discover why creators with millions of subscribers earn less than smaller creators, and find the real predictors of YouTube revenue.

---

## Features

| Module | Description |
|--------|-------------|
| **Overview Dashboard** | KPI cards, scatter plot, feature importance, efficiency scatter |
| **Channel Analyser** | Input any channel URL or stats → get gap score + recommendations |
| **Cohort Analysis** | Revenue by tier, niche×engagement heatmap, top-20 efficient channels |

## Quickstart

```bash
# 1. Clone / unzip
cd creatorlens

# 2. Create virtual env
python -m venv .venv && source .venv/bin/activate

# 3. Install deps
pip install -r requirements.txt

# 4. (Optional) Set API key
cp .env.example .env
# edit .env and add your YOUTUBE_API_KEY

# 5. Run
streamlit run app.py
```

App runs at `http://localhost:8501` — works fully on the 500-row seed dataset with no API key.

## Deploy to Streamlit Cloud

1. Push this repo to GitHub
2. Visit [share.streamlit.io](https://share.streamlit.io) → New App
3. Set `YOUTUBE_API_KEY` as a secret in App Settings (optional)
4. Deploy — Streamlit Cloud auto-installs `requirements.txt`

## Project Structure

```
creatorlens/
├── app.py                  # Main Streamlit app (3 pages)
├── data/
│   ├── collector.py        # Data loading + SQLite cache
│   ├── seed_data.csv       # 500 realistic channel rows
│   └── cache.db            # SQLite (auto-generated)
├── analysis/
│   ├── engine.py           # Regression, feature importance, cohorts
│   ├── gap.py              # Gap score calculator + recommendations
│   └── visualizations.py  # All Plotly charts
├── utils/
│   ├── youtube_api.py      # YouTube Data API v3 wrapper
│   └── helpers.py          # Formatters, tier labels, colours
├── requirements.txt
├── .env.example
└── README.md
```

## How the Gap Score Works

```
Gap Score (0–100) = weighted combination of:
  Engagement Gap      (30%) — vs niche ideal
  Views/Sub Gap       (25%) — view-through rate vs subs
  Upload Frequency    (20%) — consistency vs niche ideal
  Niche CPM Gap       (15%) — your niche vs highest-CPM niche
  Channel Age Gap     (10%) — newer channels penalised
```

Score < 20 = 🏆 Excellent · 20–40 = ✅ Good · 40–60 = ⚠️ Improve · 60–80 = 🚨 Significant · 80+ = 💀 Critical

## Revenue Estimation Model

```
estimated_monthly_revenue =
  avg_views_per_video × uploads_per_month × CPM × (1 - YouTube_cut)
where CPM is niche + country adjusted, YouTube_cut = 0.45
```

## Tech Stack

- **Frontend**: Streamlit + custom CSS (dark YouTube aesthetic)
- **Backend**: Python, pandas, scikit-learn (Ridge + Gradient Boosting)
- **Storage**: SQLite via `sqlite3`
- **Charts**: Plotly Express + Plotly Graph Objects
- **API**: YouTube Data API v3 (optional)
