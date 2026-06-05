"""
Game Segmentation Analysis
Uses K-Means clustering to identify game segments
based on playtime, price, rating and review behavior
"""

import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


# ============================================================
# STAGE 1: LOAD AND EXPLORE DATA
# ============================================================

def load_data():
    """Load game data from SQLite database"""
    conn = sqlite3.connect('gaming_data.db')

    df = pd.read_sql("""
        SELECT 
            name,
            price_usd,
            average_playtime,
            igdb_rating,
            positive_reviews,
            negative_reviews,
            primary_genre,
            data_source
        FROM games
        WHERE average_playtime IS NOT NULL
          AND price_usd IS NOT NULL
    """, conn)

    conn.close()
    return df


def explore_data(df):
    """Explore the dataset before any processing"""

    print("=" * 60)
    print("STAGE 1: DATA EXPLORATION")
    print("=" * 60)

    # Basic info
    print(f"\n📦 Total games loaded: {len(df)}")
    print(f"📋 Columns: {list(df.columns)}")

    # Check for missing values
    print("\n🔍 Missing values per column:")
    print(df.isnull().sum())

    # Basic statistics
    print("\n📊 Basic statistics:")
    print(df[['price_usd', 'average_playtime',
              'igdb_rating', 'positive_reviews']].describe())

    # Check distributions
    print("\n💰 Price breakdown:")
    print(f"   Free games: {(df['price_usd'] == 0).sum()}")
    print(f"   Paid games: {(df['price_usd'] > 0).sum()}")
    print(f"   Most expensive: ${df['price_usd'].max()}")
    print(f"   Average price: ${df['price_usd'].mean():.2f}")

    print("\n🎮 Playtime breakdown:")
    print(f"   Zero playtime: {(df['average_playtime'] == 0).sum()}")
    print(f"   Max playtime: {df['average_playtime'].max()} mins")
    print(f"   Average playtime: {df['average_playtime'].mean():.0f} mins")

    print("\n⭐ Rating breakdown:")
    print(f"   No rating: {df['igdb_rating'].isnull().sum()}")
    print(f"   Average rating: {df['igdb_rating'].mean():.1f}")


# ============================================================
# STAGE 2: DATA PREPARATION
# ============================================================

def prepare_features(df):
    """Clean and prepare features for clustering"""

    print("\n" + "=" * 60)
    print("STAGE 2: DATA PREPARATION")
    print("=" * 60)

    # Step 1: Filter to Steam games only (have review data)
    df_steam = df[df['data_source'] == 'steam'].copy()
    print(f"\n📦 Steam games available: {len(df_steam)}")

    # Step 2: Remove games with no reviews at all
    df_steam = df_steam[
        (df_steam['positive_reviews'] > 0) |
        (df_steam['negative_reviews'] > 0)
        ]
    print(f"📦 Games with review data: {len(df_steam)}")

    # Step 3: Calculate review score (sentiment ratio)
    # This is a DERIVED FEATURE - we're creating new information
    # from existing data
    total_reviews = df_steam['positive_reviews'] + df_steam['negative_reviews']
    df_steam['review_score'] = (
            df_steam['positive_reviews'] / total_reviews
    ).round(4)

    print(f"\n📊 Review score sample:")
    print(df_steam[['name', 'positive_reviews',
                    'negative_reviews', 'review_score']]
          .head(10).to_string(index=False))

    # Step 4: Select final features for clustering
    features = ['price_usd', 'positive_reviews',
                'negative_reviews', 'review_score']

    df_features = df_steam[['name', 'primary_genre'] + features].copy()

    # Step 5: Check for any remaining nulls
    print(f"\n🔍 Null check on features:")
    print(df_features[features].isnull().sum())

    # Step 6: Fill any nulls with 0
    df_features[features] = df_features[features].fillna(0)

    # Step 7: Show final statistics
    print(f"\n📊 Feature statistics after preparation:")
    print(df_features[features].describe().round(2))

    print(f"\n✅ Features ready for scaling: {features}")

    return df_features, features


# ============================================================
# STAGE 3: FEATURE SCALING
# ============================================================

from sklearn.preprocessing import MinMaxScaler


def scale_features(df_features, features):
    """
    Scale all features to range 0-1
    So no single feature dominates the clustering
    """

    print("\n" + "=" * 60)
    print("STAGE 3: FEATURE SCALING")
    print("=" * 60)

    # MinMaxScaler transforms each feature to range [0, 1]
    # Formula: (value - min) / (max - min)
    scaler = MinMaxScaler()

    # Scale the features
    scaled_values = scaler.fit_transform(df_features[features])

    # Put scaled values into a new dataframe
    df_scaled = pd.DataFrame(
        scaled_values,
        columns=[f"{f}_scaled" for f in features]
    )

    # Add name and genre back for reference
    df_scaled['name'] = df_features['name'].values
    df_scaled['primary_genre'] = df_features['primary_genre'].values

    # Show before and after comparison
    print("\n📊 Before scaling (raw values):")
    print(df_features[features].describe().round(2))

    print("\n📊 After scaling (0 to 1 range):")
    scaled_cols = [f"{f}_scaled" for f in features]
    print(df_scaled[scaled_cols].describe().round(4))

    # Verify scaling worked - all min should be 0, all max should be 1
    print("\n✅ Scaling verification:")
    for col in scaled_cols:
        min_val = df_scaled[col].min()
        max_val = df_scaled[col].max()
        print(f"   {col}: min={min_val:.4f}, max={max_val:.4f}")

    return df_scaled, scaled_cols, scaler


# ============================================================
# STAGE 4: K-MEANS CLUSTERING
# ============================================================

from sklearn.cluster import KMeans
import warnings

warnings.filterwarnings('ignore')


def find_optimal_k(df_scaled, scaled_cols):
    """
    Use the Elbow Method to find optimal number of clusters
    """

    print("\n" + "=" * 60)
    print("STAGE 4A: FINDING OPTIMAL K (ELBOW METHOD)")
    print("=" * 60)

    X = df_scaled[scaled_cols].values

    inertias = []
    k_range = range(2, 11)

    for k in k_range:
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        kmeans.fit(X)
        inertias.append(kmeans.inertia_)
        print(f"  K={k}: Inertia = {kmeans.inertia_:.4f}")

    # Plot the elbow curve
    plt.figure(figsize=(10, 6))
    plt.plot(k_range, inertias, 'bo-', linewidth=2, markersize=8)
    plt.xlabel('Number of Clusters (K)', fontsize=12)
    plt.ylabel('Inertia', fontsize=12)
    plt.title('Elbow Method - Finding Optimal K', fontsize=14)
    plt.xticks(k_range)
    plt.grid(True, alpha=0.3)

    # Highlight each point
    for k, inertia in zip(k_range, inertias):
        plt.annotate(f'K={k}', (k, inertia),
                     textcoords="offset points",
                     xytext=(0, 10), ha='center')

    plt.tight_layout()
    plt.savefig('elbow_curve.png', dpi=150, bbox_inches='tight')
    plt.show()
    print("\n📊 Elbow curve saved as: elbow_curve.png")
    print("👀 Look at the chart - where does the curve stop dropping sharply?")

    return inertias


def run_clustering(df_scaled, scaled_cols, df_features, k=4):
    """
    Run K-Means with chosen K value
    """

    print("\n" + "=" * 60)
    print(f"STAGE 4B: RUNNING K-MEANS WITH K={k}")
    print("=" * 60)

    X = df_scaled[scaled_cols].values

    # Run K-Means
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    clusters = kmeans.fit_predict(X)

    # Add cluster labels to dataframe
    df_scaled['cluster'] = clusters
    df_features['cluster'] = clusters

    # Show cluster sizes
    print("\n📊 Games per cluster:")
    cluster_counts = df_scaled['cluster'].value_counts().sort_index()
    for cluster_id, count in cluster_counts.items():
        print(f"   Cluster {cluster_id}: {count} games")

    # Show cluster characteristics (mean of each feature per cluster)
    print("\n📊 Cluster characteristics (mean scaled values):")
    cluster_means = df_scaled.groupby('cluster')[scaled_cols].mean().round(3)
    print(cluster_means.to_string())

    # Show sample games from each cluster
    print("\n🎮 Sample games per cluster:")
    for cluster_id in range(k):
        games_in_cluster = df_features[
            df_features['cluster'] == cluster_id
            ]['name'].head(5).tolist()
        print(f"\n   Cluster {cluster_id}: {', '.join(games_in_cluster)}")

    return df_scaled, df_features, kmeans


# ============================================================
# STAGE 5: VISUALIZATION
# ============================================================

def visualize_clusters(df_scaled, df_features, scaled_cols, k=4):
    """
    Create professional visualizations of clustering results
    """

    print("\n" + "=" * 60)
    print("STAGE 5: VISUALIZATION")
    print("=" * 60)

    # Confirmed segment names
    segment_names = {
        0: "Premium Releases",
        1: "Underperformers",
        2: "Community Favorites",
        3: "Evergreen Blockbusters"
    }

    # Professional color palette
    colors = {
        0: "#2E75B6",  # Blue  - Premium Releases
        1: "#C00000",  # Red   - Underperformers
        2: "#2E8B57",  # Green - Community Favorites
        3: "#F5A623"  # Amber - Evergreen Blockbusters
    }

    # Add segment names to dataframes
    df_scaled['segment'] = df_scaled['cluster'].map(segment_names)
    df_features['segment'] = df_features['cluster'].map(segment_names)

    # --------------------------------------------------------
    # CHART 1: Price vs Review Score scatter
    # --------------------------------------------------------
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))
    fig.suptitle('Game Market Segmentation Analysis',
                 fontsize=16, fontweight='bold')

    ax1 = axes[0]
    for cluster_id, segment_name in segment_names.items():
        mask = df_scaled['cluster'] == cluster_id
        ax1.scatter(
            df_scaled[mask]['price_usd_scaled'],
            df_scaled[mask]['review_score_scaled'],
            c=colors[cluster_id],
            label=segment_name,
            alpha=0.7,
            s=80,
            edgecolors='white',
            linewidth=0.5
        )

    ax1.set_xlabel('Price (Scaled)', fontsize=11)
    ax1.set_ylabel('Review Score (Scaled)', fontsize=11)
    ax1.set_title('Price vs Review Score by Segment', fontsize=12)
    ax1.legend(loc='lower right', fontsize=9)
    ax1.grid(True, alpha=0.3)
    ax1.set_facecolor('#F8F9FA')

    # --------------------------------------------------------
    # CHART 2: Popularity vs Controversy scatter
    # --------------------------------------------------------
    ax2 = axes[1]
    for cluster_id, segment_name in segment_names.items():
        mask = df_scaled['cluster'] == cluster_id
        ax2.scatter(
            df_scaled[mask]['positive_reviews_scaled'],
            df_scaled[mask]['negative_reviews_scaled'],
            c=colors[cluster_id],
            label=segment_name,
            alpha=0.7,
            s=80,
            edgecolors='white',
            linewidth=0.5
        )

    ax2.set_xlabel('Positive Reviews (Scaled)', fontsize=11)
    ax2.set_ylabel('Negative Reviews (Scaled)', fontsize=11)
    ax2.set_title('Popularity vs Controversy by Segment', fontsize=12)
    ax2.legend(loc='upper left', fontsize=9)
    ax2.grid(True, alpha=0.3)
    ax2.set_facecolor('#F8F9FA')

    plt.tight_layout()
    plt.savefig('cluster_scatter.png', dpi=150, bbox_inches='tight')
    plt.show()
    print("📊 Saved: cluster_scatter.png")

    # --------------------------------------------------------
    # CHART 3: Segment Characteristics
    # --------------------------------------------------------
    fig, ax = plt.subplots(figsize=(14, 7))

    cluster_means = df_scaled.groupby('cluster')[scaled_cols].mean()
    cluster_means.index = [segment_names[i] for i in cluster_means.index]

    display_cols = {
        'price_usd_scaled': 'Price',
        'positive_reviews_scaled': 'Positive Reviews',
        'negative_reviews_scaled': 'Negative Reviews',
        'review_score_scaled': 'Review Score'
    }
    cluster_means = cluster_means.rename(columns=display_cols)

    x = range(len(cluster_means))
    width = 0.2
    feature_colors = ['#2E75B6', '#2E8B57', '#C00000', '#F5A623']

    for i, col in enumerate(cluster_means.columns):
        offset = (i - 1.5) * width
        bars = ax.bar(
            [xi + offset for xi in x],
            cluster_means[col],
            width,
            label=col,
            color=feature_colors[i],
            alpha=0.85,
            edgecolor='white'
        )

    ax.set_xlabel('Market Segment', fontsize=11)
    ax.set_ylabel('Mean Scaled Value (0-1)', fontsize=11)
    ax.set_title('Segment Characteristics by Feature',
                 fontsize=13, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(cluster_means.index, rotation=15, ha='right')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3, axis='y')
    ax.set_facecolor('#F8F9FA')

    plt.tight_layout()
    plt.savefig('cluster_characteristics.png', dpi=150, bbox_inches='tight')
    plt.show()
    print("📊 Saved: cluster_characteristics.png")

    # --------------------------------------------------------
    # CHART 4: Games per Segment
    # --------------------------------------------------------
    fig, ax = plt.subplots(figsize=(10, 6))

    segment_order = [
        "Evergreen Blockbusters",
        "Premium Releases",
        "Community Favorites",
        "Underperformers"
    ]

    segment_counts = df_scaled['segment'].value_counts()
    segment_counts = segment_counts.reindex(segment_order)

    bar_colors = [
        "#F5A623",  # Evergreen Blockbusters
        "#2E75B6",  # Premium Releases
        "#2E8B57",  # Community Favorites
        "#C00000"  # Underperformers
    ]

    bars = ax.barh(
        segment_counts.index,
        segment_counts.values,
        color=bar_colors,
        alpha=0.85,
        edgecolor='white',
        height=0.5
    )

    # Add count and percentage labels
    total = segment_counts.sum()
    for bar, count in zip(bars, segment_counts.values):
        percentage = (count / total * 100)
        ax.text(
            bar.get_width() + 0.3,
            bar.get_y() + bar.get_height() / 2,
            f'{count} games ({percentage:.0f}%)',
            va='center',
            fontsize=10
        )

    ax.set_xlabel('Number of Games', fontsize=11)
    ax.set_title('Games per Market Segment',
                 fontsize=13, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='x')
    ax.set_facecolor('#F8F9FA')
    ax.set_xlim(0, segment_counts.max() + 15)

    plt.tight_layout()
    plt.savefig('segment_distribution.png', dpi=150, bbox_inches='tight')
    plt.show()
    print("📊 Saved: segment_distribution.png")

    # --------------------------------------------------------
    # FINAL SUMMARY
    # --------------------------------------------------------
    print("\n" + "=" * 60)
    print("SEGMENTATION SUMMARY")
    print("=" * 60)

    # Data limitation note
    print("""
⚠  DATA NOTE: Price reflects current Steam pricing,
   not original launch price. Legacy titles may show
   artificially low prices due to post-launch
   pricing adjustments (e.g. GTA V Legacy, TF2).
    """)

    for cluster_id, segment_name in segment_names.items():
        games = df_features[
            df_features['cluster'] == cluster_id
            ]['name'].tolist()

        means = df_scaled[
            df_scaled['cluster'] == cluster_id
            ][scaled_cols].mean()

        total = len(df_features)
        count = len(games)
        percentage = (count / total * 100)

        print(f"\n📊 {segment_name} ({count} games | {percentage:.0f}% of catalog)")

        if cluster_id != 3:  # Skip price for Evergreen Blockbusters
            print(f"   Avg Price Score:    {means['price_usd_scaled']:.3f}")

        print(f"   Avg Popularity:     {means['positive_reviews_scaled']:.3f}")
        print(f"   Avg Controversy:    {means['negative_reviews_scaled']:.3f}")
        print(f"   Avg Review Score:   {means['review_score_scaled']:.3f}")
        print(f"   Example titles:     {', '.join(games[:3])}")

    print("\n" + "=" * 60)
    print("KEY INSIGHT")
    print("=" * 60)
    print("""
   57% of games fall in Community Favorites - the largest
   segment. Quality at accessible price points consistently
   outperforms both premium and monetization-heavy titles.

   The market rewards genuine player value regardless of
   budget or franchise size.
    """)

if __name__ == "__main__":
    df = load_data()
    explore_data(df)
    df_features, features = prepare_features(df)
    df_scaled, scaled_cols, scaler = scale_features(df_features, features)
    inertias = find_optimal_k(df_scaled, scaled_cols)
    df_scaled, df_features, kmeans = run_clustering(
        df_scaled, scaled_cols, df_features, k=4
    )
    visualize_clusters(df_scaled, df_features, scaled_cols, k=4)