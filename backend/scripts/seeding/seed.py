import sqlite3
import polars as pl
import os
import sys

# Adjust python path to allow importing from sibling/parent directories if needed
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import from etl module (assuming ingest_data is moved to etl folder or needs path adjustment)
# Since we are moving ingest_data to ../etl/ingest_data.py, we might need to adjust imports.
# However, usually scripts are run as modules or with PYTHONPATH setup. 
# For now, I will assume the user runs from root and I might need to fix imports later.
# But `ingest_data.py` is being moved to `etl/`.
# So `from ingest_data import ...` will break if I don't fix it.

# Let's try to fix the import dynamically
try:
    from backend.scripts.etl.ingest_data import insert_data, init_db
except ImportError:
    # Fallback if running from within scripts folder
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'etl'))
    from ingest_data import insert_data, init_db

"""
Script: seed.py
Description: 
    Seeds the Postgres database from the FULL production SQLite dump (spotify.sqlite).
    It streams data in chunks to handle the massive 5GB+ dataset without running out of memory.
    
    It performs a complex JOIN on tracks, artists, and audio_features.

Usage:
    This is the "Heavy" seeder. 
    For quick development, use `dev_seed.py` instead.
"""

# Configuration
SQLITE_DB_PATH = "spotify.sqlite"

def read_sqlite_data():
    """
    Reads data from SQLite into a Polars DataFrame.
    Handles JOINs and text encoding issues.
    """
    print(f"📂 Connecting to SQLite: {SQLITE_DB_PATH}...")
    
    if not os.path.exists(SQLITE_DB_PATH):
        raise FileNotFoundError(f"❌ Could not find {SQLITE_DB_PATH}. Please download it (check README.md) and place it in the backend/ directory.")

    conn = sqlite3.connect(SQLITE_DB_PATH)
    
    # 🛠️ Fix Encoding Issues: Ignore bad bytes
    conn.text_factory = lambda b: b.decode(errors="ignore")
    
    # JOIN Query
    # Based on schema:
    # tracks(id, name, ...)
    # audio_features(id, danceability, ...)
    # r_track_artist(track_id, artist_id)
    # artists(id, name)
    
    # Note: We take the first artist for simplicity if multiple exist
    # FULL FIDELITY QUERY
    # Joins Tracks, Artists, and Audio Features for complete data.
    # Note: This might take 1-2 minutes to start streaming due to the large JOIN.
    query = """
    SELECT 
        t.id as track_id,
        t.name as name,
        a.name as artist,
        af.danceability,
        af.energy,
        af.valence,
        af.tempo,
        af.acousticness
    FROM tracks t
    JOIN audio_features af ON t.id = af.id
    JOIN r_track_artist rta ON t.id = rta.track_id
    JOIN artists a ON rta.artist_id = a.id
    GROUP BY t.id
    """
    
    print("⚡ Reading data from SQLite (fetching via cursor for safe encoding)...")
    
    # Instead of loading everything into memory (8M is too big for simple lists), 
    # we will stream: SQLite -> Chunk -> Polars -> Insert -> Repeat
    
    print("⚡ Streaming data from SQLite (Querying 8M rows with JOINs, please wait)...")
    cursor = conn.cursor()
    
    try:
        cursor.execute(query)
        
        columns = ["track_id", "name", "artist", "danceability", "energy", "valence", "tempo", "acousticness"]
        BATCH_SIZE = 10000
        total_processed = 0
        
        while True:
            rows = cursor.fetchmany(BATCH_SIZE)
            if not rows:
                break
                
            # Create small DF for transformation
            df_chunk = pl.DataFrame(rows, schema=columns, orient="row")
            
            # Transform
            df_clean = transform_data(df_chunk)
            
            # Insert (We call insert_data per chunk)
            insert_data(df_clean)
            
            total_processed += len(rows)
            print(f"   🚀 Processed total: {total_processed} rows...")

    finally:
        conn.close()

def transform_data(df: pl.DataFrame):
    """
    Normalizes data to match the Data Engineering Pipeline standards.
    """
    # print("🧹 Normalizing Data...") # Commented out to reduce noise
    
    return (
        df
        # .unique(subset=["track_id"]) # Unique per chunk is safe enough mostly, global unique handled by DB constraint
        .with_columns([
            (pl.col("tempo") / 250.0).clip(0, 1).alias("tempo_norm"),
            pl.col("danceability").clip(0, 1),
            pl.col("energy").clip(0, 1),
            pl.col("valence").clip(0, 1),
            pl.col("acousticness").clip(0, 1),
        ])
    )

if __name__ == "__main__":
    try:
        # 1. Init DB
        try:
            init_db()
        except Exception as e:
            print(f"⚠️  DB Init warning: {e}")

        # 2. Pipeline: Read -> Transform -> Insert (Streamed)
        read_sqlite_data()
        
    except Exception as e:
        print(f"❌ Seeding Failed: {e}")
