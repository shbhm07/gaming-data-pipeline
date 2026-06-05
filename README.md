# Gaming Data Analytics Pipeline

An end-to-end data analytics project built on the video game industry.
Covers API data extraction, ETL pipeline development, SQLite database design,
K-Means market segmentation, and Tableau business intelligence.

**Live Dashboard**: [View on Tableau Public](https://public.tableau.com/app/profile/shubham.kumar4613/viz/GamingDataAnalyticsDashboard/Dashboard1?publish=yes)

**Author**: Shubham Kumar | Senior Data Analyst
[LinkedIn](https://linkedin.com/in/shbhm07) · [GitHub](https://github.com/shbhm07)

---

## Project Overview

This project demonstrates a complete data analytics workflow applied to
the video game industry - from raw API extraction to machine learning
segmentation and business intelligence reporting.

**Data Sources:**
- Steam Store API + SteamSpy API (100 games with pricing and review data)
- IGDB API (100 games with ratings, genres, and platform metadata)

**Key Findings:**
- 57% of analyzed titles fall in the Community Favorites segment, driven
  by quality at accessible price points rather than production budget
- Monetization-heavy titles consistently underperform quality-driven titles
  regardless of franchise size or brand recognition
- Action and Shooter genres account for 59% of all titles in the dataset
- PC platform represents 85%+ of platform coverage

---

## Technical Architecture

```
Steam API  ──┐
             ├──► ETL Pipeline (Python) ──► SQLite Database ──► CSV Exports ──► Tableau Dashboard
IGDB API   ──┘                                    │
                                                  └──► K-Means Segmentation ──► Market Analysis
```

**Pipeline Stages:**
1. Extract - API calls with rate limiting, error handling, and retry logic
2. Transform - Data cleaning, genre normalization, derived field generation
3. Load - SQLite database with dimensional schema
4. Analyze - K-Means clustering for market segmentation
5. Visualize - Interactive Tableau dashboard with 4 analytical views

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.13 |
| Data Processing | pandas |
| Machine Learning | scikit-learn |
| Database | SQLite |
| API Integration | requests |
| Visualization | Tableau Public |
| Version Control | Git / GitHub |

---

## Project Structure

```
gaming-data-pipeline/
│
├── etl_pipeline.py          # Main ETL pipeline (Steam + IGDB extraction)
├── analyze_data.py          # Data analysis and CSV export
├── fix_genres.py            # Genre normalization and standardization
├── segmentation.py          # K-Means market segmentation model
├── config_sample.py         # Configuration template (copy to config.py)
├── requirements.txt         # Python dependencies
│
├── cluster_scatter.png      # Segmentation scatter plots
├── cluster_characteristics.png  # Segment feature comparison
├── segment_distribution.png # Games per segment chart
└── elbow_curve.png          # K selection elbow curve
```

---

## Part 1: ETL Pipeline & Dashboard

### Setup

**Step 1: Install dependencies**
```bash
pip install -r requirements.txt
```

**Step 2: Configure API keys**
```bash
cp config_sample.py config.py
```
Edit config.py and add your API keys:
- Steam API Key: https://steamcommunity.com/dev/apikey
- IGDB Credentials: https://api-docs.igdb.com/#account-creation

**Step 3: Run the pipeline**
```bash
python etl_pipeline.py
```
Expected runtime: 20-25 minutes for 200 games (API rate limits apply)

**Step 4: Export dashboard files**
```bash
python analyze_data.py
```

### Dashboard

Built in Tableau Public tracking 4 KPIs across 200 game titles:

| KPI | Value |
|-----|-------|
| Total Games Analyzed | 200 |
| Average Price | $8.61 |
| Free-to-Play Ratio | 67% |
| Average IGDB Rating | 86.8 |

Charts include: Games by Genre, Average Rating by Genre,
Price Distribution, and Platform Distribution.

**View live**: [Gaming Data Analytics Dashboard](https://public.tableau.com/app/profile/shubham.kumar4613/viz/GamingDataAnalyticsDashboard/Dashboard1?publish=yes)

---

## Part 2: Market Segmentation

K-Means clustering analysis identifying 4 distinct market segments
across 100 Steam titles based on pricing, review volume, and sentiment.

### Methodology

**Features used:**
- price_usd - Current Steam pricing
- positive_reviews - Total positive review count
- negative_reviews - Total negative review count
- review_score - Derived sentiment ratio (positive / total reviews)

All features normalized using MinMaxScaler (0-1 range) before clustering.
Optimal K=4 determined via Elbow Method.

**Data note:** Price reflects current Steam pricing, not original launch
price. Legacy titles may show lower prices due to post-launch adjustments.

### Segments Identified

| Segment | Games | Avg Review Score | Avg Price Score |
|---------|-------|-----------------|-----------------|
| Community Favorites | 57 (57%) | 0.880 | 0.169 |
| Premium Releases | 20 (20%) | 0.744 | 0.707 |
| Underperformers | 20 (20%) | 0.407 | 0.014 |
| Evergreen Blockbusters | 3 (3%) | 0.590 | N/A* |

*Price excluded as defining factor for Evergreen Blockbusters due to
legacy pricing adjustments on titles like GTA V Legacy and TF2.

### Key Finding

Community Favorites is the dominant segment at 57% of the catalog.
Quality at accessible price points consistently outperforms both
premium and monetization-heavy titles regardless of franchise size.
Titles like Palworld, Left 4 Dead 2, and Hollow Knight demonstrate
that loyal communities are built through player value, not budget.

### Run the Segmentation

```bash
python segmentation.py
```

---

## Resume Description

```
Gaming Data Analytics Pipeline | Python, SQL, scikit-learn, Tableau, Git
github.com/shbhm07/gaming-data-pipeline

- Engineered automated ETL pipeline extracting 200+ game records from
  Steam and IGDB APIs with rate limiting and error handling

- Designed SQLite database schema and built genre normalization system
  standardizing 50+ raw API genre combinations into 13 clean categories

- Built K-Means clustering model segmenting 100 Steam titles into 4
  market segments using pricing, review volume, and sentiment features

- Delivered Tableau dashboard tracking 4 KPIs across pricing trends,
  genre performance, and platform distribution across 200 titles

- Key finding: 57% of titles succeed through community value over
  production budget, regardless of franchise size
```

---

## Troubleshooting

**ModuleNotFoundError**: Run `pip install -r requirements.txt.`

**API Error 401**: Check your API keys in config.py

**Database locked**: Close any programs viewing the .db file

**No data returned**: Check API rate limits, wait 1 minute, and retry

---

*Data sourced from Steam Store API, SteamSpy API, and IGDB API.
Built as a portfolio demonstration project.*
