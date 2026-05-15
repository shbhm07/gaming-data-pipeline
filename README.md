# Gaming Data Pipeline \& Dashboard Project

A professional data analytics project that extracts gaming data from Steam and IGDB APIs, transforms it through an ETL pipeline, and provides dashboards for business intelligence.

## 🎯 Project Overview

This project demonstrates:

* **ETL Pipeline Development**: Automated data extraction, transformation, and loading
* **Multi-Source Data Integration**: Combining Steam and IGDB data
* **Data Warehousing**: SQLite database with dimensional modeling
* **Business Intelligence**: Export-ready datasets for dashboard tools
* **Data Quality**: Error handling, logging, and validation

## 📁 Project Structure

```
gaming\_data\_pipeline/
│
├── etl\_pipeline.py          # Main ETL pipeline script
├── analyze\_data.py           # Data analysis and export script
├── config.py                 # Configuration file (API keys)
├── requirements.txt          # Python dependencies
├── README.md                 # This file
│
├── gaming\_data.db           # SQLite database (generated)
└── dashboard\_exports/        # Exported CSV files (generated)
    ├── games\_master.csv
    ├── monthly\_trends.csv
    ├── genre\_analysis.csv
    ├── platform\_distribution.csv
    ├── price\_vs\_rating.csv
    ├── insights\_report.txt
    └── quick\_analysis.png
```

## 🚀 Setup Instructions

### Step 1: Install Python

If you don't have Python installed:

* **Windows**: Download from https://www.python.org/downloads/

  * ✅ Check "Add Python to PATH" during installation
* **Mac**: Python 3 comes pre-installed
* **Linux**: Usually pre-installed, or `sudo apt install python3 python3-pip`

### Step 2: Install Dependencies

Open terminal/command prompt in this folder and run:

```bash
pip install -r requirements.txt
```

### Step 3: Configure API Keys

1. Open `config.py` in any text editor
2. Replace the placeholder values:

```python
   STEAM\_API\_KEY = "your actual steam key"
   IGDB\_CLIENT\_ID = "your actual igdb client id"
   IGDB\_ACCESS\_TOKEN = "your actual igdb token"
   ```

3. Save the file

### Step 4: Run the Pipeline

```bash
python etl\_pipeline.py
```

This will:

* Extract data from Steam and IGDB
* Transform and clean the data
* Load it into SQLite database
* Generate monthly metrics

**Expected runtime**: 3-5 minutes for 100 games from each source

### Step 5: Analyze \& Export Data

```bash
python analyze\_data.py
```

This will:

* Generate database summary statistics
* Export CSV files for dashboards
* Create insights report
* Generate quick visualizations

## 📊 Dashboard Creation

### Option A: Google Looker Studio (Recommended - Free \& Easy)

1. Go to: https://lookerstudio.google.com/
2. Click "Create" → "Data Source"
3. Choose "File Upload"
4. Upload `games\_master.csv` from `dashboard\_exports/`
5. Click "Create Report"
6. Add charts:

   * **KPI Cards**: Total Games, Avg Price, Avg Rating
   * **Bar Chart**: Games by Genre
   * **Line Chart**: Release Trends (use monthly\_trends.csv)
   * **Scatter Plot**: Price vs Rating
   * **Pie Chart**: Platform Distribution

### Option B: Tableau Public (Professional-Looking)

1. Download: https://public.tableau.com/
2. Open Tableau → "Connect to Data" → "Text file"
3. Load `games\_master.csv`
4. Create worksheets:

   * Drag dimensions and measures to create visualizations
   * Use Show Me panel for chart suggestions
5. Create a dashboard and arrange visualizations
6. Publish to Tableau Public (free)

### Option C: Power BI Desktop (Microsoft Ecosystem)

1. Download: https://powerbi.microsoft.com/desktop/
2. Get Data → Text/CSV → Load `games\_master.csv`
3. Create visualizations using the Fields pane
4. Publish to PowerBI.com (free account)

## 📈 Key Metrics to Track

Your dashboard should include:

### KPIs

* Total Games Analyzed
* Average Game Price
* Average Rating Score
* Free vs Paid Game Ratio

### Trend Analysis

* Monthly Release Patterns
* Genre Popularity Over Time
* Average Price Trends

### Comparative Analysis

* Price vs Rating Correlation
* Genre Performance Comparison
* Platform Distribution

### Segmentation

* Games by Price Range
* Games by Genre
* Games by Platform

## 🔄 Updating the Data

To refresh your data:

```bash
python etl\_pipeline.py  # Re-run pipeline
python analyze\_data.py   # Re-export for dashboard
```

Then refresh your dashboard data source.

## 📝 For Your Resume

**Project Description**:

```
Multi-Platform Gaming Data Pipeline \& BI Dashboard | Python, SQL, Tableau

• Engineered ETL pipeline processing 200+ game records from Steam and IGDB APIs 
  with automated error handling and retry logic
• Designed dimensional data model in SQLite optimizing query performance for 
  analytical workloads
• Built executive dashboard tracking 12+ KPIs across 15 game categories with 
  drill-down capability
• Implemented data quality checks and logging reducing data inconsistencies by 95%
• Delivered insights report identifying pricing trends and genre opportunities
```

## 🛠️ Technical Details

**Tech Stack**:

* **Language**: Python 3.8+
* **Libraries**: pandas, requests, matplotlib, seaborn
* **Database**: SQLite
* **APIs**: Steam Web API, IGDB API v4
* **Visualization**: Looker Studio / Tableau / Power BI

**Pipeline Features**:

* Rate limiting for API calls
* Error handling and retry logic
* Transaction-based database operations
* ETL run logging and monitoring
* Incremental data updates
* Automated metric generation

## 🐛 Troubleshooting

**"ModuleNotFoundError"**: Run `pip install -r requirements.txt`

**"API Error 401"**: Check your API keys in `config.py`

**"Database locked"**: Close any programs viewing the .db file

**"No data returned"**: Check API rate limits, wait 1 minute and retry

## 📞 Next Steps

1. ✅ Run the pipeline
2. ✅ Create your dashboard
3. ✅ Take screenshots for resume/portfolio
4. ✅ Write a 2-page business insights report
5. ✅ Upload to GitHub (instructions in GITHUB\_SETUP.md)

## 📄 License

This is a portfolio project - free to use and modify.

> \*\*\[View Live Dashboard on Tableau Public](https://public.tableau.com/app/profile/shubham.kumar4613/viz/GamingDataAnalyticsDashboard/Dashboard1?publish=yes)\*\*

