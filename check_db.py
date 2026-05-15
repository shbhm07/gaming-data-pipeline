import sqlite3
import pandas as pd

conn = sqlite3.connect('gaming_data.db')

print("=" * 40)
print("DATABASE SUMMARY")
print("=" * 40)

total = pd.read_sql("SELECT COUNT(*) as total FROM games", conn)
print(f"\nTotal Games: {total['total'][0]}")

by_source = pd.read_sql("SELECT data_source, COUNT(*) as count FROM games GROUP BY data_source", conn)
print(f"\nBy Source:")
print(by_source.to_string(index=False))

genres = pd.read_sql("""
    SELECT primary_genre, COUNT(*) as count
    FROM games
    WHERE primary_genre IS NOT NULL AND primary_genre != ''
    GROUP BY primary_genre
    ORDER BY count DESC
    LIMIT 10
""", conn)
print(f"\nTop Genres:")
print(genres.to_string(index=False))

price = pd.read_sql("""
    SELECT
        ROUND(AVG(price_usd), 2) as avg_price,
        SUM(CASE WHEN price_usd = 0 THEN 1 ELSE 0 END) as free_games,
        ROUND(AVG(igdb_rating), 1) as avg_rating
    FROM games
""", conn)
print(f"\nKey Metrics:")
print(price.to_string(index=False))

conn.close()