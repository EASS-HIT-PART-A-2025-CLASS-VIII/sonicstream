import sqlite3
import psycopg
import os
from dotenv import load_dotenv

"""
Script: fast_seed.py
Description:
    A lightweight seeding script designed for SUPER FAST initialization.
    
    It bypasses complex joins and mocked data (artist='Unknown', features=0.5) 
    to populate the Postgres database with track IDs and names almost instantly.
    
    Useful for:
    - Testing backend connectivity
    - Testing search performance (with dummy data)
    - Quickly resetting the environment

Usage:
    python backend/scripts/seeding/fast_seed.py
"""

# Load env vars
load_dotenv()

# Config
SQLITE_DB = "spotify.sqlite"
PG_DSN = f"postgresql://{os.getenv('POSTGRES_USER', 'admin')}:{os.getenv('POSTGRES_PASSWORD', 'admin')}@localhost:5432/{os.getenv('POSTGRES_DB', 'music_discovery')}"
BATCH_SIZE = 5000  # Smaller batch = faster initial feedback

def run_seed():
    print(f"🚀 Starting FAST SEED...")
    print(f"   SQLite: {SQLITE_DB}")
    print(f"   Postgres: {PG_DSN.split('@')[1]}") # Print host only for privacy
    
    if not os.path.exists(SQLITE_DB):
        print(f"❌ ERROR: {SQLITE_DB} not found in {os.getcwd()}")
        return

    # 1. Connect to Postgres & Init Schema
    try:
        pg_conn = psycopg.connect(PG_DSN, autocommit=True)
        print("✅ Connected to Postgres.")
        
        # Ensure extension and table exist
        pg_conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
        pg_conn.execute("""
            CREATE TABLE IF NOT EXISTS tracks (
                track_id TEXT PRIMARY KEY,
                name TEXT,
                artist TEXT,
                danceability FLOAT,
                energy FLOAT,
                valence FLOAT,
                tempo FLOAT,
                acousticness FLOAT,
                audio_embedding VECTOR(5)
            )
        """)
        # Drop index for faster insertion, recreate later if needed? 
        # Actually keeping it is fine for COPY usually, but purely for speed we could drop/recreate.
        # Let's leave it for now.
        print("✅ Schema Verified.")
        
    except Exception as e:
        print(f"❌ Postgres Error: {e}")
        return

    # 2. Connect to SQLite
    try:
        sqlite_conn = sqlite3.connect(SQLITE_DB)
        # Avoid full scan, just stream
        sqlite_conn.text_factory = lambda b: b.decode(errors="ignore")
        print("✅ Connected to SQLite.")
        
        # ULTRA FAST QUERY (No Joins)
        # We query ONLY the tracks table to ensure instant start.
        # Audio features will be mocked as 0.5 temporarily so we can test the Search API.
        query = "SELECT id, name FROM tracks"
        
        print(f"⚡ Executing Query (Stream mode, SINGLE TABLE)...")
        cursor = sqlite_conn.cursor()
        cursor.execute(query)
        
        count = 0
        total_batches = 0
        
        while True:
            # Fetch Batch
            rows = cursor.fetchmany(BATCH_SIZE)
            if not rows:
                break
                
            clean_rows = []
            for r in rows:
                # r = (id, name)
                track_id = r[0]
                name = r[1]
                
                # Mock Data for missing columns
                artist = "Unknown Artist" 
                dance = 0.5
                energy = 0.5
                valence = 0.5
                tempo_norm = 0.5
                acoustic = 0.5
                tempo_raw = 120.0
                
                embedding = [dance, energy, valence, tempo_norm, acoustic]
                
                clean_rows.append((
                    track_id, 
                    name, 
                    artist, 
                    dance, 
                    energy, 
                    valence, 
                    tempo_raw, 
                    acoustic, 
                    str(embedding)
                ))
            
            # Insert Batch
            with pg_conn.cursor() as cur:
                with cur.copy("COPY tracks (track_id, name, artist, danceability, energy, valence, tempo, acousticness, audio_embedding) FROM STDIN") as copy:
                    for row in clean_rows:
                        copy.write_row(row)
                        
            count += len(rows)
            total_batches += 1
            if total_batches % 1 == 0: # Print every batch
                print(f"   🚀 Inserted {count} rows... (Last valid: {clean_rows[0][1]})", flush=True)

    except Exception as e:
        print(f"❌ Error during seed: {e}")
    finally:
        if 'sqlite_conn' in locals(): sqlite_conn.close()
        if 'pg_conn' in locals(): pg_conn.close()
        print(f"🏁 Finished. Total Rows: {count}")

if __name__ == "__main__":
    run_seed()
