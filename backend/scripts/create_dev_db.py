import sqlite3
import os
import sys
import time
from tqdm import tqdm

"""
Creates a lightweight 'Development Database' (spotify_dev.sqlite) from the massive 5GB source.
Strategy:
1. Connects to the main 5GB 'spotify.sqlite'.
2. Performs the complex JOIN (Tracks + Artists + AudioFeatures) for a limited subset (100k rows).
3. Materializes the result into a single FLAT table ('dev_tracks') in a new file.

Usage:
    Run this ONCE. Then use `seed.py` which will automatically detect and use this optimized file.
"""

# Config
SOURCE_DB = "spotify.sqlite"
TARGET_DB = "spotify_dev.sqlite"
LIMIT = 100000

def progress_handler():
    """Called by SQLite virtual machine every N opcodes."""
    print(".", end="", flush=True)

def create_dev_db():
    if not os.path.exists(SOURCE_DB):
        print(f"❌ Source DB '{SOURCE_DB}' not found!")
        return

    if os.path.exists(TARGET_DB):
        print(f"⚠️  Target DB '{TARGET_DB}' already exists. Overwriting...")
        os.remove(TARGET_DB)

    print(f"🚀 Starting Extraction: {SOURCE_DB} -> {TARGET_DB}")
    print(f"🎯 Target: {LIMIT} rows (with full joined data)")
    print(f"⏳ This involves a heavy JOIN. The dots below represent CPU activity (SQL opcodes).")
    print(f"   If dots are printing, IT IS WORKING. Please wait approx 5-15 mins.\n")

    # 1. Connect to Source
    src = sqlite3.connect(SOURCE_DB)
    # Print a dot every 5 million instructions to show liveness without flooding
    src.set_progress_handler(progress_handler, 5000000) 
    
    # 2. Connect to Target
    dst = sqlite3.connect(TARGET_DB)
    
    try:
        # Create single flat table
        dst.execute("""
            CREATE TABLE IF NOT EXISTS dev_tracks (
                track_id TEXT PRIMARY KEY,
                name TEXT,
                artist TEXT,
                danceability FLOAT,
                energy FLOAT,
                valence FLOAT,
                tempo FLOAT,
                acousticness FLOAT
            )
        """)
        
        # The complex query
        query = f"""
            SELECT 
                t.id, 
                t.name, 
                GROUP_CONCAT(a.name, ', ') as artist, 
                MAX(af.danceability), 
                MAX(af.energy), 
                MAX(af.valence), 
                MAX(af.tempo), 
                MAX(af.acousticness)
            FROM tracks t
            JOIN audio_features af ON t.id = af.id
            JOIN r_track_artist rta ON t.id = rta.track_id
            JOIN artists a ON rta.artist_id = a.id
            GROUP BY t.id
            LIMIT {LIMIT}
        """
        
        print("⚡ Executing Query...", end=" ")
        
        start_time = time.time()
        cursor = src.cursor()
        cursor.execute(query)
        
        print("\n✅ Query starting to yield rows! Fetching & Inserting...")
        
        # Insert Loop with Progress Bar
        pbar = tqdm(total=LIMIT, unit="rows", desc="💾 Saving")
        count = 0
        BATCH_SIZE = 10000
        
        while True:
            rows = cursor.fetchmany(BATCH_SIZE)
            if not rows:
                break
                
            dst.executemany("INSERT INTO dev_tracks VALUES (?,?,?,?,?,?,?,?)", rows)
            dst.commit()
            
            count += len(rows)
            pbar.update(len(rows))
            
        pbar.close()
        print(f"\n🏁 DONE! Created {TARGET_DB} with {count} rows.")
        print(f"⏱️  Total time: {round((time.time() - start_time)/60, 1)} minutes.")

    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        src.close()
        dst.close()

if __name__ == "__main__":
    create_dev_db()
