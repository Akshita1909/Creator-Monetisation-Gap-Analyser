CreatorLens — Monetisation Gap Analyser
 Overview

CreatorLens is a production-grade data analytics platform that helps identify why some creators with millions of followers earn less than smaller creators.

The platform analyzes creator performance metrics across multiple niches and detects the real predictors of monetisation success using statistical analysis, machine learning, and business intelligence techniques.

Instead of assuming that subscriber count directly determines revenue, CreatorLens uncovers:

engagement-driven monetisation
niche-level revenue differences
upload consistency impact
audience efficiency patterns
monetisation outliers

The platform is designed as a portfolio-grade analytics product for:

creator economy research
influencer analytics
business intelligence
monetisation benchmarking
consulting-style analytics reporting
 Key Features
 Overview Dashboard
KPI cards for:
Average Revenue
Average Engagement
Top Performing Niche
Biggest Monetisation Gap
Interactive Plotly charts
Subscriber vs Revenue scatter analysis
Feature importance visualization
Transparent dark-theme analytics UI
 Channel Analyser

Paste any YouTube channel URL to:

Fetch live channel data
Compare against similar creators
Calculate Monetisation Gap Score
Identify weak monetisation areas
Generate data-driven improvement recommendations
 Cohort Analysis

Analyze creators by subscriber tiers:

10k–50k
50k–500k
500k+

Features:

Revenue trend analysis
Engagement heatmaps
Monetisation efficiency rankings
Outlier detection
Machine Learning Analysis Engine

The analytics engine performs:

Linear Regression
Feature Importance Ranking
Outlier Detection
Cohort Benchmarking
Monetisation Efficiency Scoring
⚡ SQLite Data Caching

To avoid API quota exhaustion:

YouTube API responses are cached locally
App works without API key using seed dataset
Faster dashboard performance
Tech Stack
Layer	Technology
Frontend	Streamlit
Styling	Custom CSS
Backend	Python
Data Processing	pandas
Machine Learning	scikit-learn
Database	SQLite
Charts	Plotly Express + Graph Objects
Deployment	Streamlit Cloud
APIs	YouTube Data API v3
📂 Folder Structure
creatorlens/
│
├── app.py
│
├── data/
│   ├── collector.py
│   ├── seed_data.csv
│   └── cache.db
│
├── analysis/
│   ├── engine.py
│   ├── gap.py
│   └── visualizations.py
│
├── utils/
│   ├── youtube_api.py
│   └── helpers.py
│
├── requirements.txt
├── README.md
└── .env.example
📥 Dataset Features

The system collects and analyzes:

Feature	Description
subscriber_count	Total channel subscribers
view_count	Total lifetime views
video_count	Total uploaded videos
avg_views_per_video	Average views per upload
engagement_rate	Likes + comments per view
upload_frequency	Videos uploaded per month
channel_age_days	Age of channel
niche	Creator category
country	Creator location
estimated_monthly_revenue	Monetisation proxy
Monetisation Formula

Estimated monthly revenue is calculated using:

Revenue=AvgViewsPerVideo×0.003

Where:

AvgViewsPerVideo = estimated monthly views
0.003 = estimated CPM monetisation factor
Monetisation Efficiency Score

The app calculates:

EfficiencyScore=
ExpectedRevenueForSubscriberCount
ActualRevenue
	​


This identifies creators who:

outperform their audience size
monetize efficiently
underperform despite large audiences
Revenue Prediction Model

The ML engine uses:

Linear Regression
Feature normalization
Correlation analysis

To identify:

strongest revenue predictors
engagement impact
niche effects
upload frequency contribution
Outlier Detection

The platform flags creators earning:

ActualRevenue>3×ExpectedRevenue

These are considered:

monetisation outliers
highly efficient creators
benchmark-worthy channels
UI Design

The interface includes:

YouTube-inspired dark theme
Transparent Plotly charts
Responsive sidebar navigation
Interactive filters
Loading spinners
KPI metric cards

<img width="1800" height="1000" alt="01_scatter" src="https://github.com/user-attachments/assets/dc132521-4f05-4832-a4f4-a27d19899abb" />
<img width="1400" height="800" alt="02_feature_importance" src="https://github.com/user-attachments/assets/23a8497f-67d3-4928-8789-453e310fc2aa" />
<img width="1400" height="800" alt="03_cohort_line" src="https://github.com/user-attachments/assets/dbfb4687-f1ca-4ad7-a4bc-53f21009d05f" />
<img width="1800" height="900" alt="04_heatmap" src="https://github.com/user-attachments/assets/b7579295-fb26-4740-bd38-ec0b6b3a06e5" />
<img width="1800" height="900" alt="05_efficiency" src="https://github.com/user-attachments/assets/e8a2773d-d245-403b-ad86-989d7788f6a3" />
<img width="1000" height="800" alt="06_radar_gap" src="https://github.com/user-attachments/assets/599f72db-871e-421a-9385-c1033eb4668a" />






