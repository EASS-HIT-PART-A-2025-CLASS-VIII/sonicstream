import sqlite3
import psycopg
import os
from dotenv import load_dotenv
from tqdm import tqdm

# Load env vars
load_dotenv()

# Config
SQLITE_DB = "spotify.sqlite"
POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'db')
PG_DSN = f"postgresql://{os.getenv('POSTGRES_USER', 'admin')}:{os.getenv('POSTGRES_PASSWORD', 'admin')}@{POSTGRES_HOST}:5432/{os.getenv('POSTGRES_DB', 'music_discovery')}"
BATCH_SIZE = 1000  # Commit every N rows
ROW_LIMIT = 10000  # Total rows to seed

def run_dev_seed():
    print(f"🌱 Starting DEV SEED (Limit: {ROW_LIMIT} rows)...")
    
    if not os.path.exists(SQLITE_DB):
        print(f"❌ ERROR: {SQLITE_DB} not found in {os.getcwd()}")
        return

    # 1. Connect to Postgres & Init Schema
    try:
        pg_conn = psycopg.connect(PG_DSN, autocommit=False) # Manual commit control
        print("✅ Connected to Postgres.")
        
        with pg_conn.cursor() as cur:
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
            cur.execute("""
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
        pg_conn.commit()
    except Exception as e:
        print(f"❌ Postgres Connection Error: {e}")
        return

    # 2. Connect to SQLite & Extract Real Data
    try:
        sqlite_conn = sqlite3.connect(SQLITE_DB)
        sqlite_conn.text_factory = lambda b: b.decode(errors="ignore")
        
        # Complex JOIN to get REAL data
        # Note: We rely on the LIMIT to keep this fast.
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
            LIMIT {ROW_LIMIT}
        """
        
        print(f"⚡ Executing SQLite JOIN Query (fetching {ROW_LIMIT} rows)...")
        cursor = sqlite_conn.cursor()
        cursor.execute(query)
        
        # 3. Stream & Insert with Progress Bar
        batch_buffer = []
        total_inserted = 0
        
        # Initialize progress bar
        pbar = tqdm(total=ROW_LIMIT, unit="rows", desc="🚀 Seeding")

        while True:
            rows = cursor.fetchmany(BATCH_SIZE)
            if not rows:
                break
            
            clean_rows = []
            for r in rows:
                # r = (id, track_name, artist_name, dance, energy, valence, tempo, acoustic)
                track_id = r[0]
                name = r[1]
                artist = r[2] or "Unknown"
                dance = r[3] or 0.5
                energy = r[4] or 0.5
                valence = r[5] or 0.5
                tempo = r[6] or 120.0
                acoustic = r[7] or 0.5
                
                # Normalize tempo for embedding (0-250 approx range)
                tempo_norm = min(max(tempo / 250.0, 0.0), 1.0)
                
                embedding = [dance, energy, valence, tempo_norm, acoustic]
                
                clean_rows.append((
                    track_id, 
                    name, 
                    artist, 
                    dance, 
                    energy, 
                    valence, 
                    tempo, 
                    acoustic, 
                    str(embedding)
                ))
            
            # Insert Batch to Postgres
            with pg_conn.cursor() as cur:
                with cur.copy("COPY tracks (track_id, name, artist, danceability, energy, valence, tempo, acousticness, audio_embedding) FROM STDIN") as copy:
                    for row in clean_rows:
                        copy.write_row(row)
            
            # COMMIT THIS BATCH so it is visible immediately
            pg_conn.commit()
            
            total_inserted += len(rows)
            pbar.update(len(rows))
            
            if total_inserted >= ROW_LIMIT:
                break

        pbar.close()

    except Exception as e:
        print(f"\n❌ Error during seed: {e}")
        if 'pg_conn' in locals(): pg_conn.rollback()
    finally:
        if 'sqlite_conn' in locals(): sqlite_conn.close()
        if 'pg_conn' in locals(): pg_conn.close()
        print(f"\n🏁 Finished. Total Rows Inserted: {total_inserted}")

if __name__ == "__main__":
    run_dev_seed()
