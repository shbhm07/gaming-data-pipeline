"""
Gaming Data ETL Pipeline - Improved Version
Uses SteamSpy API (free, no key needed) for Steam data
and IGDB for additional metadata
"""

import requests
import sqlite3
import time
from datetime import datetime
import pandas as pd
from typing import List, Dict
import os

class GamingDataPipeline:
    """Main ETL Pipeline for gaming data"""

    def __init__(self, steam_api_key: str, igdb_client_id: str, igdb_access_token: str):
        self.steam_api_key = steam_api_key
        self.igdb_client_id = igdb_client_id
        self.igdb_access_token = igdb_access_token
        self.db_path = "gaming_data.db"
        self.setup_database()

    def setup_database(self):
        """Create database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("DROP TABLE IF EXISTS games")
        cursor.execute("DROP TABLE IF EXISTS monthly_metrics")

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS games (
                game_id INTEGER,
                name TEXT NOT NULL,
                release_date TEXT,
                developer TEXT,
                publisher TEXT,
                price_usd REAL,
                genres TEXT,
                platforms TEXT,
                metacritic_score INTEGER,
                positive_reviews INTEGER,
                negative_reviews INTEGER,
                estimated_owners TEXT,
                average_playtime INTEGER,
                median_playtime INTEGER,
                tags TEXT,
                igdb_rating REAL,
                igdb_rating_count INTEGER,
                data_source TEXT,
                release_year INTEGER,
                release_month INTEGER,
                is_free BOOLEAN,
                primary_genre TEXT,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (game_id, data_source)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS monthly_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                year INTEGER,
                month INTEGER,
                total_releases INTEGER,
                avg_price REAL,
                avg_metacritic REAL,
                top_genre TEXT,
                snapshot_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS etl_log (
                run_id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                source TEXT,
                records_extracted INTEGER,
                records_loaded INTEGER,
                status TEXT,
                error_message TEXT
            )
        """)

        conn.commit()
        conn.close()
        print("✓ Database setup complete")

    def extract_steamspy_data(self, limit: int = 100) -> List[Dict]:
        """
        Extract data from SteamSpy API - free, no key needed
        Returns top games by player count with rich metadata
        """
        print(f"\n📥 Extracting Steam data via SteamSpy (limit: {limit})...")
        games_data = []

        # Genre mapping for standardization
        genre_map = {
            'Role-playing (RPG)': 'RPG',
            'Hack and slash/Beat \'em up': 'Action',
            'Hack and slash': 'Action',
            'Point-and-click': 'Adventure',
            'Card & Board Game': 'Strategy',
            'Turn-based strategy (TBS)': 'Strategy',
            'Real Time Strategy (RTS)': 'Strategy',
            'Tactical': 'Strategy',
            'Fighting': 'Action',
            'Visual Novel': 'Adventure',
            'Indie': 'Indie',
            'Massively Multiplayer': 'MMO',
        }

        try:
            # SteamSpy all page returns top 1000 games by owners
            # We paginate through pages to get enough games
            pages_needed = (limit // 1000) + 1
            all_games = {}

            for page in range(pages_needed):
                url = f"https://steamspy.com/api.php?request=all&page={page}"
                print(f"  Fetching SteamSpy page {page + 1}...")
                response = requests.get(url, timeout=30)

                if response.status_code == 200:
                    page_data = response.json()
                    all_games.update(page_data)
                    print(f"  ✓ Got {len(page_data)} games from page {page + 1}")
                else:
                    print(f"  ✗ Page {page + 1} failed: {response.status_code}")

                time.sleep(2)  # SteamSpy rate limit

            print(f"  Total available: {len(all_games)} games")

            # Sort by owners (most popular first) and take limit
            sorted_games = sorted(
                all_games.items(),
                key=lambda x: x[1].get('owners', '0').split(' .. ')[0].replace(',', '').strip() if x[1].get('owners') else '0',
                reverse=True
            )[:limit]

            for idx, (app_id, game) in enumerate(sorted_games):
                try:
                    # Get detailed info from Steam Store API
                    detail_url = f"https://store.steampowered.com/api/appdetails?appids={app_id}"
                    detail_response = requests.get(detail_url, timeout=10)

                    genres = ''
                    primary_genre = ''
                    metacritic = None
                    platforms = 'windows'
                    release_date = None

                    if detail_response.status_code == 200:
                        detail_data = detail_response.json()
                        if str(app_id) in detail_data and detail_data[str(app_id)]['success']:
                            app_data = detail_data[str(app_id)]['data']
                            genres_list = [g['description'] for g in app_data.get('genres', [])]
                            genres = ', '.join(genres_list)
                            primary_genre = genre_map.get(genres_list[0], genres_list[0]) if genres_list else ''
                            metacritic = app_data.get('metacritic', {}).get('score', None)
                            platforms = ', '.join([p for p, v in app_data.get('platforms', {}).items() if v])
                            release_date = app_data.get('release_date', {}).get('date', None)

                    # Price from SteamSpy (in cents)
                    price = game.get('price', 0)
                    try:
                        price_usd = int(price) / 100 if price else 0
                    except:
                        price_usd = 0

                    # Use SteamSpy data where Steam Store doesn't have it
                    game_info = {
                        'game_id': int(app_id),
                        'name': game.get('name', 'Unknown'),
                        'release_date': release_date,
                        'developer': game.get('developer', ''),
                        'publisher': game.get('publisher', ''),
                        'price_usd': price_usd,
                        'genres': genres,
                        'primary_genre': primary_genre,
                        'platforms': platforms,
                        'metacritic_score': metacritic,
                        'positive_reviews': game.get('positive', 0),
                        'negative_reviews': game.get('negative', 0),
                        'estimated_owners': game.get('owners', ''),
                        'average_playtime': game.get('average_forever', 0),
                        'median_playtime': game.get('median_forever', 0),
                        'tags': ', '.join(list(game.get('tags', {}).keys())[:5]) if game.get('tags') else '',
                        'data_source': 'steam'
                    }

                    games_data.append(game_info)
                    print(f"  ✓ [{idx+1}/{limit}] {game_info['name']} | ${price_usd} | {primary_genre}")
                    time.sleep(1.2)  # Steam Store rate limit

                except Exception as e:
                    print(f"  ✗ Error with {app_id}: {str(e)}")
                    continue

            print(f"\n✓ Extracted {len(games_data)} games from Steam/SteamSpy")
            return games_data

        except Exception as e:
            print(f"✗ SteamSpy extraction failed: {str(e)}")
            return []

    def extract_igdb_data(self, limit: int = 100) -> List[Dict]:
        """Extract data from IGDB API"""
        print(f"\n📥 Extracting IGDB data (limit: {limit})...")
        games_data = []

        genre_map = {
            'Role-playing (RPG)': 'RPG',
            'Hack and slash/Beat \'em up': 'Action',
            'Point-and-click': 'Adventure',
            'Card & Board Game': 'Strategy',
            'Turn-based strategy (TBS)': 'Strategy',
            'Real Time Strategy (RTS)': 'Strategy',
            'Fighting': 'Action',
            'Visual Novel': 'Adventure',
        }

        try:
            url = "https://api.igdb.com/v4/games"
            headers = {
                'Client-ID': self.igdb_client_id,
                'Authorization': f'Bearer {self.igdb_access_token}'
            }

            query = f"""
                fields name, first_release_date, genres.name, platforms.name,
                       rating, rating_count, involved_companies.company.name,
                       involved_companies.developer, involved_companies.publisher;
                where rating_count > 20 & rating > 65;
                limit {min(limit, 500)};
                sort rating_count desc;
            """

            response = requests.post(url, headers=headers, data=query, timeout=30)
            igdb_games = response.json()

            for idx, game in enumerate(igdb_games):
                developers, publishers = [], []
                if 'involved_companies' in game:
                    for company in game['involved_companies']:
                        name = company.get('company', {}).get('name', '')
                        if company.get('developer'):
                            developers.append(name)
                        if company.get('publisher'):
                            publishers.append(name)

                genres_list = [g['name'] for g in game.get('genres', [])]
                primary_genre = genre_map.get(genres_list[0], genres_list[0]) if genres_list else ''

                game_info = {
                    'game_id': game.get('id'),
                    'name': game.get('name', 'Unknown'),
                    'release_date': datetime.fromtimestamp(game['first_release_date']).strftime('%Y-%m-%d') if 'first_release_date' in game else None,
                    'developer': ', '.join(set(developers)),
                    'publisher': ', '.join(set(publishers)),
                    'price_usd': None,
                    'genres': ', '.join(genres_list),
                    'primary_genre': primary_genre,
                    'platforms': ', '.join([p['name'] for p in game.get('platforms', [])]),
                    'metacritic_score': None,
                    'igdb_rating': round(game.get('rating', 0), 2),
                    'igdb_rating_count': game.get('rating_count', 0),
                    'data_source': 'igdb'
                }

                games_data.append(game_info)
                print(f"  ✓ [{idx+1}/{len(igdb_games)}] {game_info['name']} | Rating: {game_info['igdb_rating']} | {primary_genre}")

            print(f"\n✓ Extracted {len(games_data)} games from IGDB")
            return games_data

        except Exception as e:
            print(f"✗ IGDB extraction failed: {str(e)}")
            return []

    def transform_data(self, games_data: List[Dict]) -> pd.DataFrame:
        """Transform and clean extracted data"""
        print("\n🔄 Transforming data...")

        if not games_data:
            return pd.DataFrame()

        df = pd.DataFrame(games_data)

        # Ensure all columns exist
        expected_columns = [
            'game_id', 'name', 'release_date', 'developer', 'publisher',
            'price_usd', 'genres', 'primary_genre', 'platforms', 'metacritic_score',
            'positive_reviews', 'negative_reviews', 'estimated_owners',
            'average_playtime', 'median_playtime', 'tags',
            'igdb_rating', 'igdb_rating_count', 'data_source'
        ]

        for col in expected_columns:
            if col not in df.columns:
                df[col] = None

        # Clean data
        df['price_usd'] = pd.to_numeric(df['price_usd'], errors='coerce').fillna(0)
        df['release_date'] = pd.to_datetime(df['release_date'], errors='coerce')
        df['release_year'] = df['release_date'].dt.year
        df['release_month'] = df['release_date'].dt.month
        df['is_free'] = df['price_usd'] == 0

        # Remove duplicates by name within same source
        df = df.drop_duplicates(subset=['name', 'data_source'], keep='first')

        print(f"✓ Transformed {len(df)} records")
        return df

    def load_data(self, df: pd.DataFrame, source: str):
        """Load transformed data into database"""
        if df.empty:
            print(f"⚠ No {source} data to load")
            return

        print(f"\n💾 Loading {source} data to database...")
        conn = sqlite3.connect(self.db_path)

        try:
            conn.execute("DELETE FROM games WHERE data_source = ?", (source,))
            df.to_sql('games', conn, if_exists='append', index=False)

            count = pd.read_sql(
                "SELECT COUNT(*) as count FROM games WHERE data_source = ?",
                conn, params=(source,)
            )['count'][0]

            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO etl_log (source, records_extracted, records_loaded, status)
                VALUES (?, ?, ?, ?)
            """, (source, len(df), count, 'success'))

            conn.commit()
            print(f"✓ Loaded {count} records from {source}")

        except Exception as e:
            print(f"✗ Loading failed: {str(e)}")
            raise
        finally:
            conn.close()

    def export_dashboard_files(self):
        """Export clean CSV files for dashboard"""
        print("\n📤 Exporting dashboard files...")
        os.makedirs("dashboard_exports", exist_ok=True)
        conn = sqlite3.connect(self.db_path)

        # Games master
        games = pd.read_sql("""
            SELECT game_id, name, release_date, developer, publisher,
                   price_usd, primary_genre as genre, genres, platforms,
                   metacritic_score, igdb_rating, positive_reviews,
                   negative_reviews, average_playtime, estimated_owners,
                   data_source, release_year, release_month, is_free
            FROM games WHERE name IS NOT NULL
        """, conn)
        games.to_csv("dashboard_exports/games_master.csv", index=False)
        print(f"  ✓ games_master.csv ({len(games)} records)")

        # Genre analysis
        genre = pd.read_sql("""
            SELECT primary_genre as genre, COUNT(*) as game_count,
                   ROUND(AVG(price_usd), 2) as avg_price,
                   ROUND(AVG(igdb_rating), 1) as avg_rating
            FROM games
            WHERE primary_genre IS NOT NULL AND primary_genre != ''
            GROUP BY primary_genre ORDER BY game_count DESC
        """, conn)
        genre.to_csv("dashboard_exports/genre_analysis.csv", index=False)
        print(f"  ✓ genre_analysis.csv ({len(genre)} genres)")

        # Price buckets
        price = pd.read_sql("""
            SELECT CASE
                WHEN price_usd = 0 THEN '1_Free'
                WHEN price_usd < 10 THEN '2_Under $10'
                WHEN price_usd < 20 THEN '3_$10-$20'
                WHEN price_usd < 40 THEN '4_$20-$40'
                WHEN price_usd < 60 THEN '5_$40-$60'
                ELSE '6_$60+'
            END as price_range,
            COUNT(*) as game_count,
            ROUND(AVG(igdb_rating), 1) as avg_rating
            FROM games GROUP BY price_range ORDER BY price_range
        """, conn)
        price.to_csv("dashboard_exports/price_buckets.csv", index=False)
        print(f"  ✓ price_buckets.csv ({len(price)} buckets)")

        # Monthly releases
        monthly = pd.read_sql("""
            SELECT release_year as year, release_month as month,
                   COUNT(*) as releases,
                   ROUND(AVG(price_usd), 2) as avg_price
            FROM games
            WHERE release_year >= 2015 AND release_year IS NOT NULL
            GROUP BY year, month ORDER BY year, month
        """, conn)
        monthly.to_csv("dashboard_exports/monthly_trends.csv", index=False)
        print(f"  ✓ monthly_trends.csv ({len(monthly)} months)")

        # Platform breakdown
        platform = pd.read_sql("""
            SELECT CASE
                WHEN platforms LIKE '%windows%' OR platforms LIKE '%Windows%'
                     OR platforms LIKE '%PC%' THEN 'PC'
                WHEN platforms LIKE '%PlayStation%' OR platforms LIKE '%PS%' THEN 'PlayStation'
                WHEN platforms LIKE '%Xbox%' THEN 'Xbox'
                WHEN platforms LIKE '%Nintendo%' OR platforms LIKE '%Switch%' THEN 'Nintendo'
                WHEN platforms LIKE '%iOS%' OR platforms LIKE '%Android%' THEN 'Mobile'
                ELSE 'Other'
            END as platform,
            COUNT(*) as game_count
            FROM games WHERE platforms IS NOT NULL AND platforms != ''
            GROUP BY platform ORDER BY game_count DESC
        """, conn)
        platform.to_csv("dashboard_exports/platform_breakdown.csv", index=False)
        print(f"  ✓ platform_breakdown.csv ({len(platform)} platforms)")

        conn.close()
        print("\n✅ All dashboard files exported!")

    def generate_monthly_metrics(self):
        """Generate monthly metrics"""
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute("DELETE FROM monthly_metrics")
            conn.execute("""
                INSERT INTO monthly_metrics (year, month, total_releases, avg_price, top_genre)
                SELECT
                    CAST(strftime('%Y', release_date) AS INTEGER) as year,
                    CAST(strftime('%m', release_date) AS INTEGER) as month,
                    COUNT(*) as total_releases,
                    ROUND(AVG(price_usd), 2) as avg_price,
                    primary_genre as top_genre
                FROM games
                WHERE release_date IS NOT NULL
                GROUP BY year, month
                HAVING year >= 2015
            """)
            conn.commit()
            print("✓ Monthly metrics generated")
        except Exception as e:
            print(f"✗ Metrics failed: {str(e)}")
        finally:
            conn.close()

    def run_pipeline(self, steam_limit: int = 100, igdb_limit: int = 100):
        """Run complete ETL pipeline"""
        print("="*60)
        print("🚀 GAMING DATA PIPELINE - STARTING")
        print("="*60)
        start_time = time.time()

        steam_data = self.extract_steamspy_data(limit=steam_limit)
        igdb_data = self.extract_igdb_data(limit=igdb_limit)

        if steam_data:
            steam_df = self.transform_data(steam_data)
            if not steam_df.empty:
                self.load_data(steam_df, 'steam')

        if igdb_data:
            igdb_df = self.transform_data(igdb_data)
            if not igdb_df.empty:
                self.load_data(igdb_df, 'igdb')

        self.generate_monthly_metrics()
        self.export_dashboard_files()

        elapsed = time.time() - start_time
        print(f"\n{'='*60}")
        print(f"✅ PIPELINE COMPLETE - Time: {elapsed:.2f}s")
        print(f"{'='*60}")


if __name__ == "__main__":
    import config
    pipeline = GamingDataPipeline(
        config.STEAM_API_KEY,
        config.IGDB_CLIENT_ID,
        config.IGDB_ACCESS_TOKEN
    )
    pipeline.run_pipeline(
        steam_limit=config.STEAM_GAMES_LIMIT,
        igdb_limit=config.IGDB_GAMES_LIMIT
    )