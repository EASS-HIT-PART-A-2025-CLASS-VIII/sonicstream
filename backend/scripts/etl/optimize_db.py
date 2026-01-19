import sqlite3
import os
import time

"""
Script: optimize_db.py
Description:
    Optimizes the SQLite database by creating necessary indexes and running ANALYZE.
    This improves JOIN performance considerably for the large 5GB dataset.
    
Usage:
    python backend/scripts/etl/optimize_db.py
"""

# Path to database (relative to project root usually)
# Adjust search path to be robust
DB_PATH = "backend/spotify.sqlite"

def optimize_database():
    if not os.path.exists(DB_PATH):
        # fast check relative to this script
        fallback = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "spotify.sqlite")
        if os.path.exists(fallback):
             DB_PATH = fallback
        else:
            print(f"Error: Database not found at {DB_PATH}")
            return

    print(f"Connecting to database at {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Indexes to create for JOIN performance
    indexes = [
        # Foreign keys in tracks
        ("idx_tracks_audio_feature", "tracks", "audio_feature_id"),
        
        # Junction tables (CRITICAL for Joins)
        ("idx_rta_track", "r_track_artist", "track_id"),
        ("idx_rta_artist", "r_track_artist", "artist_id"),
        ("idx_rat_track", "r_albums_tracks", "track_id"),
        ("idx_rat_album", "r_albums_tracks", "album_id"),
        
        # Primary keys (usually implicit, but good to ensure for joins)
        ("idx_artists_id", "artists", "id"),
        ("idx_albums_id", "albums", "id"),
        ("idx_audio_features_id", "audio_features", "id"),
        
        # Search performance
        ("idx_tracks_name", "tracks", "name"),
        ("idx_artists_name", "artists", "name")
    ]

    print("Checking and creating indexes...")
    start_time = time.time()
    
    for idx_name, table, column in indexes:
        try:
            print(f"Creating index {idx_name} on {table}({column})...", end="", flush=True)
            # Check if index exists first to avoid time wasting if possible, 
            # though IF NOT EXISTS handles logic, it still checks
            cursor.execute(f"CREATE INDEX IF NOT EXISTS {idx_name} ON {table} ({column})")
            print(" Done.")
        except Exception as e:
            print(f" Failed: {e}")

    print(f"Indexes check/creation completed in {time.time() - start_time:.2f} seconds.")

    print("Running ANALYZE to update query planner statistics (this might take a minute)...")
    start_time = time.time()
    try:
        cursor.execute("ANALYZE")
        print(f"ANALYZE completed in {time.time() - start_time:.2f} seconds.")
    except Exception as e:
        print(f"ANALYZE failed: {e}")

    conn.commit()
    conn.close()
    print("Database optimization complete! Queries should be much faster now.")

if __name__ == "__main__":
    optimize_database()
