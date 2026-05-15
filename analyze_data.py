"""
Data Analysis & Export Script
Generates CSV exports and analysis ready for dashboard visualization
"""

import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os

class DataAnalyzer:
    """Analyzes pipeline data and exports for dashboards"""
    
    def __init__(self, db_path: str = "gaming_data.db"):
        self.db_path = db_path
        self.export_dir = "dashboard_exports"
        os.makedirs(self.export_dir, exist_ok=True)
        
    def get_database_summary(self):
        """Print summary statistics of the database"""
        conn = sqlite3.connect(self.db_path)
        
        print("\n" + "="*60)
        print("📊 DATABASE SUMMARY")
        print("="*60)
        
        # Total games
        total_games = pd.read_sql("SELECT COUNT(*) as count FROM games", conn)['count'][0]
        print(f"\n📦 Total Games: {total_games}")
        
        # Games by source
        by_source = pd.read_sql("""
            SELECT data_source, COUNT(*) as count 
            FROM games 
            GROUP BY data_source
        """, conn)
        print("\n📍 Games by Source:")
        print(by_source.to_string(index=False))
        
        # Price statistics
        price_stats = pd.read_sql("""
            SELECT 
                ROUND(AVG(price_usd), 2) as avg_price,
                ROUND(MIN(price_usd), 2) as min_price,
                ROUND(MAX(price_usd), 2) as max_price,
                COUNT(CASE WHEN price_usd = 0 THEN 1 END) as free_games
            FROM games
        """, conn)
        print("\n💰 Price Statistics:")
        print(price_stats.to_string(index=False))
        
        # Top genres
        top_genres = pd.read_sql("""
            SELECT genres, COUNT(*) as count
            FROM games
            WHERE genres IS NOT NULL AND genres != ''
            GROUP BY genres
            ORDER BY count DESC
            LIMIT 10
        """, conn)
        print("\n🎮 Top 10 Genres:")
        print(top_genres.to_string(index=False))
        
        # Recent ETL runs
        recent_runs = pd.read_sql("""
            SELECT run_date, source, records_loaded, status
            FROM etl_log
            ORDER BY run_date DESC
            LIMIT 5
        """, conn)
        print("\n📝 Recent ETL Runs:")
        print(recent_runs.to_string(index=False))
        
        conn.close()
        print("\n" + "="*60)
    
    def export_for_dashboard(self):
        """Export clean datasets for dashboard tools"""
        print("\n📤 Exporting data for dashboard...")
        conn = sqlite3.connect(self.db_path)
        
        # 1. Main games dataset
        games_df = pd.read_sql("""
            SELECT 
                game_id,
                name,
                release_date,
                developer,
                publisher,
                price_usd,
                genres,
                platforms,
                metacritic_score,
                igdb_rating,
                data_source
            FROM games
            WHERE name IS NOT NULL
        """, conn)
        
        export_path = os.path.join(self.export_dir, "games_master.csv")
        games_df.to_csv(export_path, index=False)
        print(f"  ✓ Exported: {export_path} ({len(games_df)} records)")
        
        # 2. Monthly trends
        monthly_df = pd.read_sql("""
            SELECT 
                year,
                month,
                total_releases,
                avg_price,
                avg_metacritic
            FROM monthly_metrics
            ORDER BY year, month
        """, conn)
        
        export_path = os.path.join(self.export_dir, "monthly_trends.csv")
        monthly_df.to_csv(export_path, index=False)
        print(f"  ✓ Exported: {export_path} ({len(monthly_df)} records)")
        
        # 3. Genre analysis
        genre_analysis = pd.read_sql("""
            SELECT 
                genres,
                COUNT(*) as game_count,
                ROUND(AVG(price_usd), 2) as avg_price,
                ROUND(AVG(metacritic_score), 2) as avg_rating
            FROM games
            WHERE genres IS NOT NULL AND genres != ''
            GROUP BY genres
            HAVING game_count > 2
            ORDER BY game_count DESC
        """, conn)
        
        export_path = os.path.join(self.export_dir, "genre_analysis.csv")
        genre_analysis.to_csv(export_path, index=False)
        print(f"  ✓ Exported: {export_path} ({len(genre_analysis)} records)")
        
        # 4. Platform distribution
        platform_dist = pd.read_sql("""
            SELECT 
                platforms,
                COUNT(*) as game_count,
                ROUND(AVG(price_usd), 2) as avg_price
            FROM games
            WHERE platforms IS NOT NULL AND platforms != ''
            GROUP BY platforms
            ORDER BY game_count DESC
            LIMIT 20
        """, conn)
        
        export_path = os.path.join(self.export_dir, "platform_distribution.csv")
        platform_dist.to_csv(export_path, index=False)
        print(f"  ✓ Exported: {export_path} ({len(platform_dist)} records)")
        
        # 5. Price vs Rating analysis
        price_rating = pd.read_sql("""
            SELECT 
                CASE 
                    WHEN price_usd = 0 THEN 'Free'
                    WHEN price_usd < 10 THEN '$0-10'
                    WHEN price_usd < 20 THEN '$10-20'
                    WHEN price_usd < 40 THEN '$20-40'
                    ELSE '$40+'
                END as price_range,
                COUNT(*) as game_count,
                ROUND(AVG(metacritic_score), 2) as avg_metacritic,
                ROUND(AVG(igdb_rating), 2) as avg_igdb_rating
            FROM games
            WHERE price_usd IS NOT NULL
            GROUP BY price_range
        """, conn)
        
        export_path = os.path.join(self.export_dir, "price_vs_rating.csv")
        price_rating.to_csv(export_path, index=False)
        print(f"  ✓ Exported: {export_path} ({len(price_rating)} records)")
        
        conn.close()
        print(f"\n✅ All exports complete! Files saved in: {self.export_dir}/")
    
    def generate_insights_report(self):
        """Generate a text report with key insights"""
        print("\n📄 Generating insights report...")
        conn = sqlite3.connect(self.db_path)
        
        report = []
        report.append("="*70)
        report.append("GAMING DATA PIPELINE - INSIGHTS REPORT")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("="*70)
        
        # Total games
        total = pd.read_sql("SELECT COUNT(*) as count FROM games", conn)['count'][0]
        report.append(f"\n📦 TOTAL GAMES ANALYZED: {total}")
        
        # Most expensive game
        most_expensive = pd.read_sql("""
            SELECT name, price_usd FROM games 
            WHERE price_usd > 0 
            ORDER BY price_usd DESC LIMIT 1
        """, conn)
        if not most_expensive.empty:
            report.append(f"\n💎 MOST EXPENSIVE: {most_expensive['name'][0]} (${most_expensive['price_usd'][0]})")
        
        # Highest rated
        highest_rated = pd.read_sql("""
            SELECT name, metacritic_score FROM games 
            WHERE metacritic_score IS NOT NULL 
            ORDER BY metacritic_score DESC LIMIT 1
        """, conn)
        if not highest_rated.empty:
            report.append(f"⭐ HIGHEST METACRITIC: {highest_rated['name'][0]} ({highest_rated['metacritic_score'][0]}/100)")
        
        # Most common genre
        top_genre = pd.read_sql("""
            SELECT genres, COUNT(*) as count FROM games 
            WHERE genres IS NOT NULL AND genres != ''
            GROUP BY genres 
            ORDER BY count DESC LIMIT 1
        """, conn)
        if not top_genre.empty:
            report.append(f"🎮 MOST COMMON GENRE: {top_genre['genres'][0]} ({top_genre['count'][0]} games)")
        
        # Free vs Paid
        free_paid = pd.read_sql("""
            SELECT 
                CASE WHEN price_usd = 0 THEN 'Free' ELSE 'Paid' END as type,
                COUNT(*) as count
            FROM games
            GROUP BY type
        """, conn)
        report.append("\n💰 FREE VS PAID:")
        for _, row in free_paid.iterrows():
            report.append(f"   {row['type']}: {row['count']} games")
        
        # Platform breakdown
        report.append("\n🖥️ PLATFORM COVERAGE:")
        platforms = pd.read_sql("""
            SELECT 
                SUM(CASE WHEN platforms LIKE '%windows%' OR platforms LIKE '%Windows%' THEN 1 ELSE 0 END) as windows,
                SUM(CASE WHEN platforms LIKE '%mac%' OR platforms LIKE '%Mac%' THEN 1 ELSE 0 END) as mac,
                SUM(CASE WHEN platforms LIKE '%linux%' OR platforms LIKE '%Linux%' THEN 1 ELSE 0 END) as linux
            FROM games
        """, conn)
        report.append(f"   Windows: {platforms['windows'][0]} games")
        report.append(f"   Mac: {platforms['mac'][0]} games")
        report.append(f"   Linux: {platforms['linux'][0]} games")
        
        conn.close()
        
        report.append("\n" + "="*70)
        report_text = "\n".join(report)
        
        # Save to file
        report_path = os.path.join(self.export_dir, "insights_report.txt")
        with open(report_path, 'w') as f:
            f.write(report_text)
        
        print(report_text)
        print(f"\n✅ Report saved: {report_path}")
    
    def create_quick_visualizations(self):
        """Create simple matplotlib charts for quick analysis"""
        print("\n📊 Creating quick visualizations...")
        conn = sqlite3.connect(self.db_path)
        
        # Set style
        sns.set_style("whitegrid")
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Gaming Data Pipeline - Quick Analysis', fontsize=16, fontweight='bold')
        
        # 1. Games by Genre (Top 10)
        genre_data = pd.read_sql("""
            SELECT genres, COUNT(*) as count FROM games 
            WHERE genres IS NOT NULL AND genres != ''
            GROUP BY genres ORDER BY count DESC LIMIT 10
        """, conn)
        
        axes[0, 0].barh(genre_data['genres'], genre_data['count'], color='steelblue')
        axes[0, 0].set_xlabel('Number of Games')
        axes[0, 0].set_title('Top 10 Genres')
        axes[0, 0].invert_yaxis()
        
        # 2. Price Distribution
        price_data = pd.read_sql("""
            SELECT price_usd FROM games WHERE price_usd > 0 AND price_usd < 100
        """, conn)
        
        axes[0, 1].hist(price_data['price_usd'], bins=20, color='coral', edgecolor='black')
        axes[0, 1].set_xlabel('Price (USD)')
        axes[0, 1].set_ylabel('Number of Games')
        axes[0, 1].set_title('Price Distribution')
        
        # 3. Metacritic Score Distribution
        metacritic_data = pd.read_sql("""
            SELECT metacritic_score FROM games WHERE metacritic_score IS NOT NULL
        """, conn)
        
        axes[1, 0].hist(metacritic_data['metacritic_score'], bins=15, color='mediumseagreen', edgecolor='black')
        axes[1, 0].set_xlabel('Metacritic Score')
        axes[1, 0].set_ylabel('Number of Games')
        axes[1, 0].set_title('Metacritic Score Distribution')
        
        # 4. Data Source Distribution
        source_data = pd.read_sql("""
            SELECT data_source, COUNT(*) as count FROM games GROUP BY data_source
        """, conn)
        
        axes[1, 1].pie(source_data['count'], labels=source_data['data_source'], 
                      autopct='%1.1f%%', startangle=90, colors=['skyblue', 'lightcoral'])
        axes[1, 1].set_title('Games by Data Source')
        
        plt.tight_layout()
        
        # Save plot
        plot_path = os.path.join(self.export_dir, "quick_analysis.png")
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        print(f"  ✓ Saved visualization: {plot_path}")
        
        conn.close()
        plt.close()


def main():
    """Run complete analysis and export workflow"""
    analyzer = DataAnalyzer()
    
    # Check if database exists
    if not os.path.exists("gaming_data.db"):
        print("❌ Database not found! Please run etl_pipeline.py first.")
        return
    
    print("\n🚀 Starting data analysis and export process...\n")
    
    # Run all analysis steps
    analyzer.get_database_summary()
    analyzer.export_for_dashboard()
    analyzer.generate_insights_report()
    analyzer.create_quick_visualizations()
    
    print("\n" + "="*60)
    print("✅ ANALYSIS COMPLETE!")
    print("="*60)
    print(f"\n📁 All files saved in: {analyzer.export_dir}/")
    print("\n📊 Next steps:")
    print("  1. Use the CSV files to create dashboards in Looker Studio/Tableau")
    print("  2. Review insights_report.txt for key findings")
    print("  3. Share quick_analysis.png for overview visualizations")
    print("\n")


if __name__ == "__main__":
    main()
