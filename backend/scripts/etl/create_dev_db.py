import sqlite3
import os
import sys
import time
from tqdm import tqdm

"""
Script: create_dev_db.py
Description:
    This script is the "ETL" (Extract, Transform, Load) pipeline for creating a lightweight
    development database (`spotify_dev.sqlite`) from the massive production dataset (`spotify.sqlite`).

    It performs the following roles:
    1. EXTRACT: Connects to the ~5GB source SQLite database.
    2. TRANSFORM: 
       - Joins multiple normalized tables (tracks, artists, albums, audio_features).
       - Selects a subset of tracks (controlled by LIMIT).
       - Flattens the data into a single denormalized table for easy consumption.
       - Extracts key metadata including 'popularity' and 'album' name.
    3. LOAD: Writes the result to a new, smaller SQLite file (`spotify_dev.sqlite`).

Usage:
    Run this script ONCE to generate the dev database.
    > python backend/scripts/etl/create_dev_db.py

    The resulting file is used by `dev_seed.py` to quickly seed the Postgres database
    without needing the full 5GB source file.
"""

# Configuration
# Adjust paths assuming run from project root: python backend/scripts/etl/create_dev_db.py
# SOURCE/TARGET are in backend/
SOURCE_DB = "backend/spotify.sqlite"
TARGET_DB = "backend/spotify_dev.sqlite"
LIMIT = 100000 # Number of tracks to extract

def progress_handler():
    """Called by SQLite virtual machine every N opcodes to show activity."""
    print(".", end="", flush=True)

def create_dev_db():
    global SOURCE_DB, TARGET_DB
    
    if not os.path.exists(SOURCE_DB):
        # Fallback check relative to script execution?
        # Let's try finding it just in case cwd is different
        if os.path.exists("spotify.sqlite"):
            # We are running from backend/ probably
            SOURCE_DB = "spotify.sqlite"
            TARGET_DB = "spotify_dev.sqlite"
        else:
            print(f"❌ Source DB '{SOURCE_DB}' not found! Please ensure the full dataset is present.")
            return

    if os.path.exists(TARGET_DB):
        print(f"⚠️  Target DB '{TARGET_DB}' already exists. Overwriting with new schema...")
        os.remove(TARGET_DB)

    print(f"🚀 Starting Extraction: {SOURCE_DB} -> {TARGET_DB}")
    print(f"🎯 Target: {LIMIT} rows (Flattened Schema with Album & Popularity)")
    print(f"⏳ This involves complex JOINs on a 5GB DB. Please wait approx 5-15 mins.\n")

    # 1. Connect to Source
    # We use a progress handler to give visual feedback during long queries
    src = sqlite3.connect(SOURCE_DB)
    src.set_progress_handler(progress_handler, 5000000) 
    
    # 2. Connect to Target
    dst = sqlite3.connect(TARGET_DB)
    
    try:
        # Create the single FLAT table
        # This schema is "Denormalized" - optimized for easy reading/seeding, not update speed.
        dst.execute("""
            CREATE TABLE IF NOT EXISTS dev_tracks (
                track_id TEXT PRIMARY KEY,
                name TEXT,
                artist TEXT,
                album TEXT,
                popularity INTEGER,
                danceability FLOAT,
                energy FLOAT,
                valence FLOAT,
                tempo FLOAT,
                acousticness FLOAT
            )
        """)
        
        # The Complex Extraction Query
        # Notes:
        # - GROUP_CONCAT(a.name): Handles tracks with multiple artists
        # - JOIN r_track_album + JOIN albums: Fetches the Album name
        # - MAX(...): Used because of GROUP BY track_id; ensures we get a single value per track
        query = f"""
            SELECT 
                t.id, 
                t.name, 
                GROUP_CONCAT(distinct a.name) as artist,
                MAX(alb.name) as album,
                MAX(t.popularity) as popularity,
                MAX(af.danceability), 
                MAX(af.energy), 
                MAX(af.valence), 
                MAX(af.tempo), 
                MAX(af.acousticness)
            FROM tracks t
            JOIN audio_features af ON t.id = af.id
            JOIN r_track_artist rta ON t.id = rta.track_id
            JOIN artists a ON rta.artist_id = a.id
            LEFT JOIN r_albums_tracks rtalb ON t.id = rtalb.track_id
            LEFT JOIN albums alb ON rtalb.album_id = alb.id
            GROUP BY t.id
            LIMIT {LIMIT}
        """
        
        print("⚡ Executing Query (Extracting & Joining)...", end=" ")
        
        start_time = time.time()
        cursor = src.cursor()
        cursor.execute(query)
        
        print("\n✅ Query successful! Streaming results to target DB...")
        
        # Insert Loop with Progress Bar
        # We fetch in batches to keep memory usage low
        pbar = tqdm(total=LIMIT, unit="rows", desc="💾 Saving")
        count = 0
        BATCH_SIZE = 10000
        
        while True:
            rows = cursor.fetchmany(BATCH_SIZE)
            if not rows:
                break
                
            # Insert into the flattened table
            # Validates that the number of ? matches the table columns
            dst.executemany("INSERT INTO dev_tracks VALUES (?,?,?,?,?,?,?,?,?,?)", rows)
            dst.commit()
            
            count += len(rows)
            pbar.update(len(rows))
            
        pbar.close()
        print(f"\n🏁 DONE! Created {TARGET_DB} with {count} rows.")
        print(f"   Schema includes: [id, name, artist, album, popularity, audio_features...]")
        print(f"⏱️  Total time: {round((time.time() - start_time)/60, 1)} minutes.")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        src.close()
        dst.close()

if __name__ == "__main__":
    create_dev_db()
