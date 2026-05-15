"""
Easy Project Runner
Run this to execute the complete pipeline and analysis
"""

import sys
import os

def check_config():
    """Check if API keys are configured"""
    try:
        import config
        
        if "YOUR_" in config.STEAM_API_KEY:
            print("❌ Please configure your API keys in config.py first!")
            print("   Open config.py and replace the placeholder values.")
            return False
        
        print("✅ Configuration looks good!")
        return True
    except ImportError:
        print("❌ config.py not found!")
        return False

def check_dependencies():
    """Check if required packages are installed"""
    required = ['requests', 'pandas', 'matplotlib', 'seaborn']
    missing = []
    
    for package in required:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"❌ Missing packages: {', '.join(missing)}")
        print("   Run: pip install -r requirements.txt")
        return False
    
    print("✅ All dependencies installed!")
    return True

def run_pipeline():
    """Run the ETL pipeline"""
    print("\n" + "="*60)
    print("STEP 1: Running ETL Pipeline")
    print("="*60)
    
    try:
        import etl_pipeline
        import config
        
        pipeline = etl_pipeline.GamingDataPipeline(
            config.STEAM_API_KEY,
            config.IGDB_CLIENT_ID,
            config.IGDB_ACCESS_TOKEN
        )
        
        pipeline.run_pipeline(
            steam_limit=config.STEAM_GAMES_LIMIT,
            igdb_limit=config.IGDB_GAMES_LIMIT
        )
        
        return True
    except Exception as e:
        print(f"❌ Pipeline failed: {str(e)}")
        return False

def run_analysis():
    """Run data analysis and export"""
    print("\n" + "="*60)
    print("STEP 2: Running Data Analysis & Export")
    print("="*60)
    
    try:
        import analyze_data
        analyze_data.main()
        return True
    except Exception as e:
        print(f"❌ Analysis failed: {str(e)}")
        return False

def main():
    """Main execution flow"""
    print("\n")
    print("╔════════════════════════════════════════════════════════╗")
    print("║   GAMING DATA PIPELINE - AUTOMATED RUNNER              ║")
    print("╚════════════════════════════════════════════════════════╝")
    print("\n")
    
    # Pre-flight checks
    print("🔍 Running pre-flight checks...\n")
    
    if not check_dependencies():
        sys.exit(1)
    
    if not check_config():
        sys.exit(1)
    
    print("\n✅ All checks passed! Starting pipeline...\n")
    input("Press ENTER to continue...")
    
    # Run pipeline
    if not run_pipeline():
        print("\n❌ Pipeline execution failed. Please check errors above.")
        sys.exit(1)
    
    # Run analysis
    if not run_analysis():
        print("\n❌ Analysis failed. Please check errors above.")
        sys.exit(1)
    
    # Success!
    print("\n" + "="*60)
    print("🎉 SUCCESS! Your project is complete!")
    print("="*60)
    print("\n📁 Generated files:")
    print("   ✓ gaming_data.db - Your SQLite database")
    print("   ✓ dashboard_exports/ - CSV files for dashboards")
    print("   ✓ dashboard_exports/insights_report.txt - Key findings")
    print("   ✓ dashboard_exports/quick_analysis.png - Visualizations")
    
    print("\n📊 Next steps:")
    print("   1. Open Looker Studio / Tableau / Power BI")
    print("   2. Import the CSV files from dashboard_exports/")
    print("   3. Create your dashboard visualizations")
    print("   4. Take screenshots for your portfolio")
    print("   5. Follow GITHUB_SETUP.md to upload to GitHub")
    
    print("\n💼 For your resume:")
    print("   Check README.md for the suggested project description")
    
    print("\n🎯 Project complete! You now have a professional")
    print("   data analytics portfolio piece.\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Process interrupted by user.")
        sys.exit(0)
