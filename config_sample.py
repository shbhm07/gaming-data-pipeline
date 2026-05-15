"""
Configuration File for Gaming Data Pipeline
===========================================

IMPORTANT: Replace the placeholder values below with your actual API keys
before running the pipeline.

HOW TO GET API KEYS:

1. Steam API Key:
   - Visit: https://steamcommunity.com/dev/apikey
   - Sign in with your Steam account
   - Accept the terms and create your key
   - Copy and paste it below

2. IGDB API Credentials:
   - Visit: https://api-docs.igdb.com/#account-creation
   - Sign up for a Twitch account (if you don't have one)
   - Register an application at: https://dev.twitch.tv/console/apps
   - Get your Client ID and generate an Access Token
   - Copy both values below

SECURITY NOTE: Keep this file private! Never share it or upload to GitHub
with your real API keys inside.
"""

# ============================================================================
# API CREDENTIALS - REPLACE THESE VALUES
# ============================================================================

# Steam API Key (looks like: A1B2C3D4E5F6G7H8I9J0K1L2M3N4O5P6)
STEAM_API_KEY = "YOUR_STEAM_API_KEY_HERE"

# IGDB Client ID (looks like: a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6)
IGDB_CLIENT_ID = "YOUR_IGDB_CLIENT_ID_HERE"

# IGDB Access Token (looks like: a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0)
IGDB_ACCESS_TOKEN = "YOUR_IGDB_ACCESS_TOKEN_HERE"

# ============================================================================
# PIPELINE SETTINGS (You can modify these)
# ============================================================================

# Number of games to extract from Steam
# Recommended: 50-100 (each game takes ~1.5 seconds due to rate limiting)
# For testing: Start with 20
STEAM_GAMES_LIMIT = 100

# Number of games to extract from IGDB
# Recommended: 50-100 (faster than Steam)
# For testing: Start with 20
IGDB_GAMES_LIMIT = 100

# ============================================================================
# DATABASE SETTINGS
# ============================================================================

# SQLite database filename
DATABASE_NAME = "gaming_data.db"

# ============================================================================
# VALIDATION (Don't modify this section)
# ============================================================================

def validate_config():
    """Check if configuration is properly set up"""
    errors = []

    if "YOUR_" in STEAM_API_KEY:
        errors.append("Steam API Key not configured")

    if "YOUR_" in IGDB_CLIENT_ID:
        errors.append("IGDB Client ID not configured")

    if "YOUR_" in IGDB_ACCESS_TOKEN:
        errors.append("IGDB Access Token not configured")

    if errors:
        print("\n❌ Configuration Error!")
        print("Please configure the following in config.py:")
        for error in errors:
            print(f"   • {error}")
        print("\nRefer to the comments in config.py for instructions.\n")
        return False

    return True
