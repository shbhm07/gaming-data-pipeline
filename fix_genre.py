"""
Genre Fix Script
Splits combined genre strings like "Shooter, Adventure, RPG" into
individual genre records, making charts cleaner and more meaningful
"""

import sqlite3
import pandas as pd

def fix_genres():
    db_path = "gaming_data.db"
    conn = sqlite3.connect(db_path)

    print("="*60)
    print("GENRE FIX SCRIPT")
    print("="*60)

    # Step 1: Show current state
    print("\n📊 BEFORE - Current genre combinations:")
    before = pd.read_sql("""
        SELECT genres, COUNT(*) as count
        FROM games
        WHERE genres IS NOT NULL AND genres != ''
        GROUP BY genres
        ORDER BY count DESC
        LIMIT 15
    """, conn)
    print(before.to_string(index=False))

    # Step 2: Load all games
    games = pd.read_sql("SELECT * FROM games", conn)
    print(f"\n📦 Total games loaded: {len(games)}")

    # Step 3: Split genres and explode into individual rows
    # We'll add a new column 'primary_genre' with the first/main genre
    # and a column 'all_genres' as a cleaned version

    def get_primary_genre(genre_string):
        """Get the first/primary genre from a combined string"""
        if not genre_string or pd.isna(genre_string):
            return "Unknown"
        # Split by comma and take first genre, strip whitespace
        genres = [g.strip() for g in str(genre_string).split(',')]
        return genres[0] if genres else "Unknown"

    def clean_genre(genre_string):
        """Clean and standardize genre names"""
        if not genre_string or pd.isna(genre_string):
            return "Unknown"

        # Genre mapping - standardize similar genres
        genre_map = {
            'Role-playing (RPG)': 'RPG',
            'Hack and slash/Beat \'em up': 'Action',
            'Hack and slash': 'Action',
            'Beat \'em up': 'Action',
            'Point-and-click': 'Adventure',
            'Card & Board Game': 'Strategy',
            'Turn-based strategy (TBS)': 'Strategy',
            'Real Time Strategy (RTS)': 'Strategy',
            'Tactical': 'Strategy',
            'Pinball': 'Arcade',
            'Quiz/Trivia': 'Casual',
            'Moba': 'Strategy',
            'Music': 'Casual',
            'Fighting': 'Action',
            'Visual Novel': 'Adventure',
        }

        genres = [g.strip() for g in str(genre_string).split(',')]
        cleaned = []
        for g in genres:
            cleaned.append(genre_map.get(g, g))

        return ', '.join(cleaned)

    # Apply fixes
    games['primary_genre'] = games['genres'].apply(get_primary_genre)
    games['primary_genre'] = games['primary_genre'].apply(
        lambda x: {
            'Role-playing (RPG)': 'RPG',
            'Hack and slash/Beat \'em up': 'Action',
            'Hack and slash': 'Action',
            'Point-and-click': 'Adventure',
            'Card & Board Game': 'Strategy',
            'Turn-based strategy (TBS)': 'Strategy',
            'Real Time Strategy (RTS)': 'Strategy',
            'Tactical': 'Strategy',
            'Pinball': 'Arcade',
            'Quiz/Trivia': 'Casual',
            'Moba': 'Strategy',
            'Music': 'Casual',
            'Fighting': 'Action',
            'Visual Novel': 'Adventure',
        }.get(x, x)
    )

    games['genres_cleaned'] = games['genres'].apply(clean_genre)

    print(f"\n✅ Primary genres assigned to all games")

    # Step 4: Update database - add new columns if they don't exist
    cursor = conn.cursor()

    try:
        cursor.execute("ALTER TABLE games ADD COLUMN primary_genre TEXT")
        print("✓ Added primary_genre column")
    except:
        print("✓ primary_genre column already exists")

    try:
        cursor.execute("ALTER TABLE games ADD COLUMN genres_cleaned TEXT")
        print("✓ Added genres_cleaned column")
    except:
        print("✓ genres_cleaned column already exists")

    conn.commit()

    # Step 5: Update each game record
    print("\n🔄 Updating genre data for each game...")
    updated = 0
    for _, row in games.iterrows():
        cursor.execute("""
            UPDATE games
            SET primary_genre = ?, genres_cleaned = ?
            WHERE game_id = ? AND data_source = ?
        """, (row['primary_genre'], row['genres_cleaned'],
              row['game_id'], row['data_source']))
        updated += 1

    conn.commit()
    print(f"✓ Updated {updated} game records")

    # Step 6: Show after state
    print("\n📊 AFTER - Clean primary genres:")
    after = pd.read_sql("""
        SELECT primary_genre, COUNT(*) as game_count,
               ROUND(AVG(price_usd), 2) as avg_price,
               ROUND(AVG(igdb_rating), 2) as avg_rating
        FROM games
        WHERE primary_genre IS NOT NULL
          AND primary_genre != 'Unknown'
        GROUP BY primary_genre
        ORDER BY game_count DESC
    """, conn)
    print(after.to_string(index=False))

    # Step 7: Export updated CSVs for dashboard
    print("\n📤 Exporting updated CSVs for dashboard...")

    import os
    os.makedirs("dashboard_exports", exist_ok=True)

    # Updated games master with primary genre
    games_master = pd.read_sql("""
        SELECT game_id, name, release_date, developer, publisher,
               price_usd, primary_genre as genre, platforms,
               metacritic_score, igdb_rating, data_source,
               release_year, release_month, is_free
        FROM games
        WHERE name IS NOT NULL
    """, conn)
    games_master.to_csv("dashboard_exports/games_master.csv", index=False)
    print(f"  ✓ games_master.csv updated ({len(games_master)} records)")

    # Genre analysis with clean single genres
    genre_analysis = pd.read_sql("""
        SELECT primary_genre as genre,
               COUNT(*) as game_count,
               ROUND(AVG(price_usd), 2) as avg_price,
               ROUND(AVG(igdb_rating), 2) as avg_rating,
               ROUND(AVG(metacritic_score), 2) as avg_metacritic
        FROM games
        WHERE primary_genre IS NOT NULL
          AND primary_genre != 'Unknown'
        GROUP BY primary_genre
        ORDER BY game_count DESC
    """, conn)
    genre_analysis.to_csv("dashboard_exports/genre_analysis.csv", index=False)
    print(f"  ✓ genre_analysis.csv updated ({len(genre_analysis)} genres)")

    # Rating by genre (for bar chart)
    rating_by_genre = pd.read_sql("""
        SELECT primary_genre as genre,
               COUNT(*) as game_count,
               ROUND(AVG(igdb_rating), 1) as avg_rating,
               ROUND(MAX(igdb_rating), 1) as max_rating,
               ROUND(MIN(igdb_rating), 1) as min_rating
        FROM games
        WHERE primary_genre IS NOT NULL
          AND primary_genre != 'Unknown'
          AND igdb_rating IS NOT NULL
          AND igdb_rating > 0
        GROUP BY primary_genre
        HAVING game_count >= 1
        ORDER BY avg_rating DESC
    """, conn)
    rating_by_genre.to_csv("dashboard_exports/rating_by_genre.csv", index=False)
    print(f"  ✓ rating_by_genre.csv created ({len(rating_by_genre)} genres)")

    # Price buckets for distribution chart
    price_buckets = pd.read_sql("""
        SELECT
            CASE
                WHEN price_usd = 0 THEN '1. Free'
                WHEN price_usd < 10 THEN '2. Under $10'
                WHEN price_usd < 20 THEN '3. $10 - $20'
                WHEN price_usd < 40 THEN '4. $20 - $40'
                WHEN price_usd < 60 THEN '5. $40 - $60'
                ELSE '6. $60+'
            END as price_range,
            COUNT(*) as game_count,
            ROUND(AVG(igdb_rating), 1) as avg_rating
        FROM games
        GROUP BY price_range
        ORDER BY price_range
    """, conn)
    price_buckets.to_csv("dashboard_exports/price_buckets.csv", index=False)
    print(f"  ✓ price_buckets.csv created ({len(price_buckets)} buckets)")

    # Platform breakdown
    platform_breakdown = pd.read_sql("""
        SELECT
            CASE
                WHEN platforms LIKE '%PC%' OR platforms LIKE '%windows%'
                     OR platforms LIKE '%Windows%' THEN 'PC'
                WHEN platforms LIKE '%PlayStation%' OR platforms LIKE '%PS%' THEN 'PlayStation'
                WHEN platforms LIKE '%Xbox%' THEN 'Xbox'
                WHEN platforms LIKE '%Nintendo%' OR platforms LIKE '%Switch%' THEN 'Nintendo'
                WHEN platforms LIKE '%iOS%' OR platforms LIKE '%Android%' THEN 'Mobile'
                ELSE 'Other'
            END as platform_group,
            COUNT(*) as game_count
        FROM games
        WHERE platforms IS NOT NULL AND platforms != ''
        GROUP BY platform_group
        ORDER BY game_count DESC
    """, conn)
    platform_breakdown.to_csv("dashboard_exports/platform_breakdown.csv", index=False)
    print(f"  ✓ platform_breakdown.csv created ({len(platform_breakdown)} platforms)")

    conn.close()

    print("\n" + "="*60)
    print("✅ GENRE FIX COMPLETE!")
    print("="*60)
    print("\n📊 New files available in dashboard_exports/:")
    print("  • games_master.csv       ← Updated with clean genres")
    print("  • genre_analysis.csv     ← Single genre breakdown")
    print("  • rating_by_genre.csv    ← Avg rating per genre")
    print("  • price_buckets.csv      ← Price range distribution")
    print("  • platform_breakdown.csv ← Platform groupings")
    print("\n🎯 Recommended dashboard charts:")
    print("  1. Bar chart: genre vs game_count (from genre_analysis.csv)")
    print("  2. Bar chart: genre vs avg_rating (from rating_by_genre.csv)")
    print("  3. Bar chart: price_range vs game_count (from price_buckets.csv)")
    print("  4. Pie chart: platform_group vs game_count (from platform_breakdown.csv)")
    print("\n💡 TIP: Re-upload these new CSV files to Looker Studio")
    print("        to replace your existing data sources!\n")


if __name__ == "__main__":
    fix_genres()