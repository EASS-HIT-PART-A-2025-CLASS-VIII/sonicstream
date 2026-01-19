import sqlite3
import psycopg
import os
from dotenv import load_dotenv
from tqdm import tqdm

"""
Script: dev_seed.py
Description:
    Seeds the Postgres database from a local SQLite source.
    
    It supports TWO modes of operation automatically:
    1. DEV MODE (Default): Uses `spotify_dev.sqlite`.
       - Source: A flattened, single-table (`dev_tracks`) subset of data.
       - Speed: Extremely fast.
       - Usage: Development, local testing.
       
    2. PRODUCTION MODE: Uses `spotify.sqlite` (The full 5GB dump).
       - Source: Complex normalized tables (`tracks`, `artists`, `audio_features`).
       - Speed: Slower (complex JOINs required).
       - Usage: Full system testing or production seeding.

    The script automatically detects the schema of the provided SQLite file and adapts 
    its query strategy.

Usage:
    python backend/scripts/seeding/dev_seed.py
"""

# Load env vars
load_dotenv()

# Config
# We default to the dev database. 
# To use the full DB, rename/symlink it or change this variable.
# Since we are in backend/scripts/seeding/, we might need to adjust path if running from root?
# No, let's assume it's run from project root: python backend/scripts/seeding/dev_seed.py
# The file path "spotify_dev.sqlite" is relative to CWD (root).
SQLITE_DB = "backend/spotify_dev.sqlite"  # Adjusted specific path to match root execution

POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'db')
PG_DSN = f"postgresql://{os.getenv('POSTGRES_USER', 'admin')}:{os.getenv('POSTGRES_PASSWORD', 'admin')}@{POSTGRES_HOST}:5432/{os.getenv('POSTGRES_DB', 'music_discovery')}"
BATCH_SIZE = 1000  # Commit every N rows
ROW_LIMIT = 100000  # Total rows to seed check

def run_dev_seed():
    print(f"🌱 Starting SEEDING Process...")
    print(f"   Target: Postgres at {POSTGRES_HOST}")
    print(f"   Source: {SQLITE_DB}")
    
    if not os.path.exists(SQLITE_DB):
        print(f"❌ ERROR: Source database {SQLITE_DB} not found in {os.getcwd()}")
        print(f"   Run 'python backend/scripts/etl/create_dev_db.py' to generate it.")
        return

    # 1. Detect Source Schema
    # We check if we are working with the "Flattened" Dev DB or the "Normalized" Full DB.
    is_flattened = False
    
    try:
        tmp_conn = sqlite3.connect(SQLITE_DB)
        cursor = tmp_conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='dev_tracks'")
        if cursor.fetchone():
            is_flattened = True
            print("📦 Detected FLATTENED Dev Schema (Single Table). using fast path.")
        else:
            print("🔗 Detected NORMALIZED Schema (Full DB). using complex JOINs.")
        tmp_conn.close()
    except Exception as e:
        print(f"⚠️ Error checking schema: {e}")
        return

    # 2. Connect to Postgres & Init Schema
    try:
        pg_conn = psycopg.connect(PG_DSN, autocommit=False)
        print("✅ Connected to Postgres.")
        
        with pg_conn.cursor() as cur:
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
            
            # Re-create table
            cur.execute("DROP TABLE IF EXISTS tracks CASCADE")
            
            create_query = """
                CREATE TABLE IF NOT EXISTS tracks (
                    track_id TEXT PRIMARY KEY,
                    name TEXT,
                    artist TEXT,
                    album TEXT,
                    popularity INTEGER,
                    danceability FLOAT,
                    energy FLOAT,
                    valence FLOAT,
                    tempo FLOAT,
                    acousticness FLOAT,
                    audio_embedding VECTOR(5)
                )
            """
            cur.execute(create_query)
        pg_conn.commit()
    except Exception as e:
        print(f"❌ Postgres Connection Error: {e}")
        return

    # 3. Extract Data from SQLite
    try:
        sqlite_conn = sqlite3.connect(SQLITE_DB)
        sqlite_conn.text_factory = lambda b: b.decode(errors="ignore")
        
        if is_flattened:
            # --- FAST PATH (Dev DB) ---
            # Data is already joined and clean.
            query = f"""
                SELECT 
                    track_id, 
                    name, 
                    artist,
                    album, 
                    popularity,
                    danceability, 
                    energy, 
                    valence, 
                    tempo, 
                    acousticness
                FROM dev_tracks
                LIMIT {ROW_LIMIT}
            """
        else:
            # --- SLOW PATH (Full DB) ---
            # We must join manually.
            # Handle missing tables/columns gracefully if needed
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
                ORDER BY MAX(t.popularity) DESC
                LIMIT {ROW_LIMIT}
            """
            
        print(f"⚡ Executing SQLite Extraction (Limit: {ROW_LIMIT})...")
        cursor = sqlite_conn.cursor()
        cursor.execute(query)
        
        # 4. Stream & Insert
        total_inserted = 0
        pbar = tqdm(total=ROW_LIMIT, unit="rows", desc="🚀 Seeding")

        while True:
            rows = cursor.fetchmany(BATCH_SIZE)
            if not rows:
                break
            
            clean_rows = []
            for r in rows:
                # r = (id, name, artist, album, popularity, dance, energy, valence, tempo, acoustic)
                
                # Unpack carefully
                track_id = r[0]
                name = r[1]
                artist = r[2] or "Unknown"
                album = r[3] or "Unknown"
                popularity = r[4] or 0
                
                dance = r[5] or 0.5
                energy = r[6] or 0.5
                valence = r[7] or 0.5
                tempo = r[8] or 120.0
                acoustic = r[9] or 0.5
                
                # Normalize tempo for embedding (0-250 range implied)
                tempo_norm = min(max(tempo / 250.0, 0.0), 1.0)
                embedding = [dance, energy, valence, tempo_norm, acoustic]
                
                row_data = (
                    track_id, 
                    name, 
                    artist, 
                    album, 
                    popularity,
                    dance, 
                    energy, 
                    valence, 
                    tempo, 
                    acoustic, 
                    str(embedding)
                )
                
                clean_rows.append(row_data)
            
            # Insert Batch
            with pg_conn.cursor() as cur:
                cols = "track_id, name, artist, album, popularity, danceability, energy, valence, tempo, acousticness, audio_embedding"
                
                with cur.copy(f"COPY tracks ({cols}) FROM STDIN") as copy:
                    for row in clean_rows:
                        copy.write_row(row)
            
            pg_conn.commit()
            total_inserted += len(rows)
            pbar.update(len(rows))
            
            if total_inserted >= ROW_LIMIT:
                break

        pbar.close()

    except Exception as e:
        print(f"\n❌ Error during seed: {e}")
        import traceback
        traceback.print_exc()
        if 'pg_conn' in locals(): pg_conn.rollback()
    finally:
        if 'sqlite_conn' in locals(): sqlite_conn.close()
        if 'pg_conn' in locals(): pg_conn.close()
        print(f"\n🏁 Finished. Total Rows Inserted: {total_inserted}")

if __name__ == "__main__":
    run_dev_seed()
